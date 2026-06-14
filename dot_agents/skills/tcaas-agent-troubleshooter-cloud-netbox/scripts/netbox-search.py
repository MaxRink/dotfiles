#!/usr/bin/env python3
"""
NetBox Search Script
Usage: netbox-search.py <query> [options]
"""

import sys
import json
import argparse
from typing import List, Dict, Any

from netbox_common import get_netbox_client


def search_clusters(nb, query: str, group: str = None, site: str = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Search clusters"""
    try:
        filters = {}

        if group:
            groups = list(nb.virtualization.cluster_groups.filter(name=group))
            if groups:
                filters['group_id'] = groups[0].id

        if site:
            sites = list(nb.dcim.sites.filter(name=site))
            if sites:
                filters['site_id'] = sites[0].id

        # NetBox search using q parameter
        if query:
            filters['q'] = query

        clusters = nb.virtualization.clusters.filter(**filters)

        result = []
        count = 0
        for cluster in clusters:
            if limit and count >= limit:
                break

            result.append({
                'type': 'cluster',
                'id': cluster.id,
                'name': cluster.name,
                'group': cluster.group.name if cluster.group else None,
                'site': cluster.site.name if cluster.site else None,
                'status': cluster.status.label if cluster.status else None,
                'description': cluster.description if cluster.description else '',
                'url': cluster.url if hasattr(cluster, 'url') else None,
            })
            count += 1

        return result
    except Exception as e:
        print(f"Warning: Failed to search clusters: {e}", file=sys.stderr)
        return []


def search_vms(nb, query: str, group: str = None, site: str = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Search virtual machines"""
    try:
        filters = {}

        if group:
            groups = list(nb.virtualization.cluster_groups.filter(name=group))
            if groups:
                # Get all clusters in this group
                group_clusters = list(nb.virtualization.clusters.filter(group_id=groups[0].id))
                if group_clusters:
                    cluster_ids = [c.id for c in group_clusters]
                    # Filter VMs by cluster
                    filters['cluster_id'] = cluster_ids

        if site:
            sites = list(nb.dcim.sites.filter(name=site))
            if sites:
                filters['site_id'] = sites[0].id

        if query:
            filters['q'] = query

        vms = nb.virtualization.virtual_machines.filter(**filters)

        result = []
        count = 0
        for vm in vms:
            if limit and count >= limit:
                break

            result.append({
                'type': 'vm',
                'id': vm.id,
                'name': vm.name,
                'cluster': vm.cluster.name if vm.cluster else None,
                'site': vm.site.name if vm.site else None,
                'status': vm.status.label if vm.status else None,
                'vcpus': vm.vcpus,
                'memory': vm.memory,
                'primary_ip': str(vm.primary_ip) if vm.primary_ip else None,
                'description': vm.description if vm.description else '',
                'url': vm.url if hasattr(vm, 'url') else None,
            })
            count += 1

        return result
    except Exception as e:
        print(f"Warning: Failed to search VMs: {e}", file=sys.stderr)
        return []


def search_devices(nb, query: str, site: str = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Search devices"""
    try:
        filters = {}

        if site:
            sites = list(nb.dcim.sites.filter(name=site))
            if sites:
                filters['site_id'] = sites[0].id

        if query:
            filters['q'] = query

        devices = nb.dcim.devices.filter(**filters)

        result = []
        count = 0
        for device in devices:
            if limit and count >= limit:
                break

            result.append({
                'type': 'device',
                'id': device.id,
                'name': device.name,
                'device_type': device.device_type.display if device.device_type else None,
                'site': device.site.name if device.site else None,
                'status': device.status.label if device.status else None,
                'role': device.device_role.name if device.device_role else None,
                'primary_ip': str(device.primary_ip) if device.primary_ip else None,
                'description': device.comments if hasattr(device, 'comments') and device.comments else '',
                'url': device.url if hasattr(device, 'url') else None,
            })
            count += 1

        return result
    except Exception as e:
        print(f"Warning: Failed to search devices: {e}", file=sys.stderr)
        return []


def format_table(results: List[Dict[str, Any]]):
    """Format search results as table"""
    if not results:
        print("No results found")
        return

    # Group by type
    by_type = {}
    for r in results:
        obj_type = r['type']
        if obj_type not in by_type:
            by_type[obj_type] = []
        by_type[obj_type].append(r)

    # Print each type
    for obj_type, items in sorted(by_type.items()):
        print()
        print(f"=== {obj_type.upper()}S ===")
        print()

        if obj_type == 'cluster':
            print(f"{'ID':<6} {'Name':<30} {'Group':<15} {'Site':<15} {'Status':<12} Description")
            print("-" * 110)
            for item in items:
                desc = item['description'][:30] + '...' if len(item['description']) > 30 else item['description']
                print(f"{item['id']:<6} {item['name']:<30} {item['group'] or '-':<15} "
                      f"{item['site'] or '-':<15} {item['status'] or '-':<12} {desc}")

        elif obj_type == 'vm':
            print(f"{'ID':<6} {'Name':<30} {'Cluster':<20} {'Status':<12} {'vCPUs':<7} {'Memory':<10} IP")
            print("-" * 110)
            for item in items:
                mem = f"{item['memory']}MB" if item['memory'] else '-'
                print(f"{item['id']:<6} {item['name']:<30} {item['cluster'] or '-':<20} "
                      f"{item['status'] or '-':<12} {item['vcpus'] or '-':<7} {mem:<10} {item['primary_ip'] or '-'}")

        elif obj_type == 'device':
            print(f"{'ID':<6} {'Name':<30} {'Type':<20} {'Site':<15} {'Role':<15} Status")
            print("-" * 110)
            for item in items:
                print(f"{item['id']:<6} {item['name']:<30} {item['device_type'] or '-':<20} "
                      f"{item['site'] or '-':<15} {item['role'] or '-':<15} {item['status'] or '-'}")

        print(f"\nFound: {len(items)} {obj_type}(s)")

    print()
    print(f"Total results: {len(results)}")


def format_json(results: List[Dict[str, Any]]):
    """Format search results as JSON"""
    print(json.dumps(results, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description='Search NetBox objects',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search everything
  %(prog)s "kubernetes"

  # Search only clusters
  %(prog)s "prod" --type clusters

  # Search VMs in caas group
  %(prog)s "controller" --type vms --group caas

  # Search at specific site
  %(prog)s "nginx" --site fra01

  # Get JSON output
  %(prog)s "database" --format json
        """
    )

    parser.add_argument('query', nargs='?', default='',
                       help='Search query (searches names, descriptions, comments)')
    parser.add_argument('--type', choices=['all', 'clusters', 'vms', 'devices'], default='all',
                       help='Filter by object type (default: all)')
    parser.add_argument('--group',
                       help='Filter clusters/VMs by cluster group name')
    parser.add_argument('--site',
                       help='Filter by site name')
    parser.add_argument('--limit', type=int, default=50,
                       help='Limit results per type (default: 50)')
    parser.add_argument('--format', choices=['table', 'json'], default='table',
                       help='Output format (default: table)')

    args = parser.parse_args()

    # Initialize NetBox client
    nb = get_netbox_client()

    # Search
    results = []

    if args.type in ['all', 'clusters']:
        results.extend(search_clusters(nb, args.query, group=args.group, site=args.site, limit=args.limit))

    if args.type in ['all', 'vms']:
        results.extend(search_vms(nb, args.query, group=args.group, site=args.site, limit=args.limit))

    if args.type in ['all', 'devices']:
        results.extend(search_devices(nb, args.query, site=args.site, limit=args.limit))

    # Format output
    if args.format == 'json':
        format_json(results)
    else:
        format_table(results)


if __name__ == '__main__':
    main()
