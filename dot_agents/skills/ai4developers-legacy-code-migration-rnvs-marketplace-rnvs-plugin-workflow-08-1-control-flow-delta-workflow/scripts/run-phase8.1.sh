#!/usr/bin/env bash
#
# Phase 8.1 Master Orchestration Script
# Handles validation and summary - agent launch done by command
#
# Usage: run-phase8.1.sh <feature-name> <stage>
#   stage: "validate" | "summarize"
#

set -e

FEATURE="$1"
STAGE="$2"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT}"
RESULTS_DIR="results/${FEATURE}/phase8.1"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

if [ "$STAGE" = "validate" ]; then
  #
  # VALIDATION STAGE: Run validation pipeline before agent starts
  #
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}Phase 8.1: Control Flow Changes Design${NC}"
  echo -e "${BLUE}Feature: ${FEATURE}${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

  # Run validation pipeline
  bash ${PLUGIN_ROOT}/skills/validation-generation/control-flow-changes-validator/scripts/validate-phase8.1.sh ${FEATURE}

  PIPELINE_EXIT_CODE=$?

  if [ $PIPELINE_EXIT_CODE -eq 2 ]; then
    echo -e "${RED}Validation pipeline failed - check Phase 7.1 and Phase 5 prerequisites${NC}"
    exit 2
  fi

  if [ $PIPELINE_EXIT_CODE -eq 1 ]; then
    echo -e "${YELLOW}Initial validation incomplete - agent will design control flow changes and improve quality${NC}"
  else
    echo -e "${GREEN}Validation pipeline complete - ready for control flow changes design${NC}"
  fi

  echo ""
  echo -e "${BLUE}Input files prepared:${NC}"
  echo "   - ${RESULTS_DIR}/computed-control-flow-delta.json"
  echo "   - ${RESULTS_DIR}/classification.json"
  echo ""
  echo -e "${BLUE}Launching agent to design control flow changes...${NC}"
  echo ""

elif [ "$STAGE" = "summarize" ]; then
  #
  # SUMMARY STAGE: Display results after agent completes
  #
  echo ""
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}Phase 8.1 Complete - Control Flow Changes Designed${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

  # Extract metrics if jq available
  if command -v jq &> /dev/null; then
    CHANGE_TYPE=$(jq -r '.change_type' ${RESULTS_DIR}/classification.json 2>/dev/null || echo "Unknown")
    COMPLEXITY=$(jq -r '.complexity_score' ${RESULTS_DIR}/classification.json 2>/dev/null || echo "0")
    QUALITY_TARGET=$(jq -r '.quality_target' ${RESULTS_DIR}/classification.json 2>/dev/null || echo "75")

    # Extract change summary if available
    SEQUENCES_ADDED=$(jq -r '.change_summary.sequences_added // 0' ${RESULTS_DIR}/classification.json 2>/dev/null || echo "0")
    SEQUENCES_MODIFIED=$(jq -r '.change_summary.sequences_modified // 0' ${RESULTS_DIR}/classification.json 2>/dev/null || echo "0")
    ACTIVITIES_ADDED=$(jq -r '.change_summary.activities_added // 0' ${RESULTS_DIR}/classification.json 2>/dev/null || echo "0")
    SAGAS_ADDED=$(jq -r '.change_summary.sagas_added // 0' ${RESULTS_DIR}/classification.json 2>/dev/null || echo "0")
    EVENT_FLOWS=$(jq -r '.change_summary.event_flows_modified // 0' ${RESULTS_DIR}/classification.json 2>/dev/null || echo "0")

    # Try to get quality score from validation report
    if [ -f "${RESULTS_DIR}/changes-quality-report.json" ]; then
      QUALITY_SCORE=$(jq -r '.overall_quality_score // 0' ${RESULTS_DIR}/changes-quality-report.json 2>/dev/null || echo "0")
      STATUS=$(jq -r '.overall_status // "UNKNOWN"' ${RESULTS_DIR}/changes-quality-report.json 2>/dev/null || echo "UNKNOWN")
    else
      QUALITY_SCORE="N/A"
      STATUS="N/A"
    fi

    echo -e "${YELLOW}Change Type:${NC} ${CHANGE_TYPE}"
    echo -e "${YELLOW}Complexity:${NC} ${COMPLEXITY}"
    echo -e "${YELLOW}Quality Target:${NC} ${QUALITY_TARGET}"
    echo -e "${YELLOW}Quality Score:${NC} ${QUALITY_SCORE}/100"
    echo -e "${YELLOW}Status:${NC} ${STATUS}"
    echo ""
    echo -e "${YELLOW}Changes Designed:${NC}"
    echo "  Sequence diagrams: +${SEQUENCES_ADDED} ~${SEQUENCES_MODIFIED}"
    echo "  Activity diagrams: +${ACTIVITIES_ADDED}"
    echo "  Saga diagrams: +${SAGAS_ADDED}"
    echo "  Event flows: ~${EVENT_FLOWS}"
  else
    echo -e "${YELLOW}Install jq for detailed metrics${NC}"
  fi

  echo ""
  echo -e "${GREEN}Outputs:${NC} ${RESULTS_DIR}/"
  echo "   computed-control-flow-delta.json (delta computation)"
  echo "   classification.json (change type analysis)"
  echo "   control-flow-changes-design.json (delta model)"
  echo "   control-flow-changes.md (documentation)"
  echo "   changes-quality-report.json (validation results)"
  echo "   *.puml (PlantUML diagrams)"
  echo ""
  echo -e "${GREEN}Next Phase:${NC} /rnvs-workflow:phase9-gap-analysis"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

else
  echo -e "${RED}Invalid stage: ${STAGE}${NC}"
  echo "Usage: $0 <feature> <validate|summarize>"
  exit 1
fi
