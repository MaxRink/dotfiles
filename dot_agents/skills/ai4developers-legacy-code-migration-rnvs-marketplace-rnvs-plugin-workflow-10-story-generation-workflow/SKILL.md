---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-workflow-10-story-generation-workflow
description: Generate production-ready Jira user stories from Phase 9 gap analysis. Converts functional gaps into user stories with acceptance criteria, test stories, and Jira-importable CSV. Supports both GREENFIELD and CHANGE modes with unified output format.
context: fork
agent: general-purpose
allowed-tools: Read, Glob, Grep, Write, Task, AskUserQuestion
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/workflow/skills/10-story-generation-workflow by codex-knowledge-curation/scripts/persist_project_skills.py. -->

<required_reading>
Read `results/${FEATURE}/.workflow-state.md` before any operation.
This provides workflow mode (NEW or CHANGE), completed phases, and session context.
Use Mode from state file instead of directory-based detection.
</required_reading>

# Phase 10: Story Generation Workflow

**Purpose**: Convert Phase 9 gap analysis outputs into production-ready Jira user stories, test stories, and structured metadata for development planning.

**When to use**: After Phase 9 (Gap Analysis) is complete. Output format is identical for both workflow modes - only input sources for design context differ.

---

## Prerequisites

<prerequisites>
**Feature Identification** - check in order, stop at first match:

1. **User provided feature name** (e.g., "/10-story-generation-workflow NBM") → use directly
2. **Conversation context** → use feature from earlier in session
3. **Single feature in results/** → `Glob results/*/phase9/gap_analysis.md` - if exactly one, use it
4. **Multiple features** → use AskUserQuestion to let user select
5. **No features with Phase 9** → "Complete Phase 9 first with /09-gap-analysis-workflow"

**Verify**: `results/${FEATURE}/phase9/gap_analysis.md` and `results/${FEATURE}/phase9/traceability_matrix.json` exist.

**Mode Detection**:
- `phase7/` exists → GREENFIELD mode (use Phase 7/8 design)
- `phase7.1/` exists → CHANGE mode (use Phase 6 + Phase 7.1/8.1)

**Load Feature Context**:
- Read `results/${FEATURE}/feature-definition.json` for feature metadata
- Read `results/${FEATURE}/phase9/gap_analysis.md` for gaps to convert
- Read `results/${FEATURE}/phase9/traceability_matrix.json` for mappings
</prerequisites>

---

## Overview

Phase 10 Story Generation converts gaps into actionable Jira stories:

1. **Load Phase 9 gaps** - Filter for story-worthy items (P1/P2 functional only)
2. **Load reference data** - Business rules, workflows, architecture from Phases 3-7
3. **Define Epic structure** - 3-5 epics based on microservices
4. **Generate implementation stories** - 8-12 stories from functional gaps
5. **Generate test stories** - 5-8 stories for critical workflows
6. **Format Jira CSV** - Properly escaped, importable CSV (NO story points, NO sprint)
7. **Generate metadata JSON** - Structured story data
8. **Create dependency graph** - PlantUML visualization
9. **Validate outputs** - All checks pass

> **Schema**: See `schemas/user-stories.schema.json` for JSON structure.

---

## Key Principles

### 1. Gap Filtering Rules (CRITICAL)

**INCLUDE** (Create user stories):

| Category | Priority | Include |
|----------|----------|---------|
| API Endpoint | P1, P2 | ✅ Yes |
| Integration | P1, P2 | ✅ Yes |
| Event/Async | P1, P2 | ✅ Yes |
| Database Schema | P1, P2 | ✅ Yes |
| Non-Functional | P1 only | ⚠️ Only if critical |

**EXCLUDE** (Do NOT create stories):

| Exclusion | Reason |
|-----------|--------|
| INFRA-* | Infrastructure setup |
| GAP-NFR-* with baseline/tuning | Non-functional |
| P3 (Low) | Defer to Phase 2+ |

**Target**: 8-12 focused stories, NOT 47 backlog items.

### 2. CSV Column Structure (MANDATORY)

```csv
Issue Type,Summary,Priority,Epic Link,Description,Labels,Affect Version,Acceptance Criteria,Business Scope,Depends On
```

**FORBIDDEN columns** (user requirement):
- Story Points
- Sprint
- Effort
- Assignee

### 3. Story Quality Requirements

| Requirement | Target |
|-------------|--------|
| Description length | >500 characters |
| Acceptance criteria | 10-13 items per story |
| Business rule references | ≥3 per story |
| API/DB specificity | Exact endpoints/tables |

### 4. Epic Structure Pattern

| Epic ID | Scope | Microservice |
|---------|-------|--------------|
| EPIC-FCPM | Core porting operations | prt-fcpm-* |
| EPIC-FCCM | Clearing & corrections | prt-fccm-* |
| EPIC-COMS | Carrier communication | spe-coms-* |
| EPIC-EVENT | Event-driven architecture | Cross-cutting |
| EPIC-TEST | Integration & E2E testing | Test automation |

### 5. Priority Mapping

| Phase 9 Priority | Jira Priority |
|------------------|---------------|
| P1 | Critical |
| P2 | High |

---

## 9-Stage Workflow

**Output directory**: `results/${FEATURE}/phase10/`

### Stage 1: Load Phase 9 Gap Analysis

Read and filter gaps:
- `phase9/gap_analysis.md` - Main gap report
- `phase9/traceability_matrix.json` - Structured mapping

Apply filtering rules (see Key Principles).

**Expected**: 8-12 high-priority functional gaps.

### Stage 2: Load Reference Data

**First, gather VNRM business context**: Use **vnrm-confluence-data-provider** to enhance story context:
- Reference page ID 2109544636 ("VNRM: Main Business Use cases") for official VNRM business use cases to ensure stories align with business scope
- Reference page ID 2109544290 ("VNRM: Business analysis") for business stakeholders, actors, and business process context
- Search for "VNRM business objects" to understand business entities and their relationships for more specific acceptance criteria

Read in parallel (mode-dependent):
- `phase3/ruletable.json` - Business rules
- `phase5/control-flow-mapping.json` - Workflows
- GREENFIELD: `phase7/microservice-design.json`
- CHANGE: `phase6/analysis.json` + `phase7.1/microservice-changes-design.json`

**Extract**: BR-IDs, WF-IDs, API endpoints, DB tables, Message Bus topics.

### Stage 3: Define Epic Structure

Create 3-5 epics based on:
- Microservices from Phase 7/7.1
- Functional domains from gaps
- Always include EPIC-TEST

### Stage 4: Generate Implementation Stories

Convert gaps to stories (one gap = one story):

**Story structure** (enhanced with VNRM business context):
- Story ID: `${FEATURE}-001`, `${FEATURE}-002`, etc.
- 10-13 acceptance criteria (enriched with VNRM business use case context)
- References to BR-XXX, WF-XXX, API endpoints
- Business value statement referencing VNRM business goals and stakeholder needs
- Dependencies (blocked_by, blocks)

**Quality enhancement**: Use VNRM business use cases and stakeholder context from Confluence to create more specific and business-aligned acceptance criteria.

**Output**: 8-12 implementation stories.

### Stage 5: Generate Test Stories

Create test stories for critical workflows:

| Category | Count | Scope |
|----------|-------|-------|
| E2E Workflow | 3-5 | Export, Import, Confirmation |
| Performance | 1-2 | Bulk API load |
| Resilience | 1-2 | Message Bus failure, circuit breaker |

**Story IDs**: `${FEATURE}-T001`, `${FEATURE}-T002`, etc.

### Stage 6: Format Jira CSV

Use **csv-jira-formatter** skill for proper escaping.

**Requirements**:
- UTF-8 encoding, NO BOM
- `\n` for line breaks in quoted fields
- Double quotes escaped as `""`
- Depends On column populated
- NO Story Points, NO Sprint columns

**Output**: `jira_stories.csv`

### Stage 7: Generate Metadata JSON

Create structured metadata with all story details.

**Output**: `user-stories.json` (see `schemas/user-stories.schema.json`)

### Stage 8: Create Dependency Graph

Visualize story dependencies using PlantUML.

**Rules**:
- Arrow: Story A --> Story B means "A blocks B"
- Avoid circular dependencies
- Max 2 levels deep

**Output**: `story-dependencies.puml`

### Stage 9: Validate and Finalize

**Validation checks**:
- [ ] All 5 required files exist
- [ ] CSV header matches expected columns
- [ ] NO Story Points column
- [ ] NO Sprint column
- [ ] Depends On column present
- [ ] Story count in range (8-15)
- [ ] No INFRA-* stories
- [ ] PlantUML valid (@startuml/@enduml)
- [ ] JSON parseable

**Output**: `PHASE10_SUMMARY.md`, `validation-report.txt`

---

## CHANGE Mode Specifics

When in CHANGE mode:

**Design Context**:
- Merge Phase 6 baseline + Phase 7.1 delta
- Reference Phase 7.1 changes (not Phase 7)

**Story Descriptions**:
- Include `change_type` (new endpoint, modified endpoint)
- Note baseline functionality that remains unchanged
- Distinguish "new requirement" vs "existing gap"

---

## Integration with Other Phases

### Input from Previous Phases

| Phase | File | Usage |
|-------|------|-------|
| Phase 3 | ruletable.json | Business rule references |
| Phase 5 | control-flow-mapping.json | Workflow references |
| Phase 7/7.1 | design JSON | API endpoint references |
| Phase 9 | gap_analysis.md | Gaps to convert |
| Phase 9 | traceability_matrix.json | Mappings |

### Output to Subsequent Phases

| Phase | Consumer | Usage |
|-------|----------|-------|
| Phase 11 | System Test | Test scenarios from stories |
| Phase 12 | Unit Tests | Test cases from acceptance criteria |
| Jira | Import | CSV for backlog creation |

---

## Success Criteria

Phase 10 succeeds when:

- [ ] Workflow mode correctly detected
- [ ] 8-12 implementation stories generated
- [ ] 5-8 test stories for critical workflows
- [ ] All stories have 10+ acceptance criteria
- [ ] CSV has NO Story Points, NO Sprint columns
- [ ] CSV has Depends On column populated
- [ ] All stories reference BR-XXX, WF-XXX, endpoints
- [ ] PlantUML dependency graph valid
- [ ] JSON metadata valid
- [ ] All validation checks pass

---

## Common Pitfalls and Fixes

| Pitfall | Fix |
|---------|-----|
| Too many stories (47+) | Apply filtering rules, target 8-12 |
| Story Points in CSV | Remove column, user requirement |
| Sprint column in CSV | Remove column, user requirement |
| Missing dependencies | Populate Depends On column |
| INFRA-* stories included | Exclude infrastructure gaps |
| Generic acceptance criteria | Make specific to API/DB/BR |

---

## Related Skills

- **vnrm-confluence-data-provider** - VNRM architecture documentation (use for business use cases, stakeholder context, and business value alignment)
- **csv-jira-formatter** - CSV escaping and Jira import
- **09-gap-analysis-workflow** - Phase 9 (input to Phase 10)
- **11-system-test-workflow** - Phase 11 (consumes stories)
- **german-glossary** - German telecommunications terminology

---
