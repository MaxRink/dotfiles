#!/usr/bin/env bash
#
# Phase 14 Orchestration Script
# Handles validation and summary - agent launch done by command
#
# Usage: run-phase14.sh <feature-name> <stage>
#   stage: "validate" | "summarize"
#
# Phase 14 is UNIFIED - works for both NEW and CHANGE modes
# Output always goes to results/phase14/ (external test artifacts)
#

set -e

FEATURE="$1"
STAGE="$2"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT}"
RESULTS_DIR="results/${FEATURE}"
PHASE_DIR="${RESULTS_DIR}/phase14"
CONTEXT_FILE="${RESULTS_DIR}/.workflow-context.json"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

#
# Read workflow mode from .workflow-context.json
#
get_workflow_mode() {
  if [ -f "${CONTEXT_FILE}" ] && command -v jq &> /dev/null; then
    jq -r '.workflow_mode // "UNKNOWN"' "${CONTEXT_FILE}" 2>/dev/null || echo "UNKNOWN"
  elif [ -f "${CONTEXT_FILE}" ]; then
    # Fallback without jq - simple grep
    grep -o '"workflow_mode"[[:space:]]*:[[:space:]]*"[^"]*"' "${CONTEXT_FILE}" 2>/dev/null | \
      sed 's/.*"workflow_mode"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/' || echo "UNKNOWN"
  else
    echo "UNKNOWN"
  fi
}

