#!/usr/bin/env python3
"""
GitLab Get File Script - Read file content from a repository
Usage: gitlab-get-file.py <project-path> --path <file-path> [options]
"""

import os
import sys
import json
import argparse
from typing import Dict, Any

import gitlab

from gitlab_common import (
    ALLOWED_GROUPS,
    get_gitlab_client,
    validate_project,
)

# Maximum file size to display (1MB)
MAX_FILE_SIZE = 1024 * 1024

# Binary file extensions
BINARY_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.webp',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.zip', '.tar', '.gz', '.bz2', '.7z', '.rar',
    '.exe', '.dll', '.so', '.dylib', '.bin',
    '.pyc', '.pyo', '.class', '.o', '.a',
    '.woff', '.woff2', '.ttf', '.eot', '.otf',
    '.mp3', '.mp4', '.avi', '.mov', '.wav', '.flac',
}


def is_binary_file(file_path: str) -> bool:
    """Check if file is likely binary based on extension"""
    ext = os.path.splitext(file_path)[1].lower()
    return ext in BINARY_EXTENSIONS


def get_file(gl, project_path: str, file_path: str, ref: str = None) -> Dict[str, Any]:
    """Get file content and metadata from repository"""
    try:
        project = gl.projects.get(project_path)
    except Exception as e:
        print(f"Error: Failed to get project '{project_path}': {e}", file=sys.stderr)
        sys.exit(1)

    try:
        # Get file metadata first
        kwargs = {"file_path": file_path}
        if ref:
            kwargs["ref"] = ref
        else:
            # Use default branch
            kwargs["ref"] = project.default_branch or "main"

        f = project.files.get(**kwargs)

        file_info = {
            "file_name": f.file_name,
            "file_path": f.file_path,
            "size": f.size,
            "ref": kwargs["ref"],
            "encoding": f.encoding,
            "content_sha256": f.content_sha256,
            "last_commit_id": f.last_commit_id,
        }

        # Check if binary
        if is_binary_file(file_path):
            file_info["is_binary"] = True
            file_info["content"] = None
            file_info["message"] = f"Binary file ({f.size} bytes) - content not displayed"
            return file_info

        # Check file size
        if f.size > MAX_FILE_SIZE:
            file_info["is_binary"] = False
            file_info["content"] = None
            file_info["message"] = f"File too large ({f.size} bytes > {MAX_FILE_SIZE} bytes) - content not displayed"
            return file_info

        # Decode content
        try:
            content = f.decode()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            file_info["content"] = content
            file_info["is_binary"] = False
        except UnicodeDecodeError:
            file_info["is_binary"] = True
            file_info["content"] = None
            file_info["message"] = f"Binary content detected ({f.size} bytes) - content not displayed"

        return file_info

    except gitlab.exceptions.GitlabGetError as e:
        if "404" in str(e):
            print(f"Error: File '{file_path}' not found in project", file=sys.stderr)
        else:
            print(f"Error: Failed to get file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to get file: {e}", file=sys.stderr)
        sys.exit(1)


def format_raw(file_info: Dict[str, Any]):
    """Output raw file content"""
    if file_info.get("content") is None:
        print(f"# {file_info.get('message', 'Content not available')}", file=sys.stderr)
        print(f"# File: {file_info['file_path']}", file=sys.stderr)
        print(f"# Size: {file_info['size']} bytes", file=sys.stderr)
        print(f"# Ref: {file_info['ref']}", file=sys.stderr)
        sys.exit(0)

    print(file_info["content"])


def format_json(file_info: Dict[str, Any]):
    """Output file info as JSON"""
    print(json.dumps(file_info, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Get file content from a GitLab repository",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get file from default branch
  %(prog)s cit/t-caas/my-repo --path README.md

  # Get file from specific branch
  %(prog)s cit/t-caas/my-repo --path src/main.py --ref develop

  # Get file from specific commit
  %(prog)s cit/t-caas/my-repo --path config.yaml --ref abc123def

  # Get with metadata (JSON)
  %(prog)s cit/t-caas/my-repo --path src/main.py --format json
        """
    )

    parser.add_argument("project", help="Full project path (e.g., cit/t-caas/my-repo)")
    parser.add_argument("--path", required=True,
                        help="File path within the repository")
    parser.add_argument("--ref",
                        help="Branch, tag, or commit SHA (default: default branch)")
    parser.add_argument("--format", choices=["raw", "json"], default="raw",
                        help="Output format (default: raw)")

    args = parser.parse_args()

    # Validate project
    if not validate_project(args.project):
        print(f"Error: Project '{args.project}' is not in an allowed group", file=sys.stderr)
        print(f"Allowed groups: {', '.join(ALLOWED_GROUPS)} (and their subgroups)", file=sys.stderr)
        sys.exit(1)

    # Initialize GitLab client
    gl = get_gitlab_client()

    # Get file
    file_info = get_file(gl, args.project, args.path, ref=args.ref)

    # Format output
    if args.format == "json":
        format_json(file_info)
    else:
        format_raw(file_info)


if __name__ == "__main__":
    main()
