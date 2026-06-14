---
name: ai4dev-migration-plugin-code-review
description: Parallel code review orchestrator. Reads the fingerprint, spawns 4 concern reviewers in parallel, validates outputs, merges findings, and writes the final report.
user-invocable: false
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/migration-plugin/skills/code-review by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Code Review — Orchestrator Workflow

You are the orchestrator. You do NOT read source files yourself.
You read the fingerprint, spawn Wave 1 agents via the Agent tool,
validate outputs, merge findings, and write the final report.

**Sub-agents available:**

| Agent name | Wave | Reference file |
|-----------|------|----------------|
| `one-modernizer:code-reviewer` | 1 | `skills/code-review/references/concern-reference.md` |

**Key rules:**

- Sub-agents return only `DONE: <file> written`. Read findings files from disk after Wave 1.
- Do NOT paste the full fingerprint into sub-agent prompts — pass only what each agent needs.
- Spawn all 4 agents in a single message for parallelism.

---

## Step 0 — Load Fingerprint

**If INLINE FINGERPRINT DATA was injected** by the hook: use that JSON directly.
**Otherwise**: Read `.migration/<feature>/validation/fingerprint.json`.
**If neither exists**: Glob `.migration/*/code-generation/` to infer the active feature,
  then count files manually to build a minimal fingerprint.

Extract and record:

| Field | Purpose |
|-------|---------|
| `active_feature` | Used in all output paths |
| `code_gen_dir` | Source directory to pass to each concern agent |
| `total_files` | Reported in the final summary |
| `tier` | Informs concern agents of scan depth (small/medium/large) |
| `extension_inventory` | Passed to security and performance agents for targeted grep |

## Step 1 — Read Reference Files

Read now — needed for Step 4 (Write Report):

1. [references/report-template.md](references/report-template.md)

## Step 2 — Wave 1: Parallel Concern Agents (4 agents)

Spawn all four in a **single message**. Each gets only the data it needs:

**Agent 1 — Quality Reviewer:**

- Data: concern = `quality`, `code_gen_dir`, `tier`
- Output: `.migration/<active_feature>/validation/code-review/findings/quality-findings.md`

**Agent 2 — Security Reviewer:**

- Data: concern = `security`, `code_gen_dir`, `tier`, `extension_inventory`
- Output: `.migration/<active_feature>/validation/code-review/findings/security-findings.md`

**Agent 3 — Performance Reviewer:**

- Data: concern = `performance`, `code_gen_dir`, `tier`, `extension_inventory`
- Output: `.migration/<active_feature>/validation/code-review/findings/performance-findings.md`

**Agent 4 — Testing Reviewer:**

- Data: concern = `testing`, `code_gen_dir`, `tier`
- Output: `.migration/<active_feature>/validation/code-review/findings/testing-findings.md`

### Validate Wave 1

After all agents return, Glob `.migration/<active_feature>/validation/code-review/findings/*.md`.
Verify 4 files exist, each with > 3 lines.
Re-spawn any missing or empty agent with the same prompt before proceeding.

## Step 3 — Merge Findings and Determine Verdict

Read all 4 findings files. Collect every finding across all concerns.

Count by severity:

- `critical` — security violations, broken logic, no tests at all
- `warning` — performance issues, test gaps, missing docs
- `minor` — naming, style, minor quality issues

**Determine verdict:**

- `PASS` — zero critical, zero warnings, zero minor
- `PASS_WITH_WARNINGS` — zero critical, one or more warnings or minor
- `FAIL` — one or more critical issues

## Step 4 — Write Final Report

Fill in `references/report-template.md` with all findings and write to:
`.migration/<active_feature>/validation/code-review/code-review-report.md`

The report MUST include:

- Verdict and date
- Summary table (critical / warning / minor counts)
- All findings from all 4 concern files, grouped by severity and deduplicated
- Checklist Coverage table showing PASS/FAIL per concern

Omit empty severity sections. If verdict is PASS, omit the Findings section entirely.

## Step 5 — Report to User

```text
Code review complete for .migration/<feature>/code-generation/:
  Verdict: <PASS | PASS_WITH_WARNINGS | FAIL>
  Concerns reviewed: 4 (quality, security, performance, testing)
  Critical: N | Warnings: N | Minor: N

  Findings: .migration/<feature>/validation/code-review/findings/
  Report:   .migration/<feature>/validation/code-review/code-review-report.md
```

If verdict is `FAIL`: list each critical finding with its remediation.
If verdict is `PASS_WITH_WARNINGS`: list warnings briefly, note they are non-blocking.
If verdict is `PASS`: tell the user the code is ready for the next step.

---

## Constraints

- **Read-only** — never modify any file under review; only write to `.migration/<feature>/validation/code-review/`
- **Evidence-based verdicts** — every FAIL must cite specific evidence (file path, line number)
- **No auto-fix** — report issues and remediation steps only

## Troubleshooting

- **Sub-agent fails or times out**: Re-spawn only that agent with the same prompt. Do not restart the wave.
- **Findings file empty or < 3 lines**: Re-spawn the concern agent — a valid findings file must have at least a checklist table.
- **Fingerprint missing**: Glob `.migration/*/code-generation/` to find the feature, build fingerprint inline.
