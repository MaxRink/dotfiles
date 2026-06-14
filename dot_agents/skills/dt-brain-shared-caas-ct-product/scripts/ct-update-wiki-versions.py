#!/usr/bin/env python3
"""
CT-CaaS Wiki Version Updater - Fill component versions in T-CaaS wiki release notes pages
Usage:
  ct-update-wiki-versions.py <bundle-name> --page-id PAGE_ID [--dry-run]
  ct-update-wiki-versions.py <bundle-name> --version VERSION [--dry-run]

Examples:
  ct-update-wiki-versions.py netbox-workload-34.0.22 --page-id 3805536940
  ct-update-wiki-versions.py netbox-workload-34.0.22 --version 34.0 --dry-run
"""

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ct_common import CTBundlesClient, OCIRegistryClient

# Import get_image_versions from ct-image-versions.py
import importlib.util
_script_dir = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("image_versions", os.path.join(_script_dir, "ct-image-versions.py"))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
get_image_versions = _mod.get_image_versions

# Wiki skill path for API access
WIKI_SKILL_PATH = os.path.join(os.path.dirname(_script_dir), '..', 'telekom-wiki', 'scripts')

# Component name mapping: wiki table name -> (function pattern, component filter)
# component_filter helps disambiguate when a function has multiple helm charts
WIKI_COMPONENT_MAP = {
    'kube-apiserver':               (r'^kube-apiserver$', None),
    'kube-controller-manager':      (r'^kube-controller-manager$', None),
    'kube-scheduler':               (r'^kube-scheduler$', None),
    'kube-proxy':                   (r'^kube-proxy$', None),
    'etcd':                         (r'^etcd$', None),
    'coredns':                      (r'^coredns$', None),
    'Calico':                       (r'^calico$', None),
    'authn-authz':                  (r'^auth-operator$', 'authn-authz'),
    'Kyverno':                      (r'^kyverno$', 'kyverno (helm)'),
    'Whereabouts':                  (r'^whereabouts$', None),
    'Multus CNI':                   (r'^multus-cni$', None),
    'SR-IOV network device plugin': (r'^sriov-network-device-plugin$', None),
    'SR-IOV CNI':                   (r'^sriov-cni$', None),
    'OVS CNI':                      (r'^ovs-cni$', None),
    'Accelerated Bridge CNI':       (r'^accelerated-bridge-cni$', None),
    'Flux':                         (r'^flux', None),
    'Metallb':                      (r'^metallb', None),
    'Blackbox exporter':            (r'^blackbox-exporter$', None),
    'Goldpinger':                   (r'^goldpinger$', None),
    'Metrics server':               (r'^metrics-server$', None),
    'Kube-state-metrics':           (r'^kube-state-metrics$', None),
    'Node-exporter':                (r'^node-exporter$', None),
    'Prometheus':                   (r'^prometheus$', 'prometheus (helm)'),
    'Fluentbit':                    (r'^fluent-bit$', None),
    'Ceph CSI cephfs':              (r'^ceph-csi$', 'ceph-csi-cephfs'),
    'Ceph CSI rbd':                 (r'^ceph-csi$', 'ceph-csi-rbd'),
    'Trident CSI':                  (r'^trident', None),
    'Cert-manager':                 (r'^cert-manager$', None),
    'Velero':                       (r'^velero$', None),
    'Coil Egress NAT':              (r'^coil', None),
}


def get_version_for_wiki_component(versions: List[Dict], pattern: str,
                                    comp_filter: Optional[str] = None) -> str:
    """Get image version for a component matching the pattern."""
    for v in versions:
        func = v.get('function', '')
        comp = v.get('component', '')
        if re.match(pattern, func) and ('(helm)' in comp or '(kustomize)' in comp or '(k8s)' in comp):
            if comp_filter and comp_filter not in comp:
                continue
            img_ver = v.get('image_version', '')
            if img_ver and img_ver != '-':
                return img_ver
            return v.get('type_version', '')
    return ''


def build_version_map(versions: List[Dict]) -> Dict[str, str]:
    """Build wiki component name -> version mapping."""
    result = {}
    for wiki_name, (pattern, comp_filter) in WIKI_COMPONENT_MAP.items():
        ver = get_version_for_wiki_component(versions, pattern, comp_filter)
        if ver:
            result[wiki_name] = ver
    return result


