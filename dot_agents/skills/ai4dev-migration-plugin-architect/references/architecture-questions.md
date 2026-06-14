# Architecture Questions — Question Bank

Organized question bank for the `/architect` interactive session. Questions adapt based on loaded migration context (plan.json, analysis.json, diagrams).

---

## Category 1: Existing Patterns (Always Asked First)

### Q1 — Organizational Standards

```yaml
id: Q1
category: existing-patterns
question: "Do you have existing architecture patterns or templates to follow?"
required: true
options:
  - label: "Yes — I'll provide reference files/links"
    followup: "Please share the reference files or links."
  - label: "Follow organizational standards (describe)"
    followup: "Describe your organizational architecture standards."
  - label: "No — recommend best practices"
    followup: null
  - label: "Use the same pattern as the current system"
    followup: null
context_usage: |
  If user provides reference files → Read them with Read tool and incorporate
  patterns, naming conventions, and structural decisions into the target design.
```

---

## Category 2: Service Architecture

### Q2 — Architectural Style

```yaml
id: Q2
category: service-architecture
question: "What architectural style should the target use?"
required: true
options:
  - label: "Microservices"
    description: "Independent, separately deployable services organized around business capabilities"
  - label: "Modular monolith"
    description: "Single deployable unit with strong internal module boundaries"
  - label: "Serverless / FaaS"
    description: "Function-as-a-Service with managed infrastructure"
  - label: "Event-driven architecture"
    description: "Loosely coupled components communicating through events"
  - label: "Keep current architecture (refactor in place)"
    description: "Retain the existing structure, modernize internals"
filter: |
  Show all options. Pre-select based on migration_goals if available:
    - If goal mentions "decompose" or "break apart" → highlight Microservices
    - If goal mentions "modernize" without "decompose" → highlight Modular monolith
    - If goal mentions "cloud-native" or "scale to zero" → highlight Serverless
```

### Q3 — Communication Patterns

```yaml
id: Q3
category: service-architecture
question: "How should services/components communicate?"
required: true
multiSelect: true
options:
  - label: "REST (synchronous)"
    description: "Standard HTTP/JSON APIs for request-response interactions"
  - label: "gRPC (synchronous, high-performance)"
    description: "Binary protocol for low-latency service-to-service calls"
  - label: "Message queue / async messaging"
    description: "RabbitMQ, SQS, etc. for asynchronous point-to-point communication"
  - label: "Event bus / pub-sub"
    description: "Kafka, EventBridge, etc. for broadcasting events to multiple consumers"
  - label: "Mixed (specify per integration)"
    description: "Different protocols for different integration points"
context_usage: |
  If Q2 answer is "Keep current architecture" → pre-select based on existing
  communication patterns found in analysis.json control_flows.
```

---

## Category 3: Data Architecture

### Q4 — Data Storage Strategy

```yaml
id: Q4
category: data-architecture
question: "What data storage strategy?"
required: true
options:
  - label: "Own database per service (database-per-service)"
    description: "Each service manages its own data store for independence"
  - label: "Shared database (existing)"
    description: "Services share the current database — from plan constraints"
  - label: "Event sourcing + CQRS"
    description: "Store events as source of truth, separate read/write models"
  - label: "Polyglot persistence"
    description: "Different database technologies for different services based on fit"
  - label: "Keep current (unchanged)"
    description: "Retain existing database structure per plan constraints"
filter: |
  If constraints.unchanged includes "database_schema" → pre-select "Keep current".
  If Q2 is "Microservices" → highlight "Own database per service".
  If Q2 is "Event-driven" → highlight "Event sourcing + CQRS".
```

### Q5 — Data Migration Approach

```yaml
id: Q5
category: data-architecture
question: "Data migration approach?"
required: false
skip_condition: "constraints.unchanged includes 'database_schema'"
options:
  - label: "Big bang migration"
    description: "Migrate all data in a single cutover window"
  - label: "Strangler fig (gradual)"
    description: "Incrementally redirect data access to the new system"
  - label: "Dual-write during transition"
    description: "Write to both old and new systems during migration period"
  - label: "Event-driven sync"
    description: "Use change data capture or events to sync between old and new"
  - label: "Not applicable (schema unchanged)"
    description: "No data migration needed"
```

---

## Category 4: Security & Cross-Cutting

### Q6 — Authentication / Authorization

```yaml
id: Q6
category: security-cross-cutting
question: "Authentication/authorization approach?"
required: true
options:
  - label: "Keep current auth (preserve integration)"
    description: "Retain the existing authentication mechanism"
  - label: "OAuth 2.0 / OIDC"
    description: "Standard token-based auth via identity provider"
  - label: "JWT-based stateless auth"
    description: "Self-contained tokens for stateless service authentication"
  - label: "API key / service-to-service auth"
    description: "Simple key-based auth for internal service communication"
  - label: "mTLS for service mesh"
    description: "Mutual TLS for zero-trust service-to-service security"
filter: |
  Pre-fill from constraints.integration if OAuth/IdP references are present.
  If constraints.unchanged includes auth-related items → pre-select "Keep current".
```

### Q7 — Cross-Cutting Concerns

