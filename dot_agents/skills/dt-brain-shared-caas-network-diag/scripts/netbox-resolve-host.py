#!/usr/bin/env python3
"""
Resolve a server hostname to cluster name, TOR switches, and switch details via NetBox.

Usage: netbox-resolve-host.py <hostname> [options]

Output includes:
- Cluster name (for sshuttle)
- TOR switch names, IPs, vendor/type
- Server-to-switch port mappings
"""

import sys
import os
import json
import argparse
from typing import List, Dict, Any, Optional

# Add netbox skill scripts to path for shared utilities
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "netbox", "scripts"))
from netbox_common import get_netbox_client


def search_vm_by_hostname(nb, hostname: str) -> Optional[Dict[str, Any]]:
    """Search for a VM matching the hostname, return cluster info."""
    try:
        vms = nb.virtualization.virtual_machines.filter(q=hostname)
        for vm in vms:
            if vm.name == hostname or (
                hasattr(vm, "custom_fields")
                and vm.custom_fields
                and vm.custom_fields.get("hostname") == hostname
            ):
                return {
                    "vm_name": vm.name,
                    "cluster_name": vm.cluster.name if vm.cluster else None,
                    "cluster_id": vm.cluster.id if vm.cluster else None,
                    "site": vm.site.name if vm.site else (
                        vm.cluster.site.name if vm.cluster and hasattr(vm.cluster, "site") and vm.cluster.site else None
                    ),
                }
        # If no exact match, return first result if any
        vms = list(nb.virtualization.virtual_machines.filter(q=hostname))
        if vms:
            vm = vms[0]
            return {
                "vm_name": vm.name,
                "cluster_name": vm.cluster.name if vm.cluster else None,
                "cluster_id": vm.cluster.id if vm.cluster else None,
                "site": vm.site.name if vm.site else None,
            }
        return None
    except Exception as e:
        print(f"Warning: VM search failed: {e}", file=sys.stderr)
        return None


def search_device_by_hostname(nb, hostname: str) -> Optional[Dict[str, Any]]:
    """Search for a device by hostname custom field (cf_hostname), return cluster info."""
    try:
        # Primary: search via cf_hostname custom field filter
        devices = list(nb.dcim.devices.filter(cf_hostname=hostname))
        if not devices:
            # Fallback: general query search
            devices = list(nb.dcim.devices.filter(q=hostname))

        for device in devices:
            cluster_name = None
            # Check cluster attribute (direct API field)
            if hasattr(device, "cluster") and device.cluster:
                cluster_name = device.cluster.name if hasattr(device.cluster, "name") else str(device.cluster)
            # Fallback: check custom_fields
            if not cluster_name and hasattr(device, "custom_fields") and device.custom_fields:
                cluster_name = device.custom_fields.get("cluster")

            hostname_match = False
            if hasattr(device, "custom_fields") and device.custom_fields:
                hostname_match = device.custom_fields.get("hostname") == hostname
            if device.name == hostname or hostname_match or cluster_name:
                return {
                    "device_name": device.name,
                    "device_id": device.id,
                    "cluster_name": cluster_name,
                    "site": device.site.name if device.site else None,
                }
        return None
    except Exception as e:
        print(f"Warning: Device search failed: {e}", file=sys.stderr)
        return None


def get_device_by_name(nb, name: str) -> Optional[Any]:
    """Get a device by exact name."""
    devices = list(nb.dcim.devices.filter(name=name))
    return devices[0] if devices else None


def get_nic_devices(nb, server_device: Any) -> List[Any]:
    """Get NIC child devices for a server."""
    try:
        nic_pattern = f"{server_device.name}.NIC"
        return list(nb.dcim.devices.filter(name__isw=nic_pattern))
    except Exception:
        return []


def get_nic_connections(nb, nic_device: Any) -> List[Dict[str, Any]]:
    """Get switch connections for a NIC device."""
    connections = []
    try:
        interfaces = nb.dcim.interfaces.filter(device_id=nic_device.id)
        for interface in interfaces:
            if hasattr(interface, "link_peers") and interface.link_peers:
                for peer in interface.link_peers:
                    if hasattr(peer, "device") and peer.device:
                        connections.append({
                            "interface": interface.name,
                            "switch_id": peer.device.id,
                            "switch_name": peer.device.name,
                            "switch_port": peer.name,
                        })
    except Exception as e:
        print(f"Warning: Failed to get connections for {nic_device.name}: {e}", file=sys.stderr)
    return connections


def get_switch_info(nb, switch_id: int) -> Dict[str, Any]:
    """Get switch details including IP and vendor."""
    try:
        switch = nb.dcim.devices.get(switch_id)
        primary_ip = None
        if switch.primary_ip:
            primary_ip = str(switch.primary_ip).split("/")[0]  # Remove CIDR notation

        # Detect vendor from device type or manufacturer
        vendor = "unknown"
        device_type_str = ""
        if switch.device_type:
            device_type_str = switch.device_type.display or ""
            if hasattr(switch.device_type, "manufacturer") and switch.device_type.manufacturer:
                mfg = str(switch.device_type.manufacturer).lower()
                if "cisco" in mfg:
                    vendor = "cisco"
                elif "juniper" in mfg:
                    vendor = "juniper"
            if vendor == "unknown":
                dt_lower = device_type_str.lower()
                if "cisco" in dt_lower or "nexus" in dt_lower or "nx-os" in dt_lower:
                    vendor = "cisco"
                elif "juniper" in dt_lower or "junos" in dt_lower or "qfx" in dt_lower or "ex4" in dt_lower:
                    vendor = "juniper"

        return {
            "id": switch.id,
            "name": switch.name,
            "type": device_type_str,
            "role": switch.device_role.name if switch.device_role else "N/A",
            "primary_ip": primary_ip,
            "vendor": vendor,
            "site": switch.site.name if switch.site else None,
        }
    except Exception as e:
        return {
            "id": switch_id, "name": "Unknown", "type": "N/A",
            "role": "N/A", "primary_ip": None, "vendor": "unknown", "site": None,
        }


