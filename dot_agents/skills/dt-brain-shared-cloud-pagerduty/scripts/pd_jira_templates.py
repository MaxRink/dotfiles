#!/usr/bin/env python3
"""
PagerDuty to Jira Ticket Template System
Generates Confluence wiki markup formatted tickets from PagerDuty incidents.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import re


class JiraTicketFormatter:
    """Format PagerDuty incident data into Confluence wiki markup."""

    def __init__(self):
        self.pd_web_url = "https://dt-tdi.eu.pagerduty.com"

    def h2(self, text: str) -> str:
        """Create h2 header."""
        return f"h2. {text}\n\n"

    def bold(self, text: str) -> str:
        """Create bold text."""
        return f"*{text}*"

    def bullet(self, text: str, level: int = 0) -> str:
        """Create bullet point."""
        prefix = "*" * (level + 1)
        return f"{prefix} {text}\n"

    def numbered(self, text: str) -> str:
        """Create numbered list item."""
        return f"# {text}\n"

    def checkbox(self, text: str, checked: bool = False) -> str:
        """Create checkbox item."""
        marker = "x" if checked else " "
        return f"* [{marker}] {text}\n"

    def code_block(self, code: str, language: str = "yaml") -> str:
        """Create code block."""
        return f"{{code:{language}}}\n{code}\n{{code}}\n\n"

    def table_header(self, headers: List[str]) -> str:
        """Create table header row."""
        return "|| " + " || ".join(headers) + " ||\n"

    def table_row(self, cells: List[str]) -> str:
        """Create table data row."""
        return "| " + " | ".join(cells) + " |\n"

    def link(self, text: str, url: str) -> str:
        """Create hyperlink."""
        return f"[{text}|{url}]"

    def incident_link(self, incident_number: str, incident_id: str) -> str:
        """Create formatted PagerDuty incident link."""
        url = f"{self.pd_web_url}/incidents/{incident_id}"
        return self.link(f"Incident #{incident_number}", url)

    def format_incident_reference(self, incidents: List[Dict[str, Any]]) -> str:
        """Format PagerDuty references section."""
        content = self.h2("PagerDuty References")

        for inc in incidents:
            inc_num = inc.get('incident_number', 'N/A')
            inc_id = inc.get('id', '')
            title = inc.get('title', 'No title')
            created = inc.get('created_at', '')

            # Format timestamp
            if created:
                dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                created_str = dt.strftime('%Y-%m-%d %H:%M UTC')
            else:
                created_str = 'Unknown time'

            content += self.bullet(
                f"{self.incident_link(inc_num, inc_id)} - {title} ({created_str})"
            )

        content += "\n"
        return content

    def format_problem_section(self, description: str, incidents: List[Dict[str, Any]] = None) -> str:
        """Format Problem section."""
        content = self.h2("Problem")
        content += description + "\n\n"

        if incidents and len(incidents) == 1:
            inc = incidents[0]
            inc_num = inc.get('incident_number', 'N/A')
            inc_id = inc.get('id', '')
            created = inc.get('created_at', '')

            if created:
                dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                created_str = dt.strftime('%Y-%m-%d %H:%M UTC')
            else:
                created_str = 'Unknown time'

            content += f"Incident {self.incident_link(inc_num, inc_id)} occurred on {created_str}.\n\n"

        return content

    def format_analysis_section(self, analysis: Dict[str, Any]) -> str:
        """Format Analysis section with key-value pairs."""
        content = self.h2("Analysis")

        for key, value in analysis.items():
            if isinstance(value, list):
                content += f"{self.bold(key)}:\n"
                for item in value:
                    content += self.bullet(item)
                content += "\n"
            else:
                content += f"{self.bold(key)}: {value}\n"

        content += "\n"
        return content

    def format_solution_section(self, solution_text: str, is_numbered: bool = True) -> str:
        """Format Solution section."""
        content = self.h2("Solution")
        content += solution_text + "\n\n"
        return content

    def format_acceptance_criteria(self, criteria: List[str]) -> str:
        """Format Acceptance Criteria section."""
        content = self.h2("Acceptance Criteria")

        for criterion in criteria:
            content += self.checkbox(criterion)

        content += "\n"
        return content


class SingleIncidentTemplate:
    """Template for single incident tickets."""

    def __init__(self, formatter: JiraTicketFormatter):
        self.fmt = formatter

    def generate(self, incident: Dict[str, Any], related: List[Dict[str, Any]] = None) -> str:
        """Generate ticket description for a single incident."""
        title = incident.get('title', 'No title')
        description = incident.get('description', '')
        status = incident.get('status', 'unknown')
        urgency = incident.get('urgency', 'unknown')
        service = incident.get('service', {}).get('summary', 'Unknown')
        created = incident.get('created_at', '')
        resolved = incident.get('resolved_at', '')

        # Parse cluster/site from title
        cluster_info = self._parse_cluster_info(title)

        # Build problem description
        problem_desc = f"{description}\n\n"

        if cluster_info:
            problem_desc += f"{self.fmt.bold('Alert')}: {cluster_info['alert_name']}\n"
            problem_desc += f"{self.fmt.bold('Cluster')}: {cluster_info['cluster']}\n"
            problem_desc += f"{self.fmt.bold('Site')}: {cluster_info['site']}\n\n"

        problem_desc += f"{cluster_info['description']}" if cluster_info else title

        content = self.fmt.format_problem_section(problem_desc, [incident])

        # Analysis section
        analysis = {
            'Status': status.title(),
            'Service': service,
            'Urgency': urgency.title()
        }

        if resolved and created:
            created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
            resolved_dt = datetime.fromisoformat(resolved.replace('Z', '+00:00'))
            duration = resolved_dt - created_dt
            minutes = int(duration.total_seconds() / 60)
            analysis['Duration'] = f"Resolved automatically after {minutes} minutes"

        # Add related incidents if found
        if related and len(related) > 0:
            analysis['Related Incidents'] = [
                f"{self.fmt.incident_link(r.get('incident_number', '?'), r.get('id', ''))} - "
                f"{datetime.fromisoformat(r.get('created_at', '').replace('Z', '+00:00')).strftime('%H:%M UTC')}"
                for r in related[:5]  # Limit to 5
            ]

        content += self.fmt.format_analysis_section(analysis)

        # Solution section
        solution = self._generate_solution(cluster_info)
        content += self.fmt.format_solution_section(solution)

        # Acceptance criteria
        criteria = self._generate_acceptance_criteria(cluster_info, len(related) if related else 0)
        content += self.fmt.format_acceptance_criteria(criteria)

        return content

    def _parse_cluster_info(self, title: str) -> Optional[Dict[str, str]]:
        """Parse cluster/site/alert from incident title."""
        match = re.match(r'\[([^\|]+)\s*\|\s*([^\]]+)\]\s*(\S+)\s*(.*)', title)
        if match:
            return {
                'site': match.group(1).strip(),
                'cluster': match.group(2).strip(),
                'alert_name': match.group(3).strip(),
                'description': match.group(4).strip()
            }
        return None

    def _generate_solution(self, cluster_info: Optional[Dict[str, str]]) -> str:
        """Generate solution steps based on alert type."""
        if not cluster_info:
            return "Investigate the following:\n# Review incident details and logs\n# Identify root cause\n# Implement fix\n# Monitor for recurrence"

        alert = cluster_info.get('alert_name', '').lower()

        # Alert-specific solutions
        if 'network' in alert:
            return (
                "Investigate the following:\n"
                "# Check node network interface status\n"
                "# Review network metrics for anomalies\n"
                "# Determine if metric collection is broken\n"
                "# Consider adjusting alert threshold or adding deduplication"
            )
        elif 'targetdown' in alert or 'target_down' in alert:
            return (
                "Investigate the following:\n"
                "# Check target service/pod status\n"
                "# Review service discovery configuration\n"
                "# Verify network connectivity to target\n"
                "# Check for resource constraints (CPU/memory)\n"
                "# Consider adding deduplication for flapping alerts"
            )
        elif 'pod' in alert and 'ready' in alert:
            return (
                "Investigate the following:\n"
                "# Check pod logs for errors\n"
                "# Review pod events (kubectl describe)\n"
                "# Verify readiness probe configuration\n"
                "# Check for resource constraints\n"
                "# Review related deployment/statefulset"
            )
        elif 'node' in alert and 'ready' in alert:
            return (
                "Investigate the following:\n"
                "# Check node status and conditions\n"
                "# Review kubelet logs\n"
                "# Verify network connectivity\n"
                "# Check system resources (disk, memory, CPU)\n"
                "# Review recent system changes"
            )
        else:
            return (
                "Investigate the following:\n"
                "# Review alert definition and thresholds\n"
                "# Check affected component status\n"
                "# Identify root cause\n"
                "# Implement fix or adjust monitoring\n"
                "# Monitor for recurrence"
            )

    def _generate_acceptance_criteria(self, cluster_info: Optional[Dict[str, str]],
                                     related_count: int) -> List[str]:
        """Generate acceptance criteria based on incident type."""
        criteria = ["Root cause identified"]

        if related_count > 0:
            criteria.append("Fix implemented or alert deduplication configured")
            criteria.append("No recurrence for 7 days")
        else:
            criteria.append("Fix implemented or alert threshold adjusted")
            criteria.append("Verified in production")

        return criteria


class PatternAnalysisTemplate:
    """Template for pattern/recurring issue tickets."""

    def __init__(self, formatter: JiraTicketFormatter):
        self.fmt = formatter

    def generate(self, pattern_data: Dict[str, Any]) -> str:
        """Generate ticket description for pattern analysis."""
        title = pattern_data.get('title', 'Recurring Alert Pattern')
        summary = pattern_data.get('summary', '')
        incidents = pattern_data.get('incidents', [])
        statistics = pattern_data.get('statistics', {})
        solution = pattern_data.get('solution', '')
        recommendations = pattern_data.get('recommendations', [])

        # Problem section
        content = self.fmt.format_problem_section(summary)

        # PagerDuty References
        if incidents:
            content += self.fmt.format_incident_reference(incidents[:10])  # Limit to 10

        # Statistics section (as Analysis)
        if statistics:
            content += self.fmt.format_analysis_section(statistics)

        # Solution section
        if solution:
            content += self.fmt.format_solution_section(solution, is_numbered=False)

        # Recommendations as acceptance criteria
        if recommendations:
            content += self.fmt.format_acceptance_criteria(recommendations)

        return content
