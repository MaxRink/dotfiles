# VNRM Code Analysis Field Guide

## Overview

This field guide provides detailed explanations for each field in the VNRM code analysis schema. Use this when you need specific guidance on how to populate, validate, or interpret the structured analysis data for modern VNRM microservices.

## Service Metadata Fields

### `service_name` (REQUIRED)
- **Format**: kebab-case string
- **Pattern**: `^[a-z0-9-]+$`
- **Examples**:
  - `num-fcm-fixednet-callnumber-management-api`
  - `prt-pda-processing-backend`
  - `com-cs-config-server-api`
- **Guidelines**: Use actual GitLab repository name without "vnrm/" prefix

### `service_description` (REQUIRED)
- **Format**: String
- **Length**: 10-500 characters
- **Guidelines**:
  - High-level description of service purpose and responsibilities
  - Focus on business functionality, not technical implementation
  - Include key features or domain responsibilities
- **Examples**:
  - "Fixed callnumber management service providing CRUD operations for individual and range callnumbers with complete state machine transitions and BNetzA compliance"
  - "PDA message processing backend for number portability coordination between telecommunications carriers"
  - "Centralized configuration server providing environment-specific settings to all VNRM microservices"

### `analysis_timestamp` (REQUIRED)
- **Format**: ISO8601 date-time string
- **Pattern**: `YYYY-MM-DDTHH:mm:ssZ` or with timezone offset
- **Examples**:
  - `2025-11-19T16:30:00Z`
  - `2025-11-19T16:30:00+01:00`
- **Guidelines**: Use UTC timezone when possible, record when the analysis was actually performed

### `vnrm_submodule` (REQUIRED)
- **Valid Values**: `COM`, `NUM`, `PRT`, `COR`, `SPE`, `NTW`
- **Definitions**:
  - **COM**: Common services (portal, config, RDM, error management)
  - **NUM**: Number management (callnumbers, blocks, inventory)
  - **PRT**: Porting management (PDA processing, carrier coordination)
  - **COR**: Correction management (business error tracking, resolution)
  - **SPE**: Special functions (legacy integration, RNVS proxy, CRM-T)
  - **NTW**: Network management (routing, configuration)

## Technology Stack Fields (REQUIRED)

The `technology_stack` object is required and must contain at minimum: `spring_boot_version`, `java_version`, and `database`.

### `spring_boot_version` (REQUIRED)
- **Format**: Semantic version `x.y.z`
- **Current VNRM Standard**: `2.7.18`
- **Migration Path**: Plan for Spring Boot 3.x upgrade
- **Impact**: Security patches, dependency compatibility, feature availability

### `java_version` (REQUIRED)
- **Format**: Major version number as string
- **Current VNRM Standard**: `17`
- **Supported Versions**: `17`, `21`
- **Guidelines**: Specify the Java runtime version used by the microservice

### `database` (REQUIRED)
- **Standard**: `PostgreSQL 13+`
- **Features to Document**: Partitioning, JSON columns, full-text search, extensions
- **Migration Considerations**: Oracle to PostgreSQL migration patterns

## API Contract Fields (REQUIRED)

The `api_contracts` array is required and must contain at least one endpoint definition.

### `endpoint` (REQUIRED per contract)
- **Format**: Must start with `/api/v1/`, `/api/v2/`, etc.
- **RESTful Patterns**:
  - Resource collections: `/api/v1/callnumbers`
  - Resource instances: `/api/v1/callnumbers/{id}`
  - Sub-resources: `/api/v1/callnumbers/{id}/modifications`
  - Actions: `/api/v1/callnumbers/{id}/state` (for state changes)

