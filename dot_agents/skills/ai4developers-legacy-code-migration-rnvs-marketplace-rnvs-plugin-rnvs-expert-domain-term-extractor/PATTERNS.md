# Domain Term Extraction Patterns

## Purpose

This document provides comprehensive, battle-tested regex patterns for extracting domain terminology from RNVS legacy code across multiple languages (TCL, PL/SQL, C++, Shell).

These patterns are used during Phase 1 iterative discovery to expand search keywords and achieve 100% code coverage.

## Pattern Categories

### 1. TCL Patterns (Porting Features - Critical)

**1.1 Procedure Definitions**

```regex
proc\s+(\w+)\s*\{
```

- Captures: Procedure names
- Example: `proc check_best_anf {args} {` → `check_best_anf`

**1.2 SqlStoPro Calls (TCL→PL/SQL Bridge)**

```regex
SqlStoPro\s+([\w]+)\.([\w]+)
```

- Captures: Package name and procedure name
- Example: `SqlStoPro p_generator.export_data` → `p_generator`, `export_data`

**1.3 SQL Script Execution**

```regex
exec\s+sqlplus\s+.*?@(\w+)\.sql
```

- Captures: SQL script name
- Example: `exec sqlplus user/pass@abgleich_pdat.sql` → `abgleich_pdat`

**1.4 TCL Source Includes**

```regex
source\s+([\w_/]+)\.tcl
```

- Captures: TCL file name (with path)
- Example: `source ../common/utils.tcl` → `utils`

**1.5 Variable Assignments with Domain Terms**

```regex
set\s+(\w+)\s+
```

- Captures: Variable names (filter for business domain terms)
- Example: `set bestand_file "data.txt"` → `bestand_file`

**1.6 Procedure Calls**

```regex
(\w+)\s+[\$\{]
```

- Captures: Procedure invocations
- Example: `generatorbestgesamt $args` → `generatorbestgesamt`

### 2. PL/SQL Patterns (Database Layer - Critical)

**2.1 Procedure Definitions**

```regex
PROCEDURE\s+(\w+)\s*[\(\s]
```

- Captures: Procedure names
- Example: `PROCEDURE export_pda_data(` → `export_pda_data`

**2.2 Function Definitions**

```regex
FUNCTION\s+(\w+)\s*[\(\s]
```

- Captures: Function names
- Example: `FUNCTION calculate_bestand(` → `calculate_bestand`

**2.3 Package Definitions**

```regex
PACKAGE\s+BODY\s+(\w+)|PACKAGE\s+(\w+)(?!\s+BODY)
```

- Captures: Package names (both spec and body)
- Example: `PACKAGE BODY pack_portbest` → `pack_portbest`

**2.4 Execute Calls**

```regex
EXECUTE\s+IMMEDIATE\s+.*?'.*?(\w+)'|EXECUTE\s+(\w+)
```

- Captures: Procedure/function names in EXECUTE statements
- Example: `EXECUTE p_abgleich.reconcile` → `p_abgleich`

**2.5 Package.Procedure Calls**

```regex
([\w]+)\.([\w]+)\s*\(
```

- Captures: Package and procedure names
- Example: `pack_generator.create_export(` → `pack_generator`, `create_export`

**2.6 Table References**

```regex
(?:FROM|INTO|UPDATE|DELETE\s+FROM|JOIN)\s+(\w+)
```

- Captures: Table names
- Example: `SELECT * FROM tnb_bestand` → `tnb_bestand`

**2.7 Script Includes**

```regex
@@?(\w+)\.sql
```

- Captures: SQL script names
- Example: `@nach_abgleich.sql` → `nach_abgleich`

**2.8 Cursor Definitions**

```regex
CURSOR\s+(\w+)\s+IS
```

- Captures: Cursor names
- Example: `CURSOR cur_portbest IS` → `cur_portbest`

### 3. C++ Patterns (Core Business Objects)

**3.1 Class Definitions**

```regex
class\s+(\w+)\s*[:{]
```

- Captures: Class names
- Example: `class PortingManager {` → `PortingManager`

