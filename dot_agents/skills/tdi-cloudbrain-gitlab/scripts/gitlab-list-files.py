#!/usr/bin/env python3
"""
GitLab List Files Script - List files and directories in a repository
Usage: gitlab-list-files.py <project-path> [options]
"""

import sys
import json
import argparse
from typing import List, Dict, Any

import gitlab

from gitlab_common import (
    ALLOWED_GROUPS,
    get_gitlab_client,
    validate_project,
)


def list_files(gl, project_path: str, path: str = "", ref: str = None,
               recursive: bool = False, limit: int = 100) -> List[Dict[str, Any]]:
    """List files and directories in a repository path"""
    try:
        project = gl.projects.get(project_path)
    except Exception as e:
        print(f"Error: Failed to get project '{project_path}': {e}", file=sys.stderr)
        sys.exit(1)

    try:
        kwargs: Dict[str, Any] = {
            "path": path,
            "recursive": recursive,
            "per_page": min(limit, 100),
            "get_all": False,
            "iterator": True,
        }
        if ref:
            kwargs["ref"] = ref

        items = project.repository_tree(**kwargs)

        result = []
        count = 0
        for item in items:
            if count >= limit:
                break
            result.append({
                "name": item["name"],
                "path": item["path"],
                "type": "dir" if item["type"] == "tree" else "file",
                "mode": item.get("mode", ""),
            })
            count += 1

        return result

    except gitlab.exceptions.GitlabGetError as e:
        if "404" in str(e):
            print(f"Error: Path '{path}' not found in project", file=sys.stderr)
        else:
            print(f"Error: Failed to list files: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to list files: {e}", file=sys.stderr)
        sys.exit(1)


def format_table(items: List[Dict[str, Any]], path: str):
    """Format file listing as table"""
    if not items:
        print(f"No files found in '{path or '/'}'")
        return

    # Sort: directories first, then files, alphabetically
    dirs = sorted([i for i in items if i["type"] == "dir"], key=lambda x: x["name"])
    files = sorted([i for i in items if i["type"] == "file"], key=lambda x: x["name"])
    sorted_items = dirs + files

    print(f"{'Type':<6} {'Name':<50} {'Path'}")
    print("-" * 100)

    for item in sorted_items:
        type_indicator = "📁" if item["type"] == "dir" else "📄"
        print(f"{type_indicator:<6} {item['name']:<50} {item['path']}")

    print(f"\nTotal: {len(dirs)} directories, {len(files)} files")


def format_json(items: List[Dict[str, Any]]):
    """Format file listing as JSON"""
    print(json.dumps(items, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="List files and directories in a GitLab repository",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List root directory
  %(prog)s cit/t-caas/my-repo

  # List specific directory
  %(prog)s cit/t-caas/my-repo --path src/

  # List with specific branch
  %(prog)s cit/t-caas/my-repo --path src/ --ref develop

  # Recursive listing
  %(prog)s cit/t-caas/my-repo --recursive --path src/

  # JSON output
  %(prog)s cit/t-caas/my-repo --format json
        """
    )

    parser.add_argument("project", help="Full project path (e.g., cit/t-caas/my-repo)")
    parser.add_argument("--path", default="",
                        help="Directory path within the repository (default: root)")
    parser.add_argument("--ref",
                        help="Branch, tag, or commit SHA (default: default branch)")
    parser.add_argument("--recursive", action="store_true",
                        help="List files recursively")
    parser.add_argument("--format", choices=["table", "json"], default="table",
                        help="Output format (default: table)")
    parser.add_argument("--limit", type=int, default=100,
                        help="Maximum number of results (default: 100)")

    args = parser.parse_args()

    # Validate project
    if not validate_project(args.project):
        print(f"Error: Project '{args.project}' is not in an allowed group", file=sys.stderr)
        print(f"Allowed groups: {', '.join(ALLOWED_GROUPS)} (and their subgroups)", file=sys.stderr)
        sys.exit(1)

    # Initialize GitLab client
    gl = get_gitlab_client()

    # List files
    items = list_files(
        gl, args.project,
        path=args.path,
        ref=args.ref,
        recursive=args.recursive,
        limit=args.limit,
    )

    # Format output
    if args.format == "json":
        format_json(items)
    else:
        format_table(items, args.path)


if __name__ == "__main__":
    main()
