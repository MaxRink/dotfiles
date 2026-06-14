#!/usr/bin/env python3
"""
DDU All Clusters Report Script

Get a report for all Kubernetes clusters.
Usage: ddu-report-all.py [--json] [--filter FIELD=VALUE] [--count]
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ddu_client import DDUClient, print_error, format_cluster

FILTER_FIELDS = ["name", "dc", "group", "juice_group", "owner", "version", "parent", "product_type", "type"]


def extract_clusters(data) -> list:
    """Extract cluster list from API response."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("clusters", data.get("data", [data]))
    return []


def match_filter(cluster: dict, field: str, pattern: str) -> bool:
    """Check if cluster matches filter (case-insensitive regex)."""
    # Try different key formats
    value = cluster.get(field) or cluster.get(field.upper()) or cluster.get(field.lower())
    if value is None:
        return False
    return bool(re.search(pattern, str(value), re.IGNORECASE))


def main():
    parser = argparse.ArgumentParser(
        description="Get a report for all Kubernetes clusters.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Filter fields: {', '.join(FILTER_FIELDS)}

Examples:
  ddu-report-all.py
  ddu-report-all.py --json
  ddu-report-all.py --filter name=tupl
  ddu-report-all.py --filter group=TDI --filter dc=atgraf
  ddu-report-all.py --filter version=33.1 --count
"""
    )
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output raw JSON response")
    parser.add_argument("--filter", "-f", action="append", dest="filters",
                        metavar="FIELD=PATTERN",
                        help="Filter clusters (regex, case-insensitive). Can be used multiple times.")
    parser.add_argument("--count", "-c", action="store_true",
                        help="Only output count of matching clusters")
    args = parser.parse_args()

    # Parse filters
    filters = {}
    if args.filters:
        for f in args.filters:
            if "=" not in f:
                print_error(f"Invalid filter format: {f}. Use FIELD=PATTERN")
                return 1
            field, pattern = f.split("=", 1)
            if field.lower() not in FILTER_FIELDS:
                print_error(f"Unknown filter field: {field}")
                print_error(f"Available fields: {', '.join(FILTER_FIELDS)}")
                return 1
            filters[field.lower()] = pattern

    try:
        client = DDUClient()
        data, status = client.get_all_reports()

        if status != 200:
            print_error(f"API request failed with status {status}")
            if isinstance(data, dict):
                print_error(data.get("message", str(data)))
            else:
                print_error(str(data))
            return 1

        clusters = extract_clusters(data)

        # Apply filters
        if filters:
            filtered = []
            for cluster in clusters:
                if all(match_filter(cluster, field, pattern) for field, pattern in filters.items()):
                    filtered.append(cluster)
            clusters = filtered

        # Count only
        if args.count:
            print(len(clusters))
            return 0

        # JSON output
        if args.json_output:
            print(json.dumps(clusters, indent=2))
            return 0

        # Formatted output
        print("All Clusters Report")
        print("=" * 60)
        print()
        print(f"Total Clusters: {len(clusters)}")
        if filters:
            print(f"Filters: {', '.join(f'{k}={v}' for k, v in filters.items())}")
        print()

        for cluster in clusters:
            print(format_cluster(cluster))

        return 0

    except ValueError as e:
        print_error(str(e))
        return 1
    except ConnectionError as e:
        print_error(str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
