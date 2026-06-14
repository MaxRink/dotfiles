# Oracle/PL-SQL Analysis Reference

## PL/SQL Block Structure

```
CREATE OR REPLACE PACKAGE BODY schema.package_name AS
  -- Private variables
  -- Procedure/Function implementations
  PROCEDURE proc_name(p_param IN type) IS
    -- Local declarations
  BEGIN
    -- Executable statements
  EXCEPTION
    WHEN exception_name THEN
      -- Handler
  END proc_name;
END package_name;
```

## Patterns to Detect

### PRAGMA Directives

| PRAGMA                 | Meaning                             | Migration Impact                 |
| ---------------------- | ----------------------------------- | -------------------------------- |
| AUTONOMOUS_TRANSACTION | Independent commit/rollback         | Needs equivalent isolation       |
| EXCEPTION_INIT         | Map Oracle error to named exception | Map to target DB errors          |
| RESTRICT_REFERENCES    | Purity constraints                  | May affect function usage in SQL |
| SERIALLY_REUSABLE      | Package state reset between calls   | Affects caching behavior         |

### Cursor Patterns

| Pattern         | Detection                        | Notes                             |
| --------------- | -------------------------------- | --------------------------------- |
| Explicit cursor | `CURSOR name IS SELECT...`       | Full control of fetch lifecycle   |
| Implicit cursor | `FOR rec IN (SELECT...)`         | Simpler, auto-managed             |
| REF CURSOR      | `TYPE ref_cur IS REF CURSOR`     | Dynamic, passed between modules   |
| BULK COLLECT    | `FETCH cursor BULK COLLECT INTO` | Performance-critical batch fetch  |
| Cursor variable | `SYS_REFCURSOR`                  | Often used for result set returns |

### Bulk Operations

| Pattern         | Purpose                         | Performance Impact             |
| --------------- | ------------------------------- | ------------------------------ |
| FORALL          | Bulk DML (insert/update/delete) | 10-100x faster than row-by-row |
| BULK COLLECT    | Bulk fetch into collection      | Reduces context switches       |
| SAVE EXCEPTIONS | Continue on error in FORALL     | Error handling complexity      |
| LIMIT clause    | Batch processing                | Memory management              |

### Oracle Built-in Package Usage

| Package        | Purpose                   | Migration Concern                        |
| -------------- | ------------------------- | ---------------------------------------- |
| DBMS_OUTPUT    | Debug printing            | Replace with logging                     |
| DBMS_SCHEDULER | Job scheduling            | Replace with external scheduler          |
| DBMS_LOB       | Large object manipulation | Map to target LOB handling               |
| DBMS_SQL       | Dynamic SQL               | Often replaceable with EXECUTE IMMEDIATE |
| DBMS_PIPE      | Inter-session messaging   | Replace with queuing                     |
| UTL_FILE       | Server-side file I/O      | Security and path concerns               |
| UTL_HTTP       | HTTP calls from DB        | Move to application layer                |
| UTL_MAIL       | Email from DB             | Move to application layer                |
| DBMS_AQ        | Advanced Queuing          | Replace with message broker              |
| DBMS_CRYPTO    | Encryption                | Map to target crypto API                 |
| DBMS_XMLGEN    | XML generation            | Replace with app-layer XML               |
| DBMS_METADATA  | DDL generation            | Build-time only                          |

### Trigger Patterns

| Type              | Fires                  | Use Case                                 |
| ----------------- | ---------------------- | ---------------------------------------- |
| BEFORE INSERT row | Before each row insert | Sequence-based ID generation, validation |
| AFTER INSERT row  | After each row insert  | Audit logging, cascade                   |
| BEFORE UPDATE row | Before each row update | Validation, computed columns             |
| INSTEAD OF        | On view DML            | Updatable views                          |
| Compound trigger  | Multiple timing points | Mutating table workaround                |
| System trigger    | DDL/logon/startup      | Schema audit, session init               |

### Dynamic SQL Patterns

| Pattern                       | Risk Level | Notes                    |
| ----------------------------- | ---------- | ------------------------ |
| EXECUTE IMMEDIATE with bind   | Low        | Safe from injection      |
| EXECUTE IMMEDIATE with concat | HIGH       | SQL injection risk       |
| DBMS_SQL.PARSE                | Medium     | Complex but flexible     |
| Native dynamic SQL in cursor  | Medium     | Hard to trace statically |

## Data Type Mapping Concerns

| Oracle Type              | Typical Target     | Gotcha                         |
| ------------------------ | ------------------ | ------------------------------ |
| NUMBER(p,s)              | DECIMAL/NUMERIC    | Precision loss if p>38         |
| VARCHAR2(n BYTE)         | VARCHAR            | BYTE vs CHAR semantics differ  |
| DATE                     | TIMESTAMP          | Oracle DATE includes time!     |
| TIMESTAMP WITH TIME ZONE | TIMESTAMPTZ        | Zone normalization             |
| RAW / LONG RAW           | BYTEA/BLOB         | Deprecated in Oracle           |
| CLOB/BLOB                | TEXT/BYTEA         | Size limits differ             |
| XMLTYPE                  | XML/JSON           | Often over-engineered          |
| INTERVAL                 | INTERVAL           | Syntax differences             |
| ROWID                    | N/A                | Physical address, not portable |
| BFILE                    | External reference | OS-dependent                   |

## Complexity Indicators

| Signal                                | Meaning                                   |
| ------------------------------------- | ----------------------------------------- |
| > 5 PRAGMA AUTONOMOUS_TRANSACTION     | Heavy use of isolated transactions        |
| > 10 DBMS\_ package calls             | Deep Oracle platform dependency           |
| EXECUTE IMMEDIATE with string concat  | Dynamic SQL, injection risk               |
| Multiple mutating-table workarounds   | Complex trigger cascades                  |
| REF CURSOR returned from package      | Dynamic interface, hard to trace          |
| %ROWTYPE / %TYPE                      | Schema-coupled declarations               |
| Package global state (body variables) | Session-stateful logic                    |
| DBMS_SCHEDULER jobs                   | Embedded scheduling (extract to external) |
