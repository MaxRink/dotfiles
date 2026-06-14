---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-workflow-07-0-microservice-design-workflow
description: Transform Phase 5 control flow mappings into production-ready VNRM microservice specifications with complete API, database, event, and integration designs. This skill should be used for Phase 7 after Phase 5 completion. Creates microservice-design.json, PlantUML diagrams, and quality reports using 5-gate validation framework. NEW mode only - for CHANGE mode use 07-1-microservice-delta-workflow.
context: fork
agent: general-purpose
allowed-tools: Read, Glob, Grep, Write, Task, AskUserQuestion
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/workflow/skills/07-0-microservice-design-workflow by codex-knowledge-curation/scripts/persist_project_skills.py. -->

<required_reading>
Read `results/${FEATURE}/.workflow-state.md` before any operation.
This provides workflow mode, completed phases, and session context.
</required_reading>

<state_management>
**Phase 7 SETS Mode=NEW.**
This is the branching point - executing Phase 7 (not Phase 6) commits to NEW mode workflow.
</state_management>

# Phase 7: Microservice Design Workflow

**Purpose**: Design production-ready VNRM microservices from Phase 5 control flow mappings, generating complete API specifications, database schemas, event flows, and integration contracts.

**When to use**: After Phase 5 (Control Flow Visualization) is complete, with control-flow-mapping.json available. This is for NEW mode (greenfield microservice design) - for CHANGE mode, use 07-1-microservice-delta-workflow.

---

## Prerequisites

<prerequisites>
**Feature Identification** - check in order, stop at first match:

