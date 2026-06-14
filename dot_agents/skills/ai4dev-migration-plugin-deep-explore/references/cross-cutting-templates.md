# Cross-Cutting Documentation Templates

> **Produce only the templates relevant to what was found.**
> If there are no data flows between components, skip data-flow.md entirely.
> If there are no APIs, skip api-contracts.md entirely.

---

## Template 1: data-flow.md

```markdown
# System Data Flow

## Data Sources

### Databases
- **<DatabaseName>**:
  - Type: <PostgreSQL, MySQL, MongoDB, etc.>
  - Tables/Collections: <list>
  - Access Pattern: <Read/Write patterns>
  - Connection: `<file:line>`

### External APIs
- **<APIName>**:
  - Purpose: <what data is fetched>
  - Authentication: <method>
  - Usage: `<file:line>`

### File Systems
- **<FileType>**:
  - Location: <path>
  - Purpose: <config, uploads, logs, etc.>

### Message Queues
- **<QueueName>**:
  - Type: <Kafka, RabbitMQ, etc.>
  - Topics: <topic names>
  - Message Format: <description>
  - Consumer: `<file:line>`

---

## Data Transformations

### <Transformation Name>
- **Location**: `<file:line>`
- **Input**: <data structure>
- **Process**: <what happens>
- **Output**: <data structure>
- **Business Logic**: <why this transformation exists>

---

## Data Sinks

### Database Writes
- **<TableName>**: <INSERT/UPDATE/DELETE> — `<file:line>`

### External API Calls
- **<APIEndpoint>**: <what data is sent> — `<file:line>`

### Cache Updates
- **<CacheType>**: Key pattern: <pattern>, TTL: <ttl> — `<file:line>`

---

## Critical Data Paths

### <Business Flow Name>
1. `<file:line>` → <description>
2. `<file:line>` → <description>
3. `<file:line>` → <description>

---

## Data Security

### Sensitive Data Handling
- **<DataType>**: Storage: <how>, Transmission: <how>, Access: <who>

### PII Management
- **Fields**: <list>
- **Compliance**: <GDPR, etc.>
```

---

## Template 2: dependencies.md

```markdown
# System Dependencies

## External Dependencies

### Libraries
#### <LibraryName> (v<version>)
- **Purpose**: <what it's used for>
- **License**: <license type>
- **Usage Locations**: `<file:line>`
- **Usage Pattern**: <how it's used in the codebase>

### Third-Party APIs
#### <APIName>
- **Provider**: <company/service>
- **Endpoints Used**: <endpoint>: <purpose>
- **Authentication**: <method>
- **Rate Limits**: <if applicable>
- **Fallback Strategy**: <what happens if down>

### Infrastructure
#### <DatabaseName>
- **Type**: <PostgreSQL, MongoDB, etc.>
- **Version**: <version>
- **Purpose**: <primary data store, cache, etc.>

#### <CacheName>
- **Type**: <Redis, Memcached, etc.>
- **Purpose**: <what is cached>

#### <MessageQueueName>
- **Type**: <Kafka, RabbitMQ, etc.>
- **Topics**: <list>
- **Purpose**: <async processing, events, etc.>

---

## Internal Dependencies

### Module Dependency Graph

<Mermaid diagram or text tree showing module dependencies>

### Circular Dependencies

<List any circular dependencies detected, with impact and resolution strategy>

### Shared Utilities
#### <UtilityModule>
- **Purpose**: <what it provides>
- **Used By**: <list of modules>

---

## Dependency Impact Analysis

### If <ModuleName> Changes
- **Direct Impact**: <modules that break>
- **Indirect Impact**: <modules affected transitively>

### Recommended Migration Order
1. <Module> (no dependencies)
2. <Module> (depends on 1)
3. <Module> (depends on 2)
```

---

## Template 3: api-contracts.md

