#!/usr/bin/env bash
#
# Phase 10 Orchestration Script
# Handles validation and summary - agent launch done by command
#
# Usage: run-phase10.sh <feature-name> <stage>
#   stage: "validate" | "summarize"
#
# Mode detection: Reads from .workflow-context.json (set by hooks)
#

set -e

FEATURE="$1"
STAGE="$2"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT}"
RESULTS_DIR="results/${FEATURE}"
PHASE_DIR="${RESULTS_DIR}/phase10"
CONTEXT_FILE="${RESULTS_DIR}/.workflow-context.json"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

#
# Read workflow mode from .workflow-context.json (managed by hooks)
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
# Validate NEW mode prerequisites
#
validate_new_mode() {
  local errors=0

  echo -e "${BLUE}Checking NEW mode prerequisites for Phase 10...${NC}"
  echo ""

  # Phase 3 - Business Rules
  if [ -f "${RESULTS_DIR}/phase3/ruletable.json" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 3: ruletable.json"
  else
    echo -e "  ${RED}✗${NC} Phase 3: ruletable.json missing"
    errors=$((errors + 1))
  fi

  # Phase 5 - Control Flow Mapping
  if [ -f "${RESULTS_DIR}/phase5/control-flow-mapping.json" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 5: control-flow-mapping.json"
  else
    echo -e "  ${RED}✗${NC} Phase 5: control-flow-mapping.json missing"
    errors=$((errors + 1))
  fi

  # Phase 7 - Microservice Design (NEW mode)
  if [ -f "${RESULTS_DIR}/phase7/microservice-design.json" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 7: microservice-design.json"
  else
    echo -e "  ${RED}✗${NC} Phase 7: microservice-design.json missing"
    errors=$((errors + 1))
  fi

  # Phase 9 - Gap Analysis (unified for both modes)
  if [ -f "${RESULTS_DIR}/phase9/gap_analysis.md" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 9: gap_analysis.md"
  else
    echo -e "  ${RED}✗${NC} Phase 9: gap_analysis.md missing"
    errors=$((errors + 1))
  fi

  if [ -f "${RESULTS_DIR}/phase9/traceability_matrix.json" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 9: traceability_matrix.json"
  else
    echo -e "  ${RED}✗${NC} Phase 9: traceability_matrix.json missing"
    errors=$((errors + 1))
  fi

  echo ""
  return $errors
}

#
# Validate CHANGE mode prerequisites
#
validate_change_mode() {
  local errors=0

  echo -e "${BLUE}Checking CHANGE mode prerequisites for Phase 10...${NC}"
  echo ""

  # Phase 3 - Business Rules
  if [ -f "${RESULTS_DIR}/phase3/ruletable.json" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 3: ruletable.json"
  else
    echo -e "  ${RED}✗${NC} Phase 3: ruletable.json missing"
    errors=$((errors + 1))
  fi

  # Phase 5 - Control Flow Mapping
  if [ -f "${RESULTS_DIR}/phase5/control-flow-mapping.json" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 5: control-flow-mapping.json"
  else
    echo -e "  ${RED}✗${NC} Phase 5: control-flow-mapping.json missing"
    errors=$((errors + 1))
  fi

  # Phase 6 - Baseline Analysis (CHANGE mode specific)
  if [ -f "${RESULTS_DIR}/phase6/analysis.json" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 6: analysis.json (baseline)"
  else
    echo -e "  ${RED}✗${NC} Phase 6: analysis.json missing (baseline required)"
    errors=$((errors + 1))
  fi

  # Phase 7.1 - Delta Design (CHANGE mode)
  if [ -f "${RESULTS_DIR}/phase7.1/microservice-changes-design.json" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 7.1: microservice-changes-design.json (delta)"
  else
    echo -e "  ${RED}✗${NC} Phase 7.1: microservice-changes-design.json missing"
    errors=$((errors + 1))
  fi

  # Phase 9 - Gap Analysis (unified)
  if [ -f "${RESULTS_DIR}/phase9/gap_analysis.md" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 9: gap_analysis.md"
  else
    echo -e "  ${RED}✗${NC} Phase 9: gap_analysis.md missing"
    errors=$((errors + 1))
  fi

  if [ -f "${RESULTS_DIR}/phase9/traceability_matrix.json" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 9: traceability_matrix.json"
  else
    echo -e "  ${RED}✗${NC} Phase 9: traceability_matrix.json missing"
    errors=$((errors + 1))
  fi

  echo ""
  return $errors
}

#
# Merge design context for CHANGE mode (Phase 6 baseline + Phase 7.1 delta)
#
merge_effective_design() {
  echo -e "${BLUE}Computing effective design (baseline + delta)...${NC}"

  mkdir -p "${PHASE_DIR}"

  # Create effective-design.json by combining baseline and delta
  if command -v jq &> /dev/null; then
    jq -n \
      --slurpfile baseline "${RESULTS_DIR}/phase6/analysis.json" \
      --slurpfile delta "${RESULTS_DIR}/phase7.1/microservice-changes-design.json" \
      '{
        workflow_mode: "CHANGE",
        generated_at: (now | strftime("%Y-%m-%dT%H:%M:%SZ")),
        baseline: {
          source: "phase6/analysis.json",
          service_name: $baseline[0].service_name,
          endpoints: ($baseline[0].endpoints // []),
          database_tables: ($baseline[0].database.tables // []),
          kafka_topics: ($baseline[0].kafka.topics // [])
        },
        delta: {
          source: "phase7.1/microservice-changes-design.json",
          change_type: $delta[0].change_type,
          api_changes: $delta[0].changes.api_changes,
          database_changes: $delta[0].changes.database_changes,
          event_changes: $delta[0].changes.event_changes
        },
        note: "Use baseline for existing context, delta for new/modified functionality"
      }' > "${PHASE_DIR}/effective-design.json"

    echo -e "  ${GREEN}✓${NC} Created effective-design.json"
  else
    # Fallback without jq
    cat > "${PHASE_DIR}/effective-design.json" << EOF
{
  "workflow_mode": "CHANGE",
  "generated_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "baseline_source": "phase6/analysis.json",
  "delta_source": "phase7.1/microservice-changes-design.json",
  "note": "Install jq for automatic baseline+delta merge computation"
}
EOF
    echo -e "  ${YELLOW}⚠${NC} Created minimal effective-design.json (install jq for full merge)"
  fi

  echo ""
}

#
# VALIDATION STAGE
#
if [ "$STAGE" = "validate" ]; then
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}Phase 10: Jira Story Generation${NC}"
  echo -e "${BLUE}Feature: ${FEATURE}${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

  # Read workflow mode from context file (set by hooks)
  WORKFLOW_MODE=$(get_workflow_mode)

  if [ "$WORKFLOW_MODE" = "UNKNOWN" ]; then
    echo -e "${RED}Cannot determine workflow mode${NC}"
    echo ""
    echo "The workflow mode should be set in .workflow-context.json"
    echo "This is normally set when you run Phase 6 (CHANGE) or Phase 7 (NEW)."
    echo ""
    echo "Please ensure you have completed either:"
    echo "  - Phase 6 + Phase 7.1 + Phase 9 (for CHANGE mode)"
    echo "  - Phase 7 + Phase 8 + Phase 9 (for NEW mode)"
    exit 2
  fi

  echo -e "${CYAN}Workflow Mode: ${WORKFLOW_MODE}${NC}"
  echo ""

  # Validate based on mode
  if [ "$WORKFLOW_MODE" = "NEW" ]; then
    validate_new_mode
    VALIDATION_RESULT=$?
  elif [ "$WORKFLOW_MODE" = "CHANGE" ]; then
    validate_change_mode
    VALIDATION_RESULT=$?
  else
    echo -e "${RED}Unknown workflow mode: ${WORKFLOW_MODE}${NC}"
    exit 2
  fi

  if [ $VALIDATION_RESULT -gt 0 ]; then
    echo -e "${RED}Validation failed - ${VALIDATION_RESULT} prerequisite(s) missing${NC}"
    exit 2
  fi

  # Create output directory
  mkdir -p "${PHASE_DIR}"

  # For CHANGE mode, compute effective design context
  if [ "$WORKFLOW_MODE" = "CHANGE" ]; then
    merge_effective_design
  fi

  echo -e "${GREEN}Validation complete - ready for story generation${NC}"
  echo ""

  # Show input files
  echo -e "${BLUE}Input files for story generation:${NC}"
  if [ "$WORKFLOW_MODE" = "NEW" ]; then
    echo "   Reference Data:"
    echo "     - phase3/ruletable.json (business rules)"
    echo "     - phase5/control-flow-mapping.json (workflows)"
    echo "   Design Context:"
    echo "     - phase7/microservice-design.json"
    echo "   Gap Source:"
    echo "     - phase9/gap_analysis.md"
    echo "     - phase9/traceability_matrix.json"
  else
    echo "   Reference Data:"
    echo "     - phase3/ruletable.json (business rules)"
    echo "     - phase5/control-flow-mapping.json (workflows)"
    echo "   Design Context (baseline + delta):"
    echo "     - phase6/analysis.json (baseline)"
    echo "     - phase7.1/microservice-changes-design.json (delta)"
    echo "     - phase10/effective-design.json (computed)"
    echo "   Gap Source:"
    echo "     - phase9/gap_analysis.md"
    echo "     - phase9/traceability_matrix.json"
  fi
  echo ""
  echo -e "${BLUE}Launching agent to generate Jira stories...${NC}"
  echo ""

#
# SUMMARY STAGE
#
elif [ "$STAGE" = "summarize" ]; then
  echo ""
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}Phase 10 Complete - Jira Story Generation${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

  # Read workflow mode for display
  WORKFLOW_MODE=$(get_workflow_mode)

  # Extract metrics if jq available
  if command -v jq &> /dev/null && [ -f "${PHASE_DIR}/user-stories.json" ]; then
    TOTAL_STORIES=$(jq -r '.story_generation_metadata.total_stories // 0' ${PHASE_DIR}/user-stories.json 2>/dev/null)
    IMPL_STORIES=$(jq -r '.story_generation_metadata.implementation_stories // 0' ${PHASE_DIR}/user-stories.json 2>/dev/null)
    TEST_STORIES=$(jq -r '.story_generation_metadata.test_stories // 0' ${PHASE_DIR}/user-stories.json 2>/dev/null)
    EPIC_COUNT=$(jq '.epics | length' ${PHASE_DIR}/user-stories.json 2>/dev/null || echo "0")
    DEP_COUNT=$(jq '[.stories[].dependencies.blocked_by[]? // empty] | length' ${PHASE_DIR}/user-stories.json 2>/dev/null || echo "0")

    echo -e "${CYAN}Workflow Mode:${NC} ${WORKFLOW_MODE}"
    echo ""
    echo -e "${YELLOW}Story Generation Summary:${NC}"
    echo "  Total Stories: ${TOTAL_STORIES}"
    echo "  - Implementation Stories: ${IMPL_STORIES}"
    echo "  - Test Stories: ${TEST_STORIES}"
    echo "  Epics: ${EPIC_COUNT}"
    echo "  Dependencies: ${DEP_COUNT}"
    echo ""
  else
    echo -e "${YELLOW}Install jq for detailed metrics${NC}"
    echo ""
  fi

  # Validate CSV structure
  if [ -f "${PHASE_DIR}/jira_stories.csv" ]; then
    CSV_ROWS=$(tail -n +2 "${PHASE_DIR}/jira_stories.csv" | wc -l)
    echo -e "${YELLOW}CSV Validation:${NC}"
    echo "  Rows in CSV: ${CSV_ROWS}"

    # Check for forbidden columns
    if grep -q "Story Points" "${PHASE_DIR}/jira_stories.csv" 2>/dev/null; then
      echo -e "  ${RED}✗${NC} Contains Story Points column (should be removed)"
    else
      echo -e "  ${GREEN}✓${NC} No Story Points column (user requirement met)"
    fi

    if grep -q "Sprint" "${PHASE_DIR}/jira_stories.csv" 2>/dev/null; then
      echo -e "  ${RED}✗${NC} Contains Sprint column (should be removed)"
    else
      echo -e "  ${GREEN}✓${NC} No Sprint column (user requirement met)"
    fi

    if grep -q "Depends On" "${PHASE_DIR}/jira_stories.csv" 2>/dev/null; then
      echo -e "  ${GREEN}✓${NC} Contains Depends On column (dependencies included)"
    else
      echo -e "  ${RED}✗${NC} Missing Depends On column"
    fi
    echo ""
  fi

  echo -e "${GREEN}Outputs:${NC} ${PHASE_DIR}/"
  echo "   jira_stories.csv (Jira import ready)"
  echo "   user-stories.json (structured metadata)"
  echo "   story-dependencies.puml (dependency graph)"
  echo "   PHASE10_SUMMARY.md (comprehensive report)"
  echo "   validation-report.txt (validation results)"
  if [ -f "${PHASE_DIR}/effective-design.json" ]; then
    echo "   effective-design.json (CHANGE mode baseline+delta)"
  fi
  echo ""
  echo -e "${GREEN}Jira Import Instructions:${NC}"
  echo "   1. Open Jira project"
  echo "   2. Navigate to Issues → Import Issues from CSV"
  echo "   3. Upload jira_stories.csv"
  echo "   4. Map columns and execute import"
  echo ""
  echo -e "${GREEN}Next Phase:${NC} /rnvs-workflow:phase11-define-system-tests"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

else
  echo -e "${RED}Invalid stage: ${STAGE}${NC}"
  echo "Usage: $0 <feature> <validate|summarize>"
  exit 1
fi
