#!/usr/bin/env python3
"""
AlertManager List Silences Script
Usage: am-silence-list.py [--all] [--json]
"""

import argparse
import sys

from am_common import (
    AlertManagerClient, AlertManagerError, error_exit, output_json,
    format_datetime, format_matchers
)


def main():
    parser = argparse.ArgumentParser(
        description='List AlertManager silences',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                  # List active silences
  %(prog)s --all            # Include expired silences
  %(prog)s --json           # Output as JSON
        """
    )

    parser.add_argument('--all', '-a', action='store_true',
                        help='Include expired silences')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON')

    args = parser.parse_args()

    try:
        client = AlertManagerClient()
    except AlertManagerError as e:
        error_exit(str(e))

    try:
        silences = client.list_silences(filter_expired=not args.all)
    except AlertManagerError as e:
        error_exit(str(e))

    if args.json:
        output_json(silences)
        return

    if not silences:
        print("No silences found.")
        return

    # Group by state
    active = []
    pending = []
    expired = []

    for s in silences:
        state = s.get('status', {}).get('state', 'unknown')
        if state == 'active':
            active.append(s)
        elif state == 'pending':
            pending.append(s)
        elif state == 'expired':
            expired.append(s)

    total = len(silences)
    print(f"Found {total} silence(s)")
    print()

    if active:
        print(f"ACTIVE ({len(active)})")
        print("=" * 60)
        for s in active:
            print_silence(s)
        print()

    if pending:
        print(f"PENDING ({len(pending)})")
        print("=" * 60)
        for s in pending:
            print_silence(s)
        print()

    if expired and args.all:
        print(f"EXPIRED ({len(expired)})")
        print("=" * 60)
        for s in expired[:10]:  # Limit expired to last 10
            print_silence(s)
        if len(expired) > 10:
            print(f"  ... and {len(expired) - 10} more expired silences")
        print()


def print_silence(silence: dict) -> None:
    """Print a single silence."""
    sid = silence.get('id', 'unknown')[:12]
    state = silence.get('status', {}).get('state', 'unknown').upper()
    matchers = silence.get('matchers', [])
    starts = format_datetime(silence.get('startsAt', ''))
    ends = format_datetime(silence.get('endsAt', ''))
    author = silence.get('createdBy', 'unknown')
    comment = silence.get('comment', '')

    print(f"  [{state}] {sid}...")
    print(f"    Matchers: {format_matchers(matchers)}")
    print(f"    Period: {starts} → {ends}")
    print(f"    Author: {author}")
    if comment:
        print(f"    Comment: {comment[:80]}{'...' if len(comment) > 80 else ''}")
    print()


if __name__ == '__main__':
    main()