**3.2 Function Definitions**

```regex
\w+\s+(\w+)\s*\([^)]*\)\s*[{;]
```

- Captures: Function names
- Example: `bool validatePorting(const char* id) {` → `validatePorting`

**3.3 Include Directives**

```regex
#include\s+[<"]([^>"]+)[>"]
```

- Captures: Header file names
- Example: `#include "BestandManager.hpp"` → `BestandManager.hpp`

**3.4 Namespace Usage**

```regex
(\w+)::(\w+)
```

- Captures: Namespace and identifier
- Example: `CORBA::Object_ptr` → `CORBA`, `Object_ptr`

**3.5 Method Calls**

```regex
->(\w+)\(|\.(\w+)\(
```

- Captures: Method names
- Example: `obj->exportData(` → `exportData`

### 4. Shell Patterns (Orchestration Scripts)

**4.1 Source Includes**

```regex
(?:source|\\.)\s+([\w_/]+)\.sh
```

- Captures: Shell script names
- Example: `source ./config/env.sh` → `env`

**4.2 Script Executions**

```regex
\./(\w+)\.(tcl|sh|sql)
```

- Captures: Script name and extension
- Example: `./start_pda_import.tcl` → `start_pda_import`, `tcl`

**4.3 Sqlplus Calls**

```regex
sqlplus\s+.*?@(\w+)\.sql
```

- Captures: SQL script names
- Example: `sqlplus user/pass@nachladen.sql` → `nachladen`

**4.4 TCL Script Invocations**

```regex
(?:tclsh|wish)\s+([\w_/]+)\.tcl
```

- Captures: TCL script names
- Example: `tclsh scripts/generator.tcl` → `generator`

### 5. German Business Term Patterns

**5.1 Common Business Terms (Telecommunications/Porting)**

```regex
\b(bestand|bestands?|abgleich|abgleichs?|wettbewerber|porting|portierung|portierungs?|tnb|pdat|lief|lieferant|lieferanten|anf|anfrage|anfragen|generator|generierung|export|import|reconcile|reconciliation)\b
```

- Case-insensitive matching recommended
- Captures: Domain-specific German and English terms
- Examples:
  - `bestand` → inventory/stock
  - `abgleich` → reconciliation
  - `wettbewerber` → competitor
  - `tnb` → Teilnehmerbestand (subscriber inventory)
  - `pdat` → Portierungsdaten (porting data)
  - `lief` → Lieferant (supplier/carrier)

**5.2 Comment Extraction**

```regex
#\s*(.*?)$|//\s*(.*?)$|--\s*(.*?)$|/\*\s*(.*?)\*/
```

- Captures: Comment text (for further term analysis)
- Process comment text through german-glossary skill for translation

**5.3 Variable/Function Names with German Terms**

```regex
(\w*(?:bestand|abgleich|wettbewerber|port|tnb|pdat)\w*)
```

- Captures: Identifiers containing German business terms
- Example: `update_bestand_status` → `update_bestand_status`

### 6. Cross-Language Call Patterns

**6.1 TCL Calling PL/SQL**

```regex
SqlStoPro\s+([\w]+)\.([\w]+)
```

- Already covered in 1.2
- Resolution: `{package}.{procedure}` → `pack_body_{package}.sql`

**6.2 Shell Calling TCL**

```regex
(?:tclsh|wish|\./)(\w+)\.tcl
```

- Resolution: `{script}.tcl` in same or parent directory

**6.3 PL/SQL Calling C++ (via CORBA)**

```regex
UTL_CORBA\.|CORBA\.|(\w+_CORBA)
```

- Indicates external C++ CORBA service (mark as external integration)

## Usage Guidelines

### Extraction Process

1. **Read File Content**

   ```python
   content = Read(file_path)
   ```

2. **Apply Language-Specific Patterns**

   ```python
   if file.endswith('.tcl'):
       patterns = TCL_PATTERNS
   elif file.endswith('.sql'):
       patterns = PLSQL_PATTERNS
   elif file.endswith(('.cpp', '.hpp')):
       patterns = CPP_PATTERNS
   elif file.endswith('.sh'):
       patterns = SHELL_PATTERNS
   ```

