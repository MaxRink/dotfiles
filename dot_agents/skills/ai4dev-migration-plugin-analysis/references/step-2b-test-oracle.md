# Step 2b — Test Oracle Discovery

Discover existing test coverage for every business rule identified in Step 2. This captures test evidence already present in the codebase and derives behavioral contracts and edge cases.

**Every BR MUST have a `test_oracle` object when analysis is complete** with this exact structure:

```json
"test_oracle": {
  "type": "unit-tests",
  "location": "path/to/TestFile.java",
  "test_methods": ["testMethod1", "testMethod2"],
  "behavioral_contracts": [
    "GIVEN precondition WHEN action THEN expected outcome"
  ],
  "edge_cases": [
    "Description of a boundary condition or unusual input"
  ]
}
```

BRs without existing tests get: `"type": "manual-integration"`, `"location": "No tests found"`, `"test_methods": []` — but STILL require `behavioral_contracts` and `edge_cases`.

## Overview

Five phases, executed in order:

1. **Phase 1**: Discover existing tests in the legacy codebase
2. **Phase 2**: Run baseline execution (when `test_command` exists)
3. **Phase 3**: Derive behavioral contracts per BR (REQUIRED)
4. **Phase 4**: Identify edge cases per BR (REQUIRED)
5. **Phase 5**: Compute `test_coverage_summary`

**Key rule:** This step performs discovery only — no test files are generated.

---

## Phase 1 — Discover Existing Tests

For each business rule's owning component (class/module from Step 2), find tests that exercise it.

### 1.1 Glob for test files within plan scope

Use these patterns to find test files:

```text
# Java / Kotlin
**/src/test/**/*Test.java
**/src/test/**/*Tests.java
**/src/test/**/*Spec.java
**/src/test/**/*IT.java
**/src/test/**/*Test.kt

# Python
**/tests/**/*.py
**/test/**/*.py
**/*_test.py
**/test_*.py

# JavaScript / TypeScript
**/__tests__/**/*.{js,ts,tsx}
**/*.test.{js,ts,tsx}
**/*.spec.{js,ts,tsx}

# General
**/spec/**/*
**/test*/**/*
```

Collect the full list of test files. This is a one-time scan — reuse the list across all BRs.

### 1.2 Match tests to components

For each BR, take the owning component name (e.g., `OrderValidator`) and key method name (e.g., `validateOrder`):

1. Grep the test file list for the component name (class/module name)
2. Grep hits for the method name to narrow further
3. Read each matched test method to confirm it actually exercises the BR's logic

**Example grep strategy:**

```bash
# Find tests referencing OrderValidator
grep -l "OrderValidator" <test-files>

# Within those, find tests referencing validateOrder
grep -n "validateOrder" <matched-files>
```

### 1.3 Record in `test_oracle`

For each confirmed test hit, extract:

- **test method names**: The actual method names of tests that cover this BR
- **test type**: Classify as `unit-tests`, `integration-required`, or `manual-integration`
- **test file location**: Path to the test file

**Output format (per BR):**

```json
{
  "type": "unit-tests",
  "location": "src/test/java/com/example/OrderValidatorTest.java",
  "test_methods": [
    "testValidateOrder_NegativeQuantity_Rejected",
    "testValidateOrder_ValidOrder_Accepted"
  ],
  "behavioral_contracts": [],
  "edge_cases": []
}
```

(behavioral_contracts and edge_cases are populated in Phases 3 and 4 below)

**If no tests found:**

```json
{
  "type": "manual-integration",
  "location": "No tests found for this BR",
  "test_methods": [],
  "behavioral_contracts": [],
  "edge_cases": []
}
```

### 1.4 How to classify test_oracle.type

| Signal | `test_oracle.type` value |
|--------|------|
| `@Test` in `src/test/unit/`, no DB/HTTP setup, mocked deps | `"unit-tests"` |
| `@SpringBootTest`, `@DataJpaTest`, testcontainers, HTTP client | `"integration-required"` |
| No tests found for this BR | `"manual-integration"` |
| Configuration-only logic (bean definitions, properties) | `"configuration-validation"` |

When ambiguous, default to `"integration-required"`.

---

## Phase 2 — Run Baseline Execution

**Precondition:** `plan.json` has `source_stack.test_command` set to a non-null value.

