#!/usr/bin/env python3
"""
PagerDuty to Jira Ticket Creation Script
Create well-formatted Jira tickets from PagerDuty incident analysis.

Usage:
  # Single incident mode
  pd-create-jira.py --incident Q32G3MTCMP2QBZ --project CAASPROD

  # Pattern analysis mode
  pd-create-jira.py --pattern --since "2026-02-03" --until "2026-02-03" --project CAASPROD

  # Dry-run (preview only)
  pd-create-jira.py --incident Q32G3MTCMP2QBZ --dry-run
"""

import sys
import os
import argparse
import subprocess
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from pd_common import (
    PagerDutyClient,
    PagerDutyError,
    parse_cluster_from_title,
    get_date_range,
    error_exit
)
from pd_jira_templates import (
    JiraTicketFormatter,
    SingleIncidentTemplate,
    PatternAnalysisTemplate
)


class IncidentAnalyzer:
    """Analyze incidents for patterns and correlations."""

    def __init__(self, client: PagerDutyClient):
        self.client = client

    def find_related_incidents(self, incident: Dict[str, Any],
                               time_window_hours: int = 24) -> List[Dict[str, Any]]:
        """Find incidents related to the given incident."""
        title = incident.get('title', '')
        created = incident.get('created_at', '')

        cluster_info = parse_cluster_from_title(title)
        if not cluster_info:
            return []

        alert_name = cluster_info.get('alert_name', '')
        cluster = cluster_info.get('cluster', '')

        # Get incidents in time window
        created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
        since = (created_dt - timedelta(hours=time_window_hours)).strftime('%Y-%m-%dT%H:%M:%SZ')
        until = (created_dt + timedelta(hours=time_window_hours)).strftime('%Y-%m-%dT%H:%M:%SZ')

        incidents = self.client.get_incidents(since=since, until=until, max_results=500)

        # Filter for same alert name and cluster
        related = []
        for inc in incidents:
            if inc['id'] == incident['id']:
                continue

            inc_cluster_info = parse_cluster_from_title(inc.get('title', ''))
            if inc_cluster_info:
                if (inc_cluster_info.get('alert_name', '') == alert_name and
                    inc_cluster_info.get('cluster', '') == cluster):
                    related.append(inc)

        # Sort by created time
        related.sort(key=lambda x: x.get('created_at', ''))
        return related

    def analyze_patterns(self, incidents: List[Dict[str, Any]],
                        filter_text: str = None) -> Dict[str, Any]:
        """Analyze incidents for patterns."""
        # Filter incidents if needed
        if filter_text:
            incidents = [
                inc for inc in incidents
                if filter_text.lower() in inc.get('title', '').lower()
            ]

        # Group by alert name
        by_alert = defaultdict(list)
        by_cluster = defaultdict(list)

        for inc in incidents:
            cluster_info = parse_cluster_from_title(inc.get('title', ''))
            if cluster_info:
                alert = cluster_info.get('alert_name', 'Unknown')
                cluster = cluster_info.get('cluster', 'Unknown')
                by_alert[alert].append(inc)
                by_cluster[cluster].append(inc)

        # Find flapping alerts
        flapping = {}
        for alert, alert_incidents in by_alert.items():
            if len(alert_incidents) >= 3:
                # Check if incidents are close together (flapping)
                times = sorted([
                    datetime.fromisoformat(inc['created_at'].replace('Z', '+00:00'))
                    for inc in alert_incidents
                ])

                # Calculate average interval
                if len(times) > 1:
                    intervals = [(times[i+1] - times[i]).total_seconds() / 60
                                for i in range(len(times) - 1)]
                    avg_interval = sum(intervals) / len(intervals)

                    if avg_interval < 60:  # Less than 1 hour average
                        flapping[alert] = {
                            'count': len(alert_incidents),
                            'avg_interval_minutes': int(avg_interval),
                            'incidents': alert_incidents
                        }

        return {
            'total': len(incidents),
            'by_alert': dict(by_alert),
            'by_cluster': dict(by_cluster),
            'flapping': flapping,
            'top_alerts': sorted(by_alert.items(), key=lambda x: len(x[1]), reverse=True)[:5],
            'top_clusters': sorted(by_cluster.items(), key=lambda x: len(x[1]), reverse=True)[:5]
        }


