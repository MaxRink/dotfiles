---
name: ai4dev-migration-plugin-audit-spec
description: Validates spec-specification output against architecture, checks BR coverage, contract completeness, edge cases, and consistency.
user-invocable: false
disable-model-invocation: true
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/migration-plugin/skills/audit-spec by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Audit Specification

Validate the output of `/spec-specification` against architecture artifacts and quality criteria.
Produces an audit report with pass/fail verdicts and remediation guidance.

## Before Starting — Load References

You MUST read this reference file before running any checks:

1. Read [references/checklist.md](references/checklist.md) — the validation checklist with pass/fail criteria

## Target

The audit targets are:

- `.migration/<feature-name>/spec-specification/contracts.md`
- `.migration/<feature-name>/spec-specification/functional-requirements.md`
- `.migration/<feature-name>/spec-specification/nonfunctional-requirements.md`
- `.migration/<feature-name>/spec-specification/technical-plan.md`

Determine the feature name from `.migration/migration.json` (`active_feature` field).
If `migration.json` is absent, use `$ARGUMENTS` as the feature name.

## Output

Write the audit report to: `.migration/<feature-name>/spec-specification/audit-report.md`

---

## Workflow

### Step 1 — Load Targets

1. Read `.migration/migration.json` to get the active feature name. If absent, use `$ARGUMENTS`.
2. Read all four spec files:
   - `.migration/<feature>/spec-specification/contracts.md`
   - `.migration/<feature>/spec-specification/functional-requirements.md`
   - `.migration/<feature>/spec-specification/nonfunctional-requirements.md`
   - `.migration/<feature>/spec-specification/technical-plan.md`
3. If any file is missing → produce a FAIL report listing missing files
4. Read prerequisite artifacts for validation:
   - `.migration/<feature>/plan/plan.json`
   - `.migration/<feature>/analysis/analysis.json`
   - `.migration/<feature>/architect/target-architecture.md`
   - `.migration/<feature>/gap-analysis/gaps.json`

### Step 2 — Execute Checklist

Run all checks from `references/checklist.md` in order. For each check:

1. Execute the validation steps described in the checklist
2. Record the result: `PASS` or `FAIL`
3. Record details: what was checked, what was found
4. If FAIL: record severity (`critical` or `warning`), evidence, and remediation

### Step 3 — Compile Results

1. Count critical issues and warnings
2. Determine verdict:
   - `PASS` — zero critical, zero warnings
   - `PASS_WITH_WARNINGS` — zero critical, one or more warnings
   - `FAIL` — one or more critical issues
3. Write the audit report to `.migration/<feature>/spec-specification/audit-report.md`

### Step 4 — Report to User

Present a summary:

```text
Audit complete for <feature-name> specifications:
  Verdict: <PASS | PASS_WITH_WARNINGS | FAIL>
  Checks passed: N/12
  Critical issues: N
  Warnings: N

  Report: .migration/<feature-name>/spec-specification/audit-report.md
```

If the verdict is FAIL, list each critical issue with its remediation in the summary.

---

## Constraints

- **Read-only for source code** — never modify repository files
- **Read-only for spec output** — never modify spec files (except writing `audit-report.md`)
- **Follow the checklist exactly** — do not invent additional checks or skip any
- **Evidence-based verdicts** — every FAIL must cite specific evidence (IDs, file names, values)
- **No auto-fix** — report issues and remediation steps, but do not fix the spec output

## Completion

- **If PASS or PASS_WITH_WARNINGS**: Tell the user the specifications are validated and direct them to run `/code-generation <feature-name>` as the next step.
- **If FAIL**: List each critical issue with its remediation. Direct the user to re-run `/spec-specification <feature-name>` to fix the issues.
