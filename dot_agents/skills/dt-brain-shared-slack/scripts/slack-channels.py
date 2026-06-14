#!/usr/bin/env python3
"""
Slack List Channels Script
Usage: slack-channels.py [options]
"""

import argparse
import re
import sys
from datetime import datetime, timezone

from slack_common import SlackClient, error_exit, output_json, ts_to_datetime, format_datetime


def filter_channels(channels, pattern=None):
    """Filter channels by name pattern (regex)."""
    if not pattern:
        return channels
    try:
        rx = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        error_exit(f"Invalid filter pattern: {e}")
    return [ch for ch in channels if rx.search(ch['name'])
            or rx.search(ch.get('topic', {}).get('value', ''))
            or rx.search(ch.get('purpose', {}).get('value', ''))]


def sort_channels(channels, sort_key='name'):
    """Sort channels by key."""
    if sort_key == 'name':
        return sorted(channels, key=lambda c: c['name'])
    elif sort_key == 'members':
        return sorted(channels, key=lambda c: c.get('num_members', 0), reverse=True)
    elif sort_key == 'activity':
        # updated is a unix timestamp of last activity
        return sorted(channels, key=lambda c: float(c.get('updated', 0) or 0), reverse=True)
    return channels


def format_table(channels):
    """Format channels as a table."""
    if not channels:
        print("No channels found.")
        return

    # Header
    print(f"{'Channel':<35} {'Members':>7}  {'Topic / Purpose'}")
    print(f"{'─' * 35} {'─' * 7}  {'─' * 50}")

    for ch in channels:
        name = f"#{ch['name']}"
        members = ch.get('num_members', '?')
        topic = ch.get('topic', {}).get('value', '').replace('\n', ' ').strip()
        purpose = ch.get('purpose', {}).get('value', '').replace('\n', ' ').strip()
        desc = topic or purpose or '—'
        if len(desc) > 50:
            desc = desc[:47] + '…'
        private = '🔒' if ch.get('is_private') else '  '
        print(f"{private}{name:<33} {members:>7}  {desc}")

    print(f"\nTotal: {len(channels)} channels")


def main():
    parser = argparse.ArgumentParser(description='List Slack channels the bot has joined')
    parser.add_argument('--filter', '-f', help='Filter by name/topic/purpose (regex)')
    parser.add_argument('--sort', '-s', choices=['name', 'members', 'activity'],
                        default='name', help='Sort order (default: name)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--private', action='store_true', help='Show only private channels')
    parser.add_argument('--all-workspace', action='store_true',
                        help='List ALL workspace channels (slow on large instances)')
    parser.add_argument('--limit', '-n', type=int, help='Max channels to show')
    args = parser.parse_args()

    client = SlackClient()

    if args.all_workspace:
        channels = client.get_channels()
    else:
        channels = client.get_member_channels()

    if args.private:
        channels = [ch for ch in channels if ch.get('is_private')]

    channels = filter_channels(channels, args.filter)
    channels = sort_channels(channels, args.sort)

    if args.limit:
        channels = channels[:args.limit]

    if args.json:
        output_json([{
            'id': ch['id'],
            'name': ch['name'],
            'is_private': ch.get('is_private', False),
            'num_members': ch.get('num_members', 0),
            'topic': ch.get('topic', {}).get('value', ''),
            'purpose': ch.get('purpose', {}).get('value', ''),
        } for ch in channels])
    else:
        format_table(channels)


if __name__ == '__main__':
    main()
