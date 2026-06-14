#!/usr/bin/env bash
#
# RLM Stop-Hook: Verhindert vorzeitiges Stoppen bis FINAL: gefunden wird.
#
# Features:
# - Blocks stop until "FINAL:" is written
# - Detects and reports partial results from interrupted sessions
# - Iteration counter to prevent infinite loops
#
# Dokumentationsquelle: docs/claude-code/en/hooks.md
# - Stop Event: Zeilen 397-399
# - Decision Control: Zeilen 917-929
# - stop_hook_active: Zeilen 659-672
#

set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

MAX_ITERATIONS=20
FINAL_MARKER="FINAL:"
STATE_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude/rlm_state"
ITERATION_FILE="${STATE_DIR}/iteration_count.txt"
PARTIAL_RESULTS_FILE=""

# ═══════════════════════════════════════════════════════════════════════════
# READ HOOK INPUT
# ═══════════════════════════════════════════════════════════════════════════

# Hook input comes via stdin as JSON
HOOK_INPUT=$(cat)

TRANSCRIPT_PATH=$(echo "$HOOK_INPUT" | jq -r '.transcript_path // empty')
STOP_HOOK_ACTIVE=$(echo "$HOOK_INPUT" | jq -r '.stop_hook_active // false')

# ═══════════════════════════════════════════════════════════════════════════
# SAFETY: PREVENT INFINITE LOOPS
# ═══════════════════════════════════════════════════════════════════════════

if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
    if [ -n "$TRANSCRIPT_PATH" ] && [ -f "$TRANSCRIPT_PATH" ]; then
        if grep -q "$FINAL_MARKER" "$TRANSCRIPT_PATH" 2>/dev/null; then
            exit 0
        fi
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════
# CHECK FOR PARTIAL RESULTS
# ═══════════════════════════════════════════════════════════════════════════

find_partial_results() {
    # Look for partial_results.json in any session directory
    local latest_partial=""
    local latest_time=0

    if [ -d "$STATE_DIR" ]; then
        for session_dir in "$STATE_DIR"/session_*/; do
            if [ -d "$session_dir" ]; then
                local partial_file="${session_dir}partial_results.json"
                if [ -f "$partial_file" ]; then
                    local file_time
                    file_time=$(stat -c %Y "$partial_file" 2>/dev/null || stat -f %m "$partial_file" 2>/dev/null || echo "0")
                    if [ "$file_time" -gt "$latest_time" ]; then
                        latest_time=$file_time
                        latest_partial=$partial_file
                    fi
                fi
            fi
        done
    fi

    echo "$latest_partial"
}

PARTIAL_RESULTS_FILE=$(find_partial_results)
PARTIAL_INFO=""

if [ -n "$PARTIAL_RESULTS_FILE" ] && [ -f "$PARTIAL_RESULTS_FILE" ]; then
    COMPLETED=$(jq -r '.completed_findings // 0' "$PARTIAL_RESULTS_FILE" 2>/dev/null || echo "0")
    TOTAL=$(jq -r '.total_chunks // 0' "$PARTIAL_RESULTS_FILE" 2>/dev/null || echo "0")
    SESSION_ID=$(jq -r '.session_id // "unknown"' "$PARTIAL_RESULTS_FILE" 2>/dev/null || echo "unknown")

    if [ "$COMPLETED" -gt 0 ]; then
        PARTIAL_INFO="
NOTE: Found partial results from interrupted session:
  - Session: $SESSION_ID
  - Completed findings: $COMPLETED
  - Total chunks: $TOTAL
  - File: $PARTIAL_RESULTS_FILE

Consider resuming from partial results or starting fresh."
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════
# CHECK FOR FINAL MARKER
# ═══════════════════════════════════════════════════════════════════════════

if [ -n "$TRANSCRIPT_PATH" ] && [ -f "$TRANSCRIPT_PATH" ]; then
    if grep -q "$FINAL_MARKER" "$TRANSCRIPT_PATH" 2>/dev/null; then
        rm -f "$ITERATION_FILE" 2>/dev/null || true
        # Clean up partial results on successful completion
        if [ -n "$PARTIAL_RESULTS_FILE" ] && [ -f "$PARTIAL_RESULTS_FILE" ]; then
            rm -f "$PARTIAL_RESULTS_FILE" 2>/dev/null || true
        fi
        exit 0
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════
# ITERATION COUNTER
# ═══════════════════════════════════════════════════════════════════════════

mkdir -p "$STATE_DIR"

ITERATION=0
if [ -f "$ITERATION_FILE" ]; then
    ITERATION=$(cat "$ITERATION_FILE" 2>/dev/null || echo "0")
    if ! [[ "$ITERATION" =~ ^[0-9]+$ ]]; then
        ITERATION=0
    fi
fi

if [ "$ITERATION" -ge "$MAX_ITERATIONS" ]; then
    echo "RLM: Max iterations ($MAX_ITERATIONS) reached. Allowing stop." >&2
    rm -f "$ITERATION_FILE" 2>/dev/null || true
    exit 0
fi

ITERATION=$((ITERATION + 1))
echo "$ITERATION" > "$ITERATION_FILE"

# ═══════════════════════════════════════════════════════════════════════════
# BLOCK STOP AND PROVIDE CONTINUATION PROMPT
# ═══════════════════════════════════════════════════════════════════════════

# Build the reason message with optional partial results info
REASON="RLM workflow not complete (iteration $ITERATION/$MAX_ITERATIONS). Continue the analysis:

1. If you have gathered enough evidence, synthesize and write: FINAL: [your answer]
2. If more chunks need analysis, continue with the subcall loop
3. If you're stuck, explain what's blocking progress
${PARTIAL_INFO}
Remember: The Stop-Hook will only allow termination when you write FINAL:"

jq -n \
    --arg iteration "$ITERATION" \
    --arg max "$MAX_ITERATIONS" \
    --arg reason "$REASON" \
    '{
        "decision": "block",
        "reason": $reason
    }'
