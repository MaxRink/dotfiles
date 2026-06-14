#!/usr/bin/env bash
#
# Phase 7.1 Master Orchestration Script
# Handles validation and summary - agent launch done by command
#
# Usage: run-phase7.1.sh <feature-name> <stage>
#   stage: "validate" | "summarize"
#

set -e

FEATURE="$1"
STAGE="$2"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT}"
RESULTS_DIR="results/${FEATURE}/phase7.1"

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
  echo -e "${BLUE}Phase 7.1: Microservice Changes Design${NC}"
  echo -e "${BLUE}Feature: ${FEATURE}${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

  # Run validation pipeline
  bash ${PLUGIN_ROOT}/skills/validation-generation/microservice-changes-validator/scripts/validate-phase7.1.sh ${FEATURE}

  PIPELINE_EXIT_CODE=$?

  if [ $PIPELINE_EXIT_CODE -eq 2 ]; then
    echo -e "${RED}❌ Validation pipeline failed - check Phase 5 and Phase 6 prerequisites${NC}"
    exit 2
  fi

  if [ $PIPELINE_EXIT_CODE -eq 1 ]; then
    echo -e "${YELLOW}⚠️  Initial validation incomplete - agent will design delta model and improve quality${NC}"
  else
    echo -e "${GREEN}✅ Validation pipeline complete - ready for delta model design${NC}"
  fi

  echo ""
  echo -e "${BLUE}📂 Input files prepared:${NC}"
  echo "   - ${RESULTS_DIR}/computed-delta.json"
  echo "   - ${RESULTS_DIR}/classification.json"
  echo ""
  echo -e "${BLUE}🤖 Launching agent to design delta model...${NC}"
  echo ""

elif [ "$STAGE" = "summarize" ]; then
  #
  # SUMMARY STAGE: Display results after agent completes
  #
  echo ""
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}Phase 7.1 Complete - Delta Model Designed${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

  # Extract metrics if jq available
  if command -v jq &> /dev/null; then
    SERVICE_NAME=$(jq -r '.baseline.service_name' ${RESULTS_DIR}/microservice-changes-design.json 2>/dev/null || echo "Unknown")
    CHANGE_TYPE=$(jq -r '.change_type' ${RESULTS_DIR}/microservice-changes-design.json 2>/dev/null || echo "Unknown")
    COMPLEXITY=$(jq -r '.complexity_score' ${RESULTS_DIR}/microservice-changes-design.json 2>/dev/null || echo "0")
    BREAKING=$(jq -r '.is_breaking_change' ${RESULTS_DIR}/microservice-changes-design.json 2>/dev/null || echo "false")
    QUALITY_SCORE=$(jq -r '.validation_report.overall_quality_score' ${RESULTS_DIR}/microservice-changes-design.json 2>/dev/null || echo "0")

    ENDPOINTS_ADD=$(jq '.changes.api_changes.endpoints_to_add | length' ${RESULTS_DIR}/microservice-changes-design.json 2>/dev/null || echo "0")
    ENDPOINTS_MOD=$(jq '.changes.api_changes.endpoints_to_modify | length' ${RESULTS_DIR}/microservice-changes-design.json 2>/dev/null || echo "0")
    ENDPOINTS_DEP=$(jq '.changes.api_changes.endpoints_to_deprecate | length' ${RESULTS_DIR}/microservice-changes-design.json 2>/dev/null || echo "0")
    TABLES_ADD=$(jq '.changes.database_changes.tables_to_add | length' ${RESULTS_DIR}/microservice-changes-design.json 2>/dev/null || echo "0")
    COLUMNS_ADD=$(jq '.changes.database_changes.columns_to_add | length' ${RESULTS_DIR}/microservice-changes-design.json 2>/dev/null || echo "0")
    TOPICS_ADD=$(jq '.changes.event_changes.topics_to_add | length' ${RESULTS_DIR}/microservice-changes-design.json 2>/dev/null || echo "0")

    echo -e "${YELLOW}Service:${NC} ${SERVICE_NAME}"
    echo -e "${YELLOW}Change Type:${NC} ${CHANGE_TYPE}"
    echo -e "${YELLOW}Complexity:${NC} ${COMPLEXITY}"
    echo -e "${YELLOW}Breaking:${NC} ${BREAKING}"
    echo -e "${YELLOW}Quality Score:${NC} ${QUALITY_SCORE}/100"
    echo ""
    echo -e "${YELLOW}Changes Designed:${NC}"
    echo "  API Endpoints: +${ENDPOINTS_ADD} ~${ENDPOINTS_MOD} -${ENDPOINTS_DEP}"
    echo "  Database: +${TABLES_ADD} tables, +${COLUMNS_ADD} columns"
    echo "  Events: +${TOPICS_ADD} topics"
  else
    echo -e "${YELLOW}ℹ️  Install jq for detailed metrics${NC}"
  fi

  echo ""
  echo -e "${GREEN}📁 Outputs:${NC} ${RESULTS_DIR}/"
  echo "   ✅ microservice-changes-design.json (delta model)"
  echo "   ✅ changes-quality-report.json (validation results)"
  echo "   ✅ computed-delta.json (Phase 6 vs Phase 5 diff)"
  echo "   ✅ classification.json (change type analysis)"
  echo ""
  echo -e "${GREEN}Next Phase:${NC} /rnvs-workflow:phase8-design-control-flow"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

else
  echo -e "${RED}❌ Invalid stage: ${STAGE}${NC}"
  echo "Usage: $0 <feature> <validate|summarize>"
  exit 1
fi
