# Validation — Orchestrator Workflow

You are the orchestrator. You do NOT read source code or generated code yourself.
You read the fingerprint, spawn waves of sub-agents via the Agent tool,
merge their findings, and compile the final report.

**Sub-agents available:**

| Agent name | Wave | Task |
|-----------|------|------|
| `one-modernizer:traceability-builder` | 1 | Build Phase 1 traceability matrix from artifacts |
| `one-modernizer:br-validator` | 2 | Validate a batch of BRs against generated code |
| `one-modernizer:validation-checker` | 3 | Run cross-checks (reverse traceability, risks, constraints) |

**Key rules:**

- Sub-agents return only `DONE: <file> written`. Read files from disk between waves.
- Do NOT read source files or generated code yourself — pass paths to sub-agents.
- Spawn all agents in a wave in a single message for parallelism.
- Temp files (`br-batch-*.json`, `check-*-findings.json`) are deleted after merging.
- **Output files:** ONLY `traceability-matrix.json` and `business-logic-validation-report.json`
  may exist in `.migration/<feature>/validation/` after completion.
  Do NOT write any `.md` files or any other files.

---

## Step 0 — Load Fingerprint

**If INLINE FINGERPRINT DATA was injected** by the hook: use that JSON directly.
**Otherwise**: Read `.migration/<feature>/validation/fingerprint.json`.

Extract and record:

| Field | Purpose |
|-------|---------|
| `active_feature` | Used in all output paths |
| `code_gen_dir` | Root of generated code — passed to sub-agents |
| `tier` | Informs sub-agents of scan depth (small/medium/large) |

---

## Step 1 — Wave 1: Build Traceability Matrix (1 agent)

Spawn one `one-modernizer:traceability-builder` agent.

Pass only what it needs:

```text
Build the Phase 1 traceability matrix.
Feature: <active_feature>
Artifacts:
  - .migration/<active_feature>/plan/plan.json
  - .migration/<active_feature>/analysis/analysis.json
  - .migration/<active_feature>/spec-specification/spec.json
  - .migration/<active_feature>/spec-specification/functional-requirements.md
Write to: .migration/<active_feature>/validation/traceability-matrix.json
Return DONE when complete.
```

### Validate Wave 1

After the agent returns, read `.migration/<active_feature>/validation/traceability-matrix.json`.
Verify it exists and `artifact_coverage.in_scope > 0`.

If critical issues exist in `traceability-matrix.json` (entries with `spec_coverage: "MISSING"`
or matrix-level `issues[]` with `severity: "critical"`), present the decision gate to the user:

```text
Critical traceability gaps found. How do you want to proceed?
  [1] Continue — validate all BRs; MISSING entries will be marked unlocatable
  [2] Stop — fix documentation gaps in spec.json traceability first, then re-run
```

If [2]: halt. Do not proceed to Wave 2.

---

## Step 2 — Prepare BR Batches

Read `traceability-matrix.json`. Extract all `entries[]` where `spec_coverage != "MISSING"`.

**Batch size: 5 BRs per agent.**
Number of agents: `ceil(in_scope_entries / 5)`

**Resolve component paths** — build a map of `target_component` → file path hint:
Glob `<code_gen_dir>/**/*` and fuzzy-match each unique `target_component` name against
actual file names (case-insensitive substring match). Record the best match per component.
Components with no match are left unresolved — br-validator will search broadly.

---

## Step 3 — Wave 2: BR Validation (N parallel agents)

Spawn all `one-modernizer:br-validator` agents in a **single message**.

Each agent prompt:

```text
Validate this batch of BRs against the generated code.
Batch: <N> of <total>
Feature: <active_feature>
Generated code root: <code_gen_dir>
Tier: <tier>
Component path hints: <JSON object: { "OrderService": "src/services/order/OrderService.java", ... }>

BR entries to validate (JSON):
<array of 5 entries: br_id, summary, pseudocode, target_component, expected_test_areas, spec_coverage>

Write findings to: .migration/<active_feature>/validation/br-batch-<N>.json
Return DONE when complete.
```

### Validate Wave 2

