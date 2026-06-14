#!/usr/bin/env python3
"""
List all issues linked to an epic.

Usage:
    cid-epic-issues.py <epic-iid> [options]

Arguments:
    epic-iid        Epic IID number

Options:
    --format FORMAT Output format: table (default), json
    --limit N       Maximum results (default: 100)
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for utils import
sys.path.insert(0, str(Path(__file__).parent))

from utils import get_gitlab_client, get_cid_group, print_table, print_json, print_error
from utils.output import format_date, format_labels, truncate
from utils.validators import validate_positive_int


def list_epic_issues(epic_iid, limit=100):
    """
    List all issues linked to an epic.

    Args:
        epic_iid: The epic IID
        limit: Maximum results

    Returns:
        list: List of issue objects
    """
    gl = get_gitlab_client()
    group = get_cid_group(gl)

    try:
        epic = group.epics.get(epic_iid)
        issues = epic.issues.list(per_page=min(limit, 100))

        # Handle pagination if limit > 100
        if limit > 100:
            all_issues = list(issues)
            page = 2
            while len(all_issues) < limit:
                next_page = epic.issues.list(per_page=100, page=page)
                if not next_page:
                    break
                all_issues.extend(next_page)
                page += 1
            return all_issues[:limit]

        return list(issues)[:limit]

    except Exception as e:
        print_error(f"Failed to list issues for epic {epic_iid}: {e}")
        sys.exit(1)


def get_project_path(issue):
    """Extract project path from issue web_url."""
    web_url = getattr(issue, "web_url", "")
    if "/-/issues/" in web_url:
        # URL format: https://gitlab.../group/project/-/issues/123
        path = web_url.split("/-/issues/")[0]
        # Remove base URL
        path = path.replace("https://gitlab.devops.telekom.de/", "")
        return path
    return "unknown"


def get_assignee(issue):
    """Get assignee username from issue."""
    assignees = getattr(issue, "assignees", [])
    if assignees and len(assignees) > 0:
        return assignees[0].get("username", "")
    assignee = getattr(issue, "assignee", None)
    if assignee:
        return assignee.get("username", "")
    return ""


def format_issue_for_table(issue):
    """Format an issue for table display."""
    return [
        issue.iid,
        truncate(get_project_path(issue), 30),
        truncate(issue.title, 45),
        issue.state,
        get_assignee(issue),
        format_labels(getattr(issue, "labels", []), max_length=25),
        format_date(getattr(issue, "due_date", None)),
    ]


def format_issue_for_json(issue):
    """Format an issue for JSON output."""
    return {
        "iid": issue.iid,
        "id": getattr(issue, "id", None),
        "project_path": get_project_path(issue),
        "title": issue.title,
        "description": getattr(issue, "description", None),
        "state": issue.state,
        "assignees": [
            {"username": a.get("username"), "name": a.get("name")}
            for a in getattr(issue, "assignees", [])
        ],
        "labels": getattr(issue, "labels", []),
        "milestone": {
            "id": issue.milestone.get("id"),
            "title": issue.milestone.get("title"),
        } if getattr(issue, "milestone", None) else None,
        "due_date": getattr(issue, "due_date", None),
        "created_at": getattr(issue, "created_at", None),
        "updated_at": getattr(issue, "updated_at", None),
        "closed_at": getattr(issue, "closed_at", None),
        "web_url": getattr(issue, "web_url", None),
    }


def main():
    parser = argparse.ArgumentParser(description="List issues linked to an epic")
    parser.add_argument("epic_iid", type=int, help="Epic IID number")
    parser.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    parser.add_argument("--limit", type=int, default=100, help="Maximum results")

    args = parser.parse_args()

    # Validate inputs
    epic_iid = validate_positive_int(args.epic_iid, "epic_iid")
    limit = validate_positive_int(args.limit, "limit")

    # Fetch issues
    issues = list_epic_issues(epic_iid, limit)

    # Output results
    if args.format == "json":
        print_json([format_issue_for_json(i) for i in issues])
    else:
        headers = ["IID", "Project", "Title", "State", "Assignee", "Labels", "Due"]
        rows = [format_issue_for_table(i) for i in issues]
        max_widths = {1: 30, 2: 45, 5: 25}
        print(f"\nFound {len(issues)} issue(s) linked to epic #{epic_iid}:\n")
        print_table(headers, rows, max_widths)


if __name__ == "__main__":
    main()
