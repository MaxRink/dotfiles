#!/usr/bin/env bash
#
# Phase 7 Orchestration Script
# Handles validation and summary - agent launch done by command
#
# Usage: run-phase7.sh <feature-name> <stage>
#   stage: "validate" | "summarize"
#
# Phase 7 is for NEW mode only (greenfield microservice design)
#

set -e

FEATURE="$1"
STAGE="$2"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT}"
RESULTS_DIR="results/${FEATURE}"
PHASE_DIR="${RESULTS_DIR}/phase7"
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
# Validate Phase 5 prerequisites
#
validate_prerequisites() {
  local errors=0

  echo -e "${BLUE}Checking Phase 5 prerequisites...${NC}"
  echo ""

  # Phase 5 - Control Flow Mapping (required)
  if [ -f "${RESULTS_DIR}/phase5/control-flow-mapping.json" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 5: control-flow-mapping.json"

    # Extract microservice count if jq available
    if command -v jq &> /dev/null; then
      MS_COUNT=$(jq -r '.component_mappings | length // 0' "${RESULTS_DIR}/phase5/control-flow-mapping.json" 2>/dev/null || echo "0")
      echo -e "  ${CYAN}   Microservices to design: ${MS_COUNT}${NC}"
    fi
  else
    echo -e "  ${RED}✗${NC} Phase 5: control-flow-mapping.json missing"
    errors=$((errors + 1))
  fi

  # Phase 4 - Business Documentation (recommended)
  if [ -f "${RESULTS_DIR}/phase4/business-documentation.json" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 4: business-documentation.json"
  else
    echo -e "  ${YELLOW}⚠${NC} Phase 4: business-documentation.json missing (recommended)"
  fi

  # Phase 3 - Business Rules (recommended)
  if [ -f "${RESULTS_DIR}/phase3/ruletable.json" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 3: ruletable.json"
  else
    echo -e "  ${YELLOW}⚠${NC} Phase 3: ruletable.json missing (recommended)"
  fi

  # Phase 1 - Analysis (optional)
  if [ -f "${RESULTS_DIR}/phase1/analysis.json" ]; then
    echo -e "  ${GREEN}✓${NC} Phase 1: analysis.json"
  else
    echo -e "  ${YELLOW}○${NC} Phase 1: analysis.json (optional)"
  fi

  echo ""
  return $errors
}

#
# VALIDATION STAGE
#
if [ "$STAGE" = "validate" ]; then
  echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${MAGENTA}Phase 7: Microservice Design (NEW Mode)${NC}"
  echo -e "${MAGENTA}Feature: ${FEATURE}${NC}"
  echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

  # Read workflow mode
  WORKFLOW_MODE=$(get_workflow_mode)
  echo -e "${CYAN}Workflow Mode: ${WORKFLOW_MODE}${NC}"

  # Warn if CHANGE mode detected
  if [ "$WORKFLOW_MODE" = "CHANGE" ]; then
    echo -e "${YELLOW}⚠ Warning: CHANGE mode detected. Consider using Phase 7.1 instead.${NC}"
    echo -e "${YELLOW}  Phase 7 is for NEW (greenfield) microservice design.${NC}"
    echo ""
  fi
  echo ""

  # Validate prerequisites
  validate_prerequisites
  PREREQ_ERRORS=$?

  if [ $PREREQ_ERRORS -gt 0 ]; then
    echo -e "${RED}Validation failed - ${PREREQ_ERRORS} prerequisite(s) missing${NC}"
    echo ""
    echo "Please complete Phase 5 first:"
    echo "  /rnvs-workflow:phase5-control-flow-mapping"
    exit 2
  fi

  # Create output directory
  mkdir -p "${PHASE_DIR}"

  echo -e "${GREEN}Validation complete - ready for microservice design${NC}"
  echo ""

  # Show input files
  echo -e "${BLUE}Input files for microservice design:${NC}"
  echo "   Phase 5: control-flow-mapping.json (primary)"
  echo "   Phase 4: business-documentation.json (context)"
  echo "   Phase 3: ruletable.json (business rules)"
  echo "   Phase 1: analysis.json (legacy complexity)"
  echo ""

  echo -e "${BLUE}Target Outputs:${NC}"
  echo "   results/${FEATURE}/phase7/"
  echo "     - microservice-design.json"
  echo "     - microservice-design-quality-report.json"
  echo "     - PHASE7_SUMMARY.md"
  echo "     - microservice-dependencies.puml"
  echo "     - event-flow-*.puml"
  echo "     - state-machine-*.puml"
  echo "     - database-erd.puml"
  echo ""
  echo -e "${BLUE}Launching agent to perform microservice design...${NC}"
  echo ""

#
# SUMMARY STAGE
#
elif [ "$STAGE" = "summarize" ]; then
  echo ""
  echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${MAGENTA}Phase 7 Complete - Microservice Design${NC}"
  echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

  # Check main outputs
  if [ -f "${PHASE_DIR}/microservice-design.json" ]; then
    echo -e "${GREEN}✓${NC} microservice-design.json generated"

    # Extract metrics if jq available
    if command -v jq &> /dev/null; then
      MS_COUNT=$(jq -r '.microservices | length // 0' "${PHASE_DIR}/microservice-design.json" 2>/dev/null || echo "0")
      FEATURE_TYPE=$(jq -r '.feature_type // "UNKNOWN"' "${PHASE_DIR}/microservice-design.json" 2>/dev/null || echo "UNKNOWN")
      echo -e "  ${CYAN}Microservices designed: ${MS_COUNT}${NC}"
      echo -e "  ${CYAN}Feature type: ${FEATURE_TYPE}${NC}"
    fi
  else
    echo -e "${YELLOW}⚠${NC} microservice-design.json not found"
  fi
  echo ""

  # Check quality report
  if [ -f "${PHASE_DIR}/microservice-design-quality-report.json" ]; then
    echo -e "${GREEN}✓${NC} microservice-design-quality-report.json"

    if command -v jq &> /dev/null; then
      QUALITY_SCORE=$(jq -r '.overall_score // 0' "${PHASE_DIR}/microservice-design-quality-report.json" 2>/dev/null || echo "0")
      QUALITY_STATUS=$(jq -r '.overall_status // "UNKNOWN"' "${PHASE_DIR}/microservice-design-quality-report.json" 2>/dev/null || echo "UNKNOWN")
      echo -e "  ${CYAN}Quality Score: ${QUALITY_SCORE}/100${NC}"
      echo -e "  ${CYAN}Status: ${QUALITY_STATUS}${NC}"
    fi
  else
    echo -e "${YELLOW}⚠${NC} microservice-design-quality-report.json not found"
  fi
  echo ""

  # Check summary
  if [ -f "${PHASE_DIR}/PHASE7_SUMMARY.md" ]; then
    echo -e "${GREEN}✓${NC} PHASE7_SUMMARY.md"
  else
    echo -e "${YELLOW}⚠${NC} PHASE7_SUMMARY.md not found"
  fi
  echo ""

  # Count PlantUML diagrams
  echo -e "${YELLOW}PlantUML Diagrams:${NC}"

  if [ -f "${PHASE_DIR}/microservice-dependencies.puml" ]; then
    echo -e "  ${GREEN}✓${NC} microservice-dependencies.puml"
  else
    echo -e "  ${YELLOW}○${NC} microservice-dependencies.puml (not generated)"
  fi

  if [ -f "${PHASE_DIR}/database-erd.puml" ]; then
    echo -e "  ${GREEN}✓${NC} database-erd.puml"
  else
    echo -e "  ${YELLOW}○${NC} database-erd.puml (not generated)"
  fi

  # Count event flow and state machine diagrams
  if command -v find &> /dev/null; then
    EVENT_FLOW_COUNT=$(find "${PHASE_DIR}" -name "event-flow-*.puml" 2>/dev/null | wc -l)
    STATE_MACHINE_COUNT=$(find "${PHASE_DIR}" -name "state-machine-*.puml" 2>/dev/null | wc -l)
    echo -e "  ${CYAN}   Event flow diagrams: ${EVENT_FLOW_COUNT}${NC}"
    echo -e "  ${CYAN}   State machine diagrams: ${STATE_MACHINE_COUNT}${NC}"
  fi
  echo ""

  echo -e "${GREEN}Outputs:${NC} ${PHASE_DIR}/"
  echo "   microservice-design.json"
  echo "   microservice-design-quality-report.json"
  echo "   PHASE7_SUMMARY.md"
  echo "   *.puml (diagrams)"
  echo ""

  echo -e "${GREEN}Next Phase:${NC} /rnvs-workflow:phase8-design-control-flow"
  echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

else
  echo -e "${RED}Invalid stage: ${STAGE}${NC}"
  echo "Usage: $0 <feature> <validate|summarize>"
  exit 1
fi
