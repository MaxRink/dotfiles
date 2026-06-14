---
name: ai4dev-migration-plugin-validation
description: Validates generated code against the legacy application with business-logic validation, code-review and architecture validation. Requires plan.json, analysis.json, target-architecture.md, functional-requirements.md, and generated code.
user-invocable: true
disable-model-invocation: true
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/migration-plugin/skills/validation by codex-knowledge-curation/scripts/persist_project_skills.py. -->

## Workflow

1. Read `skills/validation/references/orchestrator-workflow.md` and follow it. Feature: $ARGUMENTS
Wait for completion before moving to the next step.

2. Load the `one-modernizer:code-review` skill via the Skill tool and execute it. Feature: $ARGUMENTS
Wait for completion before moving to the next step.

3. Load the `one-modernizer:architecture-validation` skill via the Skill tool and execute it. Feature: $ARGUMENTS
