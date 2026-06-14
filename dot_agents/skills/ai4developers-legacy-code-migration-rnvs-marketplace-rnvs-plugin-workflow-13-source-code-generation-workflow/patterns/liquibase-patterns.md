# Liquibase Migration Patterns

Patterns for Liquibase database migrations in VNRM microservices.

**Note**: Some VNRM services use Liquibase instead of Flyway. Check `pom.xml` for which tool is used.

---

## Pattern 1: Create Table Changelog

Standard table creation:

```yaml
# db/changelog/changes/V${version}__create_${table_name}_table.yaml
databaseChangeLog:
  - changeSet:
      id: ${version}-create-${table_name}
      author: ${author}
      comment: "Create ${table_name} table for ${feature_name}. Implements: ${business_rule}"
      changes:
        - createTable:
            tableName: T_${TABLE_NAME}
            columns:
              - column:
                  name: id
                  type: BIGINT
                  autoIncrement: true
                  constraints:
                    primaryKey: true
                    primaryKeyName: pk_${table_name}

              # Business fields
              - column:
                  name: ${column_name}
                  type: VARCHAR(255)
                  constraints:
                    nullable: false

              - column:
                  name: status
                  type: VARCHAR(50)
                  constraints:
                    nullable: false
                  defaultValue: 'NEW'

              # Foreign key
              - column:
                  name: ${parent}_id
                  type: BIGINT
                  constraints:
                    nullable: false
                    foreignKeyName: fk_${table_name}_${parent}
                    references: T_${PARENT}(id)

              # Audit fields
              - column:
                  name: created_at
                  type: TIMESTAMP
                  constraints:
                    nullable: false
                  defaultValueComputed: CURRENT_TIMESTAMP

              - column:
                  name: updated_at
                  type: TIMESTAMP

              - column:
                  name: created_by
                  type: VARCHAR(255)

              - column:
                  name: updated_by
                  type: VARCHAR(255)

              - column:
                  name: deleted_at
                  type: TIMESTAMP

        # Indexes
        - createIndex:
            tableName: T_${TABLE_NAME}
            indexName: idx_${table_name}_status
            columns:
              - column:
                  name: status

        - createIndex:
            tableName: T_${TABLE_NAME}
            indexName: idx_${table_name}_${parent}_id
            columns:
              - column:
                  name: ${parent}_id

        - createIndex:
            tableName: T_${TABLE_NAME}
            indexName: idx_${table_name}_created_at
            columns:
              - column:
                  name: created_at
                  descending: true
```

---

## Pattern 2: Add Columns Changelog

Adding columns to existing table:

```yaml
# db/changelog/changes/V${version}__add_${feature}_columns.yaml
databaseChangeLog:
  - changeSet:
      id: ${version}-add-${feature}-columns
      author: ${author}
      comment: "Add ${feature} columns to T_${TABLE_NAME}. Implements: ${business_rule}"
      changes:
        # Add new columns
        - addColumn:
            tableName: T_${TABLE_NAME}
            columns:
              - column:
                  name: queue_status
                  type: VARCHAR(50)
                  remarks: "Queue workflow status"

              - column:
                  name: escalation_level
                  type: INT
                  defaultValueNumeric: 0
                  remarks: "Escalation level (0=none, 1=L1, 2=L2)"

              - column:
                  name: assigned_to
                  type: VARCHAR(255)
                  remarks: "Currently assigned user"

              - column:
                  name: deadline
                  type: TIMESTAMP
                  remarks: "Resolution deadline for SLA tracking"

        # Set default for existing rows
        - update:
            tableName: T_${TABLE_NAME}
            columns:
              - column:
                  name: queue_status
                  value: 'NEW'
            where: queue_status IS NULL

        # Add NOT NULL constraint after population
        - addNotNullConstraint:
            tableName: T_${TABLE_NAME}
            columnName: queue_status
            columnDataType: VARCHAR(50)

        # Add index for new column
        - createIndex:
            tableName: T_${TABLE_NAME}
            indexName: idx_${table_name}_queue_status
            columns:
              - column:
                  name: queue_status
```

