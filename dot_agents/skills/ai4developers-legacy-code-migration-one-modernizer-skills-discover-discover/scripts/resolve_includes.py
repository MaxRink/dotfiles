#!/usr/bin/env python3
"""Resolve COBOL COPY and C/C++ #include chains to build composite data structures.

Usage: python3 resolve_includes.py [project-root] [--include-path PATH ...]

Outputs:
- .migration/includes/resolution-map.json — file → resolved includes
- .migration/includes/shared-structures.md — which programs share which copybooks/headers
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _constants import COBOL_EXTENSIONS, C_EXTENSIONS, IGNORE_DIRS

_RE_COBOL_COPY = re.compile(r"^\s+COPY\s+(\S+?)[\s.]", re.MULTILINE | re.IGNORECASE)
_RE_C_INCLUDE_LOCAL = re.compile(r'^\s*#\s*include\s+"([^"]+)"', re.MULTILINE)


def find_source_files(root: Path, extensions: set) -> list[Path]:
    files = []
    for f in root.rglob("*"):
        if any(part in IGNORE_DIRS for part in f.parts):
            continue
        if f.is_file() and f.suffix.lower() in extensions:
            files.append(f)
    return sorted(files)


def find_copybook(name: str, search_paths: list[Path]) -> Path | None:
    candidates = [name, f"{name}.cpy", f"{name}.CPY", f"{name}.cbl", f"{name}.CBL"]
    for sp in search_paths:
        for cand in candidates:
            p = sp / cand
            if p.exists():
                return p
    return None


def find_header(name: str, search_paths: list[Path]) -> Path | None:
    for sp in search_paths:
        p = sp / name
        if p.exists():
            return p
    return None


def resolve_cobol(root: Path, search_paths: list[Path]) -> dict:
    """Resolve all COPY statements in COBOL files."""
    cobol_files = find_source_files(root, COBOL_EXTENSIONS)
    resolution = {}
    copybook_usage = defaultdict(list)

    for f in cobol_files:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        rel = str(f.relative_to(root))
        copies = []

        for m in _RE_COBOL_COPY.finditer(content):
            copybook_name = m.group(1).rstrip(".")
            resolved = find_copybook(copybook_name, search_paths)
            entry = {
                "name": copybook_name,
                "resolved_path": str(resolved.relative_to(root)) if resolved else None,
                "line": content[: m.start()].count("\n") + 1,
            }
            copies.append(entry)
            copybook_usage[copybook_name].append(rel)

        if copies:
            resolution[rel] = copies

    return {"resolution": resolution, "copybook_usage": dict(copybook_usage)}


def resolve_c_includes(root: Path, search_paths: list[Path]) -> dict:
    """Resolve all local #include statements in C/C++ files."""
    c_files = find_source_files(root, C_EXTENSIONS)
    resolution = {}
    header_usage = defaultdict(list)

    for f in c_files:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        rel = str(f.relative_to(root))
        includes = []

        for m in _RE_C_INCLUDE_LOCAL.finditer(content):
            header_name = m.group(1)
            file_search_paths = [f.parent] + search_paths
            resolved = find_header(header_name, file_search_paths)
            entry = {
                "name": header_name,
                "resolved_path": str(resolved.relative_to(root)) if resolved else None,
                "line": content[: m.start()].count("\n") + 1,
            }
            includes.append(entry)
            header_usage[header_name].append(rel)

        if includes:
            resolution[rel] = includes

    return {"resolution": resolution, "header_usage": dict(header_usage)}