```markdown
# API Contracts

## REST Endpoints

### <HTTP_METHOD> <path>

**Module**: <module name>
**Location**: `<file:line>`

- **Purpose**: <what this endpoint does>
- **Request**:
  - Headers: <required headers>
  - Path Parameters: <params>
  - Query Parameters: <params>
  - Body: <JSON shape>
- **Response**:
  - Success (200): <JSON shape>
  - Error (4xx): <error shape>
  - Error (5xx): <error shape>
- **Authentication**: <method>
- **Authorization**: <required roles>
- **Rate Limiting**: <if applicable>

---

## GraphQL (if applicable)

### Schema
<schema definition>

### Queries
#### <queryName>
- **Purpose**: <description>
- **Arguments**: <args>
- **Returns**: <type>

### Mutations
#### <mutationName>
- **Purpose**: <description>
- **Arguments**: <args>
- **Returns**: <type>

---

## CORBA / IDL Interfaces (if applicable)

### <IDLModuleName>
**IDL File**: `<file:line>`
**Pragma Prefix**: `<pragma prefix>`

#### Interface: <InterfaceName>
- **Purpose**: <description>
- **C++ Servant**: `<file:line>`
- **Java Stub**: `<file:line>`
- **Key Methods**:
  - `<returnType> <methodName>(<params>)` — <description>
  - `<returnType> <methodName>(<params>)` — <description>
- **Data Transfer Objects**: <list of DTOs / structs used>
- **Registration**: <how servants are registered, e.g., NameService, IOR file>

---

## SOAP / WSDL Endpoints (if applicable)

### <ServiceName>
**WSDL File**: `<file:line>`
**Binding**: <SOAP 1.1/1.2, JMS, etc.>
**Module**: <module>
**Location**: `<file:line>`

#### Operation: <operationName>
- **Purpose**: <description>
- **Input**: <XML element / type>
- **Output**: <XML element / type>
- **Fault**: <fault type>
- **Transport**: <HTTP, JMS queue name, etc.>

---

## Internal Service Interfaces

### <ServiceInterfaceName>
**Module**: <module>
**Location**: `<file:line>`

#### <methodName>
- **Signature**: <method signature>
- **Purpose**: <description>
- **Contract**: <pre/post conditions>

---

## Event Contracts

### <EventName>
- **Publisher**: <module/service> — `<file:line>`
- **Topic/Channel**: <name>
- **Payload**: <JSON shape>
- **Consumers**: <list of consumers with file:line>
- **Delivery Guarantee**: <at-least-once, exactly-once, etc.>
```

---

## Template 4: security.md

```markdown
# Security Overview

## Authentication Architecture

### Authentication Flow
1. <Step 1> — `<file:line>`
2. <Step 2> — `<file:line>`
3. <Step 3> — `<file:line>`

### Token Lifecycle
- **Creation**: `<file:line>` — <how tokens are issued>
- **Validation**: `<file:line>` — <how tokens are verified>
- **Refresh**: `<file:line>` — <refresh strategy>
- **Expiry**: <TTL, sliding window, absolute>
- **Revocation**: <how tokens are invalidated>

### Session Management
- **Storage**: <server-side, JWT, cookie, etc.>
- **Timeout**: <inactivity, absolute>
- **Concurrent Sessions**: <policy>

---

## Authorization Model

### Role Hierarchy
- <Role>: <permissions>
  - <Sub-role>: <permissions>

### Permission Matrix

| Resource | Action | <Role 1> | <Role 2> | <Role 3> |
|----------|--------|----------|----------|----------|
| <resource> | <action> | Yes/No | Yes/No | Yes/No |

### Guard/Middleware Chain
1. `<file:line>` — <what it checks>
2. `<file:line>` — <what it checks>

### Ownership Checks
- **Pattern**: <how ownership is verified>
- **Location**: `<file:line>`

---

## Secrets Management

### Secret Sources
- **Environment Variables**: <list of secret env vars>
- **Vault Integration**: <if applicable> — `<file:line>`
- **Config Files**: <which config files contain secrets>

### Secret Injection
- <How secrets reach the application at runtime>

### Concerns
- **Hardcoded Credentials**: `<file:line>` (if found)
- **Secrets in Version Control**: <any .env files committed>
- **Rotation Policy**: <if documented>

---

## Data Protection

### Encryption at Rest
- **Method**: <algorithm>
- **What's Encrypted**: <databases, file storage, etc.>
- **Key Management**: <where keys are stored>

### Encryption in Transit
- **TLS Configuration**: `<file:line>`
- **Certificate Management**: <approach>

### PII Handling
- **Fields**: <list of PII fields across the system>
- **Storage**: <how PII is stored>
- **Access Controls**: <who can access PII>
- **Compliance**: <GDPR, CCPA, HIPAA requirements>

---

## Security Headers and CORS

### CORS Configuration
- **Allowed Origins**: `<file:line>` — <origins>
- **Allowed Methods**: <methods>
- **Credentials**: <allowed or not>

### Security Headers
- **CSP**: `<file:line>` — <policy>
- **HSTS**: <configuration>
- **X-Frame-Options**: <value>
- **X-Content-Type-Options**: <value>

---

## Vulnerabilities Found

### <Vulnerability Description>
- **Location**: `<file:line>`
- **Severity**: <Critical/High/Medium/Low>
- **Description**: <what the issue is>
- **Impact**: <what could happen>

---

## Audit Trail

### What's Logged
- <Action>: <format, destination> — `<file:line>`

### Log Destinations
- <destination>: <what goes here>

### Retention
- <policy if documented>
```