1. **User provided feature name** (e.g., "/07-0-microservice-design-workflow NBM") → use directly
2. **Conversation context** → use feature from earlier in session
3. **Single feature in results/** → `Glob results/*/phase5/control-flow-mapping.json` - if exactly one, use it
4. **Multiple features** → use AskUserQuestion to let user select
5. **No features with Phase 5** → "Complete Phase 5 first with /05-control-flow-visualization-workflow"

**Verify**: `results/${FEATURE}/phase5/control-flow-mapping.json` exists.

**Load Feature Context**:
- Read `results/${FEATURE}/feature-definition.json` for feature metadata
- Extract `feature_name`, `feature_description`, `scope`
</prerequisites>

---

## Step 0: Load Workflow State

Read `results/${FEATURE}/.workflow-state.md` and verify:

1. **Phase Check**: Phase 5 must be ✅ Complete
2. **Phase 6 Check**: Phase 6 must be ⬜ Pending (NOT completed - that would indicate CHANGE mode)
3. **Mode Check**: Must be UNKNOWN (not yet set)
4. **Status**: Should be "In Progress"

If state file missing: "Run /00-feature-definition-workflow first to initialize workflow state."

**If Phase 6 is ✅ Complete**: ERROR - "Phase 6 was completed, which set Mode=CHANGE. Use /07-1-microservice-delta-workflow instead."

**Update state immediately**:
- Set **Mode** to `NEW`
- Set Phase 7 to 🔄 In Progress
- Update Last Activity: "Starting NEW mode workflow - designing greenfield microservice"
- Add to Decisions Log: "Chose NEW mode - creating new microservice from scratch"

---

## Overview

Phase 7 Microservice Design transforms validated control flow mappings into production-ready microservice specifications:

1. **Stage 1: Load inputs** - Load Phase 5 control flow mappings (primary) + Phases 1-4 (context), classify feature type
2. **Stage 2: Design progressively** - Build skeleton JSON, add microservices in batches of 2-3 with API/database/events
3. **Stage 3: Validate** - Apply 5-gate framework, iterate until quality target met (≥85/90/95)
4. **Stage 4: Generate diagrams** - PlantUML for dependencies, event flows, state machines, database ERD
5. **Stage 5: Generate summary** - PHASE7_SUMMARY.md with specifications and next steps

**Without Phase 7**: Control flow mappings remain abstract without concrete implementation specifications, making development estimation and planning impossible.

**With Phase 7**: Complete microservice specifications enable accurate development planning, API contract publishing, database migration scripts, and event-driven architecture implementation.

---

## Key Principles

### 1. Source Priority Hierarchy

Phase 7 builds on validated Phase 5 control flow mappings:

**Priority 1: Phase 5 Results** (PRIMARY - Control Flow Mappings)
- `control-flow-mapping.json`: Component mappings, control flows, VNRM targets
- Used for: Microservice identification, API endpoint seeding, event discovery

**Priority 2: Phase 4 Results** (SECONDARY - Business Context)
- `business-documentation.json`: Business processes with stakeholder context
- Used for: Business rule mapping, service descriptions, domain context

**Priority 3: Phase 3 Results** (SUPPORTING - Business Rules)
- `ruletable.json`: Validated business rules with conditions
- Used for: API validation rules, error code mapping, state machine triggers

**Priority 4: Phase 1 Results** (CONTEXT - Legacy Complexity)
- `analysis.json`: Legacy components, database tables, dependencies
- Used for: Database migration strategy, legacy component mapping

### 2. VNRM Service Catalog Compliance

All microservices MUST use exact names from VNRM catalog or Phase 5:

**VNRM Standard Services** (18 services):

| Submodule | Service Name | Abbreviation | Description |
|-----------|--------------|--------------|-------------|
| **NUM** | num-fcm-fixednet-callnumber-management-api | FCNM | Callnumber lifecycle management |
| **NUM** | num-nbmi-number-block-inventory-management-api | NBIM | Block inventory management |
| **NUM** | num-nbom-numberblock-order-management-api | NBOM | BNetzA number block orders |
| **NUM** | num-cnrm-callnumber-resource-mngmt-api | CNRM | TMF639 resource management |
| **NUM** | num-cpin-callnumber-porting-info-backend | CPIN | Porting status information |
| **NUM** | num-caci-callnumber-contingent-info-api | CACI | Contingent information |
| **PRT** | prt-fcpm-fixed-callnumber-porting-management-api | FCPM | Individual porting management |
| **PRT** | prt-fbpm-fixed-block-porting-management-api | FBPM | Block porting management |
| **PRT** | prt-fccm-fixed-callnumber-clearing-management-api | FCCM | Error correction clearing |
| **COM** | com-tsp-telephony-service-provider-api | TSP | Operator/provider management |
| **COM** | com-rdm-reference-data-management-api | RDM | Reference data management |
| **COM** | com-cs-config-server-api | CS | Configuration server |
| **COM** | com-ecc-errorcode-catalog-api | ECC | Error code catalog |
| **SPE** | spe-coms-communication-server-api | COMS | SFTP file exchange |
| **SPE** | spe-beaa-backend-automation-adapter-api | BEAA | CRM-T integration adapter |
| **SPE** | spe-vnrm-rnvs-db-api | VNRM-DB | Legacy RNVS database sync |
| **COR** | cor-bem-business-error-management-api | BEM | Business error management |
| **NTW** | vnrm-container | VNRM | Network container management |

**NOT ALLOWED: Inventing Service Names**
- All service names MUST exist in VNRM catalog or Phase 5 control-flow-mapping.json
- Custom services from Phase 5 use CUSTOM submodule
- Do NOT invent new service names based on "logical assumptions"

### 3. Feature Type Classification

Classify feature based on Phase 5 microservices:

| Type | Criteria | Quality Target |
|------|----------|----------------|
| **STANDARD_VNRM** | All services in VNRM catalog | ≥95/100 |
| **HYBRID_CUSTOM** | Mix of catalog and custom | ≥90/100 |
| **FULLY_CUSTOM** | All custom services from Phase 5 | ≥85/100 |

---

## 5-Stage Design Workflow

### Stage 1: Load All Previous Phase Outputs

**Objective**: Load Phase 5 control flow mappings and supporting context from Phases 1-4.

**Actions** (load in parallel for efficiency):
1. Read `results/${FEATURE}/phase5/control-flow-mapping.json` (PRIMARY)
2. Read `results/${FEATURE}/phase4/business-documentation.json` (SECONDARY)
3. Read `results/${FEATURE}/phase3/ruletable.json` (SUPPORTING)
4. Read `results/${FEATURE}/phase1/analysis.json` (CONTEXT)

**What to Extract from Phase 4**:
- `business_processes[]` → Business context for service descriptions
- `enhanced_business_rules[]` → Business rules for API validations

**What to Extract from Phase 3**:
- `business_rules[]` → Map rule IDs to API error codes
- Conditional rules → State machine triggers

**What to Extract from Phase 1**:
- `components[]` → RNVS legacy complexity context
- `database_tables[]` → Inform VNRM database migration strategy

**Before Classification**: Use **vnrm-confluence-data-provider** skill to validate VNRM service catalog:
- Search for "VNRM architecture DHVOICE" to access the official VNRM service catalog
- Reference page ID 2069758700 for complete architecture building blocks matrix
- Validate that all Phase 5 microservices align with VNRM submodule structure (NUM, PRT, COM, SPE, COR, NTW)

**Classify Feature Type**: Based on Phase 5 microservices, determine type (see [Feature Type Classification](#3-feature-type-classification)) and set quality target.

---

### Stage 2: Design Microservices Progressively

**Objective**: Build microservice design incrementally to avoid token limits.

> **Schema Reference**: See [schemas/microservice-design.schema.json](schemas/microservice-design.schema.json) for complete structure.

#### Step 2.1: Write Skeleton JSON

Create `results/${FEATURE}/phase7/microservice-design.json` with skeleton structure from schema.

#### Step 2.2: Add Microservices in Batches of 2-3

**For each microservice batch**: Use **vnrm-confluence-data-provider** to get submodule-specific patterns:
- Search for relevant VNRM submodule architecture (e.g., "NUM VNRM architecture" for number management services)
- Reference architectural building blocks and interface patterns from Confluence documentation

For each microservice from Phase 5, design with these sections:

| Section | Required Fields | Source |
|---------|-----------------|--------|
| **Metadata** | `service_name`, `vnrm_submodule`, `service_level`, `description` (≥50 chars) | Phase 5 component_mappings + Confluence patterns |
| **database_design** | tables[], indexes, constraints, migration_from_rnvs | Phase 1 database_tables + VNRM patterns |
| **api_design** | endpoints[] with 400/404/409/500 responses, business_rules_enforced | Phase 5 api_endpoints + VNRM API patterns |
| **event_design** | message_topics[], event_subscriptions[] with idempotency | Phase 5 events_published + VNRM event patterns |
| **state_machine** | states[], transitions[] with guards/actions | Phase 3 conditional rules |
| **dependencies** | internal_services[] with circuit_breaker, external_services[] | Phase 5 service calls |
| **deployment_config** | scaling, health_checks, monitoring | Standard VNRM patterns |

#### Step 2.3: Add Service Dependencies Graph

After all microservices, add `service_dependencies` mapping each service to its `rest_dependencies[]` and `event_dependencies[]`.

#### Step 2.4: Add Event Catalog

Add `event_catalog` listing all Kafka topics with `publisher`, `subscribers[]`, `event_type`, `retention_days`.

---

### Stage 3: Validate and Iterate

**Objective**: Apply 5-gate validation framework and iterate until quality target met.

#### 5-Gate Validation Framework

| Gate | Weight | Criteria |
|------|--------|----------|
| **Gate 1: Completeness** | 30% | All Phase 5 services designed, required fields present |
| **Gate 2: API Quality** | 30% | Error responses (400, 404, 409, 500), business rules, RNVS mapping |
| **Gate 3: Database Quality** | 20% | Indexes, optimistic locking, constraints, migration strategy |
| **Gate 4: Integration Quality** | 10% | Circuit breakers, timeouts, retries, fallbacks for all deps |
| **Gate 5: Schema Validation** | 10% | Valid JSON, service names in catalog or Phase 5 |

**Iteration Loop**:
1. Run validation on current design
2. If score < target: Fix highest-impact issues first
3. Use Edit tool to update microservice-design.json
4. Re-validate
5. Repeat until COMPLETE (≥ target) or max 3 iterations

**Output**: Write `results/${FEATURE}/phase7/microservice-design-quality-report.json` with gate scores and issues.

---

### Stage 4: Generate PlantUML Diagrams

**Objective**: Create visual diagrams from the completed microservice design.

> **Syntax Reference**: See `plantuml-syntax` skill for diagram patterns and VNRM color schemes.

| Diagram | File | Content | Source |
|---------|------|---------|--------|
| **Dependencies** | `microservice-dependencies.puml` | Component diagram with submodule colors | `service_dependencies` |
| **Event Flow** | `event-flow-{topic}.puml` | Sequence diagram per Message Bus topic | `event_catalog` |
| **State Machine** | `state-machine-{service}.puml` | State diagram per service | `state_machine` sections |
| **Database ERD** | `database-erd.puml` | Entity-relationship diagram | `database_design` sections |

**VNRM Submodule Colors**:
- NUM: `#3498DB`, PRT: `#E74C3C`, COM: `#2ECC71`, SPE: `#9B59B6`, COR: `#F39C12`, NTW: `#1ABC9C`, CUSTOM: `#95A5A6`

