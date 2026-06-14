#!/usr/bin/env python3
"""Generate AI IDE instruction files from the plugin's output style + pipeline description.

Produces config files for: GitHub Copilot, Cursor, Windsurf, JetBrains/Junie, Cline, Aider.
All files point the host LLM at the same goal-driven behavior and pipeline awareness.

Usage: python3 generate_host_configs.py [project-root]
"""

import os
import sys
from pathlib import Path


def get_instructions() -> str:
    """Core instructions shared across all hosts."""
    return """You are operating within the one-modernizer migration plugin.

## Pipeline

Run skills in order: discover → assess → decompose → architect → implement → validate.
Each skill depends on the prior skill's output in .migration/.

## Behavior

- State the goal once. Work toward it. Report the result.
- No preambles, no summaries of what you just did, no hedging.
- When asking questions, give concrete options — not open-ended prose.
- When something fails, state what failed and fix it. Don't explain the error generically.
- Trust code over comments. Every claim needs a file:line citation.

## Key Paths

- Knowledge graph: .migration/discovery/graphify-out/graph.json
- Module docs: .migration/discovery/modules/*.md
- Pipeline state: .migration/index.json

## Tools

- `one-modernizer extract` — build knowledge graph from source
- `one-modernizer query "<question>" --graph <path>` — query the graph
- `one-modernizer path "A" "B" --graph <path>` — find path between nodes
"""


def write_copilot(root: Path):
    out = root / ".github" / "copilot-instructions.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(get_instructions(), encoding="utf-8")
    return out


def write_cursor(root: Path):
    out = root / ".cursor" / "rules" / "one-modernizer.mdc"
    out.parent.mkdir(parents=True, exist_ok=True)
    frontmatter = """---
description: "one-modernizer migration plugin — goal-driven, terse output"
globs: "**/*"
alwaysApply: true
---
"""
    out.write_text(frontmatter + get_instructions(), encoding="utf-8")
    return out


def write_windsurf(root: Path):
    out = root / ".windsurfrules"
    out.write_text(get_instructions(), encoding="utf-8")
    return out


def write_junie(root: Path):
    out = root / ".junie" / "guidelines.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(get_instructions(), encoding="utf-8")
    return out


def write_cline(root: Path):
    out = root / ".clinerules"
    out.write_text(get_instructions(), encoding="utf-8")
    return out


def write_aider(root: Path):
    out = root / ".aider.conventions.md"
    out.write_text(get_instructions(), encoding="utf-8")
    return out


GENERATORS = {
    "copilot": write_copilot,
    "cursor": write_cursor,
    "windsurf": write_windsurf,
    "junie": write_junie,
    "cline": write_cline,
    "aider": write_aider,
}


def main():
    hosts = []
    root_arg = None

    args = sys.argv[1:]
    while args:
        arg = args.pop(0)
        if arg == "--host" and args:
            hosts.append(args.pop(0).lower())
        elif not arg.startswith("-"):
            root_arg = arg

    root = Path(root_arg or os.getenv("CLAUDE_PROJECT_DIR", ".")).resolve()

    if not hosts:
        print("Usage: python3 generate_host_configs.py [root] --host <name>")
        print(f"Available hosts: {', '.join(GENERATORS.keys())}")
        print("Use --host multiple times for multiple targets.")
        sys.exit(1)

    invalid = [h for h in hosts if h not in GENERATORS]
    if invalid:
        print(f"Unknown host(s): {', '.join(invalid)}")
        print(f"Available: {', '.join(GENERATORS.keys())}")
        sys.exit(1)

    for name in hosts:
        path = GENERATORS[name](root)
        print(f"  {name}: {path.relative_to(root)}")


if __name__ == "__main__":
    main()
