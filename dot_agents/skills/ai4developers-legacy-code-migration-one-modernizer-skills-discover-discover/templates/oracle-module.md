# {{SCHEMA_NAME}} — Oracle Database Module

## Purpose

{{What business function this schema/set of DB objects serves}}

## Schema Objects

### Tables

| Table          | Rows (est.)  | Partitioned? | Description          |
| -------------- | ------------ | ------------ | -------------------- |
| {{table_name}} | {{estimate}} | {{yes/no}}   | {{business purpose}} |

### Views

| View     | Base Tables | Materialized? | Purpose     |
| -------- | ----------- | ------------- | ----------- |
| {{name}} | {{tables}}  | {{yes/no}}    | {{purpose}} |

### Sequences

| Sequence | Used By        | Increment | Cache |
| -------- | -------------- | --------- | ----- |
| {{name}} | {{table/proc}} | {{n}}     | {{n}} |

### DB Links

| Link Name | Target DB    | Used By   | Purpose        |
| --------- | ------------ | --------- | -------------- |
| {{name}}  | {{host/sid}} | {{procs}} | {{data sync?}} |

## Stored Procedures & Functions

| Name     | Type          | Parameters | Tables Accessed | Called By   | Complexity |
| -------- | ------------- | ---------- | --------------- | ----------- | ---------- |
| {{name}} | {{proc/func}} | {{list}}   | {{tables}}      | {{callers}} | {{lines}}  |

## Packages

### {{PACKAGE_NAME}}

**Spec**: `{{file:line}}`
**Body**: `{{file:line}}`

| Procedure/Function | Visibility         | Parameters | Purpose  |
| ------------------ | ------------------ | ---------- | -------- |
| {{name}}           | {{public/private}} | {{sig}}    | {{what}} |

## Triggers

| Trigger  | Fires On       | Event                  | Purpose          |
| -------- | -------------- | ---------------------- | ---------------- |
| {{name}} | {{table_name}} | {{BEFORE INSERT/etc.}} | {{what it does}} |

## Dependencies (Procedure → Table)

| Procedure | Reads From | Writes To  | Transaction Boundary |
| --------- | ---------- | ---------- | -------------------- |
| {{name}}  | {{tables}} | {{tables}} | {{autonomous?}}      |

## Partitioning Strategy

| Table    | Partition Type      | Key Column | Partitions | Subpartitions? |
| -------- | ------------------- | ---------- | ---------- | -------------- |
| {{name}} | {{range/list/hash}} | {{col}}    | {{count}}  | {{yes/no}}     |

## Data Volume Profile

| Table    | Row Count | Size (GB) | Growth/Month | Archival?  |
| -------- | --------- | --------- | ------------ | ---------- |
| {{name}} | {{count}} | {{size}}  | {{rate}}     | {{yes/no}} |

## PL/SQL Patterns Detected

- [ ] BULK COLLECT usage: {{where}}
- [ ] FORALL usage: {{where}}
- [ ] PRAGMA AUTONOMOUS_TRANSACTION: {{where}}
- [ ] Dynamic SQL (EXECUTE IMMEDIATE): {{where}}
- [ ] DBMS_SCHEDULER jobs: {{where}}
- [ ] UTL_FILE (file I/O): {{where}}
- [ ] DBMS_OUTPUT: {{where}}
- [ ] Pipelined functions: {{where}}

## Business Rules (in DB Logic)

| #   | Rule            | Location (file:line) | Confidence                   |
| --- | --------------- | -------------------- | ---------------------------- |
| 1   | {{description}} | {{file:line}}        | {{clear/inferred/ambiguous}} |

## Unknowns

- {{Any unclear trigger logic, undocumented stored procedures, missing package specs}}
