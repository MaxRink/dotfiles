#!/usr/bin/env python3
"""
CaaS Compare Versions - Compare functions between two product versions
Usage: caas-compare-versions.py <product1> <product2> [--format FORMAT] [--images]
"""

import argparse
import sys
from typing import Dict, List, Tuple

from caas_common import (
    CaaSBundlesClient,
    HelmIndexClient,
    format_json,
    format_table,
    format_markdown_table,
)

# Import image version extraction logic
import importlib.util
import os

# Load caas-image-versions module for reuse
_script_dir = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("image_versions", os.path.join(_script_dir, "caas-image-versions.py"))
_image_versions_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_image_versions_module)

extract_helm_sources = _image_versions_module.extract_helm_sources
extract_tag_from_values_data = _image_versions_module.extract_tag_from_values_data
extract_hardcoded_tags = _image_versions_module.extract_hardcoded_tags
CHARTS_WITH_BAD_APPVERSION = _image_versions_module.CHARTS_WITH_BAD_APPVERSION
CHARTS_WITH_PRODUCT_VERSION = _image_versions_module.CHARTS_WITH_PRODUCT_VERSION
CHART_TAG_OVERRIDES = _image_versions_module.CHART_TAG_OVERRIDES


def compare_products(
    client: CaaSBundlesClient,
    product1: str,
    product2: str
) -> Dict[str, List[Dict]]:
    """Compare functions between two products"""
    # Get both products
    p1_data = client.get_product(product1)
    p2_data = client.get_product(product2)

    if not p1_data:
        print(f"Product not found: {product1}", file=sys.stderr)
        sys.exit(1)
    if not p2_data:
        print(f"Product not found: {product2}", file=sys.stderr)
        sys.exit(1)

    # Extract functions as dict {name: version}
    p1_funcs = {}
    for f in p1_data.get('spec', {}).get('functions', []):
        p1_funcs[f.get('name', '')] = f.get('version', '')

    p2_funcs = {}
    for f in p2_data.get('spec', {}).get('functions', []):
        p2_funcs[f.get('name', '')] = f.get('version', '')

    # Compare
    all_funcs = sorted(set(list(p1_funcs.keys()) + list(p2_funcs.keys())))

    added = []
    removed = []
    changed = []
    unchanged = []

    for func in all_funcs:
        v1 = p1_funcs.get(func)
        v2 = p2_funcs.get(func)

        if v1 is None:
            added.append({'function': func, 'version': v2, 'change': 'added'})
        elif v2 is None:
            removed.append({'function': func, 'version': v1, 'change': 'removed'})
        elif v1 != v2:
            changed.append({
                'function': func,
                'old_version': v1,
                'new_version': v2,
                'change': 'changed'
            })
        else:
            unchanged.append({'function': func, 'version': v1, 'change': 'unchanged'})

    return {
        'added': added,
        'removed': removed,
        'changed': changed,
        'unchanged': unchanged,
        'product1': product1,
        'product2': product2,
        'summary': {
            'added': len(added),
            'removed': len(removed),
            'changed': len(changed),
            'unchanged': len(unchanged)
        }
    }


def get_image_versions(client: CaaSBundlesClient, helm_client: HelmIndexClient,
                       product_name: str, kubernetes_version: str) -> Dict[str, str]:
    """Get image versions for a product as {chart_name: image_tag}"""
    functions = client.get_product_functions(product_name)
    if not functions:
        return {}

    images = {}
    for func in functions:
        func_data = client.get_function(func['name'], func['version'])
        if not func_data:
            continue

        helm_sources = extract_helm_sources(func_data)
        for source in helm_sources:
            chart_name = source['chart']
            chart_version = source['version']
            values_data = source.get('valuesData', '')

            # Determine image tag using same logic as caas-image-versions.py
            if chart_name in CHARTS_WITH_PRODUCT_VERSION:
                app_version = kubernetes_version
            elif chart_name in CHART_TAG_OVERRIDES:
                app_version = CHART_TAG_OVERRIDES[chart_name].get(chart_version)
            elif chart_name in CHARTS_WITH_BAD_APPVERSION:
                app_version = extract_tag_from_values_data(values_data)
                if not app_version:
                    hardcoded = extract_hardcoded_tags(func_data)
                    app_version = hardcoded[0] if hardcoded else None
            else:
                app_version = helm_client.get_appversion(chart_name, chart_version)

            if app_version:
                images[f"{chart_name}:{chart_version}"] = app_version

    return images


