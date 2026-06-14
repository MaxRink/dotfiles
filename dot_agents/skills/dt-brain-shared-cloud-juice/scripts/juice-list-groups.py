#!/usr/bin/env python3
"""List JUICE groups accessible to the authenticated user."""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from juice_common import (
    juice_request,
    print_table,
    print_json,
    add_common_args,
    resolve_juice_group,
    JUICE_ENVS,
)


def main():
    parser = argparse.ArgumentParser(description="List JUICE groups")
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
    parser.add_argument(
        "--product-type",
        choices=["compute", "caas", "caasbm", "baremetal"],
        help="Filter by product type",
    )
    parser.add_argument(
        "--limit", type=int, default=1000, help="Max results (default: 1000)"
    )
    args = parser.parse_args()
    juice_group = resolve_juice_group(args.juice_group)

    params = {"limit": args.limit}
    if args.product_type:
        params["product_type"] = args.product_type

    data = juice_request(
        "GET", "/v2/juice/groups", juice_group, args.env, params=params
    )
    groups = data.get("data", [])

    if args.format == "json":
        print_json(groups)
        return

    rows = []
    for g in groups:
        rows.append(
            [
                g.get("name", ""),
                g.get("product_type", ""),
                g.get("os_domain", ""),
                g.get("state", ""),
                ", ".join(g.get("tags", [])) if g.get("tags") else "",
                g.get("description", "") or "",
            ]
        )

    print_table(
        ["Name", "Product Type", "OS Domain", "State", "Tags", "Description"], rows
    )
    print(f"\nTotal: {len(rows)} groups")


if __name__ == "__main__":
    main()
