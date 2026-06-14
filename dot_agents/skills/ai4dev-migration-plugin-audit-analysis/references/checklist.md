# Analysis Audit Checklist

These are the 8 checks to run against `/analysis` output. Execute them in order. Each check has explicit pass/fail criteria.

---

## Check 1: Schema Compliance

**What**: Verify `analysis.json` exists, is valid JSON, and has all required fields per the schema.

**Steps**:

1. Read `.migration/<feature-name>/analysis/analysis.json`
2. Parse as JSON — must not throw
3. Verify required top-level fields: `feature_name` (string), `feature_description` (string), `business_rules` (array, min 1), `components` (array, min 1)
4. Verify optional arrays are present if claimed: `control_flows`, `entities`, `external_integrations`

**Pass criteria**: Valid JSON with all required fields present and correctly typed.

**Fail severity**: `critical` — downstream skills (architect) cannot consume malformed output.

---

## Check 2: Business Rule Integrity

**What**: Every business rule has valid structure, unique ID, and source evidence.

**Steps**:

1. For each business rule, verify:
   - `id` matches pattern `^BR[0-9]{3}$`
   - `summary` is non-empty
   - `type` is one of: validation, calculation, decision, transformation
   - `location` is non-empty and follows `file:line` format
   - `confidence` is one of: high, medium, low
2. Verify all IDs are unique (no duplicates)
3. Verify IDs are sequential (BR001, BR002, ...) with no gaps
4. Verify `related_rules` references all resolve to existing BR IDs

**Pass criteria**: All rules have valid structure, unique sequential IDs, and resolvable cross-references.

**Fail severity**: `critical` — broken IDs or cross-references cascade into architect and implementation.

---

## Check 3: Source Evidence Spot-Check

**What**: Randomly verify that file:line references in business rules point to real code.

**Steps**:

1. Select up to 5 random business rules (or all if fewer than 5)
2. For each, read the referenced source file at the claimed line
3. Verify the code at that location is plausibly related to the rule's summary
4. Record any mismatches: wrong file, wrong line, unrelated code

**Pass criteria**: At least 80% of spot-checked references point to relevant code.

**Fail severity**: `critical` — fabricated evidence makes the entire analysis unreliable.

---

## Check 4: Control Flow Completeness

**What**: Control flows have valid structure with proper business rule cross-references.

**Steps**:

1. For each control flow, verify:
   - `id` matches pattern `^CF[0-9]{3}$`
   - `name` and `trigger` are non-empty
   - `steps` is non-empty, each step has `order` and `action`
   - Steps are in sequential order (1, 2, 3, ...)
   - `business_rules` references in steps resolve to existing BR IDs
2. Verify `outcomes` is non-empty (at least one outcome per flow)

**Pass criteria**: All flows have valid structure with resolvable cross-references.

**Fail severity**: `warning` — control flows are valuable but not strictly required by downstream.

---

## Check 5: Pseudocode Presence

**What**: Business rules, control flows, and key methods have pseudocode.

**Steps**:

1. Count business rules with non-empty `pseudocode` field
2. Count control flows with non-empty `pseudocode` field
3. Count key methods (across all components) with non-empty `pseudocode` field
4. Calculate coverage percentages for each category

**Pass criteria**: At least 80% of business rules and control flows have pseudocode.

**Fail severity**: `warning` — pseudocode is the primary input for code generation, missing it degrades downstream quality.

---

## Check 6: Component Coverage

**What**: Components cover the plan scope and have meaningful content.

**Steps**:

1. Read plan.json to get `scope.include.paths`
2. For each component, verify:
   - `source` references a file within plan scope
   - `description` is non-empty and substantive (>20 chars)
   - `key_methods` has at least 1 entry
3. Check that business rules are distributed across components (not all assigned to one)
4. Verify `dependencies` descriptions explain "what for", not just names

**Pass criteria**: All components are within plan scope, have substantive descriptions, and business rules are reasonably distributed.

**Fail severity**: `warning` — thin components reduce value for architect.

---

## Check 7: Entity & Integration Consistency

**What**: Entities have business descriptions and integrations reference real components.

**Steps**:

1. For each entity, verify:
   - `description` explains business meaning (>20 chars)
   - `fields` has at least 1 entry with description
   - `relationships` targets reference other entities in the analysis
2. For each external integration, verify:
   - `used_by` references component names that exist in the `components` array
   - `protocol` is a valid enum value

**Pass criteria**: All entity relationships resolve and integration references are valid.

**Fail severity**: `warning` — broken references confuse downstream consumers.

---

## Check 8: Test Oracle Completeness

**What**: Every business rule has a structurally complete `test_oracle` and `test_coverage_summary` is consistent.

**Steps**:

1. For each business rule, verify:
   - `test_oracle` object is present
   - `test_oracle.existing_tests` is an array (may be empty)
   - `test_oracle.characterization_tests` is an array and is empty (`[]`)
   - `test_oracle.baseline` is an object with a `status` field
   - `baseline.status` is one of: `passed`, `failed`, `skipped`
   - If `baseline.status` is `passed` or `failed`, `tests_run` and `tests_passed` are present
   - Each entry in `existing_tests` has `location` (file:line format) and `assertion` (non-empty)
2. Verify `test_coverage_summary` exists at top level with all required fields:
   - `rules_with_existing_tests` (integer >= 0)
   - `rules_without_tests` (integer >= 0)
   - `characterization_tests_generated` (integer, must be 0)
   - `baseline_status` is one of: `passed`, `partial`, `failed`, `skipped`
3. Verify consistency:
   - `rules_with_existing_tests` + `rules_without_tests` == total BR count
   - `rules_with_existing_tests` == count of BRs where `existing_tests` is non-empty
   - `characterization_tests_generated` == 0

**Pass criteria**: All BRs have structurally valid `test_oracle`, summary is present and counts are consistent.

**Fail severity**: `warning` — missing test oracle degrades downstream test planning but does not block architecture.
