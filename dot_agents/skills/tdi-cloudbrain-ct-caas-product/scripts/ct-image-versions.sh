#!/bin/bash
# ct-image-versions.sh - Extract container image versions from CT-CaaS function definitions
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
Usage: $(basename "$0") <bundle-name> [OPTIONS]

Extract component versions from CT-CaaS function definitions.

Extracts:
    - Helm chart names, versions, and container image versions (appVersion)
    - Kustomize release names and OCI references
    - Container images from kustomize image overrides

Arguments:
    bundle-name    The bundle name (e.g., netbox-workload-34.0.19)

Options:
    --format FORMAT Output format: table (default), json, markdown
    -h, --help      Show this help message

Environment:
    ARTIFACTORY_TOKEN   Required for Helm image version lookup

Examples:
    $(basename "$0") netbox-workload-34.0.19
    $(basename "$0") netbox-workload-34.0.19 --format markdown
    $(basename "$0") openstack-management-33.6.6 --format json

Requires: yq (https://github.com/mikefarah/yq)
EOF
}

FORMAT="table"
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

CT_BUNDLES=$(find_ct_bundles)
BUNDLES_DIR="$CT_BUNDLES/bundles"
FUNCTIONDEFS_DIR="$CT_BUNDLES/functiondefinitions"

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
    exit 1
fi

# OCI Registry base URL for CT-CaaS charts
OCI_REGISTRY_URL="https://artifactory.devops.telekom.de/v2/cit-t-caas-oci/charts"

# Clean template variables from chart path
# Input: "{{ .config.sources.registry.mirrors.charts.path }}/kyverno/kyverno"
# Output: "kyverno/kyverno"
clean_chart_path() {
    local raw_path="$1"
    # Remove the Go template variable and leading slash
    echo "$raw_path" | sed -E 's/^\{\{[^}]+\}\}\///'
}

