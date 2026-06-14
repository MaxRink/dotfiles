# Step 3 — Setup

Execute Setup batch (typically 1 batch with all setup tasks).

## Overview

Setup step creates the project foundation:

- Directory structure per language conventions
- Build configuration files
- Application configuration files
- Test infrastructure setup

## Execute Batch Following Standard Template

See `batch-execution-template.md` for the complete batch execution loop (8 steps).

This file documents **Step-Specific Customization Points** only.

## Step-Specific: Task Execution (Template Step 4a)

For each task in the Setup batch, apply language-specific conventions from loaded references.

### Load Language Context

Before executing tasks:

```text
1. Read batch from tasks.json to get batch.language_context

2. IF language_context exists:
     FOR each reference in language_context.references:
       path = skills/{language_context.skill}/references/{reference}
       Read {path}
       Store content in memory for this batch

   Example for Java Setup batch:
     Read skills/code-generation/references/java/build-tools.md
     Read skills/code-generation/references/java/springboot-core.md
     Read skills/code-generation/references/java/coding-standards.md

   Example for Python Setup batch:
     Read skills/code-generation/references/python/build-tools.md
     Read skills/code-generation/references/python/fastapi-core.md
     Read skills/code-generation/references/python/coding-standards.md

3. ELSE (no language context - generic workflow):
     Proceed with language-agnostic patterns from technical-plan.md
```

### Apply Language-Specific Conventions

For each task:

1. **Directory structure** from `language_context.conventions.directory_layout`
2. **File naming** from `language_context.conventions.naming`
3. **Templates** from `language_context.templates`

### Generate Files Using Language Patterns

**Java Example:**

```text
Write <output-dir>/pom.xml (template from build-tools.md)
Write <output-dir>/src/main/java/com/example/{module}/ (structure from build-tools.md)
Write <output-dir>/src/main/resources/application.yml (template from springboot-core.md)
Write <output-dir>/src/main/resources/application-test.yml
Write <output-dir>/src/test/java/com/example/{module}/ (test structure from build-tools.md)
Write <output-dir>/src/test/resources/
Write <output-dir>/.gitignore (Java patterns)
Write <output-dir>/README.md (project overview)
```

**Python Example:**

```text
Write <output-dir>/pyproject.toml (template from build-tools.md)
Write <output-dir>/src/app/ (structure from fastapi-core.md)
Write <output-dir>/src/app/main.py (template from fastapi-core.md)
Write <output-dir>/src/app/__init__.py
Write <output-dir>/tests/ (pytest structure)
Write <output-dir>/tests/conftest.py (pytest fixtures)
Write <output-dir>/alembic/ (init from sqlalchemy-patterns.md if using SQLAlchemy)
Write <output-dir>/.gitignore (Python patterns)
Write <output-dir>/README.md (project overview)
```

**Generic (no language skill):**

```text
Use directory structure and file patterns from technical-plan.md
Create basic project layout as specified
```

### Update Task Status

**Mark task as passed after all files for that task are written and verified:**

```text
Update tasks.json:
  - task.status = "passed"
  - task.completed_at = current_timestamp
  - task.duration_seconds = elapsed_time

Update tasks.md progress tracker

Note: Write ALL files for a task before updating state. See batch-execution-template.md.
```

## Database Schema Tasks (Conditional)

When `contracts.md` section 3 (Database Contracts) or `technical-plan.md` section 4 (Data Implementation) specifies database requirements, the Setup batch includes additional DB schema tasks.

### Detection

```text
IF contracts.md contains "## 3. Database Contracts"
   OR technical-plan.md contains "## 4. Data Implementation" with schema changes:

  1. Extract DB type from contracts.md (PostgreSQL, MySQL, MongoDB, SQLite)
  2. Load db-codegen references based on DB type:
     - Read skills/code-generation/references/db/{db-type}-patterns.md (if exists)
     - Read skills/code-generation/references/db/schema-design-rules.md
     - Read skills/code-generation/references/db/migration-patterns.md
  3. Execute DB tasks after normal setup tasks complete
```

### DB Task Execution Order

