---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-workflow-08-1-control-flow-delta-workflow
description: Design control flow CHANGES to existing VNRM flows based on Phase 7.1 microservice modifications. Use for Phase 8.1 (CHANGE mode only) after Phase 7.1. Creates delta diagrams showing additions and modifications to sequence, activity, saga, and event flows. Outputs control-flow-changes-design.json and quality reports.
context: fork
agent: general-purpose
allowed-tools: Read, Glob, Grep, Write, Task, AskUserQuestion
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/workflow/skills/08-1-control-flow-delta-workflow by codex-knowledge-curation/scripts/persist_project_skills.py. -->

<required_reading>
Read `results/${FEATURE}/.workflow-state.md` before any operation.
This provides workflow mode, completed phases, and session context.
</required_reading>

<state_management>
**Phase 8.1 VERIFIES Mode=CHANGE.**
Phase 6 must have set Mode=CHANGE. If Mode is NEW or UNKNOWN, this is an error.
</state_management>

# Phase 8.1: Control Flow Delta Workflow

**Purpose**: Design control flow changes (deltas) to existing VNRM flows based on Phase 7.1 microservice modifications, showing what gets added or modified in service orchestration.

**When to use**: After Phase 7.1 (Microservice Delta Design) is complete, with microservice-changes-design.json available. This is for CHANGE mode (modifying existing control flows) - for NEW mode, use 08-0-control-flow-design-workflow.

---

## Prerequisites

<prerequisites>
**Feature Identification** - check in order, stop at first match:

1. **User provided feature name** (e.g., "/08-1-control-flow-delta-workflow NBM") → use directly
2. **Conversation context** → use feature from earlier in session
3. **Single feature in results/** → `Glob results/*/phase7.1/microservice-changes-design.json` - if exactly one, use it
4. **Multiple features** → use AskUserQuestion to let user select
5. **No features with Phase 7.1** → "Complete Phase 7.1 first with /07-1-microservice-delta-workflow"

**Verify**: Required files exist:
- `results/${FEATURE}/phase7.1/microservice-changes-design.json` (PRIMARY)
- `results/${FEATURE}/phase7.1/classification.json` (CONTEXT)
- `results/${FEATURE}/phase5/control-flow-mapping.json` (SUPPORTING)

**Load Feature Context**:
- Read `results/${FEATURE}/feature-definition.json` for feature metadata
- Extract `feature_name`, `feature_description`, `scope`
</prerequisites>

---

## Step 0: Load Workflow State

Read `results/${FEATURE}/.workflow-state.md` and verify:

1. **Phase Check**: Phase 7.1 must be ✅ Complete
2. **Mode Check**: Must be `CHANGE` (set by Phase 6)
3. **Status**: Should be "In Progress"

If state file missing: "Run /00-feature-definition-workflow first to initialize workflow state."

**If Mode is not CHANGE**: ERROR - "Mode is ${MODE}, but Phase 8.1 requires CHANGE mode. Use /08-0-control-flow-design-workflow for NEW mode."

**Update state**:
- Set Phase 8.1 to 🔄 In Progress
- Update Last Activity: "Designing control flow delta for CHANGE mode"

---

## Overview

Phase 8.1 Control Flow Delta Design transforms microservice deltas into control flow modifications:

1. **Load Phase 7.1 results** - Use microservice changes as primary input, with Phase 5 and baseline Phase 8 as context
2. **Compute control flow delta** - Identify which flows need updates based on endpoint/event changes
3. **Classify change complexity** - Determine MINOR, MODERATE, or MAJOR based on change scope
4. **Design flow deltas** - Create delta diagrams showing additions and modifications
5. **Update API contracts** - Modify OpenAPI specifications for changed endpoints
6. **Validate changes** - Ensure consistency with baseline flows and VNRM patterns
7. **Produce final outputs** - Delta diagrams, modified specs, change documentation, quality report

> **Pattern References**: See `patterns/` directory for delta diagram patterns.

---

## Key Principles

### 1. Delta Model Approach (CRITICAL)

Phase 8.1 uses delta model - document ONLY what changes, not entire flows.

| Delta Type | Description | Action |
|------------|-------------|--------|
| **ADD** | New diagrams for new endpoints | Create new sequence diagram |
| **MODIFY** | Updated diagrams for changed endpoints | Annotate changes in existing |
| **REUSE** | Unchanged flows | Reference only |

**Anti-Pattern**: Do NOT recreate entire flows. Only show deltas with change annotations.

### 2. Change Annotation Standards (MANDATORY)

All delta diagrams MUST include yellow notes (#FFFF00):

```plantuml
note right of PARTICIPANT #FFFF00
  **NEW in Phase 8.1**
  [Description]
  Source: Phase 7.1 [reference]
