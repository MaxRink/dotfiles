---
name: ai4dev-migration-plugin-audit-explore
description: Validates deep-explore documentation output. Checks structural compliance, quality score accuracy, cross-cutting coverage, evidence validity, and template adherence.
user-invocable: false
disable-model-invocation: true
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/migration-plugin/skills/audit-explore by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Audit Explore

Think deeply and carefully before reaching any verdict. This is a validation task — false negatives (missed failures) are more costly than false positives.

Validate the output of `/deep-explore` against its specification. Produces an audit report with pass/fail verdicts and remediation guidance.

## Before Starting — Load References

You MUST read these reference files before running any checks:

1. Read [references/checklist.md](references/checklist.md) — the 9-check validation checklist with pass/fail criteria
2. Read `skills/deep-explore/references/schemas/schema.json` — the JSON schema for `index.json` (required before running checks)
3. Read `skills/golden-principles/references/default-principles.md` — default golden principles (cross-project evaluation guidelines that prevent known false positives)
4. Glob `${CLAUDE_PLUGIN_DATA}/golden-principles/*.md` and read any confirmed learned principles

## Target

The audit target is `.migration/docs/` — specifically the `index.json` manifest and all files it references.

## Output

Write the audit report to: `.migration/docs/audit-report.md`

---

## Workflow

### Step 1 — Load Target

1. Read `.migration/docs/index.json`
2. If it doesn't exist → immediately produce a FAIL report with a single critical issue: "index.json not found"
3. Parse the JSON — if invalid JSON, produce a FAIL report with critical issue: "index.json is not valid JSON"
4. Store the parsed manifest for use in subsequent checks

### Step 2 — Execute Checklist

Run all 9 checks from `references/checklist.md` in order. For each check:

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
3. Write the audit report to `.migration/docs/audit-report.md`

### Step 4 — Report to User

Present a summary:

```text
Audit complete for .migration/docs/:
  Verdict: <PASS | PASS_WITH_WARNINGS | FAIL>
  Checks passed: N/9
  Critical issues: N
  Warnings: N

  Report: .migration/docs/audit-report.md
```

If the verdict is FAIL, list each critical issue with its remediation in the summary.

---

## Constraints

- **Read-only for source code** — never modify repository files
- **Read-only for deep-explore output** — never modify `.migration/docs/` files (except writing `audit-report.md`)
- **Follow the checklist exactly** — do not invent additional checks or skip any
- **Evidence-based verdicts** — every FAIL must cite specific evidence (file paths, values, line numbers)
- **No auto-fix** — report issues and remediation steps, but do not fix the deep-explore output

## Completion

- **If PASS or PASS_WITH_WARNINGS**: Tell the user the documentation is validated.
- **If FAIL**: List each critical issue with its remediation.