# Check if a tag value is a placeholder that should be ignored
is_placeholder_tag() {
    local tag="$1"
    # Ignore: empty, "latest", template variables like "vX.Y.Z" or "{{ ... }}"
    if [[ -z "$tag" ]] || \
       [[ "$tag" == "latest" ]] || \
       [[ "$tag" =~ ^v?X\.Y\.Z$ ]] || \
       [[ "$tag" =~ \{\{ ]]; then
        return 0  # true - is placeholder
    fi
    return 1  # false - is valid
}

# Extract image tag from chart directory, trying multiple patterns
extract_image_tag_from_chart() {
    local chart_dir="$1"
    local chart_name="${2:-}"  # Optional: chart name for special handling
    local tag=""

    local values_file="$chart_dir/values.yaml"
    local chart_file="$chart_dir/Chart.yaml"

    if [[ -f "$values_file" ]]; then
        # Pattern 1: image.tag at root level (most common)
        tag=$(awk '
            /^image:/{found=1; next}
            found && /^[a-zA-Z]/ {exit}  # Stop at next top-level key
            found && /tag:/ {
                gsub(/.*tag:[[:space:]]*/, "")
                gsub(/^["'\'']/, "")
                gsub(/["'\''].*$/, "")
                if ($0 != "" && $0 !~ /^[[:space:]]*$/) {
                    print
                }
                exit
            }
        ' "$values_file" 2>/dev/null)

        # Check if tag is a placeholder
        if is_placeholder_tag "$tag"; then
            tag=""
        fi

        # Pattern 2: global.image.tag (used by some charts like fluent-bit, kyverno)
        if [[ -z "$tag" ]]; then
            tag=$(awk '
                /^global:/{in_global=1; next}
                in_global && /^[a-zA-Z]/ && !/^[[:space:]]/ {in_global=0}
                in_global && /[[:space:]]+image:/{in_image=1; next}
                in_global && in_image && /^[a-zA-Z]/ {in_image=0}  # Exit on next top-level key under global
                in_global && in_image && /[[:space:]]+tag:/ {
                    gsub(/.*tag:[[:space:]]*/, "")
                    gsub(/^["'\'']/, "")
                    gsub(/["'\''].*$/, "")
                    if ($0 != "" && $0 !~ /^[[:space:]]*$/) {
                        print
                    }
                    exit
                }
            ' "$values_file" 2>/dev/null)

            if is_placeholder_tag "$tag"; then
                tag=""
            fi
        fi

        # Pattern 3: controller.image.tag (used by ingress-nginx)
        if [[ -z "$tag" ]]; then
            tag=$(awk '
                /^controller:/{in_ctrl=1; next}
                in_ctrl && /^[a-zA-Z]/ && !/^[[:space:]]/ {in_ctrl=0}
                in_ctrl && /image:/{in_image=1; next}
                in_ctrl && in_image && /^[[:space:]]+[a-zA-Z]/ && !/tag:/ && !/digest:/ && !/registry:/ && !/repository:/ {in_image=0}
                in_ctrl && in_image && /tag:/ {
                    gsub(/.*tag:[[:space:]]*/, "")
                    gsub(/^["'\'']/, "")
                    gsub(/["'\''].*$/, "")
                    if ($0 != "" && $0 !~ /^[[:space:]]*$/) {
                        print
                    }
                    exit
                }
            ' "$values_file" 2>/dev/null)

            if is_placeholder_tag "$tag"; then
                tag=""
            fi
        fi

        # Pattern 3b: fluent-bit specific - collector.image.tag or forwarder.image.tag
        if [[ -z "$tag" ]]; then
            tag=$(awk '
                /^(collector|forwarder):/{in_section=1; next}
                in_section && /^[a-zA-Z]/ && !/^[[:space:]]/ {in_section=0}
                in_section && /image:/{in_image=1; next}
                in_section && in_image && /^[[:space:]]+[a-zA-Z]/ && !/tag:/ && !/digest:/ && !/registry:/ && !/repository:/ {in_image=0}
                in_section && in_image && /tag:/ {
                    gsub(/.*tag:[[:space:]]*/, "")
                    gsub(/^["'\'']/, "")
                    gsub(/["'\''].*$/, "")
                    if ($0 != "" && $0 !~ /^[[:space:]]*$/) {
                        print
                    }
                    exit
                }
            ' "$values_file" 2>/dev/null)

            if is_placeholder_tag "$tag"; then
                tag=""
            fi
        fi

        # Pattern 3c: Chart name as top-level key (e.g., fluent-bit.image.tag)
        if [[ -z "$tag" ]] && [[ -n "$chart_name" ]]; then
            tag=$(awk -v name="$chart_name" '
                $0 ~ "^" name ":"{in_section=1; next}
                in_section && /^[a-zA-Z]/ && !/^[[:space:]]/ {in_section=0}
                in_section && /image:/{in_image=1; next}
                in_section && in_image && /^[[:space:]]+[a-zA-Z]/ && !/tag:/ {in_image=0}
                in_section && in_image && /tag:/ {
                    gsub(/.*tag:[[:space:]]*/, "")
                    gsub(/^["'\'']/, "")
                    gsub(/["'\''].*$/, "")
                    if ($0 != "" && $0 !~ /^[[:space:]]*$/) {
                        print
                    }
                    exit
                }
            ' "$values_file" 2>/dev/null)

            if is_placeholder_tag "$tag"; then
                tag=""
            fi
        fi
    fi

    # Pattern 4: Check for bundled sub-charts in charts/ directory FIRST
    # Wrapper charts may bundle the upstream chart directly - prefer sub-chart appVersion
    if [[ -z "$tag" ]] && [[ -d "$chart_dir/charts" ]]; then
        # First try exact name match (unpacked directory)
        local sub_chart_dir="$chart_dir/charts/$chart_name"
        if [[ -f "$sub_chart_dir/Chart.yaml" ]]; then
            tag=$(awk '/^appVersion:/ {
                gsub(/.*appVersion:[[:space:]]*/, "")
                gsub(/^["'\'']/, "")
                gsub(/["'\''].*$/, "")
                print
            }' "$sub_chart_dir/Chart.yaml" 2>/dev/null)
        fi

        # Try .tgz files in charts/ directory (common for helm dependencies)
        if [[ -z "$tag" ]]; then
            local sub_tgz
            # First try exact name match
            sub_tgz="$chart_dir/charts/${chart_name}-"*.tgz
            if ! compgen -G "$sub_tgz" > /dev/null 2>&1; then
                # Fallback to first .tgz found
                sub_tgz=$(find "$chart_dir/charts" -maxdepth 1 -name "*.tgz" 2>/dev/null | head -1)
            else
                sub_tgz=$(compgen -G "$sub_tgz" | head -1)
            fi

            if [[ -n "$sub_tgz" ]] && [[ -f "$sub_tgz" ]]; then
                # Extract Chart.yaml from the tgz and get appVersion
                tag=$(tar -xzf "$sub_tgz" -O --wildcards "*/Chart.yaml" 2>/dev/null | awk '/^appVersion:/ {
                    gsub(/.*appVersion:[[:space:]]*/, "")
                    gsub(/^["'\'']/, "")
                    gsub(/["'\''].*$/, "")
                    print
                    exit
                }')
            fi
        fi

        # If no tgz match, try first unpacked sub-chart directory
        if [[ -z "$tag" ]]; then
            local first_sub_chart
            first_sub_chart=$(find "$chart_dir/charts" -maxdepth 1 -type d ! -name charts 2>/dev/null | head -1)
            if [[ -n "$first_sub_chart" ]] && [[ -f "$first_sub_chart/Chart.yaml" ]]; then
                tag=$(awk '/^appVersion:/ {
                    gsub(/.*appVersion:[[:space:]]*/, "")
                    gsub(/^["'\'']/, "")
                    gsub(/["'\''].*$/, "")
                    print
                }' "$first_sub_chart/Chart.yaml" 2>/dev/null)
            fi
        fi
    fi

    # Pattern 5: For wrapper charts, fetch appVersion from the dependency chart
    # This handles cases like t-caas/fluent-bit which wraps upstream fluent-bit
    if [[ -z "$tag" ]] && [[ -f "$chart_file" ]] && [[ -n "$chart_name" ]]; then
        local dep_info
        dep_info=$(extract_dependency_info "$chart_file" "$chart_name")
        if [[ -z "$dep_info" ]]; then
            # Try first dependency if no exact match
            dep_info=$(extract_dependency_info "$chart_file" | head -1)
        fi

        if [[ -n "$dep_info" ]]; then
            local dep_name dep_version dep_repo
            IFS='|' read -r dep_name dep_version dep_repo <<< "$dep_info"
            if [[ -n "$dep_name" ]] && [[ -n "$dep_version" ]]; then
                tag=$(fetch_dependency_app_version "$dep_name" "$dep_version" "$dep_repo")
            fi
        fi
    fi

    # Pattern 6: Known wrapper chart mappings - fallback for charts without explicit dependencies
    # These are t-caas wrapper charts where we know the upstream chart location
    if [[ -z "$tag" ]] && [[ -f "$chart_file" ]] && [[ -n "$chart_name" ]]; then
        local upstream_version
        upstream_version=$(get_known_wrapper_upstream_version "$chart_name" "$chart_file")
        if [[ -n "$upstream_version" ]]; then
            tag="$upstream_version"
        fi
    fi

    # Fallback: If tag is still empty, get appVersion from Chart.yaml
    if [[ -z "$tag" ]] && [[ -f "$chart_file" ]]; then
        tag=$(awk '/^appVersion:/ {
            gsub(/.*appVersion:[[:space:]]*/, "")
            gsub(/^["'\'']/, "")
            gsub(/["'\''].*$/, "")
            print
        }' "$chart_file" 2>/dev/null)
    fi

    echo "$tag"
}

# Extract dependency info (name, version, repository) from Chart.yaml
# Returns: name|version|repository
extract_dependency_info() {
    local chart_file="$1"
    local target_name="${2:-}"  # Optional: specific dependency name to find

    # Parse dependencies section
    awk -v target="$target_name" '
        /^dependencies:/{in_deps=1; next}
        in_deps && /^[a-zA-Z]/ && !/^[[:space:]]/ {exit}
        in_deps && /- name:/ || (in_deps && /^[[:space:]]+name:/) {
            if (current_name != "" && current_version != "") {
                if (target == "" || current_name == target) {
                    print current_name "|" current_version "|" current_repo
                    if (target != "") exit
                }
            }
            gsub(/.*name:[[:space:]]*/, "")
            gsub(/^["'\'']/, "")
            gsub(/["'\''].*$/, "")
            current_name=$0
            current_version=""
            current_repo=""
        }
        in_deps && /version:/ {
            gsub(/.*version:[[:space:]]*/, "")
            gsub(/^["'\'']/, "")
            gsub(/["'\''].*$/, "")
            current_version=$0
        }
        in_deps && /repository:/ {
            gsub(/.*repository:[[:space:]]*/, "")
            gsub(/^["'\'']/, "")
            gsub(/["'\''].*$/, "")
            current_repo=$0
        }
        END {
            if (in_deps && current_name != "" && current_version != "") {
                if (target == "" || current_name == target) {
                    print current_name "|" current_version "|" current_repo
                }
            }
        }
    ' "$chart_file" 2>/dev/null
}

# Fetch appVersion from a dependency chart in the OCI registry
# This handles wrapper charts like t-caas/fluent-bit that depend on upstream charts
fetch_dependency_app_version() {
    local dep_name="$1"
    local dep_version="$2"
    local dep_repo="$3"

    if [[ -z "${ARTIFACTORY_TOKEN:-}" ]] || [[ -z "$dep_name" ]] || [[ -z "$dep_version" ]]; then
        echo ""
        return
    fi

    # Build the chart path from repository URL
    # Common patterns:
    #   oci://registry/path -> path/chart_name
    #   https://charts.example.com -> (not supported, skip)
    local chart_path=""
    if [[ "$dep_repo" =~ ^oci:// ]]; then
        # Extract path after oci://hostname/
        chart_path=$(echo "$dep_repo" | sed -E 's|^oci://[^/]+/||')
        chart_path="${chart_path}/${dep_name}"
    elif [[ -z "$dep_repo" ]] || [[ "$dep_repo" == "file://"* ]]; then
        # No repository or local file - try common upstream paths
        # Known mappings for t-caas wrapper charts
        case "$dep_name" in
            fluent-bit)
                chart_path="fluent/fluent-bit"
                ;;
            *)
                # Skip - can't determine path
                echo ""
                return
                ;;
        esac
    else
        # HTTPS or other - not supported
        echo ""
        return
    fi

    # Try to fetch the dependency chart
    local manifest
    manifest=$(curl -sf -H "Authorization: Bearer $ARTIFACTORY_TOKEN" \
        -H "Accept: application/vnd.oci.image.manifest.v1+json" \
        "$OCI_REGISTRY_URL/$chart_path/manifests/$dep_version" 2>/dev/null)

    if [[ -z "$manifest" ]]; then
        echo ""
        return
    fi

    local layer_digest
    layer_digest=$(printf '%s' "$manifest" | jq -r '.layers[0].digest' 2>/dev/null)

    if [[ -z "$layer_digest" ]] || [[ "$layer_digest" == "null" ]]; then
        echo ""
        return
    fi

    # Download and extract appVersion
    local tmp_file
    tmp_file=$(mktemp)
    local app_version=""

    if curl -sf -H "Authorization: Bearer $ARTIFACTORY_TOKEN" \
        "$OCI_REGISTRY_URL/$chart_path/blobs/$layer_digest" \
        -o "$tmp_file" 2>/dev/null; then

        app_version=$(tar -xzf "$tmp_file" -O --wildcards "*/Chart.yaml" 2>/dev/null | awk '/^appVersion:/ {
            gsub(/.*appVersion:[[:space:]]*/, "")
            gsub(/^["'\'']/, "")
            gsub(/["'\''].*$/, "")
            print
            exit
        }')
    fi

    rm -f "$tmp_file"
    echo "$app_version"
}

# Known wrapper chart mappings for t-caas charts
# Returns upstream appVersion for known wrapper charts
get_known_wrapper_upstream_version() {
    local chart_name="$1"
    local chart_file="$2"

    if [[ -z "${ARTIFACTORY_TOKEN:-}" ]]; then
        echo ""
        return
    fi

    # Map of t-caas wrapper charts to their upstream chart paths
    # Format: wrapper_name -> upstream_path
    local upstream_path=""
    local upstream_version=""

    case "$chart_name" in
        fluent-bit)
            upstream_path="fluent/fluent-bit"
            # Extract the upstream version from values.yaml or use a known pattern
            # The t-caas fluent-bit wrapper specifies the upstream chart version in Chart.yaml or values
            # Try to extract from Chart.yaml dependencies first
            upstream_version=$(awk '
                /^dependencies:/{in_deps=1; next}
                in_deps && /^[a-zA-Z]/ && !/^[[:space:]]/ {exit}
                in_deps && /version:/ {
                    gsub(/.*version:[[:space:]]*/, "")
                    gsub(/^["'\'']/, "")
                    gsub(/["'\''].*$/, "")
                    if ($0 != "" && $0 !~ /^[[:space:]]*$/) {
                        print
                        exit
                    }
                }
            ' "$chart_file" 2>/dev/null)
            ;;
        *)
            echo ""
            return
            ;;
    esac

    if [[ -z "$upstream_path" ]] || [[ -z "$upstream_version" ]]; then
        echo ""
        return
    fi

    # Fetch the upstream chart and get its appVersion
    fetch_dependency_app_version "$chart_name" "$upstream_version" ""
}

# Lookup image tag from OCI registry by downloading chart and extracting from values.yaml or Chart.yaml
lookup_oci_image_tag() {
    local chart_name="$1"
    local chart_version="$2"
    local chart_path_raw="${3:-}"  # Optional: path from function definition

    if [[ -z "${ARTIFACTORY_TOKEN:-}" ]]; then
        echo ""
        return
    fi

    # Use the path from the function definition if provided
    local chart_path=""
    if [[ -n "$chart_path_raw" ]]; then
        chart_path=$(clean_chart_path "$chart_path_raw")
    fi

    # If no path provided, skip (don't guess)
    if [[ -z "$chart_path" ]]; then
        echo ""
        return
    fi

    # Try different version formats (with and without v prefix)
    local chart_versions=("$chart_version")
    if [[ "$chart_version" == v* ]]; then
        chart_versions+=("${chart_version#v}")  # Also try without v prefix
    else
        chart_versions+=("v${chart_version}")   # Also try with v prefix
    fi

    for ver in "${chart_versions[@]}"; do
        # Get OCI manifest to find the layer digest
        local manifest
        manifest=$(curl -sf -H "Authorization: Bearer $ARTIFACTORY_TOKEN" \
            -H "Accept: application/vnd.oci.image.manifest.v1+json" \
            "$OCI_REGISTRY_URL/$chart_path/manifests/$ver" 2>/dev/null)

        if [[ -z "$manifest" ]]; then
            continue
        fi

        # Extract layer digest (use printf to preserve special chars in JSON)
        local layer_digest
        layer_digest=$(printf '%s' "$manifest" | jq -r '.layers[0].digest' 2>/dev/null)

        if [[ -z "$layer_digest" ]] || [[ "$layer_digest" == "null" ]]; then
            continue
        fi

        # Download and extract chart
        local tmp_dir
        tmp_dir=$(mktemp -d)
        local tag=""

        if curl -sf -H "Authorization: Bearer $ARTIFACTORY_TOKEN" \
            "$OCI_REGISTRY_URL/$chart_path/blobs/$layer_digest" \
            -o "$tmp_dir/chart.tgz" 2>/dev/null; then

            if tar -xzf "$tmp_dir/chart.tgz" -C "$tmp_dir" 2>/dev/null; then
                # Find the extracted chart directory (may differ from chart_name)
                local chart_dir
                chart_dir=$(find "$tmp_dir" -maxdepth 1 -type d ! -name "$(basename "$tmp_dir")" | head -1)

                if [[ -n "$chart_dir" ]]; then
                    tag=$(extract_image_tag_from_chart "$chart_dir" "$chart_name")
                fi
            fi
        fi

        rm -rf "$tmp_dir"

        if [[ -n "$tag" ]]; then
            echo "$tag"
            return
        fi
    done

    echo ""
}

# Find function definition file
find_functiondef_file() {
    local full_name="$1"  # e.g., "coredns-0.3.1"

    # Search in all subdirectories
    local found
    found=$(find "$FUNCTIONDEFS_DIR" -name "${full_name}.yaml" 2>/dev/null | head -1)

    if [[ -n "$found" ]]; then
        echo "$found"
        return
    fi

    echo ""
}

# Extract Helm chart info from function definition file using yq
# CT-CaaS format: spec.releases[].helm.name and spec.releases[].helm.version
# Also extracts the chart path from helm.provider.flux.repo.path or helm.provider.manual.repo.path
extract_helm_info() {
    local func_file="$1"

    yq '
        .spec.releases.[] |
        select(has("helm")) |
        "helm|" + .helm.name + "|" + (.helm.version | tostring) + "|" + (.helm.provider.flux.repo.path // .helm.provider.manual.repo.path // "")
    ' "$func_file" 2>/dev/null
}

# Extract Kustomize version from function definition file using yq
# CT-CaaS format: spec.releases[].kustomize.provider.flux.repo.oci.reference
extract_kustomize_info() {
    local func_file="$1"

    yq -r '
        .spec.releases[]? |
        select(.kustomize != null) |
        .name as $name |
        .kustomize.provider.flux.repo.oci.reference // .kustomize.provider.manual.repo.git.reference |
        select(. != null) |
        "kustomize|" + $name + "|" + .
    ' "$func_file" 2>/dev/null
}

# Extract container images from kustomize images block using yq
# Returns full image names like docker.io/calico/node
extract_kustomize_images() {
    local func_file="$1"

    yq -r '
        .spec.releases[]? |
        select(.kustomize != null) |
        .kustomize.images[]?.name |
        select(. != null and (. | test("\\{\\{") | not)) |
        "image|" + . + "|"
    ' "$func_file" 2>/dev/null
}

# Temp file for results
RESULTS_FILE=$(mktemp)
trap "rm -f $RESULTS_FILE" EXIT

# Temp file for function list
FUNC_LIST=$(mktemp)
trap "rm -f $RESULTS_FILE $FUNC_LIST" EXIT

# Extract functions to temp file first (CT-CaaS format: combined name-version)
awk '
/^  functions:/ { in_functions=1; next }
/^  [a-z]/ && !/- / && in_functions { in_functions=0 }
in_functions && /name:/ {
    gsub(/.*name: *["'\''"]?/, "")
    gsub(/["'\''"].*/, "")
    full_name=$0
    # Split on last version pattern
    if (match(full_name, /-[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.-]+)?$/)) {
        version = substr(full_name, RSTART+1)
        name = substr(full_name, 1, RSTART-1)
        print name "|" version "|" full_name
    }
}
' "$BUNDLE_FILE" > "$FUNC_LIST"

# Process each function
while IFS='|' read -r func_name func_version full_name; do
    [[ -z "$func_name" ]] && continue

    func_file=$(find_functiondef_file "$full_name")

    if [[ -z "$func_file" ]]; then
        echo "$func_name|$func_version|||Function definition not found" >> "$RESULTS_FILE"
        continue
    fi

    # Get Helm chart info
    helm_info=$(extract_helm_info "$func_file")

    # Get Kustomize info
    kustomize_info=$(extract_kustomize_info "$func_file")

    if [[ -n "$helm_info" ]]; then
        # Process Helm releases - lookup image version from OCI registry
        while IFS='|' read -r type chart_name chart_version chart_path; do
            [[ -z "$chart_name" ]] && continue

            # Lookup image version from OCI registry using chart path from function definition
            image_version=$(lookup_oci_image_tag "$chart_name" "$chart_version" "$chart_path")

            echo "$func_name|$func_version|$chart_name (helm)|$chart_version|$image_version|" >> "$RESULTS_FILE"
        done <<< "$helm_info"
    fi

    if [[ -n "$kustomize_info" ]]; then
        # Process Kustomize releases - OCI reference IS the version
        while IFS='|' read -r type release_name kust_version; do
            [[ -z "$release_name" ]] && continue
            echo "$func_name|$func_version|$release_name (kustomize)|$kust_version|$kust_version|" >> "$RESULTS_FILE"
        done <<< "$kustomize_info"
    fi

    # Extract kustomize images for functions with kustomize
    kust_images=$(extract_kustomize_images "$func_file")
    if [[ -n "$kust_images" ]]; then
        while IFS='|' read -r type image_name _; do
            [[ -z "$image_name" ]] && continue
            echo "$func_name|$func_version|$image_name|image|-|" >> "$RESULTS_FILE"
        done <<< "$kust_images"
    fi

    if [[ -z "$helm_info" ]] && [[ -z "$kustomize_info" ]] && [[ -z "$kust_images" ]]; then
        echo "$func_name|$func_version||||No releases found" >> "$RESULTS_FILE"
    fi
done < "$FUNC_LIST"

# Output results
case "$FORMAT" in
    table)
        echo "FUNCTION|VERSION|COMPONENT|TYPE/VERSION|IMAGE_VERSION|NOTES"
        echo "--------|-------|---------|------------|-------------|-----"
        if [[ -s "$RESULTS_FILE" ]]; then
            cat "$RESULTS_FILE" | column -t -s'|'
        fi
        ;;

    markdown)
        echo "| Function | Version | Component | Type/Version | Image Version | Notes |"
        echo "|----------|---------|-----------|--------------|---------------|-------|"
        if [[ -s "$RESULTS_FILE" ]]; then
            while IFS='|' read -r func ver component type_ver image_ver notes; do
                echo "| $func | $ver | $component | $type_ver | $image_ver | $notes |"
            done < "$RESULTS_FILE"
        fi
        ;;

    json)
        echo "{"
        echo "  \"bundle\": \"$BUNDLE_NAME\","
        echo "  \"components\": ["
        if [[ -s "$RESULTS_FILE" ]]; then
            first=true
            while IFS='|' read -r func ver component type_ver image_ver notes; do
                if $first; then
                    first=false
                else
                    echo ","
                fi
                printf '    {"function": "%s", "function_version": "%s", "component": "%s", "type_version": "%s", "image_version": "%s", "notes": "%s"}' \
                    "$func" "$ver" "$component" "$type_ver" "$image_ver" "$notes"
            done < "$RESULTS_FILE"
            echo ""
        fi
        echo "  ]"
        echo "}"
        ;;

    *)
        echo "ERROR: Unknown format: $FORMAT" >&2
        exit 1
        ;;
esac
