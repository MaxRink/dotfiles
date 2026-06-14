#!/usr/bin/env python3
"""
List issues from the CIT-IaaS CID group.

Usage:
    cid-list-issues.py [options]

Options:
    --state STATE         Filter by state: opened (default), closed, all
    --labels LABELS       Filter by comma-separated labels
    --squad NAME          Filter by squad shorthand (e.g., CaaS, CDM, DC, Networks)
    --assignee NAME       Filter by assignee (supports partial name search)
    --author USERNAME     Filter by author username
    --search TEXT         Search in title and description
    --country COUNTRIES   Filter by country codes or names (comma-separated)
    --subgroup NAME       Filter to specific subgroup: nitrogen, dc-devops, gangs, etc.
    --updated-after DATE  Only issues updated after this date (ISO format)
    --created-after DATE  Only issues created after this date (ISO format)
    --sort-by FIELD       Sort results by: due_date, created_at, updated_at, title
    --format FORMAT       Output format: table (default), json
    --verbose             Show enhanced output with squad, location columns
    --limit N             Maximum results (default: 50)
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for utils import
sys.path.insert(0, str(Path(__file__).parent))

from utils import get_gitlab_client, get_cid_group, print_table, print_json, print_error
from utils import find_user_by_name
from utils.config import (
    DEFAULT_LIMIT,
    COUNTRY_CODES,
    ENV_LABEL_PREFIXES,
    VALID_SQUAD_LABELS,
    get_country_code,
    get_country_patterns,
)
from utils.output import format_date, format_labels
from utils.validators import validate_state, validate_positive_int


def resolve_squad_label(squad_name: str) -> str:
    """
    Resolve a squad shorthand to the full label.

    Args:
        squad_name: Squad shorthand (e.g., "CaaS", "CDM", "DC")

    Returns:
        Full squad label (e.g., "A - CaaS_squad")

    Raises:
        SystemExit if squad name is invalid
    """
    # Try exact match first
    full_label = f"A - {squad_name}_squad"
    if full_label in VALID_SQUAD_LABELS:
        return full_label

    # Try case-insensitive match
    for label in VALID_SQUAD_LABELS:
        label_name = label.replace("A - ", "").replace("_squad", "")
        if label_name.lower() == squad_name.lower():
            return label

    valid = ", ".join(
        label.replace("A - ", "").replace("_squad", "")
        for label in sorted(VALID_SQUAD_LABELS.keys())
    )
    print_error(f"Unknown squad: '{squad_name}'. Valid squads: {valid}")
    sys.exit(1)


def parse_countries(country_arg: str) -> list[str]:
    """Parse comma-separated country codes/names into validated country codes."""
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


def filter_by_country(issues: list, country_codes: list[str]) -> list:
    """
    Filter issues by country codes, matching title patterns and labels.

    Args:
        issues: List of issue dicts
        country_codes: List of country codes (e.g., ["SK", "HU"])

    Returns:
        Filtered list of issues
    """
    if not country_codes:
        return issues

    title_patterns = []
    label_patterns = []

    for code in country_codes:
        title_patterns.extend(get_country_patterns(code))
        for prefix in ENV_LABEL_PREFIXES:
            label_patterns.append(f"{prefix}{code}")

    filtered = []
    for issue in issues:
        title_lower = issue["title"].lower()
        labels = issue.get("labels", []) or []

        title_match = any(pattern in title_lower for pattern in title_patterns)
        label_match = any(
            any(label.startswith(f"E - {pattern}") for pattern in label_patterns)
            for label in labels
        )

        if title_match or label_match:
            filtered.append(issue)

    return filtered


def extract_label_info(labels: list) -> dict:
    """Extract structured info from labels for verbose output."""
    info = {
        "squad": [],
        "location": [],
        "priority": None,
    }

    for label in labels:
        if label.startswith("A - ") and "_squad" in label:
            squad_name = label[4:].replace("_squad", "")
            info["squad"].append(squad_name)
        elif label.startswith("E - "):
            info["location"].append(label[4:])
        elif label.startswith("D - "):
            info["priority"] = label[4:]

    return info


def list_issues(state="opened", labels=None, author=None, search=None,
                updated_after=None, created_after=None, limit=DEFAULT_LIMIT,
                country_codes=None, sort_by=None, subgroup=None,
                assignee_username=None):
    """
    List issues from the CID group.

    Returns:
        list: List of issue dicts
    """
    gl = get_gitlab_client()

    # Handle subgroup filtering
    if subgroup:
        subgroup_lower = subgroup.lower()
        if subgroup_lower in ("parent", "cid", "cit-iaas/cid"):
            group = gl.groups.get("cit-iaas/cid")
            include_subgroups = False
        else:
            subgroup_path = f"cit-iaas/cid/{subgroup_lower}"
            try:
                group = gl.groups.get(subgroup_path)
                include_subgroups = True
            except Exception as e:
                parent = gl.groups.get("cit-iaas/cid")
                valid_subs = [sg.path for sg in parent.subgroups.list(get_all=True)]
                print_error(f"Unknown subgroup: '{subgroup}'. Valid subgroups: {', '.join(valid_subs)}, parent")
                sys.exit(1)
    else:
        group = gl.groups.get("cit-iaas/cid")
        include_subgroups = True

    # Build query parameters
    fetch_limit = limit * 3 if country_codes else limit
    params = {
        "include_subgroups": include_subgroups,
        "per_page": min(fetch_limit, 100),
    }

    if state != "all":
        params["state"] = state
    if labels:
        params["labels"] = labels
    if author:
        params["author_username"] = author
    if assignee_username:
        params["assignee_username"] = assignee_username
    if search:
        params["search"] = search
    if updated_after:
        params["updated_after"] = updated_after
    if created_after:
        params["created_after"] = created_after

    try:
        if country_codes or limit > 100:
            issues_raw = list(group.issues.list(**params, get_all=True))
        else:
            issues_raw = list(group.issues.list(**params, get_all=False))

        # Convert to dicts
        results = []
        for issue in issues_raw:
            ref = getattr(issue, "references", {})
            if isinstance(ref, dict):
                full_ref = ref.get("full", "")
            else:
                full_ref = str(ref)
            project = full_ref.rsplit("#", 1)[0] if "#" in full_ref else ""

            assignees = getattr(issue, "assignees", []) or []
            assignee_names = [a["username"] for a in assignees if isinstance(a, dict)] if assignees else []

            results.append({
                "iid": issue.iid,
                "project": project,
                "title": issue.title,
                "state": issue.state,
                "assignees": assignee_names,
                "labels": getattr(issue, "labels", []),
                "due_date": getattr(issue, "due_date", None),
                "created_at": getattr(issue, "created_at", None),
                "updated_at": getattr(issue, "updated_at", None),
                "web_url": getattr(issue, "web_url", None),
            })

        # Apply country filter (post-fetch)
        if country_codes:
            results = filter_by_country(results, country_codes)

        # Sort if requested
        if sort_by:
            def sort_key(i):
                if sort_by == "due_date":
                    return i.get("due_date") or "9999-99-99"
                elif sort_by == "created_at":
                    return i.get("created_at") or ""
                elif sort_by == "updated_at":
                    return i.get("updated_at") or ""
                elif sort_by == "title":
                    return i["title"].lower()
                return ""
            results = sorted(results, key=sort_key)

        return results[:limit]

    except Exception as e:
        print_error(f"Failed to list issues: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="List issues from the CID group")
    parser.add_argument("--state", default="opened", help="Filter by state: opened, closed, all")
    parser.add_argument("--labels", help="Filter by comma-separated labels")
    parser.add_argument("--squad", help="Filter by squad shorthand (e.g., CaaS, CDM, DC, Networks)")
    parser.add_argument("--assignee", help="Filter by assignee (supports partial name search)")
    parser.add_argument("--author", help="Filter by author username")
    parser.add_argument("--search", help="Search in title and description")
    parser.add_argument("--country", help="Filter by country codes/names (comma-separated)")
    parser.add_argument("--subgroup", help="Filter to subgroup: nitrogen, dc-devops, gangs, or 'parent' for cid only")
    parser.add_argument("--updated-after", help="Only issues updated after this date (ISO format)")
    parser.add_argument("--created-after", help="Only issues created after this date (ISO format)")
    parser.add_argument("--sort-by", choices=["due_date", "created_at", "updated_at", "title"],
                        help="Sort results by field")
    parser.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    parser.add_argument("--verbose", action="store_true",
                        help="Show enhanced output with squad, location columns")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Maximum results")

    args = parser.parse_args()

    # Validate inputs
    state = validate_state(args.state)
    limit = validate_positive_int(args.limit, "limit")
    country_codes = parse_countries(args.country) if args.country else None

    # Resolve squad shorthand to label
    labels = args.labels
    if args.squad:
        squad_label = resolve_squad_label(args.squad)
        labels = f"{labels},{squad_label}" if labels else squad_label

    # Resolve assignee username if provided
    assignee_username = None
    if args.assignee:
        gl = get_gitlab_client()
        group = get_cid_group(gl)
        assignee_username = find_user_by_name(group, args.assignee, interactive=True)
        if not assignee_username:
            sys.exit(1)
        print(f"Filtering by assignee: @{assignee_username}\n", file=sys.stderr)

    # Fetch issues
    issues = list_issues(
        state=state,
        labels=labels,
        author=args.author,
        search=args.search,
        updated_after=args.updated_after,
        created_after=args.created_after,
        limit=limit,
        country_codes=country_codes,
        sort_by=args.sort_by,
        subgroup=args.subgroup,
        assignee_username=assignee_username,
    )

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

    # Output results
    if args.format == "json":
        if args.verbose:
            for issue in issues:
                info = extract_label_info(issue.get("labels", []))
                issue["squad"] = info["squad"]
                issue["location"] = info["location"]
                issue["priority"] = info["priority"]
        print_json(issues)
    else:
        print(f"\nFound {len(issues)} issue(s) in {' '.join(desc_parts)}:\n")

        if args.verbose:
            headers = ["IID", "Project", "Title", "State", "Assignee", "Squad", "Due"]
            rows = []
            for i in issues:
                info = extract_label_info(i.get("labels", []))
                rows.append([
                    i["iid"],
                    i["project"].replace("cit-iaas/cid/", ""),
                    i["title"],
                    i["state"],
                    ", ".join(i["assignees"][:2]) if i["assignees"] else "-",
                    ", ".join(info["squad"][:2]) or "-",
                    format_date(i["due_date"]),
                ])
            print_table(headers, rows, max_widths={1: 30, 2: 50, 4: 22, 5: 15})
        else:
            headers = ["IID", "Project", "Title", "State", "Assignee", "Due"]
            rows = []
            for i in issues:
                rows.append([
                    i["iid"],
                    i["project"].replace("cit-iaas/cid/", ""),
                    i["title"],
                    i["state"],
                    ", ".join(i["assignees"][:2]) if i["assignees"] else "-",
                    format_date(i["due_date"]),
                ])
            print_table(headers, rows, max_widths={1: 30, 2: 55, 4: 22})


if __name__ == "__main__":
    main()
