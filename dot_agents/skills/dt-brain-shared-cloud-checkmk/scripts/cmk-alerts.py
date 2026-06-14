#!/usr/bin/env python3
"""
CheckMK Active Alerts Script
Queries CheckMK REST API for active host and service problems.

Usage: cmk-alerts.py [--group GROUP] [--host PATTERN] [--service PATTERN] [--state STATE] [--hosts-only|--services-only] [--summary] [--json]
"""

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cmk_common import CheckMKClient as _BaseClient, resolve_group, KNOWN_HOST_GROUPS, HOST_GROUP_ALIASES


class CheckMKClient(_BaseClient):
    """Extended client with problem query support."""

    def _build_query(self, group=None, group_column="host_groups"):
        """Build Livestatus query for problems, optionally filtered by host group."""
        problem_filter = {"op": "!=", "left": "state", "right": "0"}
        if not group:
            return json.dumps(problem_filter)
        group_filter = {"op": ">=", "left": group_column, "right": group}
        return json.dumps({"op": "and", "expr": [problem_filter, group_filter]})

    def get_service_problems(self, group=None, columns=None):
        """Get services in non-OK state, optionally filtered by host group."""
        if columns is None:
            columns = [
                "host_name", "description", "state", "last_state_change",
                "plugin_output", "acknowledged", "scheduled_downtime_depth",
                "host_groups",
            ]
        params = {
            "columns": columns,
            "query": self._build_query(group, group_column="host_groups"),
        }
        data = self._get("domain-types/service/collections/all", params=params)
        return data.get("value", [])

    def get_host_problems(self, group=None, columns=None):
        """Get hosts in non-UP state, optionally filtered by host group."""
        if columns is None:
            columns = [
                "name", "state", "last_state_change",
                "plugin_output", "acknowledged", "scheduled_downtime_depth",
                "groups",
            ]
        params = {
            "columns": columns,
            "query": self._build_query(group, group_column="groups"),
        }
        data = self._get("domain-types/host/collections/all", params=params)
        return data.get("value", [])


# --- State mappings ---

HOST_STATES = {0: "UP", 1: "DOWN", 2: "UNREACHABLE"}
SERVICE_STATES = {0: "OK", 1: "WARN", 2: "CRIT", 3: "UNKNOWN"}

STATE_ICONS = {
    "CRIT": "🔴", "DOWN": "🔴",
    "WARN": "🟡", "UNREACHABLE": "🟡",
    "UNKNOWN": "🟣",
    "OK": "🟢", "UP": "🟢",
}


