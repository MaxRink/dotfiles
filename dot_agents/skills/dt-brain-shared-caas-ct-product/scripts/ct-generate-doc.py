#!/usr/bin/env python3
"""
CT-CaaS Generate Doc - Generate comprehensive bundle documentation
Usage: ct-generate-doc.py <bundle-name> [--release-notes] [--output FILE] [--format FORMAT]
"""

import argparse
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ct_common import (
    CTBundlesClient,
    OCIRegistryClient,
    format_markdown_table,
    format_confluence_table,
    format_json,
)

# Import image version and release notes logic
import importlib.util

_script_dir = os.path.dirname(os.path.abspath(__file__))

_spec_img = importlib.util.spec_from_file_location("image_versions", os.path.join(_script_dir, "ct-image-versions.py"))
_image_versions_module = importlib.util.module_from_spec(_spec_img)
_spec_img.loader.exec_module(_image_versions_module)
get_image_versions = _image_versions_module.get_image_versions

_spec_rn = importlib.util.spec_from_file_location("release_notes", os.path.join(_script_dir, "ct-release-notes.py"))
_release_notes_module = importlib.util.module_from_spec(_spec_rn)
_spec_rn.loader.exec_module(_release_notes_module)
generate_release_notes = _release_notes_module.generate_release_notes
detect_bundle_type = _release_notes_module.detect_bundle_type


def generate_full_doc_markdown(client: CTBundlesClient, oci_client: OCIRegistryClient,
                                bundle_name: str) -> str:
    """Generate comprehensive markdown documentation"""
    bundle = client.get_bundle(bundle_name)
    if not bundle:
        return ""

    spec = bundle.get('spec', {})
    k8s_version = spec.get('k8sVersion', 'N/A')
    bundle_type = client.get_bundle_type(bundle_name) or 'unknown'
    version = CTBundlesClient._extract_version(bundle_name)

    lines = []

    # Header
    lines.append(f"# {bundle_name}")
    lines.append("")
    lines.append(f"*Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}*")
    lines.append("")

    # Overview
    lines.append("## Overview")
    lines.append("")
    lines.append("| Property | Value |")
    lines.append("|----------|-------|")
    lines.append(f"| **Bundle Name** | {bundle_name} |")
    lines.append(f"| **Version** | {version} |")
    lines.append(f"| **Bundle Type** | {bundle_type} |")
    lines.append(f"| **Kubernetes Version** | {k8s_version} |")
    lines.append("")

    # Functions table
    functions = client.get_bundle_functions(bundle_name)
    if functions:
        lines.append("## Functions")
        lines.append("")
        lines.append("| Function | Version |")
        lines.append("|----------|---------|")
        for f in sorted(functions, key=lambda x: x['name']):
            lines.append(f"| {f['name']} | {f['version']} |")
        lines.append("")

    # Image versions
    lines.append("## Chart/Image Versions")
    lines.append("")
    versions = get_image_versions(client, oci_client, bundle_name)
    if versions:
        lines.append("| Function | Version | Component | Type/Version | Image Version | Notes |")
        lines.append("|----------|---------|-----------|--------------|---------------|-------|")
        for v in versions:
            lines.append(
                f"| {v['function']} | {v['function_version']} | {v['component']} "
                f"| {v['type_version']} | {v['image_version']} | {v['notes']} |"
            )
    else:
        lines.append("*No version data available*")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"*Source: GitLab project {client.project.path_with_namespace}*")

    return '\n'.join(lines)