### `method` (REQUIRED per contract)
- **Valid Values**: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`
- **Guidelines**:
  - `GET`: Retrieve resources (idempotent, safe)
  - `POST`: Create new resources or non-idempotent operations
  - `PUT`: Full resource replacement (idempotent)
  - `PATCH`: Partial resource update
  - `DELETE`: Remove resources (idempotent)

### `description` (REQUIRED per contract)
- **Format**: String with minimum 10 characters
- **Guidelines**:
  - Clear description of endpoint functionality
  - Include key business logic or validation performed
  - Mention any special behavior or side effects
- **Examples**:
  - "Retrieve callnumber details including current state and validity period"
  - "Update callnumber state with business rule validation"
  - "Search callnumbers with filtering and pagination"

### `status_codes` (optional but recommended)
- **Standard HTTP Codes**:
  - `200`: Success with response body
  - `201`: Created (POST operations)
  - `204`: Success without response body (DELETE)
  - `400`: Bad request (validation errors)
  - `401`: Unauthorized (authentication failure)
  - `403`: Forbidden (authorization failure)
  - `404`: Not found
  - `409`: Conflict (business rule violation, optimistic locking)
  - `429`: Too many requests (rate limiting)
  - `500`: Internal server error
  - `503`: Service unavailable (circuit breaker open)

### `rate_limiting`
- **Formats**:
  - `1000 req/min` - Requests per minute
  - `100 req/sec` - Requests per second
  - `10000 req/hour` - Requests per hour
- **VNRM Standards**: Typically 1000 req/min for read operations, 500 req/min for write operations

## Database Schema Fields

### `tables.columns.type`
- **PostgreSQL Types**:
  - `VARCHAR(n)` - Variable length string
  - `TEXT` - Unlimited text
  - `INTEGER` - 32-bit integer
  - `BIGINT` - 64-bit integer
  - `TIMESTAMP(6)` - Timestamp with microsecond precision
  - `UUID` - Universally unique identifier
  - `BOOLEAN` - True/false
  - `JSON` / `JSONB` - JSON data (prefer JSONB)

### `audit_columns`
- **Standard VNRM Pattern**:
  - `created_date`: TIMESTAMP(6) NOT NULL
  - `updated_date`: TIMESTAMP(6) NOT NULL
  - `created_by`: VARCHAR(60) NOT NULL
  - `updated_by`: VARCHAR(60) NOT NULL
  - `modification_uuid`: UUID NOT NULL (for change tracking)

### `state_machines.states`
- **Callnumber States** (NUM module):
  - `AVAILABLE` (frei) - Ready for booking
  - `RESERVED` (reserviert) - Temporarily allocated
  - `BLOCKED` (blockiert/Fehler) - Manual block or error
  - `WAITING` (warten) - Reuse waiting period
  - `PROCESSING` (in Verarbeitung) - Internal porting
  - `ACTIVATED` (gebucht/vergeben) - Active service
  - `BNETZA` (BNETZA) - Federal authority control

- **Porting States** (PRT module):
  - `PENDING` - Porting request received
  - `VALIDATED` - Request validated
  - `CONFIRMED` - Carrier confirmation
  - `SCHEDULED` - Porting scheduled
  - `EXECUTED` - Porting completed
  - `FAILED` - Porting failed
  - `CANCELLED` - Request cancelled

## Integration Pattern Fields

### `type` Classifications
- **`service_dependency`**: Internal VNRM service calls
- **`external_integration`**: External systems (BNetzA, legacy RNVS, third-party)
- **`event_driven`**: Message Bus message publishing/consuming
- **`database_integration`**: Direct database access (should be exclusive per service)

### `protocol` Values
- **`REST`**: HTTP-based API calls with JSON
- **`gRPC`**: High-performance RPC (rare in current VNRM)
- **`Message Bus`**: Asynchronous messaging via Tardis Horizon
- **`Database`**: Direct PostgreSQL connection
- **`SOAP`**: Legacy protocol (mainly for BNetzA integration)
- **`File`**: File-based integration (SFTP, batch processing)

### `criticality` Levels
- **`CRITICAL`**: Service cannot function without this integration
  - Examples: config-server, database
- **`HIGH`**: Core functionality impacted, but service can degrade gracefully
  - Examples: RDM validation, porting coordination
- **`MEDIUM`**: Feature functionality impacted, core operations continue
  - Examples: monitoring, notification services
- **`LOW`**: Nice-to-have integration, minimal impact if unavailable
  - Examples: analytics, reporting

## Resilience Pattern Fields

### `circuit_breaker.failure_threshold`
- **Typical Values**:
  - Critical services: `5` failures
  - High-priority services: `3` failures
  - Best-effort services: `10` failures
- **Timeout Values**:
  - Fast recovery: `30s`
  - Standard recovery: `60s`
  - Slow recovery: `300s` (5 minutes)

### `retry_policy` Strategies
- **`none`**: No retries (for non-idempotent operations)
- **`fixed_delay`**: Fixed wait between retries
- **`exponential_backoff`**: Increasing delays (2s, 4s, 8s, 16s, ...)
- **Use Cases**:
  - Network timeouts: exponential_backoff
  - Rate limiting: fixed_delay with longer intervals
  - Database deadlocks: exponential_backoff with jitter

## Operational Metrics Fields

### `service_level` Classifications
- **`HA`** (High Availability):
  - Support: 24/7 with 3-hour response time
  - Availability: 99.9%+ uptime requirement
  - Examples: Core transaction services, critical APIs

- **`OT`** (Office Time):
  - Support: Business hours with 3-day response time
  - Availability: 99.5% during business hours
  - Examples: Administrative interfaces, reporting systems

- **`BE`** (Best Effort):
  - Support: Best effort, no guaranteed response time
  - Availability: No specific SLA
  - Examples: Development tools, experimental features

### `availability_target` Formats
- **Format**: `99.9%`, `99.95%`, `99.99%`
- **Downtime Equivalents**:
  - 99.9% = 8.77 hours/year downtime
  - 99.95% = 4.38 hours/year downtime
  - 99.99% = 52.6 minutes/year downtime

## Compliance Requirements

### `GDPR` Requirements
- **`data_encryption`**: Encryption at rest and in transit
- **`audit_trails`**: Complete audit logging for data access/modification
- **`right_to_deletion`**: Data deletion capabilities (often soft delete)
- **`data_minimization`**: Collect only necessary data
- **`consent_management`**: User consent tracking (where applicable)

### `BNetzA` Requirements
- **`number_portability_compliance`**: Full PDA message processing support
- **`audit_trails`**: Regulatory audit logging with 10-year retention
- **`regulatory_reporting`**: Automated compliance reporting capabilities
- **`data_retention`**: Long-term data retention per telecommunications law

### `TKG` Requirements
- **`number_reuse_waiting_period`**: Enforced waiting periods for number reuse
- **`carrier_coordination`**: Proper coordination between telecommunications providers
- **`transparent_pricing`**: Price transparency for number-related services

## Enhancement Opportunity Categories

### `performance` Examples
- "Implement Redis caching for frequent ONKZ lookups"
- "Database query optimization with composite indexes"
- "Connection pooling optimization for high throughput"
- "Implement database read replicas for search operations"

### `modernization` Examples
- "Migrate to Spring Boot 3.x for improved security"
- "Implement reactive programming patterns"
- "Upgrade to Java 21 LTS for performance gains"
- "Add GraphQL API layer for flexible queries"

### `observability` Examples
- "Implement distributed tracing with Jaeger"
- "Add business metrics collection for analytics"
- "Enhanced monitoring dashboards with Grafana"
- "Structured logging with correlation IDs"

### `security` Examples
- "Implement fine-grained RBAC for operations"
- "Add request signing for critical transactions"
- "Implement audit log encryption"
- "Add rate limiting per client/tenant"

### `architecture` Examples
- "Implement CQRS pattern for read/write separation"
- "Add event sourcing for complete history"
- "Implement domain events for decoupling"
- "Add API versioning strategy"

## Validation Guidelines

### Required Field Validation
1. **Service Metadata**: All required fields must be present
2. **API Contracts**: At least one endpoint must be documented
3. **Technology Stack**: Core components (Spring Boot, Java, database) required
4. **Integration Patterns**: Document all external dependencies

### Quality Standards
1. **Completeness**: Document all major APIs and integrations
2. **Accuracy**: Reflect actual implementation, not intended design
3. **Consistency**: Use standard VNRM terminology and patterns
4. **Traceability**: Link analysis to actual code artifacts and configurations

### Common Validation Errors
1. **Missing authentication details** on API endpoints
2. **Incomplete state machine transitions** for entities with states
3. **Missing resilience patterns** for external integrations
4. **Incorrect service level classification** (HA vs OT vs BE)
5. **Missing compliance requirements** for telecommunications services

## Best Practices

### For API Documentation
1. **Use standard HTTP methods** (GET, POST, PUT, PATCH, DELETE)
2. **Include complete request/response schemas** with validation rules
3. **Document all possible status codes** with explanations
4. **Specify authentication and rate limiting** for each endpoint

### For Database Schema
1. **Include all audit columns** following VNRM standards
2. **Document state machines completely** with business rules
3. **Specify indexes and constraints** for performance and data integrity
4. **Use proper PostgreSQL data types** optimized for the use case

### For Integration Patterns
1. **Classify all integrations by criticality** for proper resilience design
2. **Document timeout and retry policies** for each integration
3. **Include compliance requirements** for regulatory integrations
4. **Specify circuit breaker configurations** for critical dependencies

### For Enhancement Opportunities
1. **Be specific and actionable** rather than generic suggestions
2. **Consider operational impact** of proposed changes
3. **Align with VNRM modernization roadmap** and technology standards
4. **Include effort estimates** where possible (small/medium/large)

---

## Test Infrastructure Fields (OPTIONAL - for Phase 11/12 CHANGE mode)

The `test_infrastructure` object captures existing test coverage in the VNRM microservice. This data is used by Phase 11 (system test scenarios) and Phase 12 (unit test generation) to classify test scenarios as REUSE/MODIFY/NEW.

### `test_framework`
- **Purpose**: Document testing frameworks and libraries used
- **Fields**:
  - `unit_testing`: Unit test framework (e.g., "JUnit 5.8.2")
  - `mocking`: Mocking library (e.g., "Mockito 4.x")
  - `integration`: Integration test stack (e.g., "Spring Boot Test + TestContainers")
  - `api_testing`: API test approach (e.g., "MockMvc + WebTestClient")
  - `event_testing`: Event/Message Bus testing (e.g., "EmbeddedMessage Bus")
- **Example**:
```json
"test_framework": {
  "unit_testing": "JUnit 5.9.0",
  "mocking": "Mockito 4.8.0",
  "integration": "Spring Boot Test 2.7.18 + TestContainers 1.17.x",
  "api_testing": "MockMvc",
  "event_testing": "EmbeddedMessage Bus"
}
```

### `test_coverage_metrics`
- **Purpose**: Current test coverage measurements from CI/CD pipeline
- **Fields**:
  - `line_coverage_percent`: Line coverage (0-100)
  - `branch_coverage_percent`: Branch coverage (0-100)
  - `method_coverage_percent`: Method coverage (0-100)
  - `last_measured`: Date coverage was last measured
- **Guidelines**: Extract from JaCoCo reports if available
- **Example**:
```json
"test_coverage_metrics": {
  "line_coverage_percent": 78,
  "branch_coverage_percent": 65,
  "method_coverage_percent": 82,
  "last_measured": "2024-12-01"
}
```

### `test_inventory` (ARRAY)
- **Purpose**: Inventory of existing test classes with production class mapping
- **Required Fields per Entry**:
  - `test_class`: Fully qualified test class name
  - `test_type`: Type of test (unit, integration, e2e, performance, security)
  - `production_class`: Production class being tested
- **Optional Fields per Entry**:
  - `tests_count`: Number of test methods
  - `workflows_covered`: Workflow IDs tested (WF-XXX)
  - `business_rules_tested`: Business rule IDs tested (BR-XXX)
  - `api_endpoints_tested`: API endpoints tested
- **Guidelines**:
  - Scan `src/test/java/**/*Test.java` files
  - Map each test class to its corresponding production class
  - Identify workflows by analyzing test method names and assertions
  - Extract business rule references from comments and test names
- **Example**:
```json
"test_inventory": [
  {
    "test_class": "com.telekom.vnrm.num.CallnumberServiceTest",
    "test_type": "unit",
    "tests_count": 15,
    "production_class": "com.telekom.vnrm.num.CallnumberService",
    "workflows_covered": ["WF-001", "WF-002"],
    "business_rules_tested": ["BR-015", "BR-016", "BR-017"]
  },
  {
    "test_class": "com.telekom.vnrm.num.CallnumberControllerIntegrationTest",
    "test_type": "integration",
    "tests_count": 8,
    "production_class": "com.telekom.vnrm.num.CallnumberController",
    "api_endpoints_tested": ["POST /api/v1/callnumbers", "GET /api/v1/callnumbers/{id}"]
  }
]
```

### `test_patterns`
- **Purpose**: Document testing patterns and conventions used
- **Fields**:
  - `database_setup`: How test database is configured (e.g., "TestContainers PostgreSQL")
  - `fixture_strategy`: Test fixture approach (e.g., "TestDataBuilder pattern")
  - `mocking_strategy`: Mocking conventions (e.g., "Mockito inline mocks")
- **Example**:
```json
"test_patterns": {
  "database_setup": "TestContainers PostgreSQL with Flyway migrations",
  "fixture_strategy": "TestDataBuilder pattern with dedicated fixtures package",
  "mocking_strategy": "Mockito inline mocks for service layer, MockMvc for controllers"
}
```

### `test_utilities` (ARRAY)
- **Purpose**: Reusable test utility classes that can be referenced
- **Fields per Entry**:
  - `utility_class`: Class name
  - `purpose`: What the utility provides
  - `location`: Package/directory location
- **Example**:
```json
"test_utilities": [
  {
    "utility_class": "CallnumberTestDataBuilder",
    "purpose": "Factory for creating Callnumber test fixtures",
    "location": "src/test/java/com/telekom/vnrm/num/util/"
  },
  {
    "utility_class": "Message BusTestHelper",
    "purpose": "Helper for producing/consuming test Message Bus messages",
    "location": "src/test/java/com/telekom/vnrm/common/message_bus/"
  }
]
```

### How Test Inventory is Used

**Phase 11 (System Tests)**:
- Reads `test_infrastructure.test_inventory`
- Classifies scenarios as:
  - **REUSE**: Existing test covers unchanged functionality
  - **MODIFY**: Existing test needs update for Phase 7.1/8.1 changes
  - **NEW**: No existing coverage, new scenario needed

**Phase 12 (Unit Tests)**:
- Reads `test_infrastructure.test_inventory`
- Classifies unit tests as:
  - **REUSE**: Existing unit test covers unchanged component
  - **MODIFY**: Existing test needs update for Phase 7.1 changes
  - **NEW**: No existing test for new component from delta design
