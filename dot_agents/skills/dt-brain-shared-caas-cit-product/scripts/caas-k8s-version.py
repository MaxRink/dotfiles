#!/usr/bin/env python3
"""
CaaS Kubernetes Version - Show the Kubernetes version used by CaaS products
Usage: caas-k8s-version.py <major-version> [--type TYPE] [--format FORMAT]

Shows spec.kubernetesVersion for the latest product in each minor version line.

Examples:
    caas-k8s-version.py 35
    caas-k8s-version.py 34 --type baremetal
    caas-k8s-version.py 35 --format json
"""

import argparse
import os
import re
import sys
from collections import defaultdict
from typing import Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from caas_common import (
    CaaSBundlesClient,
    format_json,
    format_table,
    format_markdown_table,
    output_results,
)


def get_latest_per_minor(products: List[Dict], client: CaaSBundlesClient) -> List[Dict]:
    """Group products by major.minor and keep only the latest patch version."""
    groups: Dict[str, Dict] = {}
    for p in products:
        version = p['version']
        parts = version.split('.')
        if len(parts) < 3:
            continue
        minor_key = f"{parts[0]}.{parts[1]}"
        if minor_key not in groups:
            groups[minor_key] = p
        else:
            if client.compare_versions(version, groups[minor_key]['version']) > 0:
                groups[minor_key] = p
    return [groups[k] for k in sorted(groups.keys(),
            key=lambda x: [int(n) for n in x.split('.')])]


def main():
    parser = argparse.ArgumentParser(
        description='Show the Kubernetes version used by CaaS products for a given major version'
    )
    parser.add_argument(
        'major_version',
        help='CaaS major version number (e.g., 35)'
    )
    parser.add_argument(
        '--type',
        default='baremetal',
        help='Product type to query (default: baremetal)'
    )
    parser.add_argument(
        '--all-types',
        action='store_true',
        help='Show all product types, not just one'
    )
    parser.add_argument(
        '--ref',
        default='master',
        help='Git branch/tag/commit (default: master)'
    )
    parser.add_argument(
        '--format',
        choices=['table', 'json', 'markdown'],
        default='table',
        help='Output format (default: table)'
    )

    args = parser.parse_args()
    major = args.major_version.strip()

    client = CaaSBundlesClient(ref=args.ref)

    if args.all_types:
        products = client.list_products()
    else:
        products = client.list_products(product_type=args.type)

    # Filter to requested major version
    version_prefix = f"{major}."
    products = [p for p in products if p['version'].startswith(version_prefix)]

    if not products:
        print(f"No products found for major version {major}", file=sys.stderr)
        sys.exit(1)

    # Group by product base name (e.g., baremetal-cluster)
    by_base: Dict[str, List[Dict]] = defaultdict(list)
    for p in products:
        version = p['version']
        base = p['name'][:p['name'].rfind('-' + version)] if version else p['name']
        by_base[base].append(p)

    results = []
    for base_name in sorted(by_base.keys()):
        latest_per_minor = get_latest_per_minor(by_base[base_name], client)
        for p in latest_per_minor:
            product_data = client.get_product(p['name'])
            if not product_data:
                continue
            k8s_ver = product_data.get('spec', {}).get('kubernetesVersion', 'N/A')
            results.append({
                'product': p['name'],
                'minor': '.'.join(p['version'].split('.')[:2]),
                'k8s_version': k8s_ver,
            })

    if not results:
        print(f"Could not retrieve Kubernetes versions for major version {major}",
              file=sys.stderr)
        sys.exit(1)

    if args.format == 'json':
        print(format_json(results))
    else:
        headers = ['PRODUCT (latest patch)', 'MINOR', 'KUBERNETES VERSION']
        keys = ['product', 'minor', 'k8s_version']
        output_results(results, headers, keys, args.format)


if __name__ == '__main__':
    main()
