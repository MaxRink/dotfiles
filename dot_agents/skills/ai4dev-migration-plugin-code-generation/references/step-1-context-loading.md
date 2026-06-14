# Step 1 — Load Context & Language Skills

Load specification context and language-specific code generation guidance.

## Overview

Step 1 consists of 3 sub-steps:

- **1a**: Load context from spec artifacts
- **1b**: Detect and load language-specific skill
- **1c**: (Already done in Step 0e - Environment Validation)

## Step 1a — Load Context

Read and extract comprehensive information from spec artifacts.

**Note**: Step 0d already read technical-plan.md to detect target stack. This step performs a complete read of all artifacts to extract detailed business requirements, components, architecture, etc.

### Read Artifacts

**Validate All Required Files Exist:**

```text
REQUIRED_FILES = [
  "functional-requirements.md",
  "technical-plan.md",
  "nonfunctional-requirements.md",
  "contracts.md"
]

FOR EACH file IN REQUIRED_FILES:
  IF NOT exists(.migration/<feature-name>/spec-specification/{file}):
    HALT: "Missing required spec artifact: {file}"

Log: "✓ All 4 required spec files validated"
```

**Read All Artifacts:**

```text
Read .migration/<feature-name>/spec-specification/functional-requirements.md ✓ REQUIRED
Read .migration/<feature-name>/spec-specification/technical-plan.md ✓ REQUIRED
Read .migration/<feature-name>/spec-specification/nonfunctional-requirements.md ✓ REQUIRED
Read .migration/<feature-name>/spec-specification/contracts.md ✓ REQUIRED
Read .migration/<feature-name>/analysis/analysis.json (optional)
Read .migration/<feature-name>/architect/target-architecture.md (optional)
```

### Extract Information

**From functional-requirements.md (REQUIRED):**

- Functional requirements with FR IDs (FR-001, FR-002, etc.)
- Use cases with UC IDs (UC-001, UC-002, etc.)
- Traceability matrix (BR ID → FR ID → Component)
- Acceptance criteria per FR
- Edge cases and validation rules
- Formula and calculation rules

**Maps to:** BDD scenarios (Step 4), unit tests (Step 4), traceability matrix (Step 8)

**From nonfunctional-requirements.md (REQUIRED):**

- Performance requirements (NFR-PERF-xxx)
- Security requirements (NFR-SEC-xxx)
- Reliability requirements (NFR-REL-xxx)
- Scalability requirements (NFR-SCALE-xxx)
- Usability requirements (NFR-UX-xxx)

**Maps to:** Setup dependencies (Step 3), performance optimizations (Step 5), security hardening (Step 7)

**From contracts.md (REQUIRED):**

- REST API contracts (endpoints, request/response schemas, auth)
- Messaging contracts (topics, queue names, message schemas)
- Database contracts (schema access, stored procedures, transaction boundaries)
- File contracts (formats, paths, error handling)

**Maps to:** API contract tests (Step 4), DTOs/endpoints (Step 5), database schema (Step 6)

**From technical-plan.md (REQUIRED):**

- Component specifications
- Architecture overview
- Technology stack (already extracted in Step 0d)
- Integration requirements
- Implementation steps
- Data models

**Maps to:** Task generation (Step 2), setup configuration (Step 3), core implementation (Step 5), integration wiring (Step 6)

**From analysis.json (supplementary):**

- Business rule details
- Pseudocode for complex logic
- Control flows
- Edge cases

**From target-architecture.md (supplementary):**

- Architecture patterns
- Component relationships
- System boundaries
- Quality attributes

## Step 1b — Consult Language-Specific Skill

Load language-specific code generation guidance based on detected target stack.

### Identify Target Language

Use `target_language` detected in Step 0d:

```text
From Step 0d:
  target_language = "java" or "python" or ...
  target_version = "17" or "3.11" or ...
  frameworks = ["spring-boot"] or ["fastapi"] or ...
```

### Map to Language Skill

```text
Language Skills Available:
  java + spring-boot → java-codegen
  java + quarkus → quarkus-codegen
  python → python-codegen
```

### Load Language Skill References

The language skill is already loaded into agent context via the agent's skills array.

**For Java:**

```text
Skill: java-codegen
Available References:
  - fundamentals.md
  - springboot-core.md
  - springboot-security.md
  - testing.md
  - build-tools.md
  - jpa-patterns.md
  - microservices.md
  - concurrency.md
  - performance.md
  - coding-standards.md
```

