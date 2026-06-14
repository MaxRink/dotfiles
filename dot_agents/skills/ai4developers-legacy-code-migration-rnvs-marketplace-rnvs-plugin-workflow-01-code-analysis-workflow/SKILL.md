---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-workflow-01-code-analysis-workflow
description: Phase 1 code discovery workflow for RNVS feature analysis. Discovers files via /modules folder and Grep searches. **RLM is DEFAULT for >10 files** - uses chunked analysis with accurate file:line attribution. Extracts dependencies, validates closure (>=95%). Outputs file-inventory.json and dependency-graph.json. Use after 00-feature-definition-workflow completes. Invoke with "/01-code-analysis-workflow" or "Phase 1 analysis".
allowed-tools: Read, Glob, Grep, Write, Task, AskUserQuestion, Bash
user-invocable: true
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/workflow/skills/01-code-analysis-workflow by codex-knowledge-curation/scripts/persist_project_skills.py. -->

<required_reading>
Read `results/${FEATURE}/.workflow-state.md` before any operation.
This provides workflow mode, completed phases, and session context.
</required_reading>

# Phase 1: Code Analysis Workflow

Discover all code related to a feature, **READ content** to score relevance, extract dependencies from actual code.

---

## Critical Requirement: READ BEFORE SCORE

> **You MUST read file content before assigning relevance scores.**
> Scores based on file names or grep output alone are **HALLUCINATIONS**.
> This is NOT optional. See [ANTI-HALLUCINATION.md](ANTI-HALLUCINATION.md).

---

## Prerequisites

<prerequisites>
**Feature Identification** - check in order, stop at first match:

1. **User provided feature name** (e.g., "/01-code-analysis-workflow NBM") -> use directly
2. **Conversation context** -> use feature from earlier in session
3. **Single feature in results/** -> `Glob results/*/feature-definition.json` - if exactly one, use it
4. **Multiple features** -> use AskUserQuestion to let user select
5. **No features** -> "Run /00-feature-definition-workflow first"

**Verify**: `results/${FEATURE}/feature-definition.json` exists.

**Load**: Extract `keywords`, `scope.included_components`, `scope.excluded_scope`, `feature_name`.
</prerequisites>

---

## Step 0: Load Workflow State

Read `results/${FEATURE}/.workflow-state.md` and verify:

1. **Phase Check**: Phase 0 must be ✅ Complete
2. **Status**: Should be "In Progress"

If state file missing: "Run /00-feature-definition-workflow first to initialize workflow state."

**Update state**: Set Phase 1 to 🔄 In Progress, update Last Activity.

---

## Workflow Checklist

Copy and maintain this checklist throughout the workflow:

```
Phase 1 Code Analysis Progress:
- [ ] Step 1: Feature definition loaded
- [ ] Step 2: Module references searched
- [ ] Step 3: Keyword grep completed (files FOUND, not analyzed)
- [ ] Step 3.5: RLM check - if >10 files, MUST use RLM (Step 6.1)
- [ ] Step 4: (Skip if RLM) ALL high-relevance files READ
- [ ] Step 5: (Skip if RLM) Keywords verified in actual content
- [ ] Step 6: Delegation executed (RLM or Agent)
- [ ] Step 7: Outputs transformed to Phase 1 format
- [ ] Step 8: Anti-hallucination checklist PASSED
- [ ] Step 9: Outputs written with evidence fields
- [ ] Step 10: User validated results
```

**CRITICAL**: If file count > 10 after Step 3, you MUST proceed to Step 6.1 (RLM).

---

## Step 1: Load Feature Definition

Read `results/${FEATURE}/feature-definition.json` and extract:
- `keywords.german_terms`, `keywords.english_terms`, `keywords.technical_terms`
- `scope.included_components`
- `scope.excluded_scope`

---

## Step 2: Find Module References

Search `/modules` folder for curated starting points (skip if unavailable):
```
Glob("modules/${FEATURE_RELATED}/**/*")
```

---

## Step 3: Keyword Grep Search

Expand file discovery using keywords from feature definition:
```
Grep(pattern="keyword1|keyword2|keyword3", path=".", glob="*.sql")
Grep(pattern="keyword1|keyword2|keyword3", path=".", glob="*.tcl")
Grep(pattern="keyword1|keyword2|keyword3", path=".", glob="*.cpp")
```

**Result**: List of file PATHS. These files are FOUND, not yet ANALYZED.

---

## Step 3.5: RLM Delegation Check (MANDATORY)

**IMMEDIATELY after file discovery, evaluate:**

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Files discovered | > 10 | **RLM is DEFAULT** - proceed to Step 6.1 |
| Files discovered | <= 10 | Direct analysis (Step 4) |

**This check is BLOCKING** - you cannot proceed to Step 4 if > 10 files were discovered.

### If > 10 files discovered:

**Ask user for confirmation (opt-out only):**
```
AskUserQuestion:
  question: "${FILE_COUNT} files discovered. RLM chunking is recommended for accurate analysis. Proceed with RLM?"
  header: "RLM Analysis"
  options:
    - label: "Yes, use RLM (Recommended)"
      description: "Chunked analysis with accurate file:line attribution"
    - label: "No, read files directly"
      description: "Only for small/simple codebases. May miss patterns in large files."
