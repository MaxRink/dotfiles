#!/usr/bin/env python3
"""
List epics from the CIT-IaaS CID group.

Usage:
    cid-list-epics.py [options]

Options:
    --state STATE         Filter by state: opened (default), closed, all
    --labels LABELS       Filter by comma-separated labels
    --author USERNAME     Filter by author username
    --assignee NAME       Filter by assignee/delivery manager (supports partial name search)
    --search TEXT         Search in title and description
    --country COUNTRIES   Filter by country codes or names (comma-separated)
                          Examples: SK, Slovakia, SK,HU, "Slovakia,Hungary"
    --subgroup NAME       Filter to specific subgroup: nitrogen, dc-devops, gangs, etc.
                          Use "parent" or "cid" for parent group only (no subgroups)
    --updated-after DATE  Only epics updated after this date (ISO format)
    --created-after DATE  Only epics created after this date (ISO format)
    --sort-by FIELD       Sort results by: due_date, created_at, updated_at, title
    --format FORMAT       Output format: table (default), json
    --verbose             Show enhanced output with squad, location, status labels
    --show-hierarchy      Show parent/child epic relationships
    --umbrella-only       Show only umbrella (parent) epics
    --standalone-only     Show only standalone epics (no parent, no children)
    --limit N             Maximum results (default: 50)
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for utils import
sys.path.insert(0, str(Path(__file__).parent))

from utils import get_gitlab_client, get_cid_group, print_table, print_json, print_error
from utils import find_user_by_name, filter_epics_by_assignee
from utils.config import (
    DEFAULT_LIMIT,
    COUNTRY_CODES,
    ENV_LABEL_PREFIXES,
    get_country_code,
    get_country_patterns,
)
from utils.output import format_date, format_labels
from utils.validators import validate_state, validate_positive_int


def parse_countries(country_arg: str) -> list[str]:
    """
    Parse comma-separated country codes/names into validated country codes.

    Args:
        country_arg: Comma-separated country codes or names

    Returns:
        List of validated uppercase country codes

    Raises:
        SystemExit if any country is invalid
    """
    if not country_arg:
        return []

    codes = []
    for part in country_arg.split(","):
        part = part.strip()
        if not part:
            continue
        code = get_country_code(part)
        if code is None:
            valid = ", ".join(f"{c} ({n})" for c, n in sorted(COUNTRY_CODES.items()))
            print_error(f"Unknown country: '{part}'. Valid countries: {valid}")
            sys.exit(1)
        if code not in codes:
            codes.append(code)

    return codes


def filter_by_country(epics: list, country_codes: list[str]) -> list:
    """
    Filter epics by country codes, matching both title patterns and labels.

    Args:
        epics: List of epic objects
        country_codes: List of country codes (e.g., ["SK", "HU"])

    Returns:
        Filtered list of epics
    """
    if not country_codes:
        return epics

    # Build patterns for all requested countries
    title_patterns = []
    label_patterns = []

    for code in country_codes:
        # Add city patterns for title matching
        title_patterns.extend(get_country_patterns(code))
        # Add label patterns (E - IC-SK*, E - SC-SK*, E - HC-SK*)
        for prefix in ENV_LABEL_PREFIXES:
            label_patterns.append(f"{prefix}{code}")

    filtered = []
    for epic in epics:
        title_lower = epic.title.lower()
        labels = getattr(epic, "labels", []) or []

        # Check title patterns
        title_match = any(pattern in title_lower for pattern in title_patterns)

        # Check label patterns (partial match: label starts with pattern)
        label_match = any(
            any(label.startswith(f"E - {pattern}") for pattern in label_patterns)
            for label in labels
        )

        if title_match or label_match:
            filtered.append(epic)

    return filtered


def sort_epics(epics: list, sort_by: str | None) -> list:
    """
    Sort epics by the specified field.

    Args:
        epics: List of epic objects
        sort_by: Field to sort by (due_date, created_at, updated_at, title)

    Returns:
        Sorted list of epics
    """
    if not sort_by:
        return epics

    def get_sort_key(epic):
        if sort_by == "due_date":
            return getattr(epic, "due_date", None) or "9999-99-99"
        elif sort_by == "created_at":
            return getattr(epic, "created_at", None) or ""
        elif sort_by == "updated_at":
            return getattr(epic, "updated_at", None) or ""
        elif sort_by == "title":
            return epic.title.lower()
        return ""

    return sorted(epics, key=get_sort_key)


def extract_label_info(labels: list) -> dict:
    """
    Extract structured info from labels for verbose output.

    Args:
        labels: List of label strings

    Returns:
        Dict with squad, location, status, priority keys
    """
    info = {
        "squad": [],
        "location": [],
        "status": None,
        "priority": None,
    }

    for label in labels:
        if label.startswith("A - ") and "_squad" in label:
            # Extract squad name: "A - CDM_squad" -> "CDM"
            squad_name = label[4:].replace("_squad", "")
            info["squad"].append(squad_name)
        elif label.startswith("E - "):
            # Location label
            info["location"].append(label[4:])  # Remove "E - " prefix
        elif label.startswith("B - epic:::"):
            # Epic status
            info["status"] = label.replace("B - epic:::", "")
        elif label.startswith("D - "):
            # Priority
            info["priority"] = label[4:]  # e.g., "1 - critical"

    return info


def get_hierarchy_info(epics: list) -> dict:
    """
    Analyze epics to determine parent/child relationships.

    Args:
        epics: List of epic objects

    Returns:
        Dict with:
            - parent_iids: Set of IIDs that are parents
            - children_by_parent: Dict mapping parent IID to list of child epics
            - epic_type: Dict mapping IID to 'umbrella', 'child', or 'standalone'
    """
    epic_map = {e.iid: e for e in epics}
    parent_iids = set()
    children_by_parent = {}

    # First pass: identify parent-child relationships
    for e in epics:
        parent_iid = getattr(e, 'parent_iid', None)
        if parent_iid:
            parent_iids.add(parent_iid)
            if parent_iid not in children_by_parent:
                children_by_parent[parent_iid] = []
            children_by_parent[parent_iid].append(e)

    # Second pass: classify each epic
    epic_type = {}
    for e in epics:
        parent_iid = getattr(e, 'parent_iid', None)
        if e.iid in parent_iids:
            epic_type[e.iid] = 'umbrella'
        elif parent_iid:
            epic_type[e.iid] = 'child'
        else:
            epic_type[e.iid] = 'standalone'

    return {
        'parent_iids': parent_iids,
        'children_by_parent': children_by_parent,
        'epic_type': epic_type,
        'epic_map': epic_map,
    }


def list_epics(state="opened", labels=None, author=None, search=None,
               updated_after=None, created_after=None, limit=DEFAULT_LIMIT,
               country_codes=None, sort_by=None, subgroup=None, assignee=None):
    """
    List epics from the CID group.

    Args:
        state: Filter by state (opened, closed, all)
        labels: Comma-separated label names
        author: Author username
        search: Search text
        updated_after: ISO date string
        created_after: ISO date string
        limit: Maximum results
        country_codes: List of country codes for filtering
        sort_by: Field to sort by
        subgroup: Subgroup name to filter (e.g., "nitrogen", "dc-devops", "parent")
        assignee: Assignee name/username (will be resolved and filtered post-fetch)

    Returns:
        list: List of epic objects
    """
    gl = get_gitlab_client()

    # Handle subgroup filtering
    if subgroup:
        subgroup_lower = subgroup.lower()
        if subgroup_lower in ("parent", "cid", "cit-iaas/cid"):
            # Parent group only - no descendants
            group = gl.groups.get("cit-iaas/cid")
            include_descendants = False
        else:
            # Specific subgroup
            subgroup_path = f"cit-iaas/cid/{subgroup_lower}"
            try:
                group = gl.groups.get(subgroup_path)
                include_descendants = True  # Include nested subgroups if any
            except Exception as e:
                # List valid subgroups
                parent = gl.groups.get("cit-iaas/cid")
                valid_subs = [sg.path for sg in parent.subgroups.list(get_all=True)]
                print_error(f"Unknown subgroup: '{subgroup}'. Valid subgroups: {', '.join(valid_subs)}, parent")
                sys.exit(1)
    else:
        group = gl.groups.get("cit-iaas/cid")
        include_descendants = True

    # Build query parameters
    # If filtering by country or assignee, fetch more to allow for post-filtering
    fetch_limit = limit * 3 if (country_codes or assignee) else limit
    params = {
        "include_descendant_groups": include_descendants,
        "per_page": min(fetch_limit, 100),
    }

    if state != "all":
        params["state"] = state

    if labels:
        params["labels"] = labels

    if author:
        params["author_username"] = author

    if search:
        params["search"] = search

    if updated_after:
        params["updated_after"] = updated_after

    if created_after:
        params["created_after"] = created_after

    # Fetch epics
    try:
        # Need to fetch all if filtering by country or assignee (post-fetch filter)
        if country_codes or assignee:
            epics = group.epics.list(**params, get_all=True)
            epics = list(epics)

            # Apply country filter if specified
            if country_codes:
                epics = filter_by_country(epics, country_codes)

            # Apply assignee filter if specified
            if assignee:
                epics = filter_epics_by_assignee(epics, assignee)

        elif limit > 100:
            # Fetch all and slice
            epics = list(group.epics.list(**params, get_all=True))
        else:
            epics = list(group.epics.list(**params, get_all=False))

        # Sort if requested
        if sort_by:
            epics = sort_epics(epics, sort_by)

        return epics[:limit]

    except Exception as e:
        print_error(f"Failed to list epics: {e}")
        sys.exit(1)


def format_epic_for_table(epic, verbose=False, hierarchy_info=None, show_hierarchy=False):
    """Format an epic for table display."""
    # Determine hierarchy indicator
    hierarchy_col = "-"
    if show_hierarchy and hierarchy_info:
        epic_type = hierarchy_info['epic_type'].get(epic.iid, 'standalone')
        parent_iid = getattr(epic, 'parent_iid', None)
        child_count = len(hierarchy_info['children_by_parent'].get(epic.iid, []))

        if epic_type == 'umbrella':
            hierarchy_col = f"📁 {child_count} children"
        elif epic_type == 'child':
            hierarchy_col = f"└─ #{parent_iid}"
        else:
            hierarchy_col = "standalone"

    if verbose:
        labels = getattr(epic, "labels", []) or []
        info = extract_label_info(labels)
        row = [
            epic.iid,
            epic.title[:50] + "..." if len(epic.title) > 50 else epic.title,
            epic.state,
            format_date(getattr(epic, "due_date", None)),
            ", ".join(info["squad"][:2]) or "-",
            ", ".join(info["location"][:2]) or "-",
            info["status"] or "-",
        ]
        if show_hierarchy:
            row.append(hierarchy_col)
        return row
    else:
        row = [
            epic.iid,
            epic.title[:60] + "..." if len(epic.title) > 60 else epic.title,
            epic.state,
            format_date(getattr(epic, "start_date", None)),
            format_date(getattr(epic, "due_date", None)),
        ]
        if show_hierarchy:
            row.append(hierarchy_col)
        else:
            row.append(format_labels(getattr(epic, "labels", []), max_length=30))
        return row


def format_epic_for_json(epic, verbose=False, hierarchy_info=None):
    """Format an epic for JSON output."""
    base = {
        "iid": epic.iid,
        "title": epic.title,
        "state": epic.state,
        "start_date": getattr(epic, "start_date", None),
        "due_date": getattr(epic, "due_date", None),
        "labels": getattr(epic, "labels", []),
        "author": epic.author.get("username") if hasattr(epic, "author") and epic.author else None,
        "created_at": getattr(epic, "created_at", None),
        "updated_at": getattr(epic, "updated_at", None),
        "web_url": getattr(epic, "web_url", None),
        "parent_iid": getattr(epic, "parent_iid", None),
    }

    if hierarchy_info:
        epic_type = hierarchy_info['epic_type'].get(epic.iid, 'standalone')
        base["hierarchy_type"] = epic_type
        if epic_type == 'umbrella':
            base["child_count"] = len(hierarchy_info['children_by_parent'].get(epic.iid, []))
            base["child_iids"] = [c.iid for c in hierarchy_info['children_by_parent'].get(epic.iid, [])]

    if verbose:
        labels = getattr(epic, "labels", []) or []
        info = extract_label_info(labels)
        base["squad"] = info["squad"]
        base["location"] = info["location"]
        base["epic_status"] = info["status"]
        base["priority"] = info["priority"]

    return base


def main():
    parser = argparse.ArgumentParser(description="List epics from the CID group")
    parser.add_argument("--state", default="opened", help="Filter by state: opened, closed, all")
    parser.add_argument("--labels", help="Filter by comma-separated labels")
    parser.add_argument("--author", help="Filter by author username")
    parser.add_argument("--assignee", help="Filter by assignee/delivery manager (supports partial name search)")
    parser.add_argument("--search", help="Search in title and description")
    parser.add_argument("--country", help="Filter by country codes/names (comma-separated): SK, Slovakia, SK,HU")
    parser.add_argument("--subgroup", help="Filter to subgroup: nitrogen, dc-devops, gangs, cit-product-management, or 'parent' for cid only")
    parser.add_argument("--updated-after", help="Only epics updated after this date (ISO format)")
    parser.add_argument("--created-after", help="Only epics created after this date (ISO format)")
    parser.add_argument("--sort-by", choices=["due_date", "created_at", "updated_at", "title"],
                        help="Sort results by field")
    parser.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    parser.add_argument("--verbose", action="store_true",
                        help="Show enhanced output with squad, location, status")
    parser.add_argument("--show-hierarchy", action="store_true",
                        help="Show parent/child epic relationships")
    parser.add_argument("--umbrella-only", action="store_true",
                        help="Show only umbrella (parent) epics that have children")
    parser.add_argument("--standalone-only", action="store_true",
                        help="Show only standalone epics (no parent, no children)")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Maximum results")

    args = parser.parse_args()

    # Validate inputs
    state = validate_state(args.state)
    limit = validate_positive_int(args.limit, "limit")
    country_codes = parse_countries(args.country) if args.country else None

    # Resolve assignee username if provided
    assignee_username = None
    if args.assignee:
        gl = get_gitlab_client()
        group = get_cid_group(gl)
        assignee_username = find_user_by_name(group, args.assignee, interactive=True)
        if not assignee_username:
            # User not found or selection cancelled
            sys.exit(1)
        print(f"Filtering by assignee: @{assignee_username}\n", file=sys.stderr)

    # Fetch epics
    epics = list_epics(
        state=state,
        labels=args.labels,
        author=args.author,
        search=args.search,
        updated_after=args.updated_after,
        created_after=args.created_after,
        limit=limit,
        country_codes=country_codes,
        sort_by=args.sort_by,
        subgroup=args.subgroup,
        assignee=assignee_username,
    )

    # Build hierarchy info if needed
    hierarchy_info = None
    if args.show_hierarchy or args.umbrella_only or args.standalone_only:
        hierarchy_info = get_hierarchy_info(epics)

        # Filter by hierarchy type if requested
        if args.umbrella_only:
            epics = [e for e in epics if hierarchy_info['epic_type'].get(e.iid) == 'umbrella']
        elif args.standalone_only:
            epics = [e for e in epics if hierarchy_info['epic_type'].get(e.iid) == 'standalone']

    # Build output description
    if args.subgroup:
        if args.subgroup.lower() in ("parent", "cid"):
            desc_parts = ["cit-iaas/cid (parent only)"]
        else:
            desc_parts = [f"cit-iaas/cid/{args.subgroup}"]
    else:
        desc_parts = ["cit-iaas/cid (all)"]
    if country_codes:
        country_names = [COUNTRY_CODES[c] for c in country_codes]
        desc_parts.append(f"[{', '.join(country_names)}]")
    if args.umbrella_only:
        desc_parts.append("[umbrella epics only]")
    if args.standalone_only:
        desc_parts.append("[standalone epics only]")

    # Output results
    if args.format == "json":
        print_json([format_epic_for_json(e, args.verbose, hierarchy_info) for e in epics])
    else:
        if args.verbose:
            headers = ["IID", "Title", "State", "Due", "Squad", "Location", "Status"]
            if args.show_hierarchy:
                headers.append("Hierarchy")
            rows = [format_epic_for_table(e, verbose=True, hierarchy_info=hierarchy_info,
                                           show_hierarchy=args.show_hierarchy) for e in epics]
            max_widths = {1: 50, 4: 15, 5: 20, 6: 12}
            if args.show_hierarchy:
                max_widths[7] = 18
        else:
            headers = ["IID", "Title", "State", "Start", "Due"]
            if args.show_hierarchy:
                headers.append("Hierarchy")
            else:
                headers.append("Labels")
            rows = [format_epic_for_table(e, verbose=False, hierarchy_info=hierarchy_info,
                                           show_hierarchy=args.show_hierarchy) for e in epics]
            max_widths = {1: 60, 5: 30}
            if args.show_hierarchy:
                max_widths[5] = 18

        print(f"\nFound {len(epics)} epic(s) in {' '.join(desc_parts)}:\n")
        print_table(headers, rows, max_widths)


if __name__ == "__main__":
    main()
