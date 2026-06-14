---
name: ai4dev-migration-plugin-architecture-validation
description: Validate generated code against target architecture. Requires target-architecture.md and generated code.
user-invocable: false
disable-model-invocation: false
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/migration-plugin/skills/architecture-validation by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Architecture Validation Skill

Read target architecture and validate generated code against it. Checks the evidence of the implementation for each part of the target architecture,
and produces a report of any discrepancies or issues found.

<prerequisites>

## Before Starting — Load References

**Feature name**: use `$ARGUMENTS` if provided; otherwise read from `.migration/migration.json` (`active_feature`).

Read these reference files:

- [references/report-schema.json](references/report-schema.json) — JSON schema the validation report must conform to

Then read the required artifacts for the feature:

- `.migration/<feature>/architect/target-architecture.md`

The generated code to validate should already be in the agent memory, produced by the code generation agent workflow. If any of these a

**Hard stop** if any artifact is missing — list the missing files and the skill that produces each one.

</prerequisites>

<output-spec>

## Output

All files written to `.migration/<feature>/validation/`.

```text
.migration/<feature>/validation/
└── architecture-validation-report.json
```

**Status rules:**

| Field | PASS | PASS_WITH_WARNINGS | FAIL |
|---|---|---|---|
| `overall_status` | no critical issues found across all steps | no critical issues, at least one warning present | any critical issue found |
| per-step `status` | all verifiable items confirmed in code | one or more items unverifiable or partially implemented | one or more items absent or incorrectly implemented |

All issues must appear in the top-level `issues` array with `step`, `severity`, `evidence`, and `remediation` fields.

</output-spec>

<workflow>

## Workflow

### Step 1: Executive Summary check

- read `target-architecture.md` Executive Summary section
- check the generated code for evidence of the stated architectural style and key decisions:
  - verify that **Migration goal** implemented in the code
  - verify that **Architectural style** is reflected in the code structure and design patterns used
  - verify that **Key architectural decisions** are implemented in the code

| Condition | Severity |
|---|---|
| Migration goal not implemented | `critical` |
| Architectural style not reflected in code structure | `critical` |
| A key architectural decision absent from code | `warning` |

### Step 2: Architecture Overview check

- read `target-architecture.md` Architecture Overview section
- check the generated code for evidence:
  - verify that new application corresponds the **Chosen Style**
  - verify **High-Level Component Structure** is implemented in the codebase
  - verify **Communication Patterns** are implemented in the codebase

| Condition | Severity |
|---|---|
| Chosen style not reflected in code structure | `critical` |
| A component from High-Level Component Structure entirely absent | `critical` |
| A communication pattern not implemented | `warning` |

### Step 3: Component Design check

For each component listed in this section of `target-architecture.md` verify:

- **Responsibility** reflected in the code
- **Business Rules Owned** implemented - the business rules separately checked in
  business-logic-validation, here just verify that there is a reference to the business rules in the code.
  If no just inform about it in the report
- **API Surface** implemented in the codebase, and used by other components as described
- **Dependencies** reflected in the codebase
- **Technology Recommendation** fully considered in the implementation

| Condition | Severity |
|---|---|
| Component entirely absent from codebase | `critical` |
| API Surface endpoint missing | `warning` |
| Declared dependency not present in code | `warning` |
| Technology recommendation not followed | `warning` |
| Business rule reference absent from code | `info` |

### Step 4: Data Architecture check

- read `target-architecture.md` Data Architecture section
- verify **Storage Strategy** is reflected in the code:
  - correct data access technology used (JPA, JDBC, etc.) as specified
  - no schema changes introduced (tables, columns unchanged)
- verify **Consistency Model** is enforced in the code:
  - transaction isolation levels match the specification
  - any advisory locks or concurrency controls described are present

| Condition | Severity |
|---|---|
| Schema change introduced (table or column added/modified/removed) | `critical` |
| Transaction isolation level differs from specification | `critical` |
| Wrong data access technology used | `warning` |
| Advisory lock or concurrency control absent | `warning` |

