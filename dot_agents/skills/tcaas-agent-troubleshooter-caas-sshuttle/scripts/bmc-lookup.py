#!/usr/bin/env python3
"""
Look up the management cluster and subnets needed for BMC access in a tenant.

Usage:
    bmc-lookup.py <tenant-slug>
    bmc-lookup.py --list
    bmc-lookup.py --json <tenant-slug>

Examples:
    bmc-lookup.py ic-defraf2        → mgmt-05-prod
    bmc-lookup.py hc-plwarc1        → mgmt-35-prod (+ extra subnets)
    bmc-lookup.py --list            → all tenant→mgmt mappings
"""

import argparse
import json
import sys

from bmc_config import TENANT_MGMT_MAP, EXTRA_SUBNETS, DEFAULT_SUBNET


def lookup(tenant):
    mgmt = TENANT_MGMT_MAP.get(tenant)
    if not mgmt:
        return None
    subnets = [DEFAULT_SUBNET] + EXTRA_SUBNETS.get(mgmt, [])
    return {"tenant": tenant, "mgmt_cluster": mgmt, "subnets": subnets}


def main():
    parser = argparse.ArgumentParser(description="Look up mgmt cluster for BMC access")
    parser.add_argument("tenant", nargs="?", help="NetBox tenant slug (e.g. ic-defraf2)")
    parser.add_argument("--list", action="store_true", help="List all tenant→mgmt mappings")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.list:
        if args.json:
            print(json.dumps(TENANT_MGMT_MAP, indent=2))
        else:
            for tenant, mgmt in sorted(TENANT_MGMT_MAP.items()):
                extra = EXTRA_SUBNETS.get(mgmt)
                suffix = f"  (+{', '.join(extra)})" if extra else ""
                print(f"  {tenant:20s} → {mgmt}{suffix}")
        return

    if not args.tenant:
        parser.error("tenant slug required (or use --list)")

    result = lookup(args.tenant)
    if not result:
        print(f"ERROR: tenant '{args.tenant}' not found in mapping", file=sys.stderr)
        print(f"Known tenants: {', '.join(sorted(TENANT_MGMT_MAP.keys()))}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"mgmt_cluster={result['mgmt_cluster']}")
        print(f"subnets={' '.join(result['subnets'])}")


if __name__ == "__main__":
    main()
