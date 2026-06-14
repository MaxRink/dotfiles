#!/usr/bin/env python3
"""
NetBox Get Server Connections Script
Shows physical network connections (switch/port mappings) for servers

Usage: netbox-get-server-connections.py <server-identifier> [options]
"""

import sys
import json
import argparse
from typing import List, Dict, Any, Optional

from netbox_common import get_netbox_client


def get_server_by_name(nb, device_name: str) -> Optional[Any]:
    """Get server device by exact name"""
    try:
        devices = nb.dcim.devices.filter(name=device_name)
        device_list = list(devices)
        if device_list:
            return device_list[0]
        return None
    except Exception as e:
        print(f"Error: Failed to lookup device '{device_name}': {e}", file=sys.stderr)
        return None


def get_server_by_hostname(nb, hostname: str, site: str = None) -> Optional[Any]:
    """Get server device by hostname (custom field)"""
    try:
        filters = {}
        if site:
            sites = nb.dcim.sites.filter(name=site)
            site_list = list(sites)
            if site_list:
                filters['site_id'] = site_list[0].id

        # Search for devices with matching hostname in custom fields
        devices = nb.dcim.devices.filter(**filters)
        for device in devices:
            if hasattr(device, 'custom_fields') and device.custom_fields:
                if device.custom_fields.get('hostname') == hostname:
                    return device
        return None
    except Exception as e:
        print(f"Error: Failed to lookup hostname '{hostname}': {e}", file=sys.stderr)
        return None


def get_servers_by_cluster(nb, cluster_name: str) -> List[Any]:
    """Get all server devices in a cluster by matching hostnames"""
    try:
        # Get cluster from virtualization API
        clusters = nb.virtualization.clusters.filter(name=cluster_name)
        cluster_list = list(clusters)
        if not cluster_list:
            return []

        cluster = cluster_list[0]
        site_id = cluster.site.id if cluster.site else None

        # Find devices with hostnames matching cluster pattern
        servers = []
        filters = {}
        if site_id:
            filters['site_id'] = site_id

        devices = nb.dcim.devices.filter(**filters)
        for device in devices:
            if hasattr(device, 'custom_fields') and device.custom_fields:
                hostname = device.custom_fields.get('hostname', '')
                if hostname and cluster_name in hostname:
                    servers.append(device)

        return servers
    except Exception as e:
        print(f"Error: Failed to lookup cluster '{cluster_name}': {e}", file=sys.stderr)
        return []


def get_nic_devices(nb, server_device: Any) -> List[Any]:
    """Get all NIC child devices for a server"""
    try:
        # Use name pattern matching for faster lookup
        # NIC devices follow pattern: <server-name>.NIC1, <server-name>.NIC2, etc.
        nic_pattern = f"{server_device.name}.NIC"
        nics = nb.dcim.devices.filter(name__isw=nic_pattern)
        return list(nics)
    except Exception as e:
        print(f"Error: Failed to get NIC devices for '{server_device.name}': {e}", file=sys.stderr)
        return []


def get_nic_connections(nb, nic_device: Any) -> List[Dict[str, Any]]:
    """Get all interface connections for a NIC device"""
    try:
        interfaces = nb.dcim.interfaces.filter(device_id=nic_device.id)
        connections = []

        for interface in interfaces:
            if hasattr(interface, 'link_peers') and interface.link_peers:
                for peer in interface.link_peers:
                    if hasattr(peer, 'device') and peer.device:
                        connection = {
                            'interface_name': interface.name,
                            'switch_id': peer.device.id,
                            'switch_name': peer.device.name,
                            'switch_port': peer.name,
                        }
                        connections.append(connection)

        return connections
    except Exception as e:
        print(f"Error: Failed to get connections for NIC '{nic_device.name}': {e}", file=sys.stderr)
        return []