def generate_full_doc_confluence(client: CTBundlesClient, oci_client: OCIRegistryClient,
                                  bundle_name: str) -> str:
    """Generate comprehensive Confluence wiki markup documentation"""
    bundle = client.get_bundle(bundle_name)
    if not bundle:
        return ""

    spec = bundle.get('spec', {})
    k8s_version = spec.get('k8sVersion', 'N/A')
    bundle_type = client.get_bundle_type(bundle_name) or 'unknown'
    version = CTBundlesClient._extract_version(bundle_name)

    lines = []

    lines.append(f"h1. {bundle_name}")
    lines.append("")
    lines.append("h2. Overview")
    lines.append("")
    lines.append("||Property||Value||")
    lines.append(f"|Bundle Name|{bundle_name}|")
    lines.append(f"|Version|{version}|")
    lines.append(f"|Bundle Type|{bundle_type}|")
    lines.append(f"|Kubernetes Version|{k8s_version}|")
    lines.append("")

    functions = client.get_bundle_functions(bundle_name)
    if functions:
        lines.append("h2. Functions")
        lines.append("")
        lines.append("||Function||Version||")
        for f in sorted(functions, key=lambda x: x['name']):
            lines.append(f"|{f['name']}|{f['version']}|")
        lines.append("")

    lines.append("h2. Chart/Image Versions")
    lines.append("")
    versions = get_image_versions(client, oci_client, bundle_name)
    if versions:
        lines.append("||Function||Version||Component||Type/Version||Image Version||Notes||")
        for v in versions:
            lines.append(
                f"|{v['function']}|{v['function_version']}|{v['component']}"
                f"|{v['type_version']}|{v['image_version']}|{v['notes']}|"
            )
    lines.append("")

    lines.append("----")
    lines.append("")
    lines.append(f"_Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}_")

    return '\n'.join(lines)


def generate_full_doc_json(client: CTBundlesClient, oci_client: OCIRegistryClient,
                            bundle_name: str) -> str:
    """Generate JSON documentation"""
    bundle = client.get_bundle(bundle_name)
    if not bundle:
        return ""

    spec = bundle.get('spec', {})
    k8s_version = spec.get('k8sVersion', '')
    bundle_type = client.get_bundle_type(bundle_name) or 'unknown'
    version = CTBundlesClient._extract_version(bundle_name)

    functions = client.get_bundle_functions(bundle_name)
    func_list = [{'name': f['name'], 'version': f['version']} for f in functions]

    return format_json({
        'bundle': bundle_name,
        'metadata': {
            'version': version,
            'bundle_type': bundle_type,
            'kubernetes_version': k8s_version
        },
        'functions': func_list,
        'generated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source': f"GitLab: {client.project.path_with_namespace}"
    })


def main():
    parser = argparse.ArgumentParser(
        description='Generate CT-CaaS bundle documentation'
    )
    parser.add_argument(
        'bundle',
        help='Bundle name (e.g., netbox-workload-34.0.19)'
    )
    parser.add_argument(
        '--release-notes',
        action='store_true',
        help='Generate simple component/version table for release notes'
    )
    parser.add_argument(
        '--ref',
        default='main',
        help='Git branch/tag/commit (default: main)'
    )
    parser.add_argument(
        '--format',
        choices=['markdown', 'confluence', 'json', 'plain'],
        default='markdown',
        help='Output format (default: markdown)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file (default: stdout)'
    )

    args = parser.parse_args()

    client = CTBundlesClient(ref=args.ref)
    oci_client = OCIRegistryClient()

    if args.release_notes:
        bundle = client.get_bundle(args.bundle)
        if not bundle:
            sys.exit(1)
        k8s_version = bundle.get('spec', {}).get('k8sVersion', '')
        bundle_type = detect_bundle_type(args.bundle)
        if bundle_type == 'unknown':
            bundle_type = 'netbox'
        versions = get_image_versions(client, oci_client, args.bundle)
        doc = generate_release_notes(versions, args.bundle, k8s_version, bundle_type, args.format)
    else:
        if args.format == 'confluence':
            doc = generate_full_doc_confluence(client, oci_client, args.bundle)
        elif args.format == 'json':
            doc = generate_full_doc_json(client, oci_client, args.bundle)
        else:
            doc = generate_full_doc_markdown(client, oci_client, args.bundle)

    if not doc:
        print(f"Could not generate documentation for: {args.bundle}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(doc)
        print(f"Documentation written to: {args.output}")
    else:
        print(doc)


if __name__ == '__main__':
    main()