---

## Template 5: database-schema.md

````markdown
# Database Schema

## Overview

- **Database(s)**: <name, type, version>
- **ORM/Migration Tool**: <Flyway, Alembic, Prisma, Sequelize, etc.>
- **Migration Directory**: `<path>`

---

## Entity Relationship Diagram

```mermaid
erDiagram
    <Entity1> ||--o{ <Entity2> : "<relationship>"
    <Entity2> }|--|| <Entity3> : "<relationship>"
```

---

## Tables / Collections

### <TableName>

**Purpose**: <what this table stores>
**Location**: `<model/entity file:line>`

| Column | Type | Nullable | Default | Constraints | Description |
|--------|------|----------|---------|-------------|-------------|
| `<column>` | <type> | Yes/No | <default> | <PK, FK, UNIQUE, INDEX> | <description> |

**Indexes**:

- `<index_name>`: columns `(<col1>, <col2>)` — <purpose>

**Relationships**:

- <RelationType> → `<OtherTable>` via `<foreign_key>` — <description>

**Partitioning**: <strategy if applicable>

---

## Migrations

### Migration History

| Migration | Date | Description |
|-----------|------|-------------|
| `<filename>` | <date> | <what it does> |

### Naming Convention

- <pattern>

### Rollback Support

- <yes/no, approach>

---

## Stored Procedures / Triggers / Views

### <Name>

- **Type**: <procedure/trigger/view>
- **Location**: `<file:line>`
- **Purpose**: <what it does>
- **Input**: <parameters>
- **Output**: <what it returns or affects>

---

## Access Patterns

### <TableName>

- **Read Pattern**: <frequency, typical queries>
- **Write Pattern**: <frequency, typical operations>
- **Join Patterns**: <common joins with other tables>
- **Hot Spots**: <columns frequently queried>

---

## Replication / Sharding

- **Strategy**: <if applicable>
- **Configuration**: `<file:line>`

````

---

## Template 6: testing.md

```markdown
# Testing Strategy

## Test Pyramid

- **Unit Tests**: <count/percentage> — `<path/to/unit/tests/>`
- **Integration Tests**: <count/percentage> — `<path/to/integration/tests/>`
- **E2E Tests**: <count/percentage> — `<path/to/e2e/tests/>`
- **Contract Tests**: <count/percentage> — `<path/to/contract/tests/>`
- **Performance Tests**: <count/percentage> — `<path/to/perf/tests/>`

---

## Test Frameworks

### <FrameworkName>
- **Purpose**: <unit, integration, e2e>
- **Configuration**: `<file:line>`
- **Version**: <version>

### Assertion Libraries
- <library>: <version, purpose>

### Mocking Libraries
- <library>: <version, what it mocks>

---

## Test Configuration

### Runner Configuration
- **Config File**: `<path>` — <key settings>
- **Parallelization**: <strategy>
- **Timeout**: <default timeout>

### Environment Setup
- **Test Database**: <in-memory, test containers, separate instance>
- **External Services**: <mocked, stubbed, containerized>
- **Environment Variables**: <how test env is configured>

---

## Shared Test Utilities

### Fixtures
- `<path>`: <what data/setup it provides>

### Factories / Builders
- `<path>`: <what test objects they create>

### Custom Matchers / Helpers
- `<path>`: <purpose>

---

## CI/CD Test Pipeline

### Pipeline Stages
1. <Stage>: <what tests run, trigger condition>
2. <Stage>: <what tests run>

### Parallelization
- <How tests are split across workers>

### Coverage Reporting
- **Tool**: <Istanbul, JaCoCo, coverage.py, etc.>
- **Threshold**: <minimum coverage required>
- **Report Location**: <where reports are generated>

---

## Coverage Gaps

### Untested Areas
- <Module/component>: <what's not tested>

### Known Flaky Tests
- `<test file:line>`: <why it's flaky>

### Missing Test Types
- <What types of tests are absent that should exist>
```

---

## Template 7: infrastructure.md

