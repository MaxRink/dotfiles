---
name: ai4dev-migration-plugin-analysis
description: Extract business rules, control flows, and entities from source code scoped to the migration plan. Produces analysis.json consumed by /architect.
user-invocable: false
disable-model-invocation: true
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/migration-plugin/skills/analysis by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Analysis Skill

Extract business rules, control flows, and entities from source code scoped to the active feature's migration plan.
This is the most critical step — the quality of the analysis directly impacts every downstream skill.

## CRITICAL: Output Structure Enforcement

**The output MUST be valid JSON that passes `references/schema.json` validation. No exceptions.**

Common mistakes that cause HARD FAILURES:

- Adding `metadata`, `analysis_timestamp`, `analyzer`, `scope` wrapper objects at top level
- Using `category`/`name`/`description` on BRs instead of `type`/`summary`/`details`
- Using flat `source` string instead of `location` object with file/line_start/line_end/function/class
- Missing `test_oracle` on business rules
- Empty or missing `behavioral_contracts` and `edge_cases` arrays in test_oracle
- Missing `pseudocode` string field on business rules
- Missing top-level sections: `components`, `control_flows`, `entities`, `dependencies`, `test_coverage_summary`, `migration_notes`

**If you generate output that doesn't match the schema, the entire analysis phase fails and must be rerun.**

## Input Context

The `plan.json` and `docs/index.json` are injected by hooks into context — use them directly.
If hook injection failed, read them from:

- `.migration/<feature>/plan/plan.json`
- `.migration/docs/index.json`

**Hard stop** if `plan.json` is missing — cannot determine scope without it.

<prerequisites>

## Before Starting

If a prior audit report exists at `.migration/<feature>/analysis/audit-report.md`, read it first for remediation guidance.

Reference files are available in `references/` if you need schema details, but the agent already specifies the critical requirements.

</prerequisites>

<output-spec>

## Output

All files written to `.migration/<feature>/analysis/`.

```text
.migration/<feature>/analysis/
├── analysis.json                      # Primary output — business rules, control flows, entities, components
└── diagrams/
    ├── cf001-<flow-name>.mmd          # One flowchart per control flow
    ├── entity-relationships.mmd       # ER diagram of all entities
    └── component-dependencies.mmd    # Component dependency graph
```

</output-spec>

<workflow>

## Workflow

### Step 1 — Load Context

**MANDATORY FIRST ACTION: Read the schema files (use Read tool on each):**

1. Read `references/schema.json` — memorize the EXACT structure, field names, required properties
2. Read `references/examples/example-analysis.json` — this is your output template
3. Read `references/step-2b-test-oracle.md` — covers phases 3 and 4 (behavioral_contracts and edge_cases)

**After reading schema, verify you understand:**

- Top-level structure: `feature_name`, `feature_description`, `business_rules`, `components`, `control_flows`, `entities`, `dependencies`, `test_coverage_summary`, `migration_notes` (nothing else allowed)
- BR structure: `id`, `summary`, `type`, `location` (object), `confidence`, `details`, `pseudocode`, `related_rules`, `test_oracle`
- test_oracle structure: `type`, `location`, `test_methods`, `behavioral_contracts` (min 1), `edge_cases` (min 1)

**Then build context map from the injected data:**

1. From `plan.json`: extract `scope.include.paths`, `focus_areas`, `constraints`, `modules`
2. From `docs/index.json`: match plan scope paths against `file_index` to identify relevant module docs
3. Read each in-scope module doc from `.migration/docs/modules/<name>.md`
4. Read relevant cross-cutting docs (api-contracts, data-flow, database-schema, security) from `.migration/docs/cross-cutting/`

This gives full system context without re-scanning the codebase.

### Step 2 — Deep Source Analysis

Use module docs as a guide, then read actual source files for precision.

