# Plan Migration ADR

Create a migration plan through a docs-backed ADR review loop. Invoked by the orchestrator when `.migration/docs/index.json` exists and is valid.

Feature name: use `$ARGUMENTS` if provided; otherwise use the active feature from hook-injected context.
If no feature name is available after the first interview question, derive a short kebab-case `feature_name` from the approved ADR title.

## Prerequisites

Read these before asking the first question:

1. `skills/plan-migration/references/adr-schema.json` - schema for `.migration/<feature>/plan/plan.adr.json`
2. `skills/plan-migration/references/adr-markdown-template.md` - markdown renderer for `plan.adr.md`
3. `.migration/docs/index.json` - deep-explore index

If `.migration/docs/index.json` is missing or unreadable, stop and inform the user that deep-explore must be run first, or suggest using `/plan-migration` which will route to the interview path.
If a prompt or diagram says `index.js`, treat it as `.migration/docs/index.json`.

## Load Documentation Context

Use `.migration/docs/index.json` as the source map. Read only documentation artifacts, not source code.

1. Extract documented modules from `index.modules[]` or `index.stacks[]`.
2. Extract source stack from `index.technology_stack`.
3. Read each relevant cross-cutting doc from `index.cross_cutting`:
   - `api_contracts`
   - `data_flow`
   - `database_schema`
   - `dependencies`
   - `infrastructure`
   - `security`
   - `testing`
   - `technical_debt`
4. Read module docs from `index.modules[].doc_file` only when cross-cutting docs and index summaries are not enough to identify scope, dependencies, risks, or critical components.

Build a compact planning context containing:

- candidate modules and doc paths
- detected source stack
- APIs, data stores, external systems, integration seams, security constraints, test signals, technical debt, and infrastructure notes
- likely risks and constraints with doc evidence

## Initial Interview: Maximum Four Questions

Use AskUserQuestion for every question. Ask no more than four initial questions before drafting the ADR. Combine fields instead of asking one question per schema field.

Question 1 - Knowledge level:

- Ask how well the user knows this system: `expert`, `feature-owner`, or `discovery`.
- Use this answer to decide how much explanation to include in later questions.

Question 2 - Feature and primary goal:

- Present the most likely feature/module candidates from the docs.
- Ask for feature identity, short description, and the single primary migration goal.

Question 3 - Migration type and target stack:

- Present detected source stack from `index.json`.
- Ask the user to confirm migration type and target stack: languages, frameworks, infrastructure, and any required platform standards.

Question 4 - Constraints, scope, and success:

- Present inferred scope, external systems, risks, constraints, and critical components from cross-cutting docs.
- Ask the user to confirm what is in scope, out of scope, must remain unchanged, and what concrete success criteria define approval.

If the user answers one question with enough information to cover later fields, do not ask redundant questions.
If docs already answer a field, ask for confirmation or correction rather than asking from scratch.

## Draft ADR - Non-Persistent

Draft the ADR in memory only. Do not write `plan.json`, `plan.adr.json`, `plan.adr.md`, session files, or scratch files during drafting or review.

The draft must contain all fields required by `adr-schema.json` and enough information to project into every required field of `output-schema.json`.

Drafting rules:

- Use facts from `index.json` and cross-cutting docs as evidence.
- Mark user-provided modules with `source: "user"`.
- Mark documented modules with `source: "index.json"` and preserve `doc_file` where available.
- Do not invent target technologies, external systems, constraints, or success criteria.
- Represent unresolved uncertainty as a review question, not as a persisted assumption.

## Enter Plan Mode And Review Loop

Enter plan mode before any file writes. The ADR is not approved until the user explicitly approves it.

Loop until approved:

1. Show the drafted ADR in concise markdown form. Include: title, status `Draft`, context, decision, target stack, scope, constraints, risks, success criteria, modules, and source documents.
2. Ask the user via AskUserQuestion:
   - `Approve ADR`
   - `Needs changes`
   - `Reject and restart interview`
3. If approved, exit the loop and proceed to artifact generation.
4. If changes are needed, ask the user to describe edits or pushback.
5. Ask dynamic follow-up questions only when the requested edit leaves a real gap that blocks schema-valid output. Do not ask follow-up questions for preferences or details the user already supplied.
6. Update the in-memory ADR draft.
7. Repeat from step 1.

If the user rejects the current draft, restart the interview sequence within this same workflow without writing files.

## Generate Artifacts After Approval

Only after explicit approval, write files under `.migration/<feature-name>/plan/`.

Write in this order:

1. `.migration/<feature-name>/plan/plan.adr.json`
2. `.migration/<feature-name>/plan/plan.adr.md`

Do not invoke analysis until both artifacts have been written successfully.

`plan.adr.json`:

- Must conform to `references/adr-schema.json`.
- Set `status` to `approved`.
- Include `approvals.review_iterations`.
- Include `source_documents[]` for `index.json`, every cross-cutting doc used, and any module doc used.

`plan.adr.md`:

- Render strictly from `plan.adr.json` using `references/adr-markdown-template.md`.
- Do not add decisions or context that are not present in the JSON.

Validate before writing:

1. `plan.adr.json` has every required field from `adr-schema.json`.
2. Every module role is one of `primary`, `dependency`, or `affected`.
3. Every risk severity is one of `low`, `medium`, or `high`.
4. `constraints.integration.systems` includes every external system preserved by the ADR.

## Chain To Analysis

After both artifacts are written, continue the existing workflow chain.

Completion message:

```text
Plan ADR approved for <feature-name>.
Outputs:
- .migration/<feature-name>/plan/plan.adr.json
- .migration/<feature-name>/plan/plan.adr.md

Next: analysis for <feature-name>
```

Then invoke the analysis chain by delegating to the `one-modernizer:code-analyst` agent with the approved feature name.
Do not ask the user to manually run `/analysis` unless the agent/tool invocation is unavailable.

## Error Handling

| Situation | Action |
|-----------|--------|
| `index.json` missing | Stop and inform the user to run deep-explore first, or use `/plan-migration` to route to interview path. |
| `index.json` invalid JSON | Stop and inform the user the docs index is unreadable; suggest re-running deep-explore. |
| User gives contradictory answers | Surface the contradiction and ask one targeted resolution question. |
| ADR draft lacks required plan fields | Ask a dynamic follow-up question for only the missing fields. |
| User cancels before approval | Stop without writing files. |
| File write fails | Report the exact artifact path and error; do not continue to analysis. |
