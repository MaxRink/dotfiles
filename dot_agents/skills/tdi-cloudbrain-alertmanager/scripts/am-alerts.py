#!/usr/bin/env python3
"""
AlertManager List Alerts Script
Usage: am-alerts.py [--filter name=value] [--silenced] [--inhibited] [--json]
"""

import argparse
import sys
from collections import Counter

from am_common import (
    AlertManagerClient, AlertManagerError, error_exit, output_json,
    format_datetime
)


def main():
    parser = argparse.ArgumentParser(
        description='List AlertManager alerts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # List active alerts
  %(prog)s --filter alertname=NodeDown        # Filter by alert name
  %(prog)s --silenced                         # Include silenced alerts
  %(prog)s --inhibited                        # Include inhibited alerts
  %(prog)s --summary                          # Show summary by alert name
  %(prog)s --json                             # Output as JSON
        """
    )

    parser.add_argument('--filter', '-f', action='append',
                        help='Filter in format name=value (can be repeated)')
    parser.add_argument('--silenced', '-s', action='store_true',
                        help='Include silenced alerts')
    parser.add_argument('--inhibited', '-i', action='store_true',
                        help='Include inhibited alerts')
    parser.add_argument('--summary', action='store_true',
                        help='Show summary grouped by alert name')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON')

    args = parser.parse_args()

    try:
        client = AlertManagerClient()
    except AlertManagerError as e:
        error_exit(str(e))

    try:
        alerts = client.list_alerts(
            active=True,
            silenced=args.silenced,
            inhibited=args.inhibited,
            filter_matchers=args.filter
        )
    except AlertManagerError as e:
        error_exit(str(e))

    if args.json:
        output_json(alerts)
        return

    if not alerts:
        print("No alerts found.")
        return

    print(f"Found {len(alerts)} alert(s)")
    print()

    if args.summary:
        show_summary(alerts)
    else:
        show_alerts(alerts)


def show_summary(alerts: list) -> None:
    """Show summary grouped by alert name."""
    alert_counts = Counter()
    severity_counts = Counter()

    for alert in alerts:
        labels = alert.get('labels', {})
        alert_name = labels.get('alertname', 'Unknown')
        severity = labels.get('severity', 'unknown')
        alert_counts[alert_name] += 1
        severity_counts[severity] += 1

    print("BY ALERT NAME")
    print("=" * 50)
    for name, count in alert_counts.most_common(20):
        print(f"  {name}: {count}")

    print()
    print("BY SEVERITY")
    print("=" * 50)
    for severity, count in severity_counts.most_common():
        print(f"  {severity}: {count}")


def show_alerts(alerts: list) -> None:
    """Show detailed alert list."""
    for alert in alerts[:50]:  # Limit to 50 alerts
        labels = alert.get('labels', {})
        annotations = alert.get('annotations', {})
        status = alert.get('status', {})

        alert_name = labels.get('alertname', 'Unknown')
        severity = labels.get('severity', 'unknown')
        cluster = labels.get('cluster', labels.get('job', 'N/A'))
        state = status.get('state', 'unknown')

        starts_at = format_datetime(alert.get('startsAt', ''))
        description = annotations.get('description', annotations.get('summary', ''))[:80]

        silenced = '🔇' if status.get('silencedBy') else ''
        inhibited = '⏸' if status.get('inhibitedBy') else ''

        severity_icon = {
            'critical': '🔴',
            'warning': '🟡',
            'info': '🔵'
        }.get(severity, '⚪')

        print(f"{severity_icon} [{severity.upper()}] {alert_name} {silenced}{inhibited}")
        print(f"    Cluster: {cluster}")
        print(f"    Started: {starts_at}")
        if description:
            print(f"    Description: {description}{'...' if len(description) >= 80 else ''}")
        print()

    if len(alerts) > 50:
        print(f"... and {len(alerts) - 50} more alerts (use --json for full list)")


if __name__ == '__main__':
    main()
