# File Reading Requirements

This document specifies **MANDATORY** reading requirements for Phase 1 code analysis.
These are not suggestions - they are commands.

---

## Core Principle

> **You MUST execute `Read(file_path)` before assigning relevance scores.**
> Scores based on file names or grep output alone are HALLUCINATIONS.
> This is NOT optional.

---

## Reading by File Type (NOT Score)

**CRITICAL CHANGE**: Reading requirements are based on **FILE TYPE**, not relevance score.
This prevents gaming the system by assigning low scores to avoid reading.

---

### Priority 1: PL/SQL Packages - FULL READ ALWAYS

**Run:** `Read(file_path)` for ALL files matching `pack_body_*.sql` or `pack_spec_*.sql`.

**BLOCKING RULES:**
- Do NOT skip based on file size
- Do NOT use partial reading for PL/SQL packages
- Do NOT assign score until after reading

| File Size | Action |
|-----------|--------|
| < 2000 lines | **Run:** `Read(file_path)` - single call |
| 2000-5000 lines | **Run:** Chunked read (see below) |
| > 5000 lines | **Run:** DELEGATE to agent (MANDATORY) |

**Required output:**
```json
{
  "content_read": true,
  "read_method": "full",
  "lines_read": 1847
}
```

---

### Priority 2: C++ Managers - FULL READ ALWAYS

**Run:** `Read(file_path)` for ALL files matching `*Manager.cpp` or `*Manager.hpp`.

**BLOCKING RULES:**
- Do NOT skip based on perceived relevance
- Do NOT use grep-only reading
- Do NOT assign score until after reading

| File Size | Action |
|-----------|--------|
| < 2000 lines | **Run:** `Read(file_path)` - single call |
| 2000-5000 lines | **Run:** Chunked read |
| > 5000 lines | **Run:** DELEGATE to agent (MANDATORY) |

---

### Priority 3: Entry Point Scripts - FULL READ ALWAYS

**Run:** `Read(file_path)` for ALL files that serve as entry points:
- Main TCL scripts (usually `*_main.tcl`, `*Start.tcl`)
- Shell entry points (`*.sh` that invoke other scripts)
- Batch SQL scripts (`@*.sql` runners)

**BLOCKING RULES:**
- Entry points often call many other files
- Missing an entry point breaks dependency chain
- Do NOT skip based on file size

---

### Priority 4: Other Files - Size-Based Reading

**Run:** `Read(file_path)` based on file size:

| File Size | Action |
|-----------|--------|
| < 2000 lines | **Run:** `Read(file_path)` - full read |
| 2000-5000 lines | **Run:** Chunked read (see below) |
| > 5000 lines | **Run:** DELEGATE to agent |

**BLOCKING RULES:**
- Do NOT use grep-only for files under 2000 lines
- Do NOT skip reading to save time
- Do NOT estimate content from file names

---

## Chunked Reading Strategy (2000-5000 lines)

**Run:** Execute this exact sequence for files between 2000-5000 lines:

```
Step 1: **Run:** Read(file_path, offset=1, limit=1000)
        -> Read first 1000 lines (headers, imports, declarations)

Step 2: **Run:** Grep(pattern="${KEYWORDS}", path=file_path)
        -> Get line numbers of all keyword matches

Step 3: For EACH keyword match location:
        **Run:** Read(file_path, offset=MATCH_LINE-100, limit=200)
        -> Read 200 lines centered on each match

Step 4: **Run:** Read(file_path, offset=LAST_1000_LINES, limit=1000)
        -> Read last 1000 lines (main procedures, end of package)
```

**BLOCKING RULES:**
- Do NOT skip Step 1 (headers reveal structure)
- Do NOT skip Step 4 (endings often contain main logic)
- Do NOT proceed without documenting `read_chunks`

**Required output:**
```json
{
  "content_read": true,
  "read_method": "chunked",
  "read_chunks": [[1, 1000], [1500, 1700], [2300, 2500], [3000, 4000]],
  "lines_read": 2400
}
```

---

## Agent Delegation (MANDATORY when triggered)

**You MUST delegate when ANY condition is true:**

| Condition | Threshold |
|-----------|-----------|
| Single file size | > 5000 lines |
| Total high-relevance files | > 15 |
| Total LOC to analyze | > 50,000 |
| Dependency closure | < 95% after first pass |

**Delegation prompt template:**

