# Database Design Patterns

PostgreSQL database design and Flyway migration patterns for VNRM microservices.

## Table Template (DDL)

```sql
-- ${table_name} table
-- Purpose: ${description}
-- Business Rules: ${BR-XXX}

CREATE TABLE ${schema}.${table_name} (
    -- Primary Key
    id BIGSERIAL PRIMARY KEY,

    -- Business Fields
    ${field_name} VARCHAR(${length}) NOT NULL,
    ${field_name_2} VARCHAR(${length_2}),

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',

    -- Optimistic Locking
    version BIGINT NOT NULL DEFAULT 0,

    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),

    -- Constraints
    CONSTRAINT ${table_name}_${field}_unique UNIQUE (${unique_field}),
    CONSTRAINT ${table_name}_status_check CHECK (status IN ('PENDING', 'ACTIVE', 'INACTIVE', 'DELETED'))
);

-- Indexes
CREATE INDEX idx_${table_name}_status ON ${schema}.${table_name}(status);
CREATE INDEX idx_${table_name}_created_at ON ${schema}.${table_name}(created_at);
CREATE INDEX idx_${table_name}_${field} ON ${schema}.${table_name}(${indexed_field});

-- Comments
COMMENT ON TABLE ${schema}.${table_name} IS '${description}';
COMMENT ON COLUMN ${schema}.${table_name}.${field_name} IS '${field_description}';
```

## Flyway Migration Naming

```
V{version}__{description}.sql

Examples:
V1__create_${table_name}_table.sql
V2__add_${column}_to_${table}.sql
V3__create_${index}_index.sql
V4__add_${constraint}.sql
```

## Migration Templates

### Create Table Migration

```sql
-- V1__create_${table_name}_table.sql
-- Description: Initial schema for ${EntityName}
-- Author: VNRM Migration
-- Date: ${date}

CREATE TABLE IF NOT EXISTS ${schema}.${table_name} (
    id BIGSERIAL PRIMARY KEY,
    -- ... fields ...
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_${table_name}_status
    ON ${schema}.${table_name}(status);

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ${schema}.${table_name} TO ${app_user};
GRANT USAGE, SELECT ON SEQUENCE ${schema}.${table_name}_id_seq TO ${app_user};
```

### Add Column Migration

```sql
-- V2__add_${column}_to_${table}.sql
-- Description: Add ${column} field to ${table}
-- Author: VNRM Migration
-- Date: ${date}

ALTER TABLE ${schema}.${table_name}
ADD COLUMN IF NOT EXISTS ${column_name} ${data_type} ${constraints};

-- Add index if needed
CREATE INDEX IF NOT EXISTS idx_${table_name}_${column}
    ON ${schema}.${table_name}(${column_name});

-- Update existing rows (if needed)
UPDATE ${schema}.${table_name}
SET ${column_name} = ${default_value}
WHERE ${column_name} IS NULL;
```

### Create Foreign Key Migration

```sql
-- V3__add_${fk_name}_foreign_key.sql
-- Description: Add foreign key from ${child_table} to ${parent_table}
-- Author: VNRM Migration
-- Date: ${date}

-- Add column if not exists
ALTER TABLE ${schema}.${child_table}
ADD COLUMN IF NOT EXISTS ${parent_table}_id BIGINT;

-- Add foreign key constraint
ALTER TABLE ${schema}.${child_table}
ADD CONSTRAINT fk_${child_table}_${parent_table}
FOREIGN KEY (${parent_table}_id)
REFERENCES ${schema}.${parent_table}(id)
ON DELETE ${action}
ON UPDATE CASCADE;

-- Index for FK performance
CREATE INDEX IF NOT EXISTS idx_${child_table}_${parent_table}_id
    ON ${schema}.${child_table}(${parent_table}_id);
```

### Data Migration