def generate_single_incident_ticket(client: PagerDutyClient, incident_id: str) -> Dict[str, str]:
    """Generate ticket for a single incident."""
    try:
        incident = client.get_incident(incident_id)
    except PagerDutyError as e:
        error_exit(f"Failed to fetch incident: {e}")

    # Find related incidents
    analyzer = IncidentAnalyzer(client)
    related = analyzer.find_related_incidents(incident)

    # Generate ticket content
    formatter = JiraTicketFormatter()
    template = SingleIncidentTemplate(formatter)
    description = template.generate(incident, related)

    # Generate summary
    title = incident.get('title', 'PagerDuty Incident')
    cluster_info = parse_cluster_from_title(title)

    if cluster_info:
        alert_name = cluster_info['alert_name']
        cluster = cluster_info['cluster']
        summary = f"Investigate {alert_name} on {cluster}"
    else:
        summary = f"Investigate PagerDuty incident #{incident.get('incident_number', 'N/A')}"

    return {
        'summary': summary,
        'description': description,
        'labels': ['tdi-caas-operations']
    }


def generate_pattern_ticket(client: PagerDutyClient, since: str, until: str,
                           filter_text: str = None) -> Dict[str, str]:
    """Generate ticket for pattern analysis."""
    # Initialize formatter
    formatter = JiraTicketFormatter()

    # Fetch incidents
    incidents = client.get_incidents(since=since, until=until, max_results=1000)

    if not incidents:
        error_exit("No incidents found in the specified time range")

    # Analyze patterns
    analyzer = IncidentAnalyzer(client)
    analysis = analyzer.analyze_patterns(incidents, filter_text)

    # Build pattern data for template
    flapping = analysis['flapping']

    if not flapping:
        error_exit("No flapping patterns detected. Try adjusting the time range or filter.")

    # Build summary
    date_range = f"{since[:10]} to {until[:10]}" if since and until else "specified period"
    summary_text = f"Analysis of PagerDuty incidents from {date_range} shows {analysis['total']} incidents"

    if filter_text:
        summary_text += f" matching '{filter_text}'"

    summary_text += " with significant alert noise from flapping alerts:\n\n"

    # Add flapping details
    for alert, data in sorted(flapping.items(), key=lambda x: x[1]['count'], reverse=True):
        count = data['count']
        interval = data['avg_interval_minutes']
        pct = int((count / analysis['total']) * 100)
        summary_text += f"* {formatter.bold(f'{count} incidents ({pct}%)')}: {alert} (flapping every ~{interval} min)\n"

    summary_text += f"\n{formatter.bold('Total flapping')}: {sum(d['count'] for d in flapping.values())} incidents "
    summary_text += f"({int((sum(d['count'] for d in flapping.values()) / analysis['total']) * 100)}% of total)\n"

    # Collect sample incidents for references
    sample_incidents = []
    for alert, data in list(flapping.items())[:3]:  # Top 3 flapping alerts
        sample_incidents.extend(data['incidents'][:3])  # 3 samples each

    # Build solution
    solution_text = "h3. Recommended Actions\n\n"
    solution_text += "# {bold}Implement alert deduplication{bold} - Configure AlertManager to group repeated alerts within time windows\n"
    solution_text += "# {bold}Fix root causes{bold} - Priority on most affected clusters/services\n"
    solution_text += "# {bold}Adjust alert thresholds{bold} - Review and tune sensitivity to reduce false positives\n"
    solution_text += "# {bold}Add auto-remediation{bold} - For known transient issues\n"

    solution_text = solution_text.replace('{bold}', '*')

    # Build recommendations (acceptance criteria)
    recommendations = [
        "Alert deduplication configured in AlertManager",
        "Root causes addressed for top flapping alerts",
        "Daily incident count reduced by at least 30%",
        "Verify no new alert gaps introduced"
    ]

    # Statistics for analysis section
    statistics = {
        'Total Incidents': str(analysis['total']),
        'Flapping Patterns': str(len(flapping)),
        'Most Affected Clusters': ', '.join([f"{name} ({len(incs)})" for name, incs in analysis['top_clusters'][:3]]),
    }

    # Generate ticket (formatter already initialized above)
    template = PatternAnalysisTemplate(formatter)

    pattern_data = {
        'title': 'Recurring Alert Pattern Analysis',
        'summary': summary_text,
        'incidents': sample_incidents,
        'statistics': statistics,
        'solution': solution_text,
        'recommendations': recommendations
    }

    description = template.generate(pattern_data)

    # Generate summary
    top_alert = list(flapping.keys())[0] if flapping else 'alerts'
    summary = f"Reduce alert noise: {len(flapping)} flapping patterns detected ({top_alert} and others)"

    return {
        'summary': summary,
        'description': description,
        'labels': ['tdi-caas-operations']
    }


