#!/usr/bin/env python3
"""
CT-CaaS Image Versions - Extract container image versions from function definitions
Usage: ct-image-versions.py <bundle-name> [--format FORMAT]

Extracts:
  - Helm chart names, versions, and container image versions (appVersion from OCI registry)
  - Kustomize release names and OCI references
  - Container images from kustomize image overrides
"""

import argparse
import os
import sys
from typing import Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ct_common import (
    CTBundlesClient,
    OCIRegistryClient,
    extract_helm_releases,
    extract_kustomize_releases,
    extract_kustomize_images,
    output_results,
    format_json,
)


def get_image_versions(client: CTBundlesClient, oci_client: OCIRegistryClient,
                       bundle_name: str) -> List[Dict[str, str]]:
    """Get all component versions for a bundle"""
    functions = client.get_bundle_functions(bundle_name)
    if not functions:
        return []

    results = []

    # Add K8s control plane components derived from bundle k8sVersion
    bundle = client.get_bundle(bundle_name)
    if bundle:
        k8s_version = bundle.get('spec', {}).get('k8sVersion', '')
        if k8s_version:
            for component in ['kube-apiserver', 'kube-controller-manager', 'kube-scheduler']:
                results.append({
                    'function': component,
                    'function_version': k8s_version,
                    'component': f"{component} (k8s)",
                    'type_version': k8s_version,
                    'image_version': k8s_version,
                    'notes': 'From bundle k8sVersion'
                })

    for func in functions:
        func_name = func['name']
        func_version = func['version']
        full_name = func['full_name']

        funcdef = client.get_functiondef(full_name)
        if not funcdef:
            results.append({
                'function': func_name,
                'function_version': func_version,
                'component': '',
                'type_version': '',
                'image_version': '',
                'notes': 'Function definition not found'
            })
            continue

        helm_releases = extract_helm_releases(funcdef)
        kustomize_releases = extract_kustomize_releases(funcdef)
        kustomize_imgs = extract_kustomize_images(funcdef)

        if helm_releases:
            for release in helm_releases:
                chart_name = release['chart']
                chart_version = release['version']
                chart_path = release.get('path', '')

                # Lookup image version from OCI registry
                image_version = oci_client.get_appversion(chart_name, chart_version, chart_path) or ''

                results.append({
                    'function': func_name,
                    'function_version': func_version,
                    'component': f"{chart_name} (helm)",
                    'type_version': chart_version,
                    'image_version': image_version,
                    'notes': ''
                })

        if kustomize_releases:
            for release in kustomize_releases:
                release_name = release['name']
                reference = release['reference']
                results.append({
                    'function': func_name,
                    'function_version': func_version,
                    'component': f"{release_name} (kustomize)",
                    'type_version': reference,
                    'image_version': reference,
                    'notes': ''
                })

        if kustomize_imgs:
            for img_name in kustomize_imgs:
                results.append({
                    'function': func_name,
                    'function_version': func_version,
                    'component': img_name,
                    'type_version': 'image',
                    'image_version': '-',
                    'notes': ''
                })

        if not helm_releases and not kustomize_releases and not kustomize_imgs:
            results.append({
                'function': func_name,
                'function_version': func_version,
                'component': '',
                'type_version': '',
                'image_version': '',
                'notes': 'No releases found'
            })

    return results


def main():
    parser = argparse.ArgumentParser(
        description='Extract component versions from CT-CaaS function definitions'
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
    oci_client = OCIRegistryClient()

    results = get_image_versions(client, oci_client, args.bundle)

    if not results:
        print(f"No components found for bundle: {args.bundle}", file=sys.stderr)
        sys.exit(1)

    if args.format == 'json':
        print(format_json({
            'bundle': args.bundle,
            'components': results
        }))
    else:
        headers = ['FUNCTION', 'VERSION', 'COMPONENT', 'TYPE/VERSION', 'IMAGE_VERSION', 'NOTES']
        keys = ['function', 'function_version', 'component', 'type_version', 'image_version', 'notes']
        output_results(results, headers, keys, args.format)


if __name__ == '__main__':
    main()
