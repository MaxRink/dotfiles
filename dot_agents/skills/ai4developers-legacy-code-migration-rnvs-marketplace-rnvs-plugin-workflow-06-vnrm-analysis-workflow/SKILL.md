---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-workflow-06-vnrm-analysis-workflow
description: Analyze existing VNRM microservice to establish baseline for CHANGE mode workflow. Captures repository path, API contracts, database schemas, test infrastructure, and operational patterns. Required before Phase 7.1 (design changes). CHANGE mode only - for NEW mode, skip to Phase 7.
context: fork
agent: general-purpose
allowed-tools: Skill, Read, Glob, Grep, Write
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/workflow/skills/06-vnrm-analysis-workflow by codex-knowledge-curation/scripts/persist_project_skills.py. -->

<required_reading>
Read `results/${FEATURE}/.workflow-state.md` before any operation.
This provides workflow mode, completed phases, and session context.
</required_reading>

<state_management>
**Phase 6 SETS Mode=CHANGE.**
This is the branching point - executing Phase 6 commits to CHANGE mode workflow.
</state_management>

# Phase 6: VNRM Code Analysis Workflow

**Purpose**: Analyze existing VNRM microservice to establish baseline before making changes.

**When to use**: After Phase 5 (Control Flow Mapping) when modifying an EXISTING VNRM microservice (CHANGE mode). Skip this phase for NEW mode (greenfield design) and proceed directly to Phase 7.

---

## Overview

Phase 6 VNRM Code Analysis establishes the baseline for CHANGE workflow:

1. **Identify repository** - Capture absolute path to VNRM microservice
2. **Analyze architecture** - Extract service metadata, technology stack, patterns
3. **Document APIs** - Map all REST endpoints with contracts
4. **Document database** - Extract schemas, tables, relationships
5. **Document integrations** - Identify service dependencies and events
6. **Document tests** - Map existing test infrastructure for REUSE classification
7. **Generate structured output** - Create analysis.json following vnrm-code-analysis-schema

**Without Phase 6**: Phase 7.1 cannot compute delta - it needs current state to compare against Phase 5 requirements.

**With Phase 6**: Delta computation in Phase 7.1 becomes possible, enabling targeted microservice modifications.

> **Schema Reference**: All JSON structures must conform to `vnrm-code-analysis-schema`.
> See `foundation/skills/vnrm-code-analysis-schema/references/` for schema, examples, and field guide.

---

## Workflow Steps

### Step 0: Load Workflow State

Read `results/${FEATURE}/.workflow-state.md` and verify:

1. **Phase Check**: Phase 5 must be ✅ Complete
2. **Mode Check**: Must be UNKNOWN (not yet set)
3. **Status**: Should be "In Progress"

If state file missing: "Run /00-feature-definition-workflow first to initialize workflow state."

**Update state immediately**:
- Set **Mode** to `CHANGE`
- Set Phase 6 to 🔄 In Progress
- Update Last Activity: "Starting CHANGE mode workflow - analyzing existing VNRM microservice"
- Add to Decisions Log: "Chose CHANGE mode - modifying existing microservice"

---

### Step 1: Setup

```bash
mkdir -p results/${FEATURE}/phase6
```

### Step 2: Analyze Repository

Explore the VNRM microservice. **Record the absolute repository path first.**

**Before analyzing**: Use **vnrm-confluence-data-provider** skill to gather VNRM architecture context:
- Search for "VNRM architecture DHVOICE" to get architectural overview
- Look up specific submodule patterns (NUM, PRT, COM, SPE, COR, NTW) relevant to the microservice
- Reference page ID 2069758700 ("VNRM: architecture") for platform architecture and component diagrams

| What to Extract | Sources |
|-----------------|---------|
| **Metadata** | `pom.xml`, `application.yml`, `README.md` |
| **API Contracts** | `*Controller.java`, OpenAPI annotations, DTOs |
| **Database Schema** | `@Entity` classes, `V*.sql` migrations |
| **Dependencies** | RestTemplate/WebClient calls, Message Bus topics |
| **Test Infrastructure** | `*Test.java`, `*IT.java`, test frameworks |

### Step 3: Generate analysis.json

1. Use `vnrm-code-analysis-schema` skill for structure (`references/vnrm-example.json`)
2. Populate all fields from exploration findings
3. Write to: `results/${FEATURE}/phase6/analysis.json`

**Required fields**: `repository_path`, `source_structure`, `service_name`, `vnrm_submodule`, `api_contracts[]`, `database_schema`, `test_infrastructure`

### Step 4: Validate

```bash
python3 foundation/skills/vnrm-code-analysis-schema/scripts/validate_analysis.py results/${FEATURE}/phase6/analysis.json
```

---

## Expected Outputs

**Directory**: `results/${FEATURE}/phase6/`

1. **analysis.json** - VNRM microservice analysis
   - `repository_path` - Absolute path to repository (CRITICAL)
   - `source_structure` - Source directory structure
   - `service_metadata` - Service identification
   - `technology_stack` - Technologies used
   - `api_contracts` - All REST endpoints
   - `database_schema` - All tables and schemas
   - `dependencies` - Service dependencies
   - `test_infrastructure` - Test framework and inventory

**Next Phase**: `/rnvs-workflow:phase7.1-design-changes-in-microservice`

---

## Integration with Other Phases

### Input from Previous Phases

| Phase | File | Usage |
|-------|------|-------|
| Phase 5 | control-flow-mapping.json | Requirements to compare against baseline |

### Output to Subsequent Phases

| Phase | Consumer | Usage |
|-------|----------|-------|
| Phase 7.1 | Microservice Delta Design | Baseline for delta computation |
| Phase 8.1 | Control Flow Delta Design | Baseline control flows |
| Phase 9 | Gap Analysis | Effective VNRM state |
| Phase 12 | Unit Test Generation | REUSE/MODIFY/NEW classification |
| Phase 13.1 | Code Changes | `repository_path` for direct code application |

---

## Success Criteria

Phase 6 succeeds when:

- [ ] `repository_path` is captured (absolute path)
- [ ] `source_structure` documents main/test source roots
- [ ] All REST endpoints are documented with contracts
- [ ] All database tables are documented with schemas
- [ ] All service dependencies are documented
- [ ] All Message Bus topics are documented
- [ ] Test infrastructure is analyzed
- [ ] Test inventory maps tests to production classes
- [ ] analysis.json validates against vnrm-code-analysis-schema
- [ ] Workflow context is updated to CHANGE mode

---

## Final Step: Update Workflow State

After analysis.json validates successfully, update `results/${FEATURE}/.workflow-state.md`:

1. **Mode**: Confirm `CHANGE` (should already be set in Step 0)
2. **Phase 6**: Set to ✅ Complete with timestamp
3. **Last Activity**: "Completed Phase 6 VNRM analysis - baseline established"
4. **Next Action**: "Run /07-1-microservice-delta-workflow ${FEATURE}"
5. **Decisions Log**: Add repository path and key analysis findings

---

## Related Skills

- **vnrm-confluence-data-provider** - VNRM architecture documentation (use for component specifications, architectural patterns, and platform interfaces)
- **vnrm-code-analysis-schema** - JSON schema for structured output
- **vnrm-num-architecture** - NUM submodule patterns
- **vnrm-prt-architecture** - PRT submodule patterns
- **07-1-microservice-delta-workflow** - Phase 7.1 (next phase)
- **german-glossary** - German terminology translation

---