```

**If user selects RLM (default):** Skip Step 4, go directly to **Step 6.1 (RLM Delegation)**.

**If user opts out:** Proceed to Step 4, but warn about potential accuracy issues.

---

## Step 4: Read and Analyze (MANDATORY EXECUTION)

### Degrees of Freedom: LOW (Narrow Bridge)

This step requires **LOW FREEDOM** - there is only one safe path forward.

| Action | Correct | Incorrect |
|--------|---------|-----------|
| Reading | Execute `Read(file_path)` | Skim, estimate, or assume |
| Keyword extraction | Search READ content, record line numbers | Use grep output as "analysis" |
| Dependency extraction | Find patterns in code, record source_line | Assume based on file names |
| Scoring | Calculate from actual evidence | Assign before reading |

**Analogy**: "Narrow bridge with cliffs on both sides" - one wrong step causes hallucination.

---

### 4.1 Read File Content (MANDATORY EXECUTION)

**Run:** `Read(file_path)` for EACH file discovered in Steps 2-3.

**BLOCKING RULES:**
- Do NOT proceed to 4.2 until Read tool has been executed for the file
- Do NOT use Grep output as substitute for Read content
- Do NOT skip files based on file name assumptions
- If Read fails, document error and mark `content_read: false`

**File Size Handling:**

| File Type | Lines | Action |
|-----------|-------|--------|
| PL/SQL packages (`pack_body_*.sql`) | ANY | **Run:** `Read(file_path)` - FULL READ ALWAYS |
| C++ managers (`*Manager.cpp`) | ANY | **Run:** `Read(file_path)` - FULL READ ALWAYS |
| Entry point scripts | ANY | **Run:** `Read(file_path)` - FULL READ ALWAYS |
| Other files | < 2000 | **Run:** `Read(file_path)` |
| Other files | 2000-5000 | **Run:** Chunked read in 1000-line chunks |
| Other files | > 5000 | Delegate to agent (see Step 6) |

**For chunked reads, document:**
```json
"read_method": "chunked",
"read_chunks": [[1, 1000], [1001, 2000], [2001, 3000]]
```

---

### 4.2 Extract Keywords with Evidence (FROM READ OUTPUT)

**Run:** Search the Read output for EACH keyword from feature-definition.json.

**BLOCKING RULES:**
- Do NOT use grep output as keyword evidence
- Do NOT proceed if sample_lines is empty
- Do NOT estimate occurrence counts

For EACH keyword:
1. Search the READ content (the actual file text returned by Read tool)
2. Count actual occurrences
3. Record sample line numbers as EVIDENCE

**Required output format:**
```json
"keyword_matches": [
  {
    "keyword": "RFM",
    "occurrences": 47,
    "sample_lines": [123, 456, 789, 1234]
  },
  {
    "keyword": "format_plausi",
    "occurrences": 12,
    "sample_lines": [234, 567, 890]
  }
]
```

**If `sample_lines` is empty, you did NOT read the file. Return to 4.1.**

---

### 4.3 Extract Dependencies with Evidence (FROM READ OUTPUT)

**Run:** Search the Read output for dependency patterns from [RNVS-PATTERNS.md](RNVS-PATTERNS.md).

**BLOCKING RULES:**
- Do NOT assume dependencies based on file names
- Do NOT list dependencies without source_line
- Do NOT proceed if pattern_found is missing

| Language | Pattern | Example |
|----------|---------|---------|
| PL/SQL | `package.procedure(` | `p_val.format_plausi_a(` |
| TCL | `source *.tcl` | `source ../lib/utils.tcl` |
| TCL | `SqlStoPro pkg.proc` | `SqlStoPro p_rfnr.validate` |
| C++ | `#include "*.hpp"` | `#include "RnvsError.hpp"` |

**Required output format:**
```json
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
]
```

**If `source_line` is missing, you did NOT find the dependency in code. Return to 4.1.**

---

### 4.4 Calculate Score with Evidence (FROM EXTRACTED DATA)

**Run:** Calculate `relevance_score` using ONLY data from steps 4.2 and 4.3.

**BLOCKING RULES:**
- Do NOT assign scores before reading content
- Do NOT estimate keyword counts
- Do NOT skip keyword_density_reason calculation

| Component | Max Points | Based On |
|-----------|------------|----------|
| module_reference | 30 | File in /modules folder? |
| component_match | 25 | Name in feature def included_components? |
| keyword_density | 25 | (total_matches / total_keywords) scaled |
| language_priority | 10 | PL/SQL=10, C++=8, TCL=5, Java=5, Shell=3 |
| exclusion_penalty | -50 | Matches excluded_scope? |
| dependency_indicator | 10 | Has deps to/from core files? |

**Required output format:**
```json
"scoring_breakdown": {
  "module_reference": 0,
  "component_match": 25,
  "keyword_density": 20,
  "keyword_density_reason": "47 RFM + 12 format_plausi = 59 matches, 10 keywords, avg 5.9",
  "language_priority": 10,
  "exclusion_penalty": 0,
  "dependency_indicator": 8
}
```

**`keyword_density_reason` MUST show actual math from 4.2 counts.**

---

## Step 5: Validate Before Output (MANDATORY GATE)

**You CANNOT proceed to Step 6 until this validation passes.**

Complete [ANTI-HALLUCINATION.md](ANTI-HALLUCINATION.md) checklist:

```
Pre-Output Validation:
- [ ] Every file with score >= 70 has `content_read: true`
- [ ] Every `keyword_matches` entry has `sample_lines` array with >= 1 line
- [ ] Every `dependencies` entry has `source_line` and `pattern_found`
- [ ] Every `scoring_breakdown` has `keyword_density_reason`
- [ ] No scores were assigned before reading content
```

**If ANY check fails:**
1. Return to Step 4
2. Read the files properly
3. Re-extract evidence
4. Re-run this validation

---

## Step 6: RLM Delegation (DEFAULT for >10 files)

**RLM is the DEFAULT analysis method when > 10 files are discovered.**

You arrive at this step from **Step 3.5** when file count > 10.

**Legacy thresholds (for Step 4 opt-out path only):**

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Single file size | > 5000 lines | Must delegate |
| Total high-relevance files | > 15 | Must delegate |
| Total LOC to analyze | > 50,000 | Must delegate |
| Dependency closure | < 95% after first pass | Must delegate |

### Step 6.0: Confirm RLM Method

**If arriving from Step 3.5 (default path):** Proceed directly to Step 6.1.

**If arriving from Step 4 (opt-out path) and thresholds exceeded:**

```
AskUserQuestion:
  question: "Large codebase detected (${TOTAL_LOC} LOC). Which delegation method?"
  header: "Delegation"
  options:
    - label: "RLM (Recommended)"
      description: "Recursive Language Model with chunking. Better for directory-based analysis, preserves file:line citations."
    - label: "Agent"
      description: "Multi-language-code-analyzer agent. Better for specific file lists."
```

Proceed to **Step 6.1 (RLM)** or **Step 6.2 (Agent)** based on user choice.

---

### Step 6.1: RLM Delegation (mode=dependencies)

Use the RLM skill for directory-based analysis with chunking.

**Step 6.1.1: Initialize RLM**

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm_repl.py init-dir ${CODE_DIR} \
  --pattern "${LANGUAGE_PATTERN}" \
  --recursive \
  --exclude-from results/${FEATURE}/feature-definition.json
```

Example patterns by language:
- PL/SQL: `--pattern "*.sql"`
- TCL: `--pattern "*.tcl"`
- C++: `--pattern "*.cpp" --pattern "*.hpp"`
- Mixed: `--pattern "*.{sql,tcl,cpp,hpp}"`

**Step 6.1.2: Review Session**

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm_repl.py sessions
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm_repl.py --state .claude/rlm_state/session_${SESSION_ID}/state.pkl status
```

**Step 6.1.3: Subcall Loop**

For each chunk, invoke rlm-subcall with mode=dependencies:

```
Task(
  subagent_type="rlm-subcall",
  prompt="Mode: dependencies
Query: Extract code dependencies and keyword matches for feature ${FEATURE}.
Keywords: ${KEYWORDS}
Chunk file: .claude/rlm_state/session_${SESSION_ID}/chunks/${CHUNK_ID}.txt
Manifest: .claude/rlm_state/session_${SESSION_ID}/chunks_manifest.json

Focus on:
1. Package/procedure calls (PL/SQL: package.procedure)
2. Source includes (TCL: source, C++: #include)
3. Keyword occurrences with exact line numbers
4. File boundaries (look for FILE_START/FILE_END markers)"
)
```

Run in batches of 10 for efficiency.

**Step 6.1.4: Transform RLM Output to Phase 1 Format**

After collecting all subcall results, transform to file-inventory.json format:

| RLM Field | Phase 1 Field | Transformation |
|-----------|---------------|----------------|
| `dependencies[].source_file` | `files[].file_path` | Direct mapping |
| `dependencies[].source_line` | `files[].dependencies[].source_line` | Direct mapping |
| `dependencies[].pattern_found` | `files[].dependencies[].pattern_found` | Direct mapping |
| `keyword_matches[].file` | Group by file | Aggregate per file |
| `keyword_matches[].occurrences` | `files[].keyword_matches[].occurrences` | Direct mapping |
| `keyword_matches[].sample_lines` | `files[].keyword_matches[].sample_lines` | Direct mapping |
| (computed) | `content_read` | `true` |
| (computed) | `read_method` | `"rlm_delegated"` |
| (computed) | `scoring_breakdown` | Calculate from keyword counts |
| (computed) | `classification` | Based on relevance_score thresholds |

**Scoring Calculation:**
```python
# For each file, compute score from RLM results
total_matches = sum(km['occurrences'] for km in file_keyword_matches)
keyword_count = len(keywords_from_feature_definition)
avg_matches = total_matches / keyword_count

scoring_breakdown = {
    "module_reference": 30 if in_modules_folder else 0,
    "component_match": 25 if name_in_included_components else 0,
    "keyword_density": min(25, int(avg_matches * 2)),  # Scale to max 25
    "keyword_density_reason": f"{total_matches} matches for {keyword_count} keywords = avg {avg_matches:.1f}",
    "language_priority": {"PL/SQL": 10, "C++": 8, "TCL": 5, "Java": 5, "Shell": 3}.get(language, 3),
    "exclusion_penalty": -50 if matches_excluded_scope else 0,
    "dependency_indicator": 10 if has_dependencies_to_core_files else 0
}
relevance_score = sum(scoring_breakdown.values())
classification = "high" if relevance_score >= 70 else "medium" if relevance_score >= 40 else "low"
```

**Step 6.1.5: Finalize**

After transformation, mark RLM workflow complete:
```
FINAL: RLM delegation complete. Transformed ${FILE_COUNT} files to Phase 1 format.
```

Return to **Step 5** to validate output.

---

### Step 6.2: Agent Delegation

Use the multi-language-code-analyzer agent for specific file analysis.

**Delegation prompt:**
```
Task(
  subagent_type="multi-language-code-analyzer",
  prompt="Read and analyze the following files for feature ${FEATURE}.

  For each file:
  1. Read ENTIRE content
  2. Count keyword matches for: ${KEYWORDS}
  3. Extract dependencies using patterns:
     - PL/SQL: package.procedure( calls
     - TCL: source and SqlStoPro statements
     - C++: #include directives
  4. Return JSON with evidence (line numbers)

  Files: ${FILE_LIST}

  Return format per file:
  {
    'file_path': '...',
    'lines_read': N,
    'keyword_matches': [{'keyword': '...', 'occurrences': N, 'sample_lines': [...]}],
    'dependencies': [{'target': '...', 'source_line': N, 'pattern_found': '...'}]
  }"
)
```

Set `read_method: "agent_delegated"` for files analyzed by this agent.

**Integrate agent results, then return to Step 5.**

---

## Step 7: Write Outputs

Only after Step 5 validation passes:

```
Write(results/${FEATURE}/phase1/file-inventory.json)
Write(results/${FEATURE}/phase1/dependency-graph.json)
```

**Verify all evidence fields are present.**

See [OUTPUT-SCHEMAS.md](OUTPUT-SCHEMAS.md) for complete schema including:
- `content_read` (required)
- `read_method` (required)
- `keyword_matches[].sample_lines` (required)
- `dependencies[].source_line` (required)
- `dependencies[].pattern_found` (required)

---

## Step 8: Present to User

Show results with metrics:

| Metric | Value |
|--------|-------|
| Total files discovered | N |
| High relevance (>= 70) | N |
| Medium relevance (40-69) | N |
| Low relevance (1-39) | N |
| Files fully read | N |
| Dependency closure | X% |

**Use AskUserQuestion:**
- "Does this inventory look complete?"
- "Are there areas to explore deeper?"
- "Proceed to Phase 2?"

---

## Step 9: Rework if Needed

If user identifies gaps:
1. Add missing search terms
2. Return to Step 3
3. Complete full workflow again
4. Maximum 5 rework cycles

---

## RNVS-Specific Knowledge

**File Priority** (most business logic here):
1. PL/SQL packages (`pack_body_*.sql`) - highest priority, READ FULLY
2. C++ managers (`*Manager.cpp`) - high priority
3. TCL scripts (`*.tcl`) - medium priority

**Module Paths:**
- `/modules/rnb` - Number block management
- `/modules/tnb` - Operator management
- `/modules/portierung` - Porting workflows
- `/modules/pda` - PDA exchange

For language-specific patterns, see [RNVS-PATTERNS.md](RNVS-PATTERNS.md).

---

## Error Handling

When errors occur, continue the workflow with documentation:

| Error | Action |
|-------|--------|
| File not found | Mark `content_read: false`, add to `unresolved_files` |
| Permission denied | Document in output, continue with remaining files |
| Large file (>5000 lines) | **MANDATORY delegation** to agent |
| Truncated output | Use chunked reading, document `read_chunks` |

**Principle**: Log errors, document in output, never halt the workflow.

---

## Final Step: Update Workflow State

After user approves results, update `results/${FEATURE}/.workflow-state.md`:

1. **Phase 1**: Set to ✅ Complete with timestamp
2. **Last Activity**: "Completed Phase 1 code analysis"
3. **Next Action**: "Run /02-dependency-visualization-workflow ${FEATURE}"
4. **Decisions Log**: Add any significant analysis decisions

---

## Quick Reference

| Document | Purpose |
|----------|---------|
| [READING-REQUIREMENTS.md](READING-REQUIREMENTS.md) | File reading specifications by tier |
| [RNVS-PATTERNS.md](RNVS-PATTERNS.md) | Dependency extraction patterns |
| [OUTPUT-SCHEMAS.md](OUTPUT-SCHEMAS.md) | JSON output schemas with evidence fields |
| [ANTI-HALLUCINATION.md](ANTI-HALLUCINATION.md) | **MANDATORY** verification checklist |

---

## Success Criteria

Phase 1 is complete when:

1. [ ] All discovered files have `content_read` documented
2. [ ] All high-relevance files were actually READ
3. [ ] All keyword matches have `sample_lines` evidence
4. [ ] All dependencies have `source_line` evidence
5. [ ] Dependency closure >= 95%
6. [ ] Anti-hallucination checklist PASSED
7. [ ] User approved the results
