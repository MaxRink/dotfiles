#!/usr/bin/env python3
"""
CT-CaaS List Bundles - List all available CT-CaaS bundles from GitLab repository
Usage: ct-list-bundles.py [--type TYPE] [--latest] [--format FORMAT]
"""

import argparse
import os
import sys
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ct_common import (
    CTBundlesClient,
    output_results,
    format_json,
)


def get_latest_per_bundle(bundles: List[Dict]) -> List[Dict]:
    """Filter to show only the latest version of each bundle base name"""
    latest: Dict[str, Dict] = {}

    for bundle in bundles:
        name = bundle['name']
        version = bundle['version']
        # Extract base name (e.g., netbox-workload from netbox-workload-34.0.19)
        base_name = name[:name.rfind('-' + version)] if version else name
        key = f"{bundle['type']}:{base_name}"

        if key not in latest:
            latest[key] = bundle
        else:
            current_version = latest[key]['version']
            if CTBundlesClient.compare_versions(version, current_version) > 0:
                latest[key] = bundle

    return sorted(latest.values(), key=lambda x: (x['type'], x['name']))


def main():
    parser = argparse.ArgumentParser(
        description='List all available CT-CaaS bundles'
    )
    parser.add_argument(
        '--type',
        help='Filter by bundle type (netbox, openstack)'
    )
    parser.add_argument(
        '--latest',
        action='store_true',
        help='Show only the latest version per bundle'
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

    # Validate bundle type
    if args.type:
        valid_types = client.list_bundle_types()
        if args.type not in valid_types:
            print(f"Error: Invalid bundle type: {args.type}", file=sys.stderr)
            print(f"Available types: {', '.join(valid_types)}", file=sys.stderr)
            sys.exit(1)

    bundles = client.list_bundles(bundle_type=args.type)

    if not bundles:
        print("No bundles found", file=sys.stderr)
        sys.exit(0)

    if args.latest:
        bundles = get_latest_per_bundle(bundles)

    headers = ['BUNDLE_TYPE', 'BUNDLE_NAME', 'VERSION']
    keys = ['type', 'name', 'version']
    output_results(bundles, headers, keys, args.format)


if __name__ == '__main__':
    main()
