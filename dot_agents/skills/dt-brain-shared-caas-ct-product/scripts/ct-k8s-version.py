#!/usr/bin/env python3
"""
CT-CaaS Kubernetes Version - Show the Kubernetes version used by CT-CaaS bundles
Usage: ct-k8s-version.py <major-version> [--type TYPE] [--format FORMAT]

Shows spec.k8sVersion for the latest bundle in each minor version line.

Examples:
    ct-k8s-version.py 35
    ct-k8s-version.py 34 --type netbox
    ct-k8s-version.py 35 --format json
"""

import argparse
import os
import sys
from collections import defaultdict
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ct_common import (
    CTBundlesClient,
    format_json,
    format_table,
    format_markdown_table,
    output_results,
)


def get_latest_per_minor(bundles: List[Dict], client: CTBundlesClient) -> List[Dict]:
    """Group bundles by major.minor and keep only the latest patch version."""
    groups: Dict[str, Dict] = {}
    for b in bundles:
        version = b['version']
        parts = version.split('.')
        if len(parts) < 3:
            continue
        minor_key = f"{parts[0]}.{parts[1]}"
        if minor_key not in groups:
            groups[minor_key] = b
        else:
            if client.compare_versions(version, groups[minor_key]['version']) > 0:
                groups[minor_key] = b
    return [groups[k] for k in sorted(groups.keys(),
            key=lambda x: [int(n) for n in x.split('.')])]


def main():
    parser = argparse.ArgumentParser(
        description='Show the Kubernetes version used by CT-CaaS bundles for a given major version'
    )
    parser.add_argument(
        'major_version',
        help='CT-CaaS major version number (e.g., 35)'
    )
    parser.add_argument(
        '--type',
        help='Bundle type to query (netbox, openstack). Default: all types'
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
    major = args.major_version.strip()

    client = CTBundlesClient(ref=args.ref)

    bundles = client.list_bundles(bundle_type=args.type)

    # Filter to requested major version
    version_prefix = f"{major}."
    bundles = [b for b in bundles if b['version'].startswith(version_prefix)]

    if not bundles:
        print(f"No bundles found for major version {major}", file=sys.stderr)
        sys.exit(1)

    # Group by bundle base name (e.g., netbox-workload)
    by_base: Dict[str, List[Dict]] = defaultdict(list)
    for b in bundles:
        version = b['version']
        base = b['name'][:b['name'].rfind('-' + version)] if version else b['name']
        by_base[base].append(b)

    results = []
    for base_name in sorted(by_base.keys()):
        latest_per_minor = get_latest_per_minor(by_base[base_name], client)
        for b in latest_per_minor:
            bundle_data = client.get_bundle(b['name'])
            if not bundle_data:
                continue
            k8s_ver = bundle_data.get('spec', {}).get('k8sVersion', 'N/A')
            results.append({
                'bundle': b['name'],
                'minor': '.'.join(b['version'].split('.')[:2]),
                'k8s_version': k8s_ver,
            })

    if not results:
        print(f"Could not retrieve Kubernetes versions for major version {major}",
              file=sys.stderr)
        sys.exit(1)

    if args.format == 'json':
        print(format_json(results))
    else:
        headers = ['BUNDLE (latest patch)', 'MINOR', 'KUBERNETES VERSION']
        keys = ['bundle', 'minor', 'k8s_version']
        output_results(results, headers, keys, args.format)


if __name__ == '__main__':
    main()
