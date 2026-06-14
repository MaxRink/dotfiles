---
name: ai4dev-migration-plugin-traceability-matrix-builder
description: Reads migration artifacts and builds the traceability matrix — maps every business rule to its spec requirement, target component, and expected test areas. Artifact-level only, no code search.
user-invocable: false
disable-model-invocation: false
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/migration-plugin/skills/traceability-matrix-builder by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Traceability Matrix Builder

Reads migration artifacts and produces `traceability-matrix.json` — the artifact-level
trace for every business rule. No generated code is read in this phase.

## Before Starting — Load References

1. Read [references/traceability-matrix-schema.json](references/traceability-matrix-schema.json) — output must conform to this schema
2. Read [references/build-matrix-steps.md](references/build-matrix-steps.md) — step-by-step instructions for building the matrix

Then read the artifact paths provided in your prompt:

- `.migration/<feature>/plan/plan.json`
- `.migration/<feature>/analysis/analysis.json`
- `.migration/<feature>/spec-specification/spec.json`
- `.migration/<feature>/spec-specification/functional-requirements.md`

**Hard stop** if any artifact is missing — report which files are absent.

## Workflow

Follow all steps in `build-matrix-steps.md` exactly.

## Output

Write to: `.migration/<feature>/validation/traceability-matrix.json`

The matrix must include:

- `feature`, `artifact_coverage` (counts + coverage_pct), `entries[]`, `out_of_scope_brs[]`, `issues[]`

## Constraints

- **Artifact-level only** — do not read generated code or source repository files
- **Read-only for artifacts** — never modify `plan.json`, `analysis.json`, or `spec.json`
- **Evidence-based** — every issue must cite the specific artifact field path
- **No decision gate** — write the matrix and return DONE; the orchestrator handles critical issue escalation
