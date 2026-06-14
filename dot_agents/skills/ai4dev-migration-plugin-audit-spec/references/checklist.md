# Audit Specification Checklist

Validation checklist for spec-specification output. All checks must pass for
PASS verdict.

---

## Check 1 — File Completeness

**Objective:** Verify all required specification files exist and are non-empty.

**Validation Steps:**

1. Verify `.migration/<feature>/spec-specification/contracts.md` exists and has content
2. Verify `.migration/<feature>/spec-specification/functional-requirements.md` exists and has content
3. Verify `.migration/<feature>/spec-specification/nonfunctional-requirements.md` exists and has content
4. Verify `.migration/<feature>/spec-specification/technical-plan.md` exists and has content

**Pass Criteria:** All four files exist and have > 100 characters

**Fail Criteria:** Any file missing or empty

**Severity if Fail:** Critical

**Remediation:** Re-run `/spec-specification <feature>` to generate missing files

---

## Check 2 — Business Rule Coverage

**Objective:** Every BR ID from analysis.json must appear in functional-requirements.md

**Validation Steps:**

1. Read `.migration/<feature>/analysis/analysis.json` and extract all BR IDs
   from `business_rules[]` array
2. Read `functional-requirements.md` and extract all BR ID references
3. Compare: every BR ID from analysis must appear at least once in
   functional-requirements.md
4. Check that each BR has a functional requirement (FR-NNN) associated with it

**Pass Criteria:** 100% of BR IDs from analysis.json are referenced in
functional-requirements.md

**Fail Criteria:** One or more BR IDs are missing from
functional-requirements.md

**Severity if Fail:** Critical

**Remediation:** Regenerate functional-requirements.md to include missing BR IDs

**Evidence Format:**

```text
Missing BR IDs: BR001, BR015, BR023
Coverage: 47/50 (94%)
```

---

## Check 3 — Component Coverage

**Objective:** Every component from architect target-architecture.md must have
a detailed specification in technical-plan.md

**Validation Steps:**

1. Read `.migration/<feature>/architect/target-architecture.md` Section 3
   (Component Design) and extract all component names
2. Read `technical-plan.md` Section 3 (Component Specifications) and extract
   all component specs
3. Compare: every component from architect must have a corresponding section
   in technical-plan.md
4. Verify each component spec includes: Responsibility, API Surface,
   Dependencies, Technology Stack, Business Rules, Testing Requirements

**Pass Criteria:** 100% of components from architect have detailed specs in
technical-plan.md

**Fail Criteria:** One or more components missing or incomplete specs

**Severity if Fail:** Critical

**Remediation:** Regenerate technical-plan.md to include missing component
specifications

**Evidence Format:**

```text
Missing components: UserService, PaymentGateway
Incomplete specs (missing required fields): OrderService
Coverage: 8/10 (80%)
```

---

## Check 4 — Contract Completeness

**Objective:** Every external system from plan.json constraints and architect
integration design must have a contract specification

**Validation Steps:**

1. Read `.migration/<feature>/plan/plan.json` and extract
   `constraints.integration.systems[]`
2. Read `.migration/<feature>/architect/target-architecture.md` Section 5
   (Integration Design) and extract external system names
3. Read `contracts.md` and verify each system has a contract specification
4. For each contract, verify it includes: Endpoint/Topic, Request/Message
   Schema, Response Schema, Error Handling, Authentication

**Pass Criteria:** All external systems have complete contract specifications

**Fail Criteria:** One or more systems missing or have incomplete contracts

**Severity if Fail:** Critical

**Remediation:** Regenerate contracts.md to include missing or incomplete contracts

**Evidence Format:**

```text
Missing contracts: PaymentAPI, NotificationService
Incomplete contracts (missing schema): LegacyDB
Coverage: 5/7 (71%)
```

---

## Check 5 — Technology Stack Fidelity

**Objective:** Technology choices in technical-plan.md must exactly match
plan.json target_stack

**Validation Steps:**

1. Read `.migration/<feature>/plan/plan.json` and extract `target_stack`
   (language, framework, database, etc.)
2. Read `technical-plan.md` Section 1.3 (Technology Stack) and extract all
   technology choices
3. Compare: technologies in technical-plan must match plan.json exactly
   (no substitutions)
4. Check versions match if specified in plan.json

**Pass Criteria:** 100% match between plan.json target_stack and
technical-plan.md technologies

