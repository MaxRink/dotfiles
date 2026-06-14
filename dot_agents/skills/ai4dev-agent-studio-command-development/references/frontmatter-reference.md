# Command Frontmatter Reference

Complete reference for command YAML frontmatter fields, with patterns and examples for every field and common use case.

## Basic Example

A minimal command requires only a `description` to be discoverable:

```markdown
---
description: Show project status
---

Analyze the current project state:
1. Check git status for uncommitted changes
2. Review recent commits with git log
3. Identify any failing tests
4. Summarize open TODOs in the codebase

Provide a concise status report.
```

This is sufficient for simple commands that need access to all tools and take no arguments.

## Standard Example

A typical command includes `description`, `allowed-tools`, and `argument-hint`:

```markdown
---
description: Review code in a pull request
argument-hint: [pr-number]
allowed-tools: Read, Grep, Glob, Bash(gh:*)
---

Review pull request #$1.

Steps:
1. Fetch PR details: run `gh pr view $1 --json title,body,files`
2. Read each changed file
3. Analyze for:
   - Code quality issues
   - Potential bugs or edge cases
   - Style consistency
   - Missing tests
4. Provide structured feedback with file-specific comments

Format the review as a markdown report with severity levels (critical, warning, suggestion).
```

This pattern restricts tools to read-only access plus GitHub CLI, accepts a PR number as input, and provides Claude with structured review instructions.

## Complex Example

A deployment command combining multiple frontmatter fields:

```markdown
---
description: Deploy application to environment
argument-hint: [app-name] [environment] [version]
allowed-tools: Bash(kubectl:*), Bash(helm:*), Read
model: sonnet
---

Deploy $1 to $2 environment at version $3.

Pre-deployment checks:
1. Verify the target environment ($2) is one of: staging, production, canary
2. Confirm the version ($3) exists in the container registry
3. Check current deployment status with `kubectl get deployment $1 -n $2`

Deployment steps:
1. Run `helm upgrade $1 ./charts/$1 --namespace $2 --set image.tag=$3`
2. Wait for rollout: `kubectl rollout status deployment/$1 -n $2`
3. Verify pod health: `kubectl get pods -n $2 -l app=$1`

Post-deployment:
1. Run smoke tests against the $2 endpoint
2. Report deployment status and pod health

If any step fails, immediately report the error and do NOT proceed to the next step.
```

This example restricts tool access to only Kubernetes and Helm commands plus file reading, uses the `sonnet` model for cost efficiency, and handles three positional arguments.

## Field Reference

### description

**Type:** string
**Default:** none
**Recommended:** yes

Brief text shown in the `/` command menu and help output. Without a description, the command still works but is harder for users to discover.

```yaml
description: Review code in a pull request
```

```yaml
description: Deploy application to target environment
```

```yaml
description: Generate test coverage report
```

Keep descriptions concise (under 80 characters) and action-oriented. Start with a verb.

### allowed-tools

**Type:** string (comma-separated)
**Default:** all tools available

Restrict which tools Claude can use when executing this command. Supports exact tool names and pattern-based restrictions.

**Simple tool list:**

```yaml
allowed-tools: Read, Write, Grep
```

**With command patterns:**

```yaml
allowed-tools: Bash(kubectl:*), Bash(helm:*), Read
```

**Pattern syntax:**

| Pattern | Meaning |
|---------|---------|
| `Read` | Allow the Read tool (no restrictions) |
| `Bash(git:*)` | Allow Bash only for commands starting with `git` |
| `Bash(kubectl:*)` | Allow Bash only for commands starting with `kubectl` |
| `Bash(gh:*)` | Allow Bash only for commands starting with `gh` |

Combining patterns restricts Bash to only the specified command prefixes while allowing other tools without restriction:

```yaml
allowed-tools: Read, Grep, Glob, Bash(git:*), Bash(npm:*)
```

This allows Read, Grep, and Glob unrestricted, and Bash only for `git` and `npm` commands.

**Best practice:** Follow the principle of least privilege. Grant only the tools the
command actually needs. For example, a code review command does not need Write
access, and a deployment command does not need Edit access.

### model

**Type:** string
**Default:** current session model
**Options:** `sonnet`, `opus`, `haiku`

Override the model used for this command:

```yaml
model: sonnet
```

- `sonnet` - Balanced capability and speed. Good for most commands
- `opus` - Most capable. Use for complex analysis or generation tasks
- `haiku` - Fastest and cheapest. Use for simple lookups or formatting

Omit this field to inherit the model from the current session.

### argument-hint

**Type:** string
**Default:** none

Display hint during autocomplete to show the user what arguments the command expects:

```yaml
argument-hint: [pr-number]
```

```yaml
argument-hint: [app-name] [environment] [version]
```

```yaml
argument-hint: [filename] [--verbose]
```

The hint is purely informational. It does not enforce argument count or format. Validation of arguments should happen in the prompt body.

