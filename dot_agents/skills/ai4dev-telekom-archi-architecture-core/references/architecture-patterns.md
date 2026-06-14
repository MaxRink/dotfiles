# Architecture Patterns Reference

Use this reference when you need deeper understanding of architecture frameworks, patterns, and principles. Organized by architecture domain.

## Table of Contents
1. [Enterprise Architecture](#enterprise-architecture)
2. [Solution Architecture](#solution-architecture)
3. [System Architecture](#system-architecture)
4. [Cloud Architecture](#cloud-architecture)
5. [Cross-Cutting Concerns](#cross-cutting-concerns)

---

## Enterprise Architecture

### TOGAF (The Open Group Architecture Framework)

**Architecture Development Method (ADM) Phases:**
- **Preliminary** — Establish architecture capability, principles, and governance
- **A: Architecture Vision** — Define scope, stakeholders, and high-level vision
- **B: Business Architecture** — Business processes, capabilities, organization
- **C: Information Systems Architecture** — Application and data architecture
- **D: Technology Architecture** — Infrastructure, platforms, networks
- **E: Opportunities & Solutions** — Identify transition architectures
- **F: Migration Planning** — Sequence implementation projects
- **G: Implementation Governance** — Oversee implementation
- **H: Architecture Change Management** — Manage changes to the architecture

**Architecture Domains:**
1. **Business Architecture** — Strategy, governance, organization, processes
2. **Data Architecture** — Data models, data management, data flows
3. **Application Architecture** — Application systems, interactions, relationships
4. **Technology Architecture** — Hardware, software, networking infrastructure

### ArchiMate Modeling Language

**Layers:**
- **Strategy Layer** — Resources, capabilities, courses of action
- **Business Layer** — Services, processes, functions, roles, events
- **Application Layer** — Components, services, interfaces, data objects
- **Technology Layer** — Nodes, devices, system software, artifacts
- **Physical Layer** — Equipment, facilities, distribution networks
- **Implementation & Migration** — Work packages, deliverables, gaps, plateaus

**Core Relationships:**
- Composition, Aggregation, Assignment, Realization
- Serving, Access, Influence, Association
- Triggering, Flow, Specialization

### Zachman Framework

Six interrogatives (columns) x six perspectives (rows):
- **What** (Data), **How** (Function), **Where** (Network), **Who** (People), **When** (Time), **Why** (Motivation)
- Perspectives: Executive, Business Management, Architect, Engineer, Technician, Enterprise

---

## Solution Architecture

### Microservices Patterns

**Decomposition:**
- Decompose by business capability
- Decompose by subdomain (DDD bounded contexts)
- Strangler fig pattern (gradual migration)

**Communication:**
- Synchronous: REST, gRPC, GraphQL
- Asynchronous: Event-driven (Kafka, RabbitMQ), CQRS, Event Sourcing
- Service mesh (Istio, Linkerd)

**Data Management:**
- Database per service
- Saga pattern (choreography vs orchestration)
- API Composition for queries across services
- CQRS (Command Query Responsibility Segregation)

**Resilience:**
- Circuit breaker
- Bulkhead
- Retry with exponential backoff
- Timeout
- Fallback

**Observability:**
- Distributed tracing (OpenTelemetry)
- Centralized logging (ELK, Loki)
- Metrics (Prometheus, Grafana)
- Health checks

### Event-Driven Architecture

**Patterns:**
- Event notification — Fire and forget
- Event-carried state transfer — Events carry full data
- Event sourcing — Store state as sequence of events
- CQRS — Separate read and write models

**Event Types:**
- Domain events (business-meaningful)
- Integration events (cross-boundary)
- Command events (explicit requests)

### API Architecture

**Styles:**
- REST (resource-oriented, HATEOAS)
- GraphQL (query-driven, schema-first)
- gRPC (binary protocol, contract-first)
- AsyncAPI (event-driven APIs)

**API Gateway Patterns:**
- Routing and load balancing
- Authentication/Authorization
- Rate limiting and throttling
- Request/response transformation
- API versioning strategies

---

## System Architecture

### Clean Architecture (Robert C. Martin)

**Core Principle:** Dependencies point inward. Inner layers know nothing about outer layers.

**Layers (inside-out):**
1. **Entities** — Enterprise business rules, domain objects
   - Pure business logic, no framework dependencies
   - Shared across applications
2. **Use Cases** — Application business rules
   - Orchestrate data flow to/from entities
   - Define application-specific behavior
3. **Interface Adapters** — Convert data between use cases and external formats
   - Controllers, Presenters, Gateways
   - MVC pattern lives here
4. **Frameworks & Drivers** — External tools, DB, UI, web
   - Most volatile, outermost layer
   - "Glue code" and configuration

**The Dependency Rule:** Source code dependencies can only point inward. Nothing in an inner circle can know anything about something in an outer circle.

### Hexagonal Architecture (Ports & Adapters)

**Core Concept:** The application is at the center, surrounded by ports (interfaces) and adapters (implementations).

**Ports:** Defined by the application
- **Driving ports** (primary/inbound) — How the world interacts with the app (e.g., REST API, CLI)
- **Driven ports** (secondary/outbound) — How the app interacts with the world (e.g., database, messaging)

**Adapters:** Implement the ports
- **Driving adapters** — REST controller, GraphQL resolver, CLI handler
- **Driven adapters** — PostgreSQL repository, Kafka producer, HTTP client

### Domain-Driven Design (DDD)

**Strategic Patterns:**
- **Bounded Context** — Explicit boundary within which a domain model applies
- **Ubiquitous Language** — Shared language between developers and domain experts
- **Context Map** — Relationships between bounded contexts
  - Shared Kernel, Customer-Supplier, Conformist, Anti-Corruption Layer, Open Host Service, Published Language

**Tactical Patterns:**
- **Entity** — Identity-based domain object
- **Value Object** — Identity-less, immutable
- **Aggregate** — Cluster of entities with a root entity, consistency boundary
- **Repository** — Abstraction for accessing aggregates
- **Domain Service** — Stateless operations that don't belong to an entity
- **Domain Event** — Something significant that happened in the domain
- **Factory** — Complex object creation

### SOLID Principles in Architecture

- **S** — Single Responsibility: Each module/service has one reason to change
- **O** — Open/Closed: Open for extension, closed for modification
- **L** — Liskov Substitution: Subtypes must be substitutable
- **I** — Interface Segregation: Many specific interfaces over one general
- **D** — Dependency Inversion: Depend on abstractions, not concretions

---

## Cloud Architecture

### AWS Well-Architected Framework (6 Pillars)

1. **Operational Excellence** — Run and monitor systems, continuously improve
2. **Security** — Protect information, systems, assets
3. **Reliability** — Recover from failures, meet demand
4. **Performance Efficiency** — Use resources efficiently
5. **Cost Optimization** — Avoid unnecessary costs
6. **Sustainability** — Minimize environmental impact

### Cloud Design Patterns

**Availability:**
- Health Endpoint Monitoring
- Queue-Based Load Leveling
- Throttling
- Geode (geo-distributed)

**Data Management:**
- Cache-Aside
- CQRS
- Event Sourcing
- Sharding
- Static Content Hosting
- Materialized View

**Messaging:**
- Competing Consumers
- Priority Queue
- Publisher-Subscriber
- Asynchronous Request-Reply
- Claim Check (large messages)

**Security:**
- Federated Identity
- Gatekeeper
- Valet Key (temporary access)

**Reliability:**
- Circuit Breaker
- Compensating Transaction
- Retry
- Deployment Stamps
- Bulkhead

### Multi-Cloud & Hybrid Patterns

- Cloud-bursting
- Distributed deployment
- Edge computing
- Hybrid connectivity (VPN, Direct Connect, ExpressRoute)
- Multi-cloud abstraction layer (Terraform, Pulumi)

### Container & Orchestration

- Container per service
- Sidecar pattern
- Ambassador pattern
- Init container pattern
- Operator pattern (Kubernetes)
- Service mesh (Istio, Linkerd)
- GitOps (ArgoCD, Flux)

---

## Cross-Cutting Concerns

### Security Architecture
- Zero Trust Architecture
- Defense in depth
- Least privilege
- Network segmentation
- Identity and Access Management (IAM)
- Encryption at rest and in transit
- Secret management (Vault, AWS Secrets Manager)

### Observability
- Three pillars: Logs, Metrics, Traces
- OpenTelemetry standard
- SLIs, SLOs, SLAs
- Error budgets
- Alerting strategy

### Data Architecture
- Data mesh (domain-oriented ownership)
- Data lake vs Data warehouse vs Lakehouse
- ETL vs ELT
- Change Data Capture (CDC)
- Schema registry and evolution

### Integration Patterns
- API-led connectivity
- Enterprise Service Bus (legacy)
- Integration Platform as a Service (iPaaS)
- Webhook-based integration
- File-based integration
