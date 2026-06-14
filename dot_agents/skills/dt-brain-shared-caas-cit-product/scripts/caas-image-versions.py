#!/usr/bin/env python3
"""
CaaS Image Versions - Extract container image versions from Helm repository
Usage: caas-image-versions.py <product-name> [--format FORMAT]
"""

import argparse
import re
import sys
from typing import Dict, List, Optional, Any

from caas_common import (
    CaaSBundlesClient,
    HelmIndexClient,
    output_results,
    format_json,
)

# Charts with known incorrect appVersion in Chart.yaml
# These need actual image tag extraction from valuesData
CHARTS_WITH_BAD_APPVERSION = {'multus'}

# Charts where tag uses template variables referencing product spec
CHARTS_WITH_PRODUCT_VERSION = {'kube-proxy'}

# Charts where appVersion is wrong and tag is in chart's values.yaml (not function valuesData)
# These require downloading the chart to get the real tag, so we use known mappings
CHART_TAG_OVERRIDES = {
    'whereabouts': {
        '0.2.1': 'v0.8.0',
        '0.2.0': 'v0.8.0',
        '0.1.4': 'v0.8.0',
        '0.1.3': 'v0.8.0',
        '0.1.2': 'v0.8.0',
        '0.1.1': 'v0.8.0',
        'v0.1.1': 'v0.8.0',
        'v0.1.0': 'v0.8.0',
    }
}


def extract_helm_sources(function_data: Dict) -> List[Dict[str, str]]:
    """Extract Helm chart sources from function spec"""
    results = []
    spec = function_data.get('spec', {})
    sources = spec.get('source', [])

    for source in sources:
        name = source.get('name', '')
        version = source.get('version', '')
        values_data = source.get('valuesData', '')
        if name and version:
            results.append({'chart': name, 'version': version, 'valuesData': values_data})

    return results


def extract_kustomize_sources(function_data: Dict) -> List[Dict[str, str]]:
    """Extract Kustomize OCI sources from function spec"""
    results = []
    spec = function_data.get('spec', {})

    # Check for kustomize patches with OCI references
    patches = spec.get('patches', [])
    for patch in patches:
        if isinstance(patch, dict):
            target = patch.get('target', {})
            # Look for OCI image references
            patch_content = str(patch)
            oci_match = re.search(r'oci://[^\s"\']+', patch_content)
            if oci_match:
                results.append({'source': oci_match.group(), 'type': 'kustomize'})

    return results


def extract_hardcoded_tags(function_data: Dict) -> List[str]:
    """Extract hardcoded image tags from function data including valuesData strings"""
    tags = []

    def find_tags(obj: Any, path: str = ""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == 'tag' and isinstance(v, str) and re.match(r'^[v]?\d', v):
                    tags.append(v)
                elif k == 'valuesData' and isinstance(v, str):
                    # Parse valuesData string for tag patterns
                    tag_matches = re.findall(r'tag[:\s]+["\']?([v]?[\d.]+)["\']?', v, re.IGNORECASE)
                    tags.extend(tag_matches)
                else:
                    find_tags(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                find_tags(item, f"{path}[{i}]")

    find_tags(function_data)
    return list(set(tags))[:3]  # Return max 3 unique tags


def extract_tag_from_values_data(values_data: str) -> Optional[str]:
    """Extract image tag from valuesData YAML string"""
    if not values_data:
        return None
    # Look for tag patterns like "tag: v3.8" or 'tag: "v3.8"'
    match = re.search(r'tag[:\s]+["\']?([v]?[\d.]+)["\']?', values_data, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def main():
    parser = argparse.ArgumentParser(
        description='Extract container image versions from Helm repository'
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

    # Initialize clients
    client = CaaSBundlesClient(ref=args.ref)
    helm_client = HelmIndexClient()

    # Get product data for kubernetesVersion
    product_data = client.get_product(args.product)
    kubernetes_version = None
    if product_data:
        kubernetes_version = product_data.get('spec', {}).get('kubernetesVersion')

    # Get product functions
    functions = client.get_product_functions(args.product)
    if not functions:
        print(f"No functions found for product: {args.product}", file=sys.stderr)
        sys.exit(1)

    results = []

    for func in functions:
        func_name = func['name']
        func_version = func['version']

        # Get function data
        func_data = client.get_function(func_name, func_version)
        if not func_data:
            results.append({
                'function': func_name,
                'version': func_version,
                'helm_chart': '',
                'image_tag': '',
                'notes': 'Function file not found'
            })
            continue

        # Extract Helm sources
        helm_sources = extract_helm_sources(func_data)

        if not helm_sources:
            # No Helm charts, check for hardcoded tags
            hardcoded = extract_hardcoded_tags(func_data)
            if hardcoded:
                results.append({
                    'function': func_name,
                    'version': func_version,
                    'helm_chart': '',
                    'image_tag': ', '.join(hardcoded),
                    'notes': 'Hardcoded tags'
                })
            else:
                results.append({
                    'function': func_name,
                    'version': func_version,
                    'helm_chart': '',
                    'image_tag': '',
                    'notes': 'No Helm chart'
                })
            continue

        # Process each Helm chart
        for source in helm_sources:
            chart_name = source['chart']
            chart_version = source['version']
            values_data = source.get('valuesData', '')

            # For charts where tag uses kubernetesVersion from product
            if chart_name in CHARTS_WITH_PRODUCT_VERSION:
                app_version = kubernetes_version
            # For charts with known tag overrides (appVersion wrong, tag in chart values.yaml)
            elif chart_name in CHART_TAG_OVERRIDES:
                app_version = CHART_TAG_OVERRIDES[chart_name].get(chart_version)
            # For charts with known incorrect appVersion, extract from valuesData first
            elif chart_name in CHARTS_WITH_BAD_APPVERSION:
                app_version = extract_tag_from_values_data(values_data)
                if not app_version:
                    # Fallback to other hardcoded tags in function
                    hardcoded = extract_hardcoded_tags(func_data)
                    app_version = hardcoded[0] if hardcoded else None
            else:
                # Lookup appVersion from Helm index
                app_version = helm_client.get_appversion(chart_name, chart_version)

            if app_version:
                results.append({
                    'function': func_name,
                    'version': func_version,
                    'helm_chart': f"{chart_name}:{chart_version}",
                    'image_tag': app_version,
                    'notes': ''
                })
            else:
                # Fallback to hardcoded tags
                hardcoded = extract_hardcoded_tags(func_data)
                results.append({
                    'function': func_name,
                    'version': func_version,
                    'helm_chart': f"{chart_name}:{chart_version}",
                    'image_tag': hardcoded[0] if hardcoded else '',
                    'notes': 'Hardcoded' if hardcoded else 'Not found in index'
                })

    # Output results
    if args.format == 'json':
        print(format_json({
            'product': args.product,
            'functions': results
        }))
    else:
        headers = ['FUNCTION', 'VERSION', 'HELM_CHART', 'IMAGE_TAG', 'NOTES']
        keys = ['function', 'version', 'helm_chart', 'image_tag', 'notes']
        output_results(results, headers, keys, args.format)


if __name__ == '__main__':
    main()
