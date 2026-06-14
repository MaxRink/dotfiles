---
name: ai4dev-migration-plugin-plan-migration
description: Interactive migration planning through docs-backed ADR review or adaptive interview. Use when user wants to "plan a migration", "create migration plan", "define migration scope", or "start planning".
argument-hint: "[feature-name]"
user-invocable: true
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/migration-plugin/skills/plan-migration by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Plan Migration

Route to the correct planning workflow based on documentation availability.

Feature name: use `$ARGUMENTS` if provided; otherwise use the active feature from hook-injected context.

This is an interactive interview — you need direct access to the user via AskUserQuestion. Do NOT delegate to a sub-agent.

## Routing Logic

1. Check whether `.migration/docs/index.json` exists and is valid JSON.
2. Route based on result:

   | Condition | Action |
   |-----------|--------|
   | `index.json` exists and is valid | Read `skills/plan-migration/references/adr-workflow.md` and follow it — docs-backed ADR mode |
   | `index.json` missing or unreadable | Read `skills/plan-migration/references/interview-workflow.md` and follow it — interview-only mode |

3. Pass through the feature name from `$ARGUMENTS` to the selected workflow.

## Constraints

- Do not delegate to a sub-agent. Both planning workflows are interactive and require direct access to the user via AskUserQuestion.
- Do not write files until the workflow instructs you to. Only select and read the appropriate workflow reference.
- Treat `.migration/docs/index.json` as the deep-explore index artifact. If a prompt or diagram says `index.js`, interpret that as `index.json`.
