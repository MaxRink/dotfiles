---
name: ai4dev-migration-plugin-audit-analysis
description: Validates analysis.json output against schema, checks source evidence, cross-reference integrity, pseudocode coverage, and component completeness.
user-invocable: false
disable-model-invocation: true
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/migration-plugin/skills/audit-analysis by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Audit Analysis

Think deeply and carefully before reaching any verdict. This is a validation task — false negatives (missed failures) are more costly than false positives.

Validate the output of `/analysis` against its schema and quality criteria. Produces an audit report with pass/fail verdicts and remediation guidance.

## Before Starting — Load References

You MUST read these reference files before running any checks:

1. Read [references/checklist.md](references/checklist.md) — the 7-check validation checklist with pass/fail criteria
2. Read the analysis schema at [skills/analysis/references/schema.json](../analysis/references/schema.json) — the source of truth for field requirements
3. Read `skills/golden-principles/references/default-principles.md` — default golden principles (cross-project evaluation guidelines that prevent known false positives)
4. Glob `${CLAUDE_PLUGIN_DATA}/golden-principles/*.md` and read any confirmed learned principles

## Target

The audit target is `.migration/<feature-name>/analysis/analysis.json`.

Determine the feature name from `.migration/migration.json` (`active_feature` field).
If `migration.json` is absent, use `$ARGUMENTS` as the feature name to locate the audit files.

## Output

Write the audit report to: `.migration/<feature-name>/analysis/audit-report.md`

---

## Workflow

### Step 1 — Load Target

1. Read `.migration/migration.json` to get the active feature name (`active_feature` field). If `migration.json` is absent, use `$ARGUMENTS` as the feature name.
2. Read `.migration/<feature-name>/analysis/analysis.json`
3. If it doesn't exist → immediately produce a FAIL report: "analysis.json not found. Run /analysis first."
4. Parse the JSON — if invalid, produce a FAIL report: "analysis.json is not valid JSON"
5. Read `.migration/<feature-name>/plan/plan.json` for scope validation in Check 6

### Step 2 — Execute Checklist

Run all 7 checks from `references/checklist.md` in order. For each check:

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
3. Write the audit report to `.migration/<feature-name>/analysis/audit-report.md`

### Step 4 — Report to User

Present a summary:

```text
Audit complete for <feature-name> analysis:
  Verdict: <PASS | PASS_WITH_WARNINGS | FAIL>
  Checks passed: N/7
  Critical issues: N
  Warnings: N

  Report: .migration/<feature-name>/analysis/audit-report.md
```

If the verdict is FAIL, list each critical issue with its remediation in the summary.

---

## Constraints

- **Read-only for source code** — never modify repository files
- **Read-only for analysis output** — never modify `analysis.json` (except writing `audit-report.md`)
- **Follow the checklist exactly** — do not invent additional checks or skip any
- **Evidence-based verdicts** — every FAIL must cite specific evidence (IDs, file paths, values)
- **No auto-fix** — report issues and remediation steps, but do not fix the analysis output

## Completion

- **If PASS or PASS_WITH_WARNINGS**: Tell the user the analysis is validated.
- **If FAIL**: List each critical issue with its remediation.