---

### Stage 5: Generate Summary

**Objective**: Create human-readable summary document.

**Output**: Create `results/${FEATURE}/phase7/PHASE7_SUMMARY.md` with:
- Executive Summary (feature type, quality score, microservice count)
- Microservice Specifications (per-service: submodule, endpoints, tables, topics)
- Diagram Inventory (list of generated .puml files)
- Validation Results (5-gate scores)
- Next Steps (Phase 8 reference)

---

## Pattern References

Spring Boot patterns available in `patterns/` directory:

| Pattern File | Content |
|--------------|---------|
| `domain-model.md` | JPA entities, enums, value objects, relationship mappings |
| `repository-layer.md` | Spring Data JPA, specifications, projections |
| `service-layer.md` | @Transactional, validators, event publishing, circuit breakers |
| `controller-layer.md` | REST controllers, DTOs, OpenAPI, error handling |
| `database-design.md` | PostgreSQL DDL, Flyway migrations, indexes, ETL strategies |

---

## Schema Reference

> **Full Schema**: See [schemas/microservice-design.schema.json](schemas/microservice-design.schema.json) for complete validation.

---

## Common Pitfalls and Fixes

| Pitfall | Fix |
|---------|-----|
| Inventing service names | Use exact names from VNRM catalog or Phase 5 |
| Missing error responses | Add 400, 404, 409, 500 for each endpoint |
| Missing database indexes | Add indexes for FKs and query columns |
| Missing circuit breakers | Add Resilience4j config for each dependency |
| No idempotency for events | Document idempotency_key and deduplication |
| Short descriptions | Expand to ≥50 chars with specific details |
| Writing entire file at once | Use progressive building (skeleton → batches) |
| Missing optimistic locking | Add version column to all entities |
| No migration strategy | Document ETL approach from RNVS tables |

