---
title: Target Architecture — order-migration
feature: order-migration
generated_at: "2026-02-19T14:30:00Z"
architectural_style: microservices
sources:
  - plan.json
  - analysis.json
  - diagrams (component, sequence, ERD available)
  - user decisions from interactive session
---

<!-- markdownlint-disable MD025 -->
# Target Architecture: order-migration

## 1. Executive Summary

**Migration Goal:** Decompose monolithic order management system into independently deployable microservices to improve scalability, team autonomy, and deployment frequency.

**Architectural Style:** Microservices — selected to enable independent scaling of order processing (high throughput)
and payment processing (strict compliance), and to allow separate teams to own and deploy each service.

**Key Decisions:**

- **Service Architecture**: Microservices with REST for synchronous and Kafka for async communication
- **Data**: Database-per-service with strangler fig migration approach
- **Auth**: OAuth 2.0 / OIDC preserving existing identity provider integration
- **Deployment**: Kubernetes containers with GitOps-based delivery

**Scope:** Targeted migration covering 4 modules (order, payment, inventory, notification)

---

## 2. Architecture Overview

### 2.1 Chosen Style & Justification

Microservices architecture with domain-driven service boundaries.

**Why this style:**
The existing monolith has clearly separated business domains (order management, payment processing, inventory, notifications)
that have different scaling requirements. Order processing experiences 10x traffic spikes during sales events
while payment processing requires strict PCI compliance isolation. Microservices enable independent scaling,
technology choice per service, and team autonomy aligned with the organization's shift to product teams.

### 2.2 High-Level Component Structure

The target system comprises 5 core services, an API gateway, and supporting infrastructure:

- **Order Service** — order lifecycle management, cart operations
- **Payment Service** — payment processing, refunds, PCI-compliant isolation
- **Inventory Service** — stock management, reservations
- **Notification Service** — email, SMS, push notifications
- **API Gateway** — routing, rate limiting, authentication

> See: [Target Component Diagram](diagrams/target-component-diagram.md)

### 2.3 Communication Patterns

| From | To | Protocol | Pattern | Notes |
|------|----|----------|---------|-------|
| API Gateway | Order Service | REST | Synchronous | Customer-facing APIs |
| Order Service | Payment Service | REST | Synchronous | Payment processing requires immediate response |
| Order Service | Inventory Service | REST | Synchronous | Stock check before order confirmation |
| Order Service | Notification Service | Kafka | Async event | Order status change events |
| Payment Service | Order Service | Kafka | Async event | Payment completion/failure callbacks |
| Inventory Service | Order Service | Kafka | Async event | Stock reservation expiry |

---

## 3. Component Design

### 3.1. Order Service

**Responsibility:** Manages the complete order lifecycle including cart operations, checkout, order status tracking, and fulfillment coordination.

**Business Rules Owned:**

- `BR001`: Order validation — customer exists, items valid, quantities > 0, total > 0
- `BR002`: Cart operations — add, remove, update quantities with stock availability check
- `BR003`: Order state transitions — DRAFT → PENDING → CONFIRMED → SHIPPED → DELIVERED (or CANCELLED)
- `BR007`: Order cancellation — allowed only in DRAFT or PENDING states
- `BR012`: Minimum order value — orders must meet $10 minimum

**API Surface:**

| Method | Endpoint / Message | Description |
|--------|--------------------|-------------|
| POST | /api/v1/orders | Create new order |
| GET | /api/v1/orders/{id} | Get order details |
| PUT | /api/v1/orders/{id}/status | Update order status |
| DELETE | /api/v1/orders/{id} | Cancel order |
| POST | /api/v1/cart/items | Add item to cart |
| Event | order.created | Published when order is confirmed |
| Event | order.cancelled | Published when order is cancelled |

**Dependencies:**

- Internal: Payment Service (REST), Inventory Service (REST), Notification Service (Kafka)
- External: None

