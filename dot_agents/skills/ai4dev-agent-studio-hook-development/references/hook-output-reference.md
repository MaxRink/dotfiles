# Hook Output Reference

Complete output schemas for all hook event types, plus lifecycle and debugging guidance.

## Universal Output Fields

All hook types can return these fields:

```json
{
  "continue": true,
  "stopReason": "Explanation when continue is false",
  "suppressOutput": false,
  "systemMessage": "Message added to Claude's context"
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `continue` | boolean | `true` | If false, halt hook processing chain |
| `stopReason` | string | `""` | Explanation when setting continue to false |
| `suppressOutput` | boolean | `false` | Hide hook output from transcript |
| `systemMessage` | string | `""` | Message injected into Claude's context |

## Event-Specific Output Schemas

### PreToolUse Output

```json
{
  "continue": true,
  "suppressOutput": false,
  "systemMessage": "Context about this tool use",
  "hookSpecificOutput": {
    "permissionDecision": "allow|deny|ask",
    "updatedInput": {
      "field_name": "modified_value"
    },
    "additionalContext": "Extra information for Claude"
  }
}
```

| Field | Description |
|-------|-------------|
| `permissionDecision` | `"allow"` (proceed), `"deny"` (block), `"ask"` (prompt user) |
| `updatedInput` | Modified tool input fields (partial update, merged with original) |
| `additionalContext` | Additional context string provided to Claude |

### PostToolUse Output

```json
{
  "continue": true,
  "suppressOutput": false,
  "systemMessage": "Feedback about tool result",
  "decision": "approve|block",
  "reason": "Explanation for decision"
}
```

### PostToolUseFailure Output

Same schema as PostToolUse. Fires specifically when a tool call fails.

### Stop / SubagentStop Output

```json
{
  "continue": true,
  "suppressOutput": false,
  "systemMessage": "Additional context",
  "decision": "approve|block",
  "reason": "Explanation for approval or blocking"
}
```

| Field | Description |
|-------|-------------|
| `decision` | `"approve"` (allow stop) or `"block"` (continue working) |
| `reason` | Explanation shown to Claude for the decision |

### UserPromptSubmit Output

```json
{
  "continue": true,
  "suppressOutput": false,
  "systemMessage": "Context to add to this prompt",
  "decision": "approve|block",
  "reason": "Why the prompt was blocked"
}
```

### PermissionRequest Output

```json
{
  "continue": true,
  "suppressOutput": false,
  "systemMessage": "Context about permission",
  "hookSpecificOutput": {
    "decision": {
      "behavior": "allow|deny|ask"
    },
    "updatedInput": {
      "field": "modified_value"
    },
    "message": "Reason for the permission decision",
    "interrupt": false
  }
}
```

| Field | Description |
|-------|-------------|
| `decision.behavior` | `"allow"` (auto-approve), `"deny"` (auto-deny), `"ask"` (show dialog) |
| `updatedInput` | Modified parameters for the permission request |
| `message` | Human-readable explanation of the decision |
| `interrupt` | If true, interrupt current operation |

### SubagentStart Output

```json
{
  "continue": true,
  "suppressOutput": false,
  "systemMessage": "Context for subagent startup"
}
```

### SessionStart / SessionEnd / PreCompact / Notification Output

These events use only the universal output fields.

## Temporarily Active Hooks

Create hooks that activate conditionally by checking for a flag file or configuration:

**Pattern: Flag file activation**

```bash
#!/bin/bash
# Only active when flag file exists
FLAG_FILE="$CLAUDE_PROJECT_DIR/.enable-strict-validation"

if [ ! -f "$FLAG_FILE" ]; then
  # Flag not present, skip validation
  exit 0
fi

# Flag present, run validation
input=$(cat)
# ... validation logic ...
```

**Pattern: Configuration-based activation**

```bash
#!/bin/bash
# Check configuration for activation
CONFIG_FILE="$CLAUDE_PROJECT_DIR/.claude/plugin-config.json"

if [ -f "$CONFIG_FILE" ]; then
  enabled=$(jq -r '.strictMode // false' "$CONFIG_FILE")
  if [ "$enabled" != "true" ]; then
    exit 0  # Not enabled, skip
  fi
fi

# Enabled, run hook logic
input=$(cat)
# ... hook logic ...
```

**Use cases:**

- Enable strict validation only when needed
- Temporary debugging hooks
- Project-specific hook behavior
- Feature flags for hooks

**Best practice:** Document activation mechanism in plugin README so users know how to enable/disable temporary hooks.

## Hook Lifecycle and Limitations

### Hooks Load at Session Start

**Important:** Hooks are loaded when Claude Code session starts. Changes to hook configuration require restarting Claude Code.

**Cannot hot-swap hooks:**

- Editing `hooks/hooks.json` won't affect current session
- Adding new hook scripts won't be recognized
- Changing hook commands/prompts won't update
- Must restart Claude Code: exit and run `claude` again

**To test hook changes:**

1. Edit hook configuration or scripts
2. Exit Claude Code session
3. Restart: `claude` or `cc`
4. New hook configuration loads
5. Test hooks with `claude --debug`

### Hook Validation at Startup

Hooks are validated when Claude Code starts:

- Invalid JSON in hooks.json causes loading failure
- Missing scripts cause warnings
- Syntax errors reported in debug mode

Use `/hooks` command to review loaded hooks in current session.

## Debugging Hooks

### Enable Debug Mode

```bash
claude --debug
```

Look for hook registration, execution logs, input/output JSON, and timing information.

### Test Hook Scripts

Test command hooks directly:

```bash
echo '{"tool_name": "Write", "tool_input": {"file_path": "/test"}}' | \
  bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh

echo "Exit code: $?"
```

### Validate JSON Output

Ensure hooks output valid JSON:

```bash
output=$(./your-hook.sh < test-input.json)
echo "$output" | jq .
```

### Common Issues

- **Hook not firing**: Check matcher pattern, verify event name spelling
- **Hook timing out**: Increase timeout or optimize script
- **Invalid JSON output**: Validate with `jq` before deploying
- **Environment variables missing**: Check `${CLAUDE_PLUGIN_ROOT}` is set
- **Permission denied**: Ensure scripts are executable (`chmod +x`)
