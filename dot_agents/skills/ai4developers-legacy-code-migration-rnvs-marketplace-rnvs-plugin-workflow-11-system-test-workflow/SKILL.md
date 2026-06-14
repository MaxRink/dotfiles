---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-workflow-11-system-test-workflow
description: Expand Phase 10 test stories into detailed, execution-ready test scenarios (100-120 scenarios). Covers E2E, integration, performance, security, and missing workflow tests. Supports both GREENFIELD and CHANGE modes with unified output format.
context: fork
agent: general-purpose
allowed-tools: Read, Glob, Grep, Write, Task, AskUserQuestion
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/workflow/skills/11-system-test-workflow by codex-knowledge-curation/scripts/persist_project_skills.py. -->

<required_reading>
Read `results/${FEATURE}/.workflow-state.md` before any operation.
This provides workflow mode (NEW or CHANGE), completed phases, and session context.
Use Mode from state file instead of directory-based detection.
</required_reading>

# Phase 11: System Test Workflow

**Purpose**: Expand Phase 10 test stories into detailed, execution-ready test scenarios covering E2E, integration, performance, security, and missing workflow tests.

**When to use**: After Phase 10 (Story Generation) is complete. Output format is identical for both workflow modes.

---

## Prerequisites

<prerequisites>
**Feature Identification** - check in order, stop at first match:

1. **User provided feature name** (e.g., "/11-system-test-workflow NBM") → use directly
2. **Conversation context** → use feature from earlier in session
3. **Single feature in results/** → `Glob results/*/phase10/user-stories.json` - if exactly one, use it
4. **Multiple features** → use AskUserQuestion to let user select
5. **No features with Phase 10** → "Complete Phase 10 first with /10-story-generation-workflow"

**Verify**: `results/${FEATURE}/phase10/user-stories.json` exists.

**Mode Detection**:
- `phase7/` exists → GREENFIELD mode
- `phase7.1/` exists → CHANGE mode (load existing test inventory from Phase 6)

**Load Feature Context**:
- Read `results/${FEATURE}/feature-definition.json` for feature metadata
- Read `results/${FEATURE}/phase10/user-stories.json` - filter for `story_type: "Test"`
- Read `results/${FEATURE}/phase3/ruletable.json` for business rules
- Read `results/${FEATURE}/phase5/control-flow-mapping.json` for workflows
</prerequisites>

---

## Overview

Phase 11 System Test expands test stories into comprehensive scenarios:

1. **Load Phase 10 test stories** - Filter for Test type
2. **Load existing tests (CHANGE mode)** - For scenario classification
3. **Analyze coverage gaps** - Calculate expansion targets
4. **Expand E2E scenarios** - 40-50 scenarios from test stories
5. **Create integration scenarios** - 25-35 scenarios
6. **Create performance scenarios** - 10-15 scenarios
7. **Create security scenarios** - 15-20 scenarios
8. **Add missing workflow scenarios** - 15-20 scenarios
9. **Validate outputs** - All checks pass

> **Schema**: See `schemas/test-scenarios.schema.json` for JSON structure.
> **Template**: See `templates/test-matrix-template.csv` for CSV format.

---

## Key Principles

### 1. Expansion Strategy (CRITICAL)

| Phase 10 Story | Type | Target Scenarios |
|----------------|------|------------------|
| FNPORT-T001 | E2E: Export | 10-12 |
| FNPORT-T002 | E2E: Import | 10-12 |
| FNPORT-T003 | E2E: Confirmation | 8-10 |
| FNPORT-T004 | E2E: AWK | 8-10 |
| FNPORT-T005 | Performance | 10-15 |
| FNPORT-T006 | Chaos/Resilience | 5-10 |
| NEW | Missing Workflows | 15-20 |
| NEW | Security | 15-20 |

**Target**: 100-120 scenarios (15-20x expansion from 6 test stories)

### 2. Scenario Classification (CHANGE Mode)

| Classification | When | Action |
|----------------|------|--------|
| **REUSE** | Existing test covers unchanged functionality | Reference existing test |
| **MODIFY** | Existing test needs update for Phase 7.1 changes | Generate modification instructions |
| **NEW** | No existing test coverage | Generate full scenario |

**CHANGE Mode Targets**:
- REUSE: 30-50 scenarios
- MODIFY: 20-30 scenarios
- NEW: 30-40 scenarios

### 3. Scenario Quality Requirements

| Requirement | Target |
|-------------|--------|
| Test steps per scenario | 5+ |
| Test data | Exact JSON payloads |
| Expected results | HTTP status, response, DB changes, event bus messages |
| Business rule traceability | Link to BR-XXX |

### 4. CSV Column Structure

```csv
Test_ID,Scenario_Name,Test_Type,Priority,Parent_Story,Services_Involved,Automation,Status,Business_Rules,Depends_On,Classification
```

**Classification column**: REUSE/MODIFY/NEW (CHANGE mode only, empty for NEW mode)

**Forbidden columns**: Sprint, Owner, Story Points

### 5. Test Category Targets

| Category | Scenarios | Coverage |
|----------|-----------|----------|
| **E2E** | 40-50 | WF-001 to WF-005 |
| **Integration** | 25-35 | Service-to-service, DB, Event Bus |
| **Performance** | 10-15 | Load, stress, spike, endurance |
| **Security** | 15-20 | OWASP Top 10, auth, authz |
| **Missing Workflows** | 15-20 | WF-003, WF-006, WF-007, WF-008 |

---

## 9-Stage Workflow

**Output directory**: `results/${FEATURE}/phase11/`

### Stage 1: Load Phase 10 Test Stories

Read and filter:
- `phase10/user-stories.json` - Filter `story_type: "Test"`
- `phase10/jira_stories.csv` - Test story details
- `phase3/ruletable.json` - Business rules
- `phase5/control-flow-mapping.json` - Workflows

**Expected**: 6 Phase 10 test stories loaded.

### Stage 2: Load Existing Tests (CHANGE Mode Only)

If CHANGE mode, load Phase 6 test inventory:
- `phase6/analysis.json` → `.test_infrastructure.test_inventory`

Build coverage map:
- Test classes → WF-XXX mapping
- Test classes → BR-XXX mapping

### Stage 3: Expand E2E Test Scenarios

Expand 4 E2E test stories into 40-50 scenarios.

**Per test story**:
- Happy Path: 3 scenarios
- Alternative Paths: 3 scenarios
- Error Paths: 4 scenarios
- Edge Cases: 2 scenarios

**CHANGE mode**: Classify each as REUSE/MODIFY/NEW.

### Stage 4: Create Integration Scenarios

Create 25-35 integration scenarios:

| Category | Scenarios |
|----------|-----------|
| Service-to-service | 10-15 |
| Database integration | 8-10 |
| External systems | 5-7 |
| Event bus (Horizon) | 5-8 |

### Stage 5: Create Performance Scenarios

Expand performance test story into 10-15 scenarios:

| Type | Scenarios |
|------|-----------|
| Load tests | 4-5 |
| Stress tests | 2-3 |
| Spike tests | 2-3 |
| Endurance tests | 2-3 |

### Stage 6: Create Security Scenarios

Create 15-20 security scenarios:

| Category | Scenarios | Coverage |
|----------|-----------|----------|
| Authentication | 3-4 | JWT, OAuth |
| Authorization | 4-5 | RBAC, privilege escalation |
| Data security | 3-4 | Encryption, PII |
| OWASP Top 10 | 5-7 | SQLi, XSS, CSRF, IDOR |

### Stage 7: Add Missing Workflow Scenarios

Create 15-20 scenarios for uncovered workflows:

| Workflow | Scenarios |
|----------|-----------|
| WF-003: Re-import | 5-8 |
| WF-006: SFTP retrieval | 3-5 |
| WF-007: Date reconciliation | 3-5 |
| WF-008: BNetzA reporting | 2-3 |

### Stage 8: Generate Deliverables

| File | Content |
|------|---------|
| `test-scenarios.md` | Comprehensive documentation |
| `test-scenarios.json` | Structured metadata |
| `test-matrix.csv` | Tracking matrix |
| `test-dependencies.puml` | Execution order visualization |
| `PHASE11_SUMMARY.md` | Phase summary |

### Stage 9: Validate Outputs

**Validation checks**:
- [ ] All 5 files exist
- [ ] CSV header has 11 columns
- [ ] NO Sprint column
- [ ] Depends_On column present
- [ ] Scenario count 100-150
- [ ] All 8 workflows covered
- [ ] PlantUML valid
- [ ] JSON parseable

---

## CHANGE Mode Specifics

When in CHANGE mode:

**Load existing test inventory** from Phase 6:
```json
{
  "test_class": "ExportPortingIntegrationTest",
  "workflows_covered": ["WF-001"],
  "business_rules_tested": ["BR-015", "BR-016"]
}
```

**Classification in JSON output**:
```json
{
  "classification_summary": {
    "reuse_count": 35,
    "modify_count": 25,
    "new_count": 40,
    "total_scenarios": 100
  }
}
```

---

## Integration with Other Phases

### Input from Previous Phases

| Phase | File | Usage |
|-------|------|-------|
| Phase 3 | ruletable.json | Business rule traceability |
| Phase 5 | control-flow-mapping.json | Workflow coverage |
| Phase 6 | analysis.json | Existing tests (CHANGE mode) |
| Phase 10 | user-stories.json | Test stories to expand |

### Output to Subsequent Phases

| Phase | Consumer | Usage |
|-------|----------|-------|
| Phase 12 | Unit Tests | Test case generation |
| Phase 14 | Test Scripts | Automation scripts |
| QA Team | Manual execution | test-scenarios.md |

---

## Success Criteria

Phase 11 succeeds when:

- [ ] 100-120 test scenarios generated
- [ ] Expansion ratio 15-20x achieved
- [ ] All 8 workflows covered (WF-001 to WF-008)
- [ ] 80%+ business rules referenced
- [ ] CSV has NO Sprint column
- [ ] CSV has Depends_On column
- [ ] All scenarios have 5+ test steps
- [ ] All scenarios have precise test data
- [ ] CHANGE mode: Classification summary included
- [ ] PlantUML valid
- [ ] JSON parseable

---

## Final Step: Update Workflow State

After all diagrams validate, update `results/${FEATURE}/.workflow-state.md`:

1. **Phase 11**: Set to Complete with timestamp
2. **Last Activity**: "Completed Phase 11 system test design"
3. **Next Action**: "Run /12-unit-test-generation-workflow ${FEATURE}"
4. **Decisions Log**: Add system test scenario expansion details

---

## Common Pitfalls and Fixes

| Pitfall | Fix |
|---------|-----|
| Too few scenarios (<100) | Apply expansion ratio 15-20x |
| Missing workflows | Add WF-003, WF-006, WF-007, WF-008 |
| Sprint column in CSV | Remove, forbidden |
| No classification (CHANGE mode) | Add REUSE/MODIFY/NEW to each |
| Generic test steps | Make specific with exact data |
| Missing business rules | Link each scenario to BR-XXX |

---

## Related Skills

- **10-story-generation-workflow** - Phase 10 (input to Phase 11)
- **12-unit-test-generation-workflow** - Phase 12 (uses scenarios)
- **csv-jira-formatter** - CSV escaping rules
- **german-glossary** - German telecommunications terminology
