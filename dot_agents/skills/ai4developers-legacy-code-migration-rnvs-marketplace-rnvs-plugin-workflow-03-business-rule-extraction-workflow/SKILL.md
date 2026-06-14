---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-workflow-03-business-rule-extraction-workflow
description: Phase 3 business rule extraction. **RLM is DEFAULT for >10 files** - uses two-stage extraction (quick scan → deep dive) with file:line citations. Outputs ruletable.json with source-accountable rules, confidence scoring (1-5), and specialist skill integration. Use after Phase 1 and Phase 2 completion.
allowed-tools: Read, Glob, Grep, Write, Skill, AskUserQuestion, Bash, Task
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/workflow/skills/03-business-rule-extraction-workflow by codex-knowledge-curation/scripts/persist_project_skills.py. -->

<required_reading>
Read `results/${FEATURE}/.workflow-state.md` before any operation.
This provides workflow mode, completed phases, and session context.
</required_reading>

# Phase 3: Business Rule Extraction Workflow

**Purpose**: Extract comprehensive business rules from Phase 1 code analysis and Phase 2 dependency diagrams with source accountability and user validation.

**When to use**: After Phase 1 (Code Analysis) and Phase 2 (Dependency Visualization) are complete.

---

## Prerequisites (Execute First)

<prerequisites>
**Feature Identification** - check in order, stop at first match:

1. **User provided feature name** (e.g., "/03-business-rule-extraction-workflow NBM") → use directly
2. **Conversation context** → use feature from earlier in session
3. **Single feature in results/** → `Glob results/*/feature-definition.json` - if exactly one, use it
4. **Multiple features** → use AskUserQuestion to let user select
5. **No features** → "Run /00-feature-definition-workflow first"

**Verify Phase 1/2 outputs exist**:
- `results/${FEATURE}/phase1/file-inventory.json`
- `results/${FEATURE}/phase1/dependency-graph.json`
- `results/${FEATURE}/phase2/dependencies.puml`

If missing → "Complete Phase 1/2 first."
</prerequisites>

---

## Step 0: Load Workflow State

Read `results/${FEATURE}/.workflow-state.md` and verify:

1. **Phase Check**: Phase 1 and 2 must be ✅ Complete
2. **Status**: Should be "In Progress"

If state file missing: "Run /00-feature-definition-workflow first to initialize workflow state."

**Update state**: Set Phase 3 to 🔄 In Progress, update Last Activity.

---

## Step 0.5: RLM Delegation Check (MANDATORY)

**IMMEDIATELY after loading Phase 1 results, count high-relevance files:**

```python
# Read file-inventory.json
high_relevance_count = len([f for f in files if f['relevance_score'] >= 70])
```

| Condition | Threshold | Action |
|-----------|-----------|--------|
| High-relevance files | > 10 | **RLM is DEFAULT** - proceed to RLM-Enhanced Workflow |
| High-relevance files | <= 10 | Standard Workflow (direct reading) |

**This check is BLOCKING** - you cannot proceed to Standard Workflow if > 10 high-relevance files.

### If > 10 high-relevance files:

**Ask user for confirmation (opt-out only):**
```
AskUserQuestion:
  question: "${FILE_COUNT} high-relevance files found. RLM chunking is recommended for accurate business rule extraction. Proceed with RLM?"
  header: "RLM Extraction"
  options:
    - label: "Yes, use RLM (Recommended)"
      description: "Two-stage extraction with file:line citations and specialist enrichment"
    - label: "No, read files directly"
      description: "Only for small codebases. May miss patterns in large files."
