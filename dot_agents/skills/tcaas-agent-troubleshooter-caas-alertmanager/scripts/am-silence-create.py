#!/usr/bin/env python3
"""
AlertManager Create Silence Script
Usage: am-silence-create.py --matcher "alertname=Alert" [--duration 6h | --ends 2026-08-03] --comment "reason" --author "name"
"""

import argparse
import sys
from datetime import datetime, timezone

from am_common import (
    AlertManagerClient, AlertManagerError, error_exit, output_json,
    parse_duration, parse_matcher, utc_now, to_iso8601, format_matchers
)


def main():
    parser = argparse.ArgumentParser(
        description='Create an AlertManager silence',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Silence for 6 hours
  %(prog)s --matcher "alertname=NodeDown" --duration 6h --comment "Maintenance" --author "John"

  # Silence until specific date
  %(prog)s --matcher "alertname=NodeDown" --ends 2026-08-03 --comment "Long-term" --author "John"

  # Multiple matchers
  %(prog)s --matcher "alertname=NodeDown" --matcher "cluster=prod" --duration 2d --comment "Fix" --author "John"

  # Regex matcher
  %(prog)s --matcher "alertname=~Node.*" --duration 1h --comment "Testing" --author "John"

Duration formats: 1h (hours), 2d (days), 1w (weeks), 6M (months)
        """
    )

    parser.add_argument('--matcher', '-m', action='append', required=True,
                        help='Matcher in format name=value, name!=value, name=~regex (can be repeated)')
    parser.add_argument('--duration', '-d',
                        help='Duration (e.g., 6h, 2d, 1w, 6M)')
    parser.add_argument('--ends', '-e',
                        help='End date (YYYY-MM-DD or ISO 8601)')
    parser.add_argument('--comment', '-c', required=True,
                        help='Comment/reason for the silence')
    parser.add_argument('--author', '-a', required=True,
                        help='Author name')
    parser.add_argument('--json', action='store_true',
                        help='Output result as JSON')

    args = parser.parse_args()

    # Validate duration/ends
    if not args.duration and not args.ends:
        parser.error("Either --duration or --ends is required")
    if args.duration and args.ends:
        parser.error("Cannot specify both --duration and --ends")

    # Parse matchers
    try:
        matchers = [parse_matcher(m) for m in args.matcher]
    except ValueError as e:
        error_exit(str(e))

    # Calculate time range
    now = utc_now()
    starts_at = to_iso8601(now)

    if args.duration:
        try:
            delta = parse_duration(args.duration)
            ends_at = to_iso8601(now + delta)
        except ValueError as e:
            error_exit(str(e))
    else:
        # Parse end date
        try:
            if 'T' in args.ends:
                end_dt = datetime.fromisoformat(args.ends.replace('Z', '+00:00'))
            else:
                end_dt = datetime.strptime(args.ends, '%Y-%m-%d').replace(
                    hour=23, minute=59, second=59, tzinfo=timezone.utc
                )
            ends_at = to_iso8601(end_dt)
        except ValueError:
            error_exit(f"Invalid date format: {args.ends}\nUse YYYY-MM-DD or ISO 8601")

    # Create client and silence
    try:
        client = AlertManagerClient()
    except AlertManagerError as e:
        error_exit(str(e))

    try:
        result = client.create_silence(
            matchers=matchers,
            starts_at=starts_at,
            ends_at=ends_at,
            created_by=args.author,
            comment=args.comment
        )
    except AlertManagerError as e:
        error_exit(str(e))

    if args.json:
        output_json(result)
    else:
        silence_id = result.get('silenceID', 'unknown')
        print(f"Silence created successfully!")
        print(f"  ID: {silence_id}")
        print(f"  Matchers: {format_matchers(matchers)}")
        print(f"  Starts: {starts_at}")
        print(f"  Ends: {ends_at}")
        print(f"  Author: {args.author}")
        print(f"  Comment: {args.comment}")


if __name__ == '__main__':
    main()
