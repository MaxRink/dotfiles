#!/usr/bin/env python3
"""
CaaS Generate Doc - Generate documentation for a CaaS product
Usage: caas-generate-doc.py <product-name> [--release-notes] [--output FILE]
"""

import argparse
import os
import sys
from datetime import datetime
from typing import Dict, List

from caas_common import (
    CaaSBundlesClient,
    HelmIndexClient,
    format_markdown_table,
    format_table,
)

# Import image version extraction logic
import importlib.util

_script_dir = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("image_versions", os.path.join(_script_dir, "caas-image-versions.py"))
_image_versions_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_image_versions_module)

extract_tag_from_values_data = _image_versions_module.extract_tag_from_values_data
extract_hardcoded_tags = _image_versions_module.extract_hardcoded_tags
CHARTS_WITH_BAD_APPVERSION = _image_versions_module.CHARTS_WITH_BAD_APPVERSION
CHARTS_WITH_PRODUCT_VERSION = _image_versions_module.CHARTS_WITH_PRODUCT_VERSION
CHART_TAG_OVERRIDES = _image_versions_module.CHART_TAG_OVERRIDES


def get_image_tag(client: CaaSBundlesClient, helm_client: HelmIndexClient,
                  func_name: str, func_version: str, k8s_version: str) -> str:
    """Get image tag for a function"""
    func_data = client.get_function(func_name, func_version)
    if not func_data:
        return ''

    func_spec = func_data.get('spec', {})
    sources = func_spec.get('source', [])
    if not sources:
        return ''

    chart = sources[0]
    chart_name = chart.get('name', '')
    chart_version = chart.get('version', '')
    values_data = chart.get('valuesData', '')

    if not chart_name:
        return ''

    # Apply same logic as caas-image-versions.py
    if chart_name in CHARTS_WITH_PRODUCT_VERSION:
        return k8s_version
    elif chart_name in CHART_TAG_OVERRIDES:
        return CHART_TAG_OVERRIDES[chart_name].get(chart_version, '')
    elif chart_name in CHARTS_WITH_BAD_APPVERSION:
        tag = extract_tag_from_values_data(values_data)
        if not tag:
            hardcoded = extract_hardcoded_tags(func_data)
            tag = hardcoded[0] if hardcoded else ''
        return tag
    else:
        return helm_client.get_appversion(chart_name, chart_version) or ''


def generate_release_notes(
    client: CaaSBundlesClient,
    helm_client: HelmIndexClient,
    product_name: str,
    output_format: str = 'markdown'
) -> str:
    """Generate simple component version table for release notes"""
    # Get product data
    product = client.get_product(product_name)
    if not product:
        return ""

    spec = product.get('spec', {})
    k8s_version = spec.get('kubernetesVersion', '')

    components = []

    # Add kubernetes version
    if k8s_version:
        components.append({'component': 'Kubernetes', 'version': k8s_version})

    # Process functions
    for func in spec.get('functions', []):
        func_name = func.get('name', '')
        func_version = func.get('version', '')

        if not func_name:
            continue

        image_tag = get_image_tag(client, helm_client, func_name, func_version, k8s_version)

        components.append({
            'component': func_name.replace('-', ' ').title(),
            'version': image_tag or func_version
        })

    # Format output
    if output_format == 'table':
        headers = ['COMPONENT', 'VERSION']
        rows = [[c['component'], c['version']] for c in components]
        return format_table(headers, rows)
    else:  # markdown
        lines = ["| Component | Version |", "|-----------|---------|"]
        for c in components:
            lines.append(f"| {c['component']} | {c['version']} |")
        return '\n'.join(lines)


def generate_full_documentation(
    client: CaaSBundlesClient,
    helm_client: HelmIndexClient,
    product_name: str
) -> str:
    """Generate comprehensive product documentation"""
    lines = []

    # Get product data
    product = client.get_product(product_name)
    if not product:
        return ""

    spec = product.get('spec', {})
    metadata = product.get('metadata', {})
    k8s_version = spec.get('kubernetesVersion', 'N/A')

    # Header
    lines.append(f"# {product_name}")
    lines.append("")
    lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    lines.append("")

    # Overview
    lines.append("## Overview")
    lines.append("")
    lines.append(f"- **Kubernetes Version**: {k8s_version}")

    component_config = spec.get('componentConfig', {})
    if component_config:
        if isinstance(component_config, dict):
            lines.append(f"- **Component Config**: {component_config.get('name', 'N/A')}")
        else:
            lines.append(f"- **Component Config**: {component_config}")

    labels = metadata.get('labels', {})
    product_type = labels.get('type', 'N/A')
    lines.append(f"- **Product Type**: {product_type}")
    lines.append("")

    # Functions table
    functions = spec.get('functions', [])
    if functions:
        lines.append("## Functions")
        lines.append("")
        lines.append("| Function | Version | Image Tag |")
        lines.append("|----------|---------|-----------|")

        for func in functions:
            func_name = func.get('name', '')
            func_version = func.get('version', '')
            image_tag = get_image_tag(client, helm_client, func_name, func_version, k8s_version)
            lines.append(f"| {func_name} | {func_version} | {image_tag} |")

        lines.append("")

    # Actions table
    actions = spec.get('actions', [])
    if actions:
        lines.append("## Actions")
        lines.append("")
        for action in actions:
            action_name = action.get('name', '')
            lines.append(f"### {action_name}")
            lines.append("")

            stages = action.get('stages', [])
            if stages:
                lines.append("| Stage | Description |")
                lines.append("|-------|-------------|")
                for stage in stages:
                    if isinstance(stage, dict):
                        stage_name = stage.get('name', '')
                        stage_desc = stage.get('description', stage_name)
                    else:
                        stage_name = str(stage)
                        stage_desc = stage_name
                    lines.append(f"| {stage_name} | {stage_desc} |")
                lines.append("")

    # Labels
    if labels:
        lines.append("## Labels")
        lines.append("")
        lines.append("| Label | Value |")
        lines.append("|-------|-------|")
        for k, v in sorted(labels.items()):
            lines.append(f"| {k} | {v} |")
        lines.append("")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Generate documentation for a CaaS product'
    )
    parser.add_argument(
        'product',
        help='Product name (e.g., baremetal-cluster-34.6.10)'
    )
    parser.add_argument(
        '--release-notes',
        action='store_true',
        help='Generate simple component/version table for release notes'
    )
    parser.add_argument(
        '--ref',
        default='master',
        help='Git branch/tag/commit (default: master)'
    )
    parser.add_argument(
        '--format',
        choices=['table', 'markdown'],
        default='markdown',
        help='Output format for release notes (default: markdown)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file (default: stdout)'
    )

    args = parser.parse_args()

    # Initialize clients
    client = CaaSBundlesClient(ref=args.ref)
    helm_client = HelmIndexClient()

    # Generate documentation
    if args.release_notes:
        doc = generate_release_notes(client, helm_client, args.product, args.format)
    else:
        doc = generate_full_documentation(client, helm_client, args.product)

    if not doc:
        print(f"Could not generate documentation for: {args.product}", file=sys.stderr)
        sys.exit(1)

    # Output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(doc)
        print(f"Documentation written to: {args.output}")
    else:
        print(doc)


if __name__ == '__main__':
    main()
