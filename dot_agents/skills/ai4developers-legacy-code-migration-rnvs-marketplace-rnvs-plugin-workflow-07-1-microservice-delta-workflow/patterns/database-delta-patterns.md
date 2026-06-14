# Database Delta Design Patterns

**Purpose**: Design patterns for database schema changes in delta model (tables_to_add, columns_to_add, indexes_to_add).

**Context**: Phase 7.1 captures ONLY changes to existing microservice databases, not complete database schemas.

---

## Tables to Add

### Requirements

Every table in `tables_to_add` MUST include:

1. **Table Name**: Following VNRM naming conventions (lowercase, underscores)
2. **Purpose**: Business description of what this table stores
3. **Complete DDL**: Executable PostgreSQL CREATE TABLE statement
4. **Primary Key**: UUID or composite key
5. **Foreign Keys**: With ON DELETE/UPDATE clauses
6. **Constraints**: CHECK constraints for business rules
7. **Optimistic Locking**: Version column for concurrency control
8. **Audit Columns**: created_at, updated_at, created_by, updated_by
9. **Indexes**: For foreign keys and query columns
10. **RNVS Source**: Attribution to legacy database tables

### PostgreSQL DDL Template

```sql
-- Table name: descriptive_business_entity (plural, lowercase, underscores)
CREATE TABLE table_name (
  -- Primary key (UUID recommended for distributed systems)
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Business columns
  business_field_1 VARCHAR(100) NOT NULL,
  business_field_2 INTEGER NOT NULL,
  business_field_3 TIMESTAMP,
  status VARCHAR(20) NOT NULL DEFAULT 'PENDING',

  -- Foreign keys to other tables
  related_entity_id UUID NOT NULL,
  CONSTRAINT fk_table_related FOREIGN KEY (related_entity_id)
    REFERENCES related_table(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  -- Business rule constraints
  CONSTRAINT chk_table_status CHECK (status IN ('PENDING', 'ACTIVE', 'INACTIVE', 'DELETED')),
  CONSTRAINT chk_table_field2_positive CHECK (business_field_2 >= 0),

  -- Optimistic locking (prevents concurrent update conflicts)
  version INTEGER NOT NULL DEFAULT 0,

  -- Audit columns (track changes)
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(100),
  updated_by VARCHAR(100)
);

-- Index for foreign key (performance)
CREATE INDEX idx_table_related_entity ON table_name(related_entity_id);

-- Index for common queries
CREATE INDEX idx_table_status_created ON table_name(status, created_at DESC);

-- Unique constraint (if business requires uniqueness)
CREATE UNIQUE INDEX uidx_table_business_field1 ON table_name(business_field_1)
  WHERE status != 'DELETED';

-- Comment for documentation
COMMENT ON TABLE table_name IS 'Business purpose of this table';
COMMENT ON COLUMN table_name.business_field_1 IS 'Description of this field';
```

### Complete JSON Structure

