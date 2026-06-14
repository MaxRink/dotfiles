"""Output formatting utilities for Telekom Jira integration."""

import json
import sys
from typing import List, Dict, Any, Optional

from .config import JIRA_URL, CUSTOM_FIELDS


# ANSI color codes
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


def supports_color() -> bool:
    """Check if terminal supports color output."""
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


def colorize(text: str, color: str) -> str:
    """Apply color to text if terminal supports it."""
    if supports_color():
        return f"{color}{text}{Colors.RESET}"
    return text


def print_error(message: str) -> None:
    """Print an error message to stderr."""
    prefix = colorize("Error:", Colors.RED + Colors.BOLD)
    # Remove "Error:" from message if already present
    if message.lower().startswith("error:"):
        message = message[6:].strip()
    print(f"{prefix} {message}", file=sys.stderr)


def print_success(message: str) -> None:
    """Print a success message."""
    prefix = colorize("✓", Colors.GREEN)
    print(f"{prefix} {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    prefix = colorize("Warning:", Colors.YELLOW + Colors.BOLD)
    print(f"{prefix} {message}", file=sys.stderr)


def format_json(data: Any, indent: int = 2) -> str:
    """Format data as pretty-printed JSON."""
    return json.dumps(data, indent=indent, default=str)


def get_status_color(status: str) -> str:
    """Get color code for issue status."""
    status_lower = status.lower()
    if status_lower in ('done', 'closed', 'resolved'):
        return Colors.GREEN
    elif status_lower in ('in progress', 'in review'):
        return Colors.BLUE
    elif status_lower in ('to do', 'open', 'new'):
        return Colors.YELLOW
    return Colors.RESET


def format_issues_table(issues: List[Dict[str, Any]], total: Optional[int] = None) -> str:
    """
    Format a list of issues as a readable table.

    Args:
        issues: List of issue dictionaries from Jira API
        total: Total number of issues (for pagination info)

    Returns:
        str: Formatted table string
    """
    if total is None:
        total = len(issues)

    lines = []
    lines.append(f"Found {total} issues (showing {len(issues)})")
    lines.append("")

    for issue in issues:
        key = issue.get('key', 'N/A')
        fields = issue.get('fields', {})

        summary = fields.get('summary', 'No summary')
        status = fields.get('status', {})
        status_name = status.get('name', 'Unknown') if isinstance(status, dict) else str(status)

        assignee = fields.get('assignee')
        assignee_name = assignee.get('displayName', 'Unassigned') if assignee else 'Unassigned'

        issue_type = fields.get('issuetype', {})
        type_name = issue_type.get('name', 'Unknown') if isinstance(issue_type, dict) else str(issue_type)

        labels = fields.get('labels', [])
        labels_str = ', '.join(labels) if labels else 'None'

        target_start = fields.get(CUSTOM_FIELDS['target_start'], '-') or '-'

        # Format with colors
        status_colored = colorize(status_name, get_status_color(status_name))
        key_colored = colorize(key, Colors.CYAN + Colors.BOLD)

        lines.append(f"{key_colored} [{status_colored}] ({type_name})")
        lines.append(f"  {summary}")
        lines.append(f"  Assignee: {assignee_name} | Labels: {labels_str} | Target Start: {target_start}")
        lines.append(f"  URL: {JIRA_URL}/browse/{key}")
        lines.append("")

    return '\n'.join(lines)


def format_issue_detail(issue: Dict[str, Any]) -> str:
    """
    Format a single issue with full details.

    Args:
        issue: Issue dictionary from Jira API

    Returns:
        str: Formatted issue details
    """
    key = issue.get('key', 'Unknown')
    fields = issue.get('fields', {})

    summary = fields.get('summary', 'No summary')

    status = fields.get('status', {})
    status_name = status.get('name', 'Unknown') if isinstance(status, dict) else str(status)

    issue_type = fields.get('issuetype', {})
    type_name = issue_type.get('name', 'Unknown') if isinstance(issue_type, dict) else str(issue_type)

    priority = fields.get('priority', {})
    priority_name = priority.get('name', 'None') if priority else 'None'

    assignee = fields.get('assignee')
    assignee_name = assignee.get('displayName', 'Unassigned') if assignee else 'Unassigned'

    reporter = fields.get('reporter')
    reporter_name = reporter.get('displayName', 'Unknown') if reporter else 'Unknown'

    created = fields.get('created', 'Unknown')[:10] if fields.get('created') else 'Unknown'
    updated = fields.get('updated', 'Unknown')[:10] if fields.get('updated') else 'Unknown'

    labels = fields.get('labels', [])
    labels_str = ', '.join(labels) if labels else 'None'

    target_start = fields.get(CUSTOM_FIELDS['target_start'], '-') or '-'
    target_end = fields.get(CUSTOM_FIELDS['target_end'], '-') or '-'

    # Epic link
    epic_link = fields.get(CUSTOM_FIELDS['epic_link'], '')
    if epic_link and isinstance(epic_link, str) and 'title=' in epic_link:
        import re
        match = re.search(r"title='([^']+)'", epic_link)
        epic_name = match.group(1) if match else epic_link
    else:
        epic_name = epic_link if epic_link else '-'

    # Fix versions
    fix_versions = fields.get('fixVersions', [])
    fix_versions_str = ', '.join([v.get('name', '') for v in fix_versions]) if fix_versions else 'None'

    # Description (truncate if long)
    description = fields.get('description', '') or ''
    if len(description) > 500:
        description = description[:500] + '...'

    # Build output
    lines = []
    header = colorize(f"=== {key} ===", Colors.BOLD + Colors.CYAN)
    lines.append(header)
    lines.append(f"Summary:      {summary}")
    lines.append(f"Type:         {type_name}")
    lines.append(f"Status:       {colorize(status_name, get_status_color(status_name))}")
    lines.append(f"Priority:     {priority_name}")
    lines.append("")
    lines.append(f"Assignee:     {assignee_name}")
    lines.append(f"Reporter:     {reporter_name}")
    lines.append("")
    lines.append(f"Created:      {created}")
    lines.append(f"Updated:      {updated}")
    lines.append(f"Target Start: {target_start}")
    lines.append(f"Target End:   {target_end}")
    lines.append("")
    lines.append(f"Labels:       {labels_str}")
    lines.append(f"Fix Versions: {fix_versions_str}")
    lines.append(f"Epic:         {epic_name}")
    lines.append("")
    lines.append(f"URL: {JIRA_URL}/browse/{key}")

    if description:
        lines.append("")
        lines.append("Description:")
        lines.append("-" * 40)
        lines.append(description)

    return '\n'.join(lines)


def format_transitions(transitions: List[Dict[str, Any]]) -> str:
    """Format available transitions for display."""
    lines = ["Available transitions:"]
    for t in transitions:
        name = t.get('name', 'Unknown')
        to_status = t.get('to', {})
        # Handle both dict and string formats for 'to'
        if isinstance(to_status, dict):
            to_status_name = to_status.get('name', 'unknown')
        else:
            to_status_name = str(to_status) if to_status else 'unknown'
        lines.append(f"  - {name} (to: {to_status_name})")
    return '\n'.join(lines)
