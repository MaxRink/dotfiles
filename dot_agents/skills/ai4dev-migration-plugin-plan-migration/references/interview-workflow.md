# Plan Migration User Interview

Conduct the adaptive migration planning interview when deep-explore documentation is not available.

The orchestrator routes here when `.migration/docs/index.json` is missing, unreadable, or invalid.

Produces `.migration/<feature-name>/plan/plan.json`.

Feature name: use `$ARGUMENTS` if provided; otherwise use the active feature from hook-injected context. If neither is available, ask for a short feature identifier during the interview.

Never write to `.migration/migration.json` — it is managed automatically.

## Prerequisites

Read these reference files before starting the interview:

1. `skills/plan-migration/references/output-schema.json` - JSON schema for `plan.json`
2. `skills/plan-migration/examples/sample-plan.json` - sample plan tone and structure

Your context may include hook-injected data:

- **Migration state**: active feature and existing plan directive.
- **Docs routing state**: whether `.migration/docs/index.json` is missing or unreadable.
- **Existing plan**: if present, ask whether to resume/edit or start fresh before proceeding.

If codebase documentation is unavailable, proceed in interview-only mode and mark user-provided modules with `source: "user"`.

## Interview

Use `AskUserQuestion` for every question. Wait for the response before proceeding.

Adapt interview depth based on how well the user understands this specific system. Ask this first:

- **System Expert** - knows the full system; use high-level confirmations and minimal discovery.
- **Feature Owner** - knows their part; ask targeted questions and light discovery on edges.
- **Discovery Mode** - new to this codebase; ask detailed walkthrough questions and be explicit about unknowns.

Capture enough information to populate every required `plan.json` field:

1. **Knowledge level** - `expert`, `feature-owner`, or `discovery`.
2. **Feature identity** - short identifier and one or two sentence description.
3. **Primary migration goal** - a concise label and motivation.
4. **Modules** - involved modules and role: `primary`, `dependency`, or `affected`.
5. **Migration type and technology stacks** - source stack and target stack.
6. **Scope** - included areas, excluded areas, critical components, and boundaries.
7. **Dependencies** - internal modules and external APIs, services, databases, queues, or files.
8. **Risks and constraints** - what could go wrong, what must remain unchanged, and integration contracts that must be preserved.
9. **Success criteria** - concrete, verifiable conditions that define done.
10. **Focus areas** - priority areas ranked by importance for downstream analysis and architecture.

## Confirmation Loop

Before writing files, present a structured summary that includes:

- the `plan.json` fields
- the exact output path

Ask the user to confirm or request corrections. Repeat until confirmed.

## Build Artifacts

After confirmation, build the plan artifact in memory, validate it, then write it.

### plan.json

Write `.migration/<feature-name>/plan/plan.json`.

- Must conform to `skills/plan-migration/references/output-schema.json`.
- Mark all modules with `source: "user"`.
- Use module-level `notes` for module-specific context.
- Use top-level `notes` for interview context spanning multiple fields.

## Validation Before Write

All checks must pass before writing:

1. `plan.json` has every required field from `output-schema.json`.
2. `scope.include.paths` contains human-readable areas, not source file paths unless the user explicitly provided file paths as scope.
3. Every module role is `primary`, `dependency`, or `affected`.
4. Every module source is `user`.
5. Every risk severity is `low`, `medium`, or `high`.
6. `constraints.integration.systems` includes every external system whose contract must be preserved.

## Write

Write `.migration/<feature-name>/plan/plan.json`.

Do not invoke analysis until the file has been written successfully.

## Troubleshooting

- **User gives contradictory information**: Surface the discrepancy explicitly and ask one targeted resolution question.
- **User wants to edit an existing plan**: Ask whether to resume/edit or start fresh before proceeding.
- **Output fails schema validation**: Re-read the relevant schema, fix the non-conforming fields, and re-write only after validation passes.
- **Write fails**: Report the exact file path and error. Do not chain analysis.

## Completion And Chaining

After the artifact is written, report completion:

```text
Plan saved for <feature-name>.
Output:
- .migration/<feature-name>/plan/plan.json

Next: analysis for <feature-name>
```

Then invoke the analysis chain by delegating to the `one-modernizer:code-analyst` agent with the approved feature name.
Do not ask the user to manually run `/analysis` unless the agent/tool invocation is unavailable.