From module docs and plan scope, identify source files within `scope.include.paths`. Focus on: business logic, validation, decision points, data transformations, entity definitions.
Prioritize by `focus_areas` ranking — rank 1 gets deepest analysis.

**For large scopes (>10 source files)**: delegate per-module to sub-agents via Agent tool, then merge.
See the agent's Delegation Strategy for the full protocol — sub-agents return raw findings with placeholder labels, never BR/CF IDs.
ID assignment happens only during the orchestrator merge step.

### Step 2b — Generate Test Oracle for Each BR

For EVERY business rule, generate a `test_oracle` object:

1. **Derive behavioral_contracts** from the pseudocode you just wrote:
   - Each IF/ELSE branch → one GIVEN/WHEN/THEN contract
   - Minimum: 2 contracts (1 happy path, 1 failure case)
   - Format: `"GIVEN <precondition> WHEN <action> THEN <outcome>"`

2. **List edge_cases** from the code logic:
   - Boundary values (null, empty, max, min)
   - Concurrency scenarios
   - Error conditions
   - Minimum: 2 edge cases

3. **Set test metadata:**
   - If tests exist: `type: "unit-tests"`, `location: "path/to/test"`, `test_methods: ["testMethod"]`
   - If no tests: `type: "manual-integration"`, `location: "No tests found"`, `test_methods: []`

**Example:**

```json
{
  "test_oracle": {
    "type": "unit-tests",
    "location": "src/test/TokenServiceTest.java",
    "test_methods": ["testEncryptToken", "testDecryptToken"],
    "behavioral_contracts": [
      "GIVEN valid token WHEN encrypt THEN return Base64 encrypted string",
      "GIVEN encrypted token WHEN decrypt THEN return original plaintext"
    ],
    "edge_cases": ["Null token throws exception", "Empty string handled correctly"]
  }
}
```

### Step 3 — Extract & Structure

- **Business rule IDs** (`BR001`, `BR002`, ...): every rule MUST have a `location` object with `{file, line_start, line_end, function, class}` and `confidence` rating
- **Control flow IDs** (`CF001`, `CF002`, ...): with `entry_point` object `{component, function, line}` and steps containing
  `{step, action, component, function, decision}`. Include `business_rules` array, `affected_by_migration` boolean, and `migration_impact` string
- **Pseudocode**: language-agnostic pseudocode for every business rule — 100% coverage required. Must include function signatures, all branches, error handling, constants
- **Entities**: describe with `name`, `description`, `attributes[]` (name/type/description), `storage_location`, and `related_rules[]`
- **Components**: include `path`, `functions[]` with line ranges, `dependencies[]` as strings, and `business_rules[]` BR IDs
- **Dependencies**: top-level `dependencies` object with `internal[]` (from/to/type/description) and `external[]` (name/type/description/affected_components)
- **Migration notes**: top-level `migration_notes` object with `primary_changes`, `preserved_behavior`, `testing_strategy`, `rollback_plan`

**Pre-write validation** — verify these 5 critical checks before writing:

1. **Every BR has test_oracle:** Loop through business_rules array, verify each has `test_oracle` object
2. **Every test_oracle has behavioral_contracts:** Verify `test_oracle.behavioral_contracts` is non-empty array (min 1 entry)
3. **Every test_oracle has edge_cases:** Verify `test_oracle.edge_cases` is non-empty array (min 1 entry)
4. **Top-level structure correct:** Has `feature_name`, `business_rules`, `components` (NO `metadata` wrapper)
5. **BR field names correct:** Uses `summary`/`type`/`details`, NOT `name`/`category`/`description`

**If any check fails: Fix before writing.**

### Step 4 — Generate Diagrams

Delegate diagram creation to the `mermaid-diagram-creator` agent via the Agent tool.
Provide: the extracted entities, control flows, and components from Step 3.

Required diagrams:

1. One flowchart per control flow — steps, decision points, outcomes
2. One ER diagram — all entities and their relationships
3. One component dependency diagram — components and their dependencies

