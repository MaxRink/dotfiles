#!/usr/bin/env python3
"""
CheckMK Configuration Viewer
Queries CheckMK REST API for host and service configuration details.

Usage:
  cmk-config.py --host HOSTNAME                    # Host details
  cmk-config.py --host HOSTNAME --services          # All services on host
  cmk-config.py --host HOSTNAME --service PATTERN   # Service config details
  cmk-config.py --search-hosts PATTERN              # Search hosts by name
  cmk-config.py --rulesets [SEARCH]                 # List rulesets
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cmk_common import CheckMKClient as _BaseClient, resolve_group, KNOWN_HOST_GROUPS


HOST_STATES = {0: "UP", 1: "DOWN", 2: "UNREACHABLE"}
SERVICE_STATES = {0: "OK", 1: "WARN", 2: "CRIT", 3: "UNKNOWN"}
STATE_ICONS = {
    "CRIT": "🔴", "DOWN": "🔴",
    "WARN": "🟡", "UNREACHABLE": "🟡",
    "UNKNOWN": "🟣",
    "OK": "🟢", "UP": "🟢",
}


def fmt_ts(ts):
    """Format a Unix timestamp."""
    if not ts:
        return "N/A"
    try:
        dt = datetime.fromtimestamp(float(ts), tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except (ValueError, TypeError, OSError):
        return str(ts)


class CheckMKClient(_BaseClient):
    """Extended client with configuration query support."""

    def get_host_details(self, hostname):
        """Get detailed host info via Livestatus."""
        query = json.dumps({"op": "=", "left": "name", "right": hostname})
        params = {
            "query": query,
            "columns": [
                "name", "address", "groups", "labels", "tags",
                "state", "last_state_change", "plugin_output",
                "num_services", "num_services_ok", "num_services_warn",
                "num_services_crit", "num_services_unknown",
                "check_command", "contact_groups", "contacts",
            ],
        }
        data = self._get("domain-types/host/collections/all", params=params)
        values = data.get("value", [])
        return values[0].get("extensions", {}) if values else None

    def search_hosts(self, pattern, group=None, limit=50):
        """Search hosts by name pattern."""
        expr = [{"op": "~", "left": "name", "right": f".*{pattern}.*"}]
        if group:
            expr.append({"op": ">=", "left": "groups", "right": group})
        if len(expr) == 1:
            query = json.dumps(expr[0])
        else:
            query = json.dumps({"op": "and", "expr": expr})
        params = {
            "query": query,
            "columns": [
                "name", "address", "groups", "state",
                "num_services", "num_services_crit", "num_services_warn",
                "num_services_unknown", "labels", "tags",
            ],
        }
        data = self._get("domain-types/host/collections/all", params=params)
        return [v.get("extensions", {}) for v in data.get("value", [])][:limit]

    def get_host_services(self, hostname, service_filter=None):
        """Get all services for a host, optionally filtered."""
        expr = [{"op": "=", "left": "host_name", "right": hostname}]
        if service_filter:
            expr.append({"op": "~", "left": "description", "right": f".*{service_filter}.*"})
        if len(expr) == 1:
            query = json.dumps(expr[0])
        else:
            query = json.dumps({"op": "and", "expr": expr})
        params = {
            "query": query,
            "columns": [
                "host_name", "description", "state", "plugin_output",
                "check_command", "check_type", "check_interval", "retry_interval",
                "max_check_attempts", "current_attempt",
                "contact_groups", "contacts",
                "acknowledged", "scheduled_downtime_depth",
                "last_state_change", "last_check", "next_check",
                "perf_data", "check_period", "notes", "notes_url",
            ],
        }
        data = self._get("domain-types/service/collections/all", params=params)
        return [v.get("extensions", {}) for v in data.get("value", [])]

    def get_rulesets(self, search=None):
        """List rulesets (requires Rulesets permission)."""
        params = {}
        if search:
            params["search_options"] = json.dumps({"fulltext": search})
        return self._get("domain-types/ruleset/collections/all", params=params)

    def get_rules(self, ruleset_name):
        """List rules for a ruleset (requires Rulesets permission)."""
        params = {"ruleset_name": ruleset_name}
        return self._get("domain-types/rule/collections/all", params=params)


def show_host_details(host, client):
    """Display host configuration details."""
    state = HOST_STATES.get(host.get("state", -1), "UNKNOWN")
    icon = STATE_ICONS.get(state, "⚪")
    tags = host.get("tags", {})
    labels = host.get("labels", {})

    print(f"{'Host':<20} {host.get('name', 'N/A')}")
    print(f"{'Address':<20} {host.get('address', 'N/A')}")
    print(f"{'State':<20} {icon} {state}")
    print(f"{'Output':<20} {host.get('plugin_output', '')}")
    print(f"{'Last Change':<20} {fmt_ts(host.get('last_state_change'))}")
    print(f"{'Check Command':<20} {host.get('check_command', 'N/A')}")
    print(f"{'Contact Groups':<20} {', '.join(host.get('contact_groups', []))}")
    print(f"{'Host Groups':<20} {', '.join(host.get('groups', []))}")
    print(f"{'Link':<20} {client.host_url(host.get('name', ''))}")

    # Services summary
    total = host.get("num_services", 0)
    ok = host.get("num_services_ok", 0)
    warn = host.get("num_services_warn", 0)
    crit = host.get("num_services_crit", 0)
    unk = host.get("num_services_unknown", 0)
    print()
    print(f"Services: {total} total  🟢 {ok} OK  🟡 {warn} WARN  🔴 {crit} CRIT  🟣 {unk} UNKNOWN")

    # Tags
    if tags:
        print()
        print("Tags:")
        for k, v in sorted(tags.items()):
            print(f"  {k}: {v}")

    # Labels
    if labels:
        print()
        print("Labels:")
        for k, v in sorted(labels.items()):
            print(f"  {k}: {v}")


def show_services_list(services, brief=True):
    """Display services list."""
    # Sort by state (CRIT first)
    state_order = {2: 0, 3: 1, 1: 2, 0: 3}
    services.sort(key=lambda s: (state_order.get(s.get("state", 0), 9), s.get("description", "")))

    if brief:
        hdr = f"{'Service':<45} {'State':>5} {'Check Command':<30} {'Interval':>8}"
        print(hdr)
        print("=" * len(hdr))
        for s in services:
            state = SERVICE_STATES.get(s.get("state", -1), "?")
            icon = STATE_ICONS.get(state, "⚪")
            desc = s.get("description", "?")[:44]
            cmd = s.get("check_command", "?")[:29]
            interval = f"{s.get('check_interval', '?')}m"
            print(f"{desc:<45} {icon}{state:>4} {cmd:<30} {interval:>8}")
    else:
        for s in services:
            show_service_detail(s)
            print()


def show_service_detail(svc):
    """Display detailed service configuration."""
    state = SERVICE_STATES.get(svc.get("state", -1), "UNKNOWN")
    icon = STATE_ICONS.get(state, "⚪")
    dt_depth = svc.get("scheduled_downtime_depth", 0)
    ack = svc.get("acknowledged", 0)

    print(f"{'Service':<20} {svc.get('description', 'N/A')}")
    print(f"{'Host':<20} {svc.get('host_name', 'N/A')}")
    print(f"{'State':<20} {icon} {state}")
    print(f"{'Output':<20} {svc.get('plugin_output', '')[:200]}")
    print(f"{'Check Command':<20} {svc.get('check_command', 'N/A')}")
    print(f"{'Check Interval':<20} {svc.get('check_interval', 'N/A')} min")
    print(f"{'Retry Interval':<20} {svc.get('retry_interval', 'N/A')} min")
    print(f"{'Max Attempts':<20} {svc.get('max_check_attempts', 'N/A')}")
    print(f"{'Current Attempt':<20} {svc.get('current_attempt', 'N/A')}")
    print(f"{'Check Period':<20} {svc.get('check_period', 'N/A')}")
    print(f"{'Contact Groups':<20} {', '.join(svc.get('contact_groups', []))}")
    print(f"{'Acknowledged':<20} {'Yes' if ack else 'No'}")
    print(f"{'In Downtime':<20} {'Yes' if dt_depth > 0 else 'No'}")
    print(f"{'Last Check':<20} {fmt_ts(svc.get('last_check'))}")
    print(f"{'Last State Change':<20} {fmt_ts(svc.get('last_state_change'))}")
    print(f"{'Next Check':<20} {fmt_ts(svc.get('next_check'))}")
    if svc.get("perf_data"):
        print(f"{'Perf Data':<20} {svc['perf_data'][:200]}")
    if svc.get("notes"):
        print(f"{'Notes':<20} {svc['notes']}")
    if svc.get("notes_url"):
        print(f"{'Notes URL':<20} {svc['notes_url']}")


def show_search_results(hosts):
    """Display host search results."""
    hdr = f"{'Host':<60} {'State':>5} {'Groups':<20} {'Svcs':>5} {'CRIT':>5} {'WARN':>5}"
    print(hdr)
    print("=" * len(hdr))
    for h in hosts:
        state = HOST_STATES.get(h.get("state", -1), "?")
        icon = STATE_ICONS.get(state, "⚪")
        name = h.get("name", "?")[:59]
        groups = ", ".join(h.get("groups", []))[:19]
        total = h.get("num_services", 0)
        crit = h.get("num_services_crit", 0)
        warn = h.get("num_services_warn", 0)
        print(f"{name:<60} {icon}{state:>4} {groups:<20} {total:>5} {crit:>5} {warn:>5}")
    print(f"\n{len(hosts)} host(s) found")


def main():
    parser = argparse.ArgumentParser(
        description="View CheckMK host and service configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  Host details:     %(prog)s --host HOSTNAME
  Host services:    %(prog)s --host HOSTNAME --services
  Service config:   %(prog)s --host HOSTNAME --service PATTERN
  Search hosts:     %(prog)s --search-hosts PATTERN [--group GROUP]
  List rulesets:     %(prog)s --rulesets [SEARCH]      (requires permission)

Examples:
  %(prog)s --host hc-czprgc1-CAAS-BM-czprgc1-5gc-prod-IMM-J7022553
  %(prog)s --host hc-czprgc1-CAAS-BM-czprgc1-5gc-prod-IMM-J7022553 --services
  %(prog)s --host hc-czprgc1-CAAS-BM-czprgc1-5gc-prod-IMM-J7022553 --service IPMI
  %(prog)s --search-hosts czprgc1 --group caas
  %(prog)s --rulesets ipmi
        """,
    )
    parser.add_argument("--host", help="Hostname (exact match for details)")
    parser.add_argument("--services", action="store_true", help="List all services on the host (brief)")
    parser.add_argument("--service", help="Filter/show service details (pattern match)")
    parser.add_argument("--search-hosts", help="Search hosts by name pattern")
    parser.add_argument("--group", "-g", help="Filter by host group (for --search-hosts)")
    parser.add_argument("--rulesets", nargs="?", const="", help="List rulesets (optional search term)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not any([args.host, args.search_hosts, args.rulesets is not None]):
        parser.print_help()
        sys.exit(1)

    client = CheckMKClient()

    # --- Search hosts ---
    if args.search_hosts:
        group = resolve_group(args.group) if args.group else None
        hosts = client.search_hosts(args.search_hosts, group=group)
        if args.json:
            json.dump(hosts, sys.stdout, indent=2, default=str)
            print()
        elif not hosts:
            print(f"No hosts found matching '{args.search_hosts}'")
        else:
            show_search_results(hosts)
        return

    # --- Rulesets ---
    if args.rulesets is not None:
        search = args.rulesets or None
        try:
            data = client.get_rulesets(search=search)
            rulesets = data.get("value", [])
            if args.json:
                json.dump(rulesets, sys.stdout, indent=2, default=str)
                print()
            elif not rulesets:
                print("No rulesets found.")
            else:
                print(f"Found {len(rulesets)} ruleset(s)")
                print()
                for rs in rulesets[:50]:
                    ext = rs.get("extensions", {})
                    n_rules = ext.get("number_of_rules", 0)
                    name = rs.get("id", ext.get("name", "?"))
                    marker = f" ({n_rules} rules)" if n_rules else ""
                    print(f"  {name}{marker}")
                if len(rulesets) > 50:
                    print(f"  ... and {len(rulesets) - 50} more")
        except SystemExit:
            print(
                "⚠️  Cannot access rulesets — the automation user lacks 'Rulesets' permission.\n"
                "    Ask your CheckMK admin to grant this permission, or check rules via the Web UI.",
                file=sys.stderr,
            )
        return

    # --- Host details / services ---
    if args.host:
        if args.service:
            # Detailed service config
            services = client.get_host_services(args.host, service_filter=args.service)
            if args.json:
                json.dump(services, sys.stdout, indent=2, default=str)
                print()
            elif not services:
                print(f"No services matching '{args.service}' on host '{args.host}'")
            else:
                print(f"Found {len(services)} service(s) matching '{args.service}' on {args.host}")
                print()
                for s in services:
                    show_service_detail(s)
                    print()

        elif args.services:
            # List all services (brief)
            services = client.get_host_services(args.host)
            if args.json:
                json.dump(services, sys.stdout, indent=2, default=str)
                print()
            elif not services:
                print(f"No services found on host '{args.host}'")
            else:
                print(f"{len(services)} service(s) on {args.host}")
                print()
                show_services_list(services)

        else:
            # Host details
            host = client.get_host_details(args.host)
            if args.json:
                json.dump(host, sys.stdout, indent=2, default=str)
                print()
            elif not host:
                print(f"Host '{args.host}' not found")
            else:
                show_host_details(host, client)


if __name__ == "__main__":
    main()
