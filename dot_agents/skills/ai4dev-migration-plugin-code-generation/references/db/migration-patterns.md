# Migration Patterns

Language-aware database migration patterns. Select the appropriate framework based on detected target stack.

## Framework Selection

| Target Stack | Migration Framework | Migration Path |
|-------------|-------------------|---------------|
| Java + Spring Boot | Flyway | `src/main/resources/db/migration/V{N}__{description}.sql` |
| Java + Quarkus | Flyway | `src/main/resources/db/migration/V{N}__{description}.sql` |
| Python + FastAPI | Alembic | `alembic/versions/{revision}_{description}.py` |
| Python + Django | Django Migrations | `{app}/migrations/{NNNN}_{description}.py` |
| Node.js | Knex / Prisma | `migrations/{timestamp}_{description}.js` or `prisma/migrations/` |
| Generic (no framework) | Raw SQL | `database/migrations/{NNN}_{description}.up.sql` + `.down.sql` |

## Universal Migration Rules

### 1. Transaction Wrapping

Every migration MUST be wrapped in a transaction:

```sql
BEGIN;
-- DDL statements
COMMIT;
```

Exception: Some DDL statements cannot run inside transactions (e.g., `CREATE INDEX CONCURRENTLY` in PostgreSQL). Document these explicitly.

### 2. Reversibility

Every UP migration MUST have a corresponding DOWN migration:

- UP: Apply schema changes
- DOWN: Revert to previous state
- DOWN must be tested — not just written

### 3. Idempotency

Use `IF NOT EXISTS` / `IF EXISTS` where possible:

```sql
CREATE TABLE IF NOT EXISTS users (...);
DROP TABLE IF EXISTS users;
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
```

### 4. No Data Loss

- Never drop columns with data without a data migration step
- Use `ALTER TABLE ... ADD COLUMN` with defaults for new required columns
- Rename via add-copy-drop pattern, not direct rename

### 5. Ordering

Number migrations sequentially. Never reorder or renumber existing migrations.

## Flyway (Java)

### Naming Convention

```text
V{version}__{description}.sql    — versioned migration (applied once)
U{version}__{description}.sql    — undo migration (Flyway Teams only)
R__{description}.sql             — repeatable migration (re-applied on change)
```

- Version: integer or dotted (`V1`, `V1.1`, `V2`)
- Double underscore `__` separates version from description
- Description: snake_case

### Directory Structure

```text
src/main/resources/
└── db/
    └── migration/
        ├── V1__create_users.sql
        ├── V2__create_products.sql
        ├── V3__create_orders.sql
        └── V4__add_order_items.sql
```

### Template

```sql
-- V1__create_initial_schema.sql
BEGIN;

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

COMMIT;
```

### Rollback (manual, since Flyway Community has no undo)

Create a separate rollback script in `database/migrations/`:

```sql
-- database/migrations/001_create_initial_schema.down.sql
BEGIN;
DROP TABLE IF EXISTS users CASCADE;
COMMIT;
```

### Spring Boot Configuration

```yaml
# application.yml
spring:
  flyway:
    enabled: true
    locations: classpath:db/migration
    baseline-on-migrate: true
```

## Alembic (Python)

### Directory Structure

```text
alembic/
├── env.py                    # Alembic environment config
├── alembic.ini               # Config file
├── script.py.mako            # Migration template
└── versions/
    ├── 001_create_users.py
    ├── 002_create_products.py
    └── 003_create_orders.py
```

### Migration Template

```python
"""create users table

Revision ID: 001
Revises:
Create Date: 2026-04-23
"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('idx_users_email', 'users', ['email'])


def downgrade() -> None:
    op.drop_index('idx_users_email', table_name='users')
    op.drop_table('users')
```

### Async env.py Template

```python
from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

config = context.config


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    engine = create_async_engine(config.get_main_option("sqlalchemy.url"))
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()
```

## Generic Raw SQL

For projects without a migration framework.

### Directory Structure

```text
database/
└── migrations/
    ├── 001_create_initial_schema.up.sql
    ├── 001_create_initial_schema.down.sql
    ├── 002_add_orders.up.sql
    └── 002_add_orders.down.sql
```

### Naming Convention

```text
{NNN}_{description}.up.sql    — apply migration
{NNN}_{description}.down.sql  — rollback migration
```

- NNN: zero-padded sequence number (001, 002, ...)
- description: snake_case

### UP Template

```sql
-- 001_create_initial_schema.up.sql
BEGIN;

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

COMMIT;
```

### DOWN Template

```sql
-- 001_create_initial_schema.down.sql
BEGIN;

DROP INDEX IF EXISTS idx_users_email;
DROP TABLE IF EXISTS users CASCADE;

COMMIT;
```

## Seed Data Patterns

Seed data files go in `database/seeds/sample_data.sql`.

### Rules

- Use INSERT with explicit column lists
- Reference valid FK values
- Provide 5-10 rows per table for meaningful testing
- Use realistic data (not lorem ipsum)
- Wrap in transaction
- Use ON CONFLICT DO NOTHING for idempotency

### Template

```sql
-- database/seeds/sample_data.sql
BEGIN;

-- Users (insert first — referenced by other tables)
INSERT INTO users (id, email, name, created_at) VALUES
    ('a1b2c3d4-0000-0000-0000-000000000001', 'alice@example.com', 'Alice Smith', NOW()),
    ('a1b2c3d4-0000-0000-0000-000000000002', 'bob@example.com', 'Bob Jones', NOW()),
    ('a1b2c3d4-0000-0000-0000-000000000003', 'carol@example.com', 'Carol White', NOW())
ON CONFLICT DO NOTHING;

-- Orders (references users)
INSERT INTO orders (id, user_id, total_amount, status, created_at) VALUES
    ('b2c3d4e5-0000-0000-0000-000000000001', 'a1b2c3d4-0000-0000-0000-000000000001', 99.99, 'delivered', NOW()),
    ('b2c3d4e5-0000-0000-0000-000000000002', 'a1b2c3d4-0000-0000-0000-000000000002', 49.50, 'pending', NOW())
ON CONFLICT DO NOTHING;

COMMIT;
```

## Dual Location Strategy

When a migration framework is detected, generate migrations in BOTH locations:

1. **Canonical location**: `database/migrations/` — raw SQL, framework-agnostic
2. **Framework location**: e.g., `src/main/resources/db/migration/` — framework-specific format

The canonical location serves as documentation and fallback. The framework location is what the application actually executes.

For Python/Alembic, the framework migration is Python code (not raw SQL), so the canonical SQL in `database/migrations/` provides the reference DDL while `alembic/versions/` contains the executable migration.
