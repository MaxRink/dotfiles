---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-workflow-08-0-control-flow-design-workflow
description: Design VNRM control flows and service orchestration from Phase 7 microservice specifications. Use for Phase 8 (NEW mode only) after Phase 7. Creates sequence, activity, saga, and event flow diagrams with OpenAPI specifications. Generates control flow documentation and quality reports.
context: fork
agent: general-purpose
allowed-tools: Read, Glob, Grep, Write, Task, AskUserQuestion
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/workflow/skills/08-0-control-flow-design-workflow by codex-knowledge-curation/scripts/persist_project_skills.py. -->

<required_reading>
Read `results/${FEATURE}/.workflow-state.md` before any operation.
This provides workflow mode, completed phases, and session context.
</required_reading>

<state_management>
**Phase 8 VERIFIES Mode=NEW.**
Phase 7 must have set Mode=NEW. If Mode is CHANGE, use /08-1-control-flow-delta-workflow instead.
</state_management>

# Phase 8: Control Flow Design Workflow

**Purpose**: Design production-ready VNRM control flows showing service orchestration, API interactions, event flows, and saga patterns from Phase 7 microservice specifications.

**When to use**: After Phase 7 (Microservice Design) is complete, with microservice-design.json available. This is for NEW mode (greenfield control flow design) - for CHANGE mode, use 08-1-control-flow-delta-workflow.

---

## Prerequisites

<prerequisites>
**Feature Identification** - check in order, stop at first match:

1. **User provided feature name** (e.g., "/08-0-control-flow-design-workflow NBM") → use directly
2. **Conversation context** → use feature from earlier in session
3. **Single feature in results/** → `Glob results/*/phase7/microservice-design.json` - if exactly one, use it
4. **Multiple features** → use AskUserQuestion to let user select
5. **No features with Phase 7** → "Complete Phase 7 first with /07-0-microservice-design-workflow"

**Verify**: `results/${FEATURE}/phase7/microservice-design.json` exists.

**Load Feature Context**:
- Read `results/${FEATURE}/feature-definition.json` for feature metadata
- Extract `feature_name`, `feature_description`, `scope`
</prerequisites>

---

## Step 0: Load Workflow State

Read `results/${FEATURE}/.workflow-state.md` and verify:

1. **Phase Check**: Phase 7 must be ✅ Complete
2. **Mode Check**: Must be `NEW` (set by Phase 7)
3. **Status**: Should be "In Progress"

If state file missing: "Run /00-feature-definition-workflow first to initialize workflow state."

**If Mode is not NEW**: ERROR - "Mode is ${MODE}, but Phase 8 requires NEW mode. Use /08-1-control-flow-delta-workflow for CHANGE mode."

**Update state**:
- Set Phase 8 to 🔄 In Progress
- Update Last Activity: "Designing control flows for NEW mode"

---

## Overview

Phase 8 Control Flow Design transforms microservice specifications into detailed orchestration flows:

1. **Load Phase 7 results** - Use microservice design as primary input, with Phase 5 and Phase 3 as supporting context
2. **Classify flow complexity** - Determine SIMPLE, MODERATE, or COMPLEX based on service count and interactions
3. **Design sequence diagrams** - Service-to-service interactions for key use cases
4. **Design activity diagrams** - Business process flows with decision points
5. **Design saga diagrams** - Distributed transactions with compensation
6. **Design event flow architecture** - Message Bus topics, publishers, and subscribers
7. **Generate OpenAPI specifications** - Complete API contracts for each microservice
8. **Validate and document** - PlantUML syntax validation and PHASE8_SUMMARY.md

> **OpenAPI Template**: See [patterns/openapi-template.yaml](patterns/openapi-template.yaml) for VNRM conventions.

---

## Key Principles

### 1. Source Priority Hierarchy

| Priority | Source | Usage |
|----------|--------|-------|
| **PRIMARY** | Phase 7 `microservice-design.json` | Service APIs, events, state machines, dependencies |
| **SECONDARY** | Phase 5 `control-flow-mapping.json` | Business process flow, interaction patterns |
| **SUPPORTING** | Phase 3 `ruletable.json` | Decision points, validation gates, error paths |
| **CONTEXT** | Phase 2 `flow-*.puml` | Legacy flow patterns for reference |

### 2. VNRM Color Scheme (MANDATORY)

All diagrams MUST use standard VNRM colors:

| Submodule | Color | Hex | Usage |
|-----------|-------|-----|-------|
| **NUM** | Light Orange | #FFAB91 | Number management services |
| **PRT** | Light Blue | #90CAF9 | Porting services |
| **COM** | Light Gray | #CFD8DC | Common services |
| **SPE** | Light Yellow | #FFF59D | Special function services |
| **COR** | Light Red | #FFCDD2 | Correction services |
| **NTW** | Light Green | #C8E6C9 | Network services |

### 3. Flow Complexity Classification

| Type | Criteria | Diagram Target |
|------|----------|----------------|
| **SIMPLE** | 2-3 services, <5 interactions | 1-2 sequence, 1 activity |
| **MODERATE** | 4-6 services, 5-15 interactions | 2-4 sequence, 1-2 activity, 1 saga |
| **COMPLEX** | 7+ services, 15+ interactions | 4-8 sequence, 2-3 activity, 2-3 saga, 1 event arch |

### 4. PlantUML Syntax Rules (CRITICAL)

**Activity Diagram Syntax:**
- ❌ **PROHIBITED**: `== Section Name ==` (sequence diagram syntax only!)
- ✅ **VALID**: `floating note: **Section Name**`
- ✅ **VALID**: `partition "Section Name" { }`
- ✅ **VALID**: `|Swimlane Name|`

**Sequence Diagram Syntax:**
- Use `== Section ==` for logical separators
- Use `->` for synchronous requests, `->>` for async (Message Bus), `-->` for responses
- Use `activate`/`deactivate` for lifelines
- Use `alt`/`else` for conditional flows

> **Note**: Use `floating note:` for sections in activity diagrams - never `== Section ==`.

---

## 8-Stage Workflow

**Output directory**: `results/${FEATURE}/phase8/`

### Stage 1: Load Previous Phase Outputs

**First, gather VNRM control flow patterns**: Use **vnrm-confluence-data-provider** skill:
- Search for "VNRM architecture control flow" and "VNRM platform interfaces"
- Reference page ID 3510539585 ("VNRM_arc_plattforminterfaces") for interface specifications
- Get sequence and activity diagram patterns from VNRM documentation

Read in parallel:
- `results/${FEATURE}/phase7/microservice-design.json` (PRIMARY)
- `results/${FEATURE}/phase5/control-flow-mapping.json` (SECONDARY)
- `results/${FEATURE}/phase3/ruletable.json` (SUPPORTING)
- `results/${FEATURE}/phase2/flow-*.puml` (CONTEXT)

**Extract from Phase 7**: `microservices[]`, `api_design.endpoints[]`, `event_design.message_bus_topics[]`, `dependencies`

### Stage 2: Classify Flow Complexity

Count microservices and interactions from Phase 7 to determine complexity level and diagram targets.

**Output**: Complexity classification (SIMPLE/MODERATE/COMPLEX) with diagram count targets.

### Stage 3: Design Sequence Diagrams

Design 2-3 sequence diagrams at a time showing service-to-service interactions.

**Key elements**:
- All participants match Phase 7 service names
- VNRM colors applied
- Error paths with `alt`/`else`
- Transaction boundaries
- Event publishing with `->>` syntax

**Output**: `sequence-*.puml` files (1-8 based on complexity)

### Stage 4: Design Activity Diagrams

Design 1-2 activity diagrams at a time for business processes from Phase 5.

**Key elements**:
- Use `floating note:` for sections, NOT `== Section ==`
- Business rule checks with rule IDs from Phase 3
- Transaction boundaries with BEGIN/COMMIT/ROLLBACK
- Parallel processing with `fork`/`end fork`
- Error paths ending with `stop`

> **Critical**: Use `floating note:` or `partition {}` for sections - never `== Section ==`.

**Output**: `activity-*.puml` files (1-3 based on complexity)

### Stage 5: Design Saga Diagrams

Design saga diagrams for distributed transactions across multiple services.

**Key elements**:
- Each saga step as a section with `== Step N ==`
- Compensation logic for each step
- State transitions clearly shown
- Final event publishing

**When to use**: When Phase 7 shows services with compensating transactions or distributed workflows.

**Output**: `saga-*.puml` files (0-3 based on complexity)

### Stage 6: Design Event Flow Architecture

Design event architecture showing Message Bus topics, publishers, and subscribers.

**Key elements**:
- Use `queue` for Message Bus topics
- Use `->>` for publish, `<<-` for consume
- Consumer group names
- Idempotency strategy documentation
- Partitions and retention settings

**Output**: `event-architecture.puml`

### Stage 7: Generate OpenAPI Specifications

Generate complete OpenAPI 3.0 specifications for each microservice from Phase 7 API designs.

**Required elements**:
- All endpoints from Phase 7
- Complete error responses (400, 401, 403, 404, 409, 500)
- Request/response schemas
- Security schemes (OAuth2)
- Correlation and idempotency headers

> **Template**: Start with [patterns/openapi-template.yaml](patterns/openapi-template.yaml).

**Output**: `openapi-*.yaml` files (1 per microservice)

### Stage 8: Validate and Document

1. **Validate PlantUML syntax**:
   - No `== Section ==` in activity diagrams
   - VNRM colors used correctly
   - All branches properly closed

2. **Generate documentation**:
   - `PHASE8_SUMMARY.md` with executive summary, diagram inventory, next steps

**Output**: `PHASE8_SUMMARY.md`

---

## Integration with Other Phases

### Input from Previous Phases

| Phase | File | Usage |
|-------|------|-------|
| Phase 7 | microservice-design.json | Primary: service APIs, events, dependencies |
| Phase 5 | control-flow-mapping.json | Secondary: business process flows |
| Phase 3 | ruletable.json | Supporting: decision points |
| Phase 2 | flow-*.puml | Context: legacy flow patterns |

### Output to Subsequent Phases

| Phase | Consumer | Usage |
|-------|----------|-------|
| Phase 9 | Gap Analysis | Validate flow completeness vs requirements |
| Phase 10 | Story Generation | API-based user stories with acceptance criteria |
| Phase 12 | Unit Tests | Test cases from control flow paths |
| Phase 14 | Test Scripts | Postman collections from OpenAPI specs |

---

## Success Criteria

Phase 8 succeeds when:

- [ ] All key use cases from Phase 7 have sequence diagrams
- [ ] All business processes from Phase 5 have activity diagrams
- [ ] Distributed transactions have saga diagrams with compensation
- [ ] Event flow architecture shows all Message Bus topics and consumers
- [ ] All microservices have OpenAPI specifications
- [ ] All PlantUML diagrams validate without syntax errors
- [ ] VNRM color scheme used consistently
- [ ] Activity diagrams use correct syntax (no `== Section ==`)
- [ ] All service names match Phase 7 exactly
- [ ] All event topics match Phase 7 event catalog
- [ ] Error paths included in all flows
- [ ] PHASE8_SUMMARY.md is comprehensive

---

## Final Step: Update Workflow State

After all diagrams validate, update `results/${FEATURE}/.workflow-state.md`:

1. **Phase 8**: Set to ✅ Complete with timestamp
2. **Last Activity**: "Completed Phase 8 control flow design"
3. **Next Action**: "Run /09-gap-analysis-workflow ${FEATURE}"
4. **Decisions Log**: Add flow design decisions (saga patterns, error handling)

---

## Related Skills

- **vnrm-confluence-data-provider** - VNRM architecture documentation (use for control flow patterns, platform interfaces, and interaction specifications)
- **08-1-control-flow-delta-workflow** - Phase 8.1 for CHANGE mode
- **07-0-microservice-design-workflow** - Phase 7 microservice design
- **plantuml-generator** - PlantUML generation and validation
- **plantuml-syntax** - PlantUML reference
- **vnrm-prt-architecture** - PRT submodule patterns
- **vnrm-num-architecture** - NUM submodule patterns

---