**Technology Recommendation:** Spring Boot 3.x (Java 21), PostgreSQL, Spring Data JPA

### 3.2. Payment Service

**Responsibility:** Handles all payment processing including authorization, capture, refunds, and payment status tracking. Runs in PCI-compliant isolation.

**Business Rules Owned:**

- `BR004`: Payment validation — valid payment method, sufficient funds check
- `BR005`: Retry logic — up to 3 retries on transient payment gateway failures
- `BR006`: Refund processing — full or partial refunds with audit trail
- `BR013`: Payment timeout — cancel payment attempt after 30s gateway timeout

**API Surface:**

| Method | Endpoint / Message | Description |
|--------|--------------------|-------------|
| POST | /api/v1/payments | Process payment |
| POST | /api/v1/payments/{id}/refund | Initiate refund |
| GET | /api/v1/payments/{id}/status | Get payment status |
| Event | payment.completed | Published on successful payment |
| Event | payment.failed | Published on payment failure |

**Dependencies:**

- Internal: None
- External: Stripe API (payment gateway)

**Technology Recommendation:** Spring Boot 3.x (Java 21), PostgreSQL, Resilience4j for circuit breaker

### 3.3. Inventory Service

**Responsibility:** Manages product stock levels, reservations during checkout, and stock replenishment events.

**Business Rules Owned:**

- `BR008`: Stock availability — check before order confirmation
- `BR009`: Stock reservation — reserve inventory during checkout (15-minute TTL)
- `BR010`: Reservation expiry — auto-release reserved stock after timeout
- `BR014`: Low stock alerts — trigger notification when stock < threshold

**API Surface:**

| Method | Endpoint / Message | Description |
|--------|--------------------|-------------|
| GET | /api/v1/inventory/{productId} | Check stock level |
| POST | /api/v1/inventory/reserve | Reserve stock for order |
| POST | /api/v1/inventory/release | Release reserved stock |
| Event | inventory.low-stock | Published when stock below threshold |
| Event | inventory.reservation-expired | Published on reservation timeout |

**Dependencies:**

- Internal: Notification Service (Kafka)
- External: None

**Technology Recommendation:** Spring Boot 3.x (Java 21), PostgreSQL, Redis (reservation TTL management)

### 3.4. Notification Service

**Responsibility:** Sends notifications (email, SMS, push) triggered by domain events from other services.

**Business Rules Owned:**

- `BR011`: Notification routing — determine channel (email/SMS/push) based on customer preferences
- `BR015`: Rate limiting — max 5 notifications per customer per hour

**API Surface:**

| Method | Endpoint / Message | Description |
|--------|--------------------|-------------|
| Consumer | order.created | Send order confirmation |
| Consumer | payment.completed | Send payment receipt |
| Consumer | inventory.low-stock | Alert operations team |
| POST | /api/v1/notifications/send | Direct notification (internal) |

**Dependencies:**

- Internal: None
- External: SendGrid (email), Twilio (SMS)

**Technology Recommendation:** NestJS (TypeScript), MongoDB (notification logs), Bull (job queue)

---

## 4. Data Architecture

### 4.1 Storage Strategy

Database-per-service pattern. Each service owns its database and schema. No cross-service direct database access — all data sharing via APIs or events.

| Service | Database | Rationale |
|---------|----------|-----------|
| Order Service | PostgreSQL | Complex queries, ACID transactions |
| Payment Service | PostgreSQL | Audit trail, compliance requirements |
| Inventory Service | PostgreSQL + Redis | Transactional stock, Redis for reservation TTLs |
| Notification Service | MongoDB | Flexible schema for notification templates/logs |

### 4.2 Schema Changes

| Entity | Change Type | Description | Constraint Notes |
|--------|-------------|-------------|------------------|
| Order | Split | Extract payment fields to Payment Service | Preserve order_id FK references |
| Payment | New table | Standalone payment records with order reference | New schema in Payment DB |
| Inventory | Migrate | Move from shared schema to own database | Preserve product_id references |
| Notification | New collection | New schema for notification logs | No legacy dependency |

