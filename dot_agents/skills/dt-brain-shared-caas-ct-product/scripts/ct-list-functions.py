#!/usr/bin/env python3
"""
CT-CaaS List Functions - List all functions for a specific bundle
Usage: ct-list-functions.py <bundle-name> [--format FORMAT]
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ct_common import (
    CTBundlesClient,
    output_results,
)


def main():
    parser = argparse.ArgumentParser(
        description='List all functions for a specific CT-CaaS bundle'
    )
    parser.add_argument(
        'bundle',
        help='Bundle name (e.g., netbox-workload-34.0.19)'
    )
    parser.add_argument(
        '--ref',
        default='main',
        help='Git branch/tag/commit (default: main)'
    )
    parser.add_argument(
        '--format',
        choices=['table', 'json', 'markdown'],
        default='table',
        help='Output format (default: table)'
    )

    args = parser.parse_args()

    client = CTBundlesClient(ref=args.ref)

    functions = client.get_bundle_functions(args.bundle)

    if not functions:
        print(f"No functions found for bundle: {args.bundle}", file=sys.stderr)
        sys.exit(1)

    headers = ['FUNCTION', 'VERSION']
    keys = ['name', 'version']
    output_results(functions, headers, keys, args.format)


if __name__ == '__main__':
    main()