```

**If user selects RLM (default):** Skip Standard Workflow, go directly to **RLM-Enhanced Workflow**.

**If user opts out:** Proceed to Standard Workflow, but warn about potential accuracy issues.

---

## Workflow Steps

### Standard Workflow (Small Codebases - ≤10 files)

1. **Load Phase 1/2 results** → file-inventory.json, dependency-graph.json, dependencies.puml
2. **Extract from Phase 1**:
   - `files[].functions` → validation logic, return conditions, exceptions
   - `files[].dependencies` → cross-component rules
   - Database operations → constraints, triggers, stored procedures
3. **Extract from Phase 2**:
   - Component diagrams → integration validation, dependency constraints
   - Flow diagrams → decision points, error paths, validation steps
4. **Enrich with specialist skills** → consult rnvs-error-code-specialist, porting-data-exchange-specialist
5. **Group rules** → organize by business/technical process (5-10 rules per group)
6. **Present to user** → grouped rules for validation
7. **Rework if needed** → incorporate feedback (max 3 cycles per group)

---

### RLM-Enhanced Workflow (Recommended for Large Codebases)

Use the RLM (Recursive Language Model) skill for business rule extraction when:
- Phase 1 analyzed >30 high-relevance files
- Total LOC in scope >50,000
- Deep pattern analysis required across many files

**RLM provides**:
- Two-stage extraction: quick scan (Haiku) → user selection → deep dive (Sonnet)
- File:line citations for all extracted rules
- Automatic specialist skill enrichment for error codes
- Parallel processing of large codebases

#### Step 1: Load Files and Configure Patterns

**1.1 Load Phase 1 file list**:
```
Read results/${FEATURE}/phase1/file-inventory.json
Filter files with relevance_score >= 70 (high-relevance)
```

**1.2 Load pattern configuration**:

Check `results/${FEATURE}/feature-definition.json` for `rule_patterns` field:
```json
{
  "rule_patterns": {
    "pattern_types": ["validation", "error_code", "state_transition"],
    "focus_areas": ["operator validation", "number block lifecycle"],
    "error_code_prefixes": ["RNBFM", "ECRM", "PFM"]
  }
}
```

**1.3 Ask user to confirm/adjust patterns** (use AskUserQuestion):

```
AskUserQuestion:
  question: "Rule extraction patterns configured. Proceed with these settings?"
  header: "Patterns"
  options:
    - label: "Use defaults (Recommended)"
      description: "validation, error_code, state_transition patterns"
    - label: "Add calculation rules"
      description: "Include pricing, fee, and calculation logic"
    - label: "Add security rules"
      description: "Include authentication and authorization checks"
    - label: "Custom configuration"
      description: "Specify custom pattern types and focus areas"
```

If user selects "Custom configuration", use additional questions to gather specific patterns.

#### Step 2: Stage 1 - Quick Scan (Haiku)

**2.1 Initialize RLM session**:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm_repl.py init-dir ${CODE_DIR} \
  --pattern "${LANGUAGE_PATTERN}" \
  --exclude-from results/${FEATURE}/feature-definition.json
```

**2.2 Process chunks with rlm-subcall** (mode=business_rules):

```
Task(subagent_type="rlm-subcall", model="haiku"):
  Mode: business_rules
  Stage: quick_scan
  Patterns: ${PATTERN_TYPES}
  Chunk file: .claude/rlm_state/session_<id>/chunks/chunk_NNNN.txt
  Manifest: .claude/rlm_state/session_<id>/chunks_manifest.json
```

Run in batches of 10 for efficiency.

**2.3 Aggregate quick scan results**:

Collect all subagent outputs and summarize:
- Total rule candidates found
- Rules per file
- Rules by pattern type
- Confidence distribution

#### Step 3: Present Summary to User

**3.1 Show summary**:

```
Found 47 rule candidates across 12 files:

High-relevance files (8+ rules):
  - pack_body_rnb.sql: 15 rules (12 validation, 3 error_code)
  - pack_body_crm.sql: 12 rules (8 validation, 4 state_transition)
  - pack_body_val.sql: 8 rules (6 validation, 2 constraint)

Medium-relevance files (3-7 rules):
  - pack_body_tnb.sql: 5 rules
  - pack_body_cfg.sql: 4 rules
  - pack_body_pm.sql: 3 rules
```

**3.2 Ask user to select files for deep dive**:

