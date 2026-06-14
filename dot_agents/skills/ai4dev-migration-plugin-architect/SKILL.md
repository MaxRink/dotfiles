---
name: ai4dev-migration-plugin-architect
description: Design the target-state architecture interactively. Use when the user asks to "architect", "design target architecture", "plan the new system", or "define target state". Requires plan.json and analysis.json. Produces target-architecture.md, session.json, and optional Mermaid diagrams.
user-invocable: true
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/migration-plugin/skills/architect by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Architect Skill

Design the target-state architecture through an interactive questionnaire.
Produces a comprehensive target architecture document, a decisions session log,
and optional Mermaid diagrams.

**Feature name**: use `$ARGUMENTS` if provided (strip `--resume` first); otherwise use the active feature from hook-injected context.
**Resume**: if `$ARGUMENTS` contains `--resume`, restore prior session state from `.architect-session.json`.

<prerequisites>

## Before Starting — Load References

Read these files before the interview:

1. [references/architecture-questions.md](references/architecture-questions.md) — question bank with skip conditions, filter rules, adaptive triggers
2. [references/output-schema.json](references/output-schema.json) — JSON schema for `session.json` and `.architect-session.json`

Defer these until Step 4 (generation) — do NOT read them upfront:

1. [references/output-template.md](references/output-template.md) — template for `target-architecture.md` (read before generating)
2. [references/pattern-catalog.md](references/pattern-catalog.md) — architectural patterns (read before generating, filtered to chosen style)
3. [references/examples/sample-target-architecture.md](references/examples/sample-target-architecture.md) — example document (read before generating)
4. [references/examples/sample-session.json](references/examples/sample-session.json) — example session (read before writing session.json)

Then load the feature's artifacts. Hook injection provides them automatically — verify they are present in context:

- `plan.json` at `.migration/<feature>/plan/plan.json` — extract `migration_goals`, `scope`, `focus_areas`, `constraints`, `source_stack`, `target_stack`
- `analysis.json` at `.migration/<feature>/analysis/analysis.json` — extract `business_rules[]`, `control_flows[]`, `entities[]`, `components[]`

**Hard stop** if either is missing — see Error Handling.

Optional (warn if missing, continue without):

- `.migration/docs/index.json` — tech stack and module summaries for richer context

</prerequisites>

<output-spec>

## Output

All files written to `.migration/<feature>/architect/`.

```text
.migration/<feature>/architect/
├── target-architecture.md          # Full target architecture document
├── session.json                    # All decisions from the interactive session
├── .architect-session.json         # In-progress session state (deleted on completion)
└── diagrams/                       # Only if diagrams were requested in DQ1
    ├── target-component-diagram.md
    ├── target-sequence-diagram.md
    └── target-class-entity-diagram.md
```

</output-spec>

<workflow>

## Workflow

### Step 1 — Validate Context

Confirm `plan.json` and `analysis.json` are loaded. Build a merged context object:

- From `plan.json`: `migration_goals`, `scope`, `focus_areas`, `constraints`, `source_stack`, `target_stack`
- From `analysis.json`: `business_rules[]` (count + IDs), `control_flows[]`, `entities[]`, `components[]`

If `--resume`: read `.migration/<feature>/architect/.architect-session.json`, restore `responses[]`, determine next unanswered question. If file not found: warn "No previous session found. Starting fresh."

### Step 2 — Present Context Summary

Before the first question, show what was loaded:

```text
I've loaded the migration context for <feature>:

 • Goal: <migration_goals.primary.goal> — <description>
 • Scope: <scope.include.mode> (<N> paths)
 • Business rules: <N> extracted
 • Focus areas: <list from focus_areas>
 • Constraints: <unchanged items>
 • Analysis: <N> control flows, <N> entities

Ready to design the target architecture.
```

Ask: `["Continue", "I need to update context first (re-run a previous skill)"]`

If "update context" — stop and advise which skill to re-run.

### Step 3 — Interactive Questionnaire

Use `AskUserQuestion` for every question. Full question definitions, skip conditions, filter rules, and adaptive triggers are in [references/architecture-questions.md](references/architecture-questions.md).

**Question order:**

| # | ID | Topic | Skip condition |
|---|----|-------|----------------|
| 1 | Q1 | Existing patterns / org standards | — |
| 2 | Q2 | Architectural style | — |
| 3 | Q3 | Communication patterns | — |
| 4 | Q4 | Data storage strategy | — |
| 5 | Q5 | Data migration approach | `constraints.unchanged` includes `database_schema` |
| 6 | Q6 | Authentication / authorization | — |
| 7 | Q7 | Cross-cutting concerns | — |
| 8 | Q8 | Deployment model | — |
| 9 | Q9 | Additional requirements (free text) | — |
| 10 | AQ1–AQ5 | Adaptive questions | Only if trigger condition met — see question bank |
| 11 | DQ1 | Target diagrams | — |

