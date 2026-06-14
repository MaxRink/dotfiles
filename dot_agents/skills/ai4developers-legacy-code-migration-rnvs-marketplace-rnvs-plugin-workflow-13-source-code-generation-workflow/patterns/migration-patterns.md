# Database Migration Patterns

Patterns for Flyway migrations in CHANGE mode.

## Pattern 1: Create New Table

```sql
-- V${version}__create_${table_name}_table.sql
-- Feature: ${feature_name}
-- Implements: ${business_rule_ids}
-- RNVS Source: ${rnvs_source}

CREATE TABLE ${table_name} (
    id BIGSERIAL PRIMARY KEY,

    -- Business fields
    ${column_name} ${data_type} ${constraints},

    -- Foreign keys
    ${parent_table}_id BIGINT REFERENCES ${parent_table}(id),

    -- Audit fields
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),

    -- Soft delete
    deleted_at TIMESTAMP
);

-- Indexes for frequently queried columns
CREATE INDEX idx_${table_name}_${column_name} ON ${table_name}(${column_name});
CREATE INDEX idx_${table_name}_${parent_table}_id ON ${table_name}(${parent_table}_id);
CREATE INDEX idx_${table_name}_created_at ON ${table_name}(created_at);

-- Composite index for common queries
CREATE INDEX idx_${table_name}_${column1}_${column2} ON ${table_name}(${column1}, ${column2});

COMMENT ON TABLE ${table_name} IS '${table_description}';
COMMENT ON COLUMN ${table_name}.${column_name} IS '${column_description}';
```

### Example: Create feature_configurations table

```sql
-- V2__create_feature_configurations_table.sql
-- Feature: Feature Configuration Management
-- Implements: BR-FEAT-005, BR-FEAT-006
-- RNVS Source: RNVS.Feature.Config (config_handler.tcl)

CREATE TABLE feature_configurations (
    id BIGSERIAL PRIMARY KEY,

    -- Business fields
    feature_id BIGINT NOT NULL REFERENCES features(id),
    config_key VARCHAR(255) NOT NULL,
    config_value TEXT,
    config_type VARCHAR(50) NOT NULL DEFAULT 'STRING',
    is_encrypted BOOLEAN NOT NULL DEFAULT FALSE,

    -- Validation
    validation_status VARCHAR(50),
    validated_at TIMESTAMP,
    validated_by VARCHAR(255),

    -- Audit fields
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

-- Indexes
CREATE INDEX idx_feature_config_feature_id ON feature_configurations(feature_id);
CREATE UNIQUE INDEX idx_feature_config_unique ON feature_configurations(feature_id, config_key);
CREATE INDEX idx_feature_config_validation ON feature_configurations(validation_status);

COMMENT ON TABLE feature_configurations IS 'Configuration key-value pairs for features';
COMMENT ON COLUMN feature_configurations.config_type IS 'Type: STRING, INTEGER, BOOLEAN, JSON';
```

---

## Pattern 2: Add Column to Existing Table

```sql
-- V${version}__add_${column_name}_to_${table_name}.sql
-- Feature: ${feature_name}
-- Implements: ${business_rule_id}
-- RNVS Source: ${rnvs_source}

-- Add new column
ALTER TABLE ${table_name}
ADD COLUMN ${column_name} ${data_type} ${constraints};

-- Set default for existing rows (if needed)
UPDATE ${table_name}
SET ${column_name} = ${default_value}
WHERE ${column_name} IS NULL;

-- Add NOT NULL constraint after population (if required)
ALTER TABLE ${table_name}
ALTER COLUMN ${column_name} SET NOT NULL;

-- Add index if frequently queried
CREATE INDEX idx_${table_name}_${column_name} ON ${table_name}(${column_name});

COMMENT ON COLUMN ${table_name}.${column_name} IS '${column_description}';
```

### Example: Add validation columns to features

