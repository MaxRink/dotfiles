#!/usr/bin/env python3
"""
PagerDuty Incident Summary Script
Usage: pd-summary.py [--since DATE] [--until DATE] [--json]
"""

import argparse
import sys
from collections import Counter
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

from pd_common import (
    PagerDutyClient, PagerDutyError, error_exit, output_json,
    get_date_range, parse_date
)


def generate_summary(incidents: List[Dict[str, Any]], since_display: str, until_display: str) -> None:
    """Generate and print incident summary."""
    print('=' * 70)
    print('INCIDENT SUMMARY FOR T-CaaS')
    print(f'Period: {since_display} to {until_display}')
    print('=' * 70)
    print()

    if not incidents:
        print('No incidents found in the specified time range.')
        return

    # Count by status
    status_counts = Counter(inc.get('status') for inc in incidents)

    # Count by service
    service_counts = Counter(
        inc.get('service', {}).get('summary', 'Unknown') for inc in incidents
    )

    # Count by urgency
    urgency_counts = Counter(inc.get('urgency') for inc in incidents)

    # Count by day of week
    dow_counts: Counter = Counter()
    for inc in incidents:
        created = inc.get('created_at', '')
        if created:
            try:
                dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                dow_counts[dt.strftime('%A')] += 1
            except (ValueError, AttributeError):
                pass

    print(f'Total Incidents: {len(incidents)}')
    print()

    print('By Status:')
    print('-' * 30)
    for status in ['triggered', 'acknowledged', 'resolved']:
        count = status_counts.get(status, 0)
        bar = '#' * min(count, 50)
        print(f'  {status.capitalize():15} {count:>5}  {bar}')
    print()

    print('By Urgency:')
    print('-' * 30)
    for urgency in ['high', 'low']:
        count = urgency_counts.get(urgency, 0)
        pct = (count / len(incidents) * 100) if incidents else 0
        print(f'  {urgency.capitalize():15} {count:>5}  ({pct:.1f}%)')
    print()

    print('Top 10 Services by Incident Count:')
    print('-' * 50)
    for service, count in service_counts.most_common(10):
        bar = '#' * min(count, 30)
        print(f'  {service[:35]:35} {count:>5}  {bar}')
    print()

    print('Incidents by Day of Week:')
    print('-' * 30)
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for day in days_order:
        count = dow_counts.get(day, 0)
        bar = '#' * min(count, 30)
        print(f'  {day:12} {count:>5}  {bar}')
    print()

    # Resolution rate
    resolved = len([inc for inc in incidents if inc.get('status') == 'resolved'])
    print(f'Resolved: {resolved} / {len(incidents)} ({resolved/len(incidents)*100:.1f}%)')


def main():
    parser = argparse.ArgumentParser(
        description='Generate PagerDuty incident summary for T-CaaS team',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Last 30 days
  %(prog)s --since 2026-01-01 --until 2026-01-31  # January 2026
  %(prog)s --json                             # JSON output
        """
    )

    parser.add_argument('--since', help='Start date (YYYY-MM-DD, default: 30 days ago)')
    parser.add_argument('--until', help='End date (YYYY-MM-DD, default: today)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    try:
        client = PagerDutyClient()
    except PagerDutyError as e:
        error_exit(str(e))

    # Calculate date range (default: last 30 days)
    since, until = get_date_range(args.since, args.until, days_ago=30)

    try:
        incidents = client.get_incidents(since=since, until=until, max_results=5000)
    except PagerDutyError as e:
        error_exit(str(e))

    # Extract display dates
    since_display = since[:10] if since else 'N/A'
    until_display = until[:10] if until else 'N/A'

    # Output
    if args.json:
        output_json({
            'period': {'since': since_display, 'until': until_display},
            'total': len(incidents),
            'incidents': incidents
        })
    else:
        generate_summary(incidents, since_display, until_display)


if __name__ == '__main__':
    main()
