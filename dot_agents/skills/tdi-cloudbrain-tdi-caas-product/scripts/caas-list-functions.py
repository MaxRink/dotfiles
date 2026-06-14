#!/usr/bin/env python3
"""
CaaS List Functions - List all functions for a specific product
Usage: caas-list-functions.py <product-name> [--format FORMAT]
"""

import argparse
import sys

from caas_common import (
    CaaSBundlesClient,
    output_results,
)


def main():
    parser = argparse.ArgumentParser(
        description='List all functions for a specific CaaS product'
    )
    parser.add_argument(
        'product',
        help='Product name (e.g., baremetal-cluster-34.6.10)'
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

    # Get functions for product
    functions = client.get_product_functions(args.product)

    if not functions:
        print(f"No functions found for product: {args.product}", file=sys.stderr)
        sys.exit(1)

    # Output results
    headers = ['FUNCTION', 'VERSION']
    keys = ['name', 'version']
    output_results(functions, headers, keys, args.format)


if __name__ == '__main__':
    main()
