#!/usr/bin/env python3
"""
Slack Incident Search Script
Searches for incident-related messages: PagerDuty links, alert names, cluster mentions.
Usage: slack-incidents.py [options]
"""

import argparse
import re
import sys
from collections import Counter

from slack_common import (
    SlackClient, error_exit, output_json, parse_time, ts_to_datetime,
    format_datetime, truncate
)

# Patterns for incident-related content
PD_LINK_RE = re.compile(r'pagerduty\.com/incidents/([A-Z0-9]+)', re.IGNORECASE)
PD_TITLE_RE = re.compile(r'\[([^|]+)\s*\|\s*([^\]]+)\]\s*(\S+)')
ALERT_KEYWORDS = re.compile(
    r'\b(incident|outage|alert|down|degraded|failure|critical|emergency|postmortem|post-mortem|RCA)\b',
    re.IGNORECASE
)
CLUSTER_RE = re.compile(r'\b([a-z]{2}[a-z0-9]+-[a-z]+-(?:prod|staging|dev|lab))\b')


def is_incident_related(msg):
    """Check if a message is incident-related."""
    text = msg.get('text', '')
    attachments = msg.get('attachments', [])
    att_text = ' '.join(a.get('text', '') + a.get('fallback', '') for a in attachments)
    combined = text + ' ' + att_text

    return bool(
        PD_LINK_RE.search(combined)
        or ALERT_KEYWORDS.search(combined)
        or (PD_TITLE_RE.search(combined) and CLUSTER_RE.search(combined))
    )


def extract_incident_info(msg):
    """Extract structured incident info from a message."""
    text = msg.get('text', '')
    attachments = msg.get('attachments', [])
    att_text = ' '.join(a.get('text', '') + a.get('fallback', '') for a in attachments)
    combined = text + ' ' + att_text

    info = {
        'ts': msg.get('ts'),
        'user': msg.get('user', msg.get('username', 'unknown')),
        'text': truncate(text, 200),
        'pd_incidents': PD_LINK_RE.findall(combined),
        'clusters': list(set(CLUSTER_RE.findall(combined))),
        'alerts': [],
    }

    # Extract alert names from PD title format
    for match in PD_TITLE_RE.finditer(combined):
        alert_name = match.group(3)
        if alert_name and not alert_name.startswith('http'):
            info['alerts'].append(alert_name)

    return info


def main():
    parser = argparse.ArgumentParser(description='Search Slack for incident-related messages')
    parser.add_argument('--cluster', '-c', help='Filter by cluster name (partial match)')
    parser.add_argument('--alert', '-a', help='Filter by alert name (partial match)')
    parser.add_argument('--since', '-s', default='24h',
                        help='Look back period (default: 24h)')
    parser.add_argument('--channel', help='Specific channel (default: search all)')
    parser.add_argument('--keyword', '-k', help='Additional keyword filter')
    parser.add_argument('--limit', '-n', type=int, default=50,
                        help='Max results (default: 50)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--summary', action='store_true',
                        help='Show summary statistics instead of individual messages')
    args = parser.parse_args()

    client = SlackClient()
    oldest = parse_time(args.since)

    # Build search query for user-token search
    query_parts = []
    if args.keyword:
        query_parts.append(args.keyword)
    if args.cluster:
        query_parts.append(args.cluster)
    if args.alert:
        query_parts.append(args.alert)
    if args.channel:
        query_parts.append(f'in:{args.channel}')

    # If no specific query, search for general incident keywords
    if not query_parts:
        query_parts.append('incident')

    query_parts.append(f'after:{oldest.strftime("%Y-%m-%d")}')
    query = ' '.join(query_parts)

    print(f"Searching for incidents: {query} …", file=sys.stderr)

    if client.user:
        # Use search API for broader results
        result = client.search_messages(query=query, count=min(args.limit, 100))
        raw_matches = result.get('matches', [])
    else:
        # Fallback: scan channel history
        raw_matches = []
        if args.channel:
            ch_id, _ = client.resolve_channel(args.channel)
            channels_to_scan = [{'id': ch_id, 'name': args.channel}]
        else:
            channels_to_scan = client.get_member_channels()

        for ch in channels_to_scan:
            print(f"  Scanning #{ch['name']} …", file=sys.stderr)
            msgs = client.get_history(ch['id'], oldest=oldest, limit=200)
            for m in msgs:
                if is_incident_related(m):
                    m['channel'] = {'name': ch['name'], 'id': ch['id']}
                    raw_matches.append(m)

    # Post-filter by cluster/alert
    incidents = []
    for msg in raw_matches:
        info = extract_incident_info(msg)

        if args.cluster:
            if not any(args.cluster.lower() in c.lower() for c in info['clusters']):
                text = msg.get('text', '').lower()
                if args.cluster.lower() not in text:
                    continue

        if args.alert:
            if not any(args.alert.lower() in a.lower() for a in info['alerts']):
                text = msg.get('text', '').lower()
                if args.alert.lower() not in text:
                    continue

        info['channel'] = msg.get('channel', {})
        if isinstance(info['channel'], dict):
            info['channel_name'] = info['channel'].get('name', '?')
        else:
            info['channel_name'] = str(info['channel'])
        info['permalink'] = msg.get('permalink', '')
        incidents.append(info)

    incidents = incidents[:args.limit]

    if args.summary:
        cluster_counts = Counter()
        alert_counts = Counter()
        channel_counts = Counter()
        pd_ids = set()

        for inc in incidents:
            for c in inc['clusters']:
                cluster_counts[c] += 1
            for a in inc['alerts']:
                alert_counts[a] += 1
            channel_counts[inc['channel_name']] += 1
            pd_ids.update(inc['pd_incidents'])

        summary = {
            'total_incident_messages': len(incidents),
            'unique_pd_incidents': len(pd_ids),
            'clusters_mentioned': dict(cluster_counts.most_common(20)),
            'alerts_mentioned': dict(alert_counts.most_common(20)),
            'channels_with_incidents': dict(channel_counts.most_common(20)),
        }

        if args.json:
            output_json(summary)
        else:
            print(f"═══ Incident Summary (since {format_datetime(oldest)}) ═══\n")
            print(f"  Messages:     {summary['total_incident_messages']}")
            print(f"  PD Incidents: {summary['unique_pd_incidents']}")

            if cluster_counts:
                print(f"\n  Clusters Mentioned:")
                for cluster, count in cluster_counts.most_common(10):
                    print(f"    {cluster:<40} {count}")

            if alert_counts:
                print(f"\n  Alerts Mentioned:")
                for alert, count in alert_counts.most_common(10):
                    print(f"    {alert:<40} {count}")

            if channel_counts:
                print(f"\n  Active Channels:")
                for ch, count in channel_counts.most_common(10):
                    print(f"    #{ch:<39} {count}")
    else:
        if args.json:
            output_json(incidents)
        else:
            if not incidents:
                print("No incident-related messages found.")
                return

            print(f"Found {len(incidents)} incident-related messages:\n")
            for inc in incidents:
                ts = ts_to_datetime(inc['ts'])
                print(f"[{format_datetime(ts)}] #{inc['channel_name']}")
                print(f"  {inc['text']}")
                if inc['clusters']:
                    print(f"  Clusters: {', '.join(inc['clusters'])}")
                if inc['alerts']:
                    print(f"  Alerts: {', '.join(inc['alerts'])}")
                if inc['pd_incidents']:
                    print(f"  PD IDs: {', '.join(inc['pd_incidents'])}")
                if inc['permalink']:
                    print(f"  🔗 {inc['permalink']}")
                print()


if __name__ == '__main__':
    main()
