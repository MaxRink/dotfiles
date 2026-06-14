#!/usr/bin/env python3
"""
PagerDuty List Services Script
Usage: pd-services.py [--status STATUS] [--json]
"""

import argparse
import sys
from typing import List, Dict, Any

from pd_common import (
    PagerDutyClient, PagerDutyError, error_exit, output_json
)


def filter_by_status(services: List[Dict[str, Any]], status_filter: str) -> List[Dict[str, Any]]:
    """Filter services by status."""
    if not status_filter:
        return services
    return [s for s in services if s.get('status', '').lower() == status_filter.lower()]


def format_services(services: List[Dict[str, Any]]) -> None:
    """Format and print services list."""
    print(f'Found {len(services)} services')
    print('=' * 60)
    print()

    for svc in sorted(services, key=lambda x: x.get('name', '')):
        name = svc.get('name', 'Unknown')
        svc_id = svc.get('id', '')
        status = svc.get('status', 'unknown')
        description = svc.get('description', '-') or '-'
        escalation = svc.get('escalation_policy', {}).get('summary', 'None')
        html_url = svc.get('html_url', '')

        status_icon = '[ON]' if status == 'active' else '[OFF]'

        print(f'{status_icon} {name}')
        print(f'    ID: {svc_id}')
        print(f'    Status: {status}')
        if len(description) > 60:
            print(f'    Description: {description[:60]}...')
        else:
            print(f'    Description: {description}')
        print(f'    Escalation Policy: {escalation}')
        print(f'    URL: {html_url}')
        print()


def main():
    parser = argparse.ArgumentParser(
        description='List PagerDuty services for T-CaaS team',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                 # All services
  %(prog)s --status active # Active services only
  %(prog)s --json          # JSON output
        """
    )

    parser.add_argument('--status', help='Filter by status: active, disabled')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    try:
        client = PagerDutyClient()
    except PagerDutyError as e:
        error_exit(str(e))

    try:
        services = client.get_services()
    except PagerDutyError as e:
        error_exit(str(e))

    # Filter by status
    if args.status:
        services = filter_by_status(services, args.status)

    if not services:
        if args.status:
            print(f'No services found with status "{args.status}"')
        else:
            print('No services found for this team.')
        return

    # Output
    if args.json:
        output_json(services)
    else:
        format_services(services)


if __name__ == '__main__':
    main()
