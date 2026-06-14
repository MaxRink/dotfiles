#!/bin/bash
# Agent Trigger Tester
# Tests if an agent file has proper triggering conditions by checking
# description quality and example blocks

set -euo pipefail

# Usage
if [ $# -eq 0 ]; then
  echo "Usage: $0 <path/to/agent.md>"
  echo ""
  echo "Tests agent triggering quality:"
  echo "  - Description includes trigger phrases"
  echo "  - Example blocks are present and well-formed"
  echo "  - Commentary explains why agent triggers"
  exit 1
fi

AGENT_FILE="$1"

if [ ! -f "$AGENT_FILE" ]; then
  echo "Error: File not found: $AGENT_FILE"
  exit 1
fi

echo "Testing agent triggering: $AGENT_FILE"
echo ""

error_count=0
warning_count=0

# Extract frontmatter
frontmatter=$(sed -n '/^---$/,/^---$/p' "$AGENT_FILE" | sed '1d;$d')

if [ -z "$frontmatter" ]; then
  echo "FAIL: No YAML frontmatter found"
  exit 1
fi

# Check description exists
description=$(echo "$frontmatter" | grep -A 100 '^description:' | tail -n +1 | head -20)
if [ -z "$description" ]; then
  description=$(echo "$frontmatter" | grep '^description:' || true)
fi

if [ -z "$description" ]; then
  echo "FAIL: No description field in frontmatter"
  ((error_count++))
else
  echo "OK: Description field found"

  # Check for trigger phrases
  if echo "$description" | grep -qi "use this agent when\|trigger when\|should be used when"; then
    echo "OK: Contains trigger condition phrase"
  else
    echo "WARN: Description should start with 'Use this agent when...'"
    ((warning_count++))
  fi
fi

# Check for example blocks
example_count=$(grep -c '<example>' "$AGENT_FILE" || true)
if [ "$example_count" -eq 0 ]; then
  echo "FAIL: No <example> blocks found (need 2-4)"
  ((error_count++))
elif [ "$example_count" -lt 2 ]; then
  echo "WARN: Only $example_count example(s) found (recommend 2-4)"
  ((warning_count++))
elif [ "$example_count" -gt 4 ]; then
  echo "WARN: $example_count examples found (recommend 2-4, more can bloat context)"
  ((warning_count++))
else
  echo "OK: $example_count example blocks found"
fi

# Check example structure
if [ "$example_count" -gt 0 ]; then
  # Check for user/assistant/commentary in examples
  if grep -q 'user:' "$AGENT_FILE"; then
    echo "OK: Examples contain user messages"
  else
    echo "WARN: Examples should contain 'user:' messages"
    ((warning_count++))
  fi

  if grep -q 'assistant:' "$AGENT_FILE"; then
    echo "OK: Examples contain assistant responses"
  else
    echo "WARN: Examples should contain 'assistant:' responses"
    ((warning_count++))
  fi

  commentary_count=$(grep -c '<commentary>' "$AGENT_FILE" || true)
  if [ "$commentary_count" -eq 0 ]; then
    echo "WARN: Examples should contain <commentary> explaining why agent triggers"
    ((warning_count++))
  else
    echo "OK: Examples contain commentary"
  fi

  context_count=$(grep -c 'Context:' "$AGENT_FILE" || true)
  if [ "$context_count" -eq 0 ]; then
    echo "WARN: Examples should contain 'Context:' descriptions"
    ((warning_count++))
  else
    echo "OK: Examples contain context descriptions"
  fi
fi

# Check for system prompt (body after frontmatter)
body=$(sed -n '/^---$/,/^---$/!p' "$AGENT_FILE" | tail -n +1)
body_length=${#body}

if [ "$body_length" -lt 100 ]; then
  echo "FAIL: System prompt is too short ($body_length chars, need >100)"
  ((error_count++))
else
  echo "OK: System prompt present ($body_length chars)"
fi

echo ""
echo "---"
if [ $error_count -eq 0 ] && [ $warning_count -eq 0 ]; then
  echo "OK: All triggering checks passed!"
  exit 0
elif [ $error_count -eq 0 ]; then
  echo "WARN: Passed with $warning_count warning(s)"
  exit 0
else
  echo "FAIL: $error_count error(s) and $warning_count warning(s)"
  exit 1
fi
