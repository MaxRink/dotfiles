#!/bin/bash

# Spectral Linting Skill
# Purpose: Validate OpenAPI specifications against security standards and API guidelines
# Supports: OWASP API Security Top 10, Deutsche Telekom G-API guidelines
#
# The script expects to live inside a "spectral/" directory alongside the ruleset files.
# The parent directory of "spectral/" is treated as the specs directory.
#
# Usage: ./spectral-lint.sh <path-to-spec> [OPTIONS]
#
# Examples:
#   ./spectral-lint.sh ../FNCallnumberPortingMgmt/spec/FNCallnumberPortingMgmt.yaml
#   ./spectral-lint.sh .. --all
#   ./spectral-lint.sh ../FNCallnumberPortingMgmtBff/spec/FNCallnumberPortingMgmtBff.yaml --ruleset gapi --verbose

set -e

# Script directory (where this script and rulesets live)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Specs directory is the parent of the spectral/ folder
SPECS_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Rulesets are co-located with this script
OWASP_RULESET="${SCRIPT_DIR}/owasp-linter-rules.spectral.yaml"
GAPI_RULESET="${SCRIPT_DIR}/gapi-linter-rules.spectral.yaml"
RULESET="$OWASP_RULESET"  # Default ruleset

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to display help
show_help() {
    cat << EOF
Spectral Linting Skill - Validate OpenAPI Specifications

USAGE:
    ./spectral-lint.sh <spec-path> [OPTIONS]

ARGUMENTS:
    <spec-path>    Path to OpenAPI spec file or directory (relative or absolute)
                   Examples: ../FNCallnumberPortingMgmt/spec/FNCallnumberPortingMgmt.yaml
                            ..   (parent directory, to lint all specs)

OPTIONS:
    --verbose      Enable verbose output from spectral
    --all          Lint all OpenAPI specifications in the specs directory
    --ruleset      Choose ruleset: 'owasp' (default) or 'gapi'
                   OWASP: API Security Top 10 by OWASP
                   GAPI: Deutsche Telekom G-API guidelines (v2.11.1)
    --help         Display this help message

EXAMPLES:
    # Lint single spec with OWASP rules (default)
    ./spectral-lint.sh ../FNCallnumberPortingMgmt/spec/FNCallnumberPortingMgmt.yaml

    # Lint all specs with OWASP rules
    ./spectral-lint.sh .. --all

    # Lint with G-API rules
    ./spectral-lint.sh ../FNCallnumberPortingMgmtBff/spec/FNCallnumberPortingMgmtBff.yaml --ruleset gapi

    # Lint all specs with G-API rules and verbose output
    ./spectral-lint.sh .. --all --ruleset gapi --verbose

RULESETS:
    OWASP (default): $OWASP_RULESET
    G-API:           $GAPI_RULESET

REQUIREMENTS:
    - Node.js and npm must be installed
    - Run 'npm install' in the spectral/ directory to install dependencies
    - OpenAPI spec files must be present in the parent directory

EOF
}

# Check if spectral is installed locally or globally
check_spectral() {
    local version

    # Try npx from the script directory (local node_modules)
    if version=$(cd "${SCRIPT_DIR}" && npx spectral --version 2>/dev/null); then
        log_success "Spectral CLI found: $version"
        return 0
    fi

    # If npx fails, spectral is not installed
    log_error "Spectral CLI is not installed"
    echo "Install it with: cd ${SCRIPT_DIR} && npm install"
    exit 1
}

# Check if ruleset exists
check_ruleset() {
    local selected_ruleset="$1"

    if [[ ! -f "$selected_ruleset" ]]; then
        log_error "Ruleset not found at: $selected_ruleset"
        exit 1
    fi
    log_success "Ruleset found: $(basename "$selected_ruleset")"
}

