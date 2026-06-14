#!/usr/bin/env python3
"""
NetBox List Clusters Script
Usage: netbox-list-clusters.py [options]
"""

import sys
import json
import argparse
from typing import List, Dict, Any

from netbox_common import get_netbox_client, COUNTRY_MAPPING


def list_clusters(nb, group: str = None, site: str = None, status: str = None,
                 cluster_type: str = None, show_all: bool = False, limit: int = None) -> List[Dict[str, Any]]:
    """List clusters with optional filters"""
    try:
        # Build filter parameters
        filters = {}

        if not show_all and group:
            # Get group ID first
            try:
                groups = nb.virtualization.cluster_groups.filter(name=group)
                group_list = list(groups)
                if not group_list:
                    print(f"Warning: Cluster group '{group}' not found", file=sys.stderr)
                    return []
                filters['group_id'] = group_list[0].id
            except Exception as e:
                print(f"Warning: Failed to lookup group '{group}': {e}", file=sys.stderr)

        if site:
            # Check if site is a country name or code
            site_upper = site.upper().replace(' ', ' ')  # Normalize spacing
            country_code = COUNTRY_MAPPING.get(site_upper)

            if country_code:
                # Get all sites for this country (sites starting with country code)
                try:
                    all_sites = nb.dcim.sites.all()
                    country_sites = [s for s in all_sites if s.name and s.name.startswith(country_code)]
                    if country_sites:
                        site_ids = [s.id for s in country_sites]
                        filters['site_id'] = site_ids
                    else:
                        print(f"Warning: No sites found for country '{site}' (code: {country_code})", file=sys.stderr)
                        return []
                except Exception as e:
                    print(f"Warning: Failed to lookup sites for country '{site}': {e}", file=sys.stderr)
            else:
                # Try exact site name match
                try:
                    sites = nb.dcim.sites.filter(name=site)
                    site_list = list(sites)
                    if not site_list:
                        # Provide helpful error with available countries
                        available = sorted(set(COUNTRY_MAPPING.values()))
                        print(f"Warning: Site '{site}' not found", file=sys.stderr)
                        print(f"Available countries: {', '.join(available)}", file=sys.stderr)
                        print(f"Or specify exact site name (e.g., SKBRAD003)", file=sys.stderr)
                        return []
                    filters['site_id'] = site_list[0].id
                except Exception as e:
                    print(f"Warning: Failed to lookup site '{site}': {e}", file=sys.stderr)

        if cluster_type:
            # Get cluster type ID
            try:
                types = nb.virtualization.cluster_types.filter(name=cluster_type)
                type_list = list(types)
                if not type_list:
                    print(f"Warning: Cluster type '{cluster_type}' not found", file=sys.stderr)
                    return []
                filters['type_id'] = type_list[0].id
            except Exception as e:
                print(f"Warning: Failed to lookup cluster type '{cluster_type}': {e}", file=sys.stderr)

        if status:
            filters['status'] = status

        # Fetch clusters
        clusters = nb.virtualization.clusters.filter(**filters)

        # Convert to list of dicts
        result = []
        count = 0
        for cluster in clusters:
            if limit and count >= limit:
                break

            cluster_data = {
                'id': cluster.id,
                'name': cluster.name,
                'type': cluster.type.name if cluster.type else None,
                'group': cluster.group.name if cluster.group else None,
                'site': cluster.site.name if cluster.site else None,
                'status': cluster.status.label if cluster.status else None,
                'device_count': cluster.device_count if hasattr(cluster, 'device_count') else 0,
                'vm_count': cluster.virtualmachine_count if hasattr(cluster, 'virtualmachine_count') else 0,
                'description': cluster.description if cluster.description else '',
                'url': cluster.url if hasattr(cluster, 'url') else None,
            }
            result.append(cluster_data)
            count += 1

        return result

    except Exception as e:
        print(f"Error: Failed to list clusters: {e}", file=sys.stderr)
        print("Make sure you are connected to Telekom VPN", file=sys.stderr)
        sys.exit(1)


def format_table(clusters: List[Dict[str, Any]]):
    """Format clusters as table"""
    if not clusters:
        print("No clusters found")
        return

    # Print header
    print(f"{'ID':<6} {'Name':<30} {'Group':<15} {'Site':<15} {'Status':<10} {'Devices':<8} {'VMs':<5} Description")
    print("-" * 130)

    # Print rows
    for c in clusters:
        desc = c['description'][:30] + '...' if len(c['description']) > 30 else c['description']
        print(f"{c['id']:<6} {c['name']:<30} {c['group'] or '-':<15} "
              f"{c['site'] or '-':<15} {c['status'] or '-':<10} {c['device_count']:<8} {c['vm_count']:<5} {desc}")

    # Summary
    total_devices = sum(c['device_count'] for c in clusters)
    total_vms = sum(c['vm_count'] for c in clusters)
    print(f"\nTotal: {len(clusters)} cluster(s), {total_devices} devices, {total_vms} VMs")


def format_json(clusters: List[Dict[str, Any]]):
    """Format clusters as JSON"""
    print(json.dumps(clusters, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description='List NetBox virtualization clusters',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all caas clusters (default)
  %(prog)s

  # List clusters in specific group
  %(prog)s --group openstack

  # List all clusters regardless of group
  %(prog)s --all

  # Filter by site and status
  %(prog)s --site fra01 --status active

  # Get JSON output
  %(prog)s --format json
        """
    )

    parser.add_argument('--group', default='CaaS',
                       help='Filter by cluster group name (default: CaaS)')
    parser.add_argument('--site',
                       help='Filter by site (country name/code or exact site name). '
                            'Countries: AT/Austria, SK/Slovakia, DE/Germany, CZ/Czechia, '
                            'HU/Hungary, HR/Croatia, PL/Poland, MK/Macedonia, ME/Montenegro, US/USA')
    parser.add_argument('--type',
                       help='Filter by cluster type (e.g., baremetal, openstack)')
    parser.add_argument('--status',
                       choices=['active', 'planned', 'staged', 'decommissioning', 'offline'],
                       help='Filter by status')
    parser.add_argument('--all', action='store_true',
                       help='Show all clusters (ignore group filter)')
    parser.add_argument('--format', choices=['table', 'json'], default='table',
                       help='Output format (default: table)')
    parser.add_argument('--limit', type=int,
                       help='Limit number of results')

    args = parser.parse_args()

    # Initialize NetBox client
    nb = get_netbox_client()

    # List clusters
    group = None if args.all else args.group
    clusters = list_clusters(nb, group=group, site=args.site, status=args.status,
                            cluster_type=args.type, show_all=args.all, limit=args.limit)

    # Format output
    if args.format == 'json':
        format_json(clusters)
    else:
        format_table(clusters)


if __name__ == '__main__':
    main()
