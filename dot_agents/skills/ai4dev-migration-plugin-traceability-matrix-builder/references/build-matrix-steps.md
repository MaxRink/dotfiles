# Build Traceability Matrix

Instructions for building `traceability-matrix.json` from migration artifacts.
Output schema: [traceability-matrix-schema.json](traceability-matrix-schema.json)

---

## Inputs

| Source | Fields to extract |
|---|---|
| `plan.json` | `feature` (name), `scope.include.paths`, `scope.exclude`, `scope.critical_components` |
| `analysis.json` | `business_rules[].id`, `.summary`, `.pseudocode`|
| `spec.json` | `traceability` object: keys = BR IDs, values with `functional_requirement`, `component`, `control_flow` |
| `functional-requirements.md` | Section 5 Traceability Matrix: `BR ID`, `Functional Requirement`, `Component`, `Control Flow` |

---

## Classify BRs

For each BR in `analysis.json`, test its `summary` and `pseudocode` against the scope fields (case-insensitive keyword or phrase match):

- **In scope** — any keyword or phrase from `scope.include.paths` matches, AND no keyword or phrase from `scope.exclude` matches.
- **Out of scope** — any keyword or phrase from `scope.exclude` matches. Add its `id` to `out_of_scope_brs`.
- **Ambiguous** — both sides match, or neither matches → treat as **in scope**, add a matrix-level issue:
  `{ br_id: <id>, severity: "warning", description: "BR scope membership ambiguous — included by default" }`.

Only in-scope BRs proceed further.

---

## Build Entries

For each in-scope BR, produce one entry:

| Field | Source |
|---|---|
| `br_id` | `analysis.json .business_rules[].id` |
| `summary` | `analysis.json .business_rules[].summary` |
| `pseudocode` | `analysis.json .business_rules[].pseudocode` |
| `requirement_id` | `spec.json traceability[br_id].functional_requirement`; `null` if key absent |
| `target_component` | `spec.json traceability[br_id].component`; `null` if key absent |
| `expected_test_areas` | derived — see below |
| `spec_coverage` | computed below |
| `issues` | computed below |

**If `spec.json traceability` key is absent entirely:** all in-scope BRs get `requirement_id: null`, `target_component: null`,
`expected_test_areas: []`, and add one matrix-level issue:
`{ br_id: null, severity: "critical", description: "spec.json traceability object is missing" }`.

---

## Derived Fields

### spec_coverage

| `requirement_id` | `target_component` | `spec_coverage` |
|---|---|---|
| not null | not null | `COMPLETE` |
| not null | null | `PARTIAL` |
| null | not null | `PARTIAL` |
| null | null | `MISSING` |

### expected_test_areas

For each in-scope BR, look up the row where `BR ID = br_id` in `functional-requirements.md` Section 5 Traceability Matrix:

- FR cell non-empty and not `-` → add `"unit"`
- CF cell non-empty and not `-` → add `"bdd"`

If the row is absent, or Section 5 is entirely absent, fall back to `analysis.json business_rules[].type`:

| BR type | `expected_test_areas` |
|---|---|
| `validation` | `["unit"]` |
| `calculation` | `["unit"]` |
| `decision` | `["unit", "bdd"]` |
| `transformation` | `["unit", "integration"]` |

---

### Per-entry issues

All rules are evaluated independently. Multiple issues may apply to one entry.

Record `evidence` and `remediation` on every issue at the point of detection.

| Condition | Severity | Description | Evidence | Remediation |
|---|---|---|---|---|
| `spec_coverage = MISSING` | `critical` | `"BR not mapped in spec.json traceability — no requirement or component assigned"` | `"spec.json traceability"` | `"Add an entry for <br_id> in spec.json traceability with functional_requirement and component"` |
| `spec_coverage = PARTIAL` and `requirement_id = null` | `warning` | `"BR has a component assigned but no requirement ID"` | `"spec.json traceability entry for <br_id>"` | `"Add a functional_requirement ID for <br_id> in spec.json traceability"` |
| `spec_coverage = PARTIAL` and `target_component = null` | `warning` | `"BR mapped to requirement but no component assigned — Phase 2 cannot locate implementation"` | `"spec.json traceability entry for <br_id>"` | `"Add a component for <br_id> in spec.json traceability"` |
| BR `summary`/`pseudocode` semantically matches a `scope.critical_components` entry (keyword or phrase match) and `spec_coverage != COMPLETE` | `critical` | `"BR covers a critical migration area ('<matched scope.critical_components value>') — incomplete traceability is not acceptable"` | `"plan.json scope.critical_components: '<matched value>'"` | `"Complete traceability for <br_id> in spec.json traceability before proceeding"` |

### artifact_coverage

```text
total_brs            = total entries in analysis.json business_rules[]
in_scope             = count of entries[] (excludes out_of_scope_brs)
fully_traced         = count where spec_coverage = COMPLETE
partially_traced     = count where spec_coverage = PARTIAL
untraced             = count where spec_coverage = MISSING
artifact_coverage_pct = (fully_traced / in_scope) * 100   [0 if in_scope = 0]
```

---

## Output

Write to `.migration/<feature>/validation/traceability-matrix.json`. The root object must include:

- `feature` — from `plan.json`
- `artifact_coverage` — counts and coverage_pct computed above
- `entries` — in-scope BR entries
- `out_of_scope_brs` — array of BR ID strings classified out-of-scope
- `issues` — matrix-level issues (ambiguous scope warnings, missing Section 8, etc.)

After writing, print:

```text
Traceability matrix built: <in_scope> in-scope BRs
  COMPLETE:  <fully_traced>
  PARTIAL:   <partially_traced>
  MISSING:   <untraced>
  Artifact coverage:  <artifact_coverage_pct>%
  Issues:    <total issue count>
```

If any `critical` issues exist, ask the user:

```text
Critical traceability gaps found. How do you want to proceed?
  [1] Continue — validate all BRs; MISSING entries will be marked unlocatable in Phase 2
  [2] Stop — fix documentation gaps in spec.json traceability first, then re-run
```

- If **[1]**: proceed to Phase 2. MISSING entries skip implementation search and carry their critical issues into the final report.
- If **[2]**: halt. Do not proceed to Phase 2.