# Lint a single specification
lint_spec() {
    local spec_path="$1"
    local verbose="$2"

    if [[ ! -f "$spec_path" ]]; then
        log_error "Spec file not found: $spec_path"
        return 1
    fi

    local filename
    filename=$(basename "$spec_path")
    log_info "Linting: $filename"

    # Build command as array to avoid eval
    local cmd=(npx spectral lint "$spec_path" --ruleset "$RULESET")
    if [[ "$verbose" == "true" ]]; then
        cmd+=(--verbose)
    fi

    # Run from script dir so npx finds local node_modules
    if (cd "${SCRIPT_DIR}" && "${cmd[@]}"); then
        log_success "✓ $filename passed linting"
        return 0
    else
        log_warn "✗ $filename failed linting (see errors above)"
        return 1
    fi
}

# Lint all specifications in a directory
lint_all_specs() {
    local verbose="$1"
    local failed_count=0
    local passed_count=0
    local found_specs=0

    log_info "Linting all OpenAPI specifications in: $SPECS_DIR"
    echo ""

    # Find all YAML/JSON OpenAPI specs, excluding tooling files
    while IFS= read -r spec_file; do
        found_specs=$((found_specs + 1))
        if lint_spec "$spec_file" "$verbose"; then
            passed_count=$((passed_count + 1))
        else
            failed_count=$((failed_count + 1))
        fi
        echo ""
    done < <(find "$SPECS_DIR" -type f \( -name "*.yaml" -o -name "*.yml" -o -name "*.json" \) \
        ! -path "*/target/*" \
        ! -path "*/node_modules/*" \
        ! -path "*/spectral/*" \
        ! -name "package.json" \
        ! -name "package-lock.json" \
        ! -name ".openapi-generator-ignore" \
        | sort)

    if [[ $found_specs -eq 0 ]]; then
        log_warn "No OpenAPI spec files found in: $SPECS_DIR"
        return 1
    fi

    echo ""
    echo "=========================================="
    echo "Linting Summary:"
    log_success "  Passed: $passed_count"
    if [[ $failed_count -gt 0 ]]; then
        log_error "  Failed: $failed_count"
        return 1
    else
        echo "  Failed: 0"
        return 0
    fi
}

# Main script logic
main() {
    if [[ $# -eq 0 ]]; then
        log_error "Missing argument: spec path required"
        echo ""
        show_help
        exit 1
    fi

    # Parse arguments
    local spec_arg="$1"
    local verbose="false"
    local lint_all="false"
    local ruleset_choice="owasp"

    shift || true
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --verbose)
                verbose="true"
                shift
                ;;
            --all)
                lint_all="true"
                shift
                ;;
            --ruleset)
                if [[ -z "${2:-}" ]]; then
                    log_error "Missing ruleset value"
                    echo ""
                    show_help
                    exit 1
                fi
                ruleset_choice="$2"
                shift 2
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                echo ""
                show_help
                exit 1
                ;;
        esac
    done

    # Select ruleset based on choice
    case "$ruleset_choice" in
        owasp)
            RULESET="$OWASP_RULESET"
            ;;
        gapi)
            RULESET="$GAPI_RULESET"
            ;;
        *)
            log_error "Unknown ruleset: $ruleset_choice (use 'owasp' or 'gapi')"
            echo ""
            show_help
            exit 1
            ;;
    esac

    # Check prerequisites
    log_info "Checking prerequisites..."
    check_spectral
    check_ruleset "$RULESET"
    echo ""

    # Resolve relative paths against current working directory
    if [[ "$spec_arg" != /* ]]; then
        spec_arg="$(cd "$(dirname "$spec_arg")" 2>/dev/null && pwd)/$(basename "$spec_arg")"
    fi

    # Lint
    if [[ "$lint_all" == "true" ]]; then
        if lint_all_specs "$verbose"; then
            exit 0
        else
            exit 1
        fi
    else
        # Single file or directory
        if [[ -d "$spec_arg" ]]; then
            # Override SPECS_DIR to the provided directory
            SPECS_DIR="$spec_arg"
            log_info "Linting all specs in directory: $(basename "$spec_arg")"
            if lint_all_specs "$verbose"; then
                exit 0
            else
                exit 1
            fi
        else
            if lint_spec "$spec_arg" "$verbose"; then
                exit 0
            else
                exit 1
            fi
        fi
    fi
}

# Run main function
main "$@"