---

## Pattern 3: Create History Table

Audit/history table creation:

```yaml
# db/changelog/changes/V${version}__create_${parent}_history_table.yaml
databaseChangeLog:
  - changeSet:
      id: ${version}-create-${parent}-history
      author: ${author}
      comment: "Create history table for ${parent} status changes. Implements: ${audit_rule}"
      changes:
        - createTable:
            tableName: T_${PARENT}_HISTORY
            columns:
              - column:
                  name: id
                  type: BIGINT
                  autoIncrement: true
                  constraints:
                    primaryKey: true
                    primaryKeyName: pk_${parent}_history

              - column:
                  name: ${parent}_id
                  type: BIGINT
                  constraints:
                    nullable: false
                    foreignKeyName: fk_${parent}_history_${parent}
                    references: T_${PARENT}(id)
                    deleteCascade: true

              - column:
                  name: old_status
                  type: VARCHAR(50)
                  remarks: "Previous status (null for creation)"

              - column:
                  name: new_status
                  type: VARCHAR(50)
                  constraints:
                    nullable: false
                  remarks: "New status after transition"

              - column:
                  name: changed_at
                  type: TIMESTAMP
                  constraints:
                    nullable: false

              - column:
                  name: changed_by
                  type: VARCHAR(255)

              - column:
                  name: reason
                  type: VARCHAR(1000)
                  remarks: "Reason for status change"

              - column:
                  name: notes
                  type: TEXT
                  remarks: "Additional notes"

        - createIndex:
            tableName: T_${PARENT}_HISTORY
            indexName: idx_${parent}_history_${parent}_id
            columns:
              - column:
                  name: ${parent}_id

        - createIndex:
            tableName: T_${PARENT}_HISTORY
            indexName: idx_${parent}_history_changed_at
            columns:
              - column:
                  name: changed_at
                  descending: true
```

---

## Pattern 4: Create Sync Tracking Tables

For external system synchronization:

```yaml
# db/changelog/changes/V${version}__create_${system}_sync_tables.yaml
databaseChangeLog:
  - changeSet:
      id: ${version}-create-sync-status-table
      author: ${author}
      comment: "Create sync status table for ${system} integration"
      changes:
        - createTable:
            tableName: T_${RESOURCE}_SYNC_STATUS
            columns:
              - column:
                  name: id
                  type: BIGINT
                  autoIncrement: true
                  constraints:
                    primaryKey: true

              - column:
                  name: ${resource}_id
                  type: BIGINT
                  constraints:
                    nullable: false
                    unique: true
                    foreignKeyName: fk_sync_status_${resource}
                    references: T_${RESOURCE}(id)

              - column:
                  name: status
                  type: VARCHAR(50)
                  constraints:
                    nullable: false
                  defaultValue: 'PENDING'

              - column:
                  name: retry_count
                  type: INT
                  defaultValueNumeric: 0

              - column:
                  name: max_retries
                  type: INT
                  defaultValueNumeric: 3

              - column:
                  name: last_attempt_at
                  type: TIMESTAMP

              - column:
                  name: next_attempt_at
                  type: TIMESTAMP

              - column:
                  name: last_error
                  type: VARCHAR(2000)

              - column:
                  name: external_reference
                  type: VARCHAR(255)

              - column:
                  name: synced_at
                  type: TIMESTAMP

        - createIndex:
            tableName: T_${RESOURCE}_SYNC_STATUS
            indexName: idx_sync_status_status
            columns:
              - column:
                  name: status

  - changeSet:
      id: ${version}-create-sync-log-table
      author: ${author}
      comment: "Create sync log table for ${system} audit trail"
      changes:
        - createTable:
            tableName: T_${RESOURCE}_SYNC_LOG
            columns:
              - column:
                  name: id
                  type: BIGINT
                  autoIncrement: true
                  constraints:
                    primaryKey: true

              - column:
                  name: ${resource}_id
                  type: BIGINT
                  constraints:
                    nullable: false

              - column:
                  name: operation
                  type: VARCHAR(50)
                  constraints:
                    nullable: false

              - column:
                  name: status
                  type: VARCHAR(50)
                  constraints:
                    nullable: false

              - column:
                  name: request_payload
                  type: TEXT

              - column:
                  name: response_payload
                  type: TEXT

              - column:
                  name: error_message
                  type: VARCHAR(2000)

              - column:
                  name: duration_ms
                  type: BIGINT

              - column:
                  name: created_at
                  type: TIMESTAMP
                  constraints:
                    nullable: false
                  defaultValueComputed: CURRENT_TIMESTAMP

        - createIndex:
            tableName: T_${RESOURCE}_SYNC_LOG
            indexName: idx_sync_log_${resource}_id
            columns:
              - column:
                  name: ${resource}_id

        - createIndex:
            tableName: T_${RESOURCE}_SYNC_LOG
            indexName: idx_sync_log_created_at
            columns:
              - column:
                  name: created_at
                  descending: true
```

