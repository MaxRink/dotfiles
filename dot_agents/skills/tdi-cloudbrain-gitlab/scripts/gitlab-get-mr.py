#!/usr/bin/env python3
"""
GitLab Get Merge Request Script
Usage: gitlab-get-mr.py <project-path> <mr-iid> [options]
"""

import sys
import json
import argparse
from typing import Dict, Any

from gitlab_common import (
    ALLOWED_GROUPS,
    get_gitlab_client,
    validate_project,
)


def get_merge_request(gl, project_path: str, mr_iid: int) -> Dict[str, Any]:
    """Get detailed merge request information"""
    try:
        project = gl.projects.get(project_path)
    except Exception as e:
        print(f"Error: Failed to get project '{project_path}': {e}", file=sys.stderr)
        sys.exit(1)

    try:
        mr = project.mergerequests.get(mr_iid)
    except Exception as e:
        print(f"Error: Failed to get merge request !{mr_iid}: {e}", file=sys.stderr)
        sys.exit(1)

    # Build detailed MR data
    mr_data = {
        "iid": mr.iid,
        "title": mr.title,
        "description": mr.description or "",
        "state": mr.state,
        "author": mr.author.get("username", "") if mr.author else "",
        "author_name": mr.author.get("name", "") if mr.author else "",
        "assignees": [a.get("username", "") for a in (mr.assignees or [])],
        "reviewers": [r.get("username", "") for r in (mr.reviewers or [])],
        "source_branch": mr.source_branch,
        "target_branch": mr.target_branch,
        "labels": mr.labels or [],
        "milestone": mr.milestone.get("title", "") if mr.milestone else "",
        "created_at": mr.created_at or "",
        "updated_at": mr.updated_at or "",
        "merged_at": mr.merged_at or "",
        "closed_at": mr.closed_at or "",
        "merge_status": mr.merge_status or "",
        "draft": mr.draft if hasattr(mr, "draft") else False,
        "user_notes_count": mr.user_notes_count if hasattr(mr, "user_notes_count") else 0,
        "upvotes": mr.upvotes if hasattr(mr, "upvotes") else 0,
        "downvotes": mr.downvotes if hasattr(mr, "downvotes") else 0,
        "url": mr.web_url or "",
        "project": project_path,
    }

    # Pipeline status
    if hasattr(mr, "pipeline") and mr.pipeline:
        mr_data["pipeline"] = {
            "status": mr.pipeline.get("status", ""),
            "url": mr.pipeline.get("web_url", ""),
        }
    else:
        mr_data["pipeline"] = None

    # Approvals (may not be available on all tiers)
    try:
        approvals = mr.approvals.get()
        mr_data["approvals"] = {
            "approved": approvals.approved if hasattr(approvals, "approved") else False,
            "approved_by": [a.get("user", {}).get("username", "") for a in (approvals.approved_by or [])] if hasattr(approvals, "approved_by") else [],
        }
    except Exception:
        mr_data["approvals"] = None

    return mr_data


def format_detailed(mr_data: Dict[str, Any]):
    """Format merge request as detailed view"""
    print("=" * 80)
    print(f"Merge Request: {mr_data['project']}!{mr_data['iid']}")
    print("=" * 80)
    print()

    # Title and state
    draft_prefix = "[DRAFT] " if mr_data.get("draft") else ""
    print(f"  Title:          {draft_prefix}{mr_data['title']}")
    print(f"  State:          {mr_data['state']}")
    print(f"  URL:            {mr_data['url']}")
    print()

    # Branches
    print("BRANCHES")
    print("-" * 80)
    print(f"  Source:          {mr_data['source_branch']}")
    print(f"  Target:          {mr_data['target_branch']}")
    print(f"  Merge Status:    {mr_data['merge_status']}")
    print()

    # People
    print("PEOPLE")
    print("-" * 80)
    print(f"  Author:          {mr_data['author_name']} (@{mr_data['author']})")
    print(f"  Assignees:       {', '.join(mr_data['assignees']) if mr_data['assignees'] else '-'}")
    print(f"  Reviewers:       {', '.join(mr_data['reviewers']) if mr_data['reviewers'] else '-'}")
    print()

    # Approvals
    if mr_data.get("approvals"):
        print("APPROVALS")
        print("-" * 80)
        approved_str = "Yes" if mr_data["approvals"]["approved"] else "No"
        print(f"  Approved:        {approved_str}")
        if mr_data["approvals"]["approved_by"]:
            print(f"  Approved By:     {', '.join(mr_data['approvals']['approved_by'])}")
        print()

    # Pipeline
    if mr_data.get("pipeline"):
        print("PIPELINE")
        print("-" * 80)
        print(f"  Status:          {mr_data['pipeline']['status']}")
        print(f"  URL:             {mr_data['pipeline']['url']}")
        print()

    # Labels and milestone
    if mr_data["labels"] or mr_data["milestone"]:
        print("METADATA")
        print("-" * 80)
        if mr_data["labels"]:
            print(f"  Labels:          {', '.join(mr_data['labels'])}")
        if mr_data["milestone"]:
            print(f"  Milestone:       {mr_data['milestone']}")
        print()

    # Dates
    print("DATES")
    print("-" * 80)
    print(f"  Created:         {mr_data['created_at']}")
    print(f"  Updated:         {mr_data['updated_at']}")
    if mr_data["merged_at"]:
        print(f"  Merged:          {mr_data['merged_at']}")
    if mr_data["closed_at"]:
        print(f"  Closed:          {mr_data['closed_at']}")
    print()

    # Activity
    print("ACTIVITY")
    print("-" * 80)
    print(f"  Comments:        {mr_data['user_notes_count']}")
    print(f"  Upvotes:         {mr_data['upvotes']}")
    print(f"  Downvotes:       {mr_data['downvotes']}")
    print()

    # Description
    if mr_data["description"]:
        print("DESCRIPTION")
        print("-" * 80)
        print(f"  {mr_data['description']}")
        print()


def format_json(mr_data: Dict[str, Any]):
    """Format merge request as JSON"""
    print(json.dumps(mr_data, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Get GitLab merge request details",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get MR details
  %(prog)s cit/t-caas/my-repo 42

  # Get JSON output
  %(prog)s cit/t-caas/my-repo 42 --format json

  # Get MR from subgroup project
  %(prog)s cit/t-caas/sub/project 15
        """
    )

    parser.add_argument("project", help="Project path (e.g., cit/t-caas/my-repo)")
    parser.add_argument("mr_iid", type=int, help="Merge request IID (number)")
    parser.add_argument("--format", choices=["detailed", "json"], default="detailed",
                        help="Output format (default: detailed)")

    args = parser.parse_args()

    # Validate project
    if not validate_project(args.project):
        print(f"Error: Project '{args.project}' is not in an allowed group", file=sys.stderr)
        print(f"Allowed group prefixes: {', '.join(ALLOWED_GROUPS)}", file=sys.stderr)
        sys.exit(1)

    # Initialize GitLab client
    gl = get_gitlab_client()

    # Get merge request
    mr_data = get_merge_request(gl, args.project, args.mr_iid)

    # Format output
    if args.format == "json":
        format_json(mr_data)
    else:
        format_detailed(mr_data)


if __name__ == "__main__":
    main()