```
Task(
  subagent_type="multi-language-code-analyzer",
  prompt="Read and analyze the following files for feature ${FEATURE}.

  For EACH file, you MUST:
  1. **Run:** Read(file_path) - ENTIRE content, no skipping
  2. Count keyword matches for: ${KEYWORDS}
  3. Record sample line numbers for each keyword (minimum 3)
  4. Extract dependencies using RNVS patterns:
     - PL/SQL: package.procedure( calls
     - TCL: source and SqlStoPro statements
     - C++: #include directives
  5. Record source line and pattern for each dependency

  Files to analyze:
  ${FILE_LIST}

  REQUIRED return format per file:
  {
    'file_path': '...',
    'lines_read': N,
    'keyword_matches': [
      {'keyword': '...', 'occurrences': N, 'sample_lines': [N, N, N]}
    ],
    'dependencies': [
      {'target': '...', 'source_line': N, 'pattern_found': '...'}
    ]
  }

  BLOCKING RULES:
  - Do NOT skip files
  - Do NOT estimate occurrence counts
  - Do NOT assume dependencies without finding patterns
  - Do NOT return entries without line numbers"
)
```

**After delegation:**
1. Receive agent results
2. **Validate** evidence is present (`sample_lines`, `source_line`)
3. If evidence missing, re-delegate with clearer instructions
4. Integrate into file-inventory.json
5. Return to validation step

---

## Language-Specific Key Sections

### PL/SQL (pack_body_*.sql)

**Key sections to read (MANDATORY):**
- Lines 1-100: Package specification, constants, types
- PROCEDURE/FUNCTION declarations (find via grep, then read context)
- Error handling blocks: `EXCEPTION`, `RAISE`, `fc_fcode`
- Last 200 lines: Often main entry points

**Dependency patterns to extract:**
- `package.procedure(` - calls to other packages
- `@script.sql` - script inclusions
- `EXECUTE IMMEDIATE` - dynamic SQL (note as potential dep)

### TCL (*.tcl)

**Key sections to read (MANDATORY):**
- Lines 1-50: `package require`, `source` statements
- `proc` declarations
- `SqlStoPro` calls

**Dependency patterns to extract:**
- `source relative/path.tcl`
- `SqlStoPro package.procedure`
- `package require PackageName`

### C++ (*.cpp, *.hpp)

**Key sections to read (MANDATORY):**
- Lines 1-100: `#include` statements
- Class declarations
- Method implementations

**Dependency patterns to extract:**
- `#include "local/file.hpp"`
- `#include <system/file>`
- `ClassName::method()` calls

---

## What NOT To Do

| Action | Why It's Wrong | Do This Instead |
|--------|----------------|-----------------|
| Assign scores before reading | No evidence | **Run:** Read first, score after |
| Use file names as evidence | Names can mislead | **Run:** Read content |
| Skip reading "large" files | Misses critical code | **Run:** Chunk or delegate |
| Use grep output as analysis | Grep finds, doesn't analyze | **Run:** Read full context |
| Estimate line counts | Inaccurate | **Run:** Count during read |
| Copy from example schemas | Examples are templates | Extract from real code |
| Assume dependencies | Assumption != evidence | Find actual patterns in code |
| Skip files based on score | Gaming the system | Read based on FILE TYPE |

---

## Reading Evidence Checklist (MANDATORY)

**Run:** Before considering a file "read", verify ALL of these:

```
File Reading Verification for ${FILE}:
- [ ] Read tool was EXECUTED (not just planned)
- [ ] `content_read` is TRUE
- [ ] `read_method` specifies strategy (full/chunked/agent_delegated)
- [ ] `lines_read` reflects actual lines read
- [ ] For chunked: `read_chunks` lists all ranges
- [ ] At least ONE `keyword_matches` entry has `sample_lines` array
- [ ] If dependencies found: each has `source_line` and `pattern_found`
```

**If ANY check fails:**
1. Return to reading step
2. **Run:** `Read(file_path)` for the file
3. Extract evidence from Read output
4. Re-run this checklist

---

## REMOVED: Tier-Based Loopholes

The following **old approaches are NO LONGER VALID**:

| Old Approach | Why Removed |
|--------------|-------------|
| "Tier 2: First 500 lines only" | Misses 90% of large files |
| "Tier 3: Grep context only" | No actual content reading |
| "Score determines read depth" | Circular dependency - gaming possible |
| "Low relevance = skip reading" | Missing important context |

**Current approach**: Read based on **FILE TYPE** and **FILE SIZE**, not score.
Score is calculated **AFTER** reading, not before.
