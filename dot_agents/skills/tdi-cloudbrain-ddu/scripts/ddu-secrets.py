#!/usr/bin/env python3
"""
DDU Cluster Secrets Script

Retrieve passwords and secrets for a Kubernetes cluster.
Usage: ddu-secrets.py <cluster-name> [--json] [--field FIELD]
"""
import argparse
import json
import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ddu_client import DDUClient, print_error, format_value

AVAILABLE_FIELDS = [
    "GRAFANA_ADMIN_PASSWORD",
    "PROMETHEUS_PASSWORD",
    "AUTOMATION_KUBECONFIG",
    "CUSTOMER_KUBECONFIG",
    "OIDC_KUBECONFIG",
    "OPENRC",
    "CLUSTER_NAME",
    "PARENT"
]


def main():
    parser = argparse.ArgumentParser(
        description="Retrieve passwords and secrets for a Kubernetes cluster.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available fields:
  {chr(10).join(f'  {f}' for f in AVAILABLE_FIELDS)}

Examples:
  ddu-secrets.py hrzagt5-skynet-dev
  ddu-secrets.py hrzagt5-skynet-dev --json
  ddu-secrets.py hrzagt5-skynet-dev --field GRAFANA_ADMIN_PASSWORD
  ddu-secrets.py hrzagt5-skynet-dev -f PROMETHEUS_PASSWORD
"""
    )
    parser.add_argument("cluster_name", help="Name of the cluster")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output raw JSON response")
    parser.add_argument("--field", "-f", help="Extract a specific field value")
    args = parser.parse_args()

    try:
        client = DDUClient()
        data, status = client.get_secrets(args.cluster_name)

        if status != 200:
            print_error(f"API request failed with status {status}")
            if isinstance(data, dict):
                print_error(data.get("message", str(data)))
            else:
                print_error(str(data))
            return 1

        # Extract specific field
        if args.field:
            if not isinstance(data, dict):
                print_error("Response is not a JSON object")
                return 1

            value = data.get(args.field)
            if value is None:
                print_error(f'Field "{args.field}" not found')
                print_error(f"Available fields: {', '.join(data.keys())}")
                return 1
            print(value)
            return 0

        # JSON output
        if args.json_output:
            print(json.dumps(data, indent=2))
            return 0

        # Formatted output
        print("Cluster Secrets")
        print("=" * 60)
        print(f"Cluster: {args.cluster_name}")
        print()
        print("WARNING: These are sensitive credentials - handle with care!")
        print()

        if isinstance(data, dict):
            print(format_value(data))
        else:
            print(data)

        return 0

    except ValueError as e:
        print_error(str(e))
        return 1
    except ConnectionError as e:
        print_error(str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