def resolve_hostname(nb, hostname: str) -> Dict[str, Any]:
    """Full resolution: hostname → cluster + TOR switches with IPs and vendor."""
    result = {
        "hostname": hostname,
        "cluster_name": None,
        "server": None,
        "switches": [],
        "port_mappings": [],
    }

    # Step 1: Find cluster name via VM search
    print(f"Searching VMs for '{hostname}'...", file=sys.stderr)
    vm_info = search_vm_by_hostname(nb, hostname)
    if vm_info:
        result["cluster_name"] = vm_info["cluster_name"]
        result["server"] = vm_info
        print(f"  Found VM: {vm_info['vm_name']} in cluster {vm_info['cluster_name']}", file=sys.stderr)
    else:
        print(f"  No VM found, searching devices...", file=sys.stderr)
        dev_info = search_device_by_hostname(nb, hostname)
        if dev_info:
            result["cluster_name"] = dev_info.get("cluster_name")
            result["server"] = dev_info
            print(f"  Found device: {dev_info['device_name']}", file=sys.stderr)
        else:
            print(f"Error: Hostname '{hostname}' not found in NetBox", file=sys.stderr)
            return result

    # Step 2: Find the physical server device and its TOR connections
    print(f"Looking up physical server connections...", file=sys.stderr)
    server_device = None

    # Primary: search by cf_hostname custom field
    devices = list(nb.dcim.devices.filter(cf_hostname=hostname))
    if devices:
        server_device = devices[0]
    else:
        # Fallback: general query search
        devices = list(nb.dcim.devices.filter(q=hostname))
        for device in devices:
            if hasattr(device, "custom_fields") and device.custom_fields:
                if device.custom_fields.get("hostname") == hostname:
                    server_device = device
                    break
            if device.name == hostname:
                server_device = device
                break

    if not server_device:
        print(f"  Could not find physical server device for switch mapping", file=sys.stderr)
        return result

    result["server"]["device_name"] = server_device.name
    result["server"]["device_id"] = server_device.id

    # Step 3: Get NIC connections → TOR switches
    server_site = server_device.site.name if server_device.site else None
    switch_cache = {}
    nic_devices = get_nic_devices(nb, server_device)
    print(f"  Found {len(nic_devices)} NIC device(s) (server site: {server_site})", file=sys.stderr)

    for nic in nic_devices:
        connections = get_nic_connections(nb, nic)
        for conn in connections:
            switch_id = conn["switch_id"]
            if switch_id not in switch_cache:
                switch_cache[switch_id] = get_switch_info(nb, switch_id)

            # Filter: only include switches at the same site as the server
            sw_info = switch_cache[switch_id]
            if server_site and sw_info.get("site") and sw_info["site"] != server_site:
                continue

            result["port_mappings"].append({
                "nic": nic.name,
                "interface": conn["interface"],
                "switch_name": sw_info["name"],
                "switch_port": conn["switch_port"],
            })

    # Deduplicate switches by name (same physical switch may appear with different virtual contexts)
    seen_names = {}
    for sw in switch_cache.values():
        # Filter: only include switches at the same site as the server
        if server_site and sw.get("site") and sw["site"] != server_site:
            continue
        name = sw["name"]
        if name not in seen_names:
            seen_names[name] = sw
    result["switches"] = list(seen_names.values())
    skipped = len(switch_cache) - len(seen_names) - sum(1 for s in switch_cache.values() if s["name"] in seen_names)
    print(f"  Found {len(result['switches'])} connected switch(es) at site {server_site}", file=sys.stderr)
    cross_site = [s for s in switch_cache.values() if server_site and s.get("site") and s["site"] != server_site]
    if cross_site:
        sites = set(s["site"] for s in cross_site)
        print(f"  Filtered out {len(cross_site)} switch(es) from other site(s): {', '.join(sites)}", file=sys.stderr)

    return result


def format_table(data: Dict[str, Any]):
    """Display results in readable table format."""
    print(f"\n{'='*70}")
    print(f"Hostname: {data['hostname']}")
    print(f"Cluster:  {data['cluster_name'] or 'Unknown'}")
    if data["server"]:
        dev_name = data["server"].get("device_name") or data["server"].get("vm_name", "N/A")
        print(f"Device:   {dev_name}")
    print(f"{'='*70}")

    if data["switches"]:
        print(f"\nTOR Switches:")
        for sw in data["switches"]:
            ip_str = sw["primary_ip"] or "NO IP"
            print(f"  {sw['name']:<30} {ip_str:<18} {sw['vendor']:<10} {sw['type']}")
    else:
        print("\nNo TOR switches found")

    if data["port_mappings"]:
        print(f"\nPort Mappings:")
        for pm in data["port_mappings"]:
            print(f"  {pm['nic']:<20} {pm['interface']:<10} -> {pm['switch_name']:<25} {pm['switch_port']}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Resolve server hostname to cluster and TOR switch info via NetBox",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s hrzagt6-caas-13-dev-7gx8d
  %(prog)s hrzagt6-caas-13-dev-7gx8d --format json
        """,
    )
    parser.add_argument("hostname", help="Server hostname to resolve")
    parser.add_argument("--format", choices=["table", "json"], default="table",
                        help="Output format (default: table)")
    args = parser.parse_args()

    nb = get_netbox_client()
    data = resolve_hostname(nb, args.hostname)

    if args.format == "json":
        print(json.dumps(data, indent=2))
    else:
        format_table(data)

    if not data["cluster_name"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