After all agents return, Glob `.migration/<active_feature>/validation/br-batch-*.json`.
Verify each expected batch file exists with > 2 lines.
Re-spawn any missing or empty agent with the same prompt before proceeding.

---

## Step 4 — Merge BR Findings (orchestrator, no agent)

Read all `br-batch-*.json` files. Each contains an `entries[]` array keyed by `br_id`.

For each entry in `traceability-matrix.json entries[]`, find the matching `br_id` in the
batch files and write back:

- `implementation_evidence`
- `logic_verified`
- `test_evidence`
- `implementation_status`
- `issues[]` (from batch file)

Write the enriched `traceability-matrix.json`.

Compute `code_coverage_pct`:

```text
implemented = count where implementation_status = "IMPLEMENTED"
code_coverage_pct = (implemented / total in_scope_entries) * 100
```

Delete all `br-batch-*.json` temp files.

---

## Step 5 — Wave 3: Cross-Checks (2 parallel agents)

Spawn both `one-modernizer:validation-checker` agents in a **single message**.

**Agent A — Check 2 (Reverse Traceability):**

```text
Run Check 2: Reverse Traceability.
Feature: <active_feature>
Generated code root: <code_gen_dir>
Tier: <tier>
Expected components (from traceability matrix): <JSON array of unique target_component values>
Write findings to: .migration/<active_feature>/validation/check-2-findings.json
Return DONE when complete.
```

**Agent B — Checks 3–5 (Risk, Success Criteria, Constraints):**

```text
Run Checks 3, 4, and 5.
Feature: <active_feature>
Plan path: .migration/<active_feature>/plan/plan.json
Generated code root: <code_gen_dir>
Tier: <tier>
Write findings to: .migration/<active_feature>/validation/check-35-findings.json
Return DONE when complete.
```

### Validate Wave 3

After both agents return, verify both findings files exist with > 2 lines.
Re-spawn any missing agent before proceeding.

---

## Step 6 — Compile Report (orchestrator, no agent)

Read:

- `.migration/<active_feature>/validation/traceability-matrix.json`
- `.migration/<active_feature>/validation/check-2-findings.json`
- `.migration/<active_feature>/validation/check-35-findings.json`
- `skills/validation/references/report-schema.json`

Build `business-logic-validation-report.json` conforming to the schema:

- `checks.check_1_business_rules`: derive from `traceability-matrix.json` — `code_coverage_pct`,
  total/implemented/partial/missing counts, `traceability_matrix_path`
- `checks.check_2_reverse_traceability`: from `check-2-findings.json`
- `checks.check_3_risk_mitigation`, `check_4_success_criteria`, `check_5_constraints`: from `check-35-findings.json`

**Compute `overall_status`:**

| Condition | Status |
|-----------|--------|
| Any critical issue in any check, OR `code_coverage_pct < 80` | `FAIL` |
| No critical issues, `code_coverage_pct >= 80` | `PASS_WITH_WARNINGS` |
| No critical issues, no warnings, `code_coverage_pct = 100` | `PASS` |

Write: `.migration/<active_feature>/validation/business-logic-validation-report.json`

Delete temp files: `check-2-findings.json`, `check-35-findings.json`.

---

## Step 7 — Report to User

```text
Validation complete for <feature>:
  Overall: <PASS | PASS_WITH_WARNINGS | FAIL>
  BRs validated: <in_scope> (<implemented> implemented, <partial> partial, <missing> missing)
  Code coverage: <code_coverage_pct>%
  Checks passed: <N>/5
  Issues: <critical> critical, <warnings> warnings

  Traceability matrix: .migration/<feature>/validation/traceability-matrix.json
  Report:             .migration/<feature>/validation/business-logic-validation-report.json
```

If `FAIL`: list each critical issue with its file path, evidence, and remediation step.
If `PASS_WITH_WARNINGS`: list warnings briefly; note they are non-blocking.

---

## Troubleshooting

- **Sub-agent fails or times out**: Re-spawn only that agent. Do not restart the wave.
- **BR batch file empty**: Re-spawn the br-validator for that batch with the same prompt.
- **Fingerprint missing**: Check `.migration/<feature>/validation/fingerprint.json`.
  If absent, ask the user to re-run `/validation` so the hook regenerates it.
