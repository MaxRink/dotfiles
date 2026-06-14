#!/usr/bin/env python3
"""
NetBox Cluster Statistics Script

Fetches all CaaS clusters and classifies them as CIT CaaS or T-CaaS
by inspecting custom_fields.arbitrary_data.apiVersion:
  - CIT CaaS: caas.pan-net.eu/v1alpha1
  - T-CaaS:   t-caas.telekom.com/v1alpha1

Usage: netbox-cluster-stats.py [options]
"""

import sys
import json
import argparse
from typing import Dict, List, Tuple

from netbox_common import get_netbox_client


def classify_cluster(cluster) -> str:
    """Return 'cit', 'tcaas', or 'unknown' based on arbitrary_data.apiVersion."""
    try:
        ad = dict(cluster.custom_fields).get('arbitrary_data') or {}
        for val in ad.values():
            if isinstance(val, dict):
                api_version = val.get('apiVersion', '')
                if 'caas.pan-net.eu' in api_version:
                    return 'cit'
                if 't-caas.telekom.com' in api_version:
                    return 'tcaas'
    except Exception:
        pass
    return 'unknown'


def fetch_clusters(nb, group: str = 'CaaS') -> List:
    """Fetch all clusters in the given group."""
    try:
        groups = list(nb.virtualization.cluster_groups.filter(name=group))
        if not groups:
            print(f"Error: Cluster group '{group}' not found", file=sys.stderr)
            sys.exit(1)
        group_id = groups[0].id
        return list(nb.virtualization.clusters.filter(group_id=group_id))
    except Exception as e:
        print(f"Error: Failed to fetch clusters: {e}", file=sys.stderr)
        print("Make sure you are connected to Telekom VPN", file=sys.stderr)
        sys.exit(1)


def classify_all(clusters) -> Tuple[List, List, List]:
    """Return (cit_clusters, tcaas_clusters, unknown_clusters)."""
    cit, tcaas, unknown = [], [], []
    for c in clusters:
        kind = classify_cluster(c)
        if kind == 'cit':
            cit.append(c)
        elif kind == 'tcaas':
            tcaas.append(c)
        else:
            unknown.append(c)
    return cit, tcaas, unknown


def cluster_to_dict(c) -> Dict:
    return {
        'id': c.id,
        'name': c.name,
        'type': c.type.name if c.type else None,
        'site': c.site.name if c.site else None,
        'tenant': c.tenant.name if c.tenant else None,
        'status': c.status.label if c.status else None,
        'device_count': c.device_count if hasattr(c, 'device_count') else 0,
        'vm_count': c.virtualmachine_count if hasattr(c, 'virtualmachine_count') else 0,
    }


def format_table(cit, tcaas, unknown, show_list: str = None):
    print(f"{'Cluster Type':<20} {'Count':>6}")
    print("-" * 28)
    print(f"{'CIT CaaS':<20} {len(cit):>6}")
    print(f"{'T-CaaS':<20} {len(tcaas):>6}")
    if unknown:
        print(f"{'Unknown/Other':<20} {len(unknown):>6}")
    print("-" * 28)
    total = len(cit) + len(tcaas) + len(unknown)
    print(f"{'Total':<20} {total:>6}")

    if show_list in ('tcaas', 'all') and tcaas:
        print(f"\nT-CaaS Clusters ({len(tcaas)}):")
        for c in sorted(tcaas, key=lambda x: x.name):
            print(f"  {c.name}")

    if show_list in ('cit', 'all') and cit:
        print(f"\nCIT CaaS Clusters ({len(cit)}):")
        for c in sorted(cit, key=lambda x: x.name):
            print(f"  {c.name}")

    if show_list == 'unknown' and unknown:
        print(f"\nUnknown/Other Clusters ({len(unknown)}):")
        for c in sorted(unknown, key=lambda x: x.name):
            print(f"  {c.name}")


def format_json(cit, tcaas, unknown, show_list: str = None):
    result = {
        'summary': {
            'cit_caas': len(cit),
            'tcaas': len(tcaas),
            'unknown': len(unknown),
            'total': len(cit) + len(tcaas) + len(unknown),
        }
    }
    if show_list in ('tcaas', 'all'):
        result['tcaas_clusters'] = [cluster_to_dict(c) for c in sorted(tcaas, key=lambda x: x.name)]
    if show_list in ('cit', 'all'):
        result['cit_clusters'] = [cluster_to_dict(c) for c in sorted(cit, key=lambda x: x.name)]
    if show_list == 'unknown':
        result['unknown_clusters'] = [cluster_to_dict(c) for c in sorted(unknown, key=lambda x: x.name)]
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description='Show CIT CaaS vs T-CaaS cluster statistics from NetBox',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show summary counts only
  %(prog)s

  # Show summary + list of T-CaaS clusters
  %(prog)s --list tcaas

  # Show summary + list of CIT CaaS clusters
  %(prog)s --list cit

  # Show all clusters grouped by type
  %(prog)s --list all

  # JSON output with T-CaaS cluster details
  %(prog)s --list tcaas --format json
        """
    )
    parser.add_argument('--group', default='CaaS',
                        help='Cluster group to query (default: CaaS)')
    parser.add_argument('--list', choices=['tcaas', 'cit', 'all', 'unknown'],
                        dest='show_list', metavar='TYPE',
                        help='Also list cluster names for the given type: tcaas, cit, all, unknown')
    parser.add_argument('--format', choices=['table', 'json'], default='table',
                        help='Output format (default: table)')

    args = parser.parse_args()

    nb = get_netbox_client()
    clusters = fetch_clusters(nb, group=args.group)
    cit, tcaas, unknown = classify_all(clusters)

    if args.format == 'json':
        format_json(cit, tcaas, unknown, show_list=args.show_list)
    else:
        format_table(cit, tcaas, unknown, show_list=args.show_list)


if __name__ == '__main__':
    main()