---

## Integration with Other Phases

**Input**: See [Source Priority Hierarchy](#1-source-priority-hierarchy) for input files.

### Output to Subsequent Phases

| Phase | Consumer | Usage |
|-------|----------|-------|
| Phase 8 | Control Flow Design | Service orchestration sequences |
| Phase 9 | Gap Analysis | Compare design vs requirements |
| Phase 10 | Story Generation | API-based user stories |
| Phase 12 | Unit Test Generation | API contracts for test cases |
| Phase 13 | Code Generation | Implementation templates |

---

## Success Criteria

Phase 7 succeeds when:

- [ ] All Phase 5 microservices are designed
- [ ] Each microservice has complete database, API, event, state machine sections
- [ ] Service names match VNRM catalog or Phase 5 definitions
- [ ] All API endpoints have error responses (400, 404, 409, 500)
- [ ] All database tables have indexes and optimistic locking
- [ ] All service dependencies have circuit breaker configs
- [ ] All Message Bus subscriptions have idempotency strategy
- [ ] Descriptions are ≥50 characters with specific details
- [ ] Quality score meets feature type target (≥85/90/95)
- [ ] PlantUML diagrams generated for all aspects
- [ ] PHASE7_SUMMARY.md is comprehensive
- [ ] microservice-design-quality-report.json shows COMPLETE status

---

## Final Step: Update Workflow State

After quality validation passes, update `results/${FEATURE}/.workflow-state.md`:

1. **Mode**: Confirm `NEW` (should already be set in Step 0)
2. **Phase 7**: Set to ✅ Complete with timestamp
3. **Last Activity**: "Completed Phase 7 microservice design"
4. **Next Action**: "Run /08-0-control-flow-design-workflow ${FEATURE}"
5. **Decisions Log**: Add key design decisions (service names, database strategy, event patterns)

---

## Related Skills

- **07-1-microservice-delta-workflow** - Phase 7.1 for CHANGE mode (modifying existing services)
- **08-0-control-flow-design-workflow** - Phase 8 control flow design
- **plantuml-generator** - PlantUML syntax and validation
- **vnrm-num-architecture** - NUM submodule patterns
- **vnrm-prt-architecture** - PRT submodule patterns
- **vnrm-com-architecture** - COM submodule patterns

---
