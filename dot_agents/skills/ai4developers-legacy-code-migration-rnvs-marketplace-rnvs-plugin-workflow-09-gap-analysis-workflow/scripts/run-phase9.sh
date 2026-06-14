#!/usr/bin/env bash
#
# Phase 9 Orchestration Script
# Handles validation and summary - agent launch done by command
#
# Usage: run-phase9.sh <feature-name> <stage>
#   stage: "validate" | "summarize"
#
# Mode detection: Reads from .workflow-context.json (set by hooks)
#

set -e

FEATURE="$1"
STAGE="$2"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT}"
RESULTS_DIR="results/${FEATURE}"
PHASE_DIR="${RESULTS_DIR}/phase9"
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
# Validate GREENFIELD mode prerequisites (NEW mode uses integer phases)
#
validate_new_mode() {
  local errors=0

  echo -e "${BLUE}Checking NEW mode prerequisites...${NC}"
  echo ""

  # Phase 1 - Code Analysis
  if [ -f "${RESULTS_DIR}/phase1/analysis.json" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 1: analysis.json"
  else
    echo -e "  ${RED}✗${NC} Phase 1: analysis.json missing"
    errors=$((errors + 1))
  fi

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

  # Phase 7 - Microservice Design (NEW mode uses phase7, not phase7.1)
  if [ -f "${RESULTS_DIR}/phase7/microservice-design.json" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 7: microservice-design.json"
  else
    echo -e "  ${RED}✗${NC} Phase 7: microservice-design.json missing"
    errors=$((errors + 1))
  fi

  # Phase 8 - Control Flow Design (optional but recommended)
  if [ -f "${RESULTS_DIR}/phase8/control-flow-design.json" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 8: control-flow-design.json"
  else
    echo -e "  ${YELLOW}⚠${NC} Phase 8: control-flow-design.json (optional)"
  fi

  echo ""
  return $errors
}

#
# Validate CHANGE mode prerequisites (uses decimal phases)
#
validate_change_mode() {
  local errors=0

  echo -e "${BLUE}Checking CHANGE mode prerequisites...${NC}"
  echo ""

  # Phase 1 - Code Analysis (scoped to feature)
  if [ -f "${RESULTS_DIR}/phase1/analysis.json" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 1: analysis.json"
  else
    echo -e "  ${RED}✗${NC} Phase 1: analysis.json missing"
    errors=$((errors + 1))
  fi

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

  # Phase 7.1 - Delta Design (CHANGE mode uses decimal phase)
  if [ -f "${RESULTS_DIR}/phase7.1/microservice-changes-design.json" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 7.1: microservice-changes-design.json (delta)"
  else
    echo -e "  ${RED}✗${NC} Phase 7.1: microservice-changes-design.json missing"
    errors=$((errors + 1))
  fi

  # Phase 8.1 - Control Flow Changes (optional but recommended)
  if [ -f "${RESULTS_DIR}/phase8.1/control-flow-changes-design.json" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 8.1: control-flow-changes-design.json"
  else
    echo -e "  ${YELLOW}⚠${NC} Phase 8.1: control-flow-changes-design.json (optional)"
  fi

  echo ""
  return $errors
}

#
# Merge Phase 6 baseline + Phase 7.1 delta into effective state (CHANGE mode)
#
merge_effective_state() {
  echo -e "${BLUE}Computing effective VNRM state (baseline + delta)...${NC}"

  mkdir -p "${PHASE_DIR}"

  # Create effective-vnrm-state.json by combining baseline and delta
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
        effective_state: {
          description: "Combined view of baseline + applied delta changes",
          note: "Agent should compute effective endpoint/table/topic counts by applying delta to baseline"
        }
      }' > "${PHASE_DIR}/effective-vnrm-state.json"

    echo -e "  ${GREEN}✓${NC} Created effective-vnrm-state.json"
  else
    # Fallback without jq
    cat > "${PHASE_DIR}/effective-vnrm-state.json" << EOF
{
  "workflow_mode": "CHANGE",
  "generated_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "baseline_source": "phase6/analysis.json",
  "delta_source": "phase7.1/microservice-changes-design.json",
  "note": "Install jq for automatic baseline+delta merge computation"
}
EOF
    echo -e "  ${YELLOW}⚠${NC} Created minimal effective-vnrm-state.json (install jq for full merge)"
  fi

  echo ""
}

#
# VALIDATION STAGE
#
if [ "$STAGE" = "validate" ]; then
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}Phase 9: Gap Analysis${NC}"
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
    echo "  - Phase 6 + Phase 7.1 (for CHANGE mode)"
    echo "  - Phase 7 (for NEW mode)"
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

  # For CHANGE mode, compute effective state
  if [ "$WORKFLOW_MODE" = "CHANGE" ]; then
    merge_effective_state
  fi

  echo -e "${GREEN}Validation complete - ready for gap analysis${NC}"
  echo ""

  # Show input files
  echo -e "${BLUE}Input files for gap analysis:${NC}"
  if [ "$WORKFLOW_MODE" = "NEW" ]; then
    echo "   RNVS Source:"
    echo "     - phase1/analysis.json"
    echo "     - phase3/ruletable.json"
    echo "     - phase5/control-flow-mapping.json"
    echo "   VNRM Target:"
    echo "     - phase7/microservice-design.json"
    echo "     - phase8/control-flow-design.json (if available)"
  else
    echo "   RNVS Source:"
    echo "     - phase1/analysis.json"
    echo "     - phase3/ruletable.json"
    echo "     - phase5/control-flow-mapping.json"
    echo "   VNRM Target (baseline + delta):"
    echo "     - phase6/analysis.json (baseline)"
    echo "     - phase7.1/microservice-changes-design.json (delta)"
    echo "     - phase8.1/control-flow-changes-design.json (if available)"
    echo "     - phase9/effective-vnrm-state.json (computed)"
  fi
  echo ""
  echo -e "${BLUE}Launching agent to perform gap analysis...${NC}"
  echo ""

#
# SUMMARY STAGE
#
elif [ "$STAGE" = "summarize" ]; then
  echo ""
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}Phase 9 Complete - Gap Analysis${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

  # Read workflow mode for display
  WORKFLOW_MODE=$(get_workflow_mode)

  # Extract metrics if jq available
  if command -v jq &> /dev/null && [ -f "${PHASE_DIR}/traceability_matrix.json" ]; then
    COVERAGE=$(jq -r '.overall_coverage.coverage_percentage // 0' ${PHASE_DIR}/traceability_matrix.json 2>/dev/null)
    TOTAL=$(jq -r '.overall_coverage.total_rnvs_components // 0' ${PHASE_DIR}/traceability_matrix.json 2>/dev/null)
    FULLY=$(jq -r '.overall_coverage.fully_covered // 0' ${PHASE_DIR}/traceability_matrix.json 2>/dev/null)
    PARTIALLY=$(jq -r '.overall_coverage.partially_covered // 0' ${PHASE_DIR}/traceability_matrix.json 2>/dev/null)
    NOT_COVERED=$(jq -r '.overall_coverage.not_covered // 0' ${PHASE_DIR}/traceability_matrix.json 2>/dev/null)
    GAP_COUNT=$(jq '.gaps | length' ${PHASE_DIR}/traceability_matrix.json 2>/dev/null || echo "0")
    RISK_COUNT=$(jq '.risks | length' ${PHASE_DIR}/traceability_matrix.json 2>/dev/null || echo "0")
    TASK_COUNT=$(jq '.implementation_backlog | length' ${PHASE_DIR}/traceability_matrix.json 2>/dev/null || echo "0")

    # Priority breakdown
    P0_COUNT=$(jq '[.gaps[] | select(.priority == "P0")] | length' ${PHASE_DIR}/traceability_matrix.json 2>/dev/null || echo "0")
    P1_COUNT=$(jq '[.gaps[] | select(.priority == "P1")] | length' ${PHASE_DIR}/traceability_matrix.json 2>/dev/null || echo "0")
    P2_COUNT=$(jq '[.gaps[] | select(.priority == "P2")] | length' ${PHASE_DIR}/traceability_matrix.json 2>/dev/null || echo "0")
    P3_COUNT=$(jq '[.gaps[] | select(.priority == "P3")] | length' ${PHASE_DIR}/traceability_matrix.json 2>/dev/null || echo "0")

    echo -e "${CYAN}Workflow Mode:${NC} ${WORKFLOW_MODE}"
    echo ""
    echo -e "${YELLOW}Coverage Summary:${NC}"
    echo "  Overall Coverage: ${COVERAGE}%"
    echo "  Total RNVS Components: ${TOTAL}"
    echo "  - Fully Covered: ${FULLY}"
    echo "  - Partially Covered: ${PARTIALLY}"
    echo "  - Not Covered: ${NOT_COVERED}"
    echo ""
    echo -e "${YELLOW}Gap Analysis:${NC}"
    echo "  Total Gaps: ${GAP_COUNT}"
    echo "  - P0 (Critical): ${P0_COUNT}"
    echo "  - P1 (High): ${P1_COUNT}"
    echo "  - P2 (Medium): ${P2_COUNT}"
    echo "  - P3 (Low): ${P3_COUNT}"
    echo ""
    echo -e "${YELLOW}Implementation:${NC}"
    echo "  Risks Identified: ${RISK_COUNT}"
    echo "  Backlog Tasks: ${TASK_COUNT}"
  else
    echo -e "${YELLOW}Install jq for detailed metrics${NC}"
  fi

  echo ""
  echo -e "${GREEN}Outputs:${NC} ${PHASE_DIR}/"
  echo "   traceability_matrix.json (machine-readable)"
  echo "   gap_analysis.md (human-readable report)"
  echo "   rnvs_capability_inventory.md (source inventory)"
  echo "   vnrm_capability_inventory.md (target inventory)"
  echo "   implementation_backlog.md (prioritized tasks)"
  if [ -f "${PHASE_DIR}/effective-vnrm-state.json" ]; then
    echo "   effective-vnrm-state.json (CHANGE mode baseline+delta)"
  fi
  echo ""
  echo -e "${GREEN}Next Phase:${NC} /rnvs-workflow:phase10-story-generation"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

else
  echo -e "${RED}Invalid stage: ${STAGE}${NC}"
  echo "Usage: $0 <feature> <validate|summarize>"
  exit 1
fi
