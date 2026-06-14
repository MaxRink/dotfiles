
# Technical Plan Generation Reference

## Your Task

Generate comprehensive technical implementation plan from architecture artifacts.

**Output:** `.migration/<feature>/spec-specification/technical-plan.md`

## Input Context

Your prompt provides:

- Feature name
- `.migration/<feature>/architect/target-architecture.md` (all sections)
- `.migration/<feature>/analysis/analysis.json` (components, dependencies)
- `.migration/<feature>/plan/plan.json` (target_stack, constraints)
- `.migration/<feature>/spec-specification/contracts.md` (previously generated)
- `.migration/<feature>/spec-specification/functional-requirements.md` (previously generated)

## Workflow

### 1. Load Context

Read all input artifacts including previously generated contracts and functional requirements.

### 2. Generate Architecture Overview

From **target-architecture.md Section 1:**

- Architectural style (microservices, modular monolith, etc.)
- Justification for chosen style
- High-level component organization

From **plan.json target_stack:**

- Technology stack table (Layer, Technology, Version, Justification)
- Build system and tooling
- Development environment requirements

### 3. Define Implementation Phases

Analyze component dependencies from analysis.json and architect:

- Identify dependency-free components (Phase 1)
- Identify components with dependencies (later phases)
- Group components by dependency level

For each phase:

- Phase number and name
- Components to implement
- Dependencies on previous phases
- Deliverables
- Risks and mitigation

### 4. Generate Component Specifications

For each component from architect Section 3:

```markdown
### Component Name

**Responsibility:** What business rules it owns (BR IDs)
**API Surface:** Endpoints, methods, message subscriptions (from contracts.md)
**Dependencies:** Internal components and external systems
**Technology Stack:** Language, framework, libraries
**Code Organization:** Package/module structure, layer breakdown
**Business Rules:** BR001, BR002, ... (from functional-requirements.md)
**Data Access:** Entities read/written, database tables, caching
**Testing Requirements:** Unit test coverage targets, integration test scenarios
```

### 5. Document Data Implementation

From **architect Section 4 (Data Architecture):**

- Schema changes (if any) — CREATE TABLE, ALTER TABLE scripts
- Data migration scripts (if needed)
- Data access patterns (repository pattern, DAO, etc.)
- Consistency guarantees (ACID, eventual consistency)

### 6. Document Integration Implementation

From **contracts.md** and **architect Section 5:**

- External system connections (from contracts.md)
- Protocol implementation details
- Client library choices
- Contract preservation strategies (for unchanged systems)
- Error handling and retry logic

### 7. Document Security Implementation

From **architect Section 6:**

- Authentication mechanism (JWT, OAuth, SAML, etc.)
- Authorization model (RBAC, ABAC, etc.)
- Service-to-service security (mTLS, API keys, etc.)
- Data protection (encryption at rest, in transit)
- Security testing approach

### 8. Document Cross-Cutting Implementation

From **architect Section 7:**

- Logging framework and log levels
- Monitoring and metrics (Prometheus, Grafana, etc.)
- Distributed tracing (OpenTelemetry, Jaeger, etc.)
- Error handling patterns (exception hierarchy, error codes)
- Resilience patterns (retry, circuit breaker, timeout, bulkhead)
- Configuration management (environment variables, config server)

### 9. Define Testing Strategy

For each component from functional-requirements.md:

- **Unit Testing:** Framework, coverage target, test patterns
- **Integration Testing:** Scenarios, test data, mocking strategy
- **System Testing:** End-to-end scenarios, performance tests, security tests

### 10. Create Deployment Plan

From **architect Section 9 (Migration Path):**

- Deployment sequence (by phase)
- Environment requirements (dev, staging, prod)
- Deployment automation (CI/CD pipeline)
- Rollback strategy
- Monitoring during deployment

### 11. Pre-Write Validation

Before writing, verify:

- ✓ All components from architect Section 3 have detailed specifications
- ✓ Technology choices match plan.json target_stack exactly
- ✓ No new architectural decisions introduced (follow architect output only)
- ✓ Every BR ID from functional-requirements.md is assigned to exactly one component
- ✓ All external systems from contracts.md appear in Integration Implementation
- ✓ Deployment phases respect component dependency order

## Output Format

```markdown
# Technical Implementation Plan

**Feature:** {feature-name}
**Architectural Style:** {from architect}

## 1. Architecture Overview
### 1.1 Architectural Style
### 1.2 Component Structure
### 1.3 Technology Stack

| Layer | Technology | Version | Justification |
|-------|------------|---------|---------------|

## 2. Implementation Approach
### 2.1 Implementation Phases

**Phase 1: Foundation**
- Components: {list}
- Dependencies: None
- Deliverables: {list}
- Risks: {mitigation}

### 2.2 Implementation Order
### 2.3 Parallel vs Sequential Work

## 3. Component Specifications
## 4. Data Implementation
## 5. Integration Implementation
## 6. Security Implementation
## 7. Cross-Cutting Implementation
## 8. Testing Strategy
## 9. Deployment Plan
```

## Completion

Return to orchestrator:

```text
DONE: technical-plan.md written
- Components specified: N
- Implementation phases: N
- Technology stack: [summary]
- BR assignments: complete
```
