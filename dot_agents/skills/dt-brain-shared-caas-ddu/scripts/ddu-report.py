#!/usr/bin/env python3
"""
DDU Cluster Report Script

Get a detailed report for a Kubernetes cluster.
Usage: ddu-report.py <cluster-name> [--json] [--field FIELD ...]
"""
import argparse
import json
import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ddu_client import DDUClient, print_error, format_value


def extract_field(data, field_name: str):
    """Extract a field from DDU report data (case-insensitive, supports nested CC_JSON fields)."""
    # DDU returns a list with one dict per cluster
    record = data[0] if isinstance(data, list) and data else data
    if not isinstance(record, dict):
        return None

    # Direct top-level match (case-insensitive)
    for key, value in record.items():
        if key.lower() == field_name.lower():
            return value

    # Check inside CC_JSON if present (parsed cluster config)
    cc_json_raw = record.get("CC_JSON")
    if cc_json_raw:
        cc = cc_json_raw if isinstance(cc_json_raw, dict) else None
        if cc is None:
            try:
                cc = json.loads(cc_json_raw)
            except (json.JSONDecodeError, TypeError):
                cc = None
        if cc:
            for key, value in cc.items():
                if key.lower() == field_name.lower():
                    return value

    return None


def main():
    parser = argparse.ArgumentParser(
        description="Get a detailed report for a Kubernetes cluster.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ddu-report.py hrzagt5-skynet-dev
  ddu-report.py hrzagt5-skynet-dev --json
  ddu-report.py hrzagt5-skynet-dev --field owner
  ddu-report.py hrzagt5-skynet-dev --field owner version dc
"""
    )
    parser.add_argument("cluster_name", help="Name of the cluster")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output raw JSON response")
    parser.add_argument("--field", nargs="+", dest="fields", metavar="FIELD",
                        help="Extract specific field(s) from the report "
                             "(e.g., owner, version, dc, juice_group)")
    args = parser.parse_args()

    try:
        client = DDUClient()
        data, status = client.get_report(args.cluster_name)

        if status != 200:
            print_error(f"API request failed with status {status}")
            if isinstance(data, dict):
                print_error(data.get("message", str(data)))
            else:
                print_error(str(data))
            return 1

        # JSON output
        if args.json_output:
            print(json.dumps(data, indent=2))
            return 0

        # Field extraction mode
        if args.fields:
            for field in args.fields:
                value = extract_field(data, field)
                if value is None:
                    print(f"{field}: (not found)")
                elif isinstance(value, (dict, list)):
                    print(f"{field}: {json.dumps(value, indent=2)}")
                else:
                    print(f"{field}: {value}")
            return 0

        # Full formatted output
        print("Cluster Report")
        print("=" * 60)
        print(f"Cluster: {args.cluster_name}")
        print()
        print(format_value(data))

        return 0

    except ValueError as e:
        print_error(str(e))
        return 1
    except ConnectionError as e:
        print_error(str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
