#!/usr/bin/env bash
#
# Phase 8 Master Orchestration Script
# Handles validation and summary - agent launch done by command
#
# Usage: run-phase8.sh <feature-name> <stage>
#   stage: "validate" | "summarize"
#

set -e

FEATURE="$1"
STAGE="$2"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT}"
RESULTS_DIR="results/${FEATURE}"
PHASE8_DIR="${RESULTS_DIR}/phase8"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

if [ "$STAGE" = "validate" ]; then
  #
  # VALIDATION STAGE: Check prerequisites and create output directory
  #
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}Phase 8: Control Flow and Service Orchestration Design${NC}"
  echo -e "${BLUE}Feature: ${FEATURE}${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

  # Check workflow mode
  CONTEXT_FILE="${RESULTS_DIR}/.workflow-context.json"
  if [ -f "${CONTEXT_FILE}" ] && command -v jq &> /dev/null; then
    WORKFLOW_MODE=$(jq -r '.workflow_mode // "UNKNOWN"' ${CONTEXT_FILE} 2>/dev/null || echo "UNKNOWN")
    if [ "${WORKFLOW_MODE}" = "CHANGE" ]; then
      echo -e "${RED}ERROR: Phase 8 is for NEW mode only.${NC}"
      echo -e "${YELLOW}For CHANGE mode, use: /rnvs-workflow:phase8.1-design-control-flow-changes${NC}"
      exit 2
    fi
  fi

  # Check required prerequisites
  MISSING_PREREQS=0

  echo -e "${YELLOW}Checking prerequisites...${NC}"
  echo ""

  # Required: Phase 7 microservice design
  if [ -f "${RESULTS_DIR}/phase7/microservice-design.json" ]; then
    echo -e "${GREEN}✓${NC} Phase 7 microservice-design.json"
  else
    echo -e "${RED}✗${NC} Phase 7 microservice-design.json (required)"
    MISSING_PREREQS=1
  fi

  # Required: Phase 5 control flow mapping
  if [ -f "${RESULTS_DIR}/phase5/control-flow-mapping.json" ]; then
    echo -e "${GREEN}✓${NC} Phase 5 control-flow-mapping.json"
  else
    echo -e "${RED}✗${NC} Phase 5 control-flow-mapping.json (required)"
    MISSING_PREREQS=1
  fi

  # Recommended: Phase 3 business rules
  if [ -f "${RESULTS_DIR}/phase3/ruletable.json" ]; then
    echo -e "${GREEN}✓${NC} Phase 3 ruletable.json"
  else
    echo -e "${YELLOW}○${NC} Phase 3 ruletable.json (recommended)"
  fi

  # Recommended: Phase 2 flow diagrams
  PHASE2_FLOWS=$(find "${RESULTS_DIR}/phase2" -name "flow-*.puml" 2>/dev/null | wc -l)
  if [ "${PHASE2_FLOWS}" -gt 0 ]; then
    echo -e "${GREEN}✓${NC} Phase 2 flow diagrams (${PHASE2_FLOWS} found)"
  else
    echo -e "${YELLOW}○${NC} Phase 2 flow diagrams (recommended)"
  fi

  echo ""

  if [ ${MISSING_PREREQS} -eq 1 ]; then
    echo -e "${RED}ERROR: Missing required prerequisites.${NC}"
    echo -e "${RED}Complete Phase 5 and Phase 7 before running Phase 8.${NC}"
    exit 2
  fi

  # Create output directory
  mkdir -p "${PHASE8_DIR}"

  echo -e "${GREEN}Prerequisites validated - ready for control flow design${NC}"
  echo ""
  echo -e "${BLUE}Input files:${NC}"
  echo "   - ${RESULTS_DIR}/phase7/microservice-design.json"
  echo "   - ${RESULTS_DIR}/phase5/control-flow-mapping.json"
  echo "   - ${RESULTS_DIR}/phase3/ruletable.json"
  echo "   - ${RESULTS_DIR}/phase2/flow-*.puml"
  echo ""
  echo -e "${BLUE}Launching agent to design control flows...${NC}"
  echo ""

elif [ "$STAGE" = "summarize" ]; then
  #
  # SUMMARY STAGE: Display results after agent completes
  #
  echo ""
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}Phase 8 Complete - Control Flows Designed${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

  # Count generated outputs
  SEQUENCE_COUNT=$(find "${PHASE8_DIR}" -name "sequence-*.puml" 2>/dev/null | wc -l)
  ACTIVITY_COUNT=$(find "${PHASE8_DIR}" -name "activity-*.puml" 2>/dev/null | wc -l)
  SAGA_COUNT=$(find "${PHASE8_DIR}" -name "saga-*.puml" 2>/dev/null | wc -l)
  OPENAPI_COUNT=$(find "${PHASE8_DIR}" -name "openapi-*.yaml" 2>/dev/null | wc -l)

  # Check for event architecture
  if [ -f "${PHASE8_DIR}/event-architecture.puml" ]; then
    EVENT_ARCH="1"
  else
    EVENT_ARCH="0"
  fi

  TOTAL_DIAGRAMS=$((SEQUENCE_COUNT + ACTIVITY_COUNT + SAGA_COUNT + EVENT_ARCH))

  echo -e "${YELLOW}PlantUML Diagrams Generated:${NC}"
  echo "  Sequence diagrams: ${SEQUENCE_COUNT}"
  echo "  Activity diagrams: ${ACTIVITY_COUNT}"
  echo "  Saga diagrams: ${SAGA_COUNT}"
  echo "  Event architecture: ${EVENT_ARCH}"
  echo "  Total diagrams: ${TOTAL_DIAGRAMS}"
  echo ""
  echo -e "${YELLOW}OpenAPI Specifications:${NC} ${OPENAPI_COUNT}"
  echo ""

  # List documentation files
  echo -e "${YELLOW}Documentation:${NC}"
  [ -f "${PHASE8_DIR}/saga-documentation.md" ] && echo "  ✓ saga-documentation.md"
  [ -f "${PHASE8_DIR}/event-flow-documentation.md" ] && echo "  ✓ event-flow-documentation.md"
  [ -f "${PHASE8_DIR}/api-contract-documentation.md" ] && echo "  ✓ api-contract-documentation.md"
  [ -f "${PHASE8_DIR}/PHASE8_SUMMARY.md" ] && echo "  ✓ PHASE8_SUMMARY.md"
  echo ""

  echo -e "${GREEN}Outputs:${NC} ${PHASE8_DIR}/"
  echo ""
  echo -e "${GREEN}Next Phase:${NC} /rnvs-workflow:phase9-gap-analysis"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

else
  echo -e "${RED}Invalid stage: ${STAGE}${NC}"
  echo "Usage: $0 <feature> <validate|summarize>"
  exit 1
fi