Output directory: `.migration/<feature>/analysis/diagrams/`

</workflow>

<constraints>

## Constraints

- **Evidence-based** — every business rule MUST have a location object pointing to real source
- **Plan-scoped** — only analyze files within `scope.include.paths`
- **Schema-compliant** — output must conform EXACTLY to `references/schema.json`. The schema uses `additionalProperties: false` — no extra fields allowed anywhere
- **No speculation** — extract what exists; do not recommend changes or speculate about intent
- **No timestamps or metadata wrappers** — no `analysis_timestamp`, `project_info`, `metadata`, `analyzer`, `scope` objects
- **Single output file** — only `analysis.json` plus diagrams; do not split by module

### FORBIDDEN fields and patterns (DO NOT include these):

The following are common mistakes — the output MUST NOT contain any of these:

**Top-level:**

- NO `metadata` wrapper object — use flat `feature_name` and `feature_description` directly at root
- NO `analysis_date`, `analysis_timestamp`, `project_name`, `source_stack`, `target_stack`, `analyzer`, `scope`, `migration_type`
- NO `implementation`, `rationale`, `impact` fields on business rules

**Business rules:**

- NO `name` — use `summary` instead
- NO `description` as the detail field — use `details` instead
- NO `category` — use `type` instead
- NO `priority`, `source`, `logic`, `constraints` fields
- MUST use `location` object (with `file`, `line_start`, `line_end`, `function`, `class`) — not a flat `source` string
- MUST have `pseudocode` as a string field — not as an array of method objects

**Components:**

- NO `id` field on components
- NO `file_path` — use `path` instead
- NO `language`, `responsibilities`, `complexity_metrics`
- NO `pseudocode` on components — pseudocode belongs only in business_rules
- MUST use `functions` array (with `name`, `line_start`, `line_end`, `returns`, `description`)
- MUST use `business_rules` array of BR IDs this component owns

**Control flows:**

- NO `name`, `description` as separate fields — use `summary` for the description
- NO `trigger` as a string — use `entry_point` object (with `component`, `function`, `line`)
- NO `related_business_rules` — use `business_rules` array of BR IDs
- Steps MUST have: `step`, `action`, `component`, `function`, `decision`
- Steps must NOT use: `source`, `outcomes`, `command`, `condition`
- MUST include: `affected_by_migration` (boolean) and `migration_impact` (string)

**Entities:**

- NO `id`, `type`, `source`, `file_path` fields
- NO `fields` — use `attributes` array (with `name`, `type`, `description`)
- NO `relationships`, `methods`, `usage`, `confidence` fields
- MUST use: `name`, `description`, `attributes`, `storage_location`, `related_rules`

**Test coverage summary:**

- NO `total_business_rules`, `rules_with_tests`, `rules_without_tests`, `test_types`, `critical_gaps`
- NO `total_rules`, `rules_with_unit_tests`, `rules_with_integration_tests`, `baseline_status`
- MUST use: `total_tests`, `coverage_percentage`, `test_framework`, `test_command`, `tests_by_module`, `critical_test_gaps`, `recommended_test_additions`

**Top-level REQUIRED sections (schema-enforced):**

- MUST include `dependencies` object with `internal` and `external` arrays
- MUST include `migration_notes` object with `primary_changes`, `preserved_behavior`, `testing_strategy`, `rollback_plan`
- MUST include `test_coverage_summary` with `total_tests`, `tests_by_module`, `critical_test_gaps`

</constraints>

## Completion

After `analysis.json` and all diagrams are written and all 7 pre-write validation checks pass, report completion to the main conversation:

```text
Analysis complete for <feature-name>.
Output: .migration/<feature-name>/analysis/analysis.json
Business rules: <N>, Control flows: <N>, Entities: <N>, Components: <N>
Test coverage: <M>/<N> BRs with existing tests
```