#
# Validate Phase 11 prerequisites (test scenarios)
#
validate_common_prerequisites() {
  local errors=0

  echo -e "${BLUE}Checking Phase 11 prerequisites...${NC}"
  echo ""

  # Phase 11 - Test Scenarios (required for system test script generation)
  if [ -f "${RESULTS_DIR}/phase11/test-scenarios.json" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 11: test-scenarios.json"
  else
    echo -e "  ${RED}✗${NC} Phase 11: test-scenarios.json missing"
    errors=$((errors + 1))
  fi

  if [ -f "${RESULTS_DIR}/phase11/test-scenarios.md" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 11: test-scenarios.md"
  else
    echo -e "  ${RED}✗${NC} Phase 11: test-scenarios.md missing"
    errors=$((errors + 1))
  fi

  echo ""
  return $errors
}

#
# Validate mode-specific prerequisites
#
validate_mode_prerequisites() {
  local mode="$1"
  local errors=0

  echo -e "${BLUE}Checking ${mode} mode prerequisites...${NC}"
  echo ""

  if [ "$mode" = "NEW" ]; then
    # NEW mode: Need Phase 13 source code
    if [ -d "${RESULTS_DIR}/phase13/source_code" ]; then
      echo -e "  ${GREEN}✓${NC} Phase 13: source_code/ directory exists"

      # Count generated files
      if command -v find &> /dev/null; then
        JAVA_FILES=$(find "${RESULTS_DIR}/phase13/source_code" -name "*.java" 2>/dev/null | wc -l)
        echo -e "  ${CYAN}   Java files: ${JAVA_FILES}${NC}"
      fi
    else
      echo -e "  ${RED}✗${NC} Phase 13: source_code/ directory missing"
      errors=$((errors + 1))
    fi

    if [ -f "${RESULTS_DIR}/phase13/security_scan.txt" ]; then
      echo -e "  ${GREEN}✓${NC} Phase 13: security_scan.txt"
    else
      echo -e "  ${YELLOW}⚠${NC} Phase 13: security_scan.txt missing (optional)"
    fi

  elif [ "$mode" = "CHANGE" ]; then
    # CHANGE mode: Need Phase 13.1 applied changes
    if [ -f "${RESULTS_DIR}/phase13.1/applied-edits-log.json" ]; then
      echo -e "  ${GREEN}✓${NC} Phase 13.1: applied-edits-log.json"

      # Extract statistics if jq available
      if command -v jq &> /dev/null; then
        FILES_CREATED=$(jq -r '.files_created | length // 0' "${RESULTS_DIR}/phase13.1/applied-edits-log.json" 2>/dev/null || echo "0")
        FILES_MODIFIED=$(jq -r '.files_modified | length // 0' "${RESULTS_DIR}/phase13.1/applied-edits-log.json" 2>/dev/null || echo "0")
        echo -e "  ${CYAN}   Files created: ${FILES_CREATED}, modified: ${FILES_MODIFIED}${NC}"
      fi
    else
      echo -e "  ${RED}✗${NC} Phase 13.1: applied-edits-log.json missing"
      errors=$((errors + 1))
    fi

    if [ -f "${RESULTS_DIR}/phase13.1/code-changes-manifest.json" ]; then
      echo -e "  ${GREEN}✓${NC} Phase 13.1: code-changes-manifest.json"
    else
      echo -e "  ${YELLOW}⚠${NC} Phase 13.1: code-changes-manifest.json missing (optional)"
    fi

    # Check Phase 6 baseline for repository context
    if [ -f "${RESULTS_DIR}/phase6/analysis.json" ]; then
      echo -e "  ${GREEN}✓${NC} Phase 6: analysis.json (baseline context)"

      # Get repository_path for display
      if command -v jq &> /dev/null; then
        REPO_PATH=$(jq -r '.repository_path // empty' "${RESULTS_DIR}/phase6/analysis.json" 2>/dev/null)
        if [ -n "$REPO_PATH" ]; then
          echo -e "  ${CYAN}   VNRM repo: ${REPO_PATH}${NC}"
        fi
      fi
    else
      echo -e "  ${YELLOW}⚠${NC} Phase 6: analysis.json missing (baseline context)"
    fi
  fi

  echo ""
  return $errors
}

#
# VALIDATION STAGE
#
if [ "$STAGE" = "validate" ]; then
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}Phase 14: Generate System Test Scripts${NC}"
  echo -e "${BLUE}Feature: ${FEATURE}${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

  # Read workflow mode
  WORKFLOW_MODE=$(get_workflow_mode)
  echo -e "${CYAN}Workflow Mode: ${WORKFLOW_MODE}${NC}"
  echo -e "${CYAN}Phase 14 Type: UNIFIED (works for both NEW and CHANGE)${NC}"
  echo ""

  # Validate common prerequisites
  validate_common_prerequisites
  COMMON_ERRORS=$?

  # Validate mode-specific prerequisites
  validate_mode_prerequisites "$WORKFLOW_MODE"
  MODE_ERRORS=$?

  TOTAL_ERRORS=$((COMMON_ERRORS + MODE_ERRORS))

  if [ $TOTAL_ERRORS -gt 0 ]; then
    echo -e "${RED}Validation failed - ${TOTAL_ERRORS} prerequisite(s) missing${NC}"
    echo ""
    if [ "$WORKFLOW_MODE" = "NEW" ]; then
      echo "Please complete Phase 13 first:"
      echo "  /rnvs-workflow:phase13-generate-source-code"
    else
      echo "Please complete Phase 13.1 first:"
      echo "  /rnvs-workflow:phase13.1-generate-source-code"
    fi
    exit 2
  fi

  # Create output directory structure
  mkdir -p "${PHASE_DIR}/test_scripts"/{postman,jmeter,integration,security,data}

  echo -e "${GREEN}Validation complete - ready for system test script generation${NC}"
  echo ""

  # Show input files
  echo -e "${BLUE}Input files for test script generation:${NC}"
  echo "   Phase 11 Test Scenarios:"
  echo "     - phase11/test-scenarios.json"
  echo "     - phase11/test-scenarios.md"
  echo ""

  if [ "$WORKFLOW_MODE" = "NEW" ]; then
    echo "   Source Code Context (NEW mode):"
    echo "     - phase13/source_code/"
    echo ""
    echo -e "${CYAN}Scope: Generate tests for ALL endpoints${NC}"
  elif [ "$WORKFLOW_MODE" = "CHANGE" ]; then
    echo "   Source Code Context (CHANGE mode):"
    echo "     - phase13.1/applied-edits-log.json"
    echo "     - phase6/analysis.json (baseline)"
    echo ""
    echo -e "${CYAN}Scope: Generate tests for CHANGED endpoints only${NC}"
  fi
  echo ""

  echo -e "${BLUE}Target Outputs:${NC}"
  echo "   results/${FEATURE}/phase14/"
  echo "     - test_scripts/postman/ (API test collections)"
  echo "     - test_scripts/jmeter/ (performance test plans)"
  echo "     - test_scripts/integration/ (pytest scripts)"
  echo "     - test_scripts/security/ (OWASP ZAP scripts)"
  echo "     - test_scripts/data/ (test data setup)"
  echo "     - test_scripts/run_all_tests.sh"
  echo "     - test_execution_guide.md"
  echo ""
  echo -e "${BLUE}Launching agent to generate system test scripts...${NC}"
  echo ""

#
# SUMMARY STAGE
#
elif [ "$STAGE" = "summarize" ]; then
  echo ""
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}Phase 14 Complete - System Test Scripts${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

  # Read workflow mode for display
  WORKFLOW_MODE=$(get_workflow_mode)

  echo -e "${CYAN}Workflow Mode:${NC} ${WORKFLOW_MODE} (Phase 14 is unified)"
  echo ""

  # Count generated test artifacts
  echo -e "${YELLOW}Test Script Summary:${NC}"

  # Postman collections
  if [ -d "${PHASE_DIR}/test_scripts/postman" ]; then
    POSTMAN_FILES=$(find "${PHASE_DIR}/test_scripts/postman" -name "*.json" 2>/dev/null | wc -l)
    echo "  Postman collections: ${POSTMAN_FILES}"
  else
    echo "  Postman collections: 0"
  fi

  # JMeter test plans
  if [ -d "${PHASE_DIR}/test_scripts/jmeter" ]; then
    JMETER_FILES=$(find "${PHASE_DIR}/test_scripts/jmeter" -name "*.jmx" 2>/dev/null | wc -l)
    echo "  JMeter test plans: ${JMETER_FILES}"
  else
    echo "  JMeter test plans: 0"
  fi

  # pytest integration tests
  if [ -d "${PHASE_DIR}/test_scripts/integration" ]; then
    PYTEST_FILES=$(find "${PHASE_DIR}/test_scripts/integration" -name "*.py" 2>/dev/null | wc -l)
    echo "  pytest scripts: ${PYTEST_FILES}"
  else
    echo "  pytest scripts: 0"
  fi

  # Security scripts
  if [ -d "${PHASE_DIR}/test_scripts/security" ]; then
    SECURITY_FILES=$(find "${PHASE_DIR}/test_scripts/security" -name "*.py" 2>/dev/null | wc -l)
    echo "  Security scripts: ${SECURITY_FILES}"
  else
    echo "  Security scripts: 0"
  fi
  echo ""

  # Check key output files
  if [ -f "${PHASE_DIR}/test_execution_guide.md" ]; then
    echo -e "${GREEN}✓${NC} test_execution_guide.md generated"
  else
    echo -e "${YELLOW}⚠${NC} test_execution_guide.md not found"
  fi

  if [ -f "${PHASE_DIR}/test_scripts/run_all_tests.sh" ]; then
    echo -e "${GREEN}✓${NC} run_all_tests.sh generated"
  else
    echo -e "${YELLOW}⚠${NC} run_all_tests.sh not found"
  fi
  echo ""

  echo -e "${GREEN}Outputs:${NC} ${PHASE_DIR}/"
  echo "   test_scripts/"
  echo "     - postman/ (API test collections)"
  echo "     - jmeter/ (performance test plans)"
  echo "     - integration/ (pytest scripts)"
  echo "     - security/ (OWASP ZAP scripts)"
  echo "     - run_all_tests.sh"
  echo "   test_execution_guide.md"
  echo ""

  echo -e "${GREEN}Next Phase:${NC} /rnvs-workflow:phase15-check-code-quality"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

else
  echo -e "${RED}Invalid stage: ${STAGE}${NC}"
  echo "Usage: $0 <feature> <validate|summarize>"
  exit 1
fi
