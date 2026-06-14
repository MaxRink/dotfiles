#!/usr/bin/env bash
#
# Phase 11 Orchestration Script
# Handles validation and summary - agent launch done by command
#
# Usage: run-phase11.sh <feature-name> <stage>
#   stage: "validate" | "summarize"
#
# Phase 11 is UNIFIED - works for both NEW and CHANGE modes
# (Phase 10 outputs are already unified, so Phase 11 inherits this)
#

set -e

FEATURE="$1"
STAGE="$2"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT}"
RESULTS_DIR="results/${FEATURE}"
PHASE_DIR="${RESULTS_DIR}/phase11"
CONTEXT_FILE="${RESULTS_DIR}/.workflow-context.json"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

#
# Read workflow mode from .workflow-context.json (for display only)
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
# Validate Phase 10 prerequisites (unified for both modes)
#
validate_prerequisites() {
  local errors=0

  echo -e "${BLUE}Checking Phase 10 prerequisites for Phase 11...${NC}"
  echo ""

  # Phase 10 - User Stories (required for test scenario expansion)
  if [ -f "${RESULTS_DIR}/phase10/user-stories.json" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 10: user-stories.json"
  else
    echo -e "  ${RED}✗${NC} Phase 10: user-stories.json missing"
    errors=$((errors + 1))
  fi

  # Phase 10 - Jira Stories CSV
  if [ -f "${RESULTS_DIR}/phase10/jira_stories.csv" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 10: jira_stories.csv"
  else
    echo -e "  ${RED}✗${NC} Phase 10: jira_stories.csv missing"
    errors=$((errors + 1))
  fi

  # Phase 10 - Summary (validation that Phase 10 completed)
  if [ -f "${RESULTS_DIR}/phase10/PHASE10_SUMMARY.md" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 10: PHASE10_SUMMARY.md"
  else
    echo -e "  ${YELLOW}⚠${NC} Phase 10: PHASE10_SUMMARY.md missing (optional)"
  fi

  echo ""

  # Reference files (optional but helpful)
  echo -e "${BLUE}Checking reference files for test enrichment...${NC}"
  echo ""

  # Phase 3 - Business Rules
  if [ -f "${RESULTS_DIR}/phase3/ruletable.json" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 3: ruletable.json (business rules)"
  else
    echo -e "  ${YELLOW}⚠${NC} Phase 3: ruletable.json (optional - for BR-XXX references)"
  fi

  # Phase 5 - Workflows
  if [ -f "${RESULTS_DIR}/phase5/control-flow-mapping.json" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 5: control-flow-mapping.json (workflows)"
  else
    echo -e "  ${YELLOW}⚠${NC} Phase 5: control-flow-mapping.json (optional - for WF-XXX references)"
  fi

  echo ""
  return $errors
}

#
# VALIDATION STAGE
#
if [ "$STAGE" = "validate" ]; then
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}Phase 11: System Test Scenario Definition${NC}"
  echo -e "${BLUE}Feature: ${FEATURE}${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

  # Read workflow mode (for display only - Phase 11 is unified)
  WORKFLOW_MODE=$(get_workflow_mode)
  echo -e "${CYAN}Workflow Mode: ${WORKFLOW_MODE}${NC}"
  echo -e "${CYAN}Phase 11 Type: UNIFIED (works for both NEW and CHANGE)${NC}"
  echo ""

  # Validate prerequisites
  validate_prerequisites
  VALIDATION_RESULT=$?

  if [ $VALIDATION_RESULT -gt 0 ]; then
    echo -e "${RED}Validation failed - ${VALIDATION_RESULT} prerequisite(s) missing${NC}"
    echo ""
    echo "Please complete Phase 10 first:"
    echo "  /rnvs-workflow:phase10-generate-jira-stories"
    exit 2
  fi

  # Create output directory
  mkdir -p "${PHASE_DIR}"

  echo -e "${GREEN}Validation complete - ready for test scenario generation${NC}"
  echo ""

  # Show input files
  echo -e "${BLUE}Input files for test scenario generation:${NC}"
  echo "   Phase 10 Test Stories:"
  echo "     - phase10/user-stories.json (filter story_type=Test)"
  echo "     - phase10/jira_stories.csv"
  echo ""
  echo "   Reference Data (for enrichment):"
  echo "     - phase3/ruletable.json (business rules)"
  echo "     - phase5/control-flow-mapping.json (workflows)"
  echo ""

  # CHANGE Mode: Extract test inventory from Phase 6
  if [ "$WORKFLOW_MODE" = "CHANGE" ]; then
    echo -e "${CYAN}CHANGE Mode: Extracting existing test inventory from Phase 6...${NC}"

    # Check if Phase 6 has test_infrastructure
    if [ -f "${RESULTS_DIR}/phase6/analysis.json" ]; then
      if command -v jq &> /dev/null; then
        if jq -e '.test_infrastructure' "${RESULTS_DIR}/phase6/analysis.json" > /dev/null 2>&1; then
          # Extract test inventory to Phase 11 directory for agent access
          jq '.test_infrastructure' "${RESULTS_DIR}/phase6/analysis.json" > "${PHASE_DIR}/existing-test-inventory.json" 2>/dev/null
          TEST_COUNT=$(jq '[.test_inventory[]? // empty] | length' "${PHASE_DIR}/existing-test-inventory.json" 2>/dev/null || echo "0")
          echo -e "  ${GREEN}✓${NC} Extracted test inventory: ${TEST_COUNT} existing test classes"
          echo "     - existing-test-inventory.json created for agent reference"
          echo ""
          echo -e "${CYAN}Classification Mode: REUSE/MODIFY/NEW${NC}"
          echo "     - REUSE: Existing test covers unchanged functionality"
          echo "     - MODIFY: Existing test needs updates for changed code"
          echo "     - NEW: No existing test coverage"
        else
          echo -e "  ${YELLOW}⚠${NC} Phase 6: test_infrastructure not found in analysis.json"
          echo "     Treating all scenarios as NEW (no existing test coverage)"
        fi
      else
        echo -e "  ${YELLOW}⚠${NC} jq not available - cannot extract test inventory"
      fi
    else
      echo -e "  ${RED}✗${NC} Phase 6: analysis.json not found"
    fi
    echo ""
  else
    echo -e "${CYAN}NEW Mode: All scenarios will be classified as NEW${NC}"
    echo ""
  fi

  echo -e "${BLUE}Target Outputs:${NC}"
  echo "   - test-scenarios.md (100-120 detailed scenarios)"
  echo "   - test-scenarios.json (structured metadata with classification)"
  echo "   - test-matrix.csv (test tracking with Classification column)"
  echo "   - test-dependencies.puml (execution order)"
  echo "   - PHASE11_SUMMARY.md (metrics and coverage)"
  echo ""
  echo -e "${BLUE}Launching agent to generate test scenarios...${NC}"
  echo ""

#
# SUMMARY STAGE
#
elif [ "$STAGE" = "summarize" ]; then
  echo ""
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}Phase 11 Complete - System Test Scenario Definition${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

  # Read workflow mode for display
  WORKFLOW_MODE=$(get_workflow_mode)

  # Extract metrics if jq available
  if command -v jq &> /dev/null && [ -f "${PHASE_DIR}/test-scenarios.json" ]; then
    TOTAL_SCENARIOS=$(jq -r '.test_scenario_metadata.total_scenarios // 0' ${PHASE_DIR}/test-scenarios.json 2>/dev/null)
    E2E_SCENARIOS=$(jq -r '.test_scenario_metadata.e2e_scenarios // 0' ${PHASE_DIR}/test-scenarios.json 2>/dev/null)
    INT_SCENARIOS=$(jq -r '.test_scenario_metadata.integration_scenarios // 0' ${PHASE_DIR}/test-scenarios.json 2>/dev/null)
    PERF_SCENARIOS=$(jq -r '.test_scenario_metadata.performance_scenarios // 0' ${PHASE_DIR}/test-scenarios.json 2>/dev/null)
    SEC_SCENARIOS=$(jq -r '.test_scenario_metadata.security_scenarios // 0' ${PHASE_DIR}/test-scenarios.json 2>/dev/null)
    MISSING_WF=$(jq -r '.test_scenario_metadata.missing_workflow_scenarios // 0' ${PHASE_DIR}/test-scenarios.json 2>/dev/null)
    DEP_COUNT=$(jq '[.test_dependencies[]? // empty] | length' ${PHASE_DIR}/test-scenarios.json 2>/dev/null || echo "0")

    echo -e "${CYAN}Workflow Mode:${NC} ${WORKFLOW_MODE} (Phase 11 is unified)"
    echo ""
    echo -e "${YELLOW}Test Scenario Summary:${NC}"
    echo "  Total Scenarios: ${TOTAL_SCENARIOS}"
    echo "  - E2E Scenarios: ${E2E_SCENARIOS}"
    echo "  - Integration Scenarios: ${INT_SCENARIOS}"
    echo "  - Performance Scenarios: ${PERF_SCENARIOS}"
    echo "  - Security Scenarios: ${SEC_SCENARIOS}"
    echo "  - Missing Workflow Scenarios: ${MISSING_WF}"
    echo "  Dependencies: ${DEP_COUNT}"
    echo ""

    # CHANGE Mode: Show classification summary
    if [ "$WORKFLOW_MODE" = "CHANGE" ]; then
      if jq -e '.classification_summary' ${PHASE_DIR}/test-scenarios.json > /dev/null 2>&1; then
        REUSE_COUNT=$(jq -r '.classification_summary.reuse_count // 0' ${PHASE_DIR}/test-scenarios.json 2>/dev/null)
        MODIFY_COUNT=$(jq -r '.classification_summary.modify_count // 0' ${PHASE_DIR}/test-scenarios.json 2>/dev/null)
        NEW_COUNT=$(jq -r '.classification_summary.new_count // 0' ${PHASE_DIR}/test-scenarios.json 2>/dev/null)

        echo -e "${YELLOW}Classification Summary (CHANGE Mode):${NC}"
        echo "  - REUSE: ${REUSE_COUNT} (existing tests, no changes)"
        echo "  - MODIFY: ${MODIFY_COUNT} (existing tests, need updates)"
        echo "  - NEW: ${NEW_COUNT} (new test scenarios)"
        echo ""
      fi
    fi
  else
    echo -e "${YELLOW}Install jq for detailed metrics${NC}"
    echo ""
  fi

  # Validate CSV structure
  if [ -f "${PHASE_DIR}/test-matrix.csv" ]; then
    CSV_ROWS=$(tail -n +2 "${PHASE_DIR}/test-matrix.csv" | wc -l)
    echo -e "${YELLOW}CSV Validation:${NC}"
    echo "  Test scenarios in CSV: ${CSV_ROWS}"

    # Check for forbidden columns
    if grep -qi "Sprint" "${PHASE_DIR}/test-matrix.csv" 2>/dev/null; then
      echo -e "  ${RED}✗${NC} Contains Sprint column (should be removed)"
    else
      echo -e "  ${GREEN}✓${NC} No Sprint column (requirement met)"
    fi

    if grep -qi "Depends.On\|Depends_On" "${PHASE_DIR}/test-matrix.csv" 2>/dev/null; then
      echo -e "  ${GREEN}✓${NC} Contains Depends_On column (dependencies tracked)"
    else
      echo -e "  ${RED}✗${NC} Missing Depends_On column"
    fi

    # Check scenario count range
    if [ "$CSV_ROWS" -lt 80 ]; then
      echo -e "  ${YELLOW}⚠${NC} Only ${CSV_ROWS} scenarios (expected 100-150)"
    elif [ "$CSV_ROWS" -gt 200 ]; then
      echo -e "  ${YELLOW}⚠${NC} ${CSV_ROWS} scenarios (may be too granular)"
    else
      echo -e "  ${GREEN}✓${NC} Scenario count in expected range"
    fi
    echo ""
  fi

  echo -e "${GREEN}Outputs:${NC} ${PHASE_DIR}/"
  echo "   test-scenarios.md (comprehensive documentation)"
  echo "   test-scenarios.json (structured metadata)"
  echo "   test-matrix.csv (test tracking matrix)"
  echo "   test-dependencies.puml (dependency graph)"
  echo "   PHASE11_SUMMARY.md (metrics and coverage)"
  echo ""
  echo -e "${GREEN}Workflow Coverage:${NC}"
  echo "   WF-001 to WF-008 (100% coverage target)"
  echo ""
  echo -e "${GREEN}Next Phase:${NC} /rnvs-workflow:phase12-generate-unittests"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

else
  echo -e "${RED}Invalid stage: ${STAGE}${NC}"
  echo "Usage: $0 <feature> <validate|summarize>"
  exit 1
fi
