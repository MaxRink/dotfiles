#!/usr/bin/env python3
"""
Slack Channel History Script
Usage: slack-history.py --channel CHANNEL [options]
"""

import argparse
import sys

from slack_common import (
    SlackClient, error_exit, output_json, parse_time, ts_to_datetime,
    format_datetime, truncate
)


def format_messages(client, messages, verbose=False):
    """Print messages in a human-readable format."""
    if not messages:
        print("No messages found.")
        return

    for msg in messages:
        line = client.format_message(msg)
        print(line)

        # Show reactions if present
        reactions = msg.get('reactions', [])
        if reactions and verbose:
            rx_str = '  '.join(f":{r['name']}: ({r['count']})" for r in reactions)
            print(f"    Reactions: {rx_str}")

        # Show attachments/files summary
        files = msg.get('files', [])
        if files:
            for f in files:
                print(f"    📎 {f.get('name', 'file')} ({f.get('mimetype', '?')})")

    print(f"\nTotal: {len(messages)} messages")


def main():
    parser = argparse.ArgumentParser(description='Fetch Slack channel history')
    parser.add_argument('--channel', '-c', required=True,
                        help='Channel name or ID')
    parser.add_argument('--from', '-f', dest='from_time', default='24h',
                        help='Start time (ISO 8601 or relative: 1h, 2d). Default: 24h')
    parser.add_argument('--to', '-t', dest='to_time',
                        help='End time (ISO 8601 or relative). Default: now')
    parser.add_argument('--limit', '-n', type=int, default=200,
                        help='Max messages (default: 200)')
    parser.add_argument('--threads', action='store_true',
                        help='Expand thread replies (slower)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show reactions and file details')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    client = SlackClient()

    channel_id, channel_name = client.resolve_channel(args.channel)

    oldest = parse_time(args.from_time)
    latest = parse_time(args.to_time) if args.to_time else None

    print(f"Fetching #{channel_name} history from {format_datetime(oldest)}"
          f"{' to ' + format_datetime(latest) if latest else ' to now'} …",
          file=sys.stderr)

    messages = client.get_history(
        channel_id, oldest=oldest, latest=latest,
        limit=args.limit, include_threads=args.threads
    )

    # Sort chronologically (oldest first)
    messages.sort(key=lambda m: float(m.get('ts', 0)))

    if args.json:
        output_json(messages)
    else:
        format_messages(client, messages, verbose=args.verbose)


if __name__ == '__main__':
    main()
