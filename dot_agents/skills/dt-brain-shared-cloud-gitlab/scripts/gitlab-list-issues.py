#!/usr/bin/env python3
"""
GitLab List Issues Script
Usage: gitlab-list-issues.py <group-path> [options]
"""

import sys
import argparse
from typing import List, Dict, Any

from gitlab_common import (
    ALLOWED_GROUPS,
    get_gitlab_client,
    validate_group,
    print_table,
    print_json,
    print_error,
    format_date,
    format_labels,
    find_user_by_name,
)


def list_issues(gl, group_path: str, state: str = "opened",
                labels: str = None, assignee_username: str = None,
                author: str = None, search: str = None,
                updated_after: str = None, created_after: str = None,
                sort_by: str = None, limit: int = 50) -> List[Dict[str, Any]]:
    """List issues from a group (including subgroups)"""
    try:
        group = gl.groups.get(group_path)
    except Exception as e:
        print_error(f"Failed to get group '{group_path}': {e}")
        sys.exit(1)

    params = {
        "include_subgroups": True,
        "per_page": min(limit, 100),
    }

    if state != "all":
        params["state"] = state
    if labels:
        params["labels"] = labels
    if assignee_username:
        params["assignee_username"] = assignee_username
    if author:
        params["author_username"] = author
    if search:
        params["search"] = search
    if updated_after:
        params["updated_after"] = updated_after
    if created_after:
        params["created_after"] = created_after

    try:
        if limit > 100:
            issues = list(group.issues.list(**params, get_all=True))
        else:
            issues = list(group.issues.list(**params, get_all=False))

        if sort_by:
            def sort_key(issue):
                if sort_by == "due_date":
                    return getattr(issue, "due_date", None) or "9999-99-99"
                elif sort_by == "created_at":
                    return getattr(issue, "created_at", None) or ""
                elif sort_by == "updated_at":
                    return getattr(issue, "updated_at", None) or ""
                elif sort_by == "title":
                    return issue.title.lower()
                return ""
            issues = sorted(issues, key=sort_key)

        result = []
        for issue in issues[:limit]:
            # Extract project path from references
            ref = getattr(issue, "references", {})
            if isinstance(ref, dict):
                full_ref = ref.get("full", "")
            else:
                full_ref = str(ref)
            project = full_ref.rsplit("#", 1)[0] if "#" in full_ref else ""

            # Extract assignees
            assignees = getattr(issue, "assignees", []) or []
            assignee_names = [a["username"] for a in assignees if isinstance(a, dict)] if assignees else []

            result.append({
                "iid": issue.iid,
                "project": project,
                "title": issue.title,
                "state": issue.state,
                "assignees": assignee_names,
                "labels": getattr(issue, "labels", []),
                "due_date": getattr(issue, "due_date", None),
                "created_at": getattr(issue, "created_at", None),
                "updated_at": getattr(issue, "updated_at", None),
                "web_url": getattr(issue, "web_url", None),
            })

        return result

    except Exception as e:
        print_error(f"Failed to list issues: {e}")
        sys.exit(1)


def format_table_output(issues: List[Dict[str, Any]], group_path: str):
    """Format issues as table"""
    print(f"\nFound {len(issues)} issue(s) in {group_path}:\n")

    headers = ["IID", "Project", "Title", "State", "Assignee", "Due"]
    rows = []
    for i in issues:
        rows.append([
            i["iid"],
            i["project"],
            i["title"],
            i["state"],
            ", ".join(i["assignees"][:2]) if i["assignees"] else "-",
            format_date(i["due_date"]),
        ])
    print_table(headers, rows, max_widths={1: 40, 2: 55, 4: 22})


def main():
    parser = argparse.ArgumentParser(
        description="List GitLab issues from a group",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s cit-iaas/cid
  %(prog)s cit-iaas/cid --labels "A - CaaS_squad" --state all
  %(prog)s cit-iaas/cid --assignee "Angel" --sort-by due_date
  %(prog)s cit/t-caas --search "migration" --format json
        """
    )

    parser.add_argument("group", help="Group path (e.g., cit-iaas/cid)")
    parser.add_argument("--state", choices=["opened", "closed", "all"], default="opened",
                        help="Filter by state (default: opened)")
    parser.add_argument("--labels", help="Filter by comma-separated labels")
    parser.add_argument("--assignee", help="Filter by assignee (supports partial name search)")
    parser.add_argument("--author", help="Filter by author username")
    parser.add_argument("--search", help="Search in title and description")
    parser.add_argument("--updated-after", help="Only issues updated after this date (ISO format)")
    parser.add_argument("--created-after", help="Only issues created after this date (ISO format)")
    parser.add_argument("--sort-by", choices=["due_date", "created_at", "updated_at", "title"],
                        help="Sort results by field")
    parser.add_argument("--format", choices=["table", "json"], default="table",
                        help="Output format (default: table)")
    parser.add_argument("--limit", type=int, default=50,
                        help="Maximum results (default: 50)")

    args = parser.parse_args()

    if not validate_group(args.group):
        print_error(f"Group '{args.group}' is not allowed")
        print(f"Allowed groups: {', '.join(ALLOWED_GROUPS)} (and their subgroups)", file=sys.stderr)
        sys.exit(1)

    gl = get_gitlab_client()

    # Resolve assignee if provided (fuzzy search)
    assignee_username = None
    if args.assignee:
        try:
            group = gl.groups.get(args.group)
        except Exception as e:
            print_error(f"Failed to get group '{args.group}': {e}")
            sys.exit(1)
        assignee_username = find_user_by_name(group, args.assignee, interactive=True)
        if not assignee_username:
            sys.exit(1)
        print(f"Filtering by assignee: @{assignee_username}\n", file=sys.stderr)

    issues = list_issues(
        gl, args.group,
        state=args.state, labels=args.labels,
        assignee_username=assignee_username,
        author=args.author, search=args.search,
        updated_after=args.updated_after,
        created_after=args.created_after,
        sort_by=args.sort_by, limit=args.limit,
    )

    if args.format == "json":
        print_json(issues)
    else:
        format_table_output(issues, args.group)


if __name__ == "__main__":
    main()