end note
```

### 3. Source Priority Hierarchy

| Priority | Source | Usage |
|----------|--------|-------|
| **PRIMARY** | Phase 7.1 `microservice-changes-design.json` | Endpoint/event changes |
| **SECONDARY** | Phase 8 `*.puml` (if available) | Baseline flows to modify |
| **SUPPORTING** | Phase 5 `control-flow-mapping.json` | Business context |
| **CONTEXT** | Phase 7.1 `classification.json` | Change type |

### 4. VNRM Color Scheme

| Submodule | Hex | Usage |
|-----------|-----|-------|
| **NUM** | #FFAB91 | Number management |
| **PRT** | #90CAF9 | Porting services |
| **COM** | #CFD8DC | Common services |
| **SPE** | #FFF59D | Special functions |
| **COR** | #FFCDD2 | Correction services |
| **NTW** | #C8E6C9 | Network services |

### 5. Change Complexity Classification

| Type | Criteria | Quality Target |
|------|----------|----------------|
| **MINOR** | 1-2 endpoint changes, no new services | ≥85/100 |
| **MODERATE** | 3-5 endpoint changes, 1 new dependency | ≥80/100 |
| **MAJOR** | 6+ changes, 2+ new services, new saga | ≥75/100 |

---

## 7-Stage Delta Design Workflow

**Output directory**: `results/${FEATURE}/phase8.1/`

### Stage 1: Load Phase 7.1 Results and Baseline

**First, gather VNRM control flow standards**: Use **vnrm-confluence-data-provider** skill:
- Reference page ID 2069758700 for VNRM platform architecture patterns
- Search for VNRM interface documentation and control flow standards
- Validate delta changes against VNRM architectural patterns

Read in parallel:
- `results/${FEATURE}/phase7.1/microservice-changes-design.json` (PRIMARY)
- `results/${FEATURE}/phase7.1/classification.json` (CONTEXT)
- `results/${FEATURE}/phase5/control-flow-mapping.json` (SUPPORTING)
- `results/${FEATURE}/phase8/*.puml` (BASELINE - if available)

**Extract from Phase 7.1**: `endpoints_to_add[]`, `endpoints_to_modify[]`, `topics_to_add[]`, `new_internal_dependencies[]`

### Stage 2: Compute Control Flow Delta

Map Phase 7.1 changes to affected flows:

| Phase 7.1 Change | Flow Impact |
|------------------|-------------|
| `endpoints_to_add` | New sequence diagrams |
| `endpoints_to_modify` | Modified sequence diagrams |
| `topics_to_add` | Event architecture updates |
| `new_internal_dependencies` | New service interactions |

**Output**: `computed-control-flow-delta.json`

### Stage 3: Classify Change Complexity

Determine MINOR/MODERATE/MAJOR based on:
- Count of sequences to add/modify
- Count of activities to modify
- Count of sagas to add

**Output**: `classification.json`

### Stage 4: Design Delta Sequence Diagrams

Design 2-3 sequence diagrams at a time with delta annotations.

**Key elements**:
- Annotate ALL new participants with yellow notes
- Annotate ALL new interactions with yellow notes
- Comment out baseline interactions that changed
- Reference unchanged parts to baseline

> **Patterns**: See `patterns/sequence-delta-patterns.md`

**Output**: `sequence-*.puml` files with annotations

### Stage 5: Design Delta Activity Diagrams

Modify activity diagrams for changed business processes.

**Key elements**:
- Use `floating note:` for sections, NOT `== Section ==`
- Annotate new steps with yellow notes
- Include new compensation logic
- Reference unchanged steps to baseline

> **Critical**: Use `floating note:` or `partition {}` - never `== Section ==`.

**Output**: `activity-*.puml` files with annotations

### Stage 6: Design Delta Saga Diagrams

Add saga diagrams if Phase 7.1 introduces distributed transactions.

**When to add**:
- Multi-service transaction added
- Compensation logic required

**Output**: `saga-*.puml` files (if applicable)

### Stage 7: Update Event Flow and OpenAPI

Update event architecture and generate OpenAPI delta specs.

**Event flow**: Show only new topics and subscribers with annotations.

**OpenAPI deltas**: Show only changed endpoints, not entire spec.

**Output**:
- `event-architecture-modified.puml`
- `openapi-*-delta.yaml` files
- `control-flow-changes.md`
- `changes-quality-report.json`

---

## Required Annotations

Every delta diagram element MUST have:

| Element Type | Required Fields |
|--------------|-----------------|
| **New participant** | Yellow note with "NEW in Phase 8.1", source reference |
| **New interaction** | Yellow note with description, Phase 7.1 reference |
| **Modified interaction** | Comment with BEFORE/AFTER, yellow note with change |
| **Unchanged section** | Reference note: "See baseline: [filename].puml" |

---

## Integration with Other Phases

### Input from Previous Phases

| Phase | File | Usage |
|-------|------|-------|
| Phase 7.1 | microservice-changes-design.json | Primary: endpoint/event changes |
| Phase 7.1 | classification.json | Context: change type |
| Phase 8 | *.puml | Baseline: existing flows to modify |
| Phase 5 | control-flow-mapping.json | Supporting: business context |

### Output to Subsequent Phases

| Phase | Consumer | Usage |
|-------|----------|-------|
| Phase 9 | Gap Analysis | Validate flow changes cover requirements |
| Phase 10 | Story Generation | Change-based user stories |
| Phase 14 | Test Scripts | Modified API contract testing |

---

## Success Criteria

Phase 8.1 succeeds when:

- [ ] All Phase 7.1 endpoint changes have corresponding flow deltas
- [ ] All new elements annotated with yellow notes (#FFFF00)
- [ ] All modifications include source references
- [ ] Baseline flows referenced for unchanged parts
- [ ] VNRM color scheme used consistently
- [ ] Activity diagrams use correct syntax (no `== Section ==`)
- [ ] All PlantUML diagrams validate without syntax errors
- [ ] OpenAPI delta specs show only changed endpoints
- [ ] control-flow-changes.md is comprehensive
- [ ] changes-quality-report.json shows quality score ≥ target
- [ ] All changes traceable to Phase 7.1 sources

---

## Common Pitfalls and Fixes

| Pitfall | Fix |
|---------|-----|
| Recreating entire flows | Use delta model - show ONLY changes |
| Missing change annotations | Add yellow notes (#FFFF00) to ALL new/modified elements |
| No source references | Include "Source: Phase 7.1 [reference]" in annotations |
| Using `== Section ==` in activity diagrams | Use `floating note:` instead |
| Not referencing baseline | Add notes like "See baseline: [filename].puml" |
| Incomplete OpenAPI deltas | Show only changed endpoints, not entire spec |

---

## Final Step: Update Workflow State

After all delta diagrams validate, update `results/${FEATURE}/.workflow-state.md`:

1. **Phase 8.1**: Set to ✅ Complete with timestamp
2. **Last Activity**: "Completed Phase 8.1 control flow delta design"
3. **Next Action**: "Run /09-gap-analysis-workflow ${FEATURE}"
4. **Decisions Log**: Add delta design decisions (change scope, compatibility)

---

## Related Skills

- **vnrm-confluence-data-provider** - VNRM architecture documentation (use for control flow standards validation and platform interface patterns)
- **08-0-control-flow-design-workflow** - Phase 8 for NEW mode (greenfield control flow design)
- **07-1-microservice-delta-workflow** - Phase 7.1 microservice changes
- **plantuml-generator** - PlantUML syntax and validation
- **plantuml-syntax** - PlantUML reference
- **vnrm-prt-architecture** - PRT submodule patterns
- **vnrm-num-architecture** - NUM submodule patterns

---