For each question:

- Check skip conditions — if met, record `was_skipped: true` with reason, do not ask
- Apply context filters — pre-select or highlight options based on plan/analysis data (see question bank)
- Ask via `AskUserQuestion`
- Record response in `responses[]`
- Write updated `.architect-session.json` after every answer (enables `--resume`)

### Step 4 — Generate Target Architecture Document

After all questions are answered:

1. Read [references/output-template.md](references/output-template.md) — document structure and section guidelines
2. Read [references/pattern-catalog.md](references/pattern-catalog.md) — filter to the chosen architectural style from Q2
3. Read [references/examples/sample-target-architecture.md](references/examples/sample-target-architecture.md) — tone and detail level
4. Generate `target-architecture.md` using merged context + all session responses

**Content rules:**

- **Section 3 (Component Design)**: every `BR###` from `analysis.json` must be assigned to exactly one component
- **Section 4 (Data Architecture)**: never propose changes to items in `constraints.unchanged`
- **Section 5 (Integration Design)**: include every system from `constraints.integration.systems`
- **Section 8 (Migration Path)**: order phases from lowest to highest dependency coupling
- **Section 9 (Decision Log)**: one entry per question answered, including skipped and adaptive questions

### Step 5 — Generate Diagrams (if requested in DQ1)

If diagrams were requested, read Mermaid syntax references from `mermaid-diagrams` skill:

- `skills/mermaid-diagrams/references/` — component/C4, sequence, class/ERD guides

| Diagram | Output file |
|---------|-------------|
| Component / C4 | `diagrams/target-component-diagram.md` |
| Sequence | `diagrams/target-sequence-diagram.md` |
| Class / Entity | `diagrams/target-class-entity-diagram.md` |

Each diagram file: brief explanation + Mermaid code block + notes on differences from current state.

### Step 6 — Review

Display the generated `target-architecture.md` and ask via `AskUserQuestion`:

- `"Approve — save as-is"` → proceed to Step 7
- `"Needs changes — I'll describe what to adjust"` → accept feedback, regenerate affected sections, re-present
- `"Regenerate section (specify which)"` → ask which section (1–10), regenerate only that section
- `"Add more detail to a specific component"` → ask which component, expand its subsection

Increment `review_iterations` each cycle. Loop until approved.

### Step 7 — Save Artifacts

Write:

```text
.migration/<feature>/architect/target-architecture.md
.migration/<feature>/architect/session.json
.migration/<feature>/architect/diagrams/  (if generated)
```

`session.json` must conform to [references/output-schema.json](references/output-schema.json).
`generated_at` timestamp format: human-readable, e.g. `03 Mar 2026 14:30:00`.

Delete `.architect-session.json` — session is complete; `session.json` is the permanent record.

</workflow>

<constraints>

## Constraints

- **Hard stop on missing context** — never proceed without `plan.json` and `analysis.json`
- **Save session state after every question** — `.architect-session.json` enables `--resume`
- **Respect plan constraints** — never propose changes to `constraints.unchanged` items
- **Map all business rules** — every BR from `analysis.json` must own exactly one component in Section 3
- **Map all integrations** — every external system from `constraints.integration.systems` must appear in Section 5
- **Use consistent IDs** — reference business rules by their `analysis.json` IDs (BR001, BR002, etc.)
- **Follow output template** — use `references/output-template.md`; do not invent sections
- **Write only to `.migration/<feature>/architect/`** — never touch source code

</constraints>

<error-handling>

## Error Handling

| Error | Action |
|-------|--------|
| `plan.json` missing | Hard stop: "Cannot proceed: plan.json not found. Run /plan-migration first." |
| `analysis.json` missing | Hard stop: "Cannot proceed: analysis.json not found. Run /analysis first." |
| `.architect-session.json` corrupt | Warn user, offer to start fresh |
| User cancels mid-session | Save current state to `.architect-session.json` before stopping |
| Write fails | Report error, suggest checking permissions |

</error-handling>

## Completion

After `session.json` and `target-architecture.md` are saved, report completion to the main conversation:

```text
Architecture complete for <feature-name>.
Output: .migration/<feature-name>/architect/target-architecture.md
Questions answered: <N>, Review iterations: <N>

Next step: /gap-analysis
```

Do not invoke `/gap-analysis` yourself — chaining handles it.