### 4.3 Data Migration Approach

**Strangler fig (gradual):** Migrate one service at a time. During transition, the legacy monolith and new services coexist. Data flows are redirected incrementally:

1. Phase 1: Notification Service (no legacy data dependency)
2. Phase 2: Inventory Service (copy stock data, dual-read during transition)
3. Phase 3: Payment Service (dual-write for new payments, migrate historical)
4. Phase 4: Order Service (final cutover, retire monolith)

### 4.4 Consistency Model

- **Within a service**: ACID transactions (PostgreSQL)
- **Across services**: Eventual consistency via Saga pattern
- **Order → Payment flow**: Orchestration saga managed by Order Service
- **Compensation**: On payment failure, Order Service reverts to PAYMENT_FAILED and releases inventory reservation

---

## 5. Integration Design

### 5.1 External System Connections

| External System | Protocol | Direction | Contract | Preservation Strategy |
|----------------|----------|-----------|----------|-----------------------|
| Stripe API | REST/HTTPS | Outbound | Stripe API v2023-10 | Wrapped in Payment Service adapter |
| SendGrid | REST/HTTPS | Outbound | SendGrid v3 | Wrapped in Notification Service |
| Twilio | REST/HTTPS | Outbound | Twilio API 2010 | Wrapped in Notification Service |
| Identity Provider | OAuth 2.0 | Inbound | OIDC standard | API Gateway handles token validation |

### 5.2 Communication Protocols

- **External → API Gateway**: HTTPS/REST with OAuth 2.0 bearer tokens
- **API Gateway → Services**: REST over internal network (mTLS optional)
- **Service → Service (sync)**: REST with circuit breaker
- **Service → Service (async)**: Kafka with JSON payloads and schema version headers

### 5.3 Contract Preservation

All existing external API contracts are preserved at the API Gateway level.
Internal service APIs are new but map 1:1 to existing business operations.
Client-facing endpoints maintain backward compatibility; new versioned endpoints introduced under `/api/v1/`.

---

## 6. Security Architecture

### 6.1 Authentication & Authorization

**OAuth 2.0 / OIDC** via existing identity provider:

- API Gateway validates JWT tokens on every inbound request
- Token claims carry user roles and permissions
- Services trust tokens validated by the gateway (no re-validation)

### 6.2 Service-to-Service Security

- Internal REST calls use service-account JWT tokens (client_credentials flow)
- Kafka messages include originating service identity in headers
- Network policy restricts inter-service communication to defined routes

### 6.3 Data Protection

- PII encrypted at rest (PostgreSQL TDE, MongoDB encryption)
- Payment data isolated in Payment Service (PCI DSS scope reduction)
- Audit logs for all payment and order state changes

---

## 7. Cross-Cutting Concerns

### 7.1. Logging / Observability

Structured JSON logging with correlation IDs propagated across all services.

**Pattern:** ELK stack (Elasticsearch, Logstash, Kibana) or Grafana Loki
**Technology:** OpenTelemetry SDK for instrumentation, Prometheus for metrics, Grafana for dashboards

### 7.2. Distributed Tracing

End-to-end request tracing across synchronous and asynchronous boundaries.

**Pattern:** OpenTelemetry-based distributed tracing with context propagation
**Technology:** Jaeger or Grafana Tempo for trace storage and visualization

### 7.3. Circuit Breakers / Resilience

Fault tolerance for all inter-service REST calls.

**Pattern:** Circuit breaker, retry with exponential backoff, bulkhead isolation
**Technology:** Resilience4j (Java services), custom middleware (NestJS)

### 7.4. API Gateway / Rate Limiting

Centralized API management for all external-facing endpoints.

**Pattern:** API Gateway with rate limiting per client/tier, request routing, and response caching
**Technology:** Kong or AWS API Gateway

---

## 8. Migration Path

### 8.1 Recommended Migration Sequence

