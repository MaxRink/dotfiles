
# Contracts Generation Reference

## Your Task

Generate API contracts and integration specifications.

**Output:** `.migration/<feature>/spec-specification/contracts.md`

## Input Context

Your prompt provides:

- Feature name
- `.migration/<feature>/architect/target-architecture.md` (Section 5: Integration Design)
- `.migration/<feature>/analysis/analysis.json` (dependencies array)
- `.migration/<feature>/plan/plan.json` (constraints.integration.systems)

## Workflow

### 1. Extract Integration Points

From **target-architecture.md Section 5:**

- External system connections
- Protocols (REST, SOAP, GraphQL, gRPC)
- Data exchange formats

From **analysis.json dependencies:**

- External API calls
- Message queue subscriptions/publications
- Database connections
- File system interactions

From **plan.json constraints.integration.systems:**

- Systems that must remain unchanged
- Integration constraints

### 2. Define API Contracts

For each integration point, document:

**REST APIs:**

- Endpoint URL pattern
- HTTP method
- Request schema (headers, params, body)
- Response schema (success and error cases)
- Authentication requirements
- Rate limits and timeouts

**Messaging (Kafka, RabbitMQ, JMS):**

- Topic/queue name
- Message schema (JSON, Avro, Protobuf)
- Producer/consumer semantics
- Error handling (DLQ, retry policy)

**Databases:**

- Connection parameters
- Schema access requirements
- Stored procedures or views
- Transaction boundaries

**Files:**

- File formats and schemas
- Directory paths
- Read/write permissions
- Error handling for missing/corrupt files

### 3. Document Contract Preservation

For each constraint from plan.json:

- Identify which existing contracts must be preserved
- Document compatibility requirements
- Note any contract transformation needed

### 4. Generate OpenAPI/AsyncAPI Specs (Optional)

If the target stack includes REST APIs or async messaging:

- Generate OpenAPI 3.0 spec for REST endpoints
- Generate AsyncAPI 2.0 spec for message channels
- Include as code blocks in contracts.md

### 5. Pre-Write Validation

Before writing, verify:

- ✓ Every external system from plan.json is documented
- ✓ Request/response schemas complete and unambiguous
- ✓ Error scenarios documented for each contract
- ✓ Authentication specified for each external call

## Output Format

```markdown
# Integration Contracts

## Executive Summary
- Total integration points: N
- External systems: [list]
- Protocol breakdown: REST (N), Messaging (N), Database (N), File (N)

## 1. RESTful API Contracts

### 1.1 [External System Name]
**Endpoint:** `GET /api/resource/{id}`
**Authentication:** Bearer token
**Request Headers:** ...
**Response (200 OK):** ...
**Error Handling:** ...

## 2. Messaging Contracts
## 3. Database Contracts
## 4. File Contracts
## 5. Contract Preservation Strategy
```

## Completion

Return to orchestrator:

```text
DONE: contracts.md written
- Integration points: N
- REST APIs: N
- Messaging: N
- Databases: N
- Files: N
```
