#!/usr/bin/env python3
"""
CheckMK Downtimes Script
Queries CheckMK REST API for active downtimes.

Usage: cmk-downtimes.py [--host HOST] [--group GROUP] [--json]
"""

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cmk_common import CheckMKClient as _BaseClient, resolve_group, KNOWN_HOST_GROUPS


class CheckMKClient(_BaseClient):
    """Extended client with downtime query support."""

    def get_downtimes(self, query=None):
        params = {}
        if query:
            params["query"] = json.dumps(query)
        data = self._get("domain-types/downtime/collections/all", params=params)
        return data.get("value", [])


def parse_downtime(entry):
    ext = entry.get("extensions", {})
    return {
        "id": entry.get("id", ""),
        "host": ext.get("host_name", "N/A"),
        "is_service": ext.get("is_service", "no") == "yes",
        "service": ext.get("service_description", "-"),
        "author": ext.get("author", "N/A"),
        "comment": ext.get("comment", ""),
        "start_time": ext.get("start_time", ""),
        "end_time": ext.get("end_time", ""),
        "recurring": ext.get("recurring", "no"),
    }


def format_dt(ts_str):
    if not ts_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(ts_str)
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return str(ts_str)


def show_downtimes(downtimes, client):
    # Group by host
    by_host = {}
    for d in downtimes:
        host = d["host"]
        if host not in by_host:
            by_host[host] = []
        by_host[host].append(d)

    for host, dts in sorted(by_host.items()):
        svc_count = sum(1 for d in dts if d["is_service"])
        host_count = sum(1 for d in dts if not d["is_service"])
        authors = set(d["author"] for d in dts)
        comments = set(d["comment"] for d in dts if d["comment"])
        start = min(d["start_time"] for d in dts)
        end = max(d["end_time"] for d in dts)

        print(f"🔧 {host}")
        print(f"    Downtimes: {len(dts)} ({host_count} host, {svc_count} service)")
        print(f"    Author:    {', '.join(authors)}")
        print(f"    Comment:   {', '.join(comments) or '(none)'}")
        print(f"    Period:    {format_dt(start)} → {format_dt(end)}")
        print(f"    Link:      {client.host_url(host)}")
        print()

    # Summary
    authors = Counter(d["author"] for d in downtimes)
    print(f"Total: {len(downtimes)} downtime(s) on {len(by_host)} host(s)")
    if len(authors) > 1:
        print("By author:")
        for a, c in authors.most_common():
            print(f"  {a}: {c}")


def main():
    parser = argparse.ArgumentParser(
        description="List active CheckMK downtimes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # All active downtimes
  %(prog)s --host myserver                    # Downtimes for specific host
  %(prog)s --group caas                       # Downtimes for CaaS hosts
  %(prog)s --author i640753                   # Downtimes by specific author
  %(prog)s --json                             # JSON output
        """,
    )
    parser.add_argument("--host", help="Filter by hostname (exact match)")
    parser.add_argument("--group", "-g", help="Filter by host group (name or alias)")
    parser.add_argument("--author", help="Filter by author (partial match, case-insensitive)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    client = CheckMKClient()

    # Build query
    query = None
    if args.host:
        query = {"op": "=", "left": "host_name", "right": args.host}
    elif args.group:
        group = resolve_group(args.group)
        desc = KNOWN_HOST_GROUPS.get(group, group)
        print(f"Host group: {group} ({desc})", file=sys.stderr)
        query = {"op": ">=", "left": "host_groups", "right": group}

    raw = client.get_downtimes(query=query)
    downtimes = [parse_downtime(d) for d in raw]

    # Client-side author filter
    if args.author:
        downtimes = [d for d in downtimes if args.author.lower() in d["author"].lower()]

    if args.json:
        json.dump(downtimes, sys.stdout, indent=2)
        print()
        return

    if not downtimes:
        print("No active downtimes found. ✅")
        return

    show_downtimes(downtimes, client)


if __name__ == "__main__":
    main()