### Step 5: Integration Design check

- read `target-architecture.md` Integration Design section
- for each **External System Connection** verify:
  - the protocol and direction are implemented as described
  - contract preservation measures are present in the code (adapters, preserved message schemas, etc.)
- verify **Communication Protocols** are implemented:
  - primary protocol (REST/MQ/etc.) entry points exist
  - legacy/transition protocols are isolated (e.g., behind a Spring profile or adapter class)

| Condition | Severity |
|---|---|
| Protocol for an external connection not implemented | `critical` |
| Contract preservation measure (adapter, schema) absent | `critical` |
| Legacy/transition protocol not isolated | `warning` |

### Step 6: Security Architecture check

- read `target-architecture.md` Security Architecture section
- verify **Authentication & Authorization** is implemented:
  - auth mechanism (OAuth, API key, etc.) is configured in the code
  - authorization scopes/roles per operation are enforced
- verify **Data Protection** measures are implemented:
  - PII masking, encryption, or other protections described are present
  - no sensitive data logged without protection

| Condition | Severity |
|---|---|
| Auth mechanism not configured | `critical` |
| Authorization scopes/roles not enforced | `critical` |
| PII masking or data protection absent | `critical` |
| Sensitive data logged without protection | `critical` |

### Step 7: Cross-Cutting Concerns check

- read `target-architecture.md` Cross-Cutting Concerns section
- for each concern listed verify it is present in the code:
  - **Logging**: structured format, required fields (traceId, operatorId, etc.), PII masking at appender level
  - **Observability**: metrics, health endpoints, or tracing instrumentation present as specified
  - **Other concerns** (error handling, retry, etc.) if described — verify each is implemented

| Condition | Severity |
|---|---|
| Required log field missing | `warning` |
| Observability endpoint or metric absent | `warning` |
| Other described concern not implemented | `warning` |

### Step 8: Risk Mitigations check

- read `target-architecture.md` Risk Areas section
- for each **Critical** or **High** priority risk verify the described mitigation is present in the code
- skip Low/Medium risks unless they produce specific code artifacts (e.g., a lock, a test, a filter)

| Condition | Severity |
|---|---|
| Critical-priority risk mitigation absent from code | `critical` |
| High-priority risk mitigation absent from code | `critical` |

### Step 9: Compile Report

Compile all findings into `architecture-validation-report.json` conforming to `references/report-schema.json`.

- For each step (1–8) include a per-step entry with: `step`, `status` (PASS / PASS_WITH_WARNINGS / FAIL), and `issues[]`
- Collect all issues from all steps into the top-level `issues[]` array — each issue must include `step`, `severity`, `evidence` (file path + line where possible), and `remediation`
- Compute `overall_status` per the status rules in the output spec

### Step 10: Write Files

Write the output file:

```text
.migration/<feature>/validation/architecture-validation-report.json
```

### Step 11: Report to User

```text
Architecture validation complete for <feature>:
  Steps passed: N/8
  Issues found: N (critical: N, warning: N, info: N)

  Report: .migration/<feature>/validation/architecture-validation-report.json
```

</workflow>

<constraints>

## Constraints

- **Read-only for code** — never modify any file in the generated code directory
- **Read-only for source artifacts** — never modify `target-architecture.md` or any `.migration/` artifact
- **Evidence-based verdicts** — every `critical` or `warning` issue must cite specific evidence (file path, line number where possible)
- **No auto-fix** — report issues and remediation steps only; do not modify any output

</constraints>

## Completion

- **If PASS**: Tell the user the generated code fully conforms to the target architecture.
- **If PASS_WITH_WARNINGS**: Tell the user the generated code meets all critical architectural requirements. List each warning with its location and recommended action.
- **If FAIL**: List each critical issue with its step, file path, evidence, and remediation step.
