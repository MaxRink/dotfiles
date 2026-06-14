#!/usr/bin/env python3
"""
List all labels in the CID group to discover label conventions.

Usage:
    cid-list-labels.py [options]

Options:
    --search TEXT   Filter labels by name
    --format FORMAT Output format: table (default), json
    --limit N       Maximum results (default: 100)
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for utils import
sys.path.insert(0, str(Path(__file__).parent))

from utils import get_gitlab_client, get_cid_group, print_table, print_json, print_error
from utils.output import truncate
from utils.validators import validate_positive_int


def list_labels(search=None, limit=100):
    """
    List all labels in the CID group.

    Args:
        search: Filter labels by name
        limit: Maximum results

    Returns:
        list: List of label objects
    """
    gl = get_gitlab_client()
    group = get_cid_group(gl)

    try:
        params = {
            "include_ancestor_groups": True,
            "include_descendant_groups": True,
            "per_page": min(limit, 100),
        }

        if search:
            params["search"] = search

        labels = group.labels.list(**params)

        # Handle pagination if limit > 100
        if limit > 100:
            all_labels = list(labels)
            page = 2
            while len(all_labels) < limit:
                next_page = group.labels.list(**params, page=page)
                if not next_page:
                    break
                all_labels.extend(next_page)
                page += 1
            return all_labels[:limit]

        return list(labels)[:limit]

    except Exception as e:
        print_error(f"Failed to list labels: {e}")
        sys.exit(1)


def format_label_for_table(label):
    """Format a label for table display."""
    return [
        label.name,
        label.color,
        truncate(getattr(label, "description", "") or "", 50),
    ]


def format_label_for_json(label):
    """Format a label for JSON output."""
    return {
        "id": getattr(label, "id", None),
        "name": label.name,
        "color": label.color,
        "text_color": getattr(label, "text_color", None),
        "description": getattr(label, "description", None),
        "open_issues_count": getattr(label, "open_issues_count", None),
        "closed_issues_count": getattr(label, "closed_issues_count", None),
        "open_merge_requests_count": getattr(label, "open_merge_requests_count", None),
    }


def analyze_label_patterns(labels):
    """Analyze labels to identify naming patterns."""
    patterns = {}

    for label in labels:
        name = label.name
        # Check for scoped labels (e.g., "status::in-progress")
        if "::" in name:
            scope = name.split("::")[0]
            if scope not in patterns:
                patterns[scope] = []
            patterns[scope].append(name)
        # Check for prefixed labels (e.g., "DC-AMS")
        elif "-" in name:
            prefix = name.split("-")[0]
            if len(prefix) <= 5:  # Only short prefixes
                if prefix not in patterns:
                    patterns[prefix] = []
                patterns[prefix].append(name)

    return patterns


def main():
    parser = argparse.ArgumentParser(description="List labels in the CID group")
    parser.add_argument("--search", help="Filter labels by name")
    parser.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    parser.add_argument("--limit", type=int, default=100, help="Maximum results")
    parser.add_argument("--analyze", action="store_true", help="Analyze label patterns")

    args = parser.parse_args()

    # Validate inputs
    limit = validate_positive_int(args.limit, "limit")

    # Fetch labels
    labels = list_labels(search=args.search, limit=limit)

    # Output results
    if args.format == "json":
        output = [format_label_for_json(l) for l in labels]
        if args.analyze:
            patterns = analyze_label_patterns(labels)
            print_json({"labels": output, "patterns": patterns})
        else:
            print_json(output)
    else:
        headers = ["Name", "Color", "Description"]
        rows = [format_label_for_table(l) for l in labels]
        max_widths = {0: 40, 2: 50}
        print(f"\nFound {len(labels)} label(s) in cit-iaas/cid:\n")
        print_table(headers, rows, max_widths)

        # Show pattern analysis if requested
        if args.analyze:
            patterns = analyze_label_patterns(labels)
            if patterns:
                print("\n" + "=" * 50)
                print("Label Patterns Detected:")
                print("=" * 50)
                for scope, names in sorted(patterns.items()):
                    if len(names) >= 2:  # Only show patterns with multiple labels
                        print(f"\n{scope}::")
                        for name in sorted(names):
                            print(f"  - {name}")


if __name__ == "__main__":
    main()
