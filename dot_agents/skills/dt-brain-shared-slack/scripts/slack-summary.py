#!/usr/bin/env python3
"""
Slack Channel Summary Script
Usage: slack-summary.py --channel CHANNEL [options]
"""

import argparse
import sys
from collections import Counter
from datetime import datetime, timezone

from slack_common import (
    SlackClient, error_exit, output_json, parse_time, ts_to_datetime,
    format_datetime, truncate
)


def build_summary(client, messages, channel_name):
    """Build a structured summary from messages."""
    if not messages:
        return {'channel': channel_name, 'total_messages': 0}

    user_counts = Counter()
    reaction_counts = Counter()
    thread_count = 0
    links = []
    file_count = 0
    hours = Counter()

    for msg in messages:
        user_id = msg.get('user', msg.get('username', 'unknown'))
        user_counts[user_id] += 1

        if msg.get('reply_count', 0) > 0:
            thread_count += 1

        for rx in msg.get('reactions', []):
            reaction_counts[rx['name']] += rx.get('count', 1)

        # Extract links from text
        text = msg.get('text', '')
        import re
        found_links = re.findall(r'<(https?://[^>|]+)(?:\|[^>]*)?>',  text)
        links.extend(found_links)

        if msg.get('files'):
            file_count += len(msg['files'])

        ts = ts_to_datetime(msg['ts'])
        hours[ts.hour] += 1

    # Resolve top users
    top_user_ids = [uid for uid, _ in user_counts.most_common(10)]
    user_names = client.resolve_users_bulk(top_user_ids)

    top_contributors = [
        {'user': user_names.get(uid, uid), 'messages': count}
        for uid, count in user_counts.most_common(10)
    ]

    # Peak hours
    peak_hours = [{'hour': f"{h:02d}:00", 'messages': c}
                  for h, c in hours.most_common(5)]

    # Unique links
    unique_links = list(dict.fromkeys(links))[:20]

    top_reactions = [{'emoji': name, 'count': count}
                     for name, count in reaction_counts.most_common(10)]

    return {
        'channel': channel_name,
        'total_messages': len(messages),
        'unique_users': len(user_counts),
        'threads': thread_count,
        'files_shared': file_count,
        'top_contributors': top_contributors,
        'top_reactions': top_reactions,
        'peak_hours': peak_hours,
        'links_shared': unique_links,
    }


def print_summary(summary):
    """Print summary in human-readable format."""
    ch = summary['channel']
    print(f"═══ #{ch} Summary ═══\n")

    print(f"  Messages:    {summary['total_messages']}")
    print(f"  Users:       {summary['unique_users']}")
    print(f"  Threads:     {summary['threads']}")
    print(f"  Files:       {summary['files_shared']}")

    if summary.get('top_contributors'):
        print(f"\n  Top Contributors:")
        for i, c in enumerate(summary['top_contributors'][:5], 1):
            bar = '█' * min(c['messages'], 30)
            print(f"    {i}. {c['user']:<25} {c['messages']:>4}  {bar}")

    if summary.get('peak_hours'):
        print(f"\n  Peak Hours (UTC):")
        for h in summary['peak_hours'][:3]:
            print(f"    {h['hour']}  ({h['messages']} msgs)")

    if summary.get('top_reactions'):
        print(f"\n  Top Reactions:")
        rx_str = '  '.join(f":{r['emoji']}: ({r['count']})" for r in summary['top_reactions'][:5])
        print(f"    {rx_str}")

    if summary.get('links_shared'):
        print(f"\n  Links Shared ({len(summary['links_shared'])}):")
        for link in summary['links_shared'][:5]:
            print(f"    • {link}")


def main():
    parser = argparse.ArgumentParser(description='Summarize Slack channel activity')
    parser.add_argument('--channel', '-c', help='Channel name or ID')
    parser.add_argument('--all', action='store_true', help='Summarize all channels')
    parser.add_argument('--filter', '-f', dest='filter_pattern',
                        help='Filter channels by name pattern (with --all)')
    parser.add_argument('--from', '-F', dest='from_time', default='24h',
                        help='Start time (default: 24h)')
    parser.add_argument('--to', '-T', dest='to_time', help='End time (default: now)')
    parser.add_argument('--top', type=int, default=5,
                        help='Number of top contributors (default: 5)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    if not args.channel and not args.all:
        error_exit("Specify --channel or --all")

    client = SlackClient()
    oldest = parse_time(args.from_time)
    latest = parse_time(args.to_time) if args.to_time else None

    if args.all:
        import re
        channels = client.get_member_channels()
        if args.filter_pattern:
            rx = re.compile(args.filter_pattern, re.IGNORECASE)
            channels = [ch for ch in channels if rx.search(ch['name'])]

        summaries = []
        for ch in channels:
            print(f"Scanning #{ch['name']} …", file=sys.stderr)
            msgs = client.get_history(ch['id'], oldest=oldest, latest=latest, limit=500)
            if msgs:
                s = build_summary(client, msgs, ch['name'])
                summaries.append(s)

        # Sort by message count
        summaries.sort(key=lambda s: s['total_messages'], reverse=True)

        if args.json:
            output_json(summaries)
        else:
            if not summaries:
                print("No activity found in any channel for the given time range.")
                return
            print(f"Channel Activity Summary ({format_datetime(oldest)} → now)\n")
            print(f"{'Channel':<30} {'Msgs':>5} {'Users':>5} {'Threads':>7}")
            print(f"{'─' * 30} {'─' * 5} {'─' * 5} {'─' * 7}")
            for s in summaries:
                print(f"#{s['channel']:<29} {s['total_messages']:>5} "
                      f"{s['unique_users']:>5} {s['threads']:>7}")
            print(f"\nTotal: {len(summaries)} active channels, "
                  f"{sum(s['total_messages'] for s in summaries)} messages")
    else:
        channel_id, channel_name = client.resolve_channel(args.channel)
        print(f"Summarizing #{channel_name} …", file=sys.stderr)
        messages = client.get_history(channel_id, oldest=oldest, latest=latest, limit=1000)
        summary = build_summary(client, messages, channel_name)

        if args.json:
            output_json(summary)
        else:
            print_summary(summary)


if __name__ == '__main__':
    main()
