# Gap Analysis Report Template

Use this template for generating `results/${FEATURE}/phase9/gap_analysis.md`.

---

```markdown
# Gap Analysis Report: RNVS → VNRM Migration
# Feature: ${FEATURE}

**Generated**: ${TIMESTAMP}
**Phase**: 9 - Gap Analysis
**Workflow Mode**: ${WORKFLOW_MODE} (GREENFIELD | CHANGE)
**Analyst**: Claude Code (Autonomous Workflow)

---

## Executive Summary

### Migration Overview
- **Total RNVS Components Analyzed**: ${TOTAL_RNVS}
- **Total VNRM Components Designed**: ${TOTAL_VNRM}
- **Overall Coverage Rate**: ${COVERAGE_PERCENT}%
- **Identified Gaps**: ${TOTAL_GAPS}
  - Critical Gaps (P0): ${P0_COUNT}
  - High Priority Gaps (P1): ${P1_COUNT}
  - Medium Priority Gaps (P2): ${P2_COUNT}
  - Low Priority Gaps (P3): ${P3_COUNT}

### Coverage Breakdown

| Category | Coverage % | Status | Gaps |
|----------|------------|--------|------|
| Business Rules | ${BR_COVERAGE}% | ${BR_GRADE} | ${BR_GAPS} |
| API Endpoints | ${API_COVERAGE}% | ${API_GRADE} | ${API_GAPS} |
| Database Schema | ${DB_COVERAGE}% | ${DB_GRADE} | ${DB_GAPS} |
| Integrations | ${INT_COVERAGE}% | ${INT_GRADE} | ${INT_GAPS} |
| Events/Async | ${EVENT_COVERAGE}% | ${EVENT_GRADE} | ${EVENT_GAPS} |

### Quality Assessment
- **Coverage Grade**: ${OVERALL_GRADE} (Excellent/Good/Needs Improvement/Critical)
- **Migration Readiness**: ${READINESS} (Ready/Needs Work/Not Ready)
- **Recommended Action**: ${RECOMMENDATION}

---

## 1. Business Rule Coverage

### 1.1 Fully Covered Business Rules

**Total**: ${BR_FULLY_COVERED} rules

| Rule ID | Rule Name | VNRM Service | VNRM Implementation | Confidence |
|---------|-----------|--------------|---------------------|------------|
| BR-001 | ${RULE_NAME} | ${SERVICE} | ${ENDPOINT} | High |
<!-- Repeat for each fully covered rule -->

### 1.2 Partially Covered Business Rules

**Total**: ${BR_PARTIALLY_COVERED} rules

| Rule ID | Rule Name | VNRM Service | Gap Description | Priority | Effort | Recommendation |
|---------|-----------|--------------|-----------------|----------|--------|----------------|
| BR-XXX | ${RULE_NAME} | ${SERVICE} | ${GAP_DESC} | P1 | M | ${ACTION} |
<!-- Repeat for each partially covered rule -->

**Detailed Gap Analysis**:

#### BR-XXX: ${RULE_NAME}
- **RNVS Implementation**: ${RNVS_DESC}
- **RNVS Source**: ${FILE}:${LINE}
- **VNRM Implementation**: ${VNRM_DESC}
- **VNRM Service**: ${SERVICE}
- **Coverage Status**: Partially Covered (${PERCENT}%)
- **Gap**: ${GAP_DESCRIPTION}
- **Business Impact**: ${IMPACT} - ${REASON}
- **Technical Complexity**: ${COMPLEXITY} - ${DETAILS}
- **Priority**: ${PRIORITY}
- **Effort**: ${EFFORT}
- **Recommendation**: ${RECOMMENDATION}
- **Acceptance Criteria**:
  - [ ] ${CRITERION_1}
  - [ ] ${CRITERION_2}

### 1.3 Not Covered Business Rules

**Total**: ${BR_NOT_COVERED} rules

| Rule ID | Rule Name | RNVS Source | Gap Description | Priority | Effort | Recommendation |
|---------|-----------|-------------|-----------------|----------|--------|----------------|
| BR-XXX | ${RULE_NAME} | ${FILE} | ${GAP_DESC} | P0 | L | ${ACTION} |
<!-- Repeat for each not covered rule -->

### 1.4 Deprecated/Obsolete Business Rules

**Total**: ${BR_DEPRECATED} rules

| Rule ID | Rule Name | RNVS Source | Deprecation Reason | Replacement in VNRM |
|---------|-----------|-------------|-------------------|---------------------|
| BR-XXX | ${RULE_NAME} | ${FILE} | ${REASON} | ${REPLACEMENT} |

---

## 2. API Endpoint Coverage

### 2.1 Fully Covered API Endpoints

**Total**: ${API_FULLY_COVERED} endpoints

| RNVS Workflow | RNVS Source | VNRM Service | HTTP Method | Endpoint Path | Confidence |
|---------------|-------------|--------------|-------------|---------------|------------|
| ${WORKFLOW} | ${FILE} | ${SERVICE} | POST | /api/v1/${PATH} | High |

### 2.2 Partially Covered API Endpoints

**Total**: ${API_PARTIALLY_COVERED} endpoints

| RNVS Workflow | VNRM Endpoint | Gap Description | Priority | Effort | Recommendation |
|---------------|---------------|-----------------|----------|--------|----------------|
| ${WORKFLOW} | ${ENDPOINT} | ${GAP} | P1 | S | ${ACTION} |

### 2.3 Not Covered API Endpoints

**Total**: ${API_NOT_COVERED} endpoints

| RNVS Workflow | RNVS Source | Gap Description | Priority | Effort | Recommendation |
|---------------|-------------|-----------------|----------|--------|----------------|
| ${WORKFLOW} | ${FILE} | ${GAP} | P0 | M | ${ACTION} |

---

## 3. Database Schema Coverage

### 3.1 Fully Migrated Tables

**Total**: ${DB_FULLY_COVERED} tables

| RNVS Table | RNVS Database | VNRM Table | VNRM Service | VNRM Database | Migration Strategy |
|------------|---------------|------------|--------------|---------------|-------------------|
| ${TABLE} | Oracle | ${TABLE} | ${SERVICE} | PostgreSQL | Direct 1:1 mapping |

### 3.2 Partially Migrated Tables

**Total**: ${DB_PARTIALLY_COVERED} tables

| RNVS Table | VNRM Table | Gap Description | Priority | Effort | Recommendation |
|------------|------------|-----------------|----------|--------|----------------|
| ${TABLE} | ${TABLE} | Missing columns: ${COLS} | P2 | S | Extend schema |

### 3.3 Not Migrated Tables

**Total**: ${DB_NOT_COVERED} tables

| RNVS Table | RNVS Purpose | Gap Description | Priority | Effort | Recommendation |
|------------|--------------|-----------------|----------|--------|----------------|
| ${TABLE} | ${PURPOSE} | No VNRM equivalent | P1 | M | Design new schema |

---

## 4. Integration Coverage

### 4.1 Fully Covered Integrations

**Total**: ${INT_FULLY_COVERED} integrations

| External System | RNVS Integration | VNRM Service | VNRM Integration | Confidence |
|-----------------|------------------|--------------|------------------|------------|
| ${SYSTEM} | ${TYPE}/${PROTOCOL} | ${SERVICE} | REST/HTTPS | High |

### 4.2 Not Covered Integrations

**Total**: ${INT_NOT_COVERED} integrations

| External System | RNVS Integration | Gap Description | Priority | Effort | Recommendation |
|-----------------|------------------|-----------------|----------|--------|----------------|
| ${SYSTEM} | ${TYPE} | No VNRM equivalent | P1 | L | Design REST wrapper |

---

## 5. Event/Async Coverage

### 5.1 Fully Covered Async Operations

**Total**: ${EVENT_FULLY_COVERED} operations

| RNVS Async Operation | RNVS Trigger | VNRM Message Bus Topic | VNRM Publisher | Subscribers |
|---------------------|--------------|------------------|----------------|-------------|
| ${OPERATION} | ${TRIGGER} | ${TOPIC} | ${SERVICE} | ${SUBSCRIBERS} |

### 5.2 Not Covered Async Operations

**Total**: ${EVENT_NOT_COVERED} operations

| RNVS Async Operation | RNVS Implementation | Gap Description | Priority | Effort |
|---------------------|---------------------|-----------------|----------|--------|
| ${OPERATION} | ${FILE} | No event equivalent | P2 | M |

---

## 6. Risk Assessment

### 6.1 Critical Risks

**Total Critical Risks**: ${CRITICAL_RISK_COUNT}

| Risk ID | Gap Description | Business Impact | Technical Complexity | Probability | Mitigation Strategy |
|---------|-----------------|-----------------|---------------------|-------------|---------------------|
| RISK-001 | ${DESCRIPTION} | High | High | 90% | ${STRATEGY} |

### 6.2 High Risks

**Total High Risks**: ${HIGH_RISK_COUNT}

| Risk ID | Gap Description | Business Impact | Technical Complexity | Probability | Mitigation Strategy |
|---------|-----------------|-----------------|---------------------|-------------|---------------------|
| RISK-XXX | ${DESCRIPTION} | High | Medium | 70% | ${STRATEGY} |

---

## 7. Coverage Matrix (Traceability)

**Complete RNVS → VNRM Traceability Matrix**

| RNVS Component | Type | RNVS Source | VNRM Component | VNRM Service | Coverage % | Confidence | Status |
|----------------|------|-------------|----------------|--------------|------------|------------|--------|
| ${COMPONENT} | ${TYPE} | ${FILE} | ${VNRM} | ${SERVICE} | 100% | High | Complete |
| ${COMPONENT} | ${TYPE} | ${FILE} | ${VNRM} | ${SERVICE} | 75% | Medium | Partial |
| ${COMPONENT} | ${TYPE} | ${FILE} | - | - | 0% | Low | Missing |

---

## 8. Implementation Backlog Summary

### Sprint 1 (Critical - P0)
**Total Effort**: ${SPRINT1_EFFORT} days

| Task ID | Description | Gap Reference | Service | Effort |
|---------|-------------|---------------|---------|--------|
| TASK-001 | ${DESCRIPTION} | BR-XXX | ${SERVICE} | L (10d) |

### Sprint 2 (High - P1)
**Total Effort**: ${SPRINT2_EFFORT} days

| Task ID | Description | Gap Reference | Service | Effort |
|---------|-------------|---------------|---------|--------|
| TASK-XXX | ${DESCRIPTION} | BR-XXX | ${SERVICE} | M (5d) |

### Sprint 3+ (Medium/Low - P2/P3)
**Total Effort**: ${SPRINT3_EFFORT} days

See `implementation_backlog.md` for complete details.

---

## 9. Recommendations

### Immediate Actions (Next 2 Weeks)
1. **${ACTION_1}**: ${DESCRIPTION}
   - Owner: ${TEAM}
   - Success Criteria: ${CRITERIA}

### Short-Term Actions (Next 1-2 Months)
1. ${ACTION}

### Long-Term Actions (Next 3-6 Months)
1. ${ACTION}

---

## 10. Quality Gates for Next Phase

Before proceeding to Phase 10 (Generate Jira Stories), ensure:

- [ ] All P0 (Critical) gaps are acknowledged and planned
- [ ] All P1 (High) gaps are acknowledged and planned
- [ ] Coverage rate ≥ 70% (if below, escalate to architecture team)
- [ ] All critical risks have mitigation strategies
- [ ] Implementation backlog is prioritized and estimated
- [ ] Stakeholders have reviewed and approved gap analysis

---

**Report Status**: COMPLETE
**Overall Coverage**: ${COVERAGE_PERCENT}%
**Migration Readiness**: ${READINESS}
**Recommended Next Phase**: Phase 10 - Generate Jira Stories

*Generated by RNVS→VNRM Migration Workflow - Phase 9 Gap Analysis*
```