def update_confluence_content(content: str, version_map: Dict[str, str],
                               k8s_version: str) -> Tuple[str, List[str]]:
    """Update Confluence storage format HTML with component versions.
    Returns (updated_content, list_of_changes)."""
    changes = []

    # Update Kubernetes version table
    for old_pattern in [r'(<th>Kubernetes</th>)<td[^>]*>(?:[^<]*|<br\s*/>)*</td>']:
        match = re.search(old_pattern, content)
        if match and k8s_version:
            old_text = match.group(0)
            new_text = f'{match.group(1)}<td>{k8s_version}</td>'
            if old_text != new_text:
                content = content.replace(old_text, new_text, 1)
                changes.append(f'Kubernetes: {k8s_version}')

    # Update component versions
    for component, version in version_map.items():
        comp_escaped = re.escape(component)
        # Match th with optional span wrappers, then first td with various empty content patterns
        pattern = (
            rf'((?:<th[^>]*>)(?:<span[^>]*>)?{comp_escaped}\s*(?:<br\s*/?>)?(?:</span>)?</th>)'
            rf'<td[^>]*>(?:<span[^>]*>(?:<br\s*/?>)?[^<]*</span>|<br\s*/?>|\s)*</td>'
        )
        replacement = rf'\1<td>{version}</td>'
        new_content = re.sub(pattern, replacement, content, count=1)
        if new_content != content:
            content = new_content
            changes.append(f'{component}: {version}')

    return content, changes


def get_confluence_client():
    """Get Confluence client from telekom-wiki skill."""
    wiki_utils_path = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'telekom-wiki', 'scripts')
    )
    sys.path.insert(0, wiki_utils_path)
    from utils.client import get_confluence_client as _get_client
    return _get_client()


def find_wiki_page(confluence, version: str) -> Optional[Dict]:
    """Find the T-CaaS version wiki page by version number."""
    cql = f'space = TCAAS AND type = page AND title = "T-CaaS version {version}"'
    results = confluence.cql(cql, limit=5)
    if results and results.get('results'):
        page_id = results['results'][0]['content']['id']
        return confluence.get_page_by_id(page_id, expand='body.storage,version')
    return None


def get_page_by_id(confluence, page_id: str) -> Optional[Dict]:
    """Get wiki page by ID."""
    return confluence.get_page_by_id(page_id, expand='body.storage,version')


def update_wiki_page(confluence, page_id: str, title: str, content: str,
                     current_version: int) -> bool:
    """Update wiki page content."""
    result = confluence.update_page(
        page_id=page_id,
        title=title,
        body=content,
        type='page',
        representation='storage',
        minor_edit=False,
    )
    return bool(result)


def main():
    parser = argparse.ArgumentParser(
        description='Fill component versions in T-CaaS wiki release notes pages'
    )
    parser.add_argument('bundle', help='Bundle name (e.g., netbox-workload-34.0.22)')
    parser.add_argument('--page-id', help='Confluence page ID')
    parser.add_argument('--version', help='T-CaaS version (e.g., 34.0) — auto-discovers wiki page')
    parser.add_argument('--ref', default='main', help='Git branch/tag/commit (default: main)')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without updating')

    args = parser.parse_args()

    if not args.page_id and not args.version:
        print("Error: Provide either --page-id or --version", file=sys.stderr)
        sys.exit(1)

    # Step 1: Extract component versions from bundle
    print(f"Extracting versions from {args.bundle}...", file=sys.stderr)
    client = CTBundlesClient(ref=args.ref)
    oci_client = OCIRegistryClient()

    bundle = client.get_bundle(args.bundle)
    if not bundle:
        print(f"Error: Bundle not found: {args.bundle}", file=sys.stderr)
        sys.exit(1)

    k8s_version = bundle.get('spec', {}).get('k8sVersion', '')
    versions = get_image_versions(client, oci_client, args.bundle)
    if not versions:
        print("Error: No versions extracted", file=sys.stderr)
        sys.exit(1)

    version_map = build_version_map(versions)
    print(f"Extracted {len(version_map)} component versions", file=sys.stderr)

    # Step 2: Get wiki page
    print("Connecting to Confluence...", file=sys.stderr)
    confluence = get_confluence_client()

    if args.page_id:
        page = get_page_by_id(confluence, args.page_id)
    else:
        page = find_wiki_page(confluence, args.version)

    if not page:
        target = args.page_id or f"T-CaaS version {args.version}"
        print(f"Error: Wiki page not found: {target}", file=sys.stderr)
        sys.exit(1)

    page_id = page['id']
    title = page['title']
    current_version = page['version']['number']
    content = page['body']['storage']['value']

    print(f"Found page: {title} (ID: {page_id}, version: {current_version})", file=sys.stderr)

    # Step 3: Update content
    updated_content, changes = update_confluence_content(content, version_map, k8s_version)

    if not changes:
        print("No changes needed — all fields already filled or no matching components.", file=sys.stderr)
        sys.exit(0)

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Changes ({len(changes)}):", file=sys.stderr)
    for change in changes:
        print(f"  ✓ {change}", file=sys.stderr)

    if args.dry_run:
        print(f"\nDry run complete. Use without --dry-run to apply changes.", file=sys.stderr)
        sys.exit(0)

    # Step 4: Update wiki page
    print(f"\nUpdating page...", file=sys.stderr)
    success = update_wiki_page(confluence, page_id, title, updated_content, current_version)
    if success:
        print(f"✓ Page updated: {title}", file=sys.stderr)
        print(f"  URL: https://wiki.telekom.de/pages/viewpage.action?pageId={page_id}", file=sys.stderr)
    else:
        print("Error: Failed to update page", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
