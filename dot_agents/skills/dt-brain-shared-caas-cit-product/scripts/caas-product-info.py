#!/usr/bin/env python3
"""
CaaS Product Info - Show detailed information about a CaaS product
Usage: caas-product-info.py <product-name> [--format FORMAT]
"""

import argparse
import sys
from typing import Dict, Any

from caas_common import (
    CaaSBundlesClient,
    format_json,
    format_table,
    format_markdown_table,
)


def format_product_info(product: Dict[str, Any], product_name: str, fmt: str = 'table') -> str:
    """Format product information for display"""
    if fmt == 'json':
        return format_json(product)

    spec = product.get('spec', {})
    metadata = product.get('metadata', {})

    lines = []

    # Header
    lines.append(f"Product: {product_name}")
    lines.append("=" * 60)
    lines.append("")

    # Metadata
    lines.append("## Metadata")
    k8s_version = spec.get('kubernetesVersion', 'N/A')
    lines.append(f"  Kubernetes Version: {k8s_version}")

    component_config = spec.get('componentConfig', {})
    if component_config:
        if isinstance(component_config, dict):
            lines.append(f"  Component Config: {component_config.get('name', 'N/A')}")
        else:
            lines.append(f"  Component Config: {component_config}")

    labels = metadata.get('labels', {})
    if labels:
        lines.append("  Labels:")
        for k, v in labels.items():
            lines.append(f"    {k}: {v}")

    lines.append("")

    # Functions
    functions = spec.get('functions', [])
    if functions:
        lines.append("## Functions")
        if fmt == 'markdown':
            headers = ['Function', 'Version']
            rows = [[f.get('name', ''), f.get('version', '')] for f in functions]
            lines.append(format_markdown_table(headers, rows))
        else:
            headers = ['FUNCTION', 'VERSION']
            rows = [[f.get('name', ''), f.get('version', '')] for f in functions]
            lines.append(format_table(headers, rows))
        lines.append("")

    # Actions
    actions = spec.get('actions', [])
    if actions:
        lines.append("## Actions")
        if fmt == 'markdown':
            headers = ['Action', 'Stages']
            rows = []
            for a in actions:
                stages = a.get('stages', [])
                stage_names_list = []
                for s in stages[:3]:
                    if isinstance(s, dict):
                        stage_names_list.append(s.get('name', ''))
                    else:
                        stage_names_list.append(str(s))
                stage_names = ', '.join(stage_names_list)
                if len(stages) > 3:
                    stage_names += f" (+{len(stages) - 3} more)"
                rows.append([a.get('name', ''), stage_names])
            lines.append(format_markdown_table(headers, rows))
        else:
            headers = ['ACTION', 'STAGES']
            rows = []
            for a in actions:
                stages = a.get('stages', [])
                stage_names_list = []
                for s in stages[:3]:
                    if isinstance(s, dict):
                        stage_names_list.append(s.get('name', ''))
                    else:
                        stage_names_list.append(str(s))
                stage_names = ', '.join(stage_names_list)
                if len(stages) > 3:
                    stage_names += f" (+{len(stages) - 3} more)"
                rows.append([a.get('name', ''), stage_names])
            lines.append(format_table(headers, rows))

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Show detailed information about a CaaS product'
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

    # Get product
    product = client.get_product(args.product)
    if not product:
        sys.exit(1)

    # Format and output
    output = format_product_info(product, args.product, args.format)
    print(output)


if __name__ == '__main__':
    main()
