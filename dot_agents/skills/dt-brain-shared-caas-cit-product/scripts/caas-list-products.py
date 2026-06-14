#!/usr/bin/env python3
"""
CaaS List Products - List all available CaaS products from GitLab repository
Usage: caas-list-products.py [--type TYPE] [--latest] [--format FORMAT]
"""

import argparse
import os
import sys
from typing import Dict, List

# Add script directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from caas_common import (
    CaaSBundlesClient,
    output_results,
    format_json,
)


def get_latest_per_product(products: List[Dict]) -> List[Dict]:
    """Filter to show only the latest version of each product base name"""
    latest: Dict[str, Dict] = {}

    for product in products:
        # Extract base name (without version)
        name = product['name']
        version = product['version']
        base_name = name.rsplit('-', 1)[0] if version else name
        key = f"{product['type']}:{base_name}"

        if key not in latest:
            latest[key] = product
        else:
            current_version = latest[key]['version']
            if CaaSBundlesClient.compare_versions(version, current_version) > 0:
                latest[key] = product

    return sorted(latest.values(), key=lambda x: (x['type'], x['name']))


def main():
    parser = argparse.ArgumentParser(
        description='List all available CaaS products'
    )
    parser.add_argument(
        '--type',
        help='Filter by product type (baremetal, caas, mgmt-cluster, dtit, mom, support)'
    )
    parser.add_argument(
        '--latest',
        action='store_true',
        help='Show only the latest version per product'
    )
    parser.add_argument(
        '--ref',
        default='master',
        help='Git branch/tag/commit (default: main)'
    )
    parser.add_argument(
        '--format',
        choices=['table', 'json', 'markdown'],
        default='table',
        help='Output format (default: table)'
    )

    args = parser.parse_args()

    # Initialize client
    client = CaaSBundlesClient(ref=args.ref)

    # Validate product type if specified
    if args.type:
        valid_types = client.list_product_types()
        if args.type not in valid_types:
            print(f"Error: Invalid product type: {args.type}", file=sys.stderr)
            print(f"Available types: {', '.join(valid_types)}", file=sys.stderr)
            sys.exit(1)

    # Get products
    products = client.list_products(product_type=args.type)

    if not products:
        print("No products found", file=sys.stderr)
        sys.exit(0)

    # Filter to latest if requested
    if args.latest:
        products = get_latest_per_product(products)

    # Output results
    headers = ['PRODUCT_TYPE', 'PRODUCT_NAME', 'VERSION']
    keys = ['type', 'name', 'version']
    output_results(products, headers, keys, args.format)


if __name__ == '__main__':
    main()