```json
{
  "table_name": "portability_requests",
  "purpose": "Stores number portability requests from carriers. Tracks porting workflow from initial request through completion or cancellation.",
  "source": {
    "rnvs_table": "PORTIERUNGSANTRAEGE",
    "rnvs_file": "database/schema/rnvs_tables.sql:456",
    "mapping_notes": "RNVS table was denormalized with carrier info embedded. VNRM version normalizes with FK to carriers table."
  },
  "ddl": "CREATE TABLE portability_requests (\n  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n  msisdn VARCHAR(15) NOT NULL,\n  donor_carrier_id UUID NOT NULL,\n  recipient_carrier_id UUID NOT NULL,\n  desired_port_date DATE NOT NULL,\n  actual_port_date DATE,\n  status VARCHAR(30) NOT NULL DEFAULT 'PENDING_VALIDATION',\n  customer_consent BOOLEAN NOT NULL DEFAULT false,\n  \n  -- Foreign keys\n  CONSTRAINT fk_port_req_donor FOREIGN KEY (donor_carrier_id) \n    REFERENCES carriers(id) ON DELETE RESTRICT ON UPDATE CASCADE,\n  CONSTRAINT fk_port_req_recipient FOREIGN KEY (recipient_carrier_id) \n    REFERENCES carriers(id) ON DELETE RESTRICT ON UPDATE CASCADE,\n  \n  -- Business rules\n  CONSTRAINT chk_port_req_status CHECK (status IN ('PENDING_VALIDATION', 'VALIDATED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'FAILED')),\n  CONSTRAINT chk_port_req_carriers_different CHECK (donor_carrier_id != recipient_carrier_id),\n  CONSTRAINT chk_port_req_msisdn_format CHECK (msisdn ~ '^49[1-9][0-9]{9,10}$'),\n  CONSTRAINT chk_port_req_consent CHECK (customer_consent = true),\n  \n  -- Optimistic locking\n  version INTEGER NOT NULL DEFAULT 0,\n  \n  -- Audit\n  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,\n  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,\n  created_by VARCHAR(100),\n  updated_by VARCHAR(100)\n);",
  "indexes": [
    {
      "name": "idx_port_req_msisdn",
      "ddl": "CREATE INDEX idx_port_req_msisdn ON portability_requests(msisdn);",
      "purpose": "Lookup portability requests by phone number"
    },
    {
      "name": "idx_port_req_status_date",
      "ddl": "CREATE INDEX idx_port_req_status_date ON portability_requests(status, desired_port_date);",
      "purpose": "Find requests by status and scheduled date for batch processing"
    },
    {
      "name": "idx_port_req_donor",
      "ddl": "CREATE INDEX idx_port_req_donor ON portability_requests(donor_carrier_id);",
      "purpose": "FK index for donor carrier joins and carrier-specific queries"
    },
    {
      "name": "idx_port_req_recipient",
      "ddl": "CREATE INDEX idx_port_req_recipient ON portability_requests(recipient_carrier_id);",
      "purpose": "FK index for recipient carrier joins and carrier-specific queries"
    },
    {
      "name": "uidx_port_req_active_msisdn",
      "ddl": "CREATE UNIQUE INDEX uidx_port_req_active_msisdn ON portability_requests(msisdn) WHERE status IN ('PENDING_VALIDATION', 'VALIDATED', 'IN_PROGRESS');",
      "purpose": "Enforce business rule: only one active portability request per MSISDN"
    }
  ],
  "business_rules_enforced": [
    "BR-PORT-002: Donor and recipient carriers must be different",
    "BR-PORT-001: MSISDN must be valid German mobile number (E.164)",
    "BR-PORT-004: Customer consent required",
    "BR-PORT-005: Only one active portability request per MSISDN"
  ]
}
```

---

## Columns to Add

### Requirements

Every column in `columns_to_add` MUST include:

1. **Table Name**: Existing table being modified
2. **Column Name**: New column name following conventions
3. **DDL**: ALTER TABLE ADD COLUMN statement
4. **Purpose**: Why this column is needed
5. **Data Type**: PostgreSQL data type with constraints
6. **Default Value**: For existing rows (if NOT NULL)
7. **Migration Strategy**: How to populate existing rows

### Template

```json
{
  "table_name": "existing_table",
  "column_name": "new_column",
  "ddl": "ALTER TABLE existing_table ADD COLUMN new_column VARCHAR(50);",
  "purpose": "Business justification for this column",
  "migration_strategy": "How to handle existing rows (NULL, default value, data migration)"
}
```

### Complete Example: Adding Porting Priority

```json
{
  "table_name": "portability_requests",
  "column_name": "priority",
  "ddl": "ALTER TABLE portability_requests ADD COLUMN priority VARCHAR(20) NOT NULL DEFAULT 'NORMAL';",
  "purpose": "Support priority porting for VIP customers and emergency services. Enables expedited processing workflow.",
  "data_type": {
    "type": "VARCHAR(20)",
    "allowed_values": ["LOW", "NORMAL", "HIGH", "EMERGENCY"],
    "default": "NORMAL"
  },
  "migration_strategy": {
    "existing_rows": "Set to 'NORMAL' for all existing portability requests",
    "business_logic": "Future requests from VIP customer IDs or emergency service MSISDNs automatically set to 'HIGH' or 'EMERGENCY'"
  },
  "additional_constraints": [
    "ALTER TABLE portability_requests ADD CONSTRAINT chk_port_req_priority CHECK (priority IN ('LOW', 'NORMAL', 'HIGH', 'EMERGENCY'));"
  ],
  "source": {
    "rnvs_column": "PRIORITAET",
    "rnvs_table": "PORTIERUNGSANTRAEGE",
    "mapping_notes": "RNVS used integer codes (1=LOW, 2=NORMAL, 3=HIGH, 9=EMERGENCY). VNRM uses string enums for clarity."
  }
}
```

