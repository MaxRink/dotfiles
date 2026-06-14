#!/usr/bin/env bash
#
# Phase 12 Orchestration Script
# Handles validation and summary - agent launch done by command
#
# Usage: run-phase12.sh <feature-name> <stage>
#   stage: "validate" | "summarize"
#
# Phase 12 is UNIFIED - works for both NEW and CHANGE modes
#

set -e

FEATURE="$1"
STAGE="$2"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT}"
RESULTS_DIR="results/${FEATURE}"
PHASE_DIR="${RESULTS_DIR}/phase12"
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
# Validate Phase 11 prerequisites (unified for both modes)
#
validate_prerequisites() {
  local errors=0

  echo -e "${BLUE}Checking Phase 11 prerequisites for Phase 12...${NC}"
  echo ""

  # Phase 11 - Test Scenarios (required for unit test generation)
  if [ -f "${RESULTS_DIR}/phase11/test-scenarios.json" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 11: test-scenarios.json"
  else
    echo -e "  ${RED}✗${NC} Phase 11: test-scenarios.json missing"
    errors=$((errors + 1))
  fi

  # Phase 11 - Test Scenarios MD
  if [ -f "${RESULTS_DIR}/phase11/test-scenarios.md" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 11: test-scenarios.md"
  else
    echo -e "  ${RED}✗${NC} Phase 11: test-scenarios.md missing"
    errors=$((errors + 1))
  fi

  # Phase 11 - Summary (validation that Phase 11 completed)
  if [ -f "${RESULTS_DIR}/phase11/PHASE11_SUMMARY.md" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 11: PHASE11_SUMMARY.md"
  else
    echo -e "  ${YELLOW}⚠${NC} Phase 11: PHASE11_SUMMARY.md missing (optional)"
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
    # NEW mode: Need Phase 7 microservice design
    if [ -f "${RESULTS_DIR}/phase7/microservice-design.json" ]; then
      echo -e "  ${GREEN}✓${NC} Phase 7: microservice-design.json"
    else
      echo -e "  ${RED}✗${NC} Phase 7: microservice-design.json missing"
      errors=$((errors + 1))
    fi
  elif [ "$mode" = "CHANGE" ]; then
    # CHANGE mode: Need Phase 6 baseline + Phase 7.1 delta
    if [ -f "${RESULTS_DIR}/phase6/analysis.json" ]; then
      echo -e "  ${GREEN}✓${NC} Phase 6: analysis.json (baseline)"

      # CRITICAL: Validate repository_path for direct test application
      if command -v jq &> /dev/null; then
        REPO_PATH=$(jq -r '.repository_path // empty' "${RESULTS_DIR}/phase6/analysis.json" 2>/dev/null)
        if [ -n "$REPO_PATH" ] && [ -d "$REPO_PATH" ]; then
          echo -e "  ${GREEN}✓${NC} repository_path: ${REPO_PATH}"
          if [ -d "${REPO_PATH}/src/test/java" ]; then
            echo -e "  ${GREEN}✓${NC} Test directory exists: src/test/java/"
          else
            echo -e "  ${YELLOW}⚠${NC} Test directory missing (will be created): src/test/java/"
          fi
        else
          echo -e "  ${RED}✗${NC} repository_path not found or inaccessible"
          echo -e "      Expected in: phase6/analysis.json"
          errors=$((errors + 1))
        fi
      fi
    else
      echo -e "  ${RED}✗${NC} Phase 6: analysis.json missing"
      errors=$((errors + 1))
    fi

    if [ -f "${RESULTS_DIR}/phase7.1/microservice-changes-design.json" ]; then
      echo -e "  ${GREEN}✓${NC} Phase 7.1: microservice-changes-design.json (delta)"
    else
      echo -e "  ${RED}✗${NC} Phase 7.1: microservice-changes-design.json missing"
      errors=$((errors + 1))
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
  echo -e "${BLUE}Phase 12: Generate Unit Tests${NC}"
  echo -e "${BLUE}Feature: ${FEATURE}${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

  # Read workflow mode
  WORKFLOW_MODE=$(get_workflow_mode)
  echo -e "${CYAN}Workflow Mode: ${WORKFLOW_MODE}${NC}"
  echo -e "${CYAN}Phase 12 Type: UNIFIED (works for both NEW and CHANGE)${NC}"
  echo ""

  # Validate common prerequisites
  validate_prerequisites
  COMMON_ERRORS=$?

  # Validate mode-specific prerequisites
  validate_mode_prerequisites "$WORKFLOW_MODE"
  MODE_ERRORS=$?

  TOTAL_ERRORS=$((COMMON_ERRORS + MODE_ERRORS))

  if [ $TOTAL_ERRORS -gt 0 ]; then
    echo -e "${RED}Validation failed - ${TOTAL_ERRORS} prerequisite(s) missing${NC}"
    echo ""
    echo "Please complete Phase 11 first:"
    echo "  /rnvs-workflow:phase11-define-system-tests"
    exit 2
  fi

  # Create output directory
  mkdir -p "${PHASE_DIR}/unit_tests/java"

  echo -e "${GREEN}Validation complete - ready for unit test generation${NC}"
  echo ""

  # Show input files
  echo -e "${BLUE}Input files for unit test generation:${NC}"
  echo "   Phase 11 Test Scenarios:"
  echo "     - phase11/test-scenarios.json"
  echo "     - phase11/test-scenarios.md"
  echo ""

  if [ "$WORKFLOW_MODE" = "NEW" ]; then
    echo "   Design Context (NEW mode):"
    echo "     - phase7/microservice-design.json"
    echo ""
    echo -e "${BLUE}Target Outputs:${NC}"
    echo "   - results/phase12/unit_tests/java/ - JUnit test files"
    echo "   - results/phase12/test_summary.md - Test documentation"
  elif [ "$WORKFLOW_MODE" = "CHANGE" ]; then
    echo "   Design Context (CHANGE mode):"
    echo "     - phase6/analysis.json (baseline + test_infrastructure)"
    echo "     - phase7.1/microservice-changes-design.json (delta)"

    # Get repository_path for display
    if command -v jq &> /dev/null && [ -f "${RESULTS_DIR}/phase6/analysis.json" ]; then
      REPO_PATH=$(jq -r '.repository_path // empty' "${RESULTS_DIR}/phase6/analysis.json" 2>/dev/null)
      if [ -n "$REPO_PATH" ]; then
        echo ""
        echo -e "${CYAN}CHANGE Mode: Direct Repository Application${NC}"
        echo -e "   Tests will be applied to: ${YELLOW}${REPO_PATH}/src/test/java/${NC}"
        echo "     - MODIFY: Use Edit tool on existing test files"
        echo "     - NEW: Use Write tool to create new test files"
        echo ""
        echo -e "${CYAN}Classification Mode: REUSE/MODIFY/NEW${NC}"
        echo "     - REUSE: Existing unit test covers unchanged component (skip)"
        echo "     - MODIFY: Existing unit test needs updates (Edit tool)"
        echo "     - NEW: No existing unit test coverage (Write tool)"
      fi
    fi

    echo ""
    echo -e "${BLUE}Target Outputs:${NC}"
    echo "   Applied to VNRM repo: Tests via Edit/Write tools"
    echo "   Metadata: results/phase12/applied-test-edits-log.json"
    echo "   Metadata: results/phase12/test_classification.json"
    echo "   Metadata: results/phase12/test_summary.md"
  fi
  echo ""
  echo -e "${BLUE}Launching agent to generate unit tests...${NC}"
  echo ""

#
# SUMMARY STAGE
#
elif [ "$STAGE" = "summarize" ]; then
  echo ""
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}Phase 12 Complete - Unit Test Generation${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

  # Read workflow mode for display
  WORKFLOW_MODE=$(get_workflow_mode)

  echo -e "${CYAN}Workflow Mode:${NC} ${WORKFLOW_MODE} (Phase 12 is unified)"
  echo ""

  if [ "$WORKFLOW_MODE" = "CHANGE" ]; then
    # CHANGE mode: Tests applied directly to VNRM repo
    echo -e "${YELLOW}Unit Test Summary (CHANGE Mode):${NC}"

    # Check applied-test-edits-log.json
    if [ -f "${PHASE_DIR}/applied-test-edits-log.json" ]; then
      echo -e "${GREEN}✓${NC} applied-test-edits-log.json generated"

      # Extract statistics if jq available
      if command -v jq &> /dev/null; then
        TESTS_REUSED=$(jq -r '.tests_reused | length // 0' "${PHASE_DIR}/applied-test-edits-log.json" 2>/dev/null || echo "0")
        TESTS_MODIFIED=$(jq -r '.tests_modified | length // 0' "${PHASE_DIR}/applied-test-edits-log.json" 2>/dev/null || echo "0")
        TESTS_CREATED=$(jq -r '.tests_created | length // 0' "${PHASE_DIR}/applied-test-edits-log.json" 2>/dev/null || echo "0")
        REPO_PATH=$(jq -r '.repository_path // "unknown"' "${PHASE_DIR}/applied-test-edits-log.json" 2>/dev/null)

        echo ""
        echo "  Classification Results:"
        echo "    REUSE: ${TESTS_REUSED} (reference existing)"
        echo "    MODIFY: ${TESTS_MODIFIED} (edited existing tests)"
        echo "    NEW: ${TESTS_CREATED} (created new tests)"
        echo ""
        echo "  Applied to: ${REPO_PATH}/src/test/java/"
      fi
    else
      echo -e "${YELLOW}⚠${NC} applied-test-edits-log.json not found"
    fi

    # Check test_classification.json
    if [ -f "${PHASE_DIR}/test_classification.json" ]; then
      echo -e "${GREEN}✓${NC} test_classification.json generated"
    fi
    echo ""

  else
    # NEW mode: Tests in results/
    if [ -d "${PHASE_DIR}/unit_tests/java" ]; then
      TEST_FILES=$(find "${PHASE_DIR}/unit_tests/java" -name "*Test.java" 2>/dev/null | wc -l)
      echo -e "${YELLOW}Unit Test Summary (NEW Mode):${NC}"
      echo "  Test Classes Generated: ${TEST_FILES}"

      # Count test methods (rough estimate)
      if [ "$TEST_FILES" -gt 0 ]; then
        TEST_METHODS=$(grep -r "@Test" "${PHASE_DIR}/unit_tests/java" 2>/dev/null | wc -l || echo "0")
        echo "  Test Methods (approx): ${TEST_METHODS}"
      fi
      echo ""
    else
      echo -e "${YELLOW}⚠ No unit_tests/java directory found${NC}"
      echo ""
    fi
  fi

  # Check test_summary.md (both modes)
  if [ -f "${PHASE_DIR}/test_summary.md" ]; then
    echo -e "${GREEN}✓${NC} test_summary.md generated"
  else
    echo -e "${YELLOW}⚠${NC} test_summary.md not found"
  fi
  echo ""

  if [ "$WORKFLOW_MODE" = "CHANGE" ]; then
    echo -e "${GREEN}Outputs:${NC}"
    echo "   VNRM repo: Tests applied via Edit/Write tools"
    echo "   ${PHASE_DIR}/ (metadata only):"
    echo "     - applied-test-edits-log.json"
    echo "     - test_classification.json"
    echo "     - test_summary.md"
  else
    echo -e "${GREEN}Outputs:${NC} ${PHASE_DIR}/"
    echo "   unit_tests/java/ (JUnit test files)"
    echo "   test_summary.md (test documentation)"
  fi
  echo ""

  if [ "$WORKFLOW_MODE" = "NEW" ]; then
    echo -e "${GREEN}Next Phase:${NC} /rnvs-workflow:phase13-generate-source-code"
  else
    echo -e "${GREEN}Next Phase:${NC} /rnvs-workflow:phase13.1-generate-source-code"
  fi
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

else
  echo -e "${RED}Invalid stage: ${STAGE}${NC}"
  echo "Usage: $0 <feature> <validate|summarize>"
  exit 1
fi