def get_switch_details(nb, switch_id: int) -> Dict[str, Any]:
    """Get detailed information about a switch"""
    try:
        switch = nb.dcim.devices.get(switch_id)
        return {
            'id': switch.id,
            'name': switch.name,
            'type': switch.device_type.display if switch.device_type else 'N/A',
            'role': switch.device_role.name if switch.device_role else 'N/A',
        }
    except Exception as e:
        return {
            'id': switch_id,
            'name': 'Unknown',
            'type': 'N/A',
            'role': 'N/A',
        }


def gather_server_connections(nb, server_device: Any) -> Dict[str, Any]:
    """Gather all connection information for a server"""
    server_info = {
        'id': server_device.id,
        'name': server_device.name,
        'hostname': server_device.custom_fields.get('hostname', 'N/A') if server_device.custom_fields else 'N/A',
        'role': server_device.device_role.name if server_device.device_role else 'N/A',
        'site': server_device.site.name if server_device.site else 'N/A',
        'nics': []
    }

    # Get all NIC devices
    nic_devices = get_nic_devices(nb, server_device)

    # Cache for switch details to avoid repeated API calls
    switch_cache = {}

    for nic in nic_devices:
        nic_info = {
            'name': nic.name,
            'connections': []
        }

        connections = get_nic_connections(nb, nic)
        for conn in connections:
            switch_id = conn['switch_id']
            if switch_id not in switch_cache:
                switch_cache[switch_id] = get_switch_details(nb, switch_id)

            switch_details = switch_cache[switch_id]
            nic_info['connections'].append({
                'interface': conn['interface_name'],
                'switch_name': switch_details['name'],
                'switch_type': switch_details['type'],
                'switch_role': switch_details['role'],
                'switch_port': conn['switch_port'],
            })

        if nic_info['connections']:  # Only add NICs with connections
            server_info['nics'].append(nic_info)

    return server_info


def format_table(servers_data: List[Dict[str, Any]]):
    """Format server connections as compact table"""
    if not servers_data:
        print("No servers found")
        return

    for server in servers_data:
        print(f"\n{'='*80}")
        print(f"Server: {server['name']}")
        if server['hostname'] != 'N/A':
            print(f"Hostname: {server['hostname']}")
        print(f"Site: {server['site']} | Role: {server['role']}")
        print(f"{'='*80}")

        if not server['nics']:
            print("  No NIC connections found")
            continue

        for nic in server['nics']:
            print(f"\n  NIC: {nic['name']}")
            for conn in nic['connections']:
                print(f"    Port {conn['interface']:<10} -> {conn['switch_name']:<25} ({conn['switch_port']})")

        # Summary of unique switches
        unique_switches = set()
        for nic in server['nics']:
            for conn in nic['connections']:
                unique_switches.add(f"{conn['switch_name']} ({conn['switch_role']})")

        if unique_switches:
            print(f"\n  Connected to {len(unique_switches)} switch(es):")
            for sw in sorted(unique_switches):
                print(f"    - {sw}")


def format_detailed(servers_data: List[Dict[str, Any]]):
    """Format server connections with full details"""
    if not servers_data:
        print("No servers found")
        return

    for server in servers_data:
        print(f"\n{'='*100}")
        print(f"SERVER DETAILS")
        print(f"{'='*100}")
        print(f"  Device Name:  {server['name']}")
        print(f"  Hostname:     {server['hostname']}")
        print(f"  Site:         {server['site']}")
        print(f"  Role:         {server['role']}")
        print(f"  Device ID:    {server['id']}")

        if not server['nics']:
            print(f"\n  No NIC devices or connections found")
            continue

        print(f"\n{'='*100}")
        print(f"NETWORK CONNECTIONS")
        print(f"{'='*100}")

        for nic in server['nics']:
            print(f"\n  NIC Device: {nic['name']}")
            print(f"  {'-'*90}")

            for conn in nic['connections']:
                print(f"    Interface:    {conn['interface']}")
                print(f"    Switch:       {conn['switch_name']}")
                print(f"    Switch Type:  {conn['switch_type']}")
                print(f"    Switch Role:  {conn['switch_role']}")
                print(f"    Switch Port:  {conn['switch_port']}")
                print()

        # Connection summary
        print(f"\n{'='*100}")
        print(f"CONNECTION SUMMARY")
        print(f"{'='*100}")

        switch_summary = {}
        for nic in server['nics']:
            for conn in nic['connections']:
                sw_name = conn['switch_name']
                if sw_name not in switch_summary:
                    switch_summary[sw_name] = {
                        'type': conn['switch_type'],
                        'role': conn['switch_role'],
                        'ports': []
                    }
                switch_summary[sw_name]['ports'].append(conn['switch_port'])

        for sw_name, details in sorted(switch_summary.items()):
            print(f"  {sw_name}")
            print(f"    Type:  {details['type']}")
            print(f"    Role:  {details['role']}")
            print(f"    Ports: {', '.join(sorted(set(details['ports'])))}")
            print()


