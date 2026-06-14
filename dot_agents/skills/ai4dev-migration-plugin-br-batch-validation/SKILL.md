---
name: ai4dev-migration-plugin-br-batch-validation
description: Locates each BR's implementation in generated code, verifies logic against pseudocode, and finds test evidence. Writes findings to a temp batch file.
user-invocable: false
disable-model-invocation: false
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/migration-plugin/skills/br-batch-validation by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# BR Batch Validation

Validates a batch of business rules against the generated code. Receives BR entries
from the orchestrator prompt — does not read `traceability-matrix.json` directly.

## Inputs (from prompt)

- **BR entries** — JSON array of entries: `br_id`, `summary`, `pseudocode`,
  `target_component`, `expected_test_areas`, `spec_coverage`
- **`code_gen_dir`** — root path of generated code
- **`tier`** — `small | medium | large` (informs grep-first vs full-read strategy)
- **`component_path_hints`** — JSON object: `{ "ComponentName": "path/hint" }` (may be partial)
- **Batch index N** — used in the output filename

## Workflow

For each BR entry in the batch:

### 1 — Skip MISSING entries

If `spec_coverage = "MISSING"`: write entry with `implementation_status: "MISSING"`,
carry any existing issues forward, skip steps 2–5.

### 2 — Locate implementation

Use `component_path_hints` to narrow the search if a hint exists for `target_component`.
If no hint: search across the full `code_gen_dir`.

Search order:

1. Grep for the literal BR ID in comments (`// BR001`, `# BR001`, `/* BR001 */`) → `comment_reference`
2. If not found: use key terms from `pseudocode` to locate matching logic → `logic_match`

Record `found: true/false`, `file`, `line`, `evidence_type`.

### 3 — Verify implementation logic

Required when implementation was found. Using `pseudocode` as the authoritative reference, verify:

- Same business conditions enforced (guards, validations, decision points)
- Same business outcome produced (calculation, transformation, state change)
- Edge cases described in `pseudocode` are handled

If implementation diverges: record a `critical` issue describing the behavioral gap.

### 4 — Find test evidence

Use `expected_test_areas` to target the search:

- `"bdd"` → search `features/**/*.feature` for `@BR<id-number>` tags
- `"unit"` → search unit test files for the literal BR ID in comments or test names
- `"integration"` → search integration test files for the literal BR ID

For each expected type with no match, record a `warning`:
`"Expected <type> test not found for <br_id>"`

Record `found: true/false` and matching `references` as `file:line`.

### 5 — Assign status

| Implementation | Logic verified | Test evidence | `implementation_status` |
|---|---|---|---|
| found | yes | found | `IMPLEMENTED` |
| found | yes | not found | `PARTIAL` |
| not found | — | found | `PARTIAL` |
| not found | — | not found | `MISSING` |

### 6 — Apply risk-based severity escalation

For entries where `implementation_status != "IMPLEMENTED"`:
perform a case-insensitive keyword match between the BR's `summary`/`pseudocode`
and each `risk.description` from `plan.json` (read plan.json once for the batch).
If matched and `risk.severity: "high"`: escalate all `warning` issues on that entry to `critical`.

## Output

Write to: `.migration/<feature>/validation/br-batch-<N>.json`

```json
{
  "batch": <N>,
  "entries": [
    {
      "br_id": "BR001",
      "implementation_evidence": { "found": true, "file": "...", "line": 42, "evidence_type": "comment_reference" },
      "logic_verified": true,
      "test_evidence": { "found": true, "references": ["src/test/...:88"] },
      "implementation_status": "IMPLEMENTED",
      "issues": []
    }
  ]
}
```

## Constraints

- **Read-only** — never modify any file in `code_gen_dir` or `.migration/`
- **Grep-first** — always search before reading files
- **Write once** — produce the batch file at the end, not incrementally
