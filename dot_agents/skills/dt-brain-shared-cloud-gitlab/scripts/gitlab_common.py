#!/usr/bin/env python3
"""
GitLab Common Module - Shared utilities for GitLab skill scripts
"""

import os
import sys
import json

try:
    import gitlab
except ImportError:
    print("Error: python-gitlab library not installed", file=sys.stderr)
    print("Install with: pip install python-gitlab", file=sys.stderr)
    sys.exit(1)

# Allowed group prefixes (including subgroups)
ALLOWED_GROUPS = ["cit/t-caas", "tdi-caas", "cit-iaas/cid"]

GITLAB_URL = "https://gitlab.devops.telekom.de"


def get_gitlab_client():
    """Initialize GitLab API client"""
    token = os.environ.get("GITLAB_API_TOKEN")
    if not token:
        print("Error: GITLAB_API_TOKEN environment variable is not set", file=sys.stderr)
        print("Set it with: export GITLAB_API_TOKEN='your-token'", file=sys.stderr)
        sys.exit(1)

    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        gl = gitlab.Gitlab(GITLAB_URL, private_token=token, ssl_verify=False)
        gl.auth()
        return gl
    except Exception as e:
        print(f"Error: Failed to initialize GitLab client: {e}", file=sys.stderr)
        print("Make sure you are connected to Telekom VPN", file=sys.stderr)
        sys.exit(1)


def validate_group(group_path: str) -> bool:
    """Check if group path is in the allowed list (including subgroups)"""
    normalized = group_path.strip("/").lower()
    for allowed in ALLOWED_GROUPS:
        if normalized == allowed.lower() or normalized.startswith(allowed.lower() + "/"):
            return True
    return False


def validate_project(project_path: str) -> bool:
    """Check if project path belongs to an allowed group"""
    normalized = project_path.strip("/").lower()
    for allowed in ALLOWED_GROUPS:
        if normalized.startswith(allowed.lower() + "/"):
            return True
    return False


# --- Output helpers ---

def print_error(message):
    """Print an error message to stderr."""
    print(f"Error: {message}", file=sys.stderr)


def print_json(data):
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=2, default=str))


def print_table(headers, rows, max_widths=None):
    """
    Print data as a formatted table.

    Args:
        headers: List of column headers
        rows: List of row data (each row is a list)
        max_widths: Optional dict of column index -> max width for truncation
    """
    if not rows:
        print("No results found.")
        return

    max_widths = max_widths or {}

    col_widths = []
    for i, header in enumerate(headers):
        max_width = len(str(header))
        for row in rows:
            if i < len(row):
                cell = str(row[i]) if row[i] is not None else ""
                max_width = max(max_width, len(cell))
            if i in max_widths:
                max_width = min(max_width, max_widths[i])
        col_widths.append(max_width)

    fmt = "  ".join(f"{{:<{w}}}" for w in col_widths)

    print(fmt.format(*[str(h) for h in headers]))
    print(fmt.format(*["-" * w for w in col_widths]))

    for row in rows:
        formatted_cells = []
        for i, cell in enumerate(row):
            cell_str = str(cell) if cell is not None else ""
            if i in max_widths and len(cell_str) > max_widths[i]:
                cell_str = cell_str[:max_widths[i] - 3] + "..."
            formatted_cells.append(cell_str)
        while len(formatted_cells) < len(headers):
            formatted_cells.append("")
        print(fmt.format(*formatted_cells))


def truncate(text, max_length):
    """Truncate text to max_length, adding ellipsis if needed."""
    if text is None:
        return ""
    text = str(text)
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def format_date(date_str):
    """Format a date string for display (YYYY-MM-DD)."""
    if not date_str:
        return ""
    return date_str[:10]


def format_labels(labels, max_length=40):
    """Format a list of labels for display."""
    if not labels:
        return ""
    label_str = ", ".join(labels)
    return truncate(label_str, max_length)


# --- User search helpers ---

def search_group_members(group, search_term: str) -> list:
    """
    Search for users within a GitLab group by name or username.

    Args:
        group: GitLab group object
        search_term: Partial name or username to search for (case-insensitive)

    Returns:
        list: List of matching member dicts with 'username', 'name', 'id'
    """
    try:
        members = group.members_all.list(query=search_term, per_page=50)
        return [
            {'id': m.id, 'username': m.username, 'name': m.name}
            for m in members
        ]
    except Exception as e:
        print_error(f"Failed to search group members: {e}")
        return []


def find_user_by_name(group, name: str, interactive: bool = True) -> str | None:
    """
    Find a GitLab username by searching for a partial name.

    Handles ambiguous matches by showing options to user (if interactive)
    or returning None. If no group members match, returns the input as-is
    if it looks like a username (contains '.' or '-').

    Args:
        group: GitLab group object
        name: Partial name or username to search for
        interactive: If True, prompt user when multiple matches found

    Returns:
        str: Username if found, None otherwise
    """
    members = search_group_members(group, name)

    if not members:
        if '.' in name or '-' in name or '@' in name:
            username = name.lstrip('@')
            print(f"No group members found matching '{name}', using as direct username: @{username}", file=sys.stderr)
            return username
        print_error(f"No users found matching '{name}' in the group")
        return None

    if len(members) == 1:
        return members[0]['username']

    if interactive:
        print(f"\nMultiple users found matching '{name}':", file=sys.stderr)
        for i, member in enumerate(members, 1):
            print(f"  {i}. {member['name']} (@{member['username']})", file=sys.stderr)
        print(f"  {len(members) + 1}. Cancel", file=sys.stderr)

        try:
            choice = input("\nSelect a user (number): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(members):
                return members[idx]['username']
            else:
                print_error("Selection cancelled")
                return None
        except (ValueError, KeyboardInterrupt):
            print_error("\nInvalid selection or cancelled")
            return None
    else:
        print_error(f"Multiple users found matching '{name}'. Please be more specific:")
        for member in members:
            print(f"  - {member['name']} (@{member['username']})", file=sys.stderr)
        return None
