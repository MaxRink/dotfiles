#!/usr/bin/env bash
#
# Phase 7.1 Validation Pipeline Wrapper
# Orchestrates 3-script sequence: compute-delta → classify → validate
#
# Usage: validate-phase7.1.sh <feature-name>
# Example: validate-phase7.1.sh fnport
#

set -e  # Exit on first error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Validate arguments
if [ $# -lt 1 ]; then
  echo -e "${RED}❌ Error: Feature name required${NC}"
  echo ""
  echo "Usage: $0 <feature-name>"
  echo "Example: $0 fnport"
  echo ""
  exit 1
fi

FEATURE="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="results/${FEATURE}"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Phase 7.1 Validation Pipeline${NC}"
echo -e "${BLUE}  Feature: ${FEATURE}${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Validate prerequisites
if [ ! -f "${RESULTS_DIR}/phase6/analysis.json" ]; then
  echo -e "${RED}❌ Phase 6 analysis.json not found${NC}"
  echo "   Expected: ${RESULTS_DIR}/phase6/analysis.json"
  echo ""
  echo "Please complete Phase 6 first:"
  echo "  /rnvs-workflow:phase6-vnrm-code-analysis ${FEATURE}"
  echo ""
  exit 2
fi

if [ ! -f "${RESULTS_DIR}/phase5/control-flow-mapping.json" ]; then
  echo -e "${RED}❌ Phase 5 control-flow-mapping.json not found${NC}"
  echo "   Expected: ${RESULTS_DIR}/phase5/control-flow-mapping.json"
  echo ""
  echo "Please complete Phase 5 first:"
  echo "  /rnvs-workflow:phase5-control-flow ${FEATURE}"
  echo ""
  exit 2
fi

# Create output directory
mkdir -p "${RESULTS_DIR}/phase7.1"

echo -e "${BLUE}🔍 Phase 7.1 Validation Pipeline Starting...${NC}"
echo ""

# Step 1: Compute Delta
echo -e "${BLUE}📊 Step 1/3: Computing delta (Phase 6 baseline vs Phase 5 requirements)${NC}"
node "${SCRIPT_DIR}/compute-delta.js" \
  --phase6 "${RESULTS_DIR}/phase6/analysis.json" \
  --phase5 "${RESULTS_DIR}/phase5/control-flow-mapping.json" \
  --output "${RESULTS_DIR}/phase7.1/computed-delta.json"

DELTA_EXIT_CODE=$?

if [ $DELTA_EXIT_CODE -ne 0 ]; then
  echo -e "${RED}❌ Delta computation failed (exit code: ${DELTA_EXIT_CODE})${NC}"
  echo ""
  echo "Possible causes:"
  echo "  - Phase 6 or Phase 5 JSON files are invalid"
  echo "  - Missing required fields in input files"
  echo "  - JSON parse error"
  echo ""
  exit 1
fi

echo -e "${GREEN}✅ Delta computed: ${RESULTS_DIR}/phase7.1/computed-delta.json${NC}"
echo ""

# Step 2: Classify Changes
echo -e "${BLUE}🏷️  Step 2/3: Classifying change type and complexity${NC}"
node "${SCRIPT_DIR}/classify-change-type.js" \
  --delta "${RESULTS_DIR}/phase7.1/computed-delta.json" \
  --output "${RESULTS_DIR}/phase7.1/classification.json"

CLASSIFY_EXIT_CODE=$?

if [ $CLASSIFY_EXIT_CODE -ne 0 ]; then
  echo -e "${RED}❌ Classification failed (exit code: ${CLASSIFY_EXIT_CODE})${NC}"
  echo ""
  echo "Possible causes:"
  echo "  - computed-delta.json is invalid"
  echo "  - Missing required delta fields"
  echo ""
  exit 1
fi

echo -e "${GREEN}✅ Classification complete: ${RESULTS_DIR}/phase7.1/classification.json${NC}"
echo ""

# Display classification results
if command -v jq &> /dev/null; then
  CHANGE_TYPE=$(jq -r '.change_type' "${RESULTS_DIR}/phase7.1/classification.json" 2>/dev/null || echo "UNKNOWN")
  COMPLEXITY=$(jq -r '.complexity_score' "${RESULTS_DIR}/phase7.1/classification.json" 2>/dev/null || echo "0")
  BREAKING=$(jq -r '.is_breaking_change' "${RESULTS_DIR}/phase7.1/classification.json" 2>/dev/null || echo "false")
  QUALITY_TARGET=$(jq -r '.quality_target' "${RESULTS_DIR}/phase7.1/classification.json" 2>/dev/null || echo "75")

  echo -e "   ${YELLOW}Change Type:${NC} ${CHANGE_TYPE}"
  echo -e "   ${YELLOW}Complexity Score:${NC} ${COMPLEXITY}"
  echo -e "   ${YELLOW}Breaking Change:${NC} ${BREAKING}"
  echo -e "   ${YELLOW}Quality Target:${NC} ≥${QUALITY_TARGET}/100"
  echo ""
fi

# Step 3: Validate Quality
echo -e "${BLUE}✔️  Step 3/3: Validating delta model quality${NC}"
node "${SCRIPT_DIR}/validate-changes.js" \
  --delta "${RESULTS_DIR}/phase7.1/computed-delta.json" \
  --classification "${RESULTS_DIR}/phase7.1/classification.json" \
  --output "${RESULTS_DIR}/phase7.1/changes-quality-report.json"

VALIDATION_EXIT_CODE=$?

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ $VALIDATION_EXIT_CODE -eq 0 ]; then
  echo -e "${GREEN}✅ Validation PASSED (COMPLETE status)${NC}"
  echo -e "   Quality score ≥ target threshold"
elif [ $VALIDATION_EXIT_CODE -eq 1 ]; then
  echo -e "${YELLOW}⚠️  Validation INCOMPLETE${NC}"
  echo -e "   Review quality report for recommendations"
  echo ""
  echo -e "   Quality report: ${RESULTS_DIR}/phase7.1/changes-quality-report.json"
  echo ""
  if command -v jq &> /dev/null; then
    echo -e "${YELLOW}Top recommendations:${NC}"
    jq -r '.recommendations[:3][] | "  - " + .' "${RESULTS_DIR}/phase7.1/changes-quality-report.json" 2>/dev/null || echo "  (use jq to view recommendations)"
  fi
else
  echo -e "${RED}❌ Validation ERROR${NC}"
  echo -e "   Script error or invalid inputs"
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}📁 Outputs:${NC}"
echo -e "   ${RESULTS_DIR}/phase7.1/computed-delta.json"
echo -e "   ${RESULTS_DIR}/phase7.1/classification.json"
echo -e "   ${RESULTS_DIR}/phase7.1/changes-quality-report.json"
echo ""

if [ $VALIDATION_EXIT_CODE -eq 0 ]; then
  echo -e "${GREEN}✅ Phase 7.1 validation pipeline completed successfully${NC}"
  echo -e "   Ready to proceed with delta model design"
else
  echo -e "${YELLOW}⚠️  Phase 7.1 validation pipeline completed with warnings${NC}"
  echo -e "   Review quality report before proceeding"
fi

echo ""

exit $VALIDATION_EXIT_CODE