### disable-model-invocation

**Type:** boolean
**Default:** `false`

Prevent Claude from automatically invoking this command based on context. When set to `true`, the command can only be run by a user explicitly typing `/command-name`.

```yaml
disable-model-invocation: true
```

**Use for:**

- Destructive operations (deployments, deletions, data mutations)
- Sensitive workflows (credential rotation, access management)
- Interactive wizards that require explicit user intent
- Commands with side effects outside the development environment

### user-invocable

**Type:** boolean
**Default:** `true`

Control whether the command appears in the `/` menu. Set to `false` for commands intended only for background or programmatic use.

```yaml
user-invocable: false
```

A non-user-invocable command can still be triggered by other commands or agents but will not appear in the autocomplete menu.

### context

**Type:** string
**Options:** `fork`

Set to `fork` to run the command in a forked subagent context, isolated from the main conversation:

```yaml
context: fork
```

When forked, the command runs in a separate context that does not affect the
main conversation's state. This is useful for long-running or exploratory tasks
that should not pollute the primary context.

### agent

**Type:** string

Specify which subagent type to use when `context: fork` is set:

```yaml
context: fork
agent: security-auditor
```

The agent value references a defined agent (from the `agents/` directory). This combines the command's prompt with the agent's system prompt and configuration.

### hooks

**Type:** object

Lifecycle hooks scoped to this command. Same format as settings-based hooks, but only fire when this command is running:

```yaml
hooks:
  Stop:
    - matcher: "*"
      hooks:
        - type: prompt
          prompt: "Verify all steps completed successfully before stopping"
```

Hook events available: `PreToolUse`, `PostToolUse`, `Stop`, and other standard hook lifecycle events.

## Command Patterns

### Pattern: Interactive Workflow

Force manual invocation for a setup wizard:

```markdown
---
description: Walk through setup wizard
disable-model-invocation: true
---

Guide the user through initial project setup:

1. Ask which framework to use (React, Vue, Svelte)
2. Ask for the project name
3. Confirm the selected options
4. Scaffold the project structure
5. Install dependencies
6. Run initial build to verify setup

At each step, wait for user confirmation before proceeding.
```

Setting `disable-model-invocation: true` ensures Claude never auto-triggers this
command from context. The user must explicitly type `/setup-wizard` to run it.
This is appropriate because the wizard requires interactive input at each step
and should not be triggered accidentally.

### Pattern: Read-Only Analysis

Restrict tools to prevent any modifications:

```markdown
---
description: Analyze codebase architecture
allowed-tools: Read, Grep, Glob
---

Perform a comprehensive architecture analysis:

1. Identify the project structure and key directories
2. Map module dependencies
3. Identify design patterns in use
4. Find potential architectural concerns:
   - Circular dependencies
   - Overly coupled modules
   - Missing abstraction layers
5. Generate an architecture diagram description

Output a structured report with findings and recommendations.
```

By restricting to `Read`, `Grep`, and `Glob`, this command cannot modify files,
execute shell commands, or make network requests. This configuration is safe to
run on any codebase without risk of side effects.

### Pattern: Forked Context

Run a security audit in isolation from the main conversation:

```markdown
---
description: Run security audit in isolated context
context: fork
agent: security-auditor
allowed-tools: Read, Grep, Glob, Bash
---

Perform a security audit of the current project:

1. Scan for hardcoded secrets and credentials
2. Check dependency vulnerabilities
3. Review authentication and authorization patterns
4. Analyze input validation and sanitization
5. Check for common security anti-patterns

Generate a security report with severity ratings.
```

The `context: fork` setting runs this command in a forked subagent, isolated from
the main conversation. The `agent: security-auditor` setting loads the
security-auditor agent's system prompt and configuration, combining it with the
command's instructions. This prevents potentially lengthy audit output from
cluttering the main conversation context.

### Pattern: Command with Lifecycle Hooks

Attach hooks to validate completion:

```markdown
---
description: Process data pipeline
hooks:
  Stop:
    - matcher: "*"
      hooks:
        - type: prompt
          prompt: "Verify all pipeline stages completed successfully. Check that input was validated, transformation applied, and output written. If any stage was skipped, block the stop and complete the missing stage."
---

Process the data pipeline:

1. Read input data from $1
2. Validate data format and schema
3. Apply transformation rules
4. Write output to the target location
5. Generate processing summary

Report the number of records processed and any validation failures.
```

The `Stop` hook fires when Claude attempts to finish, verifying all pipeline stages completed. If a stage was skipped, the hook blocks the stop and instructs Claude to complete the missing work.

### Pattern: Background Command

Create a command not shown in the `/` menu:

```markdown
---
description: Internal validation step
user-invocable: false
allowed-tools: Read, Grep
---

Validate the current file structure against the expected schema.
Report any discrepancies.
```

Setting `user-invocable: false` hides this command from the autocomplete menu. It can still be invoked programmatically by other commands or agents that reference it.