If `test_command` is null or missing, skip to Phase 3. (Baseline results are informational only — they don't affect the test_oracle structure.)

### 2.1 Execute the test suite

Run the test command using the Bash tool:

```bash
cd <project-root> && <test_command>
```

Capture stdout/stderr and the exit code.

### 2.2 Parse results

- Exit code 0 → all tests passed
- Non-zero exit code → some or all tests failed
- Parse test runner output for pass/fail counts if available

### 2.3 Update per-BR baselines

For each BR with `existing_tests` populated:

- If associated tests passed: `{ "status": "passed", "tests_run": N, "tests_passed": N }`
- If associated tests failed: `{ "status": "failed", "tests_run": N, "tests_passed": M, "reason": "<failure message>" }`

For BRs without existing tests:

- `{ "status": "skipped", "reason": "No existing tests found for this BR" }`

---

## Phase 3 — Derive Behavioral Contracts

For each BR, write GIVEN/WHEN/THEN contracts that describe what the rule asserts. These are testable statements that downstream code generation and test generation can target directly.

### 3.1 Sources for contracts

Derive contracts from (in priority order):

1. **Existing test assertions** — translate assert statements into GIVEN/WHEN/THEN format
2. **Pseudocode logic** — each branch/condition in the BR's pseudocode implies a contract
3. **Details field** — explicit behavior described in prose

### 3.2 Contract format

Each contract MUST follow this structure:

```text
GIVEN <precondition> WHEN <action> THEN <expected outcome>
```

Examples:

- `GIVEN a user with 4 failed attempts WHEN login fails THEN account status is set to LOCKED`
- `GIVEN null input WHEN encrypt() called THEN throws SecurityException`
- `GIVEN valid session WHEN idle for 31 minutes THEN session is rejected`

### 3.3 Minimum coverage

Every BR MUST have at least one behavioral contract. Aim for:

- 1 happy-path contract (normal success case)
- 1+ failure/rejection contracts (what causes the rule to reject/fail)
- 1 boundary contract where applicable (at-the-limit values)

**Output:** populate `test_oracle.behavioral_contracts` array (strings).

---

## Phase 4 — Identify Edge Cases

For each BR, list boundary conditions and unusual inputs that could trigger unexpected behavior.

### 4.1 Edge case categories

Consider these categories for each BR:

| Category | Examples |
|----------|----------|
| **Null/empty** | Null input, empty string, empty collection |
| **Boundary** | Exactly at threshold, off-by-one, max/min values |
| **Concurrency** | Simultaneous operations, race conditions |
| **Encoding** | Unicode, special characters, very long strings |
| **Infrastructure** | Database failure, network timeout, disk full |
| **State** | Already in target state, impossible state transitions |

### 4.2 Minimum coverage

Every BR MUST have at least one edge case. Focus on cases that are:

- Likely to cause bugs during migration (different runtime behavior)
- Not already covered by existing tests
- Relevant to the BR's type (validation → invalid inputs, calculation → overflow, decision → boundary values)

**Output:** populate `test_oracle.edge_cases` array (strings).

---

## Phase 5 — Compute `test_coverage_summary`

Count across all test files and produce the top-level summary:

```json
{
  "test_coverage_summary": {
    "total_tests": <total number of test methods found>,
    "coverage_percentage": <estimated coverage 0-100>,
    "test_framework": "<framework name and version, e.g. JUnit 5.11.4 + Mockito 5.12.0>",
    "test_command": "<command to run tests, e.g. ./gradlew test>",
    "tests_by_module": [
      {
        "module": "<module/layer name>",
        "test_count": <number of test files>,
        "test_files": ["TestFile1.java", "TestFile2.java"],
        "coverage_notes": "<assessment of coverage and gaps for this module>"
      }
    ],
    "critical_test_gaps": [
      {
        "component": "<component with gap>",
        "gap": "<what's missing>",
        "risk": "<risk level and explanation>"
      }
    ],
    "recommended_test_additions": [
      "<recommended test to add for migration safety>"
    ]
  }
}
```

**How to determine values:**

- `total_tests` — count all test methods discovered in Phase 1
- `coverage_percentage` — estimate based on BRs with unit tests vs total BRs
- `test_framework` — identify from build files (pom.xml, build.gradle, package.json)
- `test_command` — from `plan.json` `source_stack.test_command` or derive from build tool
- `tests_by_module` — group test files by logical module/layer
- `critical_test_gaps` — identify components without tests, especially migration targets
- `recommended_test_additions` — specific tests needed for migration safety

---

## Anti-patterns

- **DO NOT** generate characterization test files to disk
- **DO NOT** create directories under the test directory
- **DO NOT** write any files other than `analysis.json`
- **DO NOT** skip Phase 2 when `test_command` is available — always attempt execution
