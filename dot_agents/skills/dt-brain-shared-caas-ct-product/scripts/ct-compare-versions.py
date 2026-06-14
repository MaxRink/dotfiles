#!/usr/bin/env python3
"""
CT-CaaS Compare Versions - Compare component versions between two bundle versions
Usage: ct-compare-versions.py <bundle-1> <bundle-2> [--format FORMAT] [--diff-only] [--images]
"""

import argparse
import os
import sys
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ct_common import (
    CTBundlesClient,
    OCIRegistryClient,
    format_json,
    format_table,
    format_markdown_table,
)

# Import image version extraction
import importlib.util

_script_dir = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("image_versions", os.path.join(_script_dir, "ct-image-versions.py"))
_image_versions_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_image_versions_module)
get_image_versions = _image_versions_module.get_image_versions


def compare_bundles(client: CTBundlesClient, oci_client: OCIRegistryClient,
                    bundle1: str, bundle2: str, diff_only: bool = False) -> Dict:
    """Compare component versions between two bundles"""
    # Get image versions for both
    versions1 = get_image_versions(client, oci_client, bundle1)
    versions2 = get_image_versions(client, oci_client, bundle2)

    # Build maps keyed by "function|component"
    def build_map(versions):
        result = {}
        for v in versions:
            comp = v.get('component', '')
            if not comp:
                continue
            key = f"{v.get('function', 'unknown')}|{comp}"
            result[key] = v
        return result

    map1 = build_map(versions1)
    map2 = build_map(versions2)

    all_keys = sorted(set(list(map1.keys()) + list(map2.keys())))

    comparisons = []
    for key in all_keys:
        v1 = map1.get(key)
        v2 = map2.get(key)

        func = (v1 or v2).get('function', key.split('|')[0])
        comp = (v1 or v2).get('component', key.split('|')[1] if '|' in key else '')

        img1 = v1.get('image_version', '-') if v1 else '-'
        img2 = v2.get('image_version', '-') if v2 else '-'
        tv1 = v1.get('type_version', '-') if v1 else '-'
        tv2 = v2.get('type_version', '-') if v2 else '-'

        if v1 is None:
            status = 'added'
        elif v2 is None:
            status = 'removed'
        elif img1 == img2:
            status = 'same'
        else:
            status = 'changed'

        if diff_only and status == 'same':
            continue

        comparisons.append({
            'function': func,
            'component': comp,
            'type_version1': tv1,
            'type_version2': tv2,
            'image_version1': img1,
            'image_version2': img2,
            'status': status
        })

    diff_count = sum(1 for c in comparisons if c['status'] != 'same')
    total_count = len(comparisons) if not diff_only else diff_count

    return {
        'bundle1': bundle1,
        'bundle2': bundle2,
        'comparisons': comparisons,
        'diff_count': diff_count,
        'total_count': len(all_keys)
    }


def format_comparison(result: Dict, fmt: str = 'table') -> str:
    """Format comparison results"""
    if fmt == 'json':
        return format_json(result)

    b1 = result['bundle1']
    b2 = result['bundle2']
    comparisons = result['comparisons']

    lines = []
    lines.append(f"Comparing: {b1} vs {b2}")
    lines.append("")

    if fmt == 'markdown':
        lines.append(f"| Function | Component | {b1} | {b2} | Status |")
        lines.append("|----------|-----------|" + "-" * (len(b1) + 2) + "|" + "-" * (len(b2) + 2) + "|--------|")
        for c in comparisons:
            lines.append(
                f"| {c['function']} | {c['component']} | {c['image_version1']} "
                f"| {c['image_version2']} | {c['status']} |"
            )
    else:  # table
        headers = ['FUNCTION', 'COMPONENT', b1, b2, 'STATUS']
        rows = []
        for c in comparisons:
            indicator = {'changed': '*', 'added': '+', 'removed': '-'}.get(c['status'], ' ')
            rows.append([
                c['function'],
                c['component'],
                c['image_version1'],
                c['image_version2'],
                f"{indicator}{c['status']}"
            ])
        lines.append(format_table(headers, rows))

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Compare component versions between two CT-CaaS bundles'
    )
    parser.add_argument(
        'bundle1',
        help='First bundle (e.g., netbox-workload-34.0.19)'
    )
    parser.add_argument(
        'bundle2',
        help='Second bundle (e.g., netbox-workload-33.0.0)'
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
    parser.add_argument(
        '--diff-only',
        action='store_true',
        help='Show only components with version differences'
    )

    args = parser.parse_args()

    client = CTBundlesClient(ref=args.ref)
    oci_client = OCIRegistryClient()

    # Auto-sort: older version first
    v1 = CTBundlesClient._extract_version(args.bundle1)
    v2 = CTBundlesClient._extract_version(args.bundle2)
    bundle1, bundle2 = args.bundle1, args.bundle2

    if v1 and v2 and CTBundlesClient.compare_versions(v1, v2) > 0:
        bundle1, bundle2 = bundle2, bundle1
        print(f"Note: Reordered to compare from older ({bundle1}) to newer ({bundle2})", file=sys.stderr)

    result = compare_bundles(client, oci_client, bundle1, bundle2, diff_only=args.diff_only)

    print(format_comparison(result, args.format))

    # Print summary
    diff_count = result['diff_count']
    total_count = result['total_count']
    print("", file=sys.stderr)
    if diff_count == 0:
        print(f"Summary: No component version differences found between {bundle1} and {bundle2}.", file=sys.stderr)
        print("This is OK - the bundles may differ only in Kubernetes version or other metadata.", file=sys.stderr)
    else:
        print(f"Summary: {diff_count} of {total_count} components have version differences.", file=sys.stderr)


if __name__ == '__main__':
    main()