**Fail Criteria:** Any technology mismatch or substitution

**Severity if Fail:** Critical

**Remediation:** Regenerate technical-plan.md using exact technologies from plan.json

**Evidence Format:**

```text
Mismatches:
  plan.json: Java 17 + Spring Boot 3.1
  technical-plan.md: Java 21 + Spring Boot 3.2 (MISMATCH)
```

---

## Check 6 — NFR Coverage

**Objective:** All focus areas from plan.json must have corresponding NFRs
in nonfunctional-requirements.md

**Validation Steps:**

1. Read `.migration/<feature>/plan/plan.json` and extract `focus_areas[]`
   (e.g., performance, security, reliability)
2. Read `nonfunctional-requirements.md` and extract all NFR categories
3. Verify each focus area has at least one NFR
4. Verify each NFR has a specific, measurable target metric

**Pass Criteria:** All focus areas have NFRs with measurable metrics

**Fail Criteria:** One or more focus areas missing NFRs or NFRs lack metrics

**Severity if Fail:** Warning (if focus area priority > 3), Critical (if
priority ≤ 3)
gfjg
**Remediation:** Regenerate nonfunctional-requirements.md to cover missing
focus areas

**Evidence Format:**

```text
Missing NFR coverage: scalability (priority 2)
NFRs without metrics: NFR-R003, NFR-P005
```

---

## Check 7 — Gap Documentation

**Objective:** All gaps from gap-analysis/gaps.json must be documented in
specifications

**Validation Steps:**

1. Read `.migration/<feature>/gap-analysis/gaps.json` and extract all gaps
2. Read `nonfunctional-requirements.md` Section 6 (Known Gaps) and
   `functional-requirements.md` for gap references
3. Verify every gap with severity "high" or "medium" is documented
4. Verify mitigation strategy or acceptance decision is documented for each
   gap

**Pass Criteria:** All high/medium severity gaps are documented with
mitigation or acceptance

**Fail Criteria:** One or more high/medium gaps missing from
specifications

**Severity if Fail:** Critical (for high severity gaps), Warning (for medium
severity gaps)

**Remediation:** Regenerate affected spec files to document missing gaps

**Evidence Format:**

```text
Missing gaps: GAP-003 (high), GAP-007 (medium)
Gaps without mitigation: GAP-012
Coverage: 12/15 (80%)
```

---

## Check 8 — Edge Case Coverage

**Objective:** Complex business rules (confidence < 0.8 or pseudocode > 10
lines) must have edge cases documented

**Validation Steps:**

1. Read `.migration/<feature>/analysis/analysis.json` and identify complex
   business rules (confidence < 0.8 or pseudocode line count > 10)
2. Read `functional-requirements.md` and verify each complex BR has an
   "Edge Cases" section
3. Verify edge cases describe specific scenarios and expected behaviors

**Pass Criteria:** All complex BRs have documented edge cases with expected
behaviors

**Fail Criteria:** One or more complex BRs missing edge cases

**Severity if Fail:** Warning

**Remediation:** Regenerate functional-requirements.md to add edge cases for
complex rules

**Evidence Format:**

```text
Complex BRs missing edge cases: BR005, BR018, BR032
Coverage: 8/11 (73%)
```

---

## Check 9 — Traceability Matrix Completeness

**Objective:** Traceability matrix in functional-requirements.md must map all
BRs to components and tests

**Validation Steps:**

1. Read `functional-requirements.md` and locate the Traceability Matrix section
2. Verify every BR ID from analysis.json appears in the matrix
3. Verify each BR maps to: Functional Requirement ID, Component Name,
   Control Flow (if applicable)
4. Verify no orphaned BRs (every BR must be assigned to exactly one
   component)

**Pass Criteria:** Traceability matrix is complete and consistent

**Fail Criteria:** Missing BRs, orphaned BRs, or inconsistent mappings

**Severity if Fail:** Critical

**Remediation:** Regenerate functional-requirements.md to fix traceability
matrix

**Evidence Format:**

```text
Missing from matrix: BR008, BR019
Orphaned BRs (no component): BR023
Duplicate assignments: BR015 assigned to both ComponentA and ComponentB
```

---

## Check 10 — Acceptance Criteria Quality

**Objective:** All functional requirements must have specific, testable
acceptance criteria

**Validation Steps:**

