#!/usr/bin/env python3
"""
PagerDuty Get Incident Details Script
Usage: pd-incident-get.py INCIDENT_ID [--json]
"""

import argparse
import sys
from typing import Dict, Any

from pd_common import (
    PagerDutyClient, PagerDutyError, error_exit, output_json, format_datetime,
    STATUS_ICONS, TCAAS_TEAM_ID
)


def format_incident_details(inc: Dict[str, Any], client: PagerDutyClient) -> None:
    """Format and print detailed incident information."""
    number = inc.get('incident_number', 'N/A')
    inc_id = inc.get('id', '')
    title = inc.get('title', 'No title')
    status = inc.get('status', 'unknown')
    urgency = inc.get('urgency', 'unknown')
    created = format_datetime(inc.get('created_at', ''))
    resolved = format_datetime(inc.get('resolved_at', '')) if inc.get('resolved_at') else 'Not resolved'

    service = inc.get('service', {}).get('summary', 'Unknown')
    escalation = inc.get('escalation_policy', {}).get('summary', 'Unknown')

    assignees = [a.get('assignee', {}).get('summary', '') for a in inc.get('assignments', [])]
    assignee_str = ', '.join(assignees) if assignees else 'Unassigned'

    teams = [t.get('summary', '') for t in inc.get('teams', [])]
    teams_str = ', '.join(teams) if teams else 'None'

    description = inc.get('description', '-') or '-'

    # Acknowledgements
    acks = inc.get('acknowledgements', [])
    ack_info = []
    for ack in acks:
        acker = ack.get('acknowledger', {}).get('summary', 'Unknown')
        ack_at = format_datetime(ack.get('at', ''))
        ack_info.append(f'{acker} at {ack_at}')

    # Status formatting
    status_labels = {
        'triggered': '[!] TRIGGERED',
        'acknowledged': '[~] ACKNOWLEDGED',
        'resolved': '[+] RESOLVED'
    }
    status_display = status_labels.get(status, status.upper())
    urgency_tag = '[HIGH URGENCY]' if urgency == 'high' else '[Low Urgency]'

    print('=' * 70)
    print(f'Incident #{number} - {status_display} {urgency_tag}')
    print('=' * 70)
    print()
    print(f'Title:       {title}')
    print(f'ID:          {inc_id}')
    print(f'Service:     {service}')
    print(f'Escalation:  {escalation}')
    print(f'Teams:       {teams_str}')
    print()
    print(f'Created:     {created}')
    print(f'Resolved:    {resolved}')
    print(f'Assigned To: {assignee_str}')
    print()

    if ack_info:
        print('Acknowledgements:')
        for ack in ack_info:
            print(f'  - {ack}')
        print()

    print('Description:')
    print('-' * 40)
    lines = description.split('\n')[:20]
    for line in lines:
        print(f'  {line}')
    if description.count('\n') > 20:
        print('  ...(truncated)')
    print()

    print(f'URL: {client.incident_url(inc_id)}')


def main():
    parser = argparse.ArgumentParser(
        description='Get PagerDuty incident details',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s P1234567         # Get incident details
  %(prog)s P1234567 --json  # JSON output
        """
    )

    parser.add_argument('incident_id', metavar='INCIDENT_ID',
                        help='The incident ID (e.g., PXXXXXX)')
    parser.add_argument('--json', action='store_true', help='Output raw JSON')

    args = parser.parse_args()

    try:
        client = PagerDutyClient()
    except PagerDutyError as e:
        error_exit(str(e))

    try:
        incident = client.get_incident(args.incident_id)
    except PagerDutyError as e:
        if "404" in str(e):
            error_exit(f"Incident '{args.incident_id}' not found")
        error_exit(str(e))

    if not incident:
        error_exit(f"Incident '{args.incident_id}' not found")

    # Verify incident belongs to T-CaaS team
    team_ids = [t.get('id', '') for t in incident.get('teams', [])]
    if TCAAS_TEAM_ID not in team_ids:
        error_exit(f"Incident '{args.incident_id}' does not belong to T-CaaS team")

    # Output
    if args.json:
        output_json({"incident": incident})
    else:
        format_incident_details(incident, client)


if __name__ == '__main__':
    main()
