---
name: ai4dev-agent-studio-command-development
description: This skill provides guidance for creating and improving slash commands, frontmatter, prompts, argument handling, and allowed-tools in Claude Code plugins.
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/agent-studio/skills/command-development by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Command Development for Claude Code Plugins

## Overview

Commands are user-initiated slash commands in Claude Code that trigger specific
workflows when a user types `/command-name`. They provide a direct, repeatable
interface for common tasks such as code review, deployment, testing, and
project management. Unlike skills (auto-triggered knowledge loaded by
description matching) and agents (autonomous subprocesses that handle complex
multi-step tasks independently), commands are explicit, user-invoked actions
that execute a predefined prompt with optional tool restrictions and argument
handling.

Each command is a markdown file consisting of YAML frontmatter (metadata)
followed by a prompt body (instructions for Claude). The frontmatter controls
behavior such as tool access, model selection, argument hints, and
discoverability. The prompt body defines what Claude should do when the command
runs; write it as imperative instructions.

**Key distinctions:**

- **Commands** - User-initiated via `/name`, explicit invocation, prompt-driven, scoped tool access
- **Skills** - Auto-triggered by description matching, knowledge-driven, always-available context
- **Agents** - Autonomous subprocesses, system-prompt-driven, run in isolated forked contexts

Commands are the primary way to package repeatable workflows in a plugin.
A well-designed command accepts arguments, restricts tools to the minimum
required, and provides Claude with clear, step-by-step instructions to
complete the task.

## Command File Structure

### Complete Format

A command file uses YAML frontmatter between `---` markers, followed by the markdown prompt body:

```markdown
---
description: Brief description of what this command does
allowed-tools: Read, Write, Grep
argument-hint: [filename] [options]
---

Prompt content that instructs Claude what to do when this command is invoked.

Use $ARGUMENTS to access the full argument string.
Use $1, $2, $3 for positional arguments.
```

### Minimal Example

```markdown
---
description: Show project status
---

Analyze the current project and provide a summary of:
1. Recent changes (check git log)
2. Open issues or TODOs
3. Build/test status
```

## Frontmatter Fields

All frontmatter fields are optional. Only `description` is recommended for
discoverability. For detailed documentation of each field with examples and
patterns, see `references/frontmatter-reference.md`.

| Field | Type | Description |
|-------|------|-------------|
| `description` | string | Brief description shown in the `/` menu and help text. Recommended for discoverability |
| `allowed-tools` | string | Comma-separated list of tools Claude can use. Supports patterns like `Bash(kubectl:*)` |
| `model` | string | Model to use for this command: `sonnet`, `opus`, `haiku` |
| `argument-hint` | string | Hint shown during autocomplete. Example: `[pr-number] [priority]` |
| `disable-model-invocation` | boolean | Prevent Claude from auto-invoking this command. Default: `false` |
| `user-invocable` | boolean | Show command in the `/` menu. Set to `false` for background-only commands. Default: `true` |
| `context` | string | Set to `fork` to run the command in a forked subagent context |
| `agent` | string | Which subagent type to use when `context: fork` is set |
| `hooks` | object | Hooks scoped to this command's lifecycle. Same format as settings-based hooks |

The most commonly used fields are `description`, `allowed-tools`, and
`argument-hint`. The remaining fields serve advanced use cases such as model
overrides, forked execution, and lifecycle hooks.

## Writing Command Prompts

### Commands Are Instructions for Claude

Command prompts are instructions FOR Claude, not user-facing documentation.
Write them as clear directives that tell Claude what to do, what to check, and
what to output. The user never sees the raw prompt content. Think of the
prompt as an internal playbook: it should contain specific steps, validation
criteria, expected outputs, and error-handling guidance. Avoid writing
conversational or explanatory text aimed at a human reader.

### Argument Handling

Access user-provided arguments within the prompt body:

- **`$ARGUMENTS`** - Contains the full raw argument string typed after the command name
- **`$1`** - First positional argument
- **`$2`** - Second positional argument
- **`$3`** - Third positional argument

Example prompt using arguments:

```markdown
---
description: Review a pull request
argument-hint: [pr-number]
allowed-tools: Read, Grep, Glob, Bash(gh:*)
---

Review pull request #$1.

1. Fetch the PR details using `gh pr view $1`
2. Read the changed files
3. Analyze code quality, potential bugs, and style issues
4. Provide a structured review with actionable feedback
```

### Embedded Commands

Execute shell commands during prompt rendering using the `!` backtick syntax.
These run at render time, before Claude processes the prompt, injecting
their output directly into the prompt text. This is useful for providing
Claude with live context such as current system state, environment
variables, or configuration values:

```markdown
---
description: Analyze current cluster state
allowed-tools: Bash(kubectl:*)
---

Current cluster info:
!`kubectl cluster-info`

Current pods:
!`kubectl get pods --all-namespaces`

Analyze the cluster state above and report any issues.
```

Embedded commands execute unconditionally at render time. Avoid embedding commands with side effects or long execution times, as they run every time the command is invoked.

### Loading Skills from Commands

Commands can load skills using the Skill tool to access specialized knowledge
during execution. This is useful when a command needs domain-specific
guidance that already exists in a skill. Include `Skill` in the
`allowed-tools` list and reference the skill by name within the prompt
instructions:

