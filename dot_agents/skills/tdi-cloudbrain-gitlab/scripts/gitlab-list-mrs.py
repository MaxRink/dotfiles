#!/usr/bin/env python3
"""
GitLab List Merge Requests Script
Usage: gitlab-list-mrs.py --group <group-path> [options]
"""

import sys
import json
import argparse
from typing import List, Dict, Any

from gitlab_common import (
    ALLOWED_GROUPS,
    GITLAB_URL,
    get_gitlab_client,
    validate_group,
)


def list_merge_requests(gl, group_path: str, state: str = "opened",
                        assignee: str = None, author: str = None,
                        labels: str = None, target_branch: str = None,
                        updated_after: str = None, created_after: str = None,
                        limit: int = 50) -> List[Dict[str, Any]]:
    """List merge requests from a group"""
    try:
        group = gl.groups.get(group_path)
    except Exception as e:
        print(f"Error: Failed to get group '{group_path}': {e}", file=sys.stderr)
        sys.exit(1)

    try:
        filters: Dict[str, Any] = {
            "state": state,
            "include_subgroups": True,
            "per_page": min(limit, 100),
        }

        if assignee:
            filters["assignee_username"] = assignee
        if author:
            filters["author_username"] = author
        if labels:
            filters["labels"] = labels
        if target_branch:
            filters["target_branch"] = target_branch
        if updated_after:
            filters["updated_after"] = updated_after
        if created_after:
            filters["created_after"] = created_after

        mrs = group.mergerequests.list(**filters, get_all=False, iterator=True)

        result = []
        count = 0
        for mr in mrs:
            if count >= limit:
                break

            # Extract project path from web_url
            web_url = mr.web_url or ""
            project_path = mr.references.get("full", "").rsplit("!", 1)[0] if hasattr(mr, "references") and mr.references else ""
            if not project_path:
                # Fallback: extract from web_url
                project_path = web_url.replace(GITLAB_URL + "/", "").split("/-/")[0] if web_url else ""

            mr_data = {
                "iid": mr.iid,
                "project": project_path,
                "title": mr.title,
                "author": mr.author.get("username", "") if mr.author else "",
                "assignee": mr.assignee.get("username", "") if mr.assignee else "",
                "state": mr.state,
                "target_branch": mr.target_branch,
                "created_at": mr.created_at[:10] if mr.created_at else "",
                "merged_at": mr.merged_at[:10] if mr.merged_at else "",
                "url": mr.web_url or "",
            }
            result.append(mr_data)
            count += 1

        return result

    except Exception as e:
        print(f"Error: Failed to list merge requests: {e}", file=sys.stderr)
        sys.exit(1)


def format_table(mrs: List[Dict[str, Any]]):
    """Format merge requests as table"""
    if not mrs:
        print("No merge requests found")
        return

    print(f"{'IID':<7} {'Project':<40} {'Title':<45} {'Author':<15} {'Assignee':<15} {'State':<10} {'Target':<15} {'Created':<12}")
    print("-" * 165)

    for mr in mrs:
        title = mr["title"][:42] + "..." if len(mr["title"]) > 42 else mr["title"]
        project = mr["project"][:37] + "..." if len(mr["project"]) > 37 else mr["project"]
        print(f"!{mr['iid']:<6} {project:<40} {title:<45} {mr['author']:<15} {mr['assignee'] or '-':<15} "
              f"{mr['state']:<10} {mr['target_branch']:<15} {mr['created_at']:<12}")

    print(f"\nTotal: {len(mrs)} merge request(s)")


def format_json(mrs: List[Dict[str, Any]]):
    """Format merge requests as JSON"""
    print(json.dumps(mrs, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="List GitLab merge requests from a group",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List open MRs in cit/t-caas group
  %(prog)s --group cit/t-caas

  # List merged MRs
  %(prog)s --group cit/t-caas --state merged

  # Filter by author
  %(prog)s --group cit/t-caas --author john.doe

  # Filter by assignee and target branch
  %(prog)s --group tdi-caas --assignee jane.smith --target-branch main

  # List with labels filter
  %(prog)s --group cit/t-caas --labels "bug,urgent"

  # Limit results and get JSON
  %(prog)s --group cit/t-caas --limit 10 --format json
        """
    )

    parser.add_argument("--group", required=True,
                        help="Group path (e.g., cit/t-caas, tdi-caas)")
    parser.add_argument("--state", choices=["opened", "closed", "merged", "all"],
                        default="opened",
                        help="MR state filter (default: opened)")
    parser.add_argument("--assignee",
                        help="Filter by assignee username")
    parser.add_argument("--author",
                        help="Filter by author username")
    parser.add_argument("--labels",
                        help="Filter by comma-separated labels")
    parser.add_argument("--target-branch",
                        help="Filter by target branch")
    parser.add_argument("--updated-after",
                        help="Only MRs updated after this date (ISO format, e.g. 2026-01-01)")
    parser.add_argument("--created-after",
                        help="Only MRs created after this date (ISO format, e.g. 2026-01-01)")
    parser.add_argument("--format", choices=["table", "json"], default="table",
                        help="Output format (default: table)")
    parser.add_argument("--limit", type=int, default=50,
                        help="Maximum number of results (default: 50)")

    args = parser.parse_args()

    # Validate group
    if not validate_group(args.group):
        print(f"Error: Group '{args.group}' is not allowed", file=sys.stderr)
        print(f"Allowed groups: {', '.join(ALLOWED_GROUPS)} (and their subgroups)", file=sys.stderr)
        sys.exit(1)

    # Initialize GitLab client
    gl = get_gitlab_client()

    # List merge requests
    mrs = list_merge_requests(
        gl, args.group,
        state=args.state,
        assignee=args.assignee,
        author=args.author,
        labels=args.labels,
        target_branch=args.target_branch,
        updated_after=args.updated_after,
        created_after=args.created_after,
        limit=args.limit,
    )

    # Format output
    if args.format == "json":
        format_json(mrs)
    else:
        format_table(mrs)


if __name__ == "__main__":
    main()
