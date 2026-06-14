#!/usr/bin/env python3
"""
PagerDuty List Incidents Script
Usage: pd-incidents.py [options]
"""

import argparse
import sys
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

from pd_common import (
    PagerDutyClient, PagerDutyError, error_exit, output_json,
    parse_cluster_from_title, format_datetime, parse_date,
    STATUS_ICONS
)


def filter_incidents(
    incidents: List[Dict[str, Any]],
    cluster: Optional[str] = None,
    site: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Filter incidents by cluster or site name"""
    if not cluster and not site:
        return incidents

    filtered = []
    for inc in incidents:
        title = inc.get('title', '')
        cluster_info = parse_cluster_from_title(title)

        if cluster_info:
            match = True
            if cluster:
                # Partial match, case-insensitive
                if cluster.lower() not in cluster_info['cluster'].lower():
                    match = False
            if site:
                # Partial match, case-insensitive
                if site.lower() not in cluster_info['site'].lower():
                    match = False
            if match:
                filtered.append(inc)
        elif not cluster_info and (cluster or site):
            # If no cluster info parsed but user is filtering, skip this incident
            continue

    return filtered


def format_incident(inc: Dict[str, Any], client: PagerDutyClient, show_url: bool = True) -> str:
    """Format a single incident for display"""
    number = inc.get('incident_number', 'N/A')
    inc_id = inc.get('id', '')
    title = inc.get('title', 'No title')
    status = inc.get('status', 'unknown')
    urgency = inc.get('urgency', 'unknown')
    created = format_datetime(inc.get('created_at', ''))
    service = inc.get('service', {}).get('summary', 'Unknown')
    assignees = [a.get('assignee', {}).get('summary', '') for a in inc.get('assignments', [])]
    assignee_str = ', '.join(assignees) if assignees else 'Unassigned'

    status_icon = STATUS_ICONS.get(status, '[ ]')
    urgency_tag = '[HIGH]' if urgency == 'high' else '[low]'

    lines = [
        f'{status_icon} #{number} {status.upper()} {urgency_tag}',
        f'    {title}',
        f'    Service: {service}',
        f'    Created: {created} | Assigned: {assignee_str}'
    ]

    if show_url:
        lines.append(f'    URL: {client.incident_url(inc_id)}')

    return '\n'.join(lines)


def format_json(incidents: List[Dict[str, Any]]) -> None:
    """Format incidents as JSON"""
    output_json(incidents)


def format_summary(incidents: List[Dict[str, Any]]) -> str:
    """Generate a summary of incidents"""
    if not incidents:
        return "No incidents found."

    status_counts = {}
    urgency_counts = {}
    cluster_counts = {}

    for inc in incidents:
        status = inc.get('status', 'unknown')
        urgency = inc.get('urgency', 'unknown')

        status_counts[status] = status_counts.get(status, 0) + 1
        urgency_counts[urgency] = urgency_counts.get(urgency, 0) + 1

        title = inc.get('title', '')
        cluster_info = parse_cluster_from_title(title)
        if cluster_info:
            cluster = cluster_info['cluster']
            cluster_counts[cluster] = cluster_counts.get(cluster, 0) + 1

    lines = [
        f"Total Incidents: {len(incidents)}",
        "",
        "By Status:",
    ]
    for status, count in sorted(status_counts.items()):
        lines.append(f"  {status}: {count}")

    lines.append("")
    lines.append("By Urgency:")
    for urgency, count in sorted(urgency_counts.items()):
        lines.append(f"  {urgency}: {count}")

    if cluster_counts:
        lines.append("")
        lines.append("Top 10 Affected Clusters:")
        for cluster, count in sorted(cluster_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            lines.append(f"  {cluster}: {count}")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='List PagerDuty incidents for T-CaaS team',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Last 7 days
  %(prog)s --since 2026-01-22

  # All active incidents (no time limit)
  %(prog)s --status triggered,acknowledged

  # Filter by cluster name (automatically fetches up to 10000 incidents)
  %(prog)s --since 2026-01-01 --until 2026-01-31 --cluster czthpc2-mco-prod

  # Filter by site
  %(prog)s --since 2026-01-22 --site hc-czthpc2

  # Get summary for specific cluster
  %(prog)s --since 2026-01-01 --cluster atgraf1-ndl-prod --format summary

  # JSON output
  %(prog)s --since 2026-01-22 --format json
        """
    )

    parser.add_argument('--since',
                       help='Start date (YYYY-MM-DD or ISO 8601). Default: 24 hours ago (or no limit for active incidents)')
    parser.add_argument('--until',
                       help='End date (YYYY-MM-DD or ISO 8601). Default: now')
    parser.add_argument('--status',
                       help='Comma-separated statuses: triggered,acknowledged,resolved')
    parser.add_argument('--cluster',
                       help='Filter by cluster name (partial match)')
    parser.add_argument('--site',
                       help='Filter by site name (partial match)')
    parser.add_argument('--all', action='store_true',
                       help='Show all incidents (no time limit)')
    parser.add_argument('--max', type=int, default=None,
                       help='Maximum results to fetch (default: 1000, or 10000 when filtering by cluster/site)')
    parser.add_argument('--format', choices=['table', 'json', 'summary'], default='table',
                       help='Output format (default: table)')
    parser.add_argument('--no-url', action='store_true',
                       help='Hide incident URLs in output')

    args = parser.parse_args()

    # Initialize client
    try:
        client = PagerDutyClient()
    except PagerDutyError as e:
        error_exit(str(e))

    # Parse dates
    since = args.since
    until = args.until

    # Handle statuses
    statuses = None
    active_only = False
    if args.status:
        statuses = [s.strip() for s in args.status.split(',')]
        # Check if filtering only active statuses
        if 'resolved' not in statuses:
            active_only = True

    # Apply default time filter (24 hours) only if:
    # - Not --all flag
    # - Not filtering active-only statuses
    # - User didn't explicitly set --since
    if not args.all and not active_only and not since:
        now = datetime.now(timezone.utc)
        since = (now - timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%SZ')
        until = now.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Format dates if provided as YYYY-MM-DD
    since = parse_date(since) if since else None
    until = parse_date(until, end_of_day=True) if until else None

    # Determine max_results: use larger default when filtering by cluster/site
    # to ensure we don't miss incidents that are further in the pagination
    max_results = args.max
    if max_results is None:
        # Default to 10000 if filtering by cluster/site, otherwise 1000
        max_results = 10000 if (args.cluster or args.site) else 1000

    # Fetch incidents
    try:
        incidents = client.get_incidents(
            since=since,
            until=until,
            statuses=statuses,
            max_results=max_results
        )
    except PagerDutyError as e:
        error_exit(str(e))

    # Filter by cluster/site
    if args.cluster or args.site:
        incidents = filter_incidents(incidents, cluster=args.cluster, site=args.site)

    # Output
    if args.format == 'json':
        format_json(incidents)
    elif args.format == 'summary':
        print(format_summary(incidents))
    else:
        print(f'Found {len(incidents)} incident(s)')
        print()

        if not incidents:
            print('No incidents found.')
        else:
            for inc in incidents:
                print(format_incident(inc, client, show_url=not args.no_url))
                print()


if __name__ == '__main__':
    main()
