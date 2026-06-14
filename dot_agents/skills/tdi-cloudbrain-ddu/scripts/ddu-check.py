#!/usr/bin/env python3
"""
DDU Cluster Check Script

Check the health status of a Kubernetes cluster.
Usage: ddu-check.py <cluster-name>
"""
import argparse
import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ddu_client import DDUClient, print_error


def main():
    parser = argparse.ArgumentParser(
        description="Check the health status of a Kubernetes cluster.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ddu-check.py hrzagt5-skynet-dev
"""
    )
    parser.add_argument("cluster_name", help="Name of the cluster to check")
    args = parser.parse_args()

    try:
        client = DDUClient()
        data, status = client.check_cluster(args.cluster_name)

        if status != 200:
            print_error(f"API request failed with status {status}")
            if isinstance(data, dict):
                print_error(data.get("message", str(data)))
            else:
                print_error(str(data))
            return 1

        # Output response (check endpoint typically returns plain text logs)
        if isinstance(data, str):
            print(data)
        else:
            import json
            print(json.dumps(data, indent=2))

        return 0

    except ValueError as e:
        print_error(str(e))
        return 1
    except ConnectionError as e:
        print_error(str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
