#!/bin/bash
# ct-compare-versions.sh - Compare image versions between two CT-CaaS bundle versions
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
    cat <<EOF
Usage: $(basename "$0") <bundle-1> <bundle-2> [OPTIONS]

Compare component versions between two CT-CaaS bundle versions.

Arguments:
    bundle-1        First bundle version (e.g., netbox-workload-34.0.19)
    bundle-2        Second bundle version (e.g., netbox-workload-33.0.0)

Options:
    --format FORMAT Output format: table (default), markdown, json
    --diff-only     Show only components with version differences
    -h, --help      Show this help message

Environment:
    ARTIFACTORY_TOKEN   Required for Helm image version lookup

Examples:
    $(basename "$0") netbox-workload-34.0.19 netbox-workload-33.0.0
    $(basename "$0") netbox-workload-34.0.19 netbox-workload-33.0.0 --diff-only
    $(basename "$0") netbox-workload-34.0.19 netbox-workload-33.0.0 --format markdown
EOF
}

FORMAT="table"
DIFF_ONLY=false
BUNDLE1=""
BUNDLE2=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --diff-only)
            DIFF_ONLY=true
            shift
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
            if [[ -z "$BUNDLE1" ]]; then
                BUNDLE1="$1"
            elif [[ -z "$BUNDLE2" ]]; then
                BUNDLE2="$1"
            else
                echo "ERROR: Too many arguments" >&2
                usage
                exit 1
            fi
            shift
            ;;
    esac
done

if [[ -z "$BUNDLE1" ]] || [[ -z "$BUNDLE2" ]]; then
    echo "ERROR: Two bundle names required" >&2
    usage
    exit 1
fi

# Function to extract version from bundle name (e.g., netbox-workload-34.0.19 -> 34.0.19)
extract_version() {
    echo "$1" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+$'
}

# Function to compare versions (returns 0 if v1 < v2, 1 otherwise)
version_less_than() {
    local v1="$1"
    local v2="$2"
    # Use sort -V to compare versions
    local smaller
    smaller=$(printf '%s\n%s\n' "$v1" "$v2" | sort -V | head -n1)
    [[ "$smaller" == "$v1" && "$v1" != "$v2" ]]
}

# Sort bundles so older version is always first (BUNDLE1 = older, BUNDLE2 = newer)
V1=$(extract_version "$BUNDLE1")
V2=$(extract_version "$BUNDLE2")

if [[ -n "$V1" && -n "$V2" ]]; then
    if version_less_than "$V2" "$V1"; then
        # Swap: BUNDLE2 is older, so make it BUNDLE1
        TEMP="$BUNDLE1"
        BUNDLE1="$BUNDLE2"
        BUNDLE2="$TEMP"
        echo "Note: Reordered to compare from older ($BUNDLE1) to newer ($BUNDLE2)" >&2
    fi
fi

# Check for jq
if ! command -v jq &> /dev/null; then
    echo "ERROR: jq is required but not installed" >&2
    exit 1
fi

# Get image versions for both bundles
echo "Fetching versions for $BUNDLE1..." >&2
JSON1=$("$SCRIPT_DIR/ct-image-versions.sh" "$BUNDLE1" --format json 2>/dev/null) || {
    echo "ERROR: Failed to get versions for $BUNDLE1" >&2
    exit 1
}

echo "Fetching versions for $BUNDLE2..." >&2
JSON2=$("$SCRIPT_DIR/ct-image-versions.sh" "$BUNDLE2" --format json 2>/dev/null) || {
    echo "ERROR: Failed to get versions for $BUNDLE2" >&2
    exit 1
}

# Use jq to merge and compare the two JSON outputs
# Create a unified view keyed by function name + component
RESULTS=$(jq -n --arg b1 "$BUNDLE1" --arg b2 "$BUNDLE2" \
    --argjson j1 "$JSON1" --argjson j2 "$JSON2" \
    -f "$SCRIPT_DIR/compare-versions.jq")

# Filter if diff-only requested
if $DIFF_ONLY; then
    RESULTS=$(echo "$RESULTS" | jq '.comparisons = [.comparisons[] | select(.status != "same")]')
fi

# Count differences
DIFF_COUNT=$(echo "$RESULTS" | jq '[.comparisons[] | select(.status != "same")] | length')
TOTAL_COUNT=$(echo "$RESULTS" | jq '.comparisons | length')

# Output results in requested format
case "$FORMAT" in
    table)
        echo ""
        echo "Comparing: $BUNDLE1 vs $BUNDLE2"
        echo ""
        printf "%-20s %-30s %-15s %-15s %-10s\n" "FUNCTION" "COMPONENT" "$BUNDLE1" "$BUNDLE2" "STATUS"
        printf "%-20s %-30s %-15s %-15s %-10s\n" "--------" "---------" "$(echo "$BUNDLE1" | sed 's/./-/g' | cut -c1-15)" "$(echo "$BUNDLE2" | sed 's/./-/g' | cut -c1-15)" "------"

        echo "$RESULTS" | jq -r '.comparisons[] | [.function, .component, .image_version1, .image_version2, .status] | @tsv' | \
        while IFS=$'\t' read -r func comp v1 v2 status; do
            # Add indicator for changed/added/removed
            case "$status" in
                changed) indicator="*" ;;
                added)   indicator="+" ;;
                removed) indicator="-" ;;
                *)       indicator=" " ;;
            esac
            printf "%-20s %-30s %-15s %-15s %-10s\n" "$func" "$comp" "$v1" "$v2" "$indicator$status"
        done
        ;;

    markdown)
        echo ""
        echo "## Version Comparison: $BUNDLE1 vs $BUNDLE2"
        echo ""
        echo "| Function | Component | $BUNDLE1 | $BUNDLE2 | Status |"
        echo "|----------|-----------|----------|----------|--------|"

        echo "$RESULTS" | jq -r '.comparisons[] | "| \(.function) | \(.component) | \(.image_version1) | \(.image_version2) | \(.status) |"'
        ;;

    json)
        echo "$RESULTS"
        ;;

    *)
        echo "ERROR: Unknown format: $FORMAT" >&2
        exit 1
        ;;
esac

# Print summary
echo "" >&2
if [[ "$DIFF_COUNT" -eq 0 ]]; then
    echo "Summary: No component version differences found between $BUNDLE1 and $BUNDLE2." >&2
    echo "This is OK - the bundles may differ only in Kubernetes version or other metadata." >&2
else
    echo "Summary: $DIFF_COUNT of $TOTAL_COUNT components have version differences." >&2
fi
