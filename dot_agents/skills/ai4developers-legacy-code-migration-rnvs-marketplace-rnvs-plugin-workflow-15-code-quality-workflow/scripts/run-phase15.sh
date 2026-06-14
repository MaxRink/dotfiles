#!/usr/bin/env bash
#
# Phase 15 Orchestration Script
# Handles validation and summary - agent launch done by command
#
# Usage: run-phase15.sh <feature-name> <stage>
#   stage: "validate" | "summarize"
#
# Phase 15 is UNIFIED - works for both NEW and CHANGE modes
# This is the FINAL phase of the workflow
#

set -e

FEATURE="$1"
STAGE="$2"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT}"
RESULTS_DIR="results/${FEATURE}"
PHASE_DIR="${RESULTS_DIR}/phase15"
CONTEXT_FILE="${RESULTS_DIR}/.workflow-context.json"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
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
# Validate Phase 14 prerequisites (test scripts)
#
validate_common_prerequisites() {
  local errors=0

  echo -e "${BLUE}Checking Phase 14 prerequisites...${NC}"
  echo ""

  # Phase 14 - Test Scripts (required for quality checks)
  if [ -d "${RESULTS_DIR}/phase14/test_scripts" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 14: test_scripts/ directory exists"
  else
    echo -e "  ${RED}✗${NC} Phase 14: test_scripts/ directory missing"
    errors=$((errors + 1))
  fi

  if [ -f "${RESULTS_DIR}/phase14/test_execution_guide.md" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 14: test_execution_guide.md"
  else
    echo -e "  ${YELLOW}⚠${NC} Phase 14: test_execution_guide.md missing (optional)"
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
        echo -e "  ${CYAN}   Java files to analyze: ${JAVA_FILES}${NC}"
      fi
    else
      echo -e "  ${RED}✗${NC} Phase 13: source_code/ directory missing"
      errors=$((errors + 1))
    fi

    # Phase 12 unit tests
    if [ -d "${RESULTS_DIR}/phase12/unit_tests" ]; then
      echo -e "  ${GREEN}✓${NC} Phase 12: unit_tests/ directory exists"
    else
      echo -e "  ${YELLOW}⚠${NC} Phase 12: unit_tests/ directory missing (optional)"
    fi

  elif [ "$mode" = "CHANGE" ]; then
    # CHANGE mode: Need Phase 13.1 applied changes
    if [ -f "${RESULTS_DIR}/phase13.1/applied-edits-log.json" ]; then
      echo -e "  ${GREEN}✓${NC} Phase 13.1: applied-edits-log.json"

      # Extract statistics if jq available
      if command -v jq &> /dev/null; then
        FILES_CREATED=$(jq -r '.files_created | length // 0' "${RESULTS_DIR}/phase13.1/applied-edits-log.json" 2>/dev/null || echo "0")
        FILES_MODIFIED=$(jq -r '.files_modified | length // 0' "${RESULTS_DIR}/phase13.1/applied-edits-log.json" 2>/dev/null || echo "0")
        TOTAL_FILES=$((FILES_CREATED + FILES_MODIFIED))
        echo -e "  ${CYAN}   Files to analyze: ${TOTAL_FILES} (${FILES_CREATED} new, ${FILES_MODIFIED} modified)${NC}"
      fi
    else
      echo -e "  ${RED}✗${NC} Phase 13.1: applied-edits-log.json missing"
      errors=$((errors + 1))
    fi

    # Phase 12 applied tests
    if [ -f "${RESULTS_DIR}/phase12/applied-test-edits-log.json" ]; then
      echo -e "  ${GREEN}✓${NC} Phase 12: applied-test-edits-log.json"
    else
      echo -e "  ${YELLOW}⚠${NC} Phase 12: applied-test-edits-log.json missing (optional)"
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
  echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${MAGENTA}Phase 15: Code Quality Check and Go-Live Approval${NC}"
  echo -e "${MAGENTA}Feature: ${FEATURE}${NC}"
  echo -e "${MAGENTA}*** FINAL PHASE OF WORKFLOW ***${NC}"
  echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

  # Read workflow mode
  WORKFLOW_MODE=$(get_workflow_mode)
  echo -e "${CYAN}Workflow Mode: ${WORKFLOW_MODE}${NC}"
  echo -e "${CYAN}Phase 15 Type: UNIFIED (works for both NEW and CHANGE)${NC}"
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
    echo "Please complete Phase 14 first:"
    echo "  /rnvs-workflow:phase14-generate-system-test-scripts"
    exit 2
  fi

  # Create output directory
  mkdir -p "${PHASE_DIR}"

  echo -e "${GREEN}Validation complete - ready for code quality analysis${NC}"
  echo ""

  # Show input files
  echo -e "${BLUE}Input files for quality analysis:${NC}"
  echo "   Phase 14 Test Scripts:"
  echo "     - phase14/test_scripts/"
  echo ""

  if [ "$WORKFLOW_MODE" = "NEW" ]; then
    echo "   Source Code Context (NEW mode):"
    echo "     - phase13/source_code/"
    echo "     - phase12/unit_tests/"
    echo ""
    echo -e "${CYAN}Scope: Analyze ALL generated code${NC}"
  elif [ "$WORKFLOW_MODE" = "CHANGE" ]; then
    echo "   Source Code Context (CHANGE mode):"
    echo "     - phase13.1/applied-edits-log.json"
    echo "     - phase12/applied-test-edits-log.json"
    echo "     - phase6/analysis.json (baseline)"
    echo ""
    echo -e "${CYAN}Scope: Analyze CHANGED code only${NC}"
  fi
  echo ""

  echo -e "${BLUE}Target Outputs:${NC}"
  echo "   results/${FEATURE}/phase15/"
  echo "     - security_findings.txt"
  echo "     - quality_findings.txt"
  echo "     - test_results.txt"
  echo "     - performance_baseline.txt"
  echo "     - documentation_check.txt"
  echo "     - quality_report.md (comprehensive report)"
  echo ""
  echo -e "${BLUE}Launching agent to perform quality analysis...${NC}"
  echo ""

#
# SUMMARY STAGE
#
elif [ "$STAGE" = "summarize" ]; then
  echo ""
  echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${MAGENTA}Phase 15 Complete - Code Quality Check${NC}"
  echo -e "${MAGENTA}*** WORKFLOW COMPLETE ***${NC}"
  echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

  # Read workflow mode for display
  WORKFLOW_MODE=$(get_workflow_mode)

  echo -e "${CYAN}Workflow Mode:${NC} ${WORKFLOW_MODE} (Phase 15 is unified)"
  echo ""

  # Check quality report
  if [ -f "${PHASE_DIR}/quality_report.md" ]; then
    echo -e "${GREEN}✓${NC} quality_report.md generated"

    # Try to extract key metrics from the report
    if command -v grep &> /dev/null; then
      QUALITY_SCORE=$(grep -o 'Quality Score: [0-9]*' "${PHASE_DIR}/quality_report.md" 2>/dev/null | head -1 || echo "")
      GO_LIVE=$(grep -o 'Recommendation:.*$' "${PHASE_DIR}/quality_report.md" 2>/dev/null | head -1 || echo "")

      if [ -n "$QUALITY_SCORE" ]; then
        echo -e "  ${CYAN}${QUALITY_SCORE}/100${NC}"
      fi
      if [ -n "$GO_LIVE" ]; then
        echo -e "  ${CYAN}${GO_LIVE}${NC}"
      fi
    fi
  else
    echo -e "${YELLOW}⚠${NC} quality_report.md not found"
  fi
  echo ""

  # Check other output files
  echo -e "${YELLOW}Quality Analysis Outputs:${NC}"

  if [ -f "${PHASE_DIR}/security_findings.txt" ]; then
    echo -e "  ${GREEN}✓${NC} security_findings.txt"
  else
    echo -e "  ${YELLOW}○${NC} security_findings.txt (not generated)"
  fi

  if [ -f "${PHASE_DIR}/quality_findings.txt" ]; then
    echo -e "  ${GREEN}✓${NC} quality_findings.txt"
  else
    echo -e "  ${YELLOW}○${NC} quality_findings.txt (not generated)"
  fi

  if [ -f "${PHASE_DIR}/test_results.txt" ]; then
    echo -e "  ${GREEN}✓${NC} test_results.txt"
  else
    echo -e "  ${YELLOW}○${NC} test_results.txt (not generated)"
  fi

  if [ -f "${PHASE_DIR}/performance_baseline.txt" ]; then
    echo -e "  ${GREEN}✓${NC} performance_baseline.txt"
  else
    echo -e "  ${YELLOW}○${NC} performance_baseline.txt (not generated)"
  fi

  if [ -f "${PHASE_DIR}/documentation_check.txt" ]; then
    echo -e "  ${GREEN}✓${NC} documentation_check.txt"
  else
    echo -e "  ${YELLOW}○${NC} documentation_check.txt (not generated)"
  fi
  echo ""

  echo -e "${GREEN}Outputs:${NC} ${PHASE_DIR}/"
  echo "   security_findings.txt"
  echo "   quality_findings.txt"
  echo "   test_results.txt"
  echo "   performance_baseline.txt"
  echo "   documentation_check.txt"
  echo "   quality_report.md"
  echo ""

  # Calculate total phases completed
  if command -v jq &> /dev/null && [ -f "${CONTEXT_FILE}" ]; then
    COMPLETED=$(jq -r '.completed_phases | length // 0' "${CONTEXT_FILE}" 2>/dev/null || echo "0")
    START_TIME=$(jq -r '.start_timestamp // "unknown"' "${CONTEXT_FILE}" 2>/dev/null)

    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${MAGENTA}WORKFLOW SUMMARY${NC}"
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "  Feature: ${FEATURE}"
    echo "  Mode: ${WORKFLOW_MODE}"
    echo "  Phases Completed: ${COMPLETED}"
    echo "  Started: ${START_TIME}"
    echo "  Status: COMPLETE"
    echo ""
  fi

  echo -e "${GREEN}🎉 WORKFLOW COMPLETE 🎉${NC}"
  echo ""
  echo "The RNVS→VNRM migration workflow for feature '${FEATURE}' has completed."
  echo "Review the quality_report.md for go-live decision and next steps."
  echo ""
  echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

else
  echo -e "${RED}Invalid stage: ${STAGE}${NC}"
  echo "Usage: $0 <feature> <validate|summarize>"
  exit 1
fi
