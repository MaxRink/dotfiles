# RNVS Capability Inventory Template

Use this template for generating `results/${FEATURE}/phase9/rnvs_capability_inventory.md`.

---

```markdown
# RNVS Functional Capabilities Inventory
# Feature: ${FEATURE}

**Generated**: ${TIMESTAMP}
**Source Phases**: Phase 1-5 outputs
**Workflow Mode**: ${WORKFLOW_MODE}

---

## Business Rules (from Phase 3)

**Total Rules**: ${RULE_COUNT}

| Rule ID | Rule Name | Category | Source File | Source Function | Confidence |
|---------|-----------|----------|-------------|-----------------|------------|
| BR-001 | ${NAME} | Validation | ${FILE} | ${FUNCTION} | High |
| BR-002 | ${NAME} | Business Logic | ${FILE} | ${FUNCTION} | Medium |
| BR-003 | ${NAME} | Integration | ${FILE} | ${FUNCTION} | High |
| BR-004 | ${NAME} | Compliance | ${FILE} | ${FUNCTION} | High |
<!-- Add all rules from phase3/ruletable.json -->

### Rule Category Summary

| Category | Count | Description |
|----------|-------|-------------|
| Validation | ${COUNT} | Input validation, format checks |
| Business Logic | ${COUNT} | Workflow decisions, calculations |
| Integration | ${COUNT} | External system patterns |
| Compliance | ${COUNT} | Regulatory requirements (BNetzA, GDPR) |

---

## Workflows (from Phase 5)

**Total Workflows**: ${WORKFLOW_COUNT}

| Workflow ID | Workflow Name | Steps | Business Rules | Source Files |
|-------------|---------------|-------|----------------|--------------|
| WF-001 | ${NAME} | ${STEPS} | BR-001, BR-002 | ${FILES} |
| WF-002 | ${NAME} | ${STEPS} | BR-003, BR-004 | ${FILES} |
<!-- Add all workflows from phase5/control-flow-mapping.json -->

### Workflow Details

#### WF-001: ${WORKFLOW_NAME}

**Description**: ${DESCRIPTION}

**Steps**:
1. ${STEP_1} (Rules: BR-001)
2. ${STEP_2} (Rules: BR-002)
3. ${STEP_3} (Rules: BR-003)

**Source Files**: ${FILE_LIST}

---

## External Integrations (from Phase 2)

**Total Integrations**: ${INTEGRATION_COUNT}

| Integration Name | Type | Protocol | Purpose | Source Reference |
|------------------|------|----------|---------|------------------|
| ${SYSTEM_1} | Database | Oracle JDBC | ${PURPOSE} | ${FILE} |
| ${SYSTEM_2} | API | REST/HTTPS | ${PURPOSE} | ${FILE} |
| ${SYSTEM_3} | File | SFTP | ${PURPOSE} | ${FILE} |
| ${SYSTEM_4} | Message Queue | JMS | ${PURPOSE} | ${FILE} |
<!-- Add all integrations from phase2/dependency_map.md -->

---

## Data Entities (from Phase 1/2)

**Total Tables/Files**: ${TABLE_COUNT}

| Entity Name | Type | Source | Purpose | Key Columns |
|-------------|------|--------|---------|-------------|
| ${TABLE_1} | Database Table | Oracle | ${PURPOSE} | ${COLUMNS} |
| ${TABLE_2} | Database Table | PostgreSQL | ${PURPOSE} | ${COLUMNS} |
| ${FILE_1} | File | SFTP | ${PURPOSE} | ${FORMAT} |
<!-- Add all data entities from phase1/analysis.json -->

---

## Async Operations (from Phase 5)

**Total Async Operations**: ${ASYNC_COUNT}

| Operation Name | Trigger Type | Implementation | Purpose |
|----------------|--------------|----------------|---------|
| ${OPERATION_1} | Scheduled (cron) | ${FILE} | ${PURPOSE} |
| ${OPERATION_2} | Event-driven | ${FILE} | ${PURPOSE} |
| ${OPERATION_3} | Batch | ${FILE} | ${PURPOSE} |
<!-- Add all async operations from phase5 -->

---

## Summary Statistics

| Category | Count |
|----------|-------|
| Business Rules | ${RULE_COUNT} |
| Workflows | ${WORKFLOW_COUNT} |
| External Integrations | ${INTEGRATION_COUNT} |
| Data Entities | ${TABLE_COUNT} |
| Async Operations | ${ASYNC_COUNT} |
| **Total RNVS Components** | **${TOTAL_COUNT}** |

---

*This inventory is used as the SOURCE baseline for gap analysis comparison against VNRM capabilities.*
```
