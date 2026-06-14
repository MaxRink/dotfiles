#!/usr/bin/env python3
"""
GitLab List Epic Issues Script
Usage: gitlab-epic-issues.py <group-path> <epic-iid> [options]
"""

import sys
import argparse
from typing import List, Dict, Any

from gitlab_common import (
    ALLOWED_GROUPS,
    GITLAB_URL,
    get_gitlab_client,
    validate_group,
    print_table,
    print_json,
    print_error,
    format_date,
    format_labels,
    truncate,
)


def list_epic_issues(gl, group_path: str, epic_iid: int,
                     limit: int = 100) -> List[Dict[str, Any]]:
    """List all issues linked to an epic"""
    try:
        group = gl.groups.get(group_path)
    except Exception as e:
        print_error(f"Failed to get group '{group_path}': {e}")
        sys.exit(1)

    try:
        epic = group.epics.get(epic_iid)
    except Exception as e:
        print_error(f"Failed to get epic #{epic_iid}: {e}")
        sys.exit(1)

    try:
        if limit > 100:
            issues = list(epic.issues.list(per_page=100, get_all=True))
        else:
            issues = list(epic.issues.list(per_page=min(limit, 100)))

        results = []
        for issue in issues[:limit]:
            # Extract project path from web_url
            web_url = getattr(issue, "web_url", "")
            project_path = ""
            if "/-/issues/" in web_url:
                project_path = web_url.split("/-/issues/")[0].replace(GITLAB_URL + "/", "")

            assignees = getattr(issue, "assignees", [])
            assignee = assignees[0].get("username", "") if assignees else ""

            results.append({
                "iid": issue.iid,
                "project_path": project_path,
                "title": issue.title,
                "state": issue.state,
                "assignee": assignee,
                "labels": getattr(issue, "labels", []),
                "due_date": getattr(issue, "due_date", None),
                "created_at": getattr(issue, "created_at", None),
                "updated_at": getattr(issue, "updated_at", None),
                "web_url": web_url,
            })

        return results

    except Exception as e:
        print_error(f"Failed to list issues for epic #{epic_iid}: {e}")
        sys.exit(1)


def format_table_output(issues: List[Dict[str, Any]], group_path: str, epic_iid: int):
    """Format issues as table"""
    print(f"\nFound {len(issues)} issue(s) linked to epic #{epic_iid} in {group_path}:\n")

    headers = ["IID", "Project", "Title", "State", "Assignee", "Labels", "Due"]
    rows = []
    for i in issues:
        rows.append([
            i["iid"],
            truncate(i["project_path"], 30),
            truncate(i["title"], 45),
            i["state"],
            i["assignee"] or "-",
            format_labels(i["labels"], max_length=25),
            format_date(i["due_date"]),
        ])
    print_table(headers, rows, max_widths={1: 30, 2: 45, 5: 25})


def main():
    parser = argparse.ArgumentParser(
        description="List issues linked to a GitLab epic",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s cit-iaas/cid 42
  %(prog)s cit-iaas/cid 922 --format json
  %(prog)s cit-iaas/cid 42 --limit 200
        """
    )

    parser.add_argument("group", help="Group path (e.g., cit-iaas/cid)")
    parser.add_argument("epic_iid", type=int, help="Epic IID (number)")
    parser.add_argument("--format", choices=["table", "json"], default="table",
                        help="Output format (default: table)")
    parser.add_argument("--limit", type=int, default=100,
                        help="Maximum results (default: 100)")

    args = parser.parse_args()

    if not validate_group(args.group):
        print_error(f"Group '{args.group}' is not allowed")
        print(f"Allowed groups: {', '.join(ALLOWED_GROUPS)} (and their subgroups)", file=sys.stderr)
        sys.exit(1)

    gl = get_gitlab_client()
    issues = list_epic_issues(gl, args.group, args.epic_iid, limit=args.limit)

    if args.format == "json":
        print_json(issues)
    else:
        format_table_output(issues, args.group, args.epic_iid)


if __name__ == "__main__":
    main()