```sql
-- V3__add_validation_columns_to_features.sql
-- Feature: Feature Validation
-- Implements: BR-FEAT-005
-- RNVS Source: RNVS.Feature.ValidateConfig

-- Add validation status column
ALTER TABLE features
ADD COLUMN validation_status VARCHAR(50);

-- Add validation timestamp
ALTER TABLE features
ADD COLUMN validated_at TIMESTAMP;

-- Add validator reference
ALTER TABLE features
ADD COLUMN validated_by VARCHAR(255);

-- Set default for existing rows
UPDATE features
SET validation_status = 'NOT_VALIDATED'
WHERE validation_status IS NULL;

-- Add index for status queries
CREATE INDEX idx_features_validation_status ON features(validation_status);

COMMENT ON COLUMN features.validation_status IS 'Validation status: NOT_VALIDATED, VALID, INVALID';
COMMENT ON COLUMN features.validated_at IS 'Timestamp of last validation';
```

---

## Pattern 3: Add Index

```sql
-- V${version}__add_${index_name}_index.sql
-- Feature: ${feature_name}
-- Purpose: Performance optimization for ${query_description}

-- Single column index
CREATE INDEX idx_${table_name}_${column_name} ON ${table_name}(${column_name});

-- Composite index
CREATE INDEX idx_${table_name}_${column1}_${column2} ON ${table_name}(${column1}, ${column2});

-- Partial index (PostgreSQL)
CREATE INDEX idx_${table_name}_active ON ${table_name}(${column_name})
WHERE deleted_at IS NULL;

-- Unique index
CREATE UNIQUE INDEX idx_${table_name}_${column_name}_unique ON ${table_name}(${column_name});
```

---

## Pattern 4: Add Foreign Key

```sql
-- V${version}__add_${column_name}_fk_to_${table_name}.sql
-- Feature: ${feature_name}
-- Purpose: Link ${table_name} to ${referenced_table}

-- Add column
ALTER TABLE ${table_name}
ADD COLUMN ${referenced_table}_id BIGINT;

-- Add foreign key constraint
ALTER TABLE ${table_name}
ADD CONSTRAINT fk_${table_name}_${referenced_table}
    FOREIGN KEY (${referenced_table}_id)
    REFERENCES ${referenced_table}(id)
    ON DELETE ${on_delete_action};  -- CASCADE, SET NULL, RESTRICT

-- Add index for FK performance
CREATE INDEX idx_${table_name}_${referenced_table}_id ON ${table_name}(${referenced_table}_id);
```

---

## Pattern 5: Create Enum Type (PostgreSQL)

```sql
-- V${version}__create_${enum_name}_type.sql
-- Feature: ${feature_name}

-- Create enum type
CREATE TYPE ${enum_name} AS ENUM (
    '${value1}',
    '${value2}',
    '${value3}'
);

-- Use in table
ALTER TABLE ${table_name}
ADD COLUMN ${column_name} ${enum_name};
```

---

## Pattern 6: Data Migration

```sql
-- V${version}__migrate_${description}.sql
-- Feature: ${feature_name}
-- Purpose: Migrate existing data for ${reason}

-- Step 1: Create temporary column
ALTER TABLE ${table_name}
ADD COLUMN ${new_column}_temp ${data_type};

-- Step 2: Migrate data
UPDATE ${table_name}
SET ${new_column}_temp = ${transformation_expression};

-- Step 3: Drop old column
ALTER TABLE ${table_name}
DROP COLUMN ${old_column};

-- Step 4: Rename new column
ALTER TABLE ${table_name}
RENAME COLUMN ${new_column}_temp TO ${new_column};
```

---

## Naming Conventions

| Migration Type | Naming Pattern |
|----------------|----------------|
| Create table | `V{N}__create_{table_name}_table.sql` |
| Add column | `V{N}__add_{column}_to_{table}.sql` |
| Add index | `V{N}__add_{index_name}_index.sql` |
| Add FK | `V{N}__add_{column}_fk_to_{table}.sql` |
| Data migration | `V{N}__migrate_{description}.sql` |
| Drop column | `V{N}__drop_{column}_from_{table}.sql` |

---

## Version Numbering

For CHANGE mode:
1. Find highest existing version number in project
2. Use next sequential number
3. Example: If V5 exists, use V6

```sql
-- Check existing migrations in project
-- Flyway tracks applied migrations in flyway_schema_history table
```

---

## Anti-Patterns to Avoid

1. **Don't use DROP without backup**: Always have rollback plan
2. **Don't modify existing migrations**: Create new migration instead
3. **Don't use long transactions**: Break into smaller migrations
4. **Don't forget indexes on FKs**: Always index foreign key columns
5. **Don't use reserved words**: Quote them if necessary
6. **Don't skip comments**: Document purpose and business rule
