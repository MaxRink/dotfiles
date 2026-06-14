#!/usr/bin/env python3
"""
PagerDuty Incident Report Generator
Usage: pd-report.py [--since DATE] [--until DATE] [--output FILE] [--format FORMAT] [--pdf]
"""

import argparse
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Any

from pd_common import (
    PagerDutyClient, PagerDutyError, error_exit, get_date_range,
    parse_cluster_from_title, extract_country_from_site
)

# Get the repository root (for default output path)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent


def generate_markdown_report(
    incidents: List[Dict[str, Any]],
    since_date: str,
    until_date: str,
    web_url: str
) -> str:
    """Generate markdown report from incidents."""
    now = datetime.now(timezone.utc)
    lines = []

    # Header
    lines.append("# T-CaaS Incident Report")
    lines.append("")
    if since_date == until_date:
        lines.append(f"**Date:** {since_date}")
    else:
        lines.append(f"**Date Range:** {since_date} to {until_date}")
    lines.append(f"**Report Generated:** {now.strftime('%Y-%m-%d %H:%M')} UTC")
    lines.append("**Team:** T-CaaS")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Executive Summary
    total = len(incidents)
    status_counts = Counter(inc.get('status') for inc in incidents)
    urgency_counts = Counter(inc.get('urgency') for inc in incidents)

    resolved = status_counts.get('resolved', 0)
    triggered = status_counts.get('triggered', 0)
    acknowledged = status_counts.get('acknowledged', 0)
    open_count = triggered + acknowledged
    high_urgency = urgency_counts.get('high', 0)
    low_urgency = urgency_counts.get('low', 0)

    lines.append("## Executive Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| **Total Incidents** | {total} |")
    if total > 0:
        lines.append(f"| **Resolved** | {resolved} ({resolved*100//total}%) |")
        lines.append(f"| **Triggered (Open)** | {open_count} ({open_count*100//total}%) |")
        lines.append(f"| **High Urgency** | {high_urgency} ({high_urgency*100//total}%) |")
        lines.append(f"| **Low Urgency** | {low_urgency} ({low_urgency*100//total}%) |")
    else:
        lines.append("| **Resolved** | 0 (0%) |")
        lines.append("| **Triggered (Open)** | 0 (0%) |")
        lines.append("| **High Urgency** | 0 (0%) |")
        lines.append("| **Low Urgency** | 0 (0%) |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Incidents by Service
    service_counts = Counter(
        inc.get('service', {}).get('summary', 'Unknown') for inc in incidents
    )
    lines.append("## Incidents by Service")
    lines.append("")
    lines.append("| Service | Count | Percentage |")
    lines.append("|---------|-------|------------|")
    for service, count in service_counts.most_common():
        pct = count * 100 // total if total > 0 else 0
        lines.append(f"| {service} | {count} | {pct}% |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Open Incidents
    open_incidents = [
        inc for inc in incidents if inc.get('status') in ('triggered', 'acknowledged')
    ]
    lines.append("## Open Incidents (Triggered/Acknowledged)")
    lines.append("")
    if open_incidents:
        lines.append("| # | Incident | Service | Urgency | Assigned | URL |")
        lines.append("|---|----------|---------|---------|----------|-----|")
        for i, inc in enumerate(open_incidents, 1):
            number = inc.get('incident_number', 'N/A')
            title = inc.get('title', 'No title')
            title_display = title[:60] + ('...' if len(title) > 60 else '')
            service = inc.get('service', {}).get('summary', 'Unknown')
            urgency = inc.get('urgency', 'unknown').upper()
            assignees = [a.get('assignee', {}).get('summary', '') for a in inc.get('assignments', [])]
            assignee_str = ', '.join(assignees) if assignees else 'Unassigned'
            inc_id = inc.get('id', '')
            url = f"[#{number}]({web_url}/incidents/{inc_id})"
            lines.append(f"| {i} | {title_display} | {service} | {urgency} | {assignee_str} | {url} |")
    else:
        lines.append("*No open incidents*")
    lines.append("")
    lines.append("---")
    lines.append("")

    # High Urgency Incidents Summary
    high_incidents = [inc for inc in incidents if inc.get('urgency') == 'high']
    lines.append("## High Urgency Incidents Summary")
    lines.append("")
    if high_incidents:
        # Group by alert type
        alert_groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for inc in high_incidents:
            parsed = parse_cluster_from_title(inc.get('title', ''))
            alert_name = parsed['alert_name'] if parsed else 'Unknown'
            alert_groups[alert_name].append(inc)

        for alert_name, group in sorted(alert_groups.items(), key=lambda x: -len(x[1])):
            lines.append(f"### {alert_name} ({len(group)} incidents)")
            lines.append("")
            clusters = set()
            for inc in group[:5]:
                parsed = parse_cluster_from_title(inc.get('title', ''))
                if parsed:
                    clusters.add(parsed['cluster'])
            lines.append(f"Affected clusters: {', '.join(clusters)}")
            lines.append("")
    else:
        lines.append("*No high urgency incidents*")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Incidents by Alert Type
    alert_counts: Counter = Counter()
    for inc in incidents:
        parsed = parse_cluster_from_title(inc.get('title', ''))
        alert_name = parsed['alert_name'] if parsed else 'Unknown'
        alert_counts[alert_name] += 1

    lines.append("## Incidents by Alert Type")
    lines.append("")
    lines.append("| Alert Type | Count |")
    lines.append("|------------|-------|")
    for alert_type, count in alert_counts.most_common(15):
        lines.append(f"| {alert_type} | {count} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Affected Sites
    site_counts: Counter = Counter()
    for inc in incidents:
        parsed = parse_cluster_from_title(inc.get('title', ''))
        site = parsed['site'] if parsed else 'Unknown'
        site_counts[site] += 1

    lines.append("## Affected Sites")
    lines.append("")
    lines.append("| Site | Incidents |")
    lines.append("|------|-----------|")
    for site, count in site_counts.most_common():
        lines.append(f"| {site} | {count} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Timeline of Significant Events
    lines.append("## Timeline of Significant Events")
    lines.append("")

    hourly_events: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for inc in sorted(high_incidents, key=lambda x: x.get('created_at', '')):
        created = inc.get('created_at', '')
        if created:
            try:
                dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                hour_key = dt.strftime('%Y-%m-%d %H:00')
                hourly_events[hour_key].append(inc)
            except (ValueError, AttributeError):
                pass

    if hourly_events:
        lines.append("| Time (UTC) | Event |")
        lines.append("|------------|-------|")
        for hour, events in sorted(hourly_events.items()):
            alert_summary = Counter()
            for inc in events:
                parsed = parse_cluster_from_title(inc.get('title', ''))
                alert_name = parsed['alert_name'] if parsed else 'Unknown'
                alert_summary[alert_name] += 1
            event_str = ', '.join(f"{name}: {cnt}" for name, cnt in alert_summary.most_common(3))
            lines.append(f"| {hour} | {len(events)} high urgency: {event_str} |")
    else:
        lines.append("*No significant events*")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Recommendations
    lines.append("## Recommendations")
    lines.append("")
    recommendations = []
    if alert_counts:
        top_alert, top_count = alert_counts.most_common(1)[0]
        if top_count >= 3:
            recommendations.append(f"1. **{top_alert}** - Investigate root cause ({top_count} occurrences)")
    if open_count > 0:
        recommendations.append(f"2. **Open Incidents** - {open_count} incidents require attention")
    if site_counts:
        top_site, site_count = site_counts.most_common(1)[0]
        if site_count >= 3 and top_site != 'Unknown':
            recommendations.append(f"3. **{top_site}** - Site has elevated incident count ({site_count} incidents)")

    if recommendations:
        for rec in recommendations:
            lines.append(rec)
    else:
        lines.append("*No specific recommendations based on the data*")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Full Incident List (collapsible)
    lines.append("## Full Incident List")
    lines.append("")
    lines.append(f"<details>")
    lines.append(f"<summary>Click to expand ({total} incidents)</summary>")
    lines.append("")

    # Group by country/region
    country_groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for inc in incidents:
        parsed = parse_cluster_from_title(inc.get('title', ''))
        site = parsed['site'] if parsed else 'Unknown'
        country = extract_country_from_site(site)
        country_groups[country].append(inc)

    for country in sorted(country_groups.keys()):
        group = country_groups[country]
        lines.append(f"### {country} ({len(group)} incidents)")
        lines.append("")
        lines.append("| # | Title | Cluster | Status | Urgency | Time |")
        lines.append("|---|-------|---------|--------|---------|------|")
        for inc in sorted(group, key=lambda x: x.get('created_at', '')):
            number = inc.get('incident_number', 'N/A')
            title = inc.get('title', 'No title')
            parsed = parse_cluster_from_title(title)
            cluster = (parsed['cluster'][:25] if parsed else 'Unknown')
            alert_name = parsed['alert_name'] if parsed else title.split()[0] if title else 'Unknown'
            status = inc.get('status', 'unknown')
            urgency = inc.get('urgency', 'unknown')
            created = inc.get('created_at', '')[:16].replace('T', ' ')
            alert_display = alert_name[:30] + ('...' if len(alert_name) > 30 else '')
            lines.append(f"| #{number} | {alert_display} | {cluster} | {status} | {urgency} | {created} |")
        lines.append("")

    lines.append("</details>")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Report generated automatically from PagerDuty data*")

    return '\n'.join(lines)


def generate_confluence_report(
    incidents: List[Dict[str, Any]],
    since_date: str,
    until_date: str,
    web_url: str
) -> str:
    """Generate Confluence wiki markup report from incidents."""
    now = datetime.now(timezone.utc)
    lines = []

    # Header
    lines.append("h1. T-CaaS Incident Report")
    lines.append("")
    if since_date == until_date:
        lines.append(f"*Date:* {since_date}")
    else:
        lines.append(f"*Date Range:* {since_date} to {until_date}")
    lines.append(f"*Report Generated:* {now.strftime('%Y-%m-%d %H:%M')} UTC")
    lines.append("*Team:* T-CaaS")
    lines.append("")
    lines.append("----")
    lines.append("")

    # Executive Summary
    total = len(incidents)
    status_counts = Counter(inc.get('status') for inc in incidents)
    urgency_counts = Counter(inc.get('urgency') for inc in incidents)

    resolved = status_counts.get('resolved', 0)
    triggered = status_counts.get('triggered', 0)
    acknowledged = status_counts.get('acknowledged', 0)
    open_count = triggered + acknowledged
    high_urgency = urgency_counts.get('high', 0)
    low_urgency = urgency_counts.get('low', 0)

    lines.append("h2. Executive Summary")
    lines.append("")
    lines.append("|| Metric || Value ||")
    lines.append(f"| *Total Incidents* | {total} |")
    if total > 0:
        lines.append(f"| *Resolved* | {resolved} ({resolved*100//total}%) |")
        lines.append(f"| *Triggered (Open)* | {open_count} ({open_count*100//total}%) |")
        lines.append(f"| *High Urgency* | {high_urgency} ({high_urgency*100//total}%) |")
        lines.append(f"| *Low Urgency* | {low_urgency} ({low_urgency*100//total}%) |")
    lines.append("")
    lines.append("----")
    lines.append("")

    # Incidents by Service
    service_counts = Counter(
        inc.get('service', {}).get('summary', 'Unknown') for inc in incidents
    )
    lines.append("h2. Incidents by Service")
    lines.append("")
    lines.append("|| Service || Count || Percentage ||")
    for service, count in service_counts.most_common():
        pct = count * 100 // total if total > 0 else 0
        lines.append(f"| {service} | {count} | {pct}% |")
    lines.append("")
    lines.append("----")
    lines.append("")

    # Open Incidents
    open_incidents = [
        inc for inc in incidents if inc.get('status') in ('triggered', 'acknowledged')
    ]
    lines.append("h2. Open Incidents (Triggered/Acknowledged)")
    lines.append("")
    if open_incidents:
        lines.append("|| # || Incident || Service || Urgency || Assigned || URL ||")
        for i, inc in enumerate(open_incidents, 1):
            number = inc.get('incident_number', 'N/A')
            title = inc.get('title', 'No title')[:60]
            service = inc.get('service', {}).get('summary', 'Unknown')
            urgency = inc.get('urgency', 'unknown').upper()
            assignees = [a.get('assignee', {}).get('summary', '') for a in inc.get('assignments', [])]
            assignee_str = ', '.join(assignees) if assignees else 'Unassigned'
            inc_id = inc.get('id', '')
            url = f"[#{number}|{web_url}/incidents/{inc_id}]"
            lines.append(f"| {i} | {title} | {service} | {urgency} | {assignee_str} | {url} |")
    else:
        lines.append("_No open incidents_")
    lines.append("")
    lines.append("----")
    lines.append("")

    # Incidents by Alert Type
    alert_counts: Counter = Counter()
    for inc in incidents:
        parsed = parse_cluster_from_title(inc.get('title', ''))
        alert_name = parsed['alert_name'] if parsed else 'Unknown'
        alert_counts[alert_name] += 1

    lines.append("h2. Incidents by Alert Type")
    lines.append("")
    lines.append("|| Alert Type || Count ||")
    for alert_type, count in alert_counts.most_common(15):
        lines.append(f"| {alert_type} | {count} |")
    lines.append("")
    lines.append("----")
    lines.append("")

    # Affected Sites
    site_counts: Counter = Counter()
    for inc in incidents:
        parsed = parse_cluster_from_title(inc.get('title', ''))
        site = parsed['site'] if parsed else 'Unknown'
        site_counts[site] += 1

    lines.append("h2. Affected Sites")
    lines.append("")
    lines.append("|| Site || Incidents ||")
    for site, count in site_counts.most_common():
        lines.append(f"| {site} | {count} |")
    lines.append("")
    lines.append("----")
    lines.append("")
    lines.append("_Report generated automatically from PagerDuty data_")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Generate PagerDuty incident report for T-CaaS team',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Yesterday's report (markdown)
  %(prog)s --pdf                              # Yesterday's report as PDF
  %(prog)s --pdf --since 2026-01-01 --until 2026-01-07
  %(prog)s --output reports/weekly.md
  %(prog)s --format confluence --output report.wiki
        """
    )

    parser.add_argument('--since', help='Start date (YYYY-MM-DD, default: yesterday)')
    parser.add_argument('--until', help='End date (YYYY-MM-DD, default: yesterday)')
    parser.add_argument('--output', '-o', help='Output file path (default: stdout for text, reports/ for PDF)')
    parser.add_argument('--format', '-f', choices=['markdown', 'confluence'],
                        default='markdown', help='Output format (default: markdown)')
    parser.add_argument('--pdf', action='store_true',
                        help='Generate PDF output with Telekom branding')

    args = parser.parse_args()

    # PDF format conflicts with confluence format
    if args.pdf and args.format == 'confluence':
        print("Error: --pdf cannot be used with --format confluence", file=sys.stderr)
        sys.exit(1)

    try:
        client = PagerDutyClient()
    except PagerDutyError as e:
        error_exit(str(e))

    # Calculate date range (default: yesterday)
    since, until = get_date_range(args.since, args.until, days_ago=1)

    print("Fetching incidents from PagerDuty...", file=sys.stderr)

    try:
        incidents = client.get_incidents(since=since, until=until, max_results=5000)
    except PagerDutyError as e:
        error_exit(str(e))

    print(f"Found {len(incidents)} incidents", file=sys.stderr)

    # Extract display dates
    since_display = since[:10] if since else 'N/A'
    until_display = until[:10] if until else 'N/A'

    # Generate report
    if args.format == 'confluence':
        report = generate_confluence_report(incidents, since_display, until_display, client.web_url)
    else:
        report = generate_markdown_report(incidents, since_display, until_display, client.web_url)

    # Handle PDF output
    if args.pdf:
        generate_pdf_report(report, since_display, until_display, args.output)
        return

    # Output text (markdown or confluence)
    if args.output:
        # Ensure output directory exists
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report written to: {args.output}", file=sys.stderr)
    else:
        print(report)


def generate_pdf_report(markdown_content: str, since_date: str, until_date: str, output_path: str = None):
    """Generate PDF report from markdown content."""
    # Import PDF utilities from the telekom-pdf skill
    pdf_skill_path = Path(__file__).resolve().parent.parent.parent / 'telekom-pdf' / 'scripts'
    sys.path.insert(0, str(pdf_skill_path))

    try:
        from pdf_common import generate_pdf_from_markdown
    except ImportError as e:
        print(f"Error: Could not import PDF utilities: {e}", file=sys.stderr)
        print("Make sure the telekom-pdf skill is available.", file=sys.stderr)
        sys.exit(1)

    # Determine output filename
    if output_path:
        pdf_path = output_path
    else:
        # Default: reports/tcaas-incidents-YYYY-MM-DD.pdf
        if since_date == until_date:
            filename = f"tcaas-incidents-{since_date}.pdf"
        else:
            filename = f"tcaas-incidents-{since_date}-to-{until_date}.pdf"
        pdf_path = REPO_ROOT / 'reports' / filename

    # Generate title
    if since_date == until_date:
        title = f"T-CaaS Incident Report - {since_date}"
    else:
        title = f"T-CaaS Incident Report - {since_date} to {until_date}"

    # Generate PDF
    print(f"Generating PDF report...", file=sys.stderr)
    output = generate_pdf_from_markdown(
        title=title,
        content=markdown_content,
        output=str(pdf_path),
        template='incident-report'
    )
    print(f"PDF report written to: {output}", file=sys.stderr)


if __name__ == '__main__':
    main()
