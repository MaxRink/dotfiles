#!/usr/bin/env python3
"""
Slack Search Messages Script (requires user token)
Usage: slack-search.py --query QUERY [options]
"""

import argparse
import sys

from slack_common import (
    SlackClient, error_exit, output_json, ts_to_datetime,
    format_datetime, truncate
)


def format_results(client, matches, total):
    """Print search results in a readable format."""
    if not matches:
        print("No messages found.")
        return

    print(f"Found {total} results (showing {len(matches)}):\n")

    for match in matches:
        ts = ts_to_datetime(match['ts'])
        user = match.get('username', match.get('user', 'unknown'))
        ch_name = match.get('channel', {}).get('name', '?')
        text = truncate(match.get('text', ''), 150)
        permalink = match.get('permalink', '')

        print(f"[{format_datetime(ts)}] #{ch_name} | {user}")
        print(f"  {text}")
        if permalink:
            print(f"  🔗 {permalink}")
        print()


def main():
    parser = argparse.ArgumentParser(description='Search Slack messages')
    parser.add_argument('--query', '-q', required=True,
                        help='Search query (Slack search syntax: in:channel from:user has:link etc.)')
    parser.add_argument('--sort', '-s', choices=['score', 'timestamp'],
                        default='timestamp', help='Sort by (default: timestamp)')
    parser.add_argument('--sort-dir', choices=['asc', 'desc'], default='desc',
                        help='Sort direction (default: desc)')
    parser.add_argument('--limit', '-n', type=int, default=20,
                        help='Max results (default: 20)')
    parser.add_argument('--page', type=int, default=1, help='Page number')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    client = SlackClient()

    print(f"Searching: {args.query} …", file=sys.stderr)

    result = client.search_messages(
        query=args.query,
        sort=args.sort,
        sort_dir=args.sort_dir,
        count=args.limit,
        page=args.page
    )

    matches = result.get('matches', [])
    total = result.get('total', 0)
    paging = result.get('paging', {})

    if args.json:
        output_json({
            'total': total,
            'page': paging.get('page', 1),
            'pages': paging.get('pages', 1),
            'matches': matches,
        })
    else:
        format_results(client, matches, total)
        if paging.get('pages', 1) > paging.get('page', 1):
            print(f"Page {paging['page']}/{paging['pages']} — "
                  f"use --page {paging['page'] + 1} for next")


if __name__ == '__main__':
    main()