---

## Pattern 5: SQL Changelog (Alternative)

Using SQL instead of YAML:

```sql
-- db/changelog/changes/V${version}__${description}.sql
-- liquibase formatted sql

-- changeset ${author}:${version}-${description}
-- comment: ${comment}. Implements: ${business_rule}

CREATE TABLE T_${TABLE_NAME} (
    id BIGSERIAL PRIMARY KEY,

    -- Business fields
    ${column_name} VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'NEW',

    -- Foreign key
    ${parent}_id BIGINT NOT NULL REFERENCES T_${PARENT}(id),

    -- Audit fields
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    deleted_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_${table}_status ON T_${TABLE_NAME}(status);
CREATE INDEX idx_${table}_${parent}_id ON T_${TABLE_NAME}(${parent}_id);
CREATE INDEX idx_${table}_created_at ON T_${TABLE_NAME}(created_at DESC);

COMMENT ON TABLE T_${TABLE_NAME} IS '${table_description}';
COMMENT ON COLUMN T_${TABLE_NAME}.status IS 'Status: NEW, IN_PROGRESS, RESOLVED, CANCELLED';

-- rollback DROP TABLE T_${TABLE_NAME};
```

---

## Pattern 6: Master Changelog

Main changelog file including all changes:

```yaml
# db/changelog/db.changelog-master.yaml
databaseChangeLog:
  - include:
      file: db/changelog/changes/V20260101_001__initial_schema.yaml

  - include:
      file: db/changelog/changes/V20260201_001__add_queue_columns.yaml

  - include:
      file: db/changelog/changes/V20260201_002__create_history_table.yaml

  - include:
      file: db/changelog/changes/V20260203_001__create_sync_tables.yaml
```

---

## Naming Conventions

| Migration Type | Pattern | Example |
|----------------|---------|---------|
| Create table | `V{date}_{seq}__create_{table}_table` | `V20260201_001__create_pm_queue_table` |
| Add columns | `V{date}_{seq}__add_{columns}_to_{table}` | `V20260201_002__add_escalation_to_pm` |
| Create index | `V{date}_{seq}__add_{index}_index` | `V20260201_003__add_status_index` |
| Data migration | `V{date}_{seq}__migrate_{description}` | `V20260201_004__migrate_legacy_status` |

---

## Version Numbering

For CHANGE mode:
1. List existing changelog files in project
2. Determine next version using date + sequence
3. Example: If `V20260201_001` exists, use `V20260201_002` (same day) or `V20260203_001` (new day)

---

## Anti-Patterns to Avoid

1. **Don't modify existing changesets** - Create new changesets instead
2. **Don't use `runOnChange`** for DDL - Only for views/procedures
3. **Don't forget rollback** - Include rollback for each change
4. **Don't use reserved words** - Quote if necessary
5. **Don't skip contexts** - Use contexts for environment-specific changes
6. **Don't forget comments** - Document business rules in changesets
