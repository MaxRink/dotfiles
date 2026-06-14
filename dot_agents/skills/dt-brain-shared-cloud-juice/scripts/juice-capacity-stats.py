#!/usr/bin/env python3
"""Get capacity statistics from JUICE at cloud, group, or project level."""

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


def show_cloud_stats(data, fmt):
    """Display cloud-level statistics (total vs allocated)."""
    clouds = data.get("clouds", [])
    if fmt == "json":
        print_json(clouds)
        return

    if not clouds:
        print("No cloud statistics found.")
        return

    for cloud in clouds:
        cloud_id = cloud.get("cloud_id", "unknown")
        quotas = cloud.get("quotas", [])
        print(f"\n=== Cloud: {cloud_id} ===")
        rows = []
        for q in quotas:
            rows.append(
                [
                    q.get("quota_group", ""),
                    q.get("quota", ""),
                    str(q.get("total", 0)),
                    str(q.get("allocated", 0)),
                ]
            )
        print_table(["Quota Group", "Quota", "Total", "Allocated"], rows)


def show_group_stats(data, fmt):
    """Display group-level statistics (allowed vs allocated)."""
    vcs = data.get("virtual_clouds", [])
    if fmt == "json":
        print_json(vcs)
        return

    if not vcs:
        print("No group statistics found.")
        return

    for vc in vcs:
        cloud_id = vc.get("cloud_id", "unknown")
        group = vc.get("juice_group", "unknown")
        quotas = vc.get("quotas", [])
        print(f"\n=== Group: {group} | Cloud: {cloud_id} ===")
        rows = []
        for q in quotas:
            rows.append(
                [
                    q.get("quota_group", ""),
                    q.get("quota", ""),
                    str(q.get("allowed", 0)),
                    str(q.get("allocated", 0)),
                ]
            )
        print_table(["Quota Group", "Quota", "Allowed", "Allocated"], rows)


def show_project_stats(data, fmt):
    """Display project-level statistics (used vs allocated)."""
    projects = data.get("projects", [])
    if fmt == "json":
        print_json(projects)
        return

    if not projects:
        print("No project statistics found.")
        return

    for proj in projects:
        name = proj.get("project_name", "unknown")
        cloud_id = proj.get("cloud_id", "unknown")
        group = proj.get("juice_group", "unknown")
        quotas = proj.get("quotas", [])
        print(f"\n=== Project: {name} | Group: {group} | Cloud: {cloud_id} ===")
        rows = []
        for q in quotas:
            rows.append(
                [
                    q.get("quota_group", ""),
                    q.get("quota", ""),
                    str(q.get("allocated", 0)),
                    str(q.get("used", 0)),
                ]
            )
        print_table(["Quota Group", "Quota", "Allocated", "Used"], rows)


def main():
    parser = argparse.ArgumentParser(description="Get JUICE capacity statistics")
    parser.add_argument(
        "level", choices=["cloud", "group", "project"], help="Statistics level"
    )
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
    parser.add_argument("--cloud", help="Filter by cloud name/ID")
    parser.add_argument("--group", help="Filter by juice-group name (admin only)")
    parser.add_argument(
        "--list-all", action="store_true", help="List all entries (admin only)"
    )
    parser.add_argument(
        "--quota",
        choices=["cores", "ram", "gigabytes", "object-megabytes", "floatingips"],
        help="Filter by quota type",
    )
    parser.add_argument(
        "--quota-group",
        choices=["compute", "volume", "network"],
        help="Filter by quota group",
    )
    args = parser.parse_args()
    juice_group = resolve_juice_group(args.juice_group)

    params = {}
    if args.quota:
        params["quota"] = args.quota
    if args.quota_group:
        params["quota-group"] = args.quota_group

    if args.level == "cloud":
        if args.cloud:
            params["cloud_id"] = args.cloud
        data = juice_request(
            "GET", "/v1/stat/cloud", juice_group, args.env, params=params
        )
        show_cloud_stats(data, args.format)

    elif args.level == "group":
        if args.group:
            params["group"] = args.group
        if args.cloud:
            params["cloud_id"] = args.cloud
        if args.list_all:
            params["list_all"] = True
        data = juice_request(
            "GET", "/v1/stat/group", juice_group, args.env, params=params
        )
        show_group_stats(data, args.format)

    elif args.level == "project":
        if args.group:
            params["group"] = args.group
        if args.cloud:
            params["cloud_id"] = args.cloud
        if args.list_all:
            params["list_all"] = True
        data = juice_request(
            "GET", "/v1/stat/project", juice_group, args.env, params=params
        )
        show_project_stats(data, args.format)


if __name__ == "__main__":
    main()
