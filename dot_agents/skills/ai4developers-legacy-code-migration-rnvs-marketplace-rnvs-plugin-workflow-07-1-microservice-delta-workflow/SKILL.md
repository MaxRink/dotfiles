---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-workflow-07-1-microservice-delta-workflow
description: Design CHANGES to existing VNRM microservices using delta model approach (Phase 7.1). Computes delta between Phase 6 baseline and Phase 5 requirements, classifies changes, and generates delta model with API, database, event, and state machine changes. CHANGE mode only - for NEW mode use microservice-design-workflow.
context: fork
agent: general-purpose
allowed-tools: Read, Glob, Grep, Write, Task, AskUserQuestion
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/workflow/skills/07-1-microservice-delta-workflow by codex-knowledge-curation/scripts/persist_project_skills.py. -->

<required_reading>
Read `results/${FEATURE}/.workflow-state.md` before any operation.
This provides workflow mode, completed phases, and session context.
</required_reading>

<state_management>
**Phase 7.1 VERIFIES Mode=CHANGE.**
Phase 6 must have set Mode=CHANGE. If Mode is NEW or UNKNOWN, this is an error.
</state_management>

# Phase 7.1: Microservice Delta Design Workflow

**Purpose**: Design CHANGES to existing VNRM microservices using delta model approach. Computes what needs to change and produces targeted design specifications.

**When to use**: After Phase 5 (Control Flow Mapping) and Phase 6 (VNRM Baseline Analysis) are complete. This is for CHANGE mode (modifying existing microservices) - for NEW mode, use 07-0-microservice-design-workflow.

---

## Prerequisites

<prerequisites>
**Feature Identification** - check in order, stop at first match:

