#!/usr/bin/env python3
"""
PagerDuty On-Call Script
Usage: pd-oncall.py [--schedule NAME] [--hours N] [--json]
"""

import argparse
import sys
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

from pd_common import (
    PagerDutyClient, PagerDutyError, error_exit, output_json, format_datetime
)


def filter_by_schedule(oncalls: List[Dict[str, Any]], schedule_filter: str) -> List[Dict[str, Any]]:
    """Filter on-calls by schedule name (case-insensitive partial match)."""
    if not schedule_filter:
        return oncalls
    return [
        oc for oc in oncalls
        if schedule_filter.lower() in oc.get('schedule', {}).get('summary', '').lower()
    ]


def format_current_oncall(oncalls: List[Dict[str, Any]]) -> None:
    """Format and print current on-call rotation."""
    print('Current On-Call Rotation')
    print('=' * 60)
    print()

    # Group by escalation policy
    by_policy: Dict[str, List[Dict[str, Any]]] = {}
    for oc in oncalls:
        policy = oc.get('escalation_policy', {}).get('summary', 'Direct Assignment')
        if policy not in by_policy:
            by_policy[policy] = []
        by_policy[policy].append(oc)

    for policy, entries in sorted(by_policy.items()):
        print(f'Escalation Policy: {policy}')
        print('-' * 50)

        # Sort by escalation level
        sorted_entries = sorted(entries, key=lambda x: x.get('escalation_level', 0))

        for oc in sorted_entries:
            user = oc.get('user', {}).get('summary', 'Unknown')
            level = oc.get('escalation_level', '?')
            schedule = oc.get('schedule', {}).get('summary', 'Direct')
            start = format_datetime(oc.get('start', ''))
            end = format_datetime(oc.get('end', '')) if oc.get('end') else 'Ongoing'

            print(f'  Level {level}: {user}')
            print(f'           Schedule: {schedule}')
            print(f'           Period:   {start} to {end}')
        print()


def merge_consecutive_oncalls(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Merge adjacent/overlapping on-call entries for the same user.
    For entries by the same user with gaps <= 12 hours, merge them
    (handles off-hours schedules like Second Level)."""
    sorted_entries = sorted(entries, key=lambda x: x.get('start', ''))
    if not sorted_entries:
        return []

    merged = [dict(sorted_entries[0])]
    for oc in sorted_entries[1:]:
        prev = merged[-1]
        same_user = oc.get('user', {}).get('id') == prev.get('user', {}).get('id')
        if same_user:
            prev_end = datetime.fromisoformat(prev.get('end', '').replace('Z', '+00:00'))
            oc_start = datetime.fromisoformat(oc.get('start', '').replace('Z', '+00:00'))
            gap_hours = (oc_start - prev_end).total_seconds() / 3600
            if gap_hours <= 12:
                prev['end'] = max(prev.get('end', ''), oc.get('end', ''))
                continue
        merged.append(dict(oc))
    return merged


def format_schedule_range(oncalls: List[Dict[str, Any]]) -> None:
    """Format and print on-call schedule for a time range."""
    print('On-Call Schedule')
    print('=' * 60)
    print()

    # Group by schedule name
    by_schedule: Dict[str, List[Dict[str, Any]]] = {}
    for oc in oncalls:
        sched = oc.get('schedule', {}).get('summary', 'Direct Assignment')
        if sched not in by_schedule:
            by_schedule[sched] = []
        by_schedule[sched].append(oc)

    for sched_name, entries in sorted(by_schedule.items()):
        print(f'{sched_name}')
        print('-' * 50)

        merged_entries = merge_consecutive_oncalls(entries)

        for oc in merged_entries:
            user = oc.get('user', {}).get('summary', 'Unknown')
            level = oc.get('escalation_level', '?')
            start = format_datetime(oc.get('start', ''))
            end = format_datetime(oc.get('end', '')) if oc.get('end') else 'Ongoing'

            print(f'  {start} -> {end}')
            print(f'    {user} (Level {level})')
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Show PagerDuty on-call schedule for T-CaaS team',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                         # Current on-call
  %(prog)s --hours 48              # Next 2 days schedule
  %(prog)s --schedule "First Level" # Filter by schedule name
  %(prog)s --json                  # JSON output
        """
    )

    parser.add_argument('--schedule', help='Filter by schedule name')
    parser.add_argument('--since', help='Start time (ISO 8601, default: now)')
    parser.add_argument('--until', help='End time (ISO 8601)')
    parser.add_argument('--hours', type=int, help='Show schedule for next N hours')
    parser.add_argument('--today', action='store_true', help='Show schedule for today (local time)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    try:
        client = PagerDutyClient()
    except PagerDutyError as e:
        error_exit(str(e))

    # Handle time range
    since = args.since
    until = args.until

    if args.today:
        local_now = datetime.now().astimezone()
        local_tz = local_now.tzinfo
        start_of_day = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        since = start_of_day.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        until = end_of_day.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    elif args.hours:
        now = datetime.now(timezone.utc)
        if not since:
            since = now.strftime('%Y-%m-%dT%H:%M:%SZ')
        until = (now + timedelta(hours=args.hours)).strftime('%Y-%m-%dT%H:%M:%SZ')

    try:
        oncalls = client.get_oncalls(since=since, until=until)
    except PagerDutyError as e:
        error_exit(str(e))

    # Filter by schedule name
    if args.schedule:
        oncalls = filter_by_schedule(oncalls, args.schedule)

    if not oncalls:
        if args.schedule:
            print(f'No on-call assignments found for schedule matching "{args.schedule}"')
        else:
            print('No on-call assignments found.')
        return

    # Output
    if args.json:
        output_json(oncalls)
    elif until:
        format_schedule_range(oncalls)
    else:
        format_current_oncall(oncalls)


if __name__ == '__main__':
    main()
