---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-workflow-09-gap-analysis-workflow
description: Comprehensive gap analysis comparing RNVS legacy capabilities against VNRM designed/modified architecture. Supports both GREENFIELD (Phase 7/8) and CHANGE (Phase 7.1/8.1) modes. Generates coverage metrics, traceability matrices, and prioritized implementation backlog.
context: fork
agent: general-purpose
allowed-tools: Read, Glob, Grep, Write, Task, AskUserQuestion
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/workflow/skills/09-gap-analysis-workflow by codex-knowledge-curation/scripts/persist_project_skills.py. -->

<required_reading>
Read `results/${FEATURE}/.workflow-state.md` before any operation.
This provides workflow mode (NEW or CHANGE), completed phases, and session context.
Use Mode from state file instead of directory-based detection.
</required_reading>

# Phase 9: Gap Analysis Workflow

**Purpose**: Systematic comparison between RNVS legacy functionality and VNRM target architecture, producing coverage metrics, traceability matrices, and prioritized implementation backlog.

**When to use**: After Phase 7/8 (NEW mode) or Phase 7.1/8.1 (CHANGE mode) is complete. Output format is identical for both modes - only input sources differ.

---

## Prerequisites

<prerequisites>
**Feature Identification** - check in order, stop at first match:

1. **User provided feature name** (e.g., "/09-gap-analysis-workflow NBM") → use directly
2. **Conversation context** → use feature from earlier in session
3. **Single feature in results/** → `Glob results/*/phase7/microservice-design.json` OR `Glob results/*/phase7.1/microservice-changes-design.json` - if exactly one, use it
4. **Multiple features** → use AskUserQuestion to let user select
5. **No features with Phase 7/7.1** → "Complete Phase 7 or 7.1 first"

**Mode Detection**:
- `phase7/` exists → GREENFIELD mode
- `phase7.1/` exists → CHANGE mode

**Verify** (based on mode):

**GREENFIELD**:
- `results/${FEATURE}/phase7/microservice-design.json`
- `results/${FEATURE}/phase8/` directory

**CHANGE**:
- `results/${FEATURE}/phase6/analysis.json`
- `results/${FEATURE}/phase7.1/microservice-changes-design.json`
- `results/${FEATURE}/phase8.1/control-flow-changes-design.json`

**Load Feature Context**:
- Read `results/${FEATURE}/feature-definition.json` for feature metadata
- Read `results/${FEATURE}/phase3/ruletable.json` for RNVS business rules
- Read `results/${FEATURE}/phase5/control-flow-mapping.json` for RNVS workflows
</prerequisites>

---

## Overview

Phase 9 Gap Analysis performs systematic comparison and generates actionable outputs:

1. **Detect workflow mode** - GREENFIELD or CHANGE based on directory structure
2. **Extract RNVS capabilities** - From Phase 3/5 outputs
3. **Extract VNRM capabilities** - From Phase 7/8 (greenfield) or Phase 6+7.1/8.1 (change)
4. **Perform systematic comparison** - Map every RNVS component to VNRM equivalent
5. **Calculate coverage metrics** - Using exact formula with proper rounding
6. **Prioritize gaps** - Score by business impact × technical complexity
7. **Generate outputs** - All 7 required files

> **Templates**: See `templates/` directory for output formatting.
> **Schema**: See `schemas/traceability-matrix.schema.json` for JSON structure.

---

## Key Principles

### 1. Coverage Calculation Formula (CRITICAL)

```
Coverage % = (Fully Covered + 0.5 × Partially Covered) / (Total - Not Needed) × 100%
```

**Rounding**: 2 decimal places (e.g., 94.047619% → **94.05%**)

**Consistency**: Same value MUST appear in all output files.

> **Details**: See [references/coverage-calculation.md](references/coverage-calculation.md)

### 2. Coverage Status Definitions

| Status | Symbol | Weight | Meaning |
|--------|--------|--------|---------|
| **Fully Covered** | ✅ | 1.0 | 100% implemented in VNRM |
| **Partially Covered** | ⚠️ | 0.5 | 50-99% implemented |
| **Not Covered** | ❌ | 0.0 | Gap - not implemented |
| **Not Needed** | 🗑️ | Excluded | Deprecated/obsolete |

### 3. Priority Scoring

```
Priority Score = (Business Impact × 3) + (Technical Urgency × 2) + (Dependencies × 1)
```

| Priority | Score | Sprint |
|----------|-------|--------|
| **P0 (Critical)** | ≥20 | Sprint 1 |
| **P1 (High)** | 15-19 | Sprint 1-2 |
| **P2 (Medium)** | 10-14 | Sprint 2-3 |
| **P3 (Low)** | <10 | Backlog |

> **Details**: See [references/priority-framework.md](references/priority-framework.md)

### 4. Effort Estimation

| Size | Duration |
|------|----------|
| **XS** | 1-2 hours |
| **S** | 2-8 hours |
| **M** | 1-3 days |
| **L** | 3-10 days |
| **XL** | 10+ days |

### 5. Source Priority by Mode

**GREENFIELD Mode**:

| Priority | Source | Usage |
|----------|--------|-------|
| **PRIMARY** | Phase 7 `microservice-design.json` | VNRM design |
| **SECONDARY** | Phase 8 `*.puml` | Control flows |
| **SUPPORTING** | Phase 3 `ruletable.json` | RNVS rules |
| **CONTEXT** | Phase 5 `control-flow-mapping.json` | RNVS workflows |

**CHANGE Mode**:

| Priority | Source | Usage |
|----------|--------|-------|
| **PRIMARY** | Phase 6 + Phase 7.1 | Baseline + delta |
| **SECONDARY** | Phase 8.1 | Control flow changes |
| **SUPPORTING** | Phase 3 `ruletable.json` | RNVS rules |
| **CONTEXT** | Phase 5 `control-flow-mapping.json` | RNVS workflows |

---

## 7-Stage Workflow

**Output directory**: `results/${FEATURE}/phase9/`

### Stage 1: Detect Mode and Load Inputs

Detect mode by checking directory existence, then load inputs in parallel.

**Output**: Mode determination, loaded JSON objects

### Stage 2: Extract RNVS Capabilities

Extract from Phase 3/5:
- Business rules from `ruletable.json`
- Workflows from `control-flow-mapping.json`
- Integrations from dependency analysis

**Output**: `rnvs_capability_inventory.md`

### Stage 3: Extract VNRM Capabilities

**Before extracting capabilities**: Use **vnrm-confluence-data-provider** to enhance VNRM understanding:
- Reference page ID 2109544290 ("VNRM: Business analysis") for complete VNRM business capability overview
- Reference page ID 2109544636 ("VNRM: Main Business Use cases") for official VNRM business use cases and functional scope
- Search for "VNRM business objects" to get comprehensive business entity model
- Use this context to validate and supplement the extracted capabilities from phase outputs

**GREENFIELD**: Extract from Phase 7/8 design files.
**CHANGE**: Merge Phase 6 baseline + Phase 7.1/8.1 delta.

**Output**: `vnrm_capability_inventory.md`

### Stage 4: Systematic Comparison

For each RNVS component:
1. **Search for VNRM equivalent** (enhanced with Confluence data):
   - Use extracted VNRM capabilities from Phase outputs (primary source)
   - Cross-reference with official VNRM business capabilities from Confluence (validation source)
   - Check against VNRM main business use cases for functional scope validation
2. Assess coverage status
3. Assign confidence (high/medium/low)
4. Document gap if not fully covered

**Output**: `traceability_matrix.json`

### Stage 5: Calculate Coverage Metrics

Apply formula to each category:
- Business Rules
- API Endpoints
- Database Tables
- Integrations
- Events/Async

**Validate**: Same percentages appear in all output files.

### Stage 6: Prioritize Gaps

For each gap:
1. Score business impact (1-5)
2. Score technical urgency (1-5)
3. Score dependencies (1-5)
4. Calculate priority score
5. Assign priority level (P0/P1/P2/P3)
6. Estimate effort (XS/S/M/L/XL)

**Output**: `implementation_backlog.md`

### Stage 7: Generate Final Outputs

Generate all required files using templates:

| File | Purpose |
|------|---------|
| `rnvs_capability_inventory.md` | RNVS components list |
| `vnrm_capability_inventory.md` | VNRM components list |
| `gap_analysis.md` | Comprehensive report |
| `gap_summary.csv` | Quick reference |
| `traceability_matrix.json` | Machine-readable mapping |
| `implementation_backlog.md` | Prioritized tasks |
| `PHASE9_SUMMARY.md` | Executive summary |

> **Templates**: See `templates/` directory.

---

## CHANGE Mode Specifics

When in CHANGE mode, include additional fields:

**Gap Classification**:

| Type | Description |
|------|-------------|
| **Existing Gap** | Gap existed before, still not covered |
| **New Gap** | New RNVS requirement not covered |
| **Resolved Gap** | Previously identified gap now covered |

**Traceability Entry**:
```json
{
  "change_type": "new_in_delta",
  "delta_source": "phase7.1/microservice-changes-design.json"
}
```

---

## Integration with Other Phases

### Input from Previous Phases

| Phase | File | Usage |
|-------|------|-------|
| Phase 3 | ruletable.json | RNVS business rules |
| Phase 5 | control-flow-mapping.json | RNVS workflows |
| Phase 7 | microservice-design.json | VNRM design (GREENFIELD) |
| Phase 6+7.1 | analysis.json + delta | VNRM state (CHANGE) |
| Phase 8/8.1 | *.puml | Control flows |

### Output to Subsequent Phases

| Phase | Consumer | Usage |
|-------|----------|-------|
| Phase 10 | Story Generation | Gap-based user stories |
| Phase 11 | System Test | Test scenarios from gaps |
| Phase 12 | Unit Tests | Test cases from traceability |

---

## Success Criteria

Phase 9 succeeds when:

- [ ] Workflow mode correctly detected (GREENFIELD vs CHANGE)
- [ ] All RNVS components mapped in traceability matrix
- [ ] Coverage percentages calculated with exact formula
- [ ] Same coverage values in ALL output files (consistency)
- [ ] Every gap has priority (P0/P1/P2/P3)
- [ ] Every gap has effort estimate (XS/S/M/L/XL)
- [ ] Implementation backlog prioritized by sprint
- [ ] All 7 output files generated
- [ ] JSON files valid, CSV properly formatted

---

## Common Pitfalls and Fixes

| Pitfall | Fix |
|---------|-----|
| Inconsistent coverage percentages | Calculate once, use same value everywhere |
| Missing RNVS components | Include ALL components, not just gaps |
| No priority on gaps | Assign P0/P1/P2/P3 to every gap |
| No effort estimate | Assign XS/S/M/L/XL to every gap |
| Wrong rounding | Use 2 decimal places (94.05%, not 94%) |
| Mode detection failure | Check for phase7/ vs phase7.1/ directories |

---

## Related Skills

- **vnrm-confluence-data-provider** - VNRM architecture documentation (use for business capability validation, official use cases, and business object model)
- **07-0-microservice-design-workflow** - Phase 7 (GREENFIELD input)
- **07-1-microservice-delta-workflow** - Phase 7.1 (CHANGE input)
- **10-story-generation-workflow** - Phase 10 (consumes gap analysis)
- **plantuml-generator** - Gap visualization diagrams

---
