#!/bin/bash
# ct-release-notes.sh - Generate component version table for CT-CaaS release notes
# Supports both netbox (baremetal) and OpenStack bundles
set -euo pipefail

# Auto-detect tcaas bundles path
find_ct_bundles() {
    if [[ -n "${CT_CAAS_BUNDLES_PATH:-}" ]] && [[ -d "$CT_CAAS_BUNDLES_PATH" ]]; then
        echo "$CT_CAAS_BUNDLES_PATH"
        return 0
    fi

    local paths=(
        "./tcaas/bundles"
        "../tcaas/bundles"
        "$HOME/git/tcaas/bundles"
    )

    for p in "${paths[@]}"; do
        if [[ -d "$p/bundles" ]]; then
            echo "$p"
            return 0
        fi
    done

    local found
    found=$(find /Users/*/git/tcaas/bundles -maxdepth 0 -type d 2>/dev/null | head -1)
    if [[ -n "$found" ]]; then
        echo "$found"
        return 0
    fi

    echo "ERROR: Cannot find tcaas/bundles. Set CT_CAAS_BUNDLES_PATH environment variable." >&2
    return 1
}

# Detect bundle type from bundle name
detect_bundle_type() {
    local bundle="$1"
    if [[ "$bundle" == netbox-workload-* ]]; then
        echo "netbox"
    elif [[ "$bundle" == openstack-management-* ]] || [[ "$bundle" == openstack-workload-* ]]; then
        echo "openstack"
    else
        echo "unknown"
    fi
}

usage() {
    cat <<EOF
Usage: $(basename "$0") <bundle-name> [OPTIONS]

Generate component version table for CT-CaaS release notes documentation.
Auto-detects bundle type (netbox vs OpenStack) and shows relevant components.

Arguments:
    bundle-name    The bundle name (e.g., netbox-workload-34.0.19, openstack-management-33.6.6)

Options:
    --format FORMAT Output format: markdown (default), confluence, plain
    -h, --help      Show this help message

Examples:
    $(basename "$0") netbox-workload-34.0.19
    $(basename "$0") openstack-management-33.6.6 --format confluence
    $(basename "$0") netbox-workload-34.0.19 --format plain
EOF
}

FORMAT="markdown"
BUNDLE_NAME=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --format)
            FORMAT="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        -*)
            echo "Unknown option: $1" >&2
            usage
            exit 1
            ;;
        *)
            BUNDLE_NAME="$1"
            shift
            ;;
    esac
done

if [[ -z "$BUNDLE_NAME" ]]; then
    echo "ERROR: Bundle name required" >&2
    usage
    exit 1
fi

# Get script directory for calling other scripts
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Find bundles and bundle file for Kubernetes version
CT_BUNDLES=$(find_ct_bundles)
BUNDLES_DIR="$CT_BUNDLES/bundles"

BUNDLE_FILE=""
for type_dir in "$BUNDLES_DIR"/*/; do
    if [[ -f "${type_dir}${BUNDLE_NAME}.yaml" ]]; then
        BUNDLE_FILE="${type_dir}${BUNDLE_NAME}.yaml"
        break
    fi
done

# Extract Kubernetes version from bundle YAML (CT-CaaS uses k8sVersion)
KUBERNETES_VERSION=""
if [[ -n "$BUNDLE_FILE" ]] && [[ -f "$BUNDLE_FILE" ]]; then
    KUBERNETES_VERSION=$(grep -E "^[[:space:]]*k8sVersion:" "$BUNDLE_FILE" | awk '{print $2}' | tr -d '"' || true)
fi

# Get image versions JSON
VERSIONS_JSON=$("$SCRIPT_DIR/ct-image-versions.sh" "$BUNDLE_NAME" --format json 2>/dev/null)

if [[ -z "$VERSIONS_JSON" ]]; then
    echo "ERROR: Failed to get image versions for $BUNDLE_NAME" >&2
    exit 1
fi

# Helper to get version for a component
# Prefers image_version when available, falls back to type_version
get_version() {
    local pattern="$1"
    local result
    # Get the first helm component matching the pattern
    result=$(echo "$VERSIONS_JSON" | jq -r "
        .components[]
        | select(.function | test(\"$pattern\"))
        | select(.component | contains(\"(helm)\") or contains(\"(kustomize)\"))
        | if .image_version != \"\" and .image_version != \"-\" then .image_version else .type_version end
    " 2>/dev/null | head -1)
    echo "$result"
}

# Detect bundle type
BUNDLE_TYPE=$(detect_bundle_type "$BUNDLE_NAME")

# Get common versions (both netbox and openstack)
V_METRICS_SERVER=$(get_version "^metrics-server$")
V_COREDNS=$(get_version "^coredns$")
V_CALICO=$(get_version "^calico$")
V_INGRESS_NGINX=$(get_version "^ingress-nginx")
V_CERT_MANAGER=$(get_version "^cert-manager$")
V_KYVERNO=$(get_version "^kyverno$")
V_PROMETHEUS=$(get_version "^prometheus$")
V_BLACKBOX_EXPORTER=$(get_version "blackbox-exporter")
V_GOLDPINGER=$(get_version "^goldpinger$")
V_FLUENT_BIT=$(get_version "^fluent-bit$")
V_FLUX=$(get_version "^flux")
V_KUBE_STATE_METRICS=$(get_version "^kube-state-metrics$")
V_NODE_EXPORTER=$(get_version "^node-exporter$")

# Netbox-specific versions
V_METALLB=$(get_version "^metallb")
V_MULTUS_CNI=$(get_version "^multus-cni$")
V_SRIOV_CNI=$(get_version "^sriov-cni$")
V_SRIOV_DEVICE_PLUGIN=$(get_version "sriov-network-device-plugin")
V_WHEREABOUTS=$(get_version "^whereabouts$")
V_OVS_CNI=$(get_version "^ovs-cni$")
V_CEPH_CSI=$(get_version "^ceph-csi$")

# OpenStack-specific versions
V_OPENSTACK_CCM=$(get_version "openstack-cloud-controller")
V_CINDER_CSI=$(get_version "cinder-csi")

# Output functions for different bundle types
output_markdown_netbox() {
    echo "## Component Versions (Netbox/Baremetal)"
    echo ""
    [[ -n "$KUBERNETES_VERSION" ]] && echo "**Kubernetes Version:** $KUBERNETES_VERSION"
    [[ -n "$KUBERNETES_VERSION" ]] && echo ""
    echo "| Component | Version |"
    echo "|-----------|---------|"
    echo "| **Cluster Services** | |"
    [[ -n "$V_METRICS_SERVER" ]] && echo "| metrics-server | $V_METRICS_SERVER |"
    [[ -n "$V_COREDNS" ]] && echo "| coredns | $V_COREDNS |"
    [[ -n "$V_KUBE_STATE_METRICS" ]] && echo "| kube-state-metrics | $V_KUBE_STATE_METRICS |"
    echo "| **Networking** | |"
    [[ -n "$V_CALICO" ]] && echo "| calico | $V_CALICO |"
    [[ -n "$V_METALLB" ]] && echo "| metallb | $V_METALLB |"
    [[ -n "$V_INGRESS_NGINX" ]] && echo "| ingress-nginx | $V_INGRESS_NGINX |"
    echo "| **SR-IOV & Multus** | |"
    [[ -n "$V_MULTUS_CNI" ]] && echo "| multus-cni | $V_MULTUS_CNI |"
    [[ -n "$V_SRIOV_CNI" ]] && echo "| sriov-cni | $V_SRIOV_CNI |"
    [[ -n "$V_SRIOV_DEVICE_PLUGIN" ]] && echo "| sriov-network-device-plugin | $V_SRIOV_DEVICE_PLUGIN |"
    [[ -n "$V_WHEREABOUTS" ]] && echo "| whereabouts | $V_WHEREABOUTS |"
    [[ -n "$V_OVS_CNI" ]] && echo "| ovs-cni | $V_OVS_CNI |"
    echo "| **Storage** | |"
    [[ -n "$V_CEPH_CSI" ]] && echo "| ceph-csi | $V_CEPH_CSI |"
    echo "| **Security** | |"
    [[ -n "$V_CERT_MANAGER" ]] && echo "| cert-manager | $V_CERT_MANAGER |"
    [[ -n "$V_KYVERNO" ]] && echo "| kyverno | $V_KYVERNO |"
    echo "| **Monitoring** | |"
    [[ -n "$V_PROMETHEUS" ]] && echo "| prometheus | $V_PROMETHEUS |"
    [[ -n "$V_BLACKBOX_EXPORTER" ]] && echo "| blackbox-exporter | $V_BLACKBOX_EXPORTER |"
    [[ -n "$V_GOLDPINGER" ]] && echo "| goldpinger | $V_GOLDPINGER |"
    [[ -n "$V_NODE_EXPORTER" ]] && echo "| node-exporter | $V_NODE_EXPORTER |"
    echo "| **Logging** | |"
    [[ -n "$V_FLUENT_BIT" ]] && echo "| fluent-bit | $V_FLUENT_BIT |"
    echo "| **GitOps** | |"
    [[ -n "$V_FLUX" ]] && echo "| flux | $V_FLUX |"
}

output_markdown_openstack() {
    echo "## Component Versions (OpenStack)"
    echo ""
    [[ -n "$KUBERNETES_VERSION" ]] && echo "**Kubernetes Version:** $KUBERNETES_VERSION"
    [[ -n "$KUBERNETES_VERSION" ]] && echo ""
    echo "| Component | Version |"
    echo "|-----------|---------|"
    echo "| **Cluster Services** | |"
    [[ -n "$V_METRICS_SERVER" ]] && echo "| metrics-server | $V_METRICS_SERVER |"
    [[ -n "$V_COREDNS" ]] && echo "| coredns | $V_COREDNS |"
    [[ -n "$V_KUBE_STATE_METRICS" ]] && echo "| kube-state-metrics | $V_KUBE_STATE_METRICS |"
    echo "| **Networking** | |"
    [[ -n "$V_CALICO" ]] && echo "| calico | $V_CALICO |"
    [[ -n "$V_INGRESS_NGINX" ]] && echo "| ingress-nginx | $V_INGRESS_NGINX |"
    echo "| **OpenStack Integration** | |"
    [[ -n "$V_OPENSTACK_CCM" ]] && echo "| openstack-cloud-controller-manager | $V_OPENSTACK_CCM |"
    [[ -n "$V_CINDER_CSI" ]] && echo "| cinder-csi | $V_CINDER_CSI |"
    echo "| **Security** | |"
    [[ -n "$V_CERT_MANAGER" ]] && echo "| cert-manager | $V_CERT_MANAGER |"
    [[ -n "$V_KYVERNO" ]] && echo "| kyverno | $V_KYVERNO |"
    echo "| **Monitoring** | |"
    [[ -n "$V_PROMETHEUS" ]] && echo "| prometheus | $V_PROMETHEUS |"
    [[ -n "$V_BLACKBOX_EXPORTER" ]] && echo "| blackbox-exporter | $V_BLACKBOX_EXPORTER |"
    [[ -n "$V_GOLDPINGER" ]] && echo "| goldpinger | $V_GOLDPINGER |"
    [[ -n "$V_NODE_EXPORTER" ]] && echo "| node-exporter | $V_NODE_EXPORTER |"
    echo "| **Logging** | |"
    [[ -n "$V_FLUENT_BIT" ]] && echo "| fluent-bit | $V_FLUENT_BIT |"
    echo "| **GitOps** | |"
    [[ -n "$V_FLUX" ]] && echo "| flux | $V_FLUX |"
}

output_confluence_netbox() {
    echo "h2. Component Versions (Netbox/Baremetal)"
    echo ""
    [[ -n "$KUBERNETES_VERSION" ]] && echo "*Kubernetes Version:* $KUBERNETES_VERSION"
    [[ -n "$KUBERNETES_VERSION" ]] && echo ""
    echo "|| Component || Version ||"
    echo "|| *Cluster Services* || ||"
    [[ -n "$V_METRICS_SERVER" ]] && echo "| metrics-server | $V_METRICS_SERVER |"
    [[ -n "$V_COREDNS" ]] && echo "| coredns | $V_COREDNS |"
    [[ -n "$V_KUBE_STATE_METRICS" ]] && echo "| kube-state-metrics | $V_KUBE_STATE_METRICS |"
    echo "|| *Networking* || ||"
    [[ -n "$V_CALICO" ]] && echo "| calico | $V_CALICO |"
    [[ -n "$V_METALLB" ]] && echo "| metallb | $V_METALLB |"
    [[ -n "$V_INGRESS_NGINX" ]] && echo "| ingress-nginx | $V_INGRESS_NGINX |"
    echo "|| *SR-IOV & Multus* || ||"
    [[ -n "$V_MULTUS_CNI" ]] && echo "| multus-cni | $V_MULTUS_CNI |"
    [[ -n "$V_SRIOV_CNI" ]] && echo "| sriov-cni | $V_SRIOV_CNI |"
    [[ -n "$V_SRIOV_DEVICE_PLUGIN" ]] && echo "| sriov-network-device-plugin | $V_SRIOV_DEVICE_PLUGIN |"
    [[ -n "$V_WHEREABOUTS" ]] && echo "| whereabouts | $V_WHEREABOUTS |"
    [[ -n "$V_OVS_CNI" ]] && echo "| ovs-cni | $V_OVS_CNI |"
    echo "|| *Storage* || ||"
    [[ -n "$V_CEPH_CSI" ]] && echo "| ceph-csi | $V_CEPH_CSI |"
    echo "|| *Security* || ||"
    [[ -n "$V_CERT_MANAGER" ]] && echo "| cert-manager | $V_CERT_MANAGER |"
    [[ -n "$V_KYVERNO" ]] && echo "| kyverno | $V_KYVERNO |"
    echo "|| *Monitoring* || ||"
    [[ -n "$V_PROMETHEUS" ]] && echo "| prometheus | $V_PROMETHEUS |"
    [[ -n "$V_BLACKBOX_EXPORTER" ]] && echo "| blackbox-exporter | $V_BLACKBOX_EXPORTER |"
    [[ -n "$V_GOLDPINGER" ]] && echo "| goldpinger | $V_GOLDPINGER |"
    [[ -n "$V_NODE_EXPORTER" ]] && echo "| node-exporter | $V_NODE_EXPORTER |"
    echo "|| *Logging* || ||"
    [[ -n "$V_FLUENT_BIT" ]] && echo "| fluent-bit | $V_FLUENT_BIT |"
    echo "|| *GitOps* || ||"
    [[ -n "$V_FLUX" ]] && echo "| flux | $V_FLUX |"
}

output_confluence_openstack() {
    echo "h2. Component Versions (OpenStack)"
    echo ""
    [[ -n "$KUBERNETES_VERSION" ]] && echo "*Kubernetes Version:* $KUBERNETES_VERSION"
    [[ -n "$KUBERNETES_VERSION" ]] && echo ""
    echo "|| Component || Version ||"
    echo "|| *Cluster Services* || ||"
    [[ -n "$V_METRICS_SERVER" ]] && echo "| metrics-server | $V_METRICS_SERVER |"
    [[ -n "$V_COREDNS" ]] && echo "| coredns | $V_COREDNS |"
    [[ -n "$V_KUBE_STATE_METRICS" ]] && echo "| kube-state-metrics | $V_KUBE_STATE_METRICS |"
    echo "|| *Networking* || ||"
    [[ -n "$V_CALICO" ]] && echo "| calico | $V_CALICO |"
    [[ -n "$V_INGRESS_NGINX" ]] && echo "| ingress-nginx | $V_INGRESS_NGINX |"
    echo "|| *OpenStack Integration* || ||"
    [[ -n "$V_OPENSTACK_CCM" ]] && echo "| openstack-cloud-controller-manager | $V_OPENSTACK_CCM |"
    [[ -n "$V_CINDER_CSI" ]] && echo "| cinder-csi | $V_CINDER_CSI |"
    echo "|| *Security* || ||"
    [[ -n "$V_CERT_MANAGER" ]] && echo "| cert-manager | $V_CERT_MANAGER |"
    [[ -n "$V_KYVERNO" ]] && echo "| kyverno | $V_KYVERNO |"
    echo "|| *Monitoring* || ||"
    [[ -n "$V_PROMETHEUS" ]] && echo "| prometheus | $V_PROMETHEUS |"
    [[ -n "$V_BLACKBOX_EXPORTER" ]] && echo "| blackbox-exporter | $V_BLACKBOX_EXPORTER |"
    [[ -n "$V_GOLDPINGER" ]] && echo "| goldpinger | $V_GOLDPINGER |"
    [[ -n "$V_NODE_EXPORTER" ]] && echo "| node-exporter | $V_NODE_EXPORTER |"
    echo "|| *Logging* || ||"
    [[ -n "$V_FLUENT_BIT" ]] && echo "| fluent-bit | $V_FLUENT_BIT |"
    echo "|| *GitOps* || ||"
    [[ -n "$V_FLUX" ]] && echo "| flux | $V_FLUX |"
}

output_plain_netbox() {
    echo "Component Versions for $BUNDLE_NAME (Netbox/Baremetal)"
    echo "======================================================="
    echo ""
    [[ -n "$KUBERNETES_VERSION" ]] && echo "Kubernetes Version: $KUBERNETES_VERSION"
    [[ -n "$KUBERNETES_VERSION" ]] && echo ""
    echo "Cluster Services:"
    [[ -n "$V_METRICS_SERVER" ]] && echo "  metrics-server: $V_METRICS_SERVER"
    [[ -n "$V_COREDNS" ]] && echo "  coredns: $V_COREDNS"
    [[ -n "$V_KUBE_STATE_METRICS" ]] && echo "  kube-state-metrics: $V_KUBE_STATE_METRICS"
    echo ""
    echo "Networking:"
    [[ -n "$V_CALICO" ]] && echo "  calico: $V_CALICO"
    [[ -n "$V_METALLB" ]] && echo "  metallb: $V_METALLB"
    [[ -n "$V_INGRESS_NGINX" ]] && echo "  ingress-nginx: $V_INGRESS_NGINX"
    echo ""
    echo "SR-IOV & Multus:"
    [[ -n "$V_MULTUS_CNI" ]] && echo "  multus-cni: $V_MULTUS_CNI"
    [[ -n "$V_SRIOV_CNI" ]] && echo "  sriov-cni: $V_SRIOV_CNI"
    [[ -n "$V_SRIOV_DEVICE_PLUGIN" ]] && echo "  sriov-network-device-plugin: $V_SRIOV_DEVICE_PLUGIN"
    [[ -n "$V_WHEREABOUTS" ]] && echo "  whereabouts: $V_WHEREABOUTS"
    [[ -n "$V_OVS_CNI" ]] && echo "  ovs-cni: $V_OVS_CNI"
    echo ""
    echo "Storage:"
    [[ -n "$V_CEPH_CSI" ]] && echo "  ceph-csi: $V_CEPH_CSI"
    echo ""
    echo "Security:"
    [[ -n "$V_CERT_MANAGER" ]] && echo "  cert-manager: $V_CERT_MANAGER"
    [[ -n "$V_KYVERNO" ]] && echo "  kyverno: $V_KYVERNO"
    echo ""
    echo "Monitoring:"
    [[ -n "$V_PROMETHEUS" ]] && echo "  prometheus: $V_PROMETHEUS"
    [[ -n "$V_BLACKBOX_EXPORTER" ]] && echo "  blackbox-exporter: $V_BLACKBOX_EXPORTER"
    [[ -n "$V_GOLDPINGER" ]] && echo "  goldpinger: $V_GOLDPINGER"
    [[ -n "$V_NODE_EXPORTER" ]] && echo "  node-exporter: $V_NODE_EXPORTER"
    echo ""
    echo "Logging:"
    [[ -n "$V_FLUENT_BIT" ]] && echo "  fluent-bit: $V_FLUENT_BIT"
    echo ""
    echo "GitOps:"
    [[ -n "$V_FLUX" ]] && echo "  flux: $V_FLUX"
}

output_plain_openstack() {
    echo "Component Versions for $BUNDLE_NAME (OpenStack)"
    echo "================================================"
    echo ""
    [[ -n "$KUBERNETES_VERSION" ]] && echo "Kubernetes Version: $KUBERNETES_VERSION"
    [[ -n "$KUBERNETES_VERSION" ]] && echo ""
    echo "Cluster Services:"
    [[ -n "$V_METRICS_SERVER" ]] && echo "  metrics-server: $V_METRICS_SERVER"
    [[ -n "$V_COREDNS" ]] && echo "  coredns: $V_COREDNS"
    [[ -n "$V_KUBE_STATE_METRICS" ]] && echo "  kube-state-metrics: $V_KUBE_STATE_METRICS"
    echo ""
    echo "Networking:"
    [[ -n "$V_CALICO" ]] && echo "  calico: $V_CALICO"
    [[ -n "$V_INGRESS_NGINX" ]] && echo "  ingress-nginx: $V_INGRESS_NGINX"
    echo ""
    echo "OpenStack Integration:"
    [[ -n "$V_OPENSTACK_CCM" ]] && echo "  openstack-cloud-controller-manager: $V_OPENSTACK_CCM"
    [[ -n "$V_CINDER_CSI" ]] && echo "  cinder-csi: $V_CINDER_CSI"
    echo ""
    echo "Security:"
    [[ -n "$V_CERT_MANAGER" ]] && echo "  cert-manager: $V_CERT_MANAGER"
    [[ -n "$V_KYVERNO" ]] && echo "  kyverno: $V_KYVERNO"
    echo ""
    echo "Monitoring:"
    [[ -n "$V_PROMETHEUS" ]] && echo "  prometheus: $V_PROMETHEUS"
    [[ -n "$V_BLACKBOX_EXPORTER" ]] && echo "  blackbox-exporter: $V_BLACKBOX_EXPORTER"
    [[ -n "$V_GOLDPINGER" ]] && echo "  goldpinger: $V_GOLDPINGER"
    [[ -n "$V_NODE_EXPORTER" ]] && echo "  node-exporter: $V_NODE_EXPORTER"
    echo ""
    echo "Logging:"
    [[ -n "$V_FLUENT_BIT" ]] && echo "  fluent-bit: $V_FLUENT_BIT"
    echo ""
    echo "GitOps:"
    [[ -n "$V_FLUX" ]] && echo "  flux: $V_FLUX"
}

# Output based on format and bundle type
case "$FORMAT" in
    markdown)
        if [[ "$BUNDLE_TYPE" == "openstack" ]]; then
            output_markdown_openstack
        else
            output_markdown_netbox
        fi
        ;;

    confluence)
        if [[ "$BUNDLE_TYPE" == "openstack" ]]; then
            output_confluence_openstack
        else
            output_confluence_netbox
        fi
        ;;

    plain)
        if [[ "$BUNDLE_TYPE" == "openstack" ]]; then
            output_plain_openstack
        else
            output_plain_netbox
        fi
        ;;

    *)
        echo "ERROR: Unknown format: $FORMAT" >&2
        exit 1
        ;;
esac
