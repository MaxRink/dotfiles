#!/usr/bin/env python3
"""
GitLab Get Epic Details Script
Usage: gitlab-get-epic.py <group-path> <epic-iid> [options]
"""

import sys
import argparse
from typing import Dict, Any

from gitlab_common import (
    ALLOWED_GROUPS,
    get_gitlab_client,
    validate_group,
    print_json,
    print_error,
    format_date,
)


def get_epic(gl, group_path: str, epic_iid: int):
    """Get epic object from GitLab"""
    try:
        group = gl.groups.get(group_path)
    except Exception as e:
        print_error(f"Failed to get group '{group_path}': {e}")
        sys.exit(1)

    try:
        return group, group.epics.get(epic_iid)
    except Exception as e:
        print_error(f"Failed to get epic #{epic_iid}: {e}")
        sys.exit(1)


def get_issues_count(epic) -> int | str:
    """Get the count of issues linked to an epic."""
    try:
        all_issues = epic.issues.list(per_page=100, get_all=True)
        return len(list(all_issues))
    except Exception:
        return "N/A"


def get_child_epics(group, parent_iid: int) -> list:
    """Get child epics for a parent epic."""
    try:
        all_epics = group.epics.list(state="all", per_page=100, get_all=True)
        return [e for e in all_epics if getattr(e, 'parent_iid', None) == parent_iid]
    except Exception:
        return []


def build_epic_data(group, epic) -> Dict[str, Any]:
    """Build epic data dict"""
    parent_iid = getattr(epic, 'parent_iid', None)
    child_epics = get_child_epics(group, epic.iid)

    if child_epics:
        hierarchy_type = "umbrella"
    elif parent_iid:
        hierarchy_type = "child"
    else:
        hierarchy_type = "standalone"

    return {
        "iid": epic.iid,
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
        "due_date": getattr(epic, "due_date", None),
        "created_at": getattr(epic, "created_at", None),
        "updated_at": getattr(epic, "updated_at", None),
        "closed_at": getattr(epic, "closed_at", None),
        "issues_count": get_issues_count(epic),
        "upvotes": getattr(epic, "upvotes", 0),
        "downvotes": getattr(epic, "downvotes", 0),
        "web_url": getattr(epic, "web_url", None),
        "parent_iid": parent_iid,
        "hierarchy_type": hierarchy_type,
        "child_count": len(child_epics),
        "child_iids": [c.iid for c in child_epics],
    }


def format_detailed(data: Dict[str, Any], group, epic):
    """Format epic as detailed view"""
    print("=" * 70)
    print(f"Epic #{data['iid']}: {data['title']}")
    print("=" * 70)
    print()

    print(f"State:        {data['state']}")
    print(f"Confidential: {data['confidential']}")
    print()

    # Hierarchy
    if data["hierarchy_type"] != "standalone":
        print("Hierarchy:")
        if data["parent_iid"]:
            try:
                parent = group.epics.get(data["parent_iid"])
                print(f"  Parent:     #{data['parent_iid']} - {parent.title[:50]}")
            except Exception:
                print(f"  Parent:     #{data['parent_iid']}")
        if data["child_count"] > 0:
            print(f"  Type:       UMBRELLA EPIC ({data['child_count']} children)")
            print("  Children:")
            for child_iid in data["child_iids"]:
                try:
                    child = group.epics.get(child_iid)
                    status = "✓" if child.state == "closed" else "○"
                    print(f"    {status} #{child_iid}: {child.title[:50]}")
                except Exception:
                    print(f"    ? #{child_iid}")
        elif data["parent_iid"]:
            print("  Type:       Child epic")
        print()

    # Dates
    print("Dates:")
    print(f"  Created:    {format_date(data['created_at'])}")
    print(f"  Updated:    {format_date(data['updated_at'])}")
    print(f"  Start:      {format_date(data['start_date']) or 'Not set'}")
    print(f"  Due:        {format_date(data['due_date']) or 'Not set'}")
    if data["closed_at"]:
        print(f"  Closed:     {format_date(data['closed_at'])}")
    print()

    # Author
    if data["author"]:
        print(f"Author:       {data['author']['name']} (@{data['author']['username']})")
    print()

    # Labels
    if data["labels"]:
        print("Labels:")
        for label in data["labels"]:
            print(f"  - {label}")
    else:
        print("Labels:       None")
    print()

    print(f"Issues:       {data['issues_count']}")
    print()

    # Description
    if data["description"]:
        print("Description:")
        print("-" * 40)
        for line in data["description"].split("\n"):
            print(f"  {line}")
        print("-" * 40)
    else:
        print("Description:  None")
    print()

    print(f"URL:          {data['web_url']}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Get GitLab epic details",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s cit-iaas/cid 42
  %(prog)s cit-iaas/cid 42 --format json
        """
    )

    parser.add_argument("group", help="Group path (e.g., cit-iaas/cid)")
    parser.add_argument("epic_iid", type=int, help="Epic IID (number)")
    parser.add_argument("--format", choices=["detailed", "json"], default="detailed",
                        help="Output format (default: detailed)")

    args = parser.parse_args()

    if not validate_group(args.group):
        print_error(f"Group '{args.group}' is not allowed")
        print(f"Allowed groups: {', '.join(ALLOWED_GROUPS)} (and their subgroups)", file=sys.stderr)
        sys.exit(1)

    gl = get_gitlab_client()
    group, epic = get_epic(gl, args.group, args.epic_iid)
    data = build_epic_data(group, epic)

    if args.format == "json":
        print_json(data)
    else:
        format_detailed(data, group, epic)


if __name__ == "__main__":
    main()
