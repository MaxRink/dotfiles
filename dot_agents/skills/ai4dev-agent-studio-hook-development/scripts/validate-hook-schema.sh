#!/bin/bash
# Hook Schema Validator
# Validates hooks.json structure and checks for common issues

set -euo pipefail

# Usage
if [ $# -eq 0 ]; then
  echo "Usage: $0 <path/to/hooks.json>"
  echo ""
  echo "Validates hook configuration file for:"
  echo "  - Valid JSON syntax"
  echo "  - Required fields"
  echo "  - Hook type validity"
  echo "  - Matcher patterns"
  echo "  - Timeout ranges"
  exit 1
fi

HOOKS_FILE="$1"

if [ ! -f "$HOOKS_FILE" ]; then
  echo "❌ Error: File not found: $HOOKS_FILE"
  exit 1
fi

echo "🔍 Validating hooks configuration: $HOOKS_FILE"
echo ""

# Check 1: Valid JSON
echo "Checking JSON syntax..."
if ! jq empty "$HOOKS_FILE" 2>/dev/null; then
  echo "❌ Invalid JSON syntax"
  exit 1
fi
echo "✅ Valid JSON"

# Check 1.5: Handle wrapper format (plugin hooks use {"hooks": {...}})
echo ""
echo "Checking format..."
HAS_WRAPPER=$(jq -e '.hooks' "$HOOKS_FILE" > /dev/null 2>&1 && echo "true" || echo "false")
if [ "$HAS_WRAPPER" = "true" ]; then
  echo "Detected wrapper format ({\"hooks\": {...}})"
  JQ_PREFIX=".hooks"
else
  echo "Detected direct format (events at root)"
  JQ_PREFIX="."
fi

# Check 2: Root structure
echo ""
echo "Checking root structure..."
VALID_EVENTS=("PreToolUse" "PostToolUse" "PostToolUseFailure" "UserPromptSubmit" "Stop" "SubagentStop" "SubagentStart" "PermissionRequest" "SessionStart" "SessionEnd" "PreCompact" "Notification")

for event in $(jq -r "${JQ_PREFIX} | keys[]" "$HOOKS_FILE"); do
  found=false
  for valid_event in "${VALID_EVENTS[@]}"; do
    if [ "$event" = "$valid_event" ]; then
      found=true
      break
    fi
  done

  if [ "$found" = false ]; then
    echo "⚠️  Unknown event type: $event"
  fi
done
echo "✅ Root structure valid"

# Check 3: Validate each hook
echo ""
echo "Validating individual hooks..."

error_count=0
warning_count=0

for event in $(jq -r "${JQ_PREFIX} | keys[]" "$HOOKS_FILE"); do
  hook_count=$(jq -r "${JQ_PREFIX}.\"$event\" | length" "$HOOKS_FILE")

  for ((i=0; i<hook_count; i++)); do
    # Check matcher exists
    matcher=$(jq -r "${JQ_PREFIX}.\"$event\"[$i].matcher // empty" "$HOOKS_FILE")
    if [ -z "$matcher" ]; then
      echo "❌ $event[$i]: Missing 'matcher' field"
      ((error_count++))
      continue
    fi

    # Check hooks array exists
    hooks=$(jq -r "${JQ_PREFIX}.\"$event\"[$i].hooks // empty" "$HOOKS_FILE")
    if [ -z "$hooks" ] || [ "$hooks" = "null" ]; then
      echo "❌ $event[$i]: Missing 'hooks' array"
      ((error_count++))
      continue
    fi

    # Validate each hook in the array
    hook_array_count=$(jq -r "${JQ_PREFIX}.\"$event\"[$i].hooks | length" "$HOOKS_FILE")

    for ((j=0; j<hook_array_count; j++)); do
      hook_type=$(jq -r "${JQ_PREFIX}.\"$event\"[$i].hooks[$j].type // empty" "$HOOKS_FILE")

      if [ -z "$hook_type" ]; then
        echo "❌ $event[$i].hooks[$j]: Missing 'type' field"
        ((error_count++))
        continue
      fi

      if [ "$hook_type" != "command" ] && [ "$hook_type" != "prompt" ] && [ "$hook_type" != "agent" ]; then
        echo "❌ $event[$i].hooks[$j]: Invalid type '$hook_type' (must be 'command', 'prompt', or 'agent')"
        ((error_count++))
        continue
      fi

      # Check type-specific fields
      if [ "$hook_type" = "command" ]; then
        command=$(jq -r "${JQ_PREFIX}.\"$event\"[$i].hooks[$j].command // empty" "$HOOKS_FILE")
        if [ -z "$command" ]; then
          echo "❌ $event[$i].hooks[$j]: Command hooks must have 'command' field"
          ((error_count++))
        else
          # Check for hardcoded paths
          if [[ "$command" == /* ]] && [[ "$command" != *'${CLAUDE_PLUGIN_ROOT}'* ]]; then
            echo "⚠️  $event[$i].hooks[$j]: Hardcoded absolute path detected. Consider using \${CLAUDE_PLUGIN_ROOT}"
            ((warning_count++))
          fi
        fi
      elif [ "$hook_type" = "prompt" ] || [ "$hook_type" = "agent" ]; then
        prompt=$(jq -r "${JQ_PREFIX}.\"$event\"[$i].hooks[$j].prompt // empty" "$HOOKS_FILE")
        if [ -z "$prompt" ]; then
          echo "❌ $event[$i].hooks[$j]: ${hook_type^} hooks must have 'prompt' field"
          ((error_count++))
        fi

        # Check if prompt/agent hooks are used on supported events
        if [ "$event" != "Stop" ] && [ "$event" != "SubagentStop" ] && [ "$event" != "UserPromptSubmit" ] && [ "$event" != "PreToolUse" ]; then
          echo "⚠️  $event[$i].hooks[$j]: Prompt/agent hooks may not be fully supported on $event (best on Stop, SubagentStop, UserPromptSubmit, PreToolUse)"
          ((warning_count++))
        fi

        # Agent hooks should have model field
        if [ "$hook_type" = "agent" ]; then
          model=$(jq -r "${JQ_PREFIX}.\"$event\"[$i].hooks[$j].model // empty" "$HOOKS_FILE")
          if [ -z "$model" ]; then
            echo "⚠️  $event[$i].hooks[$j]: Agent hooks should specify 'model' field (e.g. haiku, sonnet)"
            ((warning_count++))
          fi
        fi
      fi

      # Check timeout
      timeout=$(jq -r "${JQ_PREFIX}.\"$event\"[$i].hooks[$j].timeout // empty" "$HOOKS_FILE")
      if [ -n "$timeout" ] && [ "$timeout" != "null" ]; then
        if ! [[ "$timeout" =~ ^[0-9]+$ ]]; then
          echo "❌ $event[$i].hooks[$j]: Timeout must be a number"
          ((error_count++))
        elif [ "$timeout" -gt 600 ]; then
          echo "⚠️  $event[$i].hooks[$j]: Timeout $timeout seconds is very high (max 600s)"
          ((warning_count++))
        elif [ "$timeout" -lt 5 ]; then
          echo "⚠️  $event[$i].hooks[$j]: Timeout $timeout seconds is very low"
          ((warning_count++))
        fi
      fi
    done
  done
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $error_count -eq 0 ] && [ $warning_count -eq 0 ]; then
  echo "✅ All checks passed!"
  exit 0
elif [ $error_count -eq 0 ]; then
  echo "⚠️  Validation passed with $warning_count warning(s)"
  exit 0
else
  echo "❌ Validation failed with $error_count error(s) and $warning_count warning(s)"
  exit 1
fi
