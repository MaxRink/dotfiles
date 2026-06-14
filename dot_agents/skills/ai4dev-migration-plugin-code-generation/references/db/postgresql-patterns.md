# PostgreSQL Patterns

Database-specific patterns for PostgreSQL schema generation.

## Primary Keys

Use `UUID` with `gen_random_uuid()` (PostgreSQL 13+):

```sql
CREATE TABLE entity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ...
);
```

For PostgreSQL < 13, use `uuid-ossp` extension:

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- Then use uuid_generate_v4()
```

Use `BIGSERIAL` only for simple cases or when UUID overhead is unacceptable:

```sql
id BIGSERIAL PRIMARY KEY
```

## Timestamps

Use `TIMESTAMPTZ` (timezone-aware) for all timestamp columns:

```sql
created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
```

Never use `TIMESTAMP` without timezone — it silently drops timezone info.

## Auto-Update Timestamps

Create a reusable trigger function:

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

Apply to each table:

```sql
CREATE TRIGGER update_{table}_updated_at
BEFORE UPDATE ON {table}
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

## JSON Columns

Use `JSONB` (not `JSON`) for indexed JSON data:

```sql
metadata JSONB DEFAULT '{}'::jsonb
```

JSONB advantages over JSON:

- Supports GIN indexing for fast key/value lookups
- Supports containment operators (`@>`, `<@`)
- More efficient storage (binary format)

Index JSONB columns for query patterns:

```sql
-- GIN index for general JSONB queries
CREATE INDEX idx_{table}_metadata ON {table} USING GIN (metadata);

-- B-tree index on specific JSONB path
CREATE INDEX idx_{table}_metadata_type ON {table} ((metadata->>'type'));
```

## Text Columns

Prefer `TEXT` over `VARCHAR` without length limit — same performance, no artificial constraint:

```sql
description TEXT,              -- Preferred: no arbitrary limit
name VARCHAR(255) NOT NULL,    -- OK when business rule requires max length
code CHAR(3) NOT NULL          -- OK for fixed-length codes (ISO country, currency)
```

## Full-Text Search

Use `tsvector` with GIN index for searchable text:

```sql
-- Add search vector column
search_vector TSVECTOR GENERATED ALWAYS AS (
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
) STORED;

-- Index it
CREATE INDEX idx_{table}_search ON {table} USING GIN (search_vector);
```

Query with `@@` operator:

```sql
SELECT * FROM {table} WHERE search_vector @@ plainto_tsquery('english', 'search terms');
```

## Indexes

### B-tree (default)

```sql
-- Single column
CREATE INDEX idx_{table}_{column} ON {table}({column});

-- Composite (high selectivity column first)
CREATE INDEX idx_{table}_{col1}_{col2} ON {table}({col1}, {col2});

-- Partial index (only index rows matching condition)
CREATE INDEX idx_{table}_active ON {table}(status) WHERE status = 'active';

-- Descending (for ORDER BY ... DESC queries)
CREATE INDEX idx_{table}_{column}_desc ON {table}({column} DESC);
```

### GIN (Generalized Inverted Index)

For JSONB, arrays, full-text search:

```sql
CREATE INDEX idx_{table}_{column} ON {table} USING GIN ({column});
```

### BRIN (Block Range Index)

For large tables with naturally ordered data (timestamps, sequential IDs):

```sql
CREATE INDEX idx_{table}_created_at ON {table} USING BRIN (created_at);
```

## Constraints

```sql
-- CHECK with meaningful name
CONSTRAINT chk_{table}_{rule} CHECK (price >= 0),
CONSTRAINT chk_{table}_percentage CHECK (percentage BETWEEN 0 AND 100),

-- UNIQUE (single column)
CONSTRAINT uk_{table}_{column} UNIQUE ({column}),

-- UNIQUE (composite)
CONSTRAINT uk_{table}_{col1}_{col2} UNIQUE ({col1}, {col2}),

-- EXCLUDE (prevent overlapping ranges)
CONSTRAINT excl_{table}_no_overlap EXCLUDE USING GIST (
    resource_id WITH =,
    tsrange(start_time, end_time) WITH &&
)
```

## Foreign Keys

```sql
-- CASCADE delete (child removed when parent deleted)
parent_id UUID NOT NULL REFERENCES parent_table(id) ON DELETE CASCADE,

-- SET NULL (child kept, FK set to NULL)
category_id UUID REFERENCES categories(id) ON DELETE SET NULL,

-- RESTRICT (prevent parent deletion if children exist)
owner_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
```

Always index foreign key columns:

```sql
CREATE INDEX idx_{table}_{fk_column} ON {table}({fk_column});
```

## Enums

Use PostgreSQL native ENUM type for fixed sets:

```sql
CREATE TYPE order_status AS ENUM ('pending', 'processing', 'shipped', 'delivered', 'cancelled');

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status order_status NOT NULL DEFAULT 'pending'
);
```

For evolving sets, prefer a lookup table or VARCHAR with CHECK constraint.

## Partitioning

For tables expected to grow beyond 10M rows:

```sql
-- Range partitioning by date
CREATE TABLE events (
    id UUID DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL,
    event_type TEXT NOT NULL,
    payload JSONB
) PARTITION BY RANGE (created_at);

-- Create partitions
CREATE TABLE events_2026_q1 PARTITION OF events
    FOR VALUES FROM ('2026-01-01') TO ('2026-04-01');
CREATE TABLE events_2026_q2 PARTITION OF events
    FOR VALUES FROM ('2026-04-01') TO ('2026-07-01');
```

## Migration Template

```sql
-- migrations/V1__initial_schema.sql (Flyway format)
BEGIN;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Trigger function (create once, reuse)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Tables
CREATE TABLE {table} (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- columns...
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_{table}_{column} ON {table}({column});

-- Triggers
CREATE TRIGGER update_{table}_updated_at
BEFORE UPDATE ON {table}
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT;
```