```markdown
# Infrastructure & Deployment

## Deployment Topology

### Services
| Service | Type | Runtime | Port | Dependencies |
|---------|------|---------|------|-------------|
| <service> | <web, worker, cron> | <Node, JVM, etc.> | <port> | <other services> |

---

## Container Configuration

### Dockerfiles
#### <ServiceName>
- **File**: `<path>`
- **Base Image**: <image:tag>
- **Build Stages**: <multi-stage details>
- **Exposed Ports**: <ports>
- **Entry Point**: <command>

### Docker Compose
- **File**: `<path>`
- **Services**: <list of services defined>
- **Networks**: <network configuration>
- **Volumes**: <volume mounts>

---

## Kubernetes Configuration

### Deployments
#### <ServiceName>
- **File**: `<path>`
- **Replicas**: <count>
- **Resource Limits**: CPU: <limit>, Memory: <limit>
- **Environment**: <config map/secret references>

### Services
- **<ServiceName>**: Type: <ClusterIP/NodePort/LoadBalancer>, Port: <port>

### Ingress
- **Host**: <hostname>
- **Path Rules**: <routing rules>
- **TLS**: <certificate configuration>

### Config Maps / Secrets
- **<Name>**: `<path>` — <what it configures>

---

## CI/CD Pipeline

### Pipeline Definition
- **File**: `<path>` — <GitHub Actions, GitLab CI, Jenkins, etc.>

### Stages
1. **<Stage Name>**: <what happens, trigger condition>
2. **<Stage Name>**: <what happens>

### Deployment Strategy
- **Type**: <rolling update, blue-green, canary>
- **Rollback**: <automatic/manual, how>

---

## Environment Matrix

| Setting | Development | Staging | Production |
|---------|-------------|---------|------------|
| <setting> | <value> | <value> | <value> |

---

## Health Checks

### <ServiceName>
- **Health Endpoint**: `<path>` — <what it checks>
- **Readiness Endpoint**: `<path>` — <what it checks>
- **Liveness Probe**: <configuration>

---

## Scaling

### Auto-Scaling
- **Metric**: <CPU, memory, custom metric>
- **Min/Max Replicas**: <min> / <max>
- **Scale-up Threshold**: <value>
- **Scale-down Threshold**: <value>

---

## Monitoring and Alerting

### Metrics
- **Tool**: <Prometheus, Datadog, etc.>
- **Custom Metrics**: <list>
- **Dashboard**: <location if configured>

### Alerting
- **Tool**: <PagerDuty, OpsGenie, etc.>
- **Rules**: <critical alerts defined>

### Logging
- **Framework**: <log4j, Winston, etc.>
- **Aggregation**: <ELK, CloudWatch, etc.>
- **Format**: <structured/unstructured, JSON>

---

## Disaster Recovery

### Backups
- **Database**: <schedule, tool, retention>
- **File Storage**: <approach>

### Recovery Plan
- <documented procedures if found>
```

---

## Template 8: technical-debt.md

```markdown
# Technical Debt Register

## Summary

- **Total Items**: <count>

---

## TODOs / FIXMEs / HACKs

| Location | Tag | Description | Context |
|----------|-----|-------------|---------|
| `<file:line>` | <TODO/FIXME/HACK/XXX> | <text> | <surrounding context> |

---

## Deprecated Code

### <Deprecation Description>
- **Location**: `<file:line>`
- **Status**: <still in use / partially migrated / can be removed>
- **Replacement**: <new approach if known>
- **Impact**: <what breaks if removed now>

---

## Known Workarounds

### <Workaround Description>
- **Location**: `<file:line>`
- **Root Cause**: <why the workaround exists>
- **Scope**: <what code paths are affected>

---

## Coupling Hotspots

### <Module/Class Name>
- **Location**: `<file:line>`
- **Issue**: <god class, circular import, tight coupling>
- **Fan-in/Fan-out**: <count if measurable>
- **Affected Modules**: <list>

---

## Dead Code

### Unused Exports
| Location | Export | Last Referenced |
|----------|--------|----------------|
| `<file:line>` | <export name> | <never / unknown> |

### Unreachable Code
| Location | Description |
|----------|-------------|
| `<file:line>` | <why it's unreachable> |

---

## Suppressed Warnings

| Location | Suppression | Reason |
|----------|-------------|--------|
| `<file:line>` | <lint-disable rule> | <stated reason or inferred> |

---

## Outdated Dependencies

| Dependency | Current | Latest | Severity | CVEs |
|-----------|---------|--------|----------|------|
| <name> | <version> | <latest> | <Low/Medium/High/Critical> | <CVE IDs if known> |

---

## Dependency Coupling Summary

| Component | Fan-in | Fan-out | Circular Deps | Notes |
|-----------|--------|---------|---------------|-------|
| <module> | <count> | <count> | <yes/no> | <observable facts> |
```
