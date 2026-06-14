
# Validation Cross-Checks

Runs the checks specified in the prompt against the generated code and plan artifacts.
Two instances are spawned in parallel by the orchestrator:

- Instance A: Check 2 only
- Instance B: Checks 3, 4, and 5

## Inputs (from prompt)

- **Checks to run** — `"2"` or `"3-5"`
- **`code_gen_dir`** — root path of generated code
- **`tier`** — `small | medium | large`
- For Check 2 only: **`expected_components`** — JSON array of `target_component` values from the matrix
- For Checks 3–5 only: **`plan_path`** — path to `plan.json`

---

## Check 2: Reverse Traceability

Verify the generated code does not contain unnecessary business logic with no trace to the matrix.

**1 — Enumerate actual components**

Scan `code_gen_dir` for business logic components: services, handlers, processors, validators,
calculators. Exclude infrastructure — DTOs, repositories, config files, utilities, base classes.
Use grep-first: search for class/service declarations, then read selectively.

**2 — Flag untraced components**

For each discovered component NOT in `expected_components` (case-insensitive name match):
record a `warning` issue:
`"Component '<name>' has no corresponding entry in the traceability matrix — may be unnecessary or undocumented implementation"`

---

## Check 3: Risk Mitigation Validation

Read `risks[]` from `plan.json`. For each risk with a `mitigation` field:

**1 — Identify what to verify**

Extract the concrete technical action from the mitigation description.
If vague or non-technical (e.g. "schedule a meeting"): skip and record `info`:
`"Risk mitigation for '<risk>' is non-technical and cannot be verified in code"`

**2 — Search generated code** for evidence of the mitigation.

**3 — Assign result**

| Condition | Severity | Issue |
|---|---|---|
| Evidence found | — | No issue |
| Not found, `severity: high` | `critical` | `"High-severity risk mitigation not implemented: '<mitigation>'"` |
| Not found, `severity: medium` | `warning` | `"Medium-severity risk mitigation not implemented: '<mitigation>'"` |
| Not found, `severity: low` | `info` | `"Low-severity risk mitigation not implemented: '<mitigation>'"` |

---

## Check 4: Success Criteria Validation

Read `success_criteria[]` from `plan.json`. For each criterion, verify it is demonstrably
met in the generated code or test suite.

| Condition | Severity | Issue |
|---|---|---|
| Evidence found in code or tests | — | No issue |
| Not met | `critical` | `"Success criterion not met: '<criterion>'"` |

---

## Check 5: Constraints Preservation

Read `constraints.unchanged[]` and `constraints.integration.systems[]` from `plan.json`.

For each constraint:

**1 — Extract verifiable anchor** — interface name, file path convention, API method, protocol.
If no concrete anchor extractable: skip and record `info`:
`"Constraint cannot be verified in code: '<constraint>'"`

**2 — Search generated code** for the anchor.

**3 — Assign result**

| Condition | Severity | Issue |
|---|---|---|
| Anchor found and correctly used | — | No issue |
| Not found, exact identifier (class/method/endpoint) | `critical` | `"Constraint not preserved: '<constraint>'"` |
| Not found, structural pattern (naming/path convention) | `warning` | `"Constraint anchor not found — may be renamed: '<constraint>'"` |

---

## Output

**Check 2** → write to: `.migration/<feature>/validation/check-2-findings.json`

```json
{
  "check_2_reverse_traceability": {
    "issues": [ { "severity": "warning", "description": "...", "evidence": "..." } ]
  }
}
```

**Checks 3–5** → write to: `.migration/<feature>/validation/check-35-findings.json`

```json
{
  "check_3_risk_mitigation":    { "issues": [...] },
  "check_4_success_criteria":   { "issues": [...] },
  "check_5_constraints":        { "issues": [...] }
}
```

Write an empty `issues: []` array for checks with no findings — never omit a check key.

## Constraints

- **Read-only** — never modify any file in `code_gen_dir`, `.migration/`, or plan artifacts
- **Grep-first** — always search before reading files
- **Evidence-based** — every issue must cite `file/path:line` or artifact field path