```markdown
---
description: Create a new hook for the plugin
allowed-tools: Read, Write, Grep, Glob, Skill
---

Use the Skill tool to load the "hook-development" skill, then follow its guidance to create a new hook based on $ARGUMENTS.
```

This pattern avoids duplicating knowledge between commands and skills. The command handles the user interaction and argument parsing, while the skill provides the domain expertise.

### Structuring Prompts

Organize command prompts with clear steps, success criteria, and output expectations:

1. **State the objective** - What the command accomplishes in one sentence
2. **Define steps** - Numbered, sequential instructions Claude must follow
3. **Specify success criteria** - How to determine the task completed correctly
4. **Set output format** - What Claude should report back to the user
5. **Handle errors** - What to do when a step fails or input is invalid

A well-structured prompt prevents Claude from improvising and ensures
consistent, predictable behavior across invocations. Include explicit
guardrails: what to do, what NOT to do, and when to stop and ask the user for
clarification.

## Naming Conventions

### File Naming

- Use kebab-case `.md` files in the `commands/` directory
- The filename becomes the command name: `review-pr.md` maps to `/review-pr`
- Keep names short, descriptive, and action-oriented
- Prefer verb-noun patterns: `review-pr`, `deploy-app`, `run-tests`, `check-status`
- Avoid generic names like `do-thing.md` or `helper.md` that do not convey purpose

### Plugin Namespacing

Commands are namespaced by plugin name for disambiguation:

- Within the plugin: `/command-name`
- Fully qualified: `/plugin-name:command-name`

This prevents conflicts when multiple plugins define commands with similar names.

### Directory Structure

```text
plugin-name/
├── commands/
│   ├── review-pr.md        → /review-pr
│   ├── deploy.md           → /deploy
│   ├── run-tests.md        → /run-tests
│   └── setup-env.md        → /setup-env
```

## Auto-Discovery

All `.md` files in the `commands/` directory are loaded automatically by
Claude Code. No registration or configuration is required beyond placing the
file in the correct directory. Claude Code scans the directory at startup and
registers each file as a slash command.

Custom command paths defined in `plugin.json` supplement the defaults,
allowing commands to reside in additional directories when needed. However,
the `commands/` directory remains the standard, expected location for
command files. Place all commands there unless there is a specific reason to
organize them differently.

To verify a command is discoverable after creation, start Claude Code with
the plugin loaded and type `/` followed by the command name. The command
should appear in the autocomplete list with its description.

## Best Practices

### DO

- Include a clear `description` for discoverability in the `/` menu
- Use `argument-hint` to show expected arguments during autocomplete
- Restrict `allowed-tools` to the minimum set needed for the task
- Write instructions as imperative steps for Claude to follow
- Use `$ARGUMENTS` and positional args (`$1`, `$2`, `$3`) for user input
- Set `disable-model-invocation: true` for sensitive or destructive operations
- Reference relevant skills from within commands using the Skill tool

### DON'T

- Write user-facing documentation as the prompt body (the prompt is FOR Claude, not the user)
- Grant all tools when only a few are needed (follow principle of least privilege)
- Use hardcoded absolute paths; prefer `${CLAUDE_PLUGIN_ROOT}` for portability across environments
- Skip the `description` field (commands without it are harder to discover in the `/` menu)
- Make commands overly complex; split large workflows into multiple focused commands
- Assume arguments are always present; validate and handle missing arguments gracefully in the prompt

## Quick Reference

| Aspect | Details |
|--------|---------|
| File location | `commands/command-name.md` |
| Invocation | `/command-name` or `/plugin:command-name` |
| Format | YAML frontmatter + markdown prompt body |
| Required fields | None (all optional); `description` strongly recommended |
| Arguments | `$ARGUMENTS` (full string), `$1`, `$2`, `$3` (positional) |
| Tool restriction | `allowed-tools: Tool1, Tool2, Bash(cmd:*)` |
| Embedded commands | `!` backtick syntax for render-time shell execution |
| Auto-discovery | All `.md` files in `commands/` loaded automatically |
| Naming | Kebab-case filenames, verb-noun action-oriented names |
| Model override | `model: sonnet`, `opus`, or `haiku` |
| Sensitive commands | Set `disable-model-invocation: true` to require manual invocation |
| Forked execution | Set `context: fork` with optional `agent` for isolated runs |

## Command Creation Workflow

To create a new command for a plugin:

1. **Identify the task** - Determine what repeatable workflow the command should automate
2. **Choose a name** - Pick a kebab-case, action-oriented name (e.g., `review-pr`, `deploy`, `run-tests`)
3. **Define frontmatter** - Set `description`, `allowed-tools`, and `argument-hint` at minimum
4. **Write the prompt** - Create imperative, step-by-step instructions for Claude
5. **Restrict tools** - Grant only the tools the command needs (principle of least privilege)
6. **Test the command** - Load the plugin and invoke the command with various arguments
7. **Iterate** - Refine the prompt based on how Claude performs the task

For sensitive or destructive commands (deployments, deletions), always set `disable-model-invocation: true` to prevent accidental auto-invocation.

## Additional Resources

### Reference Files

For detailed frontmatter field documentation, patterns, and advanced examples, consult:

- **`references/frontmatter-reference.md`** - Complete frontmatter field reference with patterns, examples, and argument handling details
