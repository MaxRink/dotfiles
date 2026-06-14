#!/usr/bin/env python3
"""
GitLab Search Code Script - Search for patterns in repository code
Usage: gitlab-search-code.py --query <search-term> [--project <path> | --group <path>] [options]
"""

import sys
import json
import argparse
from typing import List, Dict, Any

from gitlab_common import (
    ALLOWED_GROUPS,
    get_gitlab_client,
    validate_group,
    validate_project,
)


def search_in_project(gl, project_path: str, query: str, ref: str = None,
                      limit: int = 50) -> List[Dict[str, Any]]:
    """Search code in a specific project"""
    try:
        project = gl.projects.get(project_path)
    except Exception as e:
        print(f"Error: Failed to get project '{project_path}': {e}", file=sys.stderr)
        sys.exit(1)

    try:
        kwargs = {
            "scope": "blobs",
            "search": query,
            "per_page": min(limit, 100),
            "get_all": False,
            "iterator": True,
        }
        if ref:
            kwargs["ref"] = ref

        results = project.search(**kwargs)

        output = []
        count = 0
        for item in results:
            if count >= limit:
                break
            output.append({
                "project": project_path,
                "file": item.get("path", item.get("filename", "")),
                "ref": item.get("ref", ref or "default"),
                "startline": item.get("startline", 0),
                "data": item.get("data", ""),
            })
            count += 1

        return output

    except Exception as e:
        print(f"Error: Search failed: {e}", file=sys.stderr)
        sys.exit(1)


def search_in_group(gl, group_path: str, query: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Search code across all projects in a group"""
    try:
        group = gl.groups.get(group_path)
    except Exception as e:
        print(f"Error: Failed to get group '{group_path}': {e}", file=sys.stderr)
        sys.exit(1)

    try:
        kwargs = {
            "scope": "blobs",
            "search": query,
            "per_page": min(limit, 100),
            "get_all": False,
            "iterator": True,
        }

        results = group.search(**kwargs)

        output = []
        count = 0
        for item in results:
            if count >= limit:
                break
            # Extract project path from the result
            project_id = item.get("project_id", "")
            output.append({
                "project_id": project_id,
                "file": item.get("path", item.get("filename", "")),
                "ref": item.get("ref", "default"),
                "startline": item.get("startline", 0),
                "data": item.get("data", ""),
            })
            count += 1

        return output

    except Exception as e:
        print(f"Error: Search failed: {e}", file=sys.stderr)
        sys.exit(1)


def format_table(results: List[Dict[str, Any]], query: str):
    """Format search results as table"""
    if not results:
        print(f"No results found for '{query}'")
        return

    print(f"{'File':<60} {'Line':<8} {'Match Preview'}")
    print("-" * 130)

    for item in results:
        file_path = item.get("file", "")
        if len(file_path) > 57:
            file_path = "..." + file_path[-54:]

        line = str(item.get("startline", "-"))

        # Clean up match preview
        data = item.get("data", "").strip()
        # Truncate long lines
        if len(data) > 60:
            data = data[:57] + "..."
        # Remove newlines for display
        data = data.replace("\n", " ").replace("\r", "")

        print(f"{file_path:<60} {line:<8} {data}")

    print(f"\nTotal: {len(results)} match(es)")


def format_json(results: List[Dict[str, Any]]):
    """Format search results as JSON"""
    print(json.dumps(results, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Search for code patterns in GitLab repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search in a specific project
  %(prog)s --project cit/t-caas/my-repo --query "def main"

  # Search across a group (all projects)
  %(prog)s --group cit/t-caas --query "class Handler"

  # Search in specific branch
  %(prog)s --project cit/t-caas/my-repo --query "TODO" --ref develop

  # JSON output
  %(prog)s --project cit/t-caas/my-repo --query "import os" --format json

  # Limit results
  %(prog)s --group tdi-caas --query "kubernetes" --limit 20
        """
    )

    parser.add_argument("--project",
                        help="Project path to search in (e.g., cit/t-caas/my-repo)")
    parser.add_argument("--group",
                        help="Group path to search across (e.g., cit/t-caas)")
    parser.add_argument("--query", required=True,
                        help="Search query/pattern")
    parser.add_argument("--ref",
                        help="Branch, tag, or commit SHA (only for project search)")
    parser.add_argument("--format", choices=["table", "json"], default="table",
                        help="Output format (default: table)")
    parser.add_argument("--limit", type=int, default=50,
                        help="Maximum number of results (default: 50)")

    args = parser.parse_args()

    # Validate that either project or group is specified
    if not args.project and not args.group:
        print("Error: Either --project or --group must be specified", file=sys.stderr)
        sys.exit(1)

    if args.project and args.group:
        print("Error: Cannot specify both --project and --group", file=sys.stderr)
        sys.exit(1)

    # Validate project or group
    if args.project:
        if not validate_project(args.project):
            print(f"Error: Project '{args.project}' is not in an allowed group", file=sys.stderr)
            print(f"Allowed groups: {', '.join(ALLOWED_GROUPS)} (and their subgroups)", file=sys.stderr)
            sys.exit(1)
    else:
        if not validate_group(args.group):
            print(f"Error: Group '{args.group}' is not allowed", file=sys.stderr)
            print(f"Allowed groups: {', '.join(ALLOWED_GROUPS)} (and their subgroups)", file=sys.stderr)
            sys.exit(1)

    # Warn about --ref with group search
    if args.group and args.ref:
        print("Warning: --ref is ignored for group searches", file=sys.stderr)

    # Initialize GitLab client
    gl = get_gitlab_client()

    # Search
    if args.project:
        results = search_in_project(gl, args.project, args.query, ref=args.ref, limit=args.limit)
    else:
        results = search_in_group(gl, args.group, args.query, limit=args.limit)

    # Format output
    if args.format == "json":
        format_json(results)
    else:
        format_table(results, args.query)


if __name__ == "__main__":
    main()