```
AskUserQuestion:
  question: "Select files for detailed analysis (Stage 2 with Sonnet):"
  header: "Deep dive"
  multiSelect: true
  options:
    - label: "All high-relevance files (Recommended)"
      description: "pack_body_rnb.sql, pack_body_crm.sql, pack_body_val.sql"
    - label: "All files"
      description: "Full deep dive on all 12 files"
    - label: "Custom selection"
      description: "I'll specify which files to analyze"
```

#### Step 4: Stage 2 - Deep Dive (Sonnet)

**4.1 Re-analyze selected files with Sonnet**:

Reuse Stage 1 chunks (same manifest) for selected files only:

```
Task(subagent_type="rlm-subcall", model="sonnet"):
  Mode: business_rules
  Stage: deep_dive
  Patterns: ${PATTERN_TYPES}
  Chunk file: .claude/rlm_state/session_<id>/chunks/chunk_NNNN.txt
  Manifest: .claude/rlm_state/session_<id>/chunks_manifest.json
```

**4.2 Specialist skill integration**:

The rlm-subcall agent will automatically call specialist skills for error codes:
- RNBFM, BFM, VFM → `rnvs-expert-skills:booking-distribution-error-specialist`
- ECRM → `rnvs-expert-skills:crm-integration-error-specialist`
- PFM, WFA, WFB, RNBFM → `rnvs-expert-skills:porting-workflow-error-specialist`
- PDA codes → `rnvs-expert-skills:porting-data-exchange-specialist`

**4.3 Enhanced output with specialist context**:

```json
{
  "business_rules": [
    {
      "file": "pack_body_rnb.sql",
      "line": 234,
      "pattern_type": "error_code",
      "rule_pattern": "IF p_tnb.get_operator(v_tnb_id) IS NULL THEN",
      "evidence": "IF ... IS NULL THEN RAISE_APPLICATION_ERROR(-20002, 'RNBFM002')",
      "error_code": "RNBFM002",
      "error_code_context": {
        "description": "Invalid Operator Reference",
        "domain": "Number Block Management",
        "severity": "error",
        "source": "rnvs-expert-skills:booking-distribution-error-specialist"
      },
      "confidence": "high"
    }
  ]
}
```

#### Step 5: Transform RLM Output to ruletable.json

Apply Phase 3 transformer to convert RLM raw output to ruletable.json schema.

