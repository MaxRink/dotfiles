#!/usr/bin/env bash
#
# Phase 8.1 Validation Pipeline Wrapper
# Orchestrates 3-script sequence: compute-control-flow-delta → classify → validate
#
# Usage: validate-phase8.1.sh <feature-name>
# Example: validate-phase8.1.sh fnport
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
  echo -e "${RED}Error: Feature name required${NC}"
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
echo -e "${BLUE}  Phase 8.1 Validation Pipeline${NC}"
echo -e "${BLUE}  Feature: ${FEATURE}${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Validate prerequisites
if [ ! -f "${RESULTS_DIR}/phase7.1/microservice-changes-design.json" ]; then
  echo -e "${RED}Phase 7.1 microservice-changes-design.json not found${NC}"
  echo "   Expected: ${RESULTS_DIR}/phase7.1/microservice-changes-design.json"
  echo ""
  echo "Please complete Phase 7.1 first:"
  echo "  /rnvs-workflow:phase7.1-design-changes-in-microservice ${FEATURE}"
  echo ""
  exit 2
fi

if [ ! -f "${RESULTS_DIR}/phase5/control-flow-mapping.json" ]; then
  echo -e "${RED}Phase 5 control-flow-mapping.json not found${NC}"
  echo "   Expected: ${RESULTS_DIR}/phase5/control-flow-mapping.json"
  echo ""
  echo "Please complete Phase 5 first:"
  echo "  /rnvs-workflow:phase5-control-flow ${FEATURE}"
  echo ""
  exit 2
fi

# Create output directory
mkdir -p "${RESULTS_DIR}/phase8.1"

echo -e "${BLUE}Phase 8.1 Validation Pipeline Starting...${NC}"
echo ""

# Step 1: Compute Control Flow Delta
echo -e "${BLUE}Step 1/3: Computing control flow delta (Phase 7.1 changes -> control flow changes)${NC}"
node "${SCRIPT_DIR}/compute-control-flow-delta.js" \
  --phase7.1 "${RESULTS_DIR}/phase7.1/microservice-changes-design.json" \
  --phase5 "${RESULTS_DIR}/phase5/control-flow-mapping.json" \
  --output "${RESULTS_DIR}/phase8.1/computed-control-flow-delta.json"

DELTA_EXIT_CODE=$?

if [ $DELTA_EXIT_CODE -ne 0 ]; then
  echo -e "${RED}Delta computation failed (exit code: ${DELTA_EXIT_CODE})${NC}"
  echo ""
  echo "Possible causes:"
  echo "  - Phase 7.1 or Phase 5 JSON files are invalid"
  echo "  - Missing required fields in input files"
  echo "  - JSON parse error"
  echo ""
  exit 1
fi

echo ""

# Step 2: Classify Changes
echo -e "${BLUE}Step 2/3: Classifying control flow change type and complexity${NC}"
node "${SCRIPT_DIR}/classify-change-type.js" \
  --delta "${RESULTS_DIR}/phase8.1/computed-control-flow-delta.json" \
  --output "${RESULTS_DIR}/phase8.1/classification.json"

CLASSIFY_EXIT_CODE=$?

if [ $CLASSIFY_EXIT_CODE -ne 0 ]; then
  echo -e "${RED}Classification failed (exit code: ${CLASSIFY_EXIT_CODE})${NC}"
  echo ""
  echo "Possible causes:"
  echo "  - computed-control-flow-delta.json is invalid"
  echo "  - Missing required delta fields"
  echo ""
  exit 1
fi

echo ""

# Step 3: Validate Quality
echo -e "${BLUE}Step 3/3: Validating control flow delta quality${NC}"
node "${SCRIPT_DIR}/validate-changes.js" \
  --delta "${RESULTS_DIR}/phase8.1/computed-control-flow-delta.json" \
  --classification "${RESULTS_DIR}/phase8.1/classification.json" \
  --output "${RESULTS_DIR}/phase8.1/changes-quality-report.json"

VALIDATION_EXIT_CODE=$?

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ $VALIDATION_EXIT_CODE -eq 0 ]; then
  echo -e "${GREEN}Validation PASSED (COMPLETE status)${NC}"
  echo -e "   Quality score >= target threshold"
elif [ $VALIDATION_EXIT_CODE -eq 1 ]; then
  echo -e "${YELLOW}Validation INCOMPLETE${NC}"
  echo -e "   Review quality report for recommendations"
  echo ""
  echo -e "   Quality report: ${RESULTS_DIR}/phase8.1/changes-quality-report.json"
  echo ""
  if command -v jq &> /dev/null; then
    echo -e "${YELLOW}Top recommendations:${NC}"
    jq -r '.recommendations[:3][] | "  - " + .' "${RESULTS_DIR}/phase8.1/changes-quality-report.json" 2>/dev/null || echo "  (use jq to view recommendations)"
  fi
else
  echo -e "${RED}Validation ERROR${NC}"
  echo -e "   Script error or invalid inputs"
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}Outputs:${NC}"
echo -e "   ${RESULTS_DIR}/phase8.1/computed-control-flow-delta.json"
echo -e "   ${RESULTS_DIR}/phase8.1/classification.json"
echo -e "   ${RESULTS_DIR}/phase8.1/changes-quality-report.json"
echo ""

if [ $VALIDATION_EXIT_CODE -eq 0 ]; then
  echo -e "${GREEN}Phase 8.1 validation pipeline completed successfully${NC}"
  echo -e "   Ready to proceed with control flow changes design"
else
  echo -e "${YELLOW}Phase 8.1 validation pipeline completed with warnings${NC}"
  echo -e "   Review quality report before proceeding"
fi

echo ""

exit $VALIDATION_EXIT_CODE
