#!/usr/bin/env bash
#
# Phase 13.1 Master Orchestration Script
# Handles validation and summary - agent launch done by command
#
# Usage: run-phase13.1.sh <feature-name> <stage>
#   stage: "validate" | "summarize"
#

set -e

FEATURE="$1"
STAGE="$2"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT}"
RESULTS_DIR="results/${FEATURE}/phase13.1"

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
  echo -e "${BLUE}Phase 13.1: Source Code Changes Generation${NC}"
  echo -e "${BLUE}Feature: ${FEATURE}${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

  # Run validation pipeline
  bash ${PLUGIN_ROOT}/skills/13-source-code-generation-workflow/scripts/validate-phase13.1.sh ${FEATURE}

  PIPELINE_EXIT_CODE=$?

  if [ $PIPELINE_EXIT_CODE -eq 2 ]; then
    echo -e "${RED}❌ Validation pipeline failed - check prerequisites${NC}"
    exit 2
  fi

  if [ $PIPELINE_EXIT_CODE -eq 1 ]; then
    echo -e "${YELLOW}⚠️  Initial validation incomplete - agent will proceed with available data${NC}"
  else
    echo -e "${GREEN}✅ Validation pipeline complete - ready for code generation${NC}"
  fi

  echo ""
  echo -e "${BLUE}📂 Input files prepared:${NC}"
  echo "   - ${RESULTS_DIR}/computed-code-delta.json"
  echo "   - ${RESULTS_DIR}/classification.json"
  echo ""
  echo -e "${BLUE}🤖 Launching agent to generate source code changes...${NC}"
  echo ""

elif [ "$STAGE" = "summarize" ]; then
  #
  # SUMMARY STAGE: Display results after agent completes
  #
  echo ""
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}Phase 13.1 Complete - Source Code Changes Generated${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

  # Extract metrics if jq available
  if command -v jq &> /dev/null; then
    if [ -f "${RESULTS_DIR}/code-changes-manifest.json" ]; then
      FILES_CREATED=$(jq '.files_created | length' ${RESULTS_DIR}/code-changes-manifest.json 2>/dev/null || echo "0")
      FILES_MODIFIED=$(jq '.files_modified | length' ${RESULTS_DIR}/code-changes-manifest.json 2>/dev/null || echo "0")
      MIGRATIONS=$(jq '.migrations_generated | length' ${RESULTS_DIR}/code-changes-manifest.json 2>/dev/null || echo "0")
      SECURITY_STATUS=$(jq -r '.security_scan_status' ${RESULTS_DIR}/code-changes-manifest.json 2>/dev/null || echo "UNKNOWN")

      echo -e "${YELLOW}Files Created:${NC} ${FILES_CREATED}"
      echo -e "${YELLOW}Files Modified:${NC} ${FILES_MODIFIED}"
      echo -e "${YELLOW}Migrations Generated:${NC} ${MIGRATIONS}"
      echo -e "${YELLOW}Security Scan:${NC} ${SECURITY_STATUS}"
    else
      echo -e "${YELLOW}ℹ️  Manifest not found - checking individual files${NC}"
    fi

    if [ -f "${RESULTS_DIR}/classification.json" ]; then
      CHANGE_TYPE=$(jq -r '.change_type' ${RESULTS_DIR}/classification.json 2>/dev/null || echo "Unknown")
      COMPLEXITY=$(jq -r '.complexity_score' ${RESULTS_DIR}/classification.json 2>/dev/null || echo "0")

      echo ""
      echo -e "${YELLOW}Change Type:${NC} ${CHANGE_TYPE}"
      echo -e "${YELLOW}Complexity Score:${NC} ${COMPLEXITY}"
    fi
  else
    echo -e "${YELLOW}ℹ️  Install jq for detailed metrics${NC}"
  fi

  echo ""
  echo -e "${GREEN}📁 Outputs:${NC} ${RESULTS_DIR}/"

  # Check which files exist
  [ -d "${RESULTS_DIR}/source_code" ] && echo "   ✅ source_code/ (generated code)"
  [ -f "${RESULTS_DIR}/computed-code-delta.json" ] && echo "   ✅ computed-code-delta.json"
  [ -f "${RESULTS_DIR}/classification.json" ] && echo "   ✅ classification.json"
  [ -f "${RESULTS_DIR}/changes-quality-report.json" ] && echo "   ✅ changes-quality-report.json"
  [ -f "${RESULTS_DIR}/code-changes-manifest.json" ] && echo "   ✅ code-changes-manifest.json"
  [ -f "${RESULTS_DIR}/migration-guide.md" ] && echo "   ✅ migration-guide.md"
  [ -f "${RESULTS_DIR}/security_scan.txt" ] && echo "   ✅ security_scan.txt"

  echo ""
  echo -e "${GREEN}Next Phase:${NC} /rnvs-workflow:phase14.1-generate-system-test-scripts"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

else
  echo -e "${RED}❌ Invalid stage: ${STAGE}${NC}"
  echo "Usage: $0 <feature> <validate|summarize>"
  exit 1
fi
