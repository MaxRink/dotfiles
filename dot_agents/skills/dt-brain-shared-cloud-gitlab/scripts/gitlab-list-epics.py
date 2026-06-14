#!/usr/bin/env python3
"""
GitLab List Epics Script
Usage: gitlab-list-epics.py <group-path> [options]
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
)


def list_epics(gl, group_path: str, state: str = "opened",
               labels: str = None, author: str = None, search: str = None,
               updated_after: str = None, created_after: str = None,
               sort_by: str = None, limit: int = 50) -> List[Dict[str, Any]]:
    """List epics from a group (including subgroups)"""
    try:
        group = gl.groups.get(group_path)
    except Exception as e:
        print_error(f"Failed to get group '{group_path}': {e}")
        sys.exit(1)

    params = {
        "include_descendant_groups": True,
        "per_page": min(limit, 100),
    }

    if state != "all":
        params["state"] = state
    if labels:
        params["labels"] = labels
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
            epics = list(group.epics.list(**params, get_all=True))
        else:
            epics = list(group.epics.list(**params, get_all=False))

        # Sort if requested
        if sort_by:
            def sort_key(e):
                if sort_by == "due_date":
                    return getattr(e, "due_date", None) or "9999-99-99"
                elif sort_by == "created_at":
                    return getattr(e, "created_at", None) or ""
                elif sort_by == "updated_at":
                    return getattr(e, "updated_at", None) or ""
                elif sort_by == "title":
                    return e.title.lower()
                return ""
            epics = sorted(epics, key=sort_key)

        result = []
        for epic in epics[:limit]:
            result.append({
                "iid": epic.iid,
                "title": epic.title,
                "state": epic.state,
                "start_date": getattr(epic, "start_date", None),
                "due_date": getattr(epic, "due_date", None),
                "labels": getattr(epic, "labels", []),
                "author": epic.author.get("username", "") if hasattr(epic, "author") and epic.author else "",
                "created_at": getattr(epic, "created_at", None),
                "updated_at": getattr(epic, "updated_at", None),
                "web_url": getattr(epic, "web_url", None),
                "parent_iid": getattr(epic, "parent_iid", None),
            })

        return result

    except Exception as e:
        print_error(f"Failed to list epics: {e}")
        sys.exit(1)


def format_table_output(epics: List[Dict[str, Any]], group_path: str):
    """Format epics as table"""
    print(f"\nFound {len(epics)} epic(s) in {group_path}:\n")

    headers = ["IID", "Title", "State", "Start", "Due", "Labels"]
    rows = []
    for e in epics:
        rows.append([
            e["iid"],
            e["title"],
            e["state"],
            format_date(e["start_date"]),
            format_date(e["due_date"]),
            format_labels(e["labels"], max_length=30),
        ])
    print_table(headers, rows, max_widths={1: 55, 5: 30})


def main():
    parser = argparse.ArgumentParser(
        description="List GitLab epics from a group",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s cit-iaas/cid
  %(prog)s cit-iaas/cid --state all --sort-by due_date
  %(prog)s cit-iaas/cid --labels "A - CaaS_squad" --limit 100
  %(prog)s cit/t-caas --search "migration" --format json
        """
    )

    parser.add_argument("group", help="Group path (e.g., cit-iaas/cid)")
    parser.add_argument("--state", choices=["opened", "closed", "all"], default="opened",
                        help="Filter by state (default: opened)")
    parser.add_argument("--labels", help="Filter by comma-separated labels")
    parser.add_argument("--author", help="Filter by author username")
    parser.add_argument("--search", help="Search in title and description")
    parser.add_argument("--updated-after", help="Only epics updated after this date (ISO format)")
    parser.add_argument("--created-after", help="Only epics created after this date (ISO format)")
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
    epics = list_epics(
        gl, args.group,
        state=args.state, labels=args.labels, author=args.author,
        search=args.search, updated_after=args.updated_after,
        created_after=args.created_after, sort_by=args.sort_by,
        limit=args.limit,
    )

    if args.format == "json":
        print_json(epics)
    else:
        format_table_output(epics, args.group)


if __name__ == "__main__":
    main()
