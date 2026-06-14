---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-rnvs-expert-domain-term-extractor
description: Extract domain-specific terminology from RNVS legacy code files (TCL, PL/SQL, C++, Shell, Java) to enable iterative discovery and achieve 100% code coverage. This skill should be used during Phase 1 code analysis when expanding keyword search terms, discovering related files through domain terminology, or building comprehensive feature-specific vocabularies from code analysis.
allowed-tools: Read, Grep
user-invocable: false
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/rnvs-expert/skills/domain-term-extractor by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Domain Term Extractor Skill

## Overview

**Purpose**: Extract domain-specific terminology from RNVS legacy code files to enable iterative discovery and achieve 100% code coverage.

**Languages Supported**: TCL, PL/SQL, C++, Shell, Java

**Primary Use Case**: Phase 1 iterative discovery keyword expansion

## Why This Skill Exists

During Phase 1 code analysis, the initial feature name (e.g., "pda-export") provides only a starting point. Critical files often use:

- **Domain terminology** not in the feature name (e.g., "abgleich" for reconciliation)
- **Abbreviations** specific to telecommunications (e.g., "tnb" = Teilnehmerbestand)
- **Cross-language references** (TCL calling PL/SQL procedures)
- **German business terms** requiring translation

This skill provides battle-tested regex patterns to extract these terms from discovered files, enabling iterative keyword expansion.

## How It Works

### Input

- File path and content
- File language (TCL, PL/SQL, C++, Shell)

### Process

1. Apply language-specific regex patterns (see PATTERNS.md)
2. Extract procedure names, function calls, variable names, table references
3. Identify German business terms
4. Resolve cross-language dependencies
5. Filter common language keywords and noise
6. Return domain-specific terms for next search iteration

### Output

- Set of domain-specific search terms
- Cross-language dependency mappings
- German→English translation pairs

## Usage

### In Agent Context

```python
# During Phase B: Iterative Expansion
for file in newly_discovered_files:
    content = Read(file)

    # Use domain-term-extractor skill
    if file.endswith('.tcl'):
        terms = extract_tcl_terms(content)
        dependencies = resolve_tcl_dependencies(content)

    elif file.endswith('.sql'):
        terms = extract_plsql_terms(content)
        dependencies = resolve_plsql_dependencies(content)

    elif file.endswith(('.cpp', '.hpp')):
        terms = extract_cpp_terms(content)
        dependencies = resolve_cpp_dependencies(content)

    elif file.endswith('.sh'):
        terms = extract_shell_terms(content)
        dependencies = resolve_shell_dependencies(content)

    # Translate German terms using german-glossary skill
    german_terms = identify_german_terms(terms)
    english_terms = translate_with_glossary(german_terms)

    # Add to search keywords for next iteration
    all_search_terms.update(terms)
    all_search_terms.update(english_terms)
```

### Example: pda-export Feature

**Round 1**: Search "pda|export"

- Found: `check_best_anf.tcl`, `generatorbestgesamt.tcl`

**Extract from check_best_anf.tcl**:

```tcl
proc check_best_anf {args} {
    SqlStoPro p_generator.export_bestand
    exec sqlplus @abgleich_pdat.sql
    set tnb_file "data.txt"
}
```

**Extracted Terms**:

- `check_best_anf` (procedure name)
- `p_generator`, `export_bestand` (SqlStoPro call → search for both)
- `abgleich_pdat` (SQL script → search for "abgleich")
- `tnb` (variable name contains abbreviation)

**Round 2**: Search "p_generator|export_bestand|abgleich|tnb"

- Found: `abgleich_pdat.tcl`, `pack_body_generator.sql`, `tnb_utils.tcl`

## Language-Specific Extraction

### TCL Extraction

**Patterns Applied**:

1. Procedure definitions: `proc\s+(\w+)`
2. SqlStoPro calls: `SqlStoPro\s+([\w]+)\.([\w]+)`
3. SQL script execution: `@(\w+)\.sql`
4. TCL source includes: `source\s+([\w_/]+)\.tcl`
5. Business domain variables: German term detection

