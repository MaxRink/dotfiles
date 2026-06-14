#!/bin/bash
# ct-bundle-info.sh - Show detailed information about a CT-CaaS bundle
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

usage() {
    cat <<EOF
Usage: $(basename "$0") <bundle-name>

Show detailed information about a CT-CaaS bundle.

Arguments:
    bundle-name    The bundle name (e.g., netbox-workload-34.0.19)

Examples:
    $(basename "$0") netbox-workload-34.0.19
    $(basename "$0") openstack-management-33.6.6
EOF
}

if [[ $# -lt 1 ]] || [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
    usage
    exit 0
fi

BUNDLE_NAME="$1"
CT_BUNDLES=$(find_ct_bundles)
BUNDLES_DIR="$CT_BUNDLES/bundles"

# Find the bundle file
BUNDLE_FILE=""
BUNDLE_TYPE=""
for type_dir in "$BUNDLES_DIR"/*/; do
    if [[ -f "${type_dir}${BUNDLE_NAME}.yaml" ]]; then
        BUNDLE_FILE="${type_dir}${BUNDLE_NAME}.yaml"
        BUNDLE_TYPE=$(basename "$type_dir")
        break
    fi
done

if [[ -z "$BUNDLE_FILE" ]]; then
    echo "ERROR: Bundle not found: $BUNDLE_NAME" >&2
    echo "Use ct-list-bundles.sh to see available bundles." >&2
    exit 1
fi

# Extract bundle metadata using awk
echo "=============================================="
echo "Bundle: $BUNDLE_NAME"
echo "Type: $BUNDLE_TYPE"
echo "File: $BUNDLE_FILE"
echo "=============================================="
echo ""

echo "## Metadata"
echo ""

# Extract k8sVersion (CT-CaaS uses k8sVersion instead of kubernetesVersion)
K8S_VERSION=$(awk '
/^spec:/ { in_spec=1; next }
in_spec && /k8sVersion:/ {
    gsub(/.*k8sVersion: */, "")
    gsub(/["'\''"]/, "")
    print
    exit
}
' "$BUNDLE_FILE")

if [[ -n "$K8S_VERSION" ]]; then
    printf "%-25s %s\n" "k8sVersion:" "$K8S_VERSION"
fi

echo ""
echo "## Functions"
echo ""
echo "NAME|VERSION"
echo "----|-------"

# Extract functions - CT-CaaS format uses combined ref.name
awk '
/^  functions:/ { in_functions=1; next }
/^  [a-z]/ && !/- / && in_functions { in_functions=0 }
in_functions && /name:/ {
    gsub(/.*name: *["'\''"]?/, "")
    gsub(/["'\''"].*/, "")
    full_name=$0
    # Split on last version pattern (handles names with hyphens like auth-operator)
    if (match(full_name, /-[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.-]+)?$/)) {
        version = substr(full_name, RSTART+1)
        name = substr(full_name, 1, RSTART-1)
        print name "|" version
    } else {
        print full_name "|unknown"
    }
}
' "$BUNDLE_FILE" | sort -t'|' -k1,1
