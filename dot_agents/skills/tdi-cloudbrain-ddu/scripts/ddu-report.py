#!/usr/bin/env python3
"""
DDU Cluster Report Script

Get a detailed report for a Kubernetes cluster.
Usage: ddu-report.py <cluster-name> [--json]
"""
import argparse
import json
import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ddu_client import DDUClient, print_error, format_value


def main():
    parser = argparse.ArgumentParser(
        description="Get a detailed report for a Kubernetes cluster.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ddu-report.py hrzagt5-skynet-dev
  ddu-report.py hrzagt5-skynet-dev --json
"""
    )
    parser.add_argument("cluster_name", help="Name of the cluster")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output raw JSON response")
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

        # Formatted output
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