**For Python:**

```text
Skill: python-codegen
Available References:
  - fundamentals.md
  - fastapi-core.md
  - fastapi-security.md
  - testing.md
  - build-tools.md
  - sqlalchemy-patterns.md
  - async-patterns.md
  - coding-standards.md
```

**For Quarkus:**

```text
Skill: quarkus-codegen
Available References:
  - fundamentals.md
  - quarkus-core.md
  - quarkus-security.md
  - testing.md
  - build-tools.md
  - persistence-patterns.md
  - microservices.md
  - reactive-patterns.md
  - coding-standards.md
```

### Determine Which References to Load

See `language-skill-integration.md` for complete step-to-reference mappings.

**References are loaded per-batch** during execution (Steps 3-7), not all at once here.

The mapping determines which references each batch will load:

- Setup batches → build-tools.md, {framework}-core.md, coding-standards.md
- Tests batches → testing.md, fundamentals.md
- Core batches → fundamentals.md, {framework}-core.md, {framework}-patterns.md, coding-standards.md
- Integration batches → {framework}-core.md, testing.md, {microservices}.md (if applicable)
- Polish batches → performance.md, {framework}-security.md, coding-standards.md

### Store Language Skill Context

```text
Store in memory for use in Step 2:
  language_skill = {
    "name": "java-codegen",
    "detected_language": "java",
    "detected_version": "17",
    "detected_frameworks": ["spring-boot"],
    "available_references": [list of all references]
  }

This will be written to tasks.json config section in Step 2
```

### Detect Database Skill (Step 1b+)

Check spec artifacts for database requirements:

```text
1. Check contracts.md for "## 3. Database Contracts"
2. Check technical-plan.md for "## 4. Data Implementation" with schema changes

IF either contains database specifications:
  1. Extract DB type from contracts.md (PostgreSQL, MySQL, MongoDB, SQLite)
  2. Set db_skill = "db-codegen"
  3. Determine migration framework from language + framework:
     - Java + Spring Boot  → flyway, path: src/main/resources/db/migration/
     - Java + Quarkus      → flyway, path: src/main/resources/db/migration/
     - Python + FastAPI    → alembic, path: alembic/versions/
     - Generic             → raw-sql, path: database/migrations/
  4. Store db_skill context for Step 2 task generation:
     db_skill = {
       "name": "db-codegen",
       "db_type": "postgresql",
       "migration_framework": "flyway",
       "migration_path": "src/main/resources/db/migration/",
       "available_references": ["postgresql-patterns.md", "schema-design-rules.md", "migration-patterns.md"]
     }

ELSE:
  db_skill = null (no database tasks will be generated in Step 2)
```

See `skills/code-generation/references/db/SKILL.md` for complete database skill reference and task execution guide.

### Fallback for Unsupported Languages

```text
IF no language skill exists for target_language:
  Log warning: "No language skill found for {target_language}"
  Log: "Using generic workflow based on technical-plan.md only"
  Continue without language skill
  language_skill = null
```

## Step 1c — Validate Environment

**Note**: This was already completed in Step 0e.

The original workflow had environment validation here, but it was moved to Step 0e to fail fast before loading context.

## Summary

After Step 1 completes:

- ✓ All 4 required spec artifacts validated and loaded
- ✓ Functional requirements extracted (FR IDs, UC IDs, acceptance criteria)
- ✓ Nonfunctional requirements extracted (NFR-PERF, NFR-SEC, etc.)
- ✓ API/interface contracts extracted (REST, messaging, database, file)
- ✓ Technical specs and component specifications extracted
- ✓ Language skill identified and ready
- ✓ Database skill detected (if DB contracts present)
- ✓ Reference mapping prepared for batch execution

**Loaded Context:**

```text
Store in memory for use in Step 2:
  spec_context = {
    "functional_requirements": [...],  // FR IDs with acceptance criteria
    "use_cases": [...],                // UC IDs with scenarios
    "nonfunctional_requirements": [...], // NFR IDs by category
    "contracts": {...},                // API, messaging, DB, file contracts
    "components": [...],               // From technical-plan.md
    "traceability_matrix": {...}       // BR → FR → Component mapping
  }

This drives Step 2 task generation: FR IDs → Tasks with traceability
```

## Continue to Step 2

Proceed to Step 2 — Generate Task List with Batching.