### Zero-Downtime Migration Pattern

For columns that need complex migrations:

```json
{
  "table_name": "number_allocations",
  "column_name": "allocation_metadata",
  "ddl": "ALTER TABLE number_allocations ADD COLUMN allocation_metadata JSONB;",
  "purpose": "Store flexible metadata for different allocation types without schema changes",
  "migration_strategy": {
    "phase_1": "Add nullable column (ALTER TABLE ... ADD COLUMN allocation_metadata JSONB;)",
    "phase_2": "Backfill existing rows via UPDATE with calculated JSON (batch process, non-blocking)",
    "phase_3": "After backfill complete, add NOT NULL constraint (ALTER TABLE ... ALTER COLUMN allocation_metadata SET NOT NULL;)"
  },
  "migration_script": "scripts/backfill-allocation-metadata.sql"
}
```

---

## Indexes to Add

### Requirements

Every index in `indexes_to_add` MUST include:

1. **Table Name**: Table for the index
2. **Index Name**: Following naming convention (idx_ or uidx_)
3. **DDL**: CREATE INDEX statement
4. **Columns**: Columns in index (order matters)
5. **Purpose**: Query optimization rationale
6. **Index Type**: B-tree (default), UNIQUE, partial WHERE clause

### Naming Conventions

- **Regular index**: `idx_tablename_column1_column2`
- **Unique index**: `uidx_tablename_column1_column2`
- **Partial index**: Include `_partial` suffix

### Template

```json
{
  "table_name": "table_name",
  "index_name": "idx_table_column1_column2",
  "columns": ["column1", "column2"],
  "ddl": "CREATE INDEX idx_table_column1_column2 ON table_name(column1, column2);",
  "purpose": "Optimize query: SELECT * FROM table_name WHERE column1 = ? AND column2 = ?",
  "index_type": "B-tree",
  "cardinality_estimate": "High selectivity on column1, low on column2"
}
```

### Complete Example: Composite Index for Query Optimization

```json
{
  "table_name": "portability_requests",
  "index_name": "idx_port_req_carrier_status_date",
  "columns": ["recipient_carrier_id", "status", "desired_port_date"],
  "ddl": "CREATE INDEX idx_port_req_carrier_status_date ON portability_requests(recipient_carrier_id, status, desired_port_date DESC);",
  "purpose": "Optimize dashboard query: Show pending/in-progress portability requests for a carrier ordered by scheduled date. Supports carrier-specific workflow views.",
  "index_type": "B-tree composite (3 columns)",
  "query_pattern": "SELECT * FROM portability_requests WHERE recipient_carrier_id = ? AND status IN ('PENDING_VALIDATION', 'IN_PROGRESS') ORDER BY desired_port_date DESC LIMIT 100;",
  "cardinality_estimate": {
    "recipient_carrier_id": "~50 distinct carriers (high selectivity)",
    "status": "~6 distinct statuses (low selectivity)",
    "desired_port_date": "Continuous range (high selectivity)"
  },
  "performance_impact": {
    "without_index": "Full table scan ~500ms for 1M rows",
    "with_index": "Index scan ~5ms",
    "index_size_estimate": "~20MB for 1M rows"
  }
}
```

### Partial Index Example: Active Records Only

```json
{
  "table_name": "portability_requests",
  "index_name": "uidx_port_req_active_msisdn_partial",
  "columns": ["msisdn"],
  "ddl": "CREATE UNIQUE INDEX uidx_port_req_active_msisdn_partial ON portability_requests(msisdn) WHERE status IN ('PENDING_VALIDATION', 'VALIDATED', 'IN_PROGRESS');",
  "purpose": "Enforce business rule BR-PORT-005: Only one active portability request per MSISDN. Partial index excludes completed/cancelled requests to save space.",
  "index_type": "Unique partial (WHERE clause)",
  "business_rule": "BR-PORT-005: MSISDN must not have active portability request",
  "space_savings": "~60% smaller than full unique index (excludes historical completed requests)"
}
```