1. **User provided feature name** (e.g., "/07-1-microservice-delta-workflow NBM") → use directly
2. **Conversation context** → use feature from earlier in session
3. **Single feature in results/** → `Glob results/*/phase6/analysis.json` - if exactly one, use it
4. **Multiple features** → use AskUserQuestion to let user select
5. **No features with Phase 6** → "Complete Phase 6 first with /06-vnrm-analysis-workflow"

**Verify**: Both files exist:
- `results/${FEATURE}/phase5/control-flow-mapping.json` (requirements)
- `results/${FEATURE}/phase6/analysis.json` (VNRM baseline)

**Load Feature Context**:
- Read `results/${FEATURE}/feature-definition.json` for feature metadata
- Extract `feature_name`, `feature_description`, `scope`
</prerequisites>

---

## Step 0: Load Workflow State

Read `results/${FEATURE}/.workflow-state.md` and verify:

1. **Phase Check**: Phase 6 must be ✅ Complete
2. **Mode Check**: Must be `CHANGE` (set by Phase 6)
3. **Status**: Should be "In Progress"

If state file missing: "Run /00-feature-definition-workflow first to initialize workflow state."

**If Mode is not CHANGE**: ERROR - "Mode is ${MODE}, but Phase 7.1 requires CHANGE mode. Phase 6 must be completed first to set Mode=CHANGE."

**Update state**:
- Set Phase 7.1 to 🔄 In Progress
- Update Last Activity: "Designing microservice delta for CHANGE mode"

---

## Overview

Phase 7.1 Microservice Delta Design transforms requirements into targeted change specifications:

1. **Stage 1: Compute delta** - Compare Phase 6 baseline against Phase 5 requirements
2. **Stage 2: Classify changes** - Determine ADDITIVE, ENHANCEMENT, BREAKING, or REFACTORING
3. **Stage 3: Design delta model** - API, database, event, state machine, dependency changes
4. **Stage 4: Validate quality** - Apply 5-gate framework, iterate until COMPLETE status

---

## Key Principles

### 1. Delta Model Concept

**What is Delta Model?**
Delta model captures ONLY the changes needed to existing microservice, not complete service specifications.

> **Structure**: See [examples/skeleton-template.json](examples/skeleton-template.json) for complete delta model structure.

### 2. Change Type Classification

| Change Type | Complexity | Breaking | Quality Target | Focus |
|-------------|------------|----------|----------------|-------|
| **ADDITIVE** | < 10 elements | No | ≥80/100 | Completeness, clarity |
| **ENHANCEMENT** | 10-29 elements | No | ≥75/100 | Integration, synergies |
| **BREAKING** | Any | Yes | ≥70/100 | Migration planning (MANDATORY) |
| **REFACTORING** | ≥30 elements | No | ≥70/100 | Testing, external contracts unchanged |

### 3. Delta Model Categories

Build the delta model with these categories:

| Category | Content |
|----------|---------|
| **API** | `endpoints_to_add`, `endpoints_to_modify`, `endpoints_to_deprecate` |
| **Database** | `tables_to_add`, `columns_to_add`, `indexes_to_add` |
| **Events** | `topics_to_add`, `subscriptions_to_add` |
| **State Machine** | `new_states`, `new_transitions` |
| **Dependencies** | `new_internal_dependencies` |

> **Template**: Start with [examples/skeleton-template.json](examples/skeleton-template.json). See `examples/` for complete examples.

### 4. RNVS Source Attribution (MANDATORY)

Every change MUST have traceability to RNVS legacy code:

| Change Type | Required Fields | Example |
|-------------|-----------------|---------|
| **API Endpoints** | `maps_from.rnvs_component`, `rnvs_function`, `rnvs_file:line` | `PortierungsService.java:234` |
| **Database Tables** | `source.rnvs_table`, `rnvs_file:line`, `mapping_notes` | `rnvs_tables.sql:456` |
| **Events** | `source.rnvs_trigger`, `rnvs_file:line` | `portierung_created_trigger.sql:23` |

> **Examples**: See `examples/*.json` for complete source attribution examples.

---

## 4-Stage Workflow

**Output directory**: `results/${FEATURE}/phase7.1/`

### Stage 1: Compute Delta

Compare Phase 6 baseline (current VNRM state) against Phase 5 requirements (needed from RNVS).

**Output**: `computed-delta.json` with `api_changes`, `database_changes`, `event_changes` arrays.

### Stage 2: Classify Changes

**Before classification**: Use **vnrm-confluence-data-provider** to validate architecture compliance:
- Reference page ID 2069758700 for VNRM platform architecture standards
- Check if proposed changes align with VNRM submodule patterns and interface specifications
- Validate against VNRM architectural building blocks matrix

Determine change type (ADDITIVE/ENHANCEMENT/BREAKING/REFACTORING) and quality target.

**Output**: `classification.json` with `change_type`, `complexity_score`, `quality_target`.

### Stage 3: Design Delta Model

Design delta model using categories from [Delta Model Categories](#3-delta-model-categories).

**Output**: `microservice-changes-design.json` containing:
- Metadata (feature_name, target_service, baseline/requirements sources)
- Change classification (type, complexity, quality_target)
- Changes (api_changes, database_changes, event_changes, state_machine_changes, dependency_changes)
- RNVS source mapping for traceability

> **Template**: Start with [examples/skeleton-template.json](examples/skeleton-template.json).

### Stage 4: Validate Quality

Apply 5-gate validation framework, iterate until COMPLETE status.

**Output**: `changes-quality-report.json` with gate scores and recommendations.

---

## Required Elements by Category

| Category | Required Elements |
|----------|-------------------|
| **API Changes** | OpenAPI 3.0, ALL status codes (200-500), business_rules, maps_from |
| **Database Changes** | PostgreSQL DDL, PK, FKs, constraints, indexes, audit columns |
| **Event Changes** | Message Bus topic naming, Avro schema, partition_key, retention, source |
| **State Machine** | states[], transitions[] with guards/actions |
| **Dependencies** | service_name, resilience (circuit_breaker, timeout, retry, fallback) |

> **Examples**: See `examples/` for complete change examples (additive, breaking, enhancement, refactoring).

---

## 5-Gate Validation Framework

| Gate | Weight | Criteria |
|------|--------|----------|
| **Completeness** | 30% | All delta categories populated with meaningful data |
| **API Quality** | 30% | OpenAPI specs, business rules, source attribution |
| **Database Quality** | 20% | DDL syntax, constraints, purposes |
| **Integration Quality** | 10% | Event schemas, idempotency, resilience |
| **Schema Validation** | 10% | JSON structure compliance |

**Status Interpretation**:
| Status | Condition | Action |
|--------|-----------|--------|
| **COMPLETE** | score ≥ quality_target | Ready for Phase 8.1 |
| **PARTIAL** | score ≥ target - 15 | Minor improvements recommended |
| **INCOMPLETE** | score < target - 15 | Significant improvements needed |

---

## Breaking Change Requirements

**When classified as BREAKING**, additional `migration` section is MANDATORY:

| Field | Description |
|-------|-------------|
| `consumer_impact` | What clients need to change |
| `affected_clients` | List of affected consumers |
| `versioning_strategy` | How API versions will be managed |
| `timeline.deprecation_notice` | When deprecation is announced |
| `timeline.removal_date` | When old version is removed |
| `rollback_plan` | How to revert if needed |

**Breaking changes include**: Modifying API schemas, changing required/optional fields, removing endpoints, changing column types with data loss, removing Message Bus topics.

> **Example**: See [examples/breaking-change-example.json](examples/breaking-change-example.json) for complete migration guidance.

---

## Integration with Other Phases

**Input**: Phase 5 `control-flow-mapping.json` (requirements) + Phase 6 `analysis.json` (baseline).

### Output to Subsequent Phases

| Phase | Consumer | Usage |
|-------|----------|-------|
| Phase 8.1 | Control Flow Delta Design | Service orchestration changes |
| Phase 9 | Gap Analysis | Compare design vs requirements |
| Phase 10 | Story Generation | Change-based user stories |
| Phase 13.1 | Code Changes Generator | Apply changes to VNRM repo |

---

## Success Criteria

Phase 7.1 succeeds when:

- [ ] Delta model captures ONLY changes (not full service specs)
- [ ] All changes have RNVS source attribution
- [ ] All API endpoints have complete OpenAPI 3.0 specs with all status codes
- [ ] All database changes have executable PostgreSQL DDL
- [ ] All events have Avro schemas with standard fields
- [ ] All dependencies have resilience patterns
- [ ] Breaking changes include migration guidance
- [ ] Quality score meets change-type target
- [ ] changes-quality-report.json shows COMPLETE status

---

## Final Step: Update Workflow State

After quality validation passes, update `results/${FEATURE}/.workflow-state.md`:

1. **Phase 7.1**: Set to ✅ Complete with timestamp
2. **Last Activity**: "Completed Phase 7.1 microservice delta design"
3. **Next Action**: "Run /08-1-control-flow-delta-workflow ${FEATURE}"
4. **Decisions Log**: Add key delta decisions (change classification, breaking changes)

---

## Related Skills

- **vnrm-confluence-data-provider** - VNRM architecture documentation (use for architecture compliance validation and platform interface standards)
- **07-0-microservice-design-workflow** - Phase 7 for NEW mode (greenfield design)
- **08-1-control-flow-delta-workflow** - Phase 8.1 control flow changes
- **13-source-code-generation-workflow** - Phase 13.1 applies changes to code
- **plantuml-generator** - Generate diagrams from delta model
- **vnrm-prt-architecture** - PRT submodule patterns
- **vnrm-num-architecture** - NUM submodule patterns

---
