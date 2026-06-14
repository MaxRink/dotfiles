
# Database Schema Design Skill

Comprehensive database schema design reference for generating DB artifacts during the TDD/BDD code-generation workflow.
Consult the topic-specific references as needed during Setup and Integration steps.

## References

Available at [references/](references/) — load the ones relevant to the detected database type:

| Reference | When to Load | Used During |
|-----------|-------------|-------------|
| [references/postgresql-patterns.md](references/postgresql-patterns.md) | PostgreSQL in target stack | Setup — UUID generation, TIMESTAMPTZ, JSONB, triggers, GIN indexes, full-text search |
| [references/mysql-patterns.md](references/mysql-patterns.md) | MySQL in target stack | Setup — CHAR(36) UUIDs, DATETIME(6), InnoDB engine, utf8mb4, ON UPDATE timestamps |
| [references/schema-design-rules.md](references/schema-design-rules.md) | Always (any DB target) | Setup — mandatory rules (PK, FK, NOT NULL), prohibited patterns (EAV abuse, plaintext secrets), ERD conventions (Mermaid format) |
| [references/migration-patterns.md](references/migration-patterns.md) | Always (any DB target) | Setup, Integration — language-aware migration frameworks (Java→Flyway, Python→Alembic, generic→raw SQL), transaction wrapping, rollback |

## How This Skill Is Used

The `code-generation` Step 1b detects database requirements from `contracts.md` section 3 (Database Contracts)
or `technical-plan.md` section 4 (Data Implementation). When DB contracts are present, this skill is loaded alongside the language skill.

### Detection Logic

```text
IF contracts.md contains "## 3. Database Contracts"
   OR technical-plan.md contains "## 4. Data Implementation" with schema changes:

  1. Extract DB type from contracts.md (PostgreSQL, MySQL, MongoDB, SQLite)
  2. Load db-codegen skill
  3. Load DB-type-specific reference (postgresql-patterns.md, mysql-patterns.md)
  4. Load schema-design-rules.md and migration-patterns.md (always)
  5. Add DB setup tasks to Step 3 (Setup) task list
```

### Step-to-Reference Mapping

| Code-Gen Step | Primary References | What They Provide |
|---------------|-------------------|-------------------|
| **Setup** | `{db-type}-patterns.md`, `schema-design-rules.md`, `migration-patterns.md` | DB-specific DDL patterns, constraint rules, ERD conventions, migration framework selection |
| **Integration** | `migration-patterns.md` | Migration execution wiring, seed data loading |

## Database Schema Task Execution Guide

When DB setup tasks are included in Step 3 (Setup), execute in this order:

### Task 1: Generate ERD Diagram

Read entity definitions from:

- `contracts.md` section 3 (Database Contracts)
- `technical-plan.md` section 4 (Data Implementation)
- `analysis.json` entities array (if available)

Generate `database/docs/ERD.md` with Mermaid erDiagram showing:

- All entities with attributes and types
- Relationships with cardinality (`||--o{`, `}o--|{`, etc.)
- Primary Keys (PK), Foreign Keys (FK), Unique Keys (UK)

### Task 2: Generate Schema DDL

Generate `database/schema.sql` with complete DDL:

- CREATE TABLE statements with all columns, types, constraints
- Primary keys (UUID or auto-increment per DB type)
- Foreign keys with CASCADE/SET NULL behavior
- CHECK constraints for value ranges
- UNIQUE constraints
- Indexes (PK auto-indexed, FK indexed, query-pattern indexes)
- Triggers (auto-update timestamps)

### Task 3: Generate Migration Scripts

Generate migration scripts using language-aware framework:

- **Java (Spring Boot/Quarkus)**: Flyway `V1__initial_schema.sql` in `src/main/resources/db/migration/`
- **Python**: Alembic version file in `alembic/versions/`
- **Generic**: `database/migrations/001_initial_schema.up.sql` + `.down.sql`

All migrations must be:

- Transactional (BEGIN/COMMIT wrapping)
- Reversible (UP + DOWN)
- Idempotent where possible

### Task 4: Generate Seed Data

Generate `database/seeds/sample_data.sql` with:

- Realistic test data for each table
- Correct foreign key references
- Sufficient volume for meaningful testing (5-10 rows per table)

### Task 5: Generate Schema Documentation

Generate `database/docs/SCHEMA.md` with:

- Database overview (type, version, key design decisions)
- Table-by-table documentation (purpose, columns, indexes, constraints)
- Index strategy explanation
- Constraint rationale
- Performance considerations for the detected workload pattern

## Output Structure

All DB artifacts are generated under `<output-dir>/database/`:

```text
database/
├── schema.sql                        # Complete schema DDL
├── migrations/
│   ├── 001_initial_schema.up.sql     # Generic UP migration
│   └── 001_initial_schema.down.sql   # Generic DOWN migration
├── seeds/
│   └── sample_data.sql               # Test/seed data
└── docs/
    ├── ERD.md                        # Mermaid ERD diagram
    └── SCHEMA.md                     # Schema documentation
```

For language-specific migrations, also generate in framework-expected location:

- Java: `src/main/resources/db/migration/V1__initial_schema.sql`
- Python: `alembic/versions/001_initial_schema.py`

## Supported Database Types

| DB Type | Pattern Reference | Key Features |
|---------|------------------|--------------|
| PostgreSQL | `postgresql-patterns.md` | UUID, TIMESTAMPTZ, JSONB, triggers, GIN indexes |
| MySQL | `mysql-patterns.md` | CHAR(36) UUID, DATETIME(6), InnoDB, utf8mb4 |
| MongoDB | (inline patterns) | ObjectId, denormalization, compound indexes, schema validation |
| SQLite | (inline patterns) | INTEGER PK AUTOINCREMENT, TEXT types, PRAGMA foreign_keys |

For MongoDB and SQLite, patterns are simpler and documented inline in `schema-design-rules.md` rather than separate reference files.