## allowed-tools Pattern Syntax

### Simple Tool Names

List tools by exact name, comma-separated:

```yaml
allowed-tools: Read, Write, Grep
```

Available tool names include: `Read`, `Write`, `Edit`, `Grep`, `Glob`, `Bash`, `Skill`, `WebFetch`, `NotebookEdit`.

### Bash Command Patterns

Restrict Bash to specific command prefixes using the `Bash(prefix:*)` pattern:

```yaml
allowed-tools: Bash(git:*)
```

This allows Bash to execute only commands starting with `git`. Any other Bash command is blocked.

**Multiple patterns:**

```yaml
allowed-tools: Bash(kubectl:*), Bash(helm:*), Bash(docker:*)
```

This allows Bash for `kubectl`, `helm`, and `docker` commands only.

**Combined with unrestricted tools:**

```yaml
allowed-tools: Read, Grep, Glob, Bash(git:*), Bash(npm:*)
```

Read, Grep, and Glob are unrestricted. Bash is limited to `git` and `npm` commands.

### Common allowed-tools Configurations

| Use Case | Configuration |
|----------|--------------|
| Read-only analysis | `Read, Grep, Glob` |
| Code review | `Read, Grep, Glob, Bash(gh:*)` |
| Git operations | `Read, Write, Bash(git:*)` |
| Kubernetes management | `Read, Bash(kubectl:*), Bash(helm:*)` |
| Full file access | `Read, Write, Edit, Grep, Glob` |
| Testing | `Read, Grep, Bash(npm:*), Bash(pytest:*)` |

## Argument Handling

### How Arguments Flow

When a user types `/command-name arg1 arg2 "arg three"`, the arguments become available in the prompt body through variable substitution:

| Variable | Value | Description |
|----------|-------|-------------|
| `$ARGUMENTS` | `arg1 arg2 "arg three"` | Full raw argument string |
| `$1` | `arg1` | First positional argument |
| `$2` | `arg2` | Second positional argument |
| `$3` | `arg three` | Third positional argument (quotes stripped) |

### Example: Single Argument

```markdown
---
description: Look up documentation for a module
argument-hint: [module-name]
---

Find and summarize the documentation for the "$1" module:

1. Search for files related to $1 using Grep and Glob
2. Read the primary documentation file
3. Summarize the module's purpose, API, and usage examples

If no documentation is found for "$1", check for README files or inline comments in the module source.
```

### Example: Multiple Arguments

```markdown
---
description: Compare two branches
argument-hint: [base-branch] [feature-branch]
---

Compare branch $1 with branch $2:

1. Run `git diff $1...$2 --stat` for an overview of changes
2. Run `git log $1..$2 --oneline` for commit history
3. Identify the key changes between the branches
4. Highlight any potential merge conflicts

Provide a summary suitable for a code review.
```

### Example: Full Argument String

```markdown
---
description: Search the codebase with a custom query
argument-hint: [search-query]
---

Search the codebase for: $ARGUMENTS

1. Use Grep to find all occurrences of the search term
2. Group results by file and directory
3. Provide context for each match (surrounding lines)
4. Summarize the search results with match counts per file

Use `$ARGUMENTS` as the literal search pattern. Do not modify or interpret it.
```

### Validating Arguments in Prompts

Since frontmatter does not enforce argument requirements, validate within the prompt:

```markdown
---
description: Deploy to environment
argument-hint: [environment] [version]
---

Deploy to environment $1 at version $2.

First, validate the inputs:
- If $1 is empty, ask the user which environment to deploy to (staging, production)
- If $2 is empty, ask the user which version to deploy
- If $1 is not one of "staging" or "production", inform the user of valid options

Proceed only after both arguments are confirmed valid.
```

## Combining Fields

### Full-Featured Command

An example combining most frontmatter fields:

```markdown
---
description: Deploy and verify application release
argument-hint: [app] [env] [version]
allowed-tools: Read, Bash(kubectl:*), Bash(helm:*), Bash(curl:*)
model: sonnet
disable-model-invocation: true
hooks:
  Stop:
    - matcher: "*"
      hooks:
        - type: prompt
          prompt: "Confirm deployment health checks passed before completing"
---

Deploy $1 to $2 at version $3.

Pre-flight:
1. Validate environment $2 is one of: staging, canary, production
2. Verify version $3 exists in registry
3. Check current deployment health

Deploy:
1. Run helm upgrade with appropriate values
2. Monitor rollout status
3. Execute health checks

Post-deploy:
1. Verify endpoint responds correctly
2. Check error rates for 2 minutes
3. Report final deployment status

If any step fails, halt immediately and report the failure.
```

This command:

- Appears in the `/` menu with a clear description
- Shows expected arguments during autocomplete
- Limits tools to read access and specific CLI commands
- Uses `sonnet` for cost efficiency
- Requires explicit `/command` invocation (no auto-trigger)
- Validates completion through a Stop hook
