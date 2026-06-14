#!/usr/bin/env python3
"""
CT-CaaS Release Notes - Generate component version table for release notes
Usage: ct-release-notes.py <bundle-name> [--format FORMAT]

Supports netbox (baremetal) and OpenStack bundles with type-specific component layouts.
"""

import argparse
import os
import re
import sys
from typing import Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ct_common import (
    CTBundlesClient,
    OCIRegistryClient,
    format_markdown_table,
    format_confluence_table,
)

# Import image version extraction
import importlib.util
_script_dir = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("image_versions", os.path.join(_script_dir, "ct-image-versions.py"))
_image_versions_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_image_versions_module)
get_image_versions = _image_versions_module.get_image_versions


def detect_bundle_type(bundle_name: str) -> str:
    """Detect bundle type from name"""
    if bundle_name.startswith("netbox-workload-"):
        return "netbox"
    elif bundle_name.startswith("openstack-"):
        return "openstack"
    return "unknown"


def get_version_for_component(versions: List[Dict], pattern: str,
                              component_filter: str = None) -> str:
    """Get image version for a component matching the pattern.
    Optionally filter by component name substring.
    Prefers image_version, falls back to type_version."""
    for v in versions:
        func = v.get('function', '')
        comp = v.get('component', '')
        if re.match(pattern, func) and ('(helm)' in comp or '(kustomize)' in comp or '(k8s)' in comp):
            if component_filter and component_filter not in comp:
                continue
            img_ver = v.get('image_version', '')
            if img_ver and img_ver != '-':
                return img_ver
            return v.get('type_version', '')
    return ''


# Component layout definitions per bundle type
# Aligned with the T-CaaS wiki release notes table structure
# Tuples: (display_name, function_pattern, component_filter)
# component_filter is optional — used when a function has multiple helm charts
NETBOX_COMPONENTS = [
    ("**Kubernetes**", None, None),
    ("kube-apiserver", r"^kube-apiserver$", None),
    ("kube-controller-manager", r"^kube-controller-manager$", None),
    ("kube-scheduler", r"^kube-scheduler$", None),
    ("kube-proxy", r"^kube-proxy$", None),
    ("etcd", r"^etcd$", None),
    ("coredns", r"^coredns$", None),
    ("", None, None),  # separator row
    ("**Networking**", None, None),
    ("Calico", r"^calico$", None),
    ("authn-authz", r"^auth-operator$", "authn-authz"),
    ("Kyverno", r"^kyverno$", "kyverno (helm)"),
    ("Whereabouts", r"^whereabouts$", None),
    ("Multus CNI", r"^multus-cni$", None),
    ("SR-IOV network device plugin", r"^sriov-network-device-plugin$", None),
    ("SR-IOV CNI", r"^sriov-cni$", None),
    ("OVS CNI", r"^ovs-cni$", None),
    ("Accelerated Bridge CNI", r"^accelerated-bridge-cni$", None),
    ("Flux", r"^flux", None),
    ("Metallb", r"^metallb", None),
    ("**Monitoring**", None, None),
    ("Blackbox exporter", r"^blackbox-exporter$", None),
    ("Goldpinger", r"^goldpinger$", None),
    ("Metrics server", r"^metrics-server$", None),
    ("Kube-state-metrics", r"^kube-state-metrics$", None),
    ("Node-exporter", r"^node-exporter$", None),
    ("Prometheus", r"^prometheus$", "prometheus (helm)"),
    ("**Logging**", None, None),
    ("Fluentbit", r"^fluent-bit$", None),
    ("**Storage**", None, None),
    ("Ceph CSI cephfs", r"^ceph-csi$", "ceph-csi-cephfs"),
    ("Ceph CSI rbd", r"^ceph-csi$", "ceph-csi-rbd"),
    ("Trident CSI", r"^trident", None),
    ("**Security**", None, None),
    ("Cert-manager", r"^cert-manager$", None),
    ("Velero", r"^velero$", None),
    ("Coil Egress NAT", r"^coil", None),
]