See [Transformer Logic](#phase-3-transformer-logic) section below.

#### Step 6: User Validation

Present grouped rules for user validation (same as standard workflow Step 6-7).

---

## Phase 3 Transformer Logic

Transform RLM `business_rules` output to `ruletable.json` schema.

### Transformer Mapping

| RLM Field | ruletable.json Field | Transformation |
|-----------|---------------------|----------------|
| `business_rules[].file` | `rules[].source_location` | Format as `{file}:{line}` |
| `business_rules[].line` | `rules[].source_location` | Append to file |
| `business_rules[].evidence` | `rules[].source_evidence` | Direct mapping |
| `business_rules[].pattern_type` | `rules[].rule_category` | Direct mapping |
| `business_rules[].error_code` | `rules[].error_code` | Direct mapping |
| `business_rules[].error_code_context` | `rules[].enrichment` | Include specialist data |
| `business_rules[].confidence` | `rules[].confidence_score` | Map: high=5, medium=3, low=1 |
| `business_rules[].stage` | `rules[].extraction_stage` | Preserve for transparency |
| (computed) | `rules[].rule_id` | Auto-generate: `{FEATURE}-BR-{NNN}` |
| (computed) | `rules[].rule_name` | Generate from pattern + context |
| (computed) | `rules[].validation_status` | `"pending"` until user confirms |
| (computed) | `rules[].source_type` | `"source_code"` for RLM-extracted |

### Rule ID Generation

Format: `{FEATURE}-BR-{NNN}`
- `{FEATURE}`: Feature name from feature-definition.json
- `BR`: Business Rule prefix
- `{NNN}`: Zero-padded sequential number (001, 002, ...)

Example: `NBM-BR-001`, `NBM-BR-002`, `FNPORT-BR-015`

### Rule Name Generation

Generate from pattern type and context:
- **validation**: `"{subject} Validation Before {action}"`
- **error_code**: `"Error {code}: {description}"`
- **state_transition**: `"{entity} State Transition: {from} → {to}"`
- **constraint**: `"{entity} {constraint_type} Constraint"`
- **calculation**: `"{subject} Calculation Rule"`

Use error_code_context if available for better naming.

### Stage Combination Strategy

Both Stage 1 (quick_scan) and Stage 2 (deep_dive) results are preserved:
- Each rule has `extraction_stage` field for transparency
- Stage 2 rules override Stage 1 if same file:line
- User sees extraction method during validation

### Confidence Mapping

| RLM Confidence | ruletable.json Score | Rationale |
|----------------|---------------------|-----------|
| `high` | 5 | Clear code evidence with error code |
| `medium` | 3 | Pattern detected but context unclear |
| `low` | 1 | Possible rule, requires user confirmation |

### Grouping Rules

Group rules by business/technical process (5-10 rules per group):

1. **By error code prefix**: RNBFM*, ECRM*, PFM* → separate groups
2. **By business process**: validation, state management, integration
3. **By source file**: If natural groupings emerge by package

### Example Transformer Output

**Input (RLM output)**:
```json
{
  "business_rules": [
    {
      "file": "pack_body_rnb.sql",
      "line": 234,
      "pattern_type": "error_code",
      "rule_pattern": "IF p_tnb.get_operator(v_tnb_id) IS NULL THEN",
      "evidence": "RAISE_APPLICATION_ERROR(-20002, 'RNBFM002')",
      "error_code": "RNBFM002",
      "error_code_context": {
        "description": "Invalid Operator Reference",
        "domain": "Number Block Management"
      },
      "confidence": "high",
      "stage": "deep_dive"
    }
  ]
}
```

**Output (ruletable.json)**:
```json
{
  "rules": [
    {
      "rule_id": "NBM-BR-001",
      "rule_name": "Error RNBFM002: Invalid Operator Reference",
      "rule_description": "Operator must exist in TNB table before number block assignment",
      "rule_category": "error_code",
      "source_location": "pack_body_rnb.sql:234",
      "source_type": "source_code",
      "source_evidence": "RAISE_APPLICATION_ERROR(-20002, 'RNBFM002')",
      "confidence_score": 5,
      "confidence_rationale": "Clear code evidence with error code (deep_dive stage)",
      "error_code": "RNBFM002",
      "enrichment": {
        "description": "Invalid Operator Reference",
        "domain": "Number Block Management",
        "source": "rnvs-expert-skills:booking-distribution-error-specialist"
      },
      "extraction_stage": "deep_dive",
      "validation_status": "pending"
    }
  ]
}
```

---

## Key Principles

### Source Accountability (Zero Tolerance for Speculation)

Every rule MUST cite exact source:
- `source_location`: "file.ext:line_number" or "flow_diagram:step_number"
- `source_type`: "source_code", "pda_error_code", "rnvs_error_code", "code_comment", "user_confirmed"
- `source_evidence`: Direct quote or paraphrase from source

**NEVER** add rules "because they logically should exist."

### Honest Confidence Scoring (1-5)

| Score | Meaning | Evidence Required |
|-------|---------|-------------------|
| 5 | Very High | Explicit code + documentation/comments |
| 4 | High | Clear logic from code structure |
| 3 | Medium | Supported by comments or naming conventions |
| 2 | Low | Partial evidence, requires inference |
| 1 | Very Low | Minimal evidence, high uncertainty |

**Mark uncertainty honestly** - do not inflate scores.

### Source Priority Hierarchy

1. **Source Code** (HIGHEST) - Actual implementation logic
2. **Domain Specifications** - PDA spec, regulatory docs via specialist skills
3. **Error Code Specialists** - RNVS domain context
4. **Code Comments** - Developer documentation
5. **NEVER Speculation**

---

## RNVS-Specific Guidance

**Rule Extraction Priority**:
1. **PL/SQL packages FIRST** (pack_body_*.sql) - highest business logic density
2. **Java/C++ orchestration SECOND**
3. **TCL scripts THIRD**

**Specialist Skill Consultation**:
- Rules mentioning KCODE, PDA, porting → consult **porting-data-exchange-specialist**
- Rules mentioning ECRM, PFM, RNBFM, BFM error codes → consult **rnvs-error-code-specialist**

For RNVS-specific extraction patterns, see [RNVS-EXTRACTION.md](RNVS-EXTRACTION.md).

---

## Output: ruletable.json

**File Location**: `results/${FEATURE}/phase3/ruletable.json`

**Key Fields**:
```json
{
  "feature": "NBM",
  "rules": [{
    "rule_id": "NBM-BR-001",
    "rule_name": "Operator Validation Before RNB Assignment",
    "rule_description": "Operator must exist in TNB table before number block assignment",
    "source_location": "pack_body_rnb.sql:234",
    "source_type": "source_code",
    "source_evidence": "IF p_tnb.get_operator(v_tnb_id) IS NULL THEN RAISE RNBFM002",
    "confidence_score": 5,
    "validation_status": "user_confirmed"
  }],
  "rule_groups": [...],
  "summary": {...},
  "validation_report": {...}
}
```

For complete schema, see [OUTPUT-SCHEMA.md](OUTPUT-SCHEMA.md).

---

## Anti-Hallucination Checklist

Before finalizing ruletable.json:

- Every rule has verifiable `source_location` (file:line or flow:step)
- `source_evidence` directly quotes or accurately paraphrases source
- `confidence_score` based on evidence clarity, not assumptions
- No rules added based on "logical assumptions" or "should exist"
- All specialist skill references actually consulted
- `validation_status` reflects actual user confirmation

For complete checklist, see [ANTI-HALLUCINATION.md](ANTI-HALLUCINATION.md).

---

## Phase Integration

| Phase | Input Files | Purpose |
|-------|-------------|---------|
| Phase 1 | file-inventory.json, dependency-graph.json | Components, dependencies |
| Phase 2 | dependencies.puml, dependencies_detailed.puml | Control flow, error paths |

**Output to Phase 4**: ruletable.json for business logic documentation.

---

## Success Criteria

Phase 3 succeeds when:

1. ruletable.json exists with comprehensive rules from Phase 1 AND Phase 2
2. All rules have verifiable source_location and source_evidence
3. Confidence scores are honest (based on evidence, not assumptions)
4. Rules grouped by business/technical process
5. User has validated all rule groups
6. Specialist skills consulted where appropriate (error codes, PDA)
7. Ready to proceed to Phase 4

---

## Final Step: Update Workflow State

After user validates all rule groups, update `results/${FEATURE}/.workflow-state.md`:

1. **Phase 3**: Set to ✅ Complete with timestamp
2. **Last Activity**: "Completed Phase 3 business rule extraction"
3. **Next Action**: "Run /04-business-documentation-workflow ${FEATURE}"
4. **Decisions Log**: Add any rule extraction decisions

---

## Quick Reference

| Document | Purpose |
|----------|---------|
| [RNVS-EXTRACTION.md](RNVS-EXTRACTION.md) | RNVS-specific extraction patterns and specialist skill triggers |
| [OUTPUT-SCHEMA.md](OUTPUT-SCHEMA.md) | Complete ruletable.json schema |
| [ANTI-HALLUCINATION.md](ANTI-HALLUCINATION.md) | Source verification checklist |
| [references/](references/) | Example ruletable.json |

---

**Remember**: Phase 3 is about **extraction and validation**, not invention. Every rule must be code-backed with verifiable source. Engage the user throughout. Be honest about confidence.