1. Read `functional-requirements.md` and extract all functional requirements
2. For each FR, verify it has an "Acceptance Criteria" section
3. Check that criteria are specific (no vague terms like "fast", "reliable")
4. Check that criteria are testable (can be verified through automated or
   manual tests)
5. Verify at least 2 acceptance criteria per FR

**Pass Criteria:** All FRs have ≥ 2 specific, testable acceptance
criteria

**Fail Criteria:** One or more FRs with vague, untestable, or missing
criteria

**Severity if Fail:** Warning

**Remediation:** Regenerate functional-requirements.md to improve acceptance
criteria quality

**Evidence Format:**

```text
FRs with vague criteria: FR-012 ("system should be fast"), FR-025 ("data
must be secure")
FRs with < 2 criteria: FR-008, FR-019
FRs missing criteria: FR-033
```

---

## Check 11 — Validation Rules Completeness

**Objective:** All functional requirements that validate input must have
detailed validation rules

**Validation Steps:**

1. Read `functional-requirements.md` and identify all FRs that involve input
   validation (e.g., validate email, validate amount, validate date format)
2. For each validation FR, verify it has a "Validation Rules" section
3. Check that validation rules include:
   - Format specification (standard name or description)
   - Regex pattern (if applicable)
   - Min/Max constraints (if applicable)
   - Allowed values (if applicable)
   - Error code to return on validation failure
   - At least one example of valid input
   - At least one example of invalid input with expected error
4. Verify rules are specific enough for code generation (no vague terms like
   "valid format")

**Pass Criteria:** All validation FRs have complete validation rules with
regex/format, examples, and error codes

**Fail Criteria:** One or more validation FRs missing validation rules or
have incomplete rules

**Severity if Fail:** Critical

**Remediation:** Regenerate functional-requirements.md to add complete
validation rules for all validation FRs

**Evidence Format:**

```text
FRs missing validation rules: FR-005, FR-012, FR-018
FRs with incomplete validation (missing regex): FR-007, FR-023
FRs missing valid/invalid examples: FR-009, FR-015
FRs missing error codes: FR-011
Coverage: 12/18 validation FRs complete (67%)
```

---

## Check 12 — Formula Completeness

**Objective:** All functional requirements that perform calculations must
have detailed formulas

**Validation Steps:**

1. Read `functional-requirements.md` and identify all FRs that involve
   calculations (e.g., calculate fee, compute total, calculate date)
2. For each calculation FR, verify it has a "Formula" section
3. Check that formula includes:
   - Mathematical expression with clear variable names
   - Precision specification (decimal places, rounding strategy)
   - Units (currency code, measurement unit)
   - All constants with their values
   - Worked example with actual numbers showing step-by-step
     computation
4. Verify formula is unambiguous and ready for code generation

**Pass Criteria:** All calculation FRs have complete formulas with
expression, precision, units, constants, and examples

**Fail Criteria:** One or more calculation FRs missing formulas or have
incomplete formulas

**Severity if Fail:** Critical

**Remediation:** Regenerate functional-requirements.md to add complete
formulas for all calculation FRs

**Evidence Format:**

```text
FRs missing formulas: FR-008, FR-014, FR-021
FRs with incomplete formulas (missing precision): FR-010, FR-019
FRs missing constants: FR-016
FRs missing worked examples: FR-012, FR-020
Coverage: 8/12 calculation FRs complete (67%)
```

---

## Summary Report Format

After all checks, generate a summary:

```markdown
# Specification Audit Report

**Feature:** <feature-name>
**Generated:** <timestamp>
**Verdict:** PASS | PASS_WITH_WARNINGS | FAIL

## Summary

- Checks passed: N/12
- Critical issues: N
- Warnings: N

## Checks

### Check 1: File Completeness — PASS/FAIL
{Details and evidence if FAIL}


### Check 2: Business Rule Coverage — PASS/FAIL
{Details and evidence if FAIL}

... (all 12 checks)

## Critical Issues

1. {Issue description} — {Remediation}
2. ...

## Warnings

1. {Warning description} — {Remediation}
2. ...

## Recommendations

{Overall recommendations for improving spec quality}

## Next Steps

- If PASS: Proceed to /code-generation <feature>
- If PASS_WITH_WARNINGS: Address warnings, then proceed to /code-generation
- If FAIL: Address critical issues, then re-run /spec-specification <feature>
```
