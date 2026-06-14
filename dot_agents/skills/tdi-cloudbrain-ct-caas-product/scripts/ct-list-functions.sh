#!/bin/bash
# ct-list-functions.sh - List all functions for a specific CT-CaaS bundle
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

List all functions for a specific CT-CaaS bundle.

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
for type_dir in "$BUNDLES_DIR"/*/; do
    if [[ -f "${type_dir}${BUNDLE_NAME}.yaml" ]]; then
        BUNDLE_FILE="${type_dir}${BUNDLE_NAME}.yaml"
        break
    fi
done

if [[ -z "$BUNDLE_FILE" ]]; then
    echo "ERROR: Bundle not found: $BUNDLE_NAME" >&2
    echo "Use ct-list-bundles.sh to see available bundles." >&2
    exit 1
fi

echo "Functions for $BUNDLE_NAME:"
echo ""
echo "NAME|VERSION"
echo "----|-------"

# Extract functions using awk
# CT-CaaS format: functions have ref.name with combined name-version format
# e.g., "coredns-0.3.1" needs to be split into name="coredns" version="0.3.1"
awk '
/^  functions:/ { in_functions=1; next }
/^  [a-z]/ && !/- / && in_functions { in_functions=0 }
in_functions && /name:/ {
    gsub(/.*name: *["'\''"]?/, "")
    gsub(/["'\''"].*/, "")
    full_name=$0
    # Split on last version pattern (handles names with hyphens like auth-operator)
    # Match -X.Y.Z or -X.Y.Z-suffix at the end
    if (match(full_name, /-[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.-]+)?$/)) {
        version = substr(full_name, RSTART+1)
        name = substr(full_name, 1, RSTART-1)
        print name "|" version
    } else {
        # No version pattern found, print as-is
        print full_name "|unknown"
    }
}
' "$BUNDLE_FILE" | sort -t'|' -k1,1
