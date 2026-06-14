#!/usr/bin/env python3
"""
NetBox Get Cluster Script
Usage: netbox-get-cluster.py <cluster-id-or-name> [options]

Retrieves cluster details from NetBox. Use --product to include CaaS product info.
"""

import os
import sys
import json
import argparse
import subprocess
from typing import Dict, Any, List

from netbox_common import get_netbox_client


def get_cluster_by_id(nb, cluster_id: int) -> Any:
    """Get cluster by ID"""
    try:
        cluster = nb.virtualization.clusters.get(cluster_id)
        if not cluster:
            print(f"Error: Cluster with ID {cluster_id} not found", file=sys.stderr)
            sys.exit(1)
        return cluster
    except Exception as e:
        print(f"Error: Failed to get cluster by ID: {e}", file=sys.stderr)
        sys.exit(1)


def get_cluster_by_name(nb, name: str) -> Any:
    """Get cluster by name"""
    try:
        clusters = list(nb.virtualization.clusters.filter(name=name))
        if not clusters:
            print(f"Error: Cluster with name '{name}' not found", file=sys.stderr)
            sys.exit(1)
        if len(clusters) > 1:
            print(f"Warning: Multiple clusters found with name '{name}', using first one", file=sys.stderr)
        return clusters[0]
    except Exception as e:
        print(f"Error: Failed to get cluster by name: {e}", file=sys.stderr)
        sys.exit(1)


def get_cluster_vms(nb, cluster_id: int) -> List[Dict[str, Any]]:
    """Get virtual machines in cluster"""
    try:
        vms = nb.virtualization.virtual_machines.filter(cluster_id=cluster_id)
        result = []
        for vm in vms:
            vm_data = {
                'id': vm.id,
                'name': vm.name,
                'status': vm.status.label if vm.status else None,
                'vcpus': vm.vcpus,
                'memory': vm.memory,
                'disk': vm.disk,
                'primary_ip': str(vm.primary_ip) if vm.primary_ip else None,
                'description': vm.description if vm.description else '',
            }
            result.append(vm_data)
        return result
    except Exception as e:
        print(f"Warning: Failed to get cluster VMs: {e}", file=sys.stderr)
        return []


def get_cluster_devices(nb, cluster_id: int) -> List[Dict[str, Any]]:
    """Get devices (physical servers) in cluster"""
    try:
        devices = nb.dcim.devices.filter(cluster_id=cluster_id)
        result = []
        for device in devices:
            device_data = {
                'id': device.id,
                'name': device.name,
                'device_type': device.device_type.display if device.device_type else None,
                'role': device.device_role.name if device.device_role else None,
                'status': device.status.label if device.status else None,
                'site': device.site.name if device.site else None,
                'rack': device.rack.name if device.rack else None,
                'primary_ip': str(device.primary_ip) if device.primary_ip else None,
            }
            result.append(device_data)
        return result
    except Exception as e:
        print(f"Warning: Failed to get cluster devices: {e}", file=sys.stderr)
        return []


def get_cloud_id(cluster: Any) -> str:
    """Extract cloud_id from custom_fields.arbitrary_data"""
    if hasattr(cluster, 'custom_fields') and cluster.custom_fields:
        arbitrary_data = cluster.custom_fields.get('arbitrary_data')
        if arbitrary_data and isinstance(arbitrary_data, dict):
            caas_cluster = arbitrary_data.get('Caas Cluster')
            if caas_cluster and isinstance(caas_cluster, dict):
                spec = caas_cluster.get('spec')
                if spec and isinstance(spec, dict):
                    return spec.get('cloud_id', '')
    return ''


def format_site_with_cloud_id(cluster: Any) -> str:
    """Format site - prefer cloud_id if available"""
    cloud_id = get_cloud_id(cluster)
    if cloud_id:
        return cloud_id
    return cluster.site.name if cluster.site else '-'


def extract_product_info(cluster: Any) -> Dict[str, str]:
    """Extract product information from cluster custom fields"""
    product_info = {
        'product_name': None,
        'product_version': None,
        'product_type': None,
        'k8s_version': None,
    }

    if hasattr(cluster, 'custom_fields') and cluster.custom_fields:
        product_info['k8s_version'] = cluster.custom_fields.get('version')

        arbitrary_data = cluster.custom_fields.get('arbitrary_data', {})
        if arbitrary_data:
            caas_product = arbitrary_data.get('Caas Product', {})
            if caas_product:
                spec = caas_product.get('spec', {})
                product_info['product_version'] = spec.get('version')
                product_info['product_type'] = spec.get('productType')

            config_summary = arbitrary_data.get('Active Configuration Summary', {})
            if config_summary:
                if not product_info['k8s_version']:
                    product_info['k8s_version'] = config_summary.get('Kubernetes Version')
                if not product_info['product_version']:
                    product_info['product_version'] = config_summary.get('Caas Product Version')

    if product_info['product_type'] and product_info['product_version']:
        product_info['product_name'] = f"{product_info['product_type']}-{product_info['product_version']}"

    return product_info