3. **Extract Terms**

   ```python
   terms = set()
   for pattern in patterns:
       matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
       terms.update(flatten(matches))
   ```

4. **Filter and Clean**

   ```python
   # Remove common language keywords
   KEYWORDS_TO_EXCLUDE = {'if', 'then', 'else', 'end', 'begin', 'return', 'select', 'from', 'where', 'and', 'or', 'not', 'is', 'as', 'for', 'while', 'do', 'loop'}

   terms = {t for t in terms if t.lower() not in KEYWORDS_TO_EXCLUDE}

   # Remove short/generic terms (length < 3)
   terms = {t for t in terms if len(t) >= 3}

   # Remove numeric-only terms
   terms = {t for t in terms if not t.isdigit()}
   ```

5. **Translate German Terms**
   ```python
   german_terms = identify_german_terms(terms)
   english_terms = translate_with_glossary(german_terms)
   terms.update(english_terms)
   ```

### Dependency Resolution Patterns

**TCL→SQL Dependency Resolution**:

```python
# Pattern: SqlStoPro p_generator.export_data
package = "p_generator"
procedure = "export_data"

# Resolve to: pack_body_p_generator.sql (or pack_p_generator.sql)
dependency_file = f"pack_body_{package}.sql"
```

**SQL Script References**:

```python
# Pattern: @script_name.sql or exec sqlplus @script_name.sql
script = "abgleich_pdat"

# Resolve to: abgleich_pdat.sql in same or parent directory
dependency_file = f"{script}.sql"
```

**TCL Source Includes**:

```python
# Pattern: source ../common/utils.tcl
path = "../common/utils"

# Resolve to absolute path from file location
dependency_file = resolve_relative_path(path + ".tcl", base_file_dir)
```

## Pattern Testing

### Test Cases

**TCL Test Content**:

```tcl
proc check_best_anf {args} {
    SqlStoPro p_generator.export_bestand
    exec sqlplus user/pass@abgleich_pdat.sql
    source ../common/portbest_utils.tcl
    set tnb_file "data.txt"
}
```

**Expected Extraction**:

- `check_best_anf` (procedure)
- `p_generator`, `export_bestand` (SqlStoPro call)
- `abgleich_pdat` (SQL script)
- `portbest_utils` (TCL source)
- `tnb_file` (variable with domain term)

**PL/SQL Test Content**:

```sql
CREATE OR REPLACE PACKAGE BODY pack_portbest AS
    PROCEDURE reconcile_wettbewerber(p_id NUMBER) IS
        CURSOR cur_bestand IS SELECT * FROM tnb_inventory;
    BEGIN
        pack_generator.create_export(p_id);
        @nach_abgleich.sql
    END;
END;
```

**Expected Extraction**:

- `pack_portbest` (package)
- `reconcile_wettbewerber` (procedure)
- `cur_bestand` (cursor)
- `tnb_inventory` (table)
- `pack_generator`, `create_export` (package.procedure call)
- `nach_abgleich` (SQL script)

## Quality Assurance

### Pattern Validation Checklist

**Precision**: Does the pattern match ONLY relevant terms?
**Recall**: Does the pattern capture ALL variations?
**Cross-Language**: Are cross-language calls correctly identified?
**Edge Cases**: Handles multi-line statements, special characters?
**Performance**: Regex efficiency for large files?

### Known Limitations

1. **Ambiguous Identifiers**: Generic names like `data`, `temp`, `process` may cause false positives

   - Mitigation: Filter against common terms list, require minimum term length

2. **Dynamic SQL**: SQL constructed at runtime may not be detected

   - Mitigation: Pattern matching for string concatenation with SQL keywords

3. **Obfuscated Code**: Minified or encoded content

   - Mitigation: Flag for manual review

4. **Multi-Line Statements**: Patterns may miss statements spanning multiple lines
   - Mitigation: Pre-process content to collapse multi-line statements

## References

- RNVS Code Module Mapping Documentation
- German-English Telecommunications Glossary
