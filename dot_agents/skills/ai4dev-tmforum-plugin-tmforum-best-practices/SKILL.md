---
name: ai4dev-tmforum-plugin-tmforum-best-practices
description: TM Forum implementation best practices, patterns, and recommendations for telecommunications architecture. Use this skill when seeking implementation guidance, design patterns, best practices for TMF APIs, ODA components, or overall TM Forum adoption strategies.
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/tmforum-plugin/skills/tmforum-best-practices by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# TM Forum Best Practices

## Overview

This skill provides best practices, patterns, and recommendations for implementing TM Forum standards in telecommunications systems.

## When to Use This Skill

Use when seeking implementation guidance, architectural patterns, TMF API best practices, ODA design recommendations, or TM Forum adoption strategies.

## API Implementation Best Practices

### 1. Start Small, Scale Progressively

- Begin with 5-10 core APIs relevant to your domain
- Don't try to implement all 93+ APIs at once
- Focus on high-value business capabilities first

### 2. Prioritize by Business Value

**High Priority**: TMF620 (Catalog), TMF622 (Ordering), TMF629 (Customer), TMF678 (Billing)
**Medium Priority**: TMF638 (Service Inventory), TMF621 (Trouble Tickets)
**Lower Priority**: Specialized APIs as needed

### 3. Maintain Semantic Compliance

- Use SID-aligned data models
- Follow TMF attribute naming conventions
- Extend via `characteristic` arrays, not custom attributes
- Document any deviations for interoperability

### 4. Design for Performance

- Implement caching for reference data (catalogs, specs)
- Use pagination for large result sets
- Leverage async patterns for long operations
- Consider read replicas for query-heavy APIs

### 5. Implement Proper Versioning

- Use semantic versioning (v5.0.0, v5.1.0)
- Maintain backward compatibility within major versions
- Deprecate gracefully with 6-12 month notice
- Support multiple API versions during transition

## ODA Component Best Practices

### 1. Clear Bounded Contexts

- One component = one business capability
- Avoid overly fine-grained components (nano-services)
- Avoid overly coarse components (mini-monoliths)
- Follow Domain-Driven Design (DDD) principles

### 2. Data Ownership

- Database per component (no shared databases)
- Each component owns its data
- Use events for cross-component data consistency
- Implement saga pattern for distributed transactions

### 3. API-First Design

- Define OpenAPI specs before implementation
- Use contract testing (Pact, Spring Cloud Contract)
- Version APIs independently from implementation
- Document breaking changes clearly

### 4. Event-Driven Patterns

- Publish events for all state changes
- Use event sourcing for audit trails
- Implement idempotent event handlers
- Plan for event replay and recovery

### 5. Operational Excellence

- Comprehensive logging (structured JSON)
- Metrics for all critical paths (Prometheus)
- Distributed tracing (Jaeger/Zipkin)
- Health checks and readiness probes
- Graceful shutdown handling

## Security Best Practices

### 1. Authentication & Authorization

- OAuth2/OpenID Connect for authentication
- JWT tokens with short expiration
- RBAC for role-based access
- Fine-grained authorization at API operations

### 2. Data Protection

- TLS 1.2+ for all API calls
- Encrypt sensitive data at rest
- Mask PII in logs and metrics
- Implement data retention policies

### 3. API Security

- Rate limiting per client/user
- Input validation on all requests
- SQL injection prevention
- XSS protection
- CSRF tokens for state-changing operations

## Integration Patterns

### Pattern 1: Synchronous Request-Response

**When to Use**: Immediate response needed, simple CRUD operations

**Example**: Product catalog browsing, customer lookups

**Best Practices**:

- Implement timeouts (2-5 seconds)
- Use circuit breakers (Hystrix, Resilience4j)
- Provide fallback responses
- Cache when possible

### Pattern 2: Asynchronous Event-Driven

**When to Use**: Long-running operations, loose coupling needed

**Example**: Order fulfillment, service provisioning

**Best Practices**:

- Publish events immediately after state change
- Use durable event bus (Kafka)
- Implement idempotent consumers
- Handle poison messages

### Pattern 3: Hub-Based Notifications

**When to Use**: Clients need real-time updates

**Example**: Order state changes, alarm notifications

**Best Practices**:

- Implement webhook registration
- Retry failed notifications with exponential backoff
- Support filtering at subscription time

### Pattern 4: API Composition/Aggregation

**When to Use**: Client needs data from multiple services

**Example**: Customer 360 view

**Best Practices**:

- Use BFF (Backend for Frontend) pattern
- Implement GraphQL for flexible queries
- Cache composite results
- Fail gracefully if one service is down

## Migration Strategies

### Strategy 1: Greenfield (New Systems)

- Start with ODA architecture
- Design with TMF APIs from day one
- Use SID for data modeling
- Map processes to eTOM

### Strategy 2: Brownfield (Legacy Modernization)

**Strangler Fig Pattern**:

1. Assess current architecture
2. Identify bounded contexts
3. Extract one capability as ODA component
4. Route traffic through API gateway
5. Gradually shift traffic
6. Decommission legacy when fully migrated

**Best Practices**:

- Start with high-value, low-risk capabilities
- Implement anti-corruption layer
- Sync data during coexistence
- Monitor both old and new systems

### Strategy 3: Hybrid Approach

- Modernize customer-facing systems first (web, mobile)
- Keep stable backend systems as-is temporarily
- Use API gateway for integration
- Migrate backend over time

## Common Pitfalls to Avoid

### 1. Over-Engineering

❌ Implementing all 93 APIs
✅ Implement 5-10 core APIs first

### 2. Ignoring Semantics

❌ Using TMF API names with custom data models
✅ Align data models with SID

### 3. Tight Coupling

❌ Shared databases between components
✅ Database per component + events

### 4. Premature Optimization

❌ Complex caching before measuring performance
✅ Measure first, optimize bottlenecks

### 5. Neglecting Operations

❌ No logging, metrics, or monitoring
✅ Observability from day one

### 6. Skipping Documentation

❌ No API documentation or examples
✅ OpenAPI specs + examples for all APIs

## Testing Strategies

### 1. Unit Tests

- Test business logic in isolation
- Mock external dependencies
- Aim for 80%+ code coverage

### 2. Contract Tests

- Validate API contracts (Pact)
- Test consumer-provider compatibility
- Run on every commit

### 3. Integration Tests

- Test component integration with real dependencies
- Use testcontainers for databases
- Test happy paths and error scenarios

### 4. End-to-End Tests

- Test complete business workflows
- Validate cross-component scenarios
- Run in staging environment

### 5. Performance Tests

- Load testing for scalability
- Stress testing for breaking points
- Endurance testing for stability

## Governance & Standards

### 1. API Governance

- Centralized API registry
- API design reviews
- Standard error formats
- Deprecation policies

### 2. Data Governance

- Data ownership matrix
- Data quality standards
- Master data management
- Data lineage tracking

### 3. Security Governance

- Security reviews for all APIs
- Penetration testing
- Vulnerability scanning
- Compliance audits (GDPR, PCI DSS)

## Resources

### references/implementation_patterns.md

Detailed implementation patterns with code examples.

### references/migration_guide.md

Step-by-step guide for migrating legacy systems to TM Forum standards.

### references/common_pitfalls.md

Common mistakes and how to avoid them.