OPENSTACK_COMPONENTS = [
    ("**Kubernetes**", None, None),
    ("kube-apiserver", r"^kube-apiserver$", None),
    ("kube-controller-manager", r"^kube-controller-manager$", None),
    ("kube-scheduler", r"^kube-scheduler$", None),
    ("kube-proxy", r"^kube-proxy$", None),
    ("etcd", r"^etcd$", None),
    ("coredns", r"^coredns$", None),
    ("", None, None),  # separator row
    ("**Networking**", None, None),
    ("Calico", r"^calico$", None),
    ("authn-authz", r"^auth-operator$", "authn-authz"),
    ("Kyverno", r"^kyverno$", "kyverno (helm)"),
    ("ingress-nginx", r"^ingress-nginx", None),
    ("**OpenStack Integration**", None, None),
    ("openstack-cloud-controller-manager", r"openstack-cloud-controller", None),
    ("cinder-csi", r"cinder-csi", None),
    ("**Monitoring**", None, None),
    ("Blackbox exporter", r"^blackbox-exporter$", None),
    ("Goldpinger", r"^goldpinger$", None),
    ("Metrics server", r"^metrics-server$", None),
    ("Kube-state-metrics", r"^kube-state-metrics$", None),
    ("Node-exporter", r"^node-exporter$", None),
    ("Prometheus", r"^prometheus$", "prometheus (helm)"),
    ("**Logging**", None, None),
    ("Fluentbit", r"^fluent-bit$", None),
    ("**Security**", None, None),
    ("Cert-manager", r"^cert-manager$", None),
    ("**GitOps**", None, None),
    ("Flux", r"^flux", None),
]


def generate_release_notes(versions: List[Dict], bundle_name: str,
                           k8s_version: str, bundle_type: str,
                           fmt: str = 'markdown') -> str:
    """Generate release notes table"""
    components = NETBOX_COMPONENTS if bundle_type == "netbox" else OPENSTACK_COMPONENTS
    type_label = "Netbox/Baremetal" if bundle_type == "netbox" else "OpenStack"

    rows = []
    for comp_name, pattern, comp_filter in components:
        if pattern is None:
            # Section header or separator
            rows.append([comp_name, ''])
        else:
            version = get_version_for_component(versions, pattern, comp_filter)
            rows.append([comp_name, version])

    if fmt == 'confluence':
        lines = [f"h2. Component Versions ({type_label})", ""]
        if k8s_version:
            lines.extend([f"*Kubernetes Version:* {k8s_version}", ""])
        lines.append("|| Component || Version ||")
        for row in rows:
            if row[0].startswith("**") and row[0].endswith("**"):
                # Section header in confluence
                label = row[0].strip('*')
                lines.append(f"|| *{label}* || ||")
            else:
                lines.append(f"| {row[0]} | {row[1]} |")
        return '\n'.join(lines)

    elif fmt == 'plain':
        lines = [f"Component Versions for {bundle_name} ({type_label})",
                 "=" * 60, ""]
        if k8s_version:
            lines.extend([f"Kubernetes Version: {k8s_version}", ""])
        current_section = ""
        for row in rows:
            if row[0].startswith("**") and row[0].endswith("**"):
                if current_section:
                    lines.append("")
                current_section = row[0].strip('*')
                lines.append(f"{current_section}:")
            else:
                lines.append(f"  {row[0]}: {row[1]}")
        return '\n'.join(lines)

    else:  # markdown
        lines = [f"## Component Versions ({type_label})", ""]
        if k8s_version:
            lines.extend([f"**Kubernetes Version:** {k8s_version}", ""])
        lines.extend(["| Component | Version |", "|-----------|---------|"])
        for row in rows:
            lines.append(f"| {row[0]} | {row[1]} |")
        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Generate component version table for CT-CaaS release notes'
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
        choices=['markdown', 'confluence', 'plain'],
        default='markdown',
        help='Output format (default: markdown)'
    )

    args = parser.parse_args()

    client = CTBundlesClient(ref=args.ref)
    oci_client = OCIRegistryClient()

    # Get bundle data for k8s version
    bundle = client.get_bundle(args.bundle)
    if not bundle:
        sys.exit(1)

    k8s_version = bundle.get('spec', {}).get('k8sVersion', '')
    bundle_type = detect_bundle_type(args.bundle)

    if bundle_type == 'unknown':
        print(f"Warning: Could not detect bundle type for {args.bundle}, using netbox layout", file=sys.stderr)
        bundle_type = 'netbox'

    # Get image versions
    versions = get_image_versions(client, oci_client, args.bundle)

    output = generate_release_notes(versions, args.bundle, k8s_version, bundle_type, args.format)
    print(output)


if __name__ == '__main__':
    main()