def format_timestamp(ts):
    """Format a Unix timestamp to human-readable."""
    if not ts:
        return "N/A"
    from datetime import datetime, timezone
    try:
        dt = datetime.fromtimestamp(float(ts), tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except (ValueError, TypeError, OSError):
        return str(ts)


def parse_service(entry):
    """Parse a service entry from API response."""
    ext = entry.get("extensions", {})
    return {
        "type": "service",
        "host": ext.get("host_name", entry.get("id", "N/A")),
        "service": ext.get("description", "N/A"),
        "state": SERVICE_STATES.get(ext.get("state", -1), "UNKNOWN"),
        "state_num": ext.get("state", -1),
        "output": ext.get("plugin_output", ""),
        "since": format_timestamp(ext.get("last_state_change")),
        "acknowledged": bool(ext.get("acknowledged", 0)),
        "in_downtime": ext.get("scheduled_downtime_depth", 0) > 0,
        "groups": ext.get("host_groups", []),
    }


def parse_host(entry):
    """Parse a host entry from API response."""
    ext = entry.get("extensions", {})
    return {
        "type": "host",
        "host": ext.get("name", entry.get("id", "N/A")),
        "service": "-",
        "state": HOST_STATES.get(ext.get("state", -1), "UNKNOWN"),
        "state_num": ext.get("state", -1),
        "output": ext.get("plugin_output", ""),
        "since": format_timestamp(ext.get("last_state_change")),
        "acknowledged": bool(ext.get("acknowledged", 0)),
        "in_downtime": ext.get("scheduled_downtime_depth", 0) > 0,
        "groups": ext.get("groups", []),
    }


def filter_problems(problems, host_filter=None, service_filter=None, state_filter=None, hide_ack=False, hide_downtime=False):
    """Apply filters to parsed problems."""
    result = []
    for p in problems:
        if host_filter and host_filter.lower() not in p["host"].lower():
            continue
        if service_filter and p["type"] == "service" and service_filter.lower() not in p["service"].lower():
            continue
        if state_filter and p["state"] not in state_filter:
            continue
        if hide_ack and p["acknowledged"]:
            continue
        if hide_downtime and p["in_downtime"]:
            continue
        result.append(p)
    return result


def extract_site(hostname):
    """Extract site prefix from hostname (e.g., ic-mkskof2-CAAS-BM-... → ic-mkskof2)."""
    parts = hostname.split("-")
    if len(parts) >= 2:
        return f"{parts[0]}-{parts[1]}"
    return hostname


def host_url(hostname):
    """Build CheckMK host URL."""
    base = os.environ.get("CHECKMK_URL", "")
    site = os.environ.get("CHECKMK_SITE", "")
    return f"{base}/{site}/check_mk/view.py?view_name=host&host={hostname}"


def show_problems(problems, limit=100, links=False):
    """Display problems in table format."""
    for p in problems[:limit]:
        icon = STATE_ICONS.get(p["state"], "⚪")
        ack = " ✅ACK" if p["acknowledged"] else ""
        dt = " 🔧DT" if p["in_downtime"] else ""
        type_label = "HOST" if p["type"] == "host" else "SVC"

        print(f"{icon} [{p['state']}] [{type_label}] {p['host']}")
        if p["type"] == "service":
            print(f"    Service: {p['service']}")
        output = p["output"][:120]
        if output:
            print(f"    Output:  {output}{'...' if len(p['output']) > 120 else ''}")
        print(f"    Since:   {p['since']}{ack}{dt}")
        if links:
            print(f"    Link:    {host_url(p['host'])}")
        print()

    if len(problems) > limit:
        print(f"... and {len(problems) - limit} more (use --json for full list)")


def show_by_site(problems):
    """Display breakdown grouped by site prefix."""
    sites = {}
    for p in problems:
        site = extract_site(p["host"])
        if site not in sites:
            sites[site] = {"total": 0, "CRIT": 0, "DOWN": 0, "WARN": 0, "UNKNOWN": 0, "dt": 0, "ack": 0}
        sites[site]["total"] += 1
        sites[site][p["state"]] = sites[site].get(p["state"], 0) + 1
        if p["in_downtime"]:
            sites[site]["dt"] += 1
        if p["acknowledged"]:
            sites[site]["ack"] += 1

    # Sort by total descending
    sorted_sites = sorted(sites.items(), key=lambda x: x[1]["total"], reverse=True)

    # Table header
    hdr = f"{'Site':<25} {'Total':>6} {'CRIT':>6} {'DOWN':>6} {'WARN':>6} {'UNKN':>6} {'In DT':>6} {'Unhdl':>6}"
    print(hdr)
    print("=" * len(hdr))
    for site, s in sorted_sites:
        unhandled = s["total"] - s["dt"] - s["ack"]
        print(f"{site:<25} {s['total']:>6} {s['CRIT']:>6} {s['DOWN']:>6} {s['WARN']:>6} {s['UNKNOWN']:>6} {s['dt']:>6} {unhandled:>6}")


def show_by_host(problems):
    """Display breakdown grouped by host."""
    hosts = {}
    for p in problems:
        h = p["host"]
        if h not in hosts:
            hosts[h] = {"total": 0, "CRIT": 0, "DOWN": 0, "WARN": 0, "UNKNOWN": 0, "dt": 0}
        hosts[h]["total"] += 1
        hosts[h][p["state"]] = hosts[h].get(p["state"], 0) + 1
        if p["in_downtime"]:
            hosts[h]["dt"] += 1

    sorted_hosts = sorted(hosts.items(), key=lambda x: x[1]["total"], reverse=True)

    hdr = f"{'Host':<55} {'Total':>5} {'CRIT':>5} {'WARN':>5} {'UNKN':>5} {'DT':>5}"
    print(hdr)
    print("=" * len(hdr))
    for host, s in sorted_hosts[:50]:
        print(f"{host:<55} {s['total']:>5} {s['CRIT']:>5} {s['WARN']:>5} {s['UNKNOWN']:>5} {s['dt']:>5}")
    if len(sorted_hosts) > 50:
        print(f"... and {len(sorted_hosts) - 50} more hosts")


def show_summary(problems):
    """Display summary grouped by state and type."""
    state_counts = Counter()
    host_counts = Counter()
    service_counts = Counter()
    ack_count = 0
    dt_count = 0

    for p in problems:
        state_counts[p["state"]] += 1
        if p["type"] == "host":
            host_counts[p["host"]] += 1
        else:
            service_counts[p["service"]] += 1
        if p["acknowledged"]:
            ack_count += 1
        if p["in_downtime"]:
            dt_count += 1

    print("BY STATE")
    print("=" * 50)
    for state in ["CRIT", "DOWN", "WARN", "UNREACHABLE", "UNKNOWN"]:
        if state_counts[state]:
            icon = STATE_ICONS.get(state, "⚪")
            print(f"  {icon} {state}: {state_counts[state]}")

    if ack_count or dt_count:
        print()
        print(f"  Acknowledged: {ack_count}")
        print(f"  In downtime:  {dt_count}")

    if service_counts:
        print()
        print("TOP SERVICES (by occurrences)")
        print("=" * 50)
        for svc, count in service_counts.most_common(15):
            print(f"  {svc}: {count}")

    if host_counts:
        print()
        print("HOSTS WITH PROBLEMS")
        print("=" * 50)
        for host, count in host_counts.most_common(15):
            print(f"  {host}: {count} problem(s)")


def main():
    parser = argparse.ArgumentParser(
        description="List active CheckMK problems (hosts and services)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Host Groups:
  caas-bm          CaaS bare-metal servers        (alias: caas)
  openstack-infra  IaaS / OpenStack infrastructure (alias: iaas, openstack)
  staas            Storage as a Service            (alias: storage)
  server-hw        Server hardware (IMM/ILO)       (alias: hw)
  network          Network devices                 (alias: net)
  pdu              Power Distribution Units
  check_mk         CheckMK monitoring infra

Examples:
  %(prog)s                                    # All active problems
  %(prog)s --group caas-bm                    # CaaS problems only
  %(prog)s --group iaas                       # IaaS/OpenStack problems
  %(prog)s --group staas --state CRIT         # STaaS critical only
  %(prog)s --host myserver                    # Filter by hostname
  %(prog)s --service CPU                      # Filter by service name
  %(prog)s --state CRIT                       # Only critical problems
  %(prog)s --state CRIT,WARN                  # Critical and warning
  %(prog)s --services-only                    # Only service problems
  %(prog)s --hosts-only                       # Only host problems
  %(prog)s --summary                          # Summary view
  %(prog)s --by-site                          # Breakdown by site
  %(prog)s --by-host                          # Breakdown by host
  %(prog)s --links                            # Include CheckMK URLs
  %(prog)s --no-ack --no-downtime             # Hide acknowledged/downtime
  %(prog)s --json                             # JSON output
        """,
    )
    parser.add_argument("--group", "-g", help="Filter by host group name or alias (e.g., caas-bm, iaas, staas, network)")
    parser.add_argument("--host", help="Filter by hostname (partial match, case-insensitive)")
    parser.add_argument("--service", help="Filter by service name (partial match, case-insensitive)")
    parser.add_argument("--state", help="Filter by state (comma-separated: CRIT,WARN,DOWN,UNREACHABLE,UNKNOWN)")
    parser.add_argument("--hosts-only", action="store_true", help="Show only host problems")
    parser.add_argument("--services-only", action="store_true", help="Show only service problems")
    parser.add_argument("--no-ack", action="store_true", help="Hide acknowledged problems")
    parser.add_argument("--no-downtime", action="store_true", help="Hide problems in downtime")
    parser.add_argument("--summary", action="store_true", help="Show summary grouped by state/service")
    parser.add_argument("--by-site", action="store_true", help="Show breakdown grouped by site")
    parser.add_argument("--by-host", action="store_true", help="Show breakdown grouped by host")
    parser.add_argument("--links", action="store_true", help="Include CheckMK host URLs in output")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--limit", type=int, default=100, help="Max problems to display (default: 100)")

    args = parser.parse_args()

    if args.hosts_only and args.services_only:
        print("Error: Cannot use both --hosts-only and --services-only", file=sys.stderr)
        sys.exit(1)

    # Resolve group alias
    group = resolve_group(args.group) if args.group else None
    if group:
        desc = KNOWN_HOST_GROUPS.get(group, group)
        print(f"Host group: {group} ({desc})", file=sys.stderr)
        print(file=sys.stderr)

    client = CheckMKClient()

    problems = []

    if not args.hosts_only:
        services = client.get_service_problems(group=group)
        problems.extend(parse_service(s) for s in services)

    if not args.services_only:
        hosts = client.get_host_problems(group=group)
        problems.extend(parse_host(h) for h in hosts)

    # Apply filters
    state_filter = None
    if args.state:
        state_filter = [s.strip().upper() for s in args.state.split(",")]

    problems = filter_problems(
        problems,
        host_filter=args.host,
        service_filter=args.service,
        state_filter=state_filter,
        hide_ack=args.no_ack,
        hide_downtime=args.no_downtime,
    )

    # Sort: CRIT/DOWN first, then WARN, then rest
    state_priority = {"CRIT": 0, "DOWN": 0, "WARN": 1, "UNREACHABLE": 1, "UNKNOWN": 2}
    problems.sort(key=lambda p: (state_priority.get(p["state"], 9), p["host"]))

    if args.json:
        json.dump(problems, sys.stdout, indent=2)
        print()
        return

    if not problems:
        print("No active problems found. ✅")
        return

    print(f"Found {len(problems)} active problem(s)")
    print()

    if args.summary:
        show_summary(problems)
    elif args.by_site:
        show_by_site(problems)
    elif args.by_host:
        show_by_host(problems)
    else:
        show_problems(problems, limit=args.limit, links=args.links)


if __name__ == "__main__":
    main()
