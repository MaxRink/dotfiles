#!/usr/bin/env python3
"""
CT-CaaS Bundle Info - Show detailed information about a CT-CaaS bundle
Usage: ct-bundle-info.py <bundle-name> [--format FORMAT]
"""

import argparse
import os
import sys
from typing import Dict, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ct_common import (
    CTBundlesClient,
    format_json,
    format_table,
    format_markdown_table,
)


def format_bundle_info(bundle: Dict[str, Any], bundle_name: str,
                       bundle_type: str, fmt: str = 'table') -> str:
    """Format bundle information for display"""
    if fmt == 'json':
        return format_json(bundle)

    spec = bundle.get('spec', {})
    lines = []

    lines.append(f"Bundle: {bundle_name}")
    lines.append("=" * 60)
    lines.append("")

    # Metadata
    lines.append("## Metadata")
    k8s_version = spec.get('k8sVersion', 'N/A')
    lines.append(f"  Type:              {bundle_type}")
    lines.append(f"  Kubernetes Version: {k8s_version}")
    lines.append("")

    # Functions
    functions = spec.get('functions', [])
    if functions:
        lines.append("## Functions")
        rows = []
        for f in functions:
            ref = f.get('ref', {})
            full_name = ref.get('name', '')
            name, version = CTBundlesClient._split_name_version(full_name)
            rows.append([name, version])

        rows.sort(key=lambda x: x[0])

        if fmt == 'markdown':
            lines.append(format_markdown_table(['Function', 'Version'], rows))
        else:
            lines.append(format_table(['FUNCTION', 'VERSION'], rows))

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Show detailed information about a CT-CaaS bundle'
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

    bundle = client.get_bundle(args.bundle)
    if not bundle:
        sys.exit(1)

    bundle_type = client.get_bundle_type(args.bundle) or 'unknown'
    output = format_bundle_info(bundle, args.bundle, bundle_type, args.format)
    print(output)


if __name__ == '__main__':
    main()