def compare_images(client: CaaSBundlesClient, helm_client: HelmIndexClient,
                   product1: str, product2: str) -> Dict[str, List[Dict]]:
    """Compare image versions between two products"""
    # Get kubernetes versions
    p1_data = client.get_product(product1)
    p2_data = client.get_product(product2)
    k8s_v1 = p1_data.get('spec', {}).get('kubernetesVersion') if p1_data else None
    k8s_v2 = p2_data.get('spec', {}).get('kubernetesVersion') if p2_data else None

    # Get image versions
    images1 = get_image_versions(client, helm_client, product1, k8s_v1)
    images2 = get_image_versions(client, helm_client, product2, k8s_v2)

    # Compare by chart name (without version) to find upgrades
    def chart_base(full_name):
        return full_name.rsplit(':', 1)[0]

    # Group by base chart name
    charts1 = {}
    for full, tag in images1.items():
        base = chart_base(full)
        charts1[base] = {'full': full, 'tag': tag}

    charts2 = {}
    for full, tag in images2.items():
        base = chart_base(full)
        charts2[base] = {'full': full, 'tag': tag}

    all_charts = sorted(set(list(charts1.keys()) + list(charts2.keys())))

    added = []
    removed = []
    changed = []
    unchanged = []

    for chart in all_charts:
        c1 = charts1.get(chart)
        c2 = charts2.get(chart)

        if c1 is None:
            added.append({'chart': chart, 'version': c2['full'].split(':')[-1], 'tag': c2['tag']})
        elif c2 is None:
            removed.append({'chart': chart, 'version': c1['full'].split(':')[-1], 'tag': c1['tag']})
        elif c1['tag'] != c2['tag']:
            changed.append({
                'chart': chart,
                'old_chart_version': c1['full'].split(':')[-1],
                'new_chart_version': c2['full'].split(':')[-1],
                'old_tag': c1['tag'],
                'new_tag': c2['tag']
            })
        else:
            unchanged.append({'chart': chart, 'tag': c1['tag']})

    return {
        'added': added,
        'removed': removed,
        'changed': changed,
        'unchanged': unchanged,
        'summary': {
            'added': len(added),
            'removed': len(removed),
            'changed': len(changed),
            'unchanged': len(unchanged)
        }
    }


def format_comparison(result: Dict, fmt: str = 'table') -> str:
    """Format comparison results"""
    if fmt == 'json':
        return format_json(result)

    lines = []
    p1 = result['product1']
    p2 = result['product2']
    summary = result['summary']

    # Summary
    lines.append(f"Comparison: {p1} → {p2}")
    lines.append("=" * 60)
    lines.append(f"Added: {summary['added']} | Removed: {summary['removed']} | "
                 f"Changed: {summary['changed']} | Unchanged: {summary['unchanged']}")
    lines.append("")

    # Changed functions
    if result['changed']:
        lines.append("## Changed Functions")
        if fmt == 'markdown':
            lines.append("")
            lines.append("| Function | Old Version | New Version |")
            lines.append("|----------|-------------|-------------|")
            for c in result['changed']:
                lines.append(f"| {c['function']} | {c['old_version']} | {c['new_version']} |")
        else:
            headers = ['FUNCTION', 'OLD_VERSION', 'NEW_VERSION']
            rows = [[c['function'], c['old_version'], c['new_version']] for c in result['changed']]
            lines.append(format_table(headers, rows))
        lines.append("")

    # Added functions
    if result['added']:
        lines.append("## Added Functions")
        if fmt == 'markdown':
            lines.append("")
            lines.append("| Function | Version |")
            lines.append("|----------|---------|")
            for a in result['added']:
                lines.append(f"| {a['function']} | {a['version']} |")
        else:
            headers = ['FUNCTION', 'VERSION']
            rows = [[a['function'], a['version']] for a in result['added']]
            lines.append(format_table(headers, rows))
        lines.append("")

    # Removed functions
    if result['removed']:
        lines.append("## Removed Functions")
        if fmt == 'markdown':
            lines.append("")
            lines.append("| Function | Version |")
            lines.append("|----------|---------|")
            for r in result['removed']:
                lines.append(f"| {r['function']} | {r['version']} |")
        else:
            headers = ['FUNCTION', 'VERSION']
            rows = [[r['function'], r['version']] for r in result['removed']]
            lines.append(format_table(headers, rows))
        lines.append("")

    return '\n'.join(lines)


