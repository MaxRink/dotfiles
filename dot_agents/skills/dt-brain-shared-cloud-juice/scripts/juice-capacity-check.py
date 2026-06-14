#!/usr/bin/env python3
"""Check if requested capacity is available in a JUICE-managed cloud."""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from juice_common import juice_request, print_json, JUICE_ENVS, resolve_juice_group


def main():
    parser = argparse.ArgumentParser(
        description="Check capacity availability in a cloud"
    )
    parser.add_argument("cloud_name", help="Cloud name/ID")
    parser.add_argument(
        "--juice-group",
        default=None,
        help="JUICE group for auth scope (default: JUICE_GROUP env var)",
    )
    parser.add_argument(
        "--env",
        default="prod",
        choices=list(JUICE_ENVS.keys()),
        help="JUICE environment (default: prod)",
    )
    parser.add_argument(
        "--format",
        default="table",
        choices=["table", "json"],
        help="Output format (default: table)",
    )
    parser.add_argument("--cores", type=int, help="Requested CPU cores")
    parser.add_argument("--ram", type=int, help="Requested RAM in MB")
    parser.add_argument("--gigabytes", type=int, help="Requested volume storage in GB")
    parser.add_argument("--floatingip", type=int, help="Requested floating IPs")
    args = parser.parse_args()
    juice_group = resolve_juice_group(args.juice_group)

    if not any([args.cores, args.ram, args.gigabytes, args.floatingip]):
        print(
            "Error: Specify at least one resource to check (--cores, --ram, --gigabytes, --floatingip)",
            file=sys.stderr,
        )
        sys.exit(1)

    params = {}
    if args.cores is not None:
        params["cores"] = args.cores
    if args.ram is not None:
        params["ram"] = args.ram
    if args.gigabytes is not None:
        params["gigabytes"] = args.gigabytes
    if args.floatingip is not None:
        params["floatingip"] = args.floatingip

    data = juice_request(
        "GET",
        f"/v1/capacity/{args.cloud_name}/check",
        juice_group,
        args.env,
        params=params,
    )

    if args.format == "json":
        print_json(data)
        return

    print(f"=== Capacity Check: {args.cloud_name} ===\n")
    all_ok = True
    for resource, available in data.items():
        requested = params.get(resource)
        status = "✓ Available" if available else "✗ NOT available"
        if not available:
            all_ok = False
        if requested is not None:
            print(f"  {resource}: {requested:,} — {status}")

    print(
        f"\nOverall: {'All resources available' if all_ok else 'INSUFFICIENT capacity for some resources'}"
    )


if __name__ == "__main__":
    main()
