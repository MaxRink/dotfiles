# MySQL Patterns

Database-specific patterns for MySQL schema generation.

## Engine and Character Set

Always specify explicitly:

```sql
CREATE TABLE {table} (
    ...
) ENGINE=InnoDB
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

- `InnoDB` — required for transactions, FK constraints, row-level locking
- `utf8mb4` — full Unicode support (including emoji)
- `utf8mb4_unicode_ci` — case-insensitive, accent-insensitive collation

## Primary Keys

### UUID (distributed systems)

Use `CHAR(36)` with application-generated UUID:

```sql
id CHAR(36) NOT NULL PRIMARY KEY
```

Or `BINARY(16)` for storage efficiency (requires application-layer conversion):

```sql
id BINARY(16) NOT NULL PRIMARY KEY
```

### Auto-Increment (simple systems)

```sql
id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY
```

Prefer `BIGINT UNSIGNED` over `INT` to avoid future overflow.

## Timestamps

Use `DATETIME(6)` for microsecond precision:

```sql
created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
```

Key differences from PostgreSQL:

- No native timezone support — store in UTC, handle timezone in application
- `ON UPDATE CURRENT_TIMESTAMP` handles auto-update (no trigger needed)
- `DATETIME(6)` provides microsecond precision

## JSON Columns

MySQL 5.7+ supports native `JSON` type:

```sql
metadata JSON DEFAULT NULL
```

Index JSON paths with generated columns:

```sql
-- Virtual generated column for indexing
ALTER TABLE {table}
ADD COLUMN metadata_type VARCHAR(50) GENERATED ALWAYS AS (JSON_UNQUOTE(JSON_EXTRACT(metadata, '$.type'))) VIRTUAL;

CREATE INDEX idx_{table}_metadata_type ON {table}(metadata_type);
```

Or use multi-valued index (MySQL 8.0.17+):

```sql
CREATE INDEX idx_{table}_tags ON {table}((CAST(metadata->'$.tags' AS CHAR(50) ARRAY)));
```

## Text Columns

```sql
name VARCHAR(255) NOT NULL,          -- Indexed strings (max 767 bytes for index in utf8mb4)
description TEXT,                     -- Long text (no index, use FULLTEXT for search)
code CHAR(3) NOT NULL                -- Fixed-length codes
```

Note: `VARCHAR` max length with utf8mb4 for indexed columns is ~191 characters (767 bytes / 4 bytes per char).

## Full-Text Search

```sql
-- Add FULLTEXT index
ALTER TABLE {table} ADD FULLTEXT INDEX ft_{table}_search (title, description);

-- Query
SELECT * FROM {table}
WHERE MATCH(title, description) AGAINST ('search terms' IN NATURAL LANGUAGE MODE);
```

## Indexes

```sql
-- Single column
CREATE INDEX idx_{table}_{column} ON {table}({column});

-- Composite (leftmost prefix rule applies)
CREATE INDEX idx_{table}_{col1}_{col2} ON {table}({col1}, {col2});

-- Prefix index for long strings
CREATE INDEX idx_{table}_{column} ON {table}({column}(50));

-- Descending (MySQL 8.0+)
CREATE INDEX idx_{table}_{column}_desc ON {table}({column} DESC);

-- Invisible index (for testing removal impact)
ALTER TABLE {table} ALTER INDEX idx_{table}_{column} INVISIBLE;
```

## Constraints

```sql
-- CHECK (MySQL 8.0.16+, enforced)
CONSTRAINT chk_{table}_{rule} CHECK (price >= 0),
CONSTRAINT chk_{table}_percentage CHECK (percentage BETWEEN 0 AND 100),

-- UNIQUE
CONSTRAINT uk_{table}_{column} UNIQUE ({column}),

-- UNIQUE composite
CONSTRAINT uk_{table}_{col1}_{col2} UNIQUE ({col1}, {col2})
```

Note: CHECK constraints are parsed but NOT enforced before MySQL 8.0.16.

## Foreign Keys

```sql
-- CASCADE delete
parent_id CHAR(36) NOT NULL,
CONSTRAINT fk_{table}_{parent} FOREIGN KEY (parent_id)
    REFERENCES parent_table(id) ON DELETE CASCADE ON UPDATE CASCADE,

-- SET NULL
category_id CHAR(36) DEFAULT NULL,
CONSTRAINT fk_{table}_{category} FOREIGN KEY (category_id)
    REFERENCES categories(id) ON DELETE SET NULL ON UPDATE CASCADE,

-- RESTRICT (default)
owner_id CHAR(36) NOT NULL,
CONSTRAINT fk_{table}_{owner} FOREIGN KEY (owner_id)
    REFERENCES users(id) ON DELETE RESTRICT ON UPDATE CASCADE
```

Always index foreign key columns (InnoDB requires this for FK constraints).

## Enums

MySQL has native ENUM type:

```sql
status ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled')
    NOT NULL DEFAULT 'pending'
```

Caution: Adding values to ENUM requires ALTER TABLE. For frequently changing sets, prefer a lookup table or VARCHAR with CHECK.

## Partitioning

For large tables (10M+ rows):

```sql
CREATE TABLE events (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    created_at DATETIME(6) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    payload JSON,
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (YEAR(created_at) * 100 + MONTH(created_at)) (
    PARTITION p202601 VALUES LESS THAN (202602),
    PARTITION p202602 VALUES LESS THAN (202603),
    PARTITION p202603 VALUES LESS THAN (202604),
    PARTITION pmax VALUES LESS THAN MAXVALUE
);
```

Note: Partition key must be part of every unique index (including PK).

## Migration Template

```sql
-- migrations/V1__initial_schema.sql (Flyway format)

-- Tables
CREATE TABLE {table} (
    id CHAR(36) NOT NULL PRIMARY KEY,
    -- columns...
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) ENGINE=InnoDB
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Indexes
CREATE INDEX idx_{table}_{column} ON {table}({column});
```

Rollback (Flyway undo or manual):

```sql
-- migrations/U1__initial_schema.sql
DROP TABLE IF EXISTS {table};
```