def format_image_comparison(result: Dict, product1: str, product2: str, fmt: str = 'table') -> str:
    """Format image comparison results"""
    if fmt == 'json':
        return format_json(result)

    lines = []
    summary = result['summary']

    # Summary
    lines.append(f"Image Comparison: {product1} → {product2}")
    lines.append("=" * 60)
    lines.append(f"Added: {summary['added']} | Removed: {summary['removed']} | "
                 f"Changed: {summary['changed']} | Unchanged: {summary['unchanged']}")
    lines.append("")

    # Changed images
    if result['changed']:
        lines.append("## Changed Images")
        if fmt == 'markdown':
            lines.append("")
            lines.append("| Chart | Old Tag | New Tag |")
            lines.append("|-------|---------|---------|")
            for c in result['changed']:
                lines.append(f"| {c['chart']} | {c['old_tag']} | {c['new_tag']} |")
        else:
            headers = ['CHART', 'OLD_TAG', 'NEW_TAG']
            rows = [[c['chart'], c['old_tag'], c['new_tag']] for c in result['changed']]
            lines.append(format_table(headers, rows))
        lines.append("")

    # Added images
    if result['added']:
        lines.append("## Added Images")
        if fmt == 'markdown':
            lines.append("")
            lines.append("| Chart | Tag |")
            lines.append("|-------|-----|")
            for a in result['added']:
                lines.append(f"| {a['chart']} | {a['tag']} |")
        else:
            headers = ['CHART', 'TAG']
            rows = [[a['chart'], a['tag']] for a in result['added']]
            lines.append(format_table(headers, rows))
        lines.append("")

    # Removed images
    if result['removed']:
        lines.append("## Removed Images")
        if fmt == 'markdown':
            lines.append("")
            lines.append("| Chart | Tag |")
            lines.append("|-------|-----|")
            for r in result['removed']:
                lines.append(f"| {r['chart']} | {r['tag']} |")
        else:
            headers = ['CHART', 'TAG']
            rows = [[r['chart'], r['tag']] for r in result['removed']]
            lines.append(format_table(headers, rows))
        lines.append("")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Compare functions between two CaaS product versions'
    )
    parser.add_argument(
        'product1',
        help='First product name (older version)'
    )
    parser.add_argument(
        'product2',
        help='Second product name (newer version)'
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
    parser.add_argument(
        '--images',
        action='store_true',
        help='Compare image versions instead of functions'
    )

    args = parser.parse_args()

    # Initialize client
    client = CaaSBundlesClient(ref=args.ref)

    if args.images:
        # Compare images
        helm_client = HelmIndexClient()
        result = compare_images(client, helm_client, args.product1, args.product2)
        print(format_image_comparison(result, args.product1, args.product2, args.format))
    else:
        # Compare functions
        result = compare_products(client, args.product1, args.product2)
        print(format_comparison(result, args.format))


if __name__ == '__main__':
    main()
