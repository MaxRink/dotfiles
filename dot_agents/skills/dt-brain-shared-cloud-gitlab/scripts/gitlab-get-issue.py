#!/usr/bin/env python3
"""
GitLab Get Issue Script
Usage: gitlab-get-issue.py <project-path> <issue-iid> [options]
"""

import sys
import argparse
from typing import Dict, Any

from gitlab_common import (
    ALLOWED_GROUPS,
    get_gitlab_client,
    validate_project,
    print_json,
    print_error,
    format_date,
)


def get_issue(gl, project_path: str, issue_iid: int) -> Dict[str, Any]:
    """Get detailed issue information"""
    try:
        project = gl.projects.get(project_path)
    except Exception as e:
        print_error(f"Failed to get project '{project_path}': {e}")
        sys.exit(1)

    try:
        issue = project.issues.get(issue_iid)
    except Exception as e:
        print_error(f"Failed to get issue #{issue_iid}: {e}")
        sys.exit(1)

    return {
        "iid": issue.iid,
        "title": issue.title,
        "description": issue.description or "",
        "state": issue.state,
        "author": issue.author.get("username", "") if issue.author else "",
        "author_name": issue.author.get("name", "") if issue.author else "",
        "assignees": [
            {"username": a.get("username", ""), "name": a.get("name", "")}
            for a in (issue.assignees or [])
        ],
        "labels": issue.labels or [],
        "milestone": issue.milestone.get("title", "") if issue.milestone else "",
        "due_date": issue.due_date or "",
        "created_at": issue.created_at or "",
        "updated_at": issue.updated_at or "",
        "closed_at": issue.closed_at or "",
        "user_notes_count": getattr(issue, "user_notes_count", 0),
        "upvotes": getattr(issue, "upvotes", 0),
        "downvotes": getattr(issue, "downvotes", 0),
        "url": issue.web_url or "",
        "project": project_path,
    }


def format_detailed(data: Dict[str, Any]):
    """Format issue as detailed view"""
    print("=" * 80)
    print(f"Issue: {data['project']}#{data['iid']}")
    print("=" * 80)
    print()

    print(f"  Title:          {data['title']}")
    print(f"  State:          {data['state']}")
    print(f"  URL:            {data['url']}")
    print()

    print("PEOPLE")
    print("-" * 80)
    print(f"  Author:          {data['author_name']} (@{data['author']})")
    assignee_str = ", ".join(
        f"{a['name']} (@{a['username']})" for a in data["assignees"]
    ) if data["assignees"] else "-"
    print(f"  Assignees:       {assignee_str}")
    print()

    if data["labels"] or data["milestone"]:
        print("METADATA")
        print("-" * 80)
        if data["labels"]:
            print(f"  Labels:          {', '.join(data['labels'])}")
        if data["milestone"]:
            print(f"  Milestone:       {data['milestone']}")
        if data["due_date"]:
            print(f"  Due Date:        {data['due_date']}")
        print()

    print("DATES")
    print("-" * 80)
    print(f"  Created:         {format_date(data['created_at'])}")
    print(f"  Updated:         {format_date(data['updated_at'])}")
    if data["closed_at"]:
        print(f"  Closed:          {format_date(data['closed_at'])}")
    print()

    print("ACTIVITY")
    print("-" * 80)
    print(f"  Comments:        {data['user_notes_count']}")
    print(f"  Upvotes:         {data['upvotes']}")
    print(f"  Downvotes:       {data['downvotes']}")
    print()

    if data["description"]:
        print("DESCRIPTION")
        print("-" * 80)
        print(f"  {data['description']}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Get GitLab issue details",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s cit-iaas/cid/caas-devops 124
  %(prog)s cit/t-caas/my-repo 42 --format json
        """
    )

    parser.add_argument("project", help="Project path (e.g., cit-iaas/cid/caas-devops)")
    parser.add_argument("issue_iid", type=int, help="Issue IID (number)")
    parser.add_argument("--format", choices=["detailed", "json"], default="detailed",
                        help="Output format (default: detailed)")

    args = parser.parse_args()

    if not validate_project(args.project):
        print_error(f"Project '{args.project}' is not in an allowed group")
        print(f"Allowed group prefixes: {', '.join(ALLOWED_GROUPS)}", file=sys.stderr)
        sys.exit(1)

    gl = get_gitlab_client()
    data = get_issue(gl, args.project, args.issue_iid)

    if args.format == "json":
        print_json(data)
    else:
        format_detailed(data)


if __name__ == "__main__":
    main()
