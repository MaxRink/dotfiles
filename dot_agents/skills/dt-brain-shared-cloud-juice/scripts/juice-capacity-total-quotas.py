#!/usr/bin/env python3
"""Get total hypervisor quotas and usage for an OpenStack cloud via JUICE capacity API."""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from juice_common import (
    juice_request,
    print_table,
    print_json,
    JUICE_ENVS,
    resolve_juice_group,
)


def format_number(value):
    """Format a numeric value with thousands separators."""
    if value is None:
        return "—"
    return f"{value:,}"


def main():
    parser = argparse.ArgumentParser(
        description="Get total quotas and usage for a cloud"
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
    parser.add_argument(
        "--compute-type",
        choices=["shared", "shared-local", "dedicated", "dedicated-local"],
        help="Filter by compute type",
    )
    parser.add_argument("--hw-version", help="Filter by hardware version")
    parser.add_argument("--consumer", help="Filter by consumer name")
    parser.add_argument(
        "--show-hosts", action="store_true", help="Show per-host details"
    )
    args = parser.parse_args()
    juice_group = resolve_juice_group(args.juice_group)

    params = {}
    if args.compute_type:
        params["compute_type"] = args.compute_type
    if args.hw_version:
        params["hw_version"] = args.hw_version
    if args.consumer:
        params["consumer"] = args.consumer

    data = juice_request(
        "GET",
        f"/v1/capacity/{args.cloud_name}/total-quotas",
        juice_group,
        args.env,
        params=params,
        timeout=120,
    )

    if args.format == "json":
        print_json(data)
        return

    # Total quotas summary
    tq = data.get("total_quotas", {})
    tu = data.get("total_usage", {})

    print(f"=== Cloud: {args.cloud_name} — Capacity Summary ===\n")

    # Compute capacity table
    headers = ["Resource", "Total", "Used", "Available"]
    rows = []

    # vCPU
    total_vcpu = tq.get("total_vcpu", 0) or 0
    used_vcpu = tu.get("used_vcpu_total", 0) or 0
    rows.append(
        [
            "vCPU (total)",
            format_number(total_vcpu),
            format_number(used_vcpu),
            format_number(total_vcpu - used_vcpu),
        ]
    )

    for variant in ["shared", "shared_local", "dedicated", "dedicated_local"]:
        total = tq.get(f"total_vcpu_{variant}", 0) or 0
        used = tu.get(f"used_vcpu_{variant}", 0) or 0
        if total > 0 or used > 0:
            label = variant.replace("_", "-")
            rows.append(
                [
                    f"  vCPU ({label})",
                    format_number(total),
                    format_number(used),
                    format_number(total - used),
                ]
            )

    # RAM
    total_ram = tq.get("total_ram_gb", 0) or 0
    used_ram = tu.get("used_ram_gb_total", 0) or 0
    rows.append(
        [
            "RAM GB (total)",
            format_number(total_ram),
            format_number(used_ram),
            format_number(total_ram - used_ram),
        ]
    )

    for variant in ["shared", "shared_local", "dedicated", "dedicated_local"]:
        total = tq.get(f"total_ram_gb_{variant}", 0) or 0
        used = tu.get(f"used_ram_gb_{variant}", 0) or 0
        if total > 0 or used > 0:
            label = variant.replace("_", "-")
            rows.append(
                [
                    f"  RAM GB ({label})",
                    format_number(total),
                    format_number(used),
                    format_number(total - used),
                ]
            )

    # Local Disk
    total_disk = tq.get("total_local_disk_gb", 0) or 0
    used_disk = tu.get("used_local_disk_gb_total", 0) or 0
    rows.append(
        [
            "Local Disk GB (total)",
            format_number(total_disk),
            format_number(used_disk),
            format_number(total_disk - used_disk),
        ]
    )

    for variant in ["shared", "dedicated"]:
        total = tq.get(f"total_local_disk_gb_{variant}", 0) or 0
        used = tu.get(f"used_local_disk_gb_{variant}", 0) or 0
        if total > 0 or used > 0:
            rows.append(
                [
                    f"  Local Disk GB ({variant})",
                    format_number(total),
                    format_number(used),
                    format_number(total - used),
                ]
            )

    print_table(headers, rows)

    # Host counts
    print(f"\n--- Hosts ---")
    print(f"Total: {tq.get('hosts_total', '—')}")
    for htype in ["shared", "shared_local", "dedicated", "dedicated_local", "unknown"]:
        count = tq.get(f"hosts_{htype}", 0)
        if count:
            print(f"  {htype.replace('_', '-')}: {count}")

    # Per-host details
    if args.show_hosts:
        hosts = data.get("host_list", [])
        if hosts:
            print(f"\n--- Host Details ({len(hosts)} hosts) ---")
            host_headers = [
                "Host",
                "Compute Type",
                "HW Version",
                "AZ",
                "pCPU",
                "vCPU",
                "vCPU Used",
                "RAM MB",
                "RAM Used",
                "Disk GB",
                "Disk Used",
            ]
            host_rows = []
            for h in hosts:
                host_rows.append(
                    [
                        h.get("host", ""),
                        h.get("compute_type", ""),
                        h.get("hw_version", ""),
                        h.get("availability_zone", ""),
                        str(h.get("pcpus", "")),
                        str(h.get("vcpus", "")),
                        str(h.get("vcpus_used", "")),
                        str(h.get("ram_mb", "")),
                        str(h.get("ram_mb_used", "")),
                        str(h.get("local_disk_gb", "")),
                        str(h.get("local_disk_gb_used", "")),
                    ]
                )
            print_table(host_headers, host_rows)


if __name__ == "__main__":
    main()