def get_caas_product_info(product_name: str) -> str:
    """Get CaaS product information using the caas-cit-product skill"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        skills_dir = os.path.dirname(os.path.dirname(script_dir))
        skill_dir = os.path.join(skills_dir, 'caas-cit-product')
        script_path = os.path.join(skill_dir, 'scripts', 'caas-product-info.py')

        if not os.path.exists(script_path):
            return f"⚠ CaaS product info script not found at {script_path}"

        result = subprocess.run(
            [script_path, product_name],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return result.stdout
        else:
            return f"⚠ Failed to get product info (exit code {result.returncode})"

    except subprocess.TimeoutExpired:
        return "⚠ Product info query timed out"
    except Exception as e:
        return f"⚠ Error getting product info: {e}"


def format_cluster_detailed(cluster: Any, vms: List[Dict[str, Any]] = None,
                           devices: List[Dict[str, Any]] = None, show_product: bool = False):
    """Format cluster details"""
    print("=" * 80)
    print(f"Cluster: {cluster.name}")
    print("=" * 80)
    print()

    # Basic information
    print("BASIC INFORMATION")
    print("-" * 80)
    print(f"  ID:          {cluster.id}")
    print(f"  Name:        {cluster.name}")
    print(f"  Type:        {cluster.type.name if cluster.type else '-'}")
    print(f"  Group:       {cluster.group.name if cluster.group else '-'}")
    print(f"  Site:        {format_site_with_cloud_id(cluster)}")
    print(f"  Status:      {cluster.status.label if cluster.status else '-'}")
    print(f"  Device Count: {cluster.device_count if hasattr(cluster, 'device_count') else 0}")
    print(f"  VM Count:    {cluster.virtual_machine_count if hasattr(cluster, 'virtual_machine_count') else 0}")
    print()

    # Kubernetes & Product Version (always show if available)
    product_info = extract_product_info(cluster)
    if product_info['k8s_version'] or product_info['product_version']:
        print("KUBERNETES & PRODUCT")
        print("-" * 80)
        if product_info['k8s_version']:
            print(f"  Kubernetes Version:  {product_info['k8s_version']}")
        if product_info['product_version']:
            print(f"  CaaS Product:        {product_info['product_version']}")
        if product_info['product_type']:
            print(f"  Product Type:        {product_info['product_type']}")
        print()

    # Description
    if cluster.description:
        print("DESCRIPTION")
        print("-" * 80)
        print(f"  {cluster.description}")
        print()

    # Comments
    if cluster.comments:
        print("COMMENTS")
        print("-" * 80)
        print(f"  {cluster.comments}")
        print()

    # Tags
    if cluster.tags:
        print("TAGS")
        print("-" * 80)
        tags = [tag.name for tag in cluster.tags]
        print(f"  {', '.join(tags)}")
        print()

    # Custom fields
    if hasattr(cluster, 'custom_fields') and cluster.custom_fields:
        print("CUSTOM FIELDS")
        print("-" * 80)
        for key, value in cluster.custom_fields.items():
            if value and key != 'arbitrary_data':  # Skip verbose arbitrary_data
                print(f"  {key}: {value}")
        print()

    # Devices (physical servers)
    if devices is not None:
        print("DEVICES (Physical Servers)")
        print("-" * 80)
        if devices:
            print(f"  {'ID':<6} {'Name':<20} {'Type':<25} {'Role':<15} {'Status':<10} {'Primary IP'}")
            print("  " + "-" * 90)
            for device in devices:
                print(f"  {device['id']:<6} {device['name']:<20} {(device['device_type'] or '-'):<25} "
                      f"{(device['role'] or '-'):<15} {(device['status'] or '-'):<10} {device['primary_ip'] or '-'}")
            print()
            print(f"  Total Devices: {len(devices)}")
        else:
            print("  No devices in this cluster")
        print()

    # Virtual machines
    if vms is not None:
        print("VIRTUAL MACHINES")
        print("-" * 80)
        if vms:
            print(f"  {'ID':<6} {'Name':<30} {'Status':<12} {'vCPUs':<7} {'Memory (MB)':<12} {'Primary IP'}")
            print("  " + "-" * 78)
            for vm in vms:
                print(f"  {vm['id']:<6} {vm['name']:<30} {vm['status'] or '-':<12} "
                      f"{vm['vcpus'] or '-':<7} {vm['memory'] or '-':<12} {vm['primary_ip'] or '-'}")
            print()
            print(f"  Total VMs: {len(vms)}")
        else:
            print("  No virtual machines in this cluster")
        print()

    # CaaS Product Details (only with --product flag)
    if show_product:
        product_info = extract_product_info(cluster)
        if product_info['product_name']:
            print("=" * 80)
            print("CAAS PRODUCT DETAILS")
            print("=" * 80)
            print()
            product_details = get_caas_product_info(product_info['product_name'])
            print(product_details)
        else:
            print("Note: No CaaS product information available for this cluster")
            print()

    # URL
    if hasattr(cluster, 'url'):
        print("URL")
        print("-" * 80)
        print(f"  {cluster.url}")
        print()


def format_cluster_json(cluster: Any, vms: List[Dict[str, Any]] = None,
                       devices: List[Dict[str, Any]] = None, show_product: bool = False):
    """Format cluster as JSON"""
    product_info = extract_product_info(cluster)

    cluster_data = {
        'id': cluster.id,
        'name': cluster.name,
        'type': cluster.type.name if cluster.type else None,
        'group': cluster.group.name if cluster.group else None,
        'site': format_site_with_cloud_id(cluster),
        'status': cluster.status.label if cluster.status else None,
        'device_count': cluster.device_count if hasattr(cluster, 'device_count') else 0,
        'vm_count': cluster.virtual_machine_count if hasattr(cluster, 'virtual_machine_count') else 0,
        'k8s_version': product_info['k8s_version'],
        'product_version': product_info['product_version'],
        'product_type': product_info['product_type'],
        'description': cluster.description if cluster.description else '',
        'comments': cluster.comments if cluster.comments else '',
        'tags': [tag.name for tag in cluster.tags] if cluster.tags else [],
        'custom_fields': {k: v for k, v in (cluster.custom_fields or {}).items() if k != 'arbitrary_data'},
        'url': cluster.url if hasattr(cluster, 'url') else None,
    }

    if devices is not None:
        cluster_data['devices'] = devices

    if vms is not None:
        cluster_data['virtual_machines'] = vms

    print(json.dumps(cluster_data, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description='Get NetBox cluster details',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get cluster by ID
  %(prog)s 123

  # Get cluster by name
  %(prog)s "my-cluster-name"

  # Show cluster with VMs
  %(prog)s 123 --show-vms

  # Get JSON output
  %(prog)s 123 --format json

  # Show devices (physical servers)
  %(prog)s 123 --show-devices

  # Include full CaaS product details
  %(prog)s cluster-name --product
        """
    )

    parser.add_argument('cluster', help='Cluster ID or name')
    parser.add_argument('--format', choices=['detailed', 'json'], default='detailed',
                       help='Output format (default: detailed)')
    parser.add_argument('--show-vms', action='store_true',
                       help='Include list of virtual machines')
    parser.add_argument('--show-devices', action='store_true',
                       help='Include list of devices (physical servers)')
    parser.add_argument('--product', action='store_true',
                       help='Include full CaaS product details (functions, versions, actions)')
    parser.add_argument('--id', action='store_true', dest='use_id',
                       help='Treat argument as cluster ID (faster)')
    parser.add_argument('--name', action='store_true', dest='use_name',
                       help='Treat argument as cluster name')

    args = parser.parse_args()

    # Initialize NetBox client
    nb = get_netbox_client()

    # Get cluster
    if args.use_id or args.cluster.isdigit():
        cluster = get_cluster_by_id(nb, int(args.cluster))
    else:
        cluster = get_cluster_by_name(nb, args.cluster)

    # Get devices if requested
    devices = None
    if args.show_devices:
        devices = get_cluster_devices(nb, cluster.id)

    # Get VMs if requested
    vms = None
    if args.show_vms:
        vms = get_cluster_vms(nb, cluster.id)

    # Format output
    if args.format == 'json':
        format_cluster_json(cluster, vms, devices, show_product=args.product)
    else:
        format_cluster_detailed(cluster, vms, devices, show_product=args.product)


if __name__ == '__main__':
    main()
