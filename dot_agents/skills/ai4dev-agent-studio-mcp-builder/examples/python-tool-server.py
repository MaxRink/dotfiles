#!/usr/bin/env python3
"""
Example MCP server demonstrating tools, resources, and prompts.

This server provides file analysis utilities:
- file_stats: Get statistics about a file (lines, words, characters)
- search_text: Search for a pattern in files
- list_directory: List contents of a directory

Plus a resource for server configuration and a prompt for code review.

Usage:
    python python-tool-server.py

Configure in .mcp.json:
    {
      "mcpServers": {
        "file-tools": {
          "command": "python",
          "args": ["${CLAUDE_PLUGIN_ROOT}/servers/python-tool-server.py"]
        }
      }
    }
"""

import json
import os
import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("file-tools")


# --- Tools ---


@mcp.tool()
def file_stats(path: str) -> str:
    """Get statistics about a file: line count, word count, character count, and file size."""
    try:
        file_path = Path(path)
        if not file_path.is_file():
            return f"Error: Not a file: {path}"

        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        words = content.split()
        size_bytes = file_path.stat().st_size

        return json.dumps(
            {
                "path": str(file_path.resolve()),
                "lines": len(lines),
                "words": len(words),
                "characters": len(content),
                "size_bytes": size_bytes,
                "empty_lines": sum(1 for line in lines if not line.strip()),
            },
            indent=2,
        )
    except UnicodeDecodeError:
        return f"Error: File is not valid UTF-8 text: {path}"
    except PermissionError:
        return f"Error: Permission denied: {path}"
    except FileNotFoundError:
        return f"Error: File not found: {path}"


@mcp.tool()
def search_text(pattern: str, directory: str = ".", file_glob: str = "*") -> str:
    """Search for a regex pattern in files within a directory.

    Args:
        pattern: Regular expression to search for.
        directory: Directory to search in. Defaults to current directory.
        file_glob: Glob pattern to filter files. Defaults to all files.
    """
    try:
        regex = re.compile(pattern)
    except re.error as e:
        return f"Error: Invalid regex pattern: {e}"

    dir_path = Path(directory)
    if not dir_path.is_dir():
        return f"Error: Not a directory: {directory}"

    matches = []
    file_count = 0
    max_results = 50

    for file_path in sorted(dir_path.rglob(file_glob)):
        if not file_path.is_file():
            continue
        try:
            content = file_path.read_text(encoding="utf-8")
            file_count += 1
        except (UnicodeDecodeError, PermissionError):
            continue

        for line_num, line in enumerate(content.splitlines(), start=1):
            if regex.search(line):
                matches.append(
                    {
                        "file": str(file_path),
                        "line": line_num,
                        "text": line.strip()[:200],
                    }
                )
                if len(matches) >= max_results:
                    return json.dumps(
                        {
                            "matches": matches,
                            "files_searched": file_count,
                            "truncated": True,
                        },
                        indent=2,
                    )

    return json.dumps(
        {
            "matches": matches,
            "files_searched": file_count,
            "truncated": False,
        },
        indent=2,
    )


@mcp.tool()
def list_directory(path: str = ".", include_hidden: bool = False) -> str:
    """List contents of a directory with file types and sizes.

    Args:
        path: Directory path to list. Defaults to current directory.
        include_hidden: Whether to include hidden files (starting with dot).
    """
    dir_path = Path(path)
    if not dir_path.is_dir():
        return f"Error: Not a directory: {path}"

    entries = []
    try:
        for entry in sorted(dir_path.iterdir()):
            if not include_hidden and entry.name.startswith("."):
                continue
            entry_info = {
                "name": entry.name,
                "type": "directory" if entry.is_dir() else "file",
            }
            if entry.is_file():
                entry_info["size_bytes"] = entry.stat().st_size
            entries.append(entry_info)
    except PermissionError:
        return f"Error: Permission denied: {path}"

    return json.dumps(
        {"path": str(dir_path.resolve()), "entries": entries, "count": len(entries)},
        indent=2,
    )


# --- Resources ---


@mcp.resource("config://server-info")
def get_server_info() -> str:
    """Expose server configuration and capabilities."""
    return json.dumps(
        {
            "server": "file-tools",
            "version": "1.0.0",
            "tools": ["file_stats", "search_text", "list_directory"],
            "cwd": os.getcwd(),
        },
        indent=2,
    )


# --- Prompts ---


@mcp.prompt()
def review_file(file_path: str, focus: str = "general") -> str:
    """Generate a prompt to review a file's contents.

    Args:
        file_path: Path to the file to review.
        focus: Review focus area - general, security, performance, or readability.
    """
    focus_instructions = {
        "general": "Review for bugs, code quality, and improvements",
        "security": "Focus on security vulnerabilities and input validation",
        "performance": "Focus on performance bottlenecks and optimization opportunities",
        "readability": "Focus on code clarity, naming, and documentation",
    }
    instruction = focus_instructions.get(focus, focus_instructions["general"])
    return f"{instruction} in the file at: {file_path}"


# --- Entry point ---

if __name__ == "__main__":
    mcp.run()