```yaml
id: Q7
category: security-cross-cutting
question: "What cross-cutting concerns need architectural support?"
required: true
multiSelect: true
options:
  - label: "Logging / observability"
    description: "Structured logging, metrics, dashboards"
  - label: "Distributed tracing"
    description: "End-to-end request tracing across services (OpenTelemetry, Jaeger)"
  - label: "Circuit breakers / resilience"
    description: "Fault tolerance patterns (retry, circuit breaker, bulkhead)"
  - label: "API gateway / rate limiting"
    description: "Centralized API management, throttling, routing"
  - label: "Configuration management"
    description: "Externalized config (Consul, Spring Cloud Config, AWS Parameter Store)"
  - label: "Feature flags"
    description: "Runtime feature toggling for gradual rollout"
context_usage: |
  If Q2 is "Microservices" → pre-select "Distributed tracing" and "Circuit breakers".
  If Q2 is "Serverless" → pre-select "Logging / observability".
```

---

## Category 5: Deployment & Operations

### Q8 — Deployment Model

```yaml
id: Q8
category: deployment-operations
question: "Target deployment model?"
required: true
options:
  - label: "Kubernetes / containers"
    description: "Containerized workloads orchestrated by Kubernetes"
  - label: "Serverless (AWS Lambda, Azure Functions, etc.)"
    description: "Managed functions with auto-scaling and pay-per-use"
  - label: "Traditional VM / bare metal"
    description: "Virtual machines or physical servers"
  - label: "PaaS (Heroku, App Engine, etc.)"
    description: "Platform-managed deployment with minimal infrastructure concern"
  - label: "Same as current"
    description: "Keep the existing deployment model"
filter: |
  If Q2 is "Serverless" → pre-select "Serverless".
  If Q2 is "Microservices" → highlight "Kubernetes / containers".
```

### Q9 — Additional Requirements

```yaml
id: Q9
category: deployment-operations
question: "Any additional architectural requirements or preferences?"
required: false
freeText: true
context_usage: |
  Capture any requirements not covered by previous questions.
  Feed directly into the target architecture document as additional constraints.
```

---

## Adaptive Questions

These are **conditionally asked** based on the loaded context. They appear after the core questions if their trigger condition is met.

### AQ1 — Performance Targets

```yaml
id: AQ1
trigger: "focus_areas includes 'performance'"
question: "Any specific performance targets (latency, throughput)?"
freeText: true
context_usage: |
  Include performance requirements in the Architecture Overview and
  Component Design sections. May influence technology recommendations.
```

### AQ2 — Transaction Consistency

```yaml
id: AQ2
trigger: "focus_areas includes 'data_integrity'"
question: "Transaction consistency model?"
options:
  - label: "ACID (strong consistency)"
    description: "Traditional database transactions — all or nothing"
  - label: "Eventual consistency"
    description: "Systems converge to consistent state over time"
  - label: "Saga pattern"
    description: "Distributed transactions via compensating actions"
  - label: "Mixed (per use case)"
    description: "Different consistency models for different operations"
```

### AQ3 — Module Decomposition

```yaml
id: AQ3
trigger: "scope.include has multiple modules (>1 path)"
question: "Should modules become separate services or stay in one deployable?"
options:
  - label: "Separate services (one per module)"
    description: "Each module becomes its own independently deployable service"
  - label: "Grouped services (related modules together)"
    description: "Group related modules into a smaller number of services"
  - label: "Single deployable (modular monolith)"
    description: "Keep all modules in one deployable with clear internal boundaries"
  - label: "Decide per module"
    description: "I'll specify the decomposition strategy for each module"
```

### AQ4 — Business Rules Engine

```yaml
id: AQ4
trigger: "analysis.json has >10 business rules"
question: "Should business rules be centralized (rules engine) or embedded in services?"
options:
  - label: "Centralized rules engine"
    description: "Drools, AWS Rules Engine — rules managed separately from code"
  - label: "Embedded in owning service"
    description: "Each service owns and enforces its own business rules in code"
  - label: "Shared library"
    description: "Business rules in a common library consumed by services"
  - label: "Mixed approach"
    description: "Critical rules centralized, simple validations embedded"
```

### AQ5 — Integration Layer

```yaml
id: AQ5
trigger: "constraints.integration.systems has >2 entries"
question: "Integration layer approach for external systems?"
options:
  - label: "API gateway"
    description: "Centralized entry point for all external integrations"
  - label: "Integration bus / ESB"
    description: "Enterprise service bus for message routing and transformation"
  - label: "Direct point-to-point"
    description: "Each service connects directly to its external dependencies"
  - label: "Anti-corruption layer per integration"
    description: "Dedicated adapter layer isolating each external system"
```

---

## Diagram Questions (Step 5)

### DQ1 — Target Diagrams

```yaml
id: DQ1
category: diagrams
question: "Would you like diagrams of the target architecture?"
required: true
options:
  - label: "Yes — all diagram types (component, sequence, class/entity)"
    action: "Generate all target-state diagrams"
  - label: "Yes — component diagram only (high-level overview)"
    action: "Generate target component diagram only"
  - label: "Yes — let me pick specific types"
    action: "Present sub-selection of diagram types"
    followup:
      question: "Which diagram types?"
      multiSelect: true
      options:
        - "Component / C4 diagram"
        - "Sequence diagrams (interaction flows)"
        - "Class / entity diagrams (domain model)"
        - "Before/after comparison diagrams"
  - label: "No — text document is sufficient"
    action: "Skip diagram generation"
```

---

## Review Questions (Step 6)

### RQ1 — Architecture Review

```yaml
id: RQ1
category: review
question: "Review the target architecture. What would you like to do?"
required: true
options:
  - label: "Approve — save as-is"
    action: "Proceed to save artifacts"
  - label: "Needs changes — I'll describe what to adjust"
    action: "Accept free-text feedback, regenerate affected sections"
  - label: "Regenerate section (specify which)"
    action: "Ask which section to regenerate"
  - label: "Add more detail to a specific component"
    action: "Ask which component needs more detail"
```