### Covering Index Example: Index-Only Scans

```json
{
  "table_name": "number_allocations",
  "index_name": "idx_num_alloc_covering_lookup",
  "columns": ["msisdn", "carrier_id", "allocation_date", "status"],
  "ddl": "CREATE INDEX idx_num_alloc_covering_lookup ON number_allocations(msisdn) INCLUDE (carrier_id, allocation_date, status);",
  "purpose": "Covering index for number lookup API. All required columns in index (index-only scan, no heap access).",
  "index_type": "B-tree with INCLUDE columns (PostgreSQL 11+)",
  "query_pattern": "SELECT carrier_id, allocation_date, status FROM number_allocations WHERE msisdn = ?;",
  "performance_benefit": "Index-only scan (no table access) ~40% faster than regular index"
}
```

---

## Best Practices

### Table Design

✅ **DO**: Use UUID primary keys for distributed systems and service independence
✅ **DO**: Add version column for optimistic locking (prevents lost updates)
✅ **DO**: Add audit columns (created_at, updated_at, created_by, updated_by)
✅ **DO**: Use CHECK constraints for business rules (data integrity at database level)
✅ **DO**: Define foreign keys with appropriate ON DELETE/UPDATE actions

❌ **DON'T**: Use auto-increment IDs (not distributed-friendly)
❌ **DON'T**: Store business logic only in application (use DB constraints)
❌ **DON'T**: Omit indexes on foreign keys (performance issue)
❌ **DON'T**: Use generic column names (status, type, code without context)

### Constraint Design

**Cascading Deletes** (ON DELETE CASCADE):
- Use when child records have no meaning without parent
- Example: Order items deleted when order deleted

**Restrict Deletes** (ON DELETE RESTRICT):
- Use when child records should prevent parent deletion
- Example: Cannot delete carrier if portability requests exist

**Set Null** (ON DELETE SET NULL):
- Use when relationship is optional
- Example: Deleted user ID set to NULL in audit logs

### Index Design

**When to add indexes**:
- Foreign key columns (always)
- Columns in WHERE clauses (frequently queried)
- Columns in ORDER BY (sorting)
- Columns in GROUP BY (aggregation)
- Composite indexes for multi-column queries

**When NOT to add indexes**:
- Low cardinality columns alone (e.g., boolean, single-digit enums)
- Write-heavy tables with few reads (index maintenance overhead)
- Very small tables (< 1000 rows - full scan faster)

### Migration Strategy

**Safe column addition**:
1. Add column as NULL
2. Backfill data (batch updates, non-blocking)
3. Add NOT NULL constraint after backfill
4. Add indexes after data population

**Safe table addition**:
1. Create table
2. Create indexes
3. Populate initial data (if any)
4. Deploy application code that uses table
5. No downtime risk

### RNVS Source Attribution

```json
{
  "source": {
    "rnvs_table": "PORTIERUNGSANTRAEGE",
    "rnvs_columns": ["MSISDN", "DONOR_ID", "EMPFAENGER_ID", "WUNSCHDATUM"],
    "rnvs_file": "database/schema/rnvs_tables.sql:456",
    "mapping_notes": "RNVS table denormalized. VNRM version normalized with FK references.",
    "business_logic_differences": "RNVS validated carrier IDs in application. VNRM enforces via FK constraints."
  }
}
```

---

## Database Migration Tools

### Flyway Migration Naming

```
V001__create_portability_requests_table.sql
V002__add_portability_priority_column.sql
V003__add_portability_indexes.sql
```

### Liquibase Changeset

```xml
<changeSet id="create-portability-requests-1" author="migration-phase7.1">
  <createTable tableName="portability_requests">
    <column name="id" type="UUID" defaultValueComputed="gen_random_uuid()">
      <constraints primaryKey="true"/>
    </column>
    <!-- Additional columns -->
  </createTable>
</changeSet>
```

---

## Related Patterns

- See `api-delta-patterns.md` for APIs that query these tables
- See `event-delta-patterns.md` for events triggered by database changes
- See `../examples/` for complete database change examples

---

**Use these patterns to ensure robust, performant, maintainable database schemas in your delta model.**