```text
1. Generate ERD Diagram
   - Read entity/relationship specs from contracts.md § 3 and technical-plan.md § 4
   - Read analysis.json entities array (if available)
   - Write database/docs/ERD.md with Mermaid erDiagram
   - Include all entities, attributes, types, relationships with cardinality
   - Mark PK, FK, UK per schema-design-rules.md ERD conventions

2. Generate Schema DDL
   - Write database/schema.sql with complete DDL
   - Use DB-type-specific patterns ({db-type}-patterns.md)
   - Include: CREATE TABLE, constraints, indexes, triggers
   - Follow schema-design-rules.md mandatory rules

3. Generate Migration Scripts
   - Detect migration framework from language + framework (migration-patterns.md):
     Java (Spring Boot/Quarkus) → Flyway: src/main/resources/db/migration/V1__initial_schema.sql
     Python → Alembic: alembic/versions/001_initial_schema.py
     Generic → Raw SQL: database/migrations/001_initial_schema.up.sql + .down.sql
   - Always generate canonical raw SQL in database/migrations/ as well
   - Wrap in transactions (BEGIN/COMMIT)

4. Generate Seed Data
   - Write database/seeds/sample_data.sql
   - 5-10 realistic rows per table
   - Correct FK references
   - Use ON CONFLICT DO NOTHING for idempotency

5. Generate Schema Documentation
   - Write database/docs/SCHEMA.md
   - Table-by-table documentation (purpose, columns, indexes, constraints)
   - Index strategy explanation
   - Design decision rationale
```

### DB Batch Context

DB tasks use `db_context` alongside `language_context` in the batch:

```json
{
  "language_context": { "skill": "java-codegen", "..." : "..." },
  "db_context": {
    "skill": "db-codegen",
    "db_type": "postgresql",
    "references": ["postgresql-patterns.md", "schema-design-rules.md", "migration-patterns.md"],
    "migration_framework": "flyway",
    "migration_path": "src/main/resources/db/migration/"
  }
}
```

### No DB Contracts — Skip

If neither `contracts.md` section 3 nor `technical-plan.md` section 4 contains database specifications, no DB tasks are generated and no `database/` directory is created. Code generation proceeds normally.

## Step-Specific: Checkpoint Verification (Template Step 5)

After all Setup tasks complete, verify the project foundation.

### Structure Verification

```text
1. Verify directory structure matches language conventions:
   - Java: src/main/java, src/test/java, src/main/resources, src/test/resources
   - Python: src/app, tests/, alembic/ (if applicable)

2. Verify all expected files exist:
   - Build config: pom.xml, pyproject.toml
   - App config: application.yml, .env, config files
   - Test config: application-test.yml, conftest.py
   - Documentation: README.md

3. If DB tasks were executed, verify:
   - database/schema.sql exists and is non-empty
   - database/docs/ERD.md exists with erDiagram block
   - database/migrations/ contains at least one migration pair (or framework-specific file)
   - database/seeds/sample_data.sql exists
   - database/docs/SCHEMA.md exists
   - Framework-specific migration exists (e.g., src/main/resources/db/migration/V1__*.sql for Java)
```

### Build Config Validation

Use language-specific validation tools:

**Java:**

```bash
cd <output-dir>
mvn validate
```

**Python:**

```bash
cd <output-dir>
uv sync --check
# or
poetry check
```

### Test Runner Verification

Verify test framework can be invoked:

**Java:**

```bash
mvn test-compile
```

**Python:**

```bash
pytest --collect-only
```

### Update Checkpoint

```json
{
  "batch": {
    "checkpoint": {
      "verification_type": "structure",
      "verification_passed": true,
      "structure_valid": true,
      "build_config_valid": true,
      "test_runner_ready": true,
      "notes": "Project foundation created successfully"
    }
  }
}
```

### Handle Checkpoint Failure

IF any validation fails:

```text
1. Update batch.status = "failed"
2. Update checkpoint.verification_passed = false
3. Add diagnostic info to errors array
4. Save state
5. HALT execution
6. Print diagnostic information with fix instructions
```

## Step-Specific: Progress Output (Template Step 7)

```text
[Step 1/5] Setup - Batch 1/1 completed ✓
  Tasks: T001-T003 (3/3 passed)
  Checkpoint: Structure validated ✓
  Language: Java (Spring Boot + Maven)
  Progress: 3/45 tasks (7%)
  Time: 1m 30s elapsed, ~78m remaining
  Next: Tests step
```

## Continue

Proceed immediately to Step 4 (Tests). Do NOT pause or ask for confirmation.