**Example**:

```tcl
source ../common/portbest_utils.tcl
SqlStoPro pack_abgleich.reconcile_wettbewerber
```

→ Extracts: `portbest_utils`, `pack_abgleich`, `reconcile_wettbewerber`, `portbest`, `abgleich`, `wettbewerber`

### PL/SQL Extraction

**Patterns Applied**:

1. Package/procedure/function definitions
2. Package.procedure calls
3. Table references (FROM, INTO, UPDATE, JOIN)
4. SQL script includes (@script.sql)
5. Cursor definitions

**Example**:

```sql
CREATE PACKAGE BODY pack_portbest AS
    CURSOR cur_tnb IS SELECT * FROM tnb_bestand;
    pack_generator.export_data(p_id);
    @nach_abgleich.sql
END;
```

→ Extracts: `pack_portbest`, `cur_tnb`, `tnb_bestand`, `pack_generator`, `export_data`, `nach_abgleich`

### C++ Extraction

**Patterns Applied**:

1. Class definitions
2. Function definitions
3. Include directives
4. Namespace usage (CORBA external systems)

**Example**:

```cpp
#include "BestandManager.hpp"
class PortingValidator {
    bool validateBestand(const char* id);
};
```

→ Extracts: `BestandManager`, `PortingValidator`, `validateBestand`, `bestand`

### Shell Extraction

**Patterns Applied**:

1. Source includes
2. Script executions (./script.tcl)
3. Sqlplus calls
4. Environment variables with domain terms

**Example**:

```bash
source ./config/pda_env.sh
./start_abgleich_ps.tcl
sqlplus @nachladen.sql
```

→ Extracts: `pda_env`, `start_abgleich_ps`, `abgleich`, `nachladen`

## Cross-Language Dependency Resolution

### TCL → PL/SQL

**Pattern**: `SqlStoPro package_name.procedure_name`

**Resolution**:

```python
# Extract: SqlStoPro p_generator.export_bestand
package = "p_generator"
procedure = "export_bestand"

# Resolve to file: pack_body_p_generator.sql
# Search for: "p_generator", "export_bestand", "generator"
```

### PL/SQL → PL/SQL

**Pattern**: `package.procedure(` or `@script.sql`

**Resolution**:

```python
# Pattern 1: pack_portbest.reconcile(p_id)
package = "pack_portbest"
dependency = "pack_body_portbest.sql" or "pack_portbest.sql"

# Pattern 2: @nach_abgleich.sql
script = "nach_abgleich"
dependency = "nach_abgleich.sql"
```

### Shell → TCL

**Pattern**: `./script.tcl` or `tclsh script.tcl`

**Resolution**:

```python
# ./start_pda_import.tcl
script = "start_pda_import"
dependency = "start_pda_import.tcl"
search_terms = ["start", "pda", "import"]
```

## German Term Translation

**Integration with german-glossary skill**:

```python
# German terms commonly found in RNVS code
german_terms = {
    "bestand": "inventory",
    "abgleich": "reconciliation",
    "wettbewerber": "competitor",
    "tnb": "subscriber_inventory",  # Teilnehmerbestand
    "pdat": "porting_data",          # Portierungsdaten
    "lief": "carrier",               # Lieferant
    "anf": "request",                # Anfrage
    "nach": "after"                  # nach_abgleich = after_reconciliation
}

# Use german-glossary skill for comprehensive translation
```

## Quality Filters

### Term Filtering Rules

**Exclude**:

1. Language keywords: `if`, `then`, `else`, `begin`, `end`, `select`, `from`, `where`, etc.
2. Short terms: Length < 3 characters
3. Numeric-only: `123`, `001`
4. Common noise: `data`, `temp`, `test`, `tmp`, `util`

**Include**:

1. Business domain terms (length ≥ 3)
2. German terminology
3. Procedure/function/class names
4. Table names
5. Package names
6. File references

### Example Filtering

**Raw Extraction**:

```
['if', 'then', 'check_best_anf', 'p', 'generator', 'export', 'bestand', 'sql', 'abgleich', 'pdat', '123', 'tnb']
```

