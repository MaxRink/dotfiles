#!/bin/bash
# ct-list-bundles.sh - List all available CT-CaaS bundles
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

    # Try glob pattern for any user
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
Usage: $(basename "$0") [OPTIONS]

List all available CT-CaaS bundles.

Options:
    --type TYPE     Filter by bundle type (netbox, openstack)
    --latest        Show only the latest version per bundle
    -h, --help      Show this help message

Examples:
    $(basename "$0")                      # List all bundles
    $(basename "$0") --type netbox        # List only netbox bundles
    $(basename "$0") --type openstack     # List only openstack bundles
    $(basename "$0") --latest             # Show latest version of each bundle
EOF
}

TYPE_FILTER=""
SHOW_LATEST=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --type)
            TYPE_FILTER="$2"
            shift 2
            ;;
        --latest)
            SHOW_LATEST=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage
            exit 1
            ;;
    esac
done

CT_BUNDLES=$(find_ct_bundles)
BUNDLES_DIR="$CT_BUNDLES/bundles"

if [[ ! -d "$BUNDLES_DIR" ]]; then
    echo "ERROR: Bundles directory not found: $BUNDLES_DIR" >&2
    exit 1
fi

# Get list of bundle types (directories) - only netbox and openstack
if [[ -n "$TYPE_FILTER" ]]; then
    TYPES=("$TYPE_FILTER")
    if [[ ! -d "$BUNDLES_DIR/$TYPE_FILTER" ]]; then
        echo "ERROR: Bundle type not found: $TYPE_FILTER" >&2
        echo "Available types: netbox openstack" >&2
        exit 1
    fi
else
    # Default to netbox and openstack only
    TYPES=()
    [[ -d "$BUNDLES_DIR/netbox" ]] && TYPES+=("netbox")
    [[ -d "$BUNDLES_DIR/openstack" ]] && TYPES+=("openstack")
fi

# Function to extract version for sorting
extract_version() {
    local name="$1"
    # Extract version numbers after the bundle name prefix
    echo "$name" | sed -E 's/.*-([0-9]+\.[0-9]+\.[0-9]+)\.yaml$/\1/'
}

# Function to compare versions
version_gt() {
    test "$(printf '%s\n' "$@" | sort -V | head -n 1)" != "$1"
}

if $SHOW_LATEST; then
    echo "BUNDLE_TYPE|BUNDLE_NAME|VERSION"
    echo "-----------|-----------|-------"

    for type in "${TYPES[@]}"; do
        type_dir="$BUNDLES_DIR/$type"
        [[ -d "$type_dir" ]] || continue

        for file in "$type_dir"/*.yaml; do
            [[ -f "$file" ]] || continue
            filename=$(basename "$file" .yaml)
            version=$(extract_version "$filename.yaml")
            bundle_name=$(echo "$filename" | sed -E 's/-[0-9]+\.[0-9]+\.[0-9]+$//')
            echo "$type|$bundle_name|$filename|$version"
        done
    done | sort -t'|' -k1,1 -k2,2 -k4,4Vr | awk -F'|' '
    {
        key = $1 "|" $2
        if (!(key in seen)) {
            seen[key] = 1
            print $1 "|" $3 "|" $4
        }
    }
    ' | sort -t'|' -k1,1 -k2,2V
else
    echo "BUNDLE_TYPE|BUNDLE_NAME|VERSION"
    echo "-----------|-----------|-------"

    for type in "${TYPES[@]}"; do
        type_dir="$BUNDLES_DIR/$type"
        [[ -d "$type_dir" ]] || continue

        for file in "$type_dir"/*.yaml; do
            [[ -f "$file" ]] || continue
            filename=$(basename "$file" .yaml)
            version=$(extract_version "$filename.yaml")
            echo "$type|$filename|$version"
        done
    done | sort -t'|' -k1,1 -k2,2V
fi
