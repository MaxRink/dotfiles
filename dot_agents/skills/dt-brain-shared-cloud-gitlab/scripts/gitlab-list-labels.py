#!/usr/bin/env python3
"""
GitLab List Labels Script
Usage: gitlab-list-labels.py <group-path> [options]
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
    truncate,
)


def list_labels(gl, group_path: str, search: str = None,
                limit: int = 100) -> List[Dict[str, Any]]:
    """List labels in a group"""
    try:
        group = gl.groups.get(group_path)
    except Exception as e:
        print_error(f"Failed to get group '{group_path}': {e}")
        sys.exit(1)

    try:
        params = {
            "include_ancestor_groups": True,
            "include_descendant_groups": True,
            "per_page": min(limit, 100),
        }
        if search:
            params["search"] = search

        if limit > 100:
            labels = list(group.labels.list(**params, get_all=True))
        else:
            labels = list(group.labels.list(**params))

        results = []
        for label in labels[:limit]:
            results.append({
                "name": label.name,
                "color": label.color,
                "description": getattr(label, "description", None),
                "text_color": getattr(label, "text_color", None),
                "open_issues_count": getattr(label, "open_issues_count", None),
                "closed_issues_count": getattr(label, "closed_issues_count", None),
            })

        return results

    except Exception as e:
        print_error(f"Failed to list labels: {e}")
        sys.exit(1)


def format_table_output(labels: List[Dict[str, Any]], group_path: str):
    """Format labels as table"""
    print(f"\nFound {len(labels)} label(s) in {group_path}:\n")

    headers = ["Name", "Color", "Description"]
    rows = []
    for l in labels:
        rows.append([
            l["name"],
            l["color"],
            truncate(l["description"] or "", 50),
        ])
    print_table(headers, rows, max_widths={0: 40, 2: 50})


def main():
    parser = argparse.ArgumentParser(
        description="List GitLab group labels",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s cit-iaas/cid
  %(prog)s cit-iaas/cid --search "status"
  %(prog)s cit/t-caas --format json --limit 200
        """
    )

    parser.add_argument("group", help="Group path (e.g., cit-iaas/cid)")
    parser.add_argument("--search", help="Filter labels by name")
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
    labels = list_labels(gl, args.group, search=args.search, limit=args.limit)

    if args.format == "json":
        print_json(labels)
    else:
        format_table_output(labels, args.group)


if __name__ == "__main__":
    main()