def build_shared_structures_report(cobol_data: dict, c_data: dict) -> str:
    """Generate markdown report of shared structures."""
    lines = ["# Shared Data Structures — Inclusion Analysis\n"]

    # COBOL copybooks
    usage = cobol_data.get("copybook_usage", {})
    if usage:
        lines.append("## COBOL Copybooks\n")
        lines.append("| Copybook | Used By (Programs) | Impact Radius |")
        lines.append("| -------- | ------------------ | ------------- |")
        for name, programs in sorted(usage.items(), key=lambda x: -len(x[1])):
            lines.append(
                f"| {name} | {len(programs)} programs | {'HIGH' if len(programs) > 5 else 'MEDIUM' if len(programs) > 2 else 'LOW'} |"
            )
        lines.append("")

        # Top shared copybooks detail
        top = sorted(usage.items(), key=lambda x: -len(x[1]))[:10]
        for name, programs in top:
            lines.append(f"### {name}")
            lines.append(f"\nUsed by {len(programs)} programs:\n")
            for p in programs[:20]:
                lines.append(f"- `{p}`")
            if len(programs) > 20:
                lines.append(f"- ... and {len(programs) - 20} more")
            lines.append("")

    # C/C++ headers
    h_usage = c_data.get("header_usage", {})
    if h_usage:
        lines.append("## C/C++ Headers\n")
        lines.append("| Header | Included By (Files) | Impact Radius |")
        lines.append("| ------ | ------------------- | ------------- |")
        for name, files in sorted(h_usage.items(), key=lambda x: -len(x[1])):
            lines.append(
                f"| {name} | {len(files)} files | {'HIGH' if len(files) > 10 else 'MEDIUM' if len(files) > 3 else 'LOW'} |"
            )
        lines.append("")

    # Unresolved includes
    unresolved_cobol = []
    for file_path, copies in cobol_data.get("resolution", {}).items():
        for c in copies:
            if c["resolved_path"] is None:
                unresolved_cobol.append((file_path, c["name"], c["line"]))

    unresolved_c = []
    for file_path, includes in c_data.get("resolution", {}).items():
        for inc in includes:
            if inc["resolved_path"] is None:
                unresolved_c.append((file_path, inc["name"], inc["line"]))

    if unresolved_cobol or unresolved_c:
        lines.append("## Unresolved Includes\n")
        if unresolved_cobol:
            lines.append("### COBOL (missing copybooks)\n")
            for fp, name, line in unresolved_cobol[:20]:
                lines.append(f"- `{fp}:{line}` — COPY {name}")
            lines.append("")
        if unresolved_c:
            lines.append("### C/C++ (missing headers)\n")
            for fp, name, line in unresolved_c[:20]:
                lines.append(f'- `{fp}:{line}` — #include "{name}"')
            lines.append("")

    return "\n".join(lines)


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

    # Parse --include-path arguments
    extra_paths = []
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--include-path" and i + 1 < len(args):
            extra_paths.append(Path(args[i + 1]).resolve())
            i += 2
        else:
            i += 1

    # Default search paths: project root + common conventions
    search_paths = [root] + extra_paths
    for subdir in ("COPYLIB", "copylib", "copybooks", "include", "inc", "src/include"):
        p = root / subdir
        if p.is_dir():
            search_paths.append(p)
    # Add all directories containing .cpy files
    for f in root.rglob("*.cpy"):
        if f.parent not in search_paths:
            search_paths.append(f.parent)

    print(f"Resolving includes in {root.name}...", file=sys.stderr)
    print(f"Search paths: {len(search_paths)}", file=sys.stderr)

    cobol_data = resolve_cobol(root, search_paths)
    c_data = resolve_c_includes(root, search_paths)

    # Output directory
    out_dir = root / ".migration" / "discovery" / "includes"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Write resolution map
    combined = {
        "cobol": cobol_data,
        "c_cpp": c_data,
        "search_paths": [str(p) for p in search_paths],
    }
    (out_dir / "resolution-map.json").write_text(
        json.dumps(combined, indent=2), encoding="utf-8"
    )

    # Write shared structures report
    report = build_shared_structures_report(cobol_data, c_data)
    (out_dir / "shared-structures.md").write_text(report, encoding="utf-8")

    # Summary
    cobol_count = len(cobol_data.get("resolution", {}))
    c_count = len(c_data.get("resolution", {}))
    cb_unique = len(cobol_data.get("copybook_usage", {}))
    h_unique = len(c_data.get("header_usage", {}))

    print("\n# Include Resolution Summary")
    print("")
    print(
        f"**COBOL**: {cobol_count} files with COPY statements, {cb_unique} unique copybooks"
    )
    print(f"**C/C++**: {c_count} files with local includes, {h_unique} unique headers")
    print("")
    print(f"Output: {out_dir}")


if __name__ == "__main__":
    main()
