#!/bin/bash
# ct-generate-doc.sh - Generate comprehensive CT-CaaS bundle documentation
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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
Usage: $(basename "$0") <bundle-name> [OPTIONS]

Generate comprehensive CT-CaaS bundle documentation.

Arguments:
    bundle-name    The bundle name (e.g., netbox-workload-34.0.19)

Options:
    --output FILE   Write to file (default: stdout)
    --format FORMAT Output format: markdown (default), confluence, json
    -h, --help      Show this help message

Examples:
    $(basename "$0") netbox-workload-34.0.19
    $(basename "$0") netbox-workload-34.0.19 --format confluence
    $(basename "$0") openstack-management-33.6.6 --output /tmp/bundle-doc.md
EOF
}

FORMAT="markdown"
OUTPUT_FILE=""
BUNDLE_NAME=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --output)
            OUTPUT_FILE="$2"
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
    exit 1
fi

# Extract metadata (CT-CaaS uses k8sVersion)
K8S_VERSION=$(awk '
/^spec:/ { in_spec=1; next }
in_spec && /k8sVersion:/ {
    gsub(/.*k8sVersion: */, "")
    gsub(/["'\''"]/, "")
    print
    exit
}
' "$BUNDLE_FILE")

# Extract version from bundle name
VERSION=$(echo "$BUNDLE_NAME" | sed -E 's/.*-([0-9]+\.[0-9]+\.[0-9]+)$/\1/')

# Generate documentation based on format
generate_markdown() {
    echo "# $BUNDLE_NAME"
    echo ""
    echo "## Overview"
    echo ""
    echo "| Property | Value |"
    echo "|----------|-------|"
    echo "| **Bundle Name** | $BUNDLE_NAME |"
    echo "| **Version** | $VERSION |"
    echo "| **Bundle Type** | $BUNDLE_TYPE |"
    echo "| **Kubernetes Version** | $K8S_VERSION |"
    echo ""

    echo "## Functions"
    echo ""
    echo "| Function | Version |"
    echo "|----------|---------|"

    # Extract functions (CT-CaaS format: combined ref.name)
    awk '
    /^  functions:/ { in_functions=1; next }
    /^  [a-z]/ && !/- / && in_functions { in_functions=0 }
    in_functions && /name:/ {
        gsub(/.*name: *["'\''"]?/, "")
        gsub(/["'\''"].*/, "")
        full_name=$0
        if (match(full_name, /-[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.-]+)?$/)) {
            version = substr(full_name, RSTART+1)
            name = substr(full_name, 1, RSTART-1)
            print "| " name " | " version " |"
        }
    }
    ' "$BUNDLE_FILE" | sort

    echo ""

    # Image versions section
    echo "## Chart/Image Versions"
    echo ""
    if [[ -x "$SCRIPT_DIR/ct-image-versions.sh" ]]; then
        "$SCRIPT_DIR/ct-image-versions.sh" "$BUNDLE_NAME" --format markdown 2>/dev/null || echo "*Version lookup unavailable*"
    else
        echo "*Version lookup script not available*"
    fi
    echo ""

    echo "---"
    echo ""
    echo "*Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")*"
    echo ""
    echo "*Source: $BUNDLE_FILE*"
}

generate_confluence() {
    echo "h1. $BUNDLE_NAME"
    echo ""
    echo "h2. Overview"
    echo ""
    echo "||Property||Value||"
    echo "|Bundle Name|$BUNDLE_NAME|"
    echo "|Version|$VERSION|"
    echo "|Bundle Type|$BUNDLE_TYPE|"
    echo "|Kubernetes Version|$K8S_VERSION|"
    echo ""

    echo "h2. Functions"
    echo ""
    echo "||Function||Version||"

    # Extract functions (CT-CaaS format: combined ref.name)
    awk '
    /^  functions:/ { in_functions=1; next }
    /^  [a-z]/ && !/- / && in_functions { in_functions=0 }
    in_functions && /name:/ {
        gsub(/.*name: *["'\''"]?/, "")
        gsub(/["'\''"].*/, "")
        full_name=$0
        if (match(full_name, /-[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.-]+)?$/)) {
            version = substr(full_name, RSTART+1)
            name = substr(full_name, 1, RSTART-1)
            print "|" name "|" version "|"
        }
    }
    ' "$BUNDLE_FILE" | sort

    echo ""

    echo "h2. Chart/Image Versions"
    echo ""
    if [[ -x "$SCRIPT_DIR/ct-image-versions.sh" ]]; then
        # Get image versions and convert to confluence format
        "$SCRIPT_DIR/ct-image-versions.sh" "$BUNDLE_NAME" --format table 2>/dev/null | \
        awk 'NR==1 { gsub(/\|/, "||"); print "||" $0 "||"; next }
             NR==2 { next }
             { gsub(/  +/, "|"); print "|" $0 "|" }' || echo "_Version lookup unavailable_"
    else
        echo "_Version lookup script not available_"
    fi
    echo ""

    echo "----"
    echo ""
    echo "_Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")_"
    echo ""
    echo "_Source: $BUNDLE_FILE_"
}

generate_json() {
    # Collect functions
    local functions_json=""
    while IFS='|' read -r name version; do
        [[ -z "$name" ]] && continue
        if [[ -n "$functions_json" ]]; then
            functions_json+=","
        fi
        functions_json+=$(printf '{"name":"%s","version":"%s"}' "$name" "$version")
    done < <(awk '
    /^  functions:/ { in_functions=1; next }
    /^  [a-z]/ && !/- / && in_functions { in_functions=0 }
    in_functions && /name:/ {
        gsub(/.*name: *["'\''"]?/, "")
        gsub(/["'\''"].*/, "")
        full_name=$0
        if (match(full_name, /-[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.-]+)?$/)) {
            version = substr(full_name, RSTART+1)
            name = substr(full_name, 1, RSTART-1)
            print name "|" version
        }
    }
    ' "$BUNDLE_FILE")

    cat <<EOF
{
  "bundle": "$BUNDLE_NAME",
  "metadata": {
    "version": "$VERSION",
    "bundle_type": "$BUNDLE_TYPE",
    "kubernetes_version": "$K8S_VERSION"
  },
  "functions": [$functions_json],
  "generated": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "source": "$BUNDLE_FILE"
}
EOF
}

# Generate output
output=""
case "$FORMAT" in
    markdown)
        output=$(generate_markdown)
        ;;
    confluence)
        output=$(generate_confluence)
        ;;
    json)
        output=$(generate_json)
        ;;
    *)
        echo "ERROR: Unknown format: $FORMAT" >&2
        exit 1
        ;;
esac

# Write output
if [[ -n "$OUTPUT_FILE" ]]; then
    echo "$output" > "$OUTPUT_FILE"
    echo "Documentation written to: $OUTPUT_FILE" >&2
else
    echo "$output"
fi
