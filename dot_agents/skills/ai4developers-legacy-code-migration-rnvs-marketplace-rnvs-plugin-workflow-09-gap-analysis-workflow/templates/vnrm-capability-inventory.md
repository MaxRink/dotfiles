# VNRM Capability Inventory Template

Use this template for generating `results/${FEATURE}/phase9/vnrm_capability_inventory.md`.

---

```markdown
# VNRM Planned Capabilities Inventory
# Feature: ${FEATURE}

**Generated**: ${TIMESTAMP}
**Workflow Mode**: ${WORKFLOW_MODE}
**Source**: ${VNRM_SOURCE}

---

## Microservices

**Total Microservices**: ${SERVICE_COUNT}

| Service Name | Service Code | Submodule | API Endpoints | DB Tables | Message Bus Topics | Business Rules |
|--------------|--------------|-----------|---------------|-----------|--------------|----------------|
| ${SERVICE_NAME} | ${CODE} | NUM | ${API_COUNT} | ${TABLE_COUNT} | ${TOPIC_COUNT} | BR-001 to BR-010 |
<!-- Add all microservices -->

### Service Details

#### ${SERVICE_NAME}

**Description**: ${DESCRIPTION}

**RNVS Source Mapping**:
- ${RNVS_FILE_1}
- ${RNVS_FILE_2}

**Capabilities**:
- API Endpoints: ${COUNT}
- Database Tables: ${COUNT}
- Message Bus Topics Published: ${COUNT}
- Message Bus Topics Subscribed: ${COUNT}

---

## API Endpoints

**Total Endpoints**: ${ENDPOINT_COUNT}

| Service | Method | Path | Operation | Business Rules | RNVS Source |
|---------|--------|------|-----------|----------------|-------------|
| ${SERVICE} | POST | /api/v1/${PATH} | ${OPERATION} | BR-001, BR-002 | ${FILE} |
| ${SERVICE} | GET | /api/v1/${PATH}/{id} | ${OPERATION} | BR-003 | ${FILE} |
| ${SERVICE} | PUT | /api/v1/${PATH}/{id} | ${OPERATION} | BR-004 | ${FILE} |
| ${SERVICE} | DELETE | /api/v1/${PATH}/{id} | ${OPERATION} | BR-005 | ${FILE} |
<!-- Add all endpoints from microservice-design.json -->

---

## Message Bus Events

**Total Topics**: ${TOPIC_COUNT}

| Topic Name | Publisher | Subscribers | Schema | Partition Key | RNVS Source |
|------------|-----------|-------------|--------|---------------|-------------|
| ${TOPIC} | ${SERVICE} | ${SUBSCRIBERS} | Avro | ${KEY} | ${FILE} |
<!-- Add all topics from event_catalog -->

---

## Database Tables

**Total Tables**: ${TABLE_COUNT}

| Table Name | Owning Service | Database | Purpose | RNVS Source |
|------------|----------------|----------|---------|-------------|
| ${TABLE} | ${SERVICE} | PostgreSQL | ${PURPOSE} | ${RNVS_TABLE} |
<!-- Add all tables from database_design -->

---

## External Integrations

**Total Integrations**: ${INTEGRATION_COUNT}

| Integration Name | Type | Service | Protocol | Purpose | RNVS Source |
|------------------|------|---------|----------|---------|-------------|
| ${SYSTEM} | REST API | ${SERVICE} | HTTPS | ${PURPOSE} | ${FILE} |
| ${SYSTEM} | SFTP | ${SERVICE} | SSH | ${PURPOSE} | ${FILE} |
<!-- Add all external integrations -->

---

## Summary Statistics

| Category | Count |
|----------|-------|
| Microservices | ${SERVICE_COUNT} |
| API Endpoints | ${ENDPOINT_COUNT} |
| Message Bus Topics | ${TOPIC_COUNT} |
| Database Tables | ${TABLE_COUNT} |
| External Integrations | ${INTEGRATION_COUNT} |
| **Total VNRM Components** | **${TOTAL_COUNT}** |

---

## CHANGE Mode: Delta Summary

<!-- Only include this section if WORKFLOW_MODE = CHANGE -->

**Baseline Source**: phase6/analysis.json
**Delta Source**: phase7.1/microservice-changes-design.json

### Changes Applied to Baseline

| Change Type | Count | Description |
|-------------|-------|-------------|
| Endpoints Added | ${COUNT} | New API endpoints in delta |
| Endpoints Modified | ${COUNT} | Changed existing endpoints |
| Endpoints Deprecated | ${COUNT} | Endpoints marked for removal |
| Tables Added | ${COUNT} | New database tables |
| Columns Added | ${COUNT} | New columns in existing tables |
| Topics Added | ${COUNT} | New Message Bus topics |
| Subscriptions Added | ${COUNT} | New event subscriptions |

---

*This inventory represents the TARGET state for gap analysis comparison against RNVS capabilities.*
```