```sql
-- V4__migrate_${description}.sql
-- Description: Data migration from ${source} to ${target}
-- Author: VNRM Migration
-- Date: ${date}

-- Insert migrated data
INSERT INTO ${schema}.${target_table} (${columns})
SELECT ${source_columns}
FROM ${schema}.${source_table}
WHERE ${conditions};

-- Verify migration
DO $$
DECLARE
    source_count INTEGER;
    target_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO source_count FROM ${schema}.${source_table};
    SELECT COUNT(*) INTO target_count FROM ${schema}.${target_table};

    IF source_count != target_count THEN
        RAISE EXCEPTION 'Migration count mismatch: source=%, target=%',
            source_count, target_count;
    END IF;
END $$;
```

## VNRM-Specific Schemas

### Callnumber Table (NUM submodule)

```sql
CREATE TABLE num.callnumber (
    id BIGSERIAL PRIMARY KEY,
    callnumber VARCHAR(20) NOT NULL,
    area_code VARCHAR(10),
    subscriber_number VARCHAR(15),
    number_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    assigned_at TIMESTAMP WITH TIME ZONE,
    released_at TIMESTAMP WITH TIME ZONE,
    version BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT callnumber_unique UNIQUE (callnumber),
    CONSTRAINT callnumber_type_check CHECK (number_type IN ('GEOGRAPHIC', 'NON_GEOGRAPHIC', 'MOBILE', 'SERVICE'))
);

CREATE INDEX idx_callnumber_area_code ON num.callnumber(area_code);
CREATE INDEX idx_callnumber_status ON num.callnumber(status);
```

### Porting Table (PRT submodule)

```sql
CREATE TABLE prt.porting (
    id BIGSERIAL PRIMARY KEY,
    porting_id VARCHAR(50) NOT NULL,
    callnumber VARCHAR(20) NOT NULL,
    donor_provider VARCHAR(50) NOT NULL,
    recipient_provider VARCHAR(50) NOT NULL,
    porting_date DATE,
    porting_status VARCHAR(20) NOT NULL DEFAULT 'REQUESTED',
    requested_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    version BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT porting_id_unique UNIQUE (porting_id),
    CONSTRAINT porting_status_check CHECK (porting_status IN ('REQUESTED', 'CONFIRMED', 'COMPLETED', 'REJECTED', 'CANCELLED'))
);

CREATE INDEX idx_porting_callnumber ON prt.porting(callnumber);
CREATE INDEX idx_porting_status ON prt.porting(porting_status);
CREATE INDEX idx_porting_date ON prt.porting(porting_date);
```

## Index Guidelines

| Column Type | Index Type | When to Use |
|------------|------------|-------------|
| Primary Key | B-tree (auto) | Always |
| Foreign Key | B-tree | Always |
| Status/Enum | B-tree | If frequently filtered |
| Text search | GIN | Full-text search |
| Date range | B-tree | Range queries |
| Composite | B-tree | Multiple column queries |

## ETL Strategy Patterns

### Full Load

```sql
-- Truncate and reload
TRUNCATE TABLE ${target_table};
INSERT INTO ${target_table} SELECT * FROM ${source_table};
```

### Incremental Load (CDC)

```sql
-- Insert new, update changed
INSERT INTO ${target_table}
SELECT * FROM ${source_table} s
WHERE s.updated_at > ${last_sync}
ON CONFLICT (id) DO UPDATE
SET field = EXCLUDED.field,
    updated_at = EXCLUDED.updated_at;
```

### Merge (Upsert)

```sql
INSERT INTO ${target_table} (${columns})
VALUES (${values})
ON CONFLICT (${unique_key}) DO UPDATE
SET ${column} = EXCLUDED.${column},
    updated_at = CURRENT_TIMESTAMP;
```

## Best Practices

1. **Always use BIGSERIAL** for primary keys
2. **Add optimistic locking** with version column
3. **Include audit fields** (created_at, updated_at, created_by, updated_by)
4. **Create indexes** for foreign keys and query columns
5. **Use constraints** for data integrity
6. **Add comments** for documentation
7. **Use schema namespaces** (num., prt., com.)
8. **Test migrations** before production
9. **Version migrations** incrementally
10. **Include rollback scripts** for complex changes
