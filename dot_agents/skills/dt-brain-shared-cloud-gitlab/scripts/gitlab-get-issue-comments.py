#!/usr/bin/env python3
"""
GitLab Get Issue Comments Script
Usage: gitlab-get-issue-comments.py <project-path> <issue-iid> [options]
"""

import sys
import argparse
from typing import List, Dict, Any

from gitlab_common import (
    ALLOWED_GROUPS,
    get_gitlab_client,
    validate_project,
    print_table,
    print_json,
    print_error,
    format_date,
    truncate,
)


def get_issue_comments(gl, project_path: str, issue_iid: int,
                       limit: int = 50, sort: str = "asc",
                       include_system: bool = False) -> List[Dict[str, Any]]:
    """Get comments/notes for an issue"""
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

    try:
        notes = issue.notes.list(sort=sort, per_page=min(limit, 100), get_all=(limit > 100))
        results = []
        for note in notes:
            if len(results) >= limit:
                break
            if not include_system and getattr(note, "system", False):
                continue
            results.append({
                "id": note.id,
                "author": note.author.get("username", "") if note.author else "",
                "author_name": note.author.get("name", "") if note.author else "",
                "created_at": note.created_at or "",
                "updated_at": note.updated_at or "",
                "body": note.body or "",
                "system": getattr(note, "system", False),
            })
        return results
    except Exception as e:
        print_error(f"Failed to get comments for issue #{issue_iid}: {e}")
        sys.exit(1)


def format_table_output(comments: List[Dict[str, Any]], project_path: str, issue_iid: int):
    """Format comments as table"""
    if not comments:
        print("No comments found.")
        return

    print(f"\nComments for {project_path}#{issue_iid} ({len(comments)} comment(s)):\n")

    headers = ["Author", "Date", "Comment"]
    rows = []
    for c in comments:
        rows.append([
            c["author"],
            format_date(c["created_at"]),
            truncate(c["body"].replace("\n", " "), 80),
        ])
    print_table(headers, rows, max_widths={0: 25, 2: 80})


def main():
    parser = argparse.ArgumentParser(
        description="Get GitLab issue comments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s cit-iaas/cid/caas-devops 124
  %(prog)s cit-iaas/cid/caas-devops 124 --format json
  %(prog)s cit-iaas/cid/caas-devops 124 --include-system
  %(prog)s cit/t-caas/my-repo 42 --limit 10 --sort desc
        """
    )

    parser.add_argument("project", help="Project path (e.g., cit-iaas/cid/caas-devops)")
    parser.add_argument("issue_iid", type=int, help="Issue IID (number)")
    parser.add_argument("--format", choices=["table", "json"], default="table",
                        help="Output format (default: table)")
    parser.add_argument("--limit", type=int, default=50,
                        help="Maximum number of comments (default: 50)")
    parser.add_argument("--sort", choices=["asc", "desc"], default="asc",
                        help="Sort order (default: asc, oldest first)")
    parser.add_argument("--include-system", action="store_true",
                        help="Include system notes (title changes, label changes, etc.)")

    args = parser.parse_args()

    if not validate_project(args.project):
        print_error(f"Project '{args.project}' is not in an allowed group")
        print(f"Allowed group prefixes: {', '.join(ALLOWED_GROUPS)}", file=sys.stderr)
        sys.exit(1)

    gl = get_gitlab_client()
    comments = get_issue_comments(
        gl, args.project, args.issue_iid,
        limit=args.limit, sort=args.sort,
        include_system=args.include_system,
    )

    if args.format == "json":
        print_json(comments)
    else:
        format_table_output(comments, args.project, args.issue_iid)


if __name__ == "__main__":
    main()
