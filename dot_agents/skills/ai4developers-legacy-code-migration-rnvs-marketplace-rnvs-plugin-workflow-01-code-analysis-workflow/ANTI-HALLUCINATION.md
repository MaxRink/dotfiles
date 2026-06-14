# Anti-Hallucination Checklist (MANDATORY)

## Purpose

This checklist **MUST** be completed before writing output files.
Every item must be verified. If **ANY** item fails, **DO NOT PROCEED**.

This is a **MANDATORY GATE** - not a suggestion.

---

## Contents

- [Mechanical Validation (Execute Before Write)](#mechanical-validation-execute-before-write)
- [Pre-Output Validation Checklist](#pre-output-validation-checklist)
- [Red Flags (BLOCK if detected)](#red-flags-block-if-detected)
- [Evidence Format Comparison](#evidence-format-comparison)
- [Common Hallucination Patterns](#common-hallucination-patterns)
- [Final Verification Gate](#final-verification-gate)

---

## Mechanical Validation (Execute Before Write)

**BLOCKING GATE: You CANNOT write file-inventory.json until ALL validations pass.**

These are **executable validations**, not questions to ask yourself.

### Validation 1: Content Read Count

**Run:** Count files where `content_read: true` in your prepared output.

```
COUNT = number of files with content_read: true
EXPECTED = summary.high_relevance_files (minimum)
```

| Result | Action |
|--------|--------|
| COUNT >= EXPECTED | PASS - proceed to Validation 2 |
| COUNT < EXPECTED | FAIL - return to Step 4, execute Read for missing files |

**Example:**
- Prepared output has 28 high_relevance_files
- Count files with `content_read: true` = 15
- **FAIL**: Return to Step 4, read 13 more files

---

### Validation 2: Evidence Completeness

**Run:** Count empty `sample_lines: []` arrays in your prepared output.

```
EMPTY_COUNT = number of keyword_matches entries with sample_lines: []
```

| Result | Action |
|--------|--------|
| EMPTY_COUNT = 0 | PASS - proceed to Validation 3 |
| EMPTY_COUNT > 0 | FAIL - return to Step 4.2, extract keywords from Read content |

**Example:**
- Found 5 keyword_matches with `sample_lines: []`
- **FAIL**: Return to Step 4.2, search Read output for those keywords, record line numbers

---

### Validation 3: Dependency Evidence

**Run:** Check all dependencies have `source_line` field (integer, not null).

```
MISSING_SOURCE = number of dependencies where source_line is missing or null
```

| Result | Action |
|--------|--------|
| MISSING_SOURCE = 0 | PASS - proceed to Validation 4 |
| MISSING_SOURCE > 0 | FAIL - return to Step 4.3, extract from Read content |

**Example:**
- Found 3 dependencies without `source_line`
- **FAIL**: Return to Step 4.3, find patterns in code, record source_line

---

### Validation 4: Pattern Evidence

**Run:** Check all dependencies have `pattern_found` field (string, not empty).

```
MISSING_PATTERN = number of dependencies where pattern_found is missing or empty
```

| Result | Action |
|--------|--------|
| MISSING_PATTERN = 0 | PASS - proceed to Validation 5 |
| MISSING_PATTERN > 0 | FAIL - return to Step 4.3, record actual code pattern |

---

### Validation 5: Scoring Transparency

**Run:** Check all files have `keyword_density_reason` in scoring_breakdown.

```
MISSING_REASON = number of files where scoring_breakdown.keyword_density_reason is missing
```

| Result | Action |
|--------|--------|
| MISSING_REASON = 0 | ALL VALIDATIONS PASSED - proceed to Write |
| MISSING_REASON > 0 | FAIL - return to Step 4.4, explain calculation |

---

## Pre-Output Validation Checklist

**Copy this checklist and complete ALL items:**

```
Anti-Hallucination Verification for ${FEATURE}:

VALIDATION 1 - CONTENT READING:
- [ ] Counted files with content_read: true = ___
- [ ] Minimum expected (high_relevance_files) = ___
- [ ] COUNT >= EXPECTED? ___

VALIDATION 2 - KEYWORD EVIDENCE:
- [ ] Counted empty sample_lines arrays = ___
- [ ] EMPTY_COUNT = 0? ___

VALIDATION 3 - DEPENDENCY SOURCE LINES:
- [ ] Counted dependencies without source_line = ___
- [ ] MISSING_SOURCE = 0? ___

VALIDATION 4 - DEPENDENCY PATTERNS:
- [ ] Counted dependencies without pattern_found = ___
- [ ] MISSING_PATTERN = 0? ___

VALIDATION 5 - SCORING TRANSPARENCY:
- [ ] Counted files without keyword_density_reason = ___
- [ ] MISSING_REASON = 0? ___

ALL VALIDATIONS PASSED: [ ] YES / [ ] NO
```

**If ANY validation shows NO, DO NOT proceed to Write.**

---

## Red Flags (BLOCK if detected)

If you catch yourself doing **ANY** of these, **STOP** and return to reading:

| Red Flag | Why It's Wrong | Fix |
|----------|----------------|-----|
| Scoring based on file names | File name != content | **Run:** Read the file |
| Listing keywords without `sample_lines` | No evidence of actual match | Search Read output, record lines |
| Dependencies without `source_line` | No proof it exists | Find in Read output |
| Using grep output as "complete analysis" | Grep finds, doesn't analyze | **Run:** Read full context |
| Copying from example files | Examples are templates | Extract from real code |
| Claiming 97% closure without verification | Meaningless without real deps | Trace actual deps |
| Estimating line counts | Inaccurate | **Run:** Read file or count |
| Assuming "pack_body_val" exists as dep | Assumption != evidence | Find actual call in Read output |
| Empty `sample_lines: []` arrays | Placeholder, not evidence | Search and populate |
| `"pattern_found": ""` | Empty evidence | Find actual pattern |

---

## Evidence Format Comparison

### CORRECT (with evidence):

```json
{
  "file_path": "script/plsql/pack_body_rfnr.sql",
  "content_read": true,
  "read_method": "chunked",
  "read_chunks": [[1, 1000], [1001, 2000], [2001, 3000]],
  "relevance_score": 95,
  "keyword_matches": [
    {
      "keyword": "RFM",
      "occurrences": 47,
      "sample_lines": [123, 456, 789, 1234, 2345]
    },
    {
      "keyword": "format_plausi",
      "occurrences": 12,
      "sample_lines": [234, 567, 890]
    }
  ],
  "dependencies": [
    {
      "target": "pack_body_val",
      "source_line": 234,
      "pattern_found": "p_val.format_plausi_a(l_rfnr, pm_fc_fcode)"
    },
    {
      "target": "pack_body_pm",
      "source_line": 567,
      "pattern_found": "p_pm.p_anlegen_pm(l_pm_id, l_fc_fcode)"
    }
  ],
  "scoring_breakdown": {
    "module_reference": 0,
    "component_match": 25,
    "keyword_density": 20,
    "keyword_density_reason": "47 RFM + 12 format_plausi = 59 matches for 10 keywords, avg 5.9",
    "language_priority": 10,
    "exclusion_penalty": 0,
    "dependency_indicator": 8
  }
}
```

### INCORRECT (hallucinated):

```json
{
  "file_path": "script/plsql/pack_body_rfnr.sql",
  "relevance_score": 100,
  "keyword_matches": ["RFM", "VFM", "error"],
  "dependencies": ["pack_body_val", "pack_body_pm"]
}
```

**What's wrong:**
- No `content_read` field → Validation 1 fails
- No `read_method` field → Unknown if file was read
- `keyword_matches` is just strings → Validation 2 fails (no sample_lines)
- `dependencies` is just strings → Validation 3 fails (no source_line)
- No `scoring_breakdown` → Validation 5 fails

---

## Common Hallucination Patterns

### Pattern 1: "File Name = Content"

**Hallucination:**
> "pack_body_rfnr.sql must contain RFNR-related code because of its name"

**Reality:**
> File names suggest content but don't prove it. **Run:** `Read(file_path)`.

### Pattern 2: "Grep = Analysis"

**Hallucination:**
> "Grep found 'RFM' in 14 files, so those files handle RFM errors"

**Reality:**
> Grep finds matches but doesn't understand context. A file mentioning 'RFM' once in a comment is different from a file implementing RFM logic. **Run:** `Read(file_path)` to understand context.

### Pattern 3: "Logical Dependency"

**Hallucination:**
> "pack_body_rfnr.sql must call pack_body_val for validation because that's logical"

**Reality:**
> Only actual code patterns prove dependencies. **Run:** `Read(file_path)` and find `p_val.something(` in the Read output.

### Pattern 4: "Score Estimation"

**Hallucination:**
> "This file looks important, so relevance_score = 95"

**Reality:**
> Scores must be calculated from evidence: keyword matches (from Read output), dependency presence (from Read output), component name match.

### Pattern 5: "Placeholder Evidence"

**Hallucination:**
> `"sample_lines": [234, 567, 890]` without having read the file

**Reality:**
> Line numbers must come from actual Read output. If you didn't read the file, you cannot know line numbers.

---

## Final Verification Gate

**BLOCKING: Execute this final check before calling Write:**

```
FINAL VERIFICATION:

1. All 5 mechanical validations passed?      [ ] YES / [ ] NO
2. Pre-output checklist completed?           [ ] YES / [ ] NO
3. No red flags detected?                    [ ] YES / [ ] NO
4. All evidence came from Read tool output?  [ ] YES / [ ] NO
5. Zero empty sample_lines arrays?           [ ] YES / [ ] NO
6. Zero dependencies without source_line?    [ ] YES / [ ] NO

ALL YES? -> Proceed to Write
ANY NO?  -> Return to Step 4, fix the issue
```

**This is enforced by PreToolUse hook:** The Write tool will be BLOCKED if file-inventory.json fails validation. You will receive an error message telling you what to fix.

---

## Hook Enforcement

A PreToolUse hook validates file-inventory.json writes. If you attempt to Write without proper evidence, you will see:

```
BLOCKED: file-inventory.json has no files with content_read: true

You MUST execute Read(file_path) for discovered files before writing output.
Return to Step 4 and use the Read tool on each file.
```

**This is NOT a suggestion. The Write will fail.**

To fix:
1. Return to Step 4
2. **Run:** `Read(file_path)` for each discovered file
3. Extract keywords and dependencies from Read output
4. Re-run mechanical validations
5. Attempt Write again