def format_json(servers_data: List[Dict[str, Any]]):
    """Format server connections as JSON"""
    print(json.dumps(servers_data, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description='Get server network connections (switch/port mappings)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get connections by device name
  %(prog)s F.1.1.A1.7

  # Get connections by hostname
  %(prog)s mkskof2-5gc-lab-d6w5t --by-hostname

  # Show all servers in a cluster
  %(prog)s mkskof2-5gc-lab --cluster

  # Get detailed output
  %(prog)s F.1.1.A1.7 --format detailed

  # JSON output for scripting
  %(prog)s mkskof2-5gc-lab --cluster --format json
        """
    )

    parser.add_argument('identifier',
                       help='Server device name, hostname, or cluster name')
    parser.add_argument('--by-hostname', action='store_true',
                       help='Treat identifier as hostname instead of device name')
    parser.add_argument('--cluster', action='store_true',
                       help='Treat identifier as cluster name, show all servers')
    parser.add_argument('--site',
                       help='Filter by site when searching by hostname')
    parser.add_argument('--format', choices=['table', 'detailed', 'json'], default='table',
                       help='Output format (default: table)')

    args = parser.parse_args()

    # Initialize NetBox client
    nb = get_netbox_client()

    # Get server(s) based on input method
    servers = []

    if args.cluster:
        print(f"Looking up cluster '{args.identifier}'...", file=sys.stderr)
        server_devices = get_servers_by_cluster(nb, args.identifier)
        if not server_devices:
            print(f"Error: No servers found for cluster '{args.identifier}'", file=sys.stderr)
            sys.exit(1)
        servers = server_devices
        print(f"Found {len(servers)} server(s) in cluster", file=sys.stderr)

    elif args.by_hostname:
        print(f"Looking up hostname '{args.identifier}'...", file=sys.stderr)
        server = get_server_by_hostname(nb, args.identifier, args.site)
        if not server:
            print(f"Error: Server with hostname '{args.identifier}' not found", file=sys.stderr)
            if not args.site:
                print("Tip: Try specifying --site to narrow the search", file=sys.stderr)
            sys.exit(1)
        servers = [server]

    else:
        print(f"Looking up device '{args.identifier}'...", file=sys.stderr)
        server = get_server_by_name(nb, args.identifier)
        if not server:
            print(f"Error: Device '{args.identifier}' not found", file=sys.stderr)
            print("Tip: Use --by-hostname if this is a hostname, or --cluster for cluster name", file=sys.stderr)
            sys.exit(1)
        servers = [server]

    # Gather connection information for all servers
    print(f"Gathering connection information...", file=sys.stderr)
    servers_data = []
    for server in servers:
        server_data = gather_server_connections(nb, server)
        servers_data.append(server_data)

    # Format and display output
    if args.format == 'json':
        format_json(servers_data)
    elif args.format == 'detailed':
        format_detailed(servers_data)
    else:
        format_table(servers_data)


if __name__ == '__main__':
    main()
