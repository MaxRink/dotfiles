#!/usr/bin/env python3
"""
Get detailed information about a specific epic.

Usage:
    cid-get-epic.py <epic-iid> [options]

Arguments:
    epic-iid        Epic IID number

Options:
    --format FORMAT Output format: detailed (default), json
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for utils import
sys.path.insert(0, str(Path(__file__).parent))

from utils import get_gitlab_client, get_cid_group, print_json, print_error
from utils.output import format_date
from utils.validators import validate_positive_int


def get_epic(epic_iid):
    """
    Get detailed information about an epic.

    Args:
        epic_iid: The epic IID

    Returns:
        Epic object
    """
    gl = get_gitlab_client()
    group = get_cid_group(gl)

    try:
        return group.epics.get(epic_iid)
    except Exception as e:
        print_error(f"Failed to get epic {epic_iid}: {e}")
        sys.exit(1)


def get_epic_issues_count(epic):
    """Get the count of issues linked to an epic."""
    try:
        issues = epic.issues.list(per_page=1)
        # Try to get total from response headers
        if hasattr(issues, "total"):
            return issues.total
        # Fallback: count all issues
        all_issues = epic.issues.list(per_page=100, get_all=True)
        return len(list(all_issues))
    except Exception:
        return "N/A"


def get_child_epics(group, parent_iid):
    """Get child epics for a parent epic."""
    try:
        all_epics = group.epics.list(state="all", per_page=100, get_all=True)
        return [e for e in all_epics if getattr(e, 'parent_iid', None) == parent_iid]
    except Exception:
        return []


def get_parent_epic(group, parent_iid):
    """Get parent epic details."""
    try:
        return group.epics.get(parent_iid)
    except Exception:
        return None


def format_epic_detailed(epic, group):
    """Format an epic for detailed display."""
    lines = []
    lines.append("=" * 70)
    lines.append(f"Epic #{epic.iid}: {epic.title}")
    lines.append("=" * 70)
    lines.append("")

    # Basic info
    lines.append(f"State:        {epic.state}")
    lines.append(f"Confidential: {getattr(epic, 'confidential', False)}")
    lines.append("")

    # Hierarchy info
    parent_iid = getattr(epic, 'parent_iid', None)
    child_epics = get_child_epics(group, epic.iid)

    if parent_iid or child_epics:
        lines.append("Hierarchy:")
        if parent_iid:
            parent = get_parent_epic(group, parent_iid)
            if parent:
                lines.append(f"  Parent:     #{parent_iid} - {parent.title[:50]}")
            else:
                lines.append(f"  Parent:     #{parent_iid} (unable to fetch)")
        else:
            lines.append(f"  Parent:     None (this is a top-level epic)")

        if child_epics:
            lines.append(f"  Type:       UMBRELLA EPIC (has {len(child_epics)} children)")
            lines.append(f"  Children:")
            for child in child_epics:
                c_status = "✓" if child.state == "closed" else "○"
                lines.append(f"    {c_status} #{child.iid}: {child.title[:50]}")
        elif not parent_iid:
            lines.append(f"  Type:       Standalone epic (no parent, no children)")
        else:
            lines.append(f"  Type:       Child epic")
        lines.append("")

    # Dates
    lines.append("Dates:")
    lines.append(f"  Created:    {format_date(getattr(epic, 'created_at', None))}")
    lines.append(f"  Updated:    {format_date(getattr(epic, 'updated_at', None))}")
    lines.append(f"  Start:      {format_date(getattr(epic, 'start_date', None)) or 'Not set'}")
    lines.append(f"  Due:        {format_date(getattr(epic, 'due_date', None)) or 'Not set'}")
    if getattr(epic, "closed_at", None):
        lines.append(f"  Closed:     {format_date(epic.closed_at)}")
    lines.append("")

    # Author
    author = getattr(epic, "author", {})
    if author:
        lines.append(f"Author:       {author.get('name', 'Unknown')} (@{author.get('username', 'unknown')})")
    lines.append("")

    # Labels
    labels = getattr(epic, "labels", [])
    if labels:
        lines.append("Labels:")
        for label in labels:
            lines.append(f"  - {label}")
    else:
        lines.append("Labels:       None")
    lines.append("")

    # Progress (issues)
    issues_count = get_epic_issues_count(epic)
    lines.append(f"Issues:       {issues_count}")
    lines.append("")

    # Description
    description = getattr(epic, "description", None)
    if description:
        lines.append("Description:")
        lines.append("-" * 40)
        # Indent description
        for line in description.split("\n"):
            lines.append(f"  {line}")
        lines.append("-" * 40)
    else:
        lines.append("Description:  None")
    lines.append("")

    # Web URL
    lines.append(f"URL:          {getattr(epic, 'web_url', 'N/A')}")
    lines.append("")

    return "\n".join(lines)


def format_epic_json(epic, group):
    """Format an epic for JSON output."""
    issues_count = get_epic_issues_count(epic)
    parent_iid = getattr(epic, 'parent_iid', None)
    child_epics = get_child_epics(group, epic.iid)

    # Determine hierarchy type
    if child_epics:
        hierarchy_type = "umbrella"
    elif parent_iid:
        hierarchy_type = "child"
    else:
        hierarchy_type = "standalone"

    return {
        "iid": epic.iid,
        "id": getattr(epic, "id", None),
        "title": epic.title,
        "description": getattr(epic, "description", None),
        "state": epic.state,
        "confidential": getattr(epic, "confidential", False),
        "author": {
            "username": epic.author.get("username") if epic.author else None,
            "name": epic.author.get("name") if epic.author else None,
        } if hasattr(epic, "author") and epic.author else None,
        "labels": getattr(epic, "labels", []),
        "start_date": getattr(epic, "start_date", None),
        "start_date_is_fixed": getattr(epic, "start_date_is_fixed", None),
        "due_date": getattr(epic, "due_date", None),
        "due_date_is_fixed": getattr(epic, "due_date_is_fixed", None),
        "created_at": getattr(epic, "created_at", None),
        "updated_at": getattr(epic, "updated_at", None),
        "closed_at": getattr(epic, "closed_at", None),
        "issues_count": issues_count,
        "upvotes": getattr(epic, "upvotes", 0),
        "downvotes": getattr(epic, "downvotes", 0),
        "web_url": getattr(epic, "web_url", None),
        "parent_iid": parent_iid,
        "hierarchy_type": hierarchy_type,
        "child_count": len(child_epics),
        "child_iids": [c.iid for c in child_epics],
    }


def main():
    parser = argparse.ArgumentParser(description="Get detailed information about an epic")
    parser.add_argument("epic_iid", type=int, help="Epic IID number")
    parser.add_argument("--format", choices=["detailed", "json"], default="detailed", help="Output format")

    args = parser.parse_args()

    # Validate inputs
    epic_iid = validate_positive_int(args.epic_iid, "epic_iid")

    # Get client and group for hierarchy lookups
    gl = get_gitlab_client()
    group = get_cid_group(gl)

    # Fetch epic
    epic = get_epic(epic_iid)

    # Output results
    if args.format == "json":
        print_json(format_epic_json(epic, group))
    else:
        print(format_epic_detailed(epic, group))


if __name__ == "__main__":
    main()