def create_jira_ticket(ticket_data: Dict[str, str], project: str, issue_type: str,
                      assignee: str = None, dry_run: bool = False) -> Optional[str]:
    """Create Jira ticket using jira-create.py."""
    if dry_run:
        print("=== DRY RUN MODE ===")
        print(f"\nProject: {project}")
        print(f"Type: {issue_type}")
        print(f"Assignee: {assignee or 'Unassigned'}")
        print(f"Labels: {', '.join(ticket_data.get('labels', []))}")
        print(f"\nSummary:\n{ticket_data['summary']}")
        print(f"\nDescription:\n{ticket_data['description']}")
        return None

    # Build command
    jira_script = os.path.join(os.path.dirname(__file__), '../../telekom-jira/scripts/jira-create.py')

    cmd = [
        sys.executable,
        jira_script,
        '--project', project,
        '--type', issue_type,
        '--summary', ticket_data['summary'],
        '--description', ticket_data['description']
    ]

    if ticket_data.get('labels'):
        cmd.extend(['--labels', ','.join(ticket_data['labels'])])

    if assignee:
        cmd.extend(['--assignee', assignee])

    # Execute
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)

        # Extract issue key from output
        for line in result.stdout.split('\n'):
            if 'Issue created:' in line:
                return line.split()[-1]

        return None
    except subprocess.CalledProcessError as e:
        error_exit(f"Failed to create Jira ticket: {e.stderr}")


def main():
    parser = argparse.ArgumentParser(
        description='Create Jira tickets from PagerDuty incidents',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single incident ticket
  %(prog)s --incident Q32G3MTCMP2QBZ --project CAASPROD --assignee "user@t-systems.com"

  # Pattern analysis ticket
  %(prog)s --pattern --since "2026-02-03" --until "2026-02-03" --project CAASPROD

  # With filter
  %(prog)s --pattern --since "2026-02-03" --filter "NetworkError" --project CAASPROD

  # Dry-run (preview only)
  %(prog)s --incident Q32G3MTCMP2QBZ --dry-run
        """
    )

    # Mode selection
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--incident', metavar='ID',
                           help='Single incident mode - PagerDuty incident ID')
    mode_group.add_argument('--pattern', action='store_true',
                           help='Pattern analysis mode')

    # Pattern mode options
    parser.add_argument('--since', metavar='DATE',
                       help='Start date for pattern analysis (YYYY-MM-DD)')
    parser.add_argument('--until', metavar='DATE',
                       help='End date for pattern analysis (YYYY-MM-DD)')
    parser.add_argument('--filter', metavar='TEXT',
                       help='Filter incidents by text in title')

    # Jira options
    parser.add_argument('--project', default='CAASPROD',
                       help='Jira project key (default: CAASPROD)')
    parser.add_argument('--type', default='Task',
                       help='Issue type (default: Task)')
    parser.add_argument('--assignee',
                       help='Assignee username/email')

    # Execution options
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview ticket without creating')

    args = parser.parse_args()

    # Validate pattern mode arguments
    if args.pattern and not (args.since or args.until):
        error_exit("Pattern mode requires --since and/or --until")

    # Initialize PagerDuty client
    try:
        client = PagerDutyClient()
    except PagerDutyError as e:
        error_exit(str(e))

    # Generate ticket
    if args.incident:
        print(f"Fetching incident {args.incident}...")
        ticket_data = generate_single_incident_ticket(client, args.incident)
    else:
        # Pattern mode
        since, until = get_date_range(args.since, args.until, days_ago=1)
        print(f"Analyzing incidents from {since[:10]} to {until[:10]}...")
        ticket_data = generate_pattern_ticket(client, since, until, args.filter)

    # Create ticket
    issue_key = create_jira_ticket(
        ticket_data,
        args.project,
        args.type,
        args.assignee,
        args.dry_run
    )

    if issue_key and not args.dry_run:
        print(f"\n✓ Ticket created successfully: {issue_key}")


if __name__ == '__main__':
    main()