1. **Phase 1 — Infrastructure Setup**: Kubernetes cluster, Kafka, observability stack
   - Components: Infrastructure only
   - Duration estimate: 2 weeks
   - Dependencies: None

2. **Phase 2 — Notification Service**: Lowest coupling, no legacy data
   - Components: Notification Service + Kafka consumers
   - Duration estimate: 2 weeks
   - Dependencies: Kafka infrastructure

3. **Phase 3 — Inventory Service**: Moderate coupling, clear data boundary
   - Components: Inventory Service + data migration
   - Duration estimate: 3 weeks
   - Dependencies: Phase 1 infrastructure

4. **Phase 4 — Payment Service**: PCI isolation, external integration
   - Components: Payment Service + Stripe adapter + data migration
   - Duration estimate: 3 weeks
   - Dependencies: Phase 1 infrastructure

5. **Phase 5 — Order Service + API Gateway**: Core service, highest coupling
   - Components: Order Service + API Gateway + saga orchestration
   - Duration estimate: 4 weeks
   - Dependencies: Phases 2-4 complete

6. **Phase 6 — Cutover & Decommission**: Retire monolith
   - Components: Traffic switch, monitoring, monolith shutdown
   - Duration estimate: 2 weeks
   - Dependencies: All phases complete

### 8.2 Risk Areas

| Risk | Source | Mitigation | Priority |
|------|--------|------------|----------|
| Data consistency during transition | focus: data_integrity | Saga pattern + compensating transactions | High |
| Payment processing downtime | focus: availability | Blue-green deployment for Payment Service | High |
| Performance regression | focus: performance | Load testing each service before cutover | Medium |
| Integration contract breaks | constraints: Stripe API | Anti-corruption layer in Payment Service | Medium |

### 8.3 Rollback Strategy

Each phase has an independent rollback:

- **Traffic routing**: API Gateway can redirect traffic back to monolith endpoints
- **Data**: Dual-write during transition allows fallback to legacy database
- **Full rollback**: Monolith remains operational until Phase 6; any phase failure reverts to monolith for affected service

---

## 9. Decision Log

| # | Decision | Options Considered | Chosen | Rationale |
|---|----------|--------------------|--------|-----------|
| 1 | Organizational patterns | Reference files, org standards, best practices, keep current | No — recommend best practices | No existing architecture standards documented |
| 2 | Architectural style | Microservices, modular monolith, serverless, event-driven, refactor | Microservices | Independent scaling needs, team autonomy, PCI isolation |
| 3 | Communication patterns | REST, gRPC, message queue, event bus, mixed | REST + Kafka (mixed) | REST for sync flows, Kafka for async events |
| 4 | Data storage | DB-per-service, shared, event sourcing, polyglot, keep current | Database-per-service | Service independence, PCI compliance isolation |
| 5 | Data migration | Big bang, strangler fig, dual-write, event sync | Strangler fig (gradual) | Lower risk, incremental validation |
| 6 | Authentication | Keep current, OAuth 2.0, JWT, API key, mTLS | OAuth 2.0 / OIDC | Preserve existing IdP, industry standard |
| 7 | Cross-cutting | Logging, tracing, circuit breakers, API gateway, config, feature flags | Logging, tracing, circuit breakers, API gateway | Essential for microservices operations |
| 8 | Deployment | Kubernetes, serverless, VM, PaaS, same | Kubernetes / containers | Team Kubernetes expertise, scaling flexibility |
| 9 | Additional requirements | Free text | 99.9% uptime SLA, max 200ms p95 latency | Business-critical order processing |

---

## 10. Target Diagrams

### Target Component Diagram

> [target-component-diagram.md](diagrams/target-component-diagram.md)

### Target Sequence Diagrams

> [target-sequence-diagram.md](diagrams/target-sequence-diagram.md)

### Target Class/Entity Diagrams

> [target-class-entity-diagram.md](diagrams/target-class-entity-diagram.md)