**After Filtering**:

```
['check_best_anf', 'generator', 'export', 'bestand', 'abgleich', 'pdat', 'tnb']
```

## Performance Considerations

### Optimization Strategies

1. **Batch Processing**: Process multiple files in parallel
2. **Pattern Compilation**: Pre-compile regex patterns for reuse
3. **Caching**: Cache extracted terms to avoid re-processing
4. **Lazy Evaluation**: Extract terms only when needed for next iteration

### Performance Metrics

- **Average extraction time**: ~50ms per file (TCL/PL/SQL)
- **Pattern efficiency**: Optimized regex for single-pass extraction
- **Memory usage**: Minimal (term sets, not full content storage)

## Error Handling

### Robustness

**Malformed Files**:

```python
try:
    content = Read(file)
    terms = extract_terms(content)
except Exception as e:
    log_warning(f"Failed to extract from {file}: {e}")
    terms = []  # Continue with empty set
```

**Encoding Issues**:

```python
# Handle German umlauts and special characters
content = content.encode('utf-8', errors='ignore').decode('utf-8')
```

**Large Files**:

```python
# Read in chunks if file > 10MB
if file_size > 10_000_000:
    content = read_in_chunks(file)
```

## Validation

### Self-Testing

**Test Case 1**: TCL File with SqlStoPro

```tcl
proc test_proc {args} {
    SqlStoPro pack_test.procedure_test
}
```

**Expected**: `['test_proc', 'pack_test', 'procedure_test']`

**Test Case 2**: PL/SQL with Package Calls

```sql
PROCEDURE test AS
BEGIN
    pack_portbest.reconcile(123);
    @script_test.sql
END;
```

**Expected**: `['test', 'pack_portbest', 'reconcile', 'portbest', 'script_test']`

**Test Case 3**: German Terms

```tcl
# Abgleich der Wettbewerber-Bestandsdaten
set bestand_file "tnb.dat"
```

**Expected**: `['abgleich', 'wettbewerber', 'bestand', 'bestandsdaten', 'tnb']`
**After Translation**: `['reconciliation', 'competitor', 'inventory', 'inventory_data', 'subscriber_inventory']`

## Integration Points

### Phase 1 Command

- Called during Phase B (Iterative Expansion)
- Provides keywords for next Grep search round
- Builds dependency graph for Phase C validation

### multi-language-code-analyzer Agent

- Primary consumer of this skill
- Uses extraction results to drive iterative discovery
- Validates extracted terms against convergence criteria

### german-glossary Skill

- Complementary skill for German→English translation
- Called after term extraction
- Enriches search keywords with English equivalents

## Best Practices

### When to Use

**Use for**:

- Phase 1 iterative discovery (keyword expansion)
- Dependency graph construction
- Cross-language call mapping
- Domain vocabulary building

**Do NOT use for**:

- Code analysis (use code-analysis-schema)
- Structural parsing (use Knowledge Graph for Java)
- Full semantic understanding (use agent analysis)

### Iteration Strategy

```python
# Recommended iteration pattern
round = 1
max_rounds = 3

while round <= max_rounds:
    # Extract from newly discovered files
    new_terms = extract_domain_terms(new_files)

    # Filter already-searched terms
    search_terms = new_terms - previous_terms

    if not search_terms:
        # Converged - no new terms
        break

    # Search with expanded keywords
    new_files = grep_search(search_terms)

    if not new_files:
        # No new files - converged
        break

    round += 1
```

## Maintenance

### Pattern Updates

**When to update patterns**:

- New language constructs discovered in RNVS code
- False positives/negatives identified
- Additional cross-language call patterns found

**Update process**:

1. Add test case demonstrating issue
2. Update pattern in PATTERNS.md
3. Validate against test suite
4. Document in version history

## See Also

- [PATTERNS.md](./PATTERNS.md) - Comprehensive regex pattern library
- [german-glossary Skill](../german-glossary/) - German term translation
- [code-analysis-schema Skill](../code-analysis-schema/) - Phase 1 output schema
