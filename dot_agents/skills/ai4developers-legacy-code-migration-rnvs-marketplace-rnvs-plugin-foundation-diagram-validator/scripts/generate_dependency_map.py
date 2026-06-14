#!/usr/bin/env python3
"""
Dependency Map Generator

Generates dependency_map.md from Phase1 analysis results.
This markdown file is required by Phase3 for migration planning.

Requirements:
- Python 3.10+
- No external dependencies (standard library only)

Usage:
    python generate_dependency_map.py --phase1-analysis phase1/analysis.json \
                                      --phase1-deps phase1/dependency-graph.json \
                                      --output phase2/dependency_map.md \
                                      --feature NBM
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set


def load_phase1_data(analysis_path: Path, deps_path: Path) -> tuple:
    """Load Phase1 analysis and dependency graph data."""
    # Load analysis.json
    analysis_data = json.loads(analysis_path.read_text(encoding='utf-8'))

    # Load dependency-graph.json
    deps_data = json.loads(deps_path.read_text(encoding='utf-8'))

    return analysis_data, deps_data


def extract_components(analysis_data: Dict) -> Dict[str, Dict]:
    """
    Extract component information from analysis.json.

    Returns:
        Dict of component_name -> {type, description, files}
    """
    components = {}

    for component in analysis_data.get("components", []):
        name = component["name"]
        components[name] = {
            "type": component.get("type", "unknown"),
            "description": component.get("description", "No description"),
            "files": component.get("files", []),
            "responsibilities": component.get("responsibilities", [])
        }

    return components


def extract_dependencies(deps_data: Dict) -> Dict[str, List[str]]:
    """
    Extract dependency relationships from dependency-graph.json.

    Returns:
        Dict of component_name -> [list of dependencies]
    """
    dependencies = defaultdict(list)

    for node in deps_data.get("nodes", []):
        component = node["id"]
        for dep in node.get("dependencies", []):
            dependencies[component].append(dep)

    return dict(dependencies)


def extract_database_interactions(components: Dict, dependencies: Dict) -> Dict[str, List[str]]:
    """
    Extract database interactions from components and dependencies.

    Returns:
        Dict of component_name -> [list of databases]
    """
    # Identify database components
    databases = {
        name for name, info in components.items()
        if info["type"] == "database"
    }

    # Find components that depend on databases
    db_interactions = defaultdict(list)

    for component, deps in dependencies.items():
        for dep in deps:
            if dep in databases:
                db_interactions[component].append(dep)

    return dict(db_interactions)


def generate_dependency_map_markdown(
    feature: str,
    components: Dict[str, Dict],
    dependencies: Dict[str, List[str]],
    db_interactions: Dict[str, List[str]]
) -> str:
    """
    Generate dependency_map.md markdown content.

    Args:
        feature: Feature name (e.g., "NBM")
        components: Component information
        dependencies: Component dependencies
        db_interactions: Database interactions

    Returns:
        Markdown content as string
    """
    lines = []

    # Header
    lines.append(f"# Dependency Map: {feature}")
    lines.append("")
    lines.append("**Generated from Phase1 Analysis**")
    lines.append("")
    lines.append("This document provides a comprehensive mapping of components, their dependencies, and database interactions discovered during Phase1 code analysis.")
    lines.append("")

    # Table of Contents
    lines.append("## Table of Contents")
    lines.append("")
    lines.append("1. [Component Overview](#component-overview)")
    lines.append("2. [Dependency Matrix](#dependency-matrix)")
    lines.append("3. [Database Interactions](#database-interactions)")
    lines.append("4. [Component Details](#component-details)")
    lines.append("")

    # Section 1: Component Overview
    lines.append("## Component Overview")
    lines.append("")
    lines.append(f"**Total Components**: {len(components)}")
    lines.append("")

    # Count by type
    type_counts = defaultdict(int)
    for info in components.values():
        type_counts[info["type"]] += 1

    lines.append("**Component Types**:")
    lines.append("")
    for comp_type, count in sorted(type_counts.items()):
        lines.append(f"- **{comp_type.capitalize()}**: {count}")
    lines.append("")

    # Component listing table
    lines.append("| Component | Type | Description |")
    lines.append("|-----------|------|-------------|")

    for name in sorted(components.keys()):
        info = components[name]
        comp_type = info["type"].capitalize()
        description = info["description"]
        # Truncate long descriptions
        if len(description) > 80:
            description = description[:77] + "..."
        lines.append(f"| {name} | {comp_type} | {description} |")

    lines.append("")

    # Section 2: Dependency Matrix
    lines.append("## Dependency Matrix")
    lines.append("")
    lines.append("This matrix shows which components depend on which other components.")
    lines.append("")

    if dependencies:
        lines.append("| Component | Depends On | Count |")
        lines.append("|-----------|------------|-------|")

        for component in sorted(dependencies.keys()):
            deps = dependencies[component]
            dep_list = ", ".join(sorted(deps))
            # Truncate long dependency lists
            if len(dep_list) > 60:
                dep_list = dep_list[:57] + "..."
            lines.append(f"| {component} | {dep_list} | {len(deps)} |")

        lines.append("")

        # Dependency statistics
        total_deps = sum(len(deps) for deps in dependencies.values())
        avg_deps = total_deps / len(dependencies) if dependencies else 0

        lines.append("**Dependency Statistics**:")
        lines.append("")
        lines.append(f"- **Total Dependencies**: {total_deps}")
        lines.append(f"- **Average per Component**: {avg_deps:.1f}")
        lines.append(f"- **Components with Dependencies**: {len(dependencies)}")
        lines.append("")
    else:
        lines.append("*No dependencies detected*")
        lines.append("")

    # Section 3: Database Interactions
    lines.append("## Database Interactions")
    lines.append("")

    # Identify databases
    databases = [name for name, info in components.items() if info["type"] == "database"]

    if databases:
        lines.append(f"**Databases**: {len(databases)}")
        lines.append("")

        for db in sorted(databases):
            lines.append(f"- {db}")

        lines.append("")
        lines.append("**Component-Database Interactions**:")
        lines.append("")

        if db_interactions:
            lines.append("| Component | Accesses Database(s) |")
            lines.append("|-----------|----------------------|")

            for component in sorted(db_interactions.keys()):
                db_list = ", ".join(sorted(db_interactions[component]))
                lines.append(f"| {component} | {db_list} |")

            lines.append("")
        else:
            lines.append("*No database interactions detected*")
            lines.append("")
    else:
        lines.append("*No databases detected*")
        lines.append("")

    # Section 4: Component Details
    lines.append("## Component Details")
    lines.append("")

    for name in sorted(components.keys()):
        info = components[name]

        # Component header
        lines.append(f"### {name}")
        lines.append("")

        # Type and description
        lines.append(f"**Type**: {info['type'].capitalize()}")
        lines.append("")
        lines.append(f"**Description**: {info['description']}")
        lines.append("")

        # Responsibilities
        if info.get("responsibilities"):
            lines.append("**Responsibilities**:")
            lines.append("")
            for resp in info["responsibilities"]:
                lines.append(f"- {resp}")
            lines.append("")

        # Dependencies
        if name in dependencies:
            deps = dependencies[name]
            lines.append(f"**Dependencies** ({len(deps)}):")
            lines.append("")
            for dep in sorted(deps):
                lines.append(f"- {dep}")
            lines.append("")
        else:
            lines.append("**Dependencies**: None")
            lines.append("")

        # Database interactions
        if name in db_interactions:
            dbs = db_interactions[name]
            lines.append(f"**Database Access**: {', '.join(sorted(dbs))}")
            lines.append("")

        # Files
        if info.get("files"):
            file_count = len(info["files"])
            lines.append(f"**Files** ({file_count}):")
            lines.append("")
            # Show first 5 files, then "and X more"
            for file_path in sorted(info["files"][:5]):
                lines.append(f"- `{file_path}`")
            if file_count > 5:
                lines.append(f"- *... and {file_count - 5} more files*")
            lines.append("")

        # Separator
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main():
    """Command-line interface for dependency map generation."""
    parser = argparse.ArgumentParser(
        description="Generate dependency_map.md from Phase1 analysis results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python generate_dependency_map.py --phase1-analysis results/NBM/phase1/analysis.json \\
                                    --phase1-deps results/NBM/phase1/dependency-graph.json \\
                                    --output results/NBM/phase2/dependency_map.md \\
                                    --feature NBM
        """
    )

    parser.add_argument(
        "--phase1-analysis",
        type=Path,
        required=True,
        help="Path to phase1/analysis.json"
    )
    parser.add_argument(
        "--phase1-deps",
        type=Path,
        required=True,
        help="Path to phase1/dependency-graph.json"
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path to output dependency_map.md"
    )
    parser.add_argument(
        "--feature",
        type=str,
        required=True,
        help="Feature name (e.g., NBM, PDA)"
    )

    args = parser.parse_args()

    # Validate input files exist
    if not args.phase1_analysis.exists():
        print(f"ERROR: Phase1 analysis not found: {args.phase1_analysis}", file=sys.stderr)
        sys.exit(1)

    if not args.phase1_deps.exists():
        print(f"ERROR: Phase1 dependency graph not found: {args.phase1_deps}", file=sys.stderr)
        sys.exit(1)

    # Load Phase1 data
    print(f"Loading Phase1 data...", file=sys.stderr)
    analysis_data, deps_data = load_phase1_data(args.phase1_analysis, args.phase1_deps)

    # Extract information
    print(f"Extracting components...", file=sys.stderr)
    components = extract_components(analysis_data)

    print(f"Extracting dependencies...", file=sys.stderr)
    dependencies = extract_dependencies(deps_data)

    print(f"Extracting database interactions...", file=sys.stderr)
    db_interactions = extract_database_interactions(components, dependencies)

    # Generate markdown
    print(f"Generating dependency_map.md...", file=sys.stderr)
    markdown_content = generate_dependency_map_markdown(
        feature=args.feature,
        components=components,
        dependencies=dependencies,
        db_interactions=db_interactions
    )

    # Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown_content, encoding='utf-8')

    print(f"✅ Dependency map written to: {args.output}", file=sys.stderr)
    print(f"   Components: {len(components)}", file=sys.stderr)
    print(f"   Dependencies: {sum(len(d) for d in dependencies.values())}", file=sys.stderr)
    print(f"   Database interactions: {sum(len(d) for d in db_interactions.values())}", file=sys.stderr)


if __name__ == "__main__":
    main()
