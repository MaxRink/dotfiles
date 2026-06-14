---
name: ai4dev-migration-plugin-gap-analysis
description: Cross-validate plan, analysis, and architect artifacts to surface gaps, inconsistencies, and missing coverage before implementation. Use when the user asks to "check gaps", "validate artifacts", "verify completeness", "run gap analysis", "check for missing coverage", or "are the artifacts ready". Requires plan.json, analysis.json, and target-architecture.md.
user-invocable: true
disable-model-invocation: true
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/migration-plugin/skills/gap-analysis by codex-knowledge-curation/scripts/persist_project_skills.py. -->

Delegate this task to the `one-modernizer:gap-analyst` agent. Feature: $ARGUMENTS

# Gap Analysis Skill

Cross-validate all migration artifacts to identify gaps, inconsistencies, and missing coverage
before proceeding to implementation. Acts as a quality gate requiring human approval.

**Feature name**: use `$ARGUMENTS` if provided; otherwise ask the user which feature to validate.

<prerequisites>

## Before Starting — Load References

You MUST read these reference files before doing any validation work:

1. Read [schemas/gaps.schema.json](schemas/gaps.schema.json) — JSON schema the output must conform to
2. Read [examples/example-gaps.json](examples/example-gaps.json) — concrete example of a completed gap report

Then read the three required artifacts for the feature (use `$ARGUMENTS` or ask for the feature name):

- `.migration/$ARGUMENTS/plan/plan.json`
- `.migration/$ARGUMENTS/analysis/analysis.json`
- `.migration/$ARGUMENTS/architect/target-architecture.md`

**Hard stop** if any artifact is missing — list the missing files and direct the user to the skill that produces them.

</prerequisites>

<output-spec>

## Output

All files written to `.migration/<feature-name>/gap-analysis/`.

```text
.migration/<feature-name>/gap-analysis/
└── gaps.json     # Structured gap report conforming to schemas/gaps.schema.json
```

</output-spec>

<workflow>

## Workflow

### Step 1 — Load Artifacts

Read and parse all three required artifacts:

1. `.migration/<feature-name>/plan/plan.json`
   - Extract: `scope.include.paths`, `focus_areas`, `constraints`, `source_stack`, `target_stack`, `modules`
2. `.migration/<feature-name>/analysis/analysis.json`
   - Extract: `business_rules[]` (all IDs and summaries), `components[]`, `entities[]`, `control_flows[]`
3. `.migration/<feature-name>/architect/target-architecture.md`
   - Extract: component names, business rule IDs referenced, integration systems listed, focus area sections

If any artifact is missing → **STOP** with error listing the missing files and the skill that produces each one.

### Step 2 — Cross-Artifact Validation

Run all five checks. Collect every finding as a gap entry.

**Check 1 — Business Rules Coverage**

- For every `business_rules[].id` (BR001, BR002, ...) in `analysis.json`:
  - Search `target-architecture.md` for that ID (e.g., `` `BR001` ``, `BR001:`, `(BR001)`)
  - If not found → GAP, category: `missing_business_rules`, severity: `high`
- Business rules are the primary output of analysis — every one must have an architectural home

**Check 2 — Scope Coverage**

- For every path in `plan.scope.include.paths` and every module in `plan.modules`:
  - Check that `analysis.json` contains at least one component or business rule traceable to that path/module
  - Check that `target-architecture.md` contains a component or section addressing that module
  - If analysis gap → GAP, category: `uncovered_scope`, severity: `medium`
  - If architect gap → GAP, category: `uncovered_scope`, severity: `high`

**Check 3 — Dependencies Coverage**

- For every external system in `plan.constraints.integration.systems`:
  - Check that `target-architecture.md` Section 5 (Integration Design) lists that system
  - If missing → GAP, category: `missing_integrations`, severity: `high`
- For every component `dependencies.external` in `analysis.json`:
  - Check that the architecture addresses how that dependency is handled in the target state
  - If unaddressed → GAP, category: `missing_dependencies`, severity: `medium`

**Check 4 — Technology Stack Consistency**

- Compare `plan.target_stack` with architectural choices in `target-architecture.md`
- If the architecture proposes technologies that contradict the plan's target stack → GAP, category: `contradictions`, severity: `high`
- If a focus area from `plan.focus_areas` has no corresponding section or decision in the architecture → GAP, category: `contradictions`, severity: `medium`

**Check 5 — Constraints Preservation**

- For every item in `plan.constraints.unchanged`:
  - Verify `target-architecture.md` does not propose changing that item
  - If the architecture violates a preserved constraint → GAP, category: `contradictions`, severity: `high`

### Step 3 — Generate Gap Report

**Pre-write validation** — verify before writing:

1. Every gap has a unique sequential ID (`GAP-001`, `GAP-002`, ...)
2. Every gap has a non-empty `description`, `severity`, `source_artifact`, and `recommendation`
3. `summary.categories` counts match the actual gaps array entries per category
4. `summary.total_gaps` equals the length of the `gaps` array
5. Output conforms to [schemas/gaps.schema.json](schemas/gaps.schema.json)

Write: `.migration/<feature-name>/gap-analysis/gaps.json`

### Step 4 — Return Results

After writing `gaps.json`, return a structured summary to the caller:

- Status: clean or gaps_found
- Total gaps by severity (high / medium / low)
- Each gap: ID, category, description, recommendation

Do NOT ask the user for approval — the main conversation handles the human gate. Just return the findings.

</workflow>

<constraints>

## Constraints

- **Read-only for source artifacts** — never modify `plan.json`, `analysis.json`, or `target-architecture.md`
- **Write only to `.migration/<feature-name>/gap-analysis/`**
- **Evidence-based** — every gap must cite the exact artifact path and field where the issue was found
- **Schema-compliant** — output must conform to `schemas/gaps.schema.json`
- **No speculation** — only flag gaps that are demonstrably absent. If a business rule ID appears anywhere in the architecture document, it is covered.
- **Human gate** — never auto-approve gaps. Always present findings and require user decision before marking approved.

</constraints>

## Completion

After writing `gaps.json`, return a summary to the main conversation. The main conversation handles the human approval gate.

Include in the summary:

- Gap report path: `.migration/<feature-name>/gap-analysis/gaps.json`
- Total gaps by severity
- For each gap: ID, category, description, recommendation
- If gaps found, suggest which skills to re-run:
  - Missing business rules or scope coverage → `/analysis <feature-name>`
  - Architecture gaps or contradictions → `/architect <feature-name>`
  - Plan scope or constraint issues → `/plan-migration <feature-name>`
