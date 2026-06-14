# Pattern Catalog — Common Target Architecture Patterns

Reference catalog of architectural patterns for use during the `/architect` interactive session.
The architect agent references this catalog when the user selects an architectural style
or when recommending best practices.

---

## 1. Microservices

### Overview

Independently deployable services organized around business capabilities. Each service owns its data, runs in its own process, and communicates over lightweight protocols.

### When to Use

- Large teams that need independent deployment cycles
- Different parts of the system have different scaling requirements
- Business domains are well-understood and loosely coupled
- Organization wants technology heterogeneity (different languages/frameworks per service)

### Key Characteristics

| Aspect | Approach |
|--------|----------|
| Deployment | Independent per service |
| Data | Database-per-service (strong ownership) |
| Communication | REST, gRPC, async messaging |
| Scaling | Per-service horizontal scaling |
| Team structure | One team per service or bounded context |

### Common Components

```text
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  API Gateway │────▶│ Service A   │────▶│ Service B   │
│  (routing)   │     │ + own DB    │     │ + own DB    │
└─────────────┘     └─────────────┘     └─────────────┘
       │                    │                    │
       │             ┌──────▼──────┐      ┌──────▼──────┐
       │             │  Message    │      │  Message    │
       └────────────▶│  Broker     │◀─────│  Broker     │
                     └─────────────┘      └─────────────┘
```

### Patterns to Include

- **API Gateway**: Centralized routing, auth, rate limiting
- **Service Discovery**: Consul, Eureka, or DNS-based
- **Circuit Breaker**: Resilience4j, Hystrix, Polly
- **Saga Pattern**: Distributed transactions via compensating actions
- **Event Sourcing**: Optional — store state changes as events

### Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Distributed complexity | Start with fewer, coarser services; split later |
| Data consistency | Saga pattern or eventual consistency |
| Network latency | gRPC for internal, async where possible |
| Operational overhead | Kubernetes + GitOps + observability from day one |

---

## 2. Modular Monolith

### Overview

Single deployable unit with strong internal module boundaries. Modules communicate through well-defined internal APIs, not direct method calls. Can be decomposed into microservices later.

### When to Use

- Small to medium teams
- Business domains are not yet fully understood
- Deployment simplicity is valued
- Starting a migration — modular monolith as stepping stone to microservices
- Need strong consistency guarantees (shared database transactions)

### Key Characteristics

| Aspect | Approach |
|--------|----------|
| Deployment | Single deployable (one artifact) |
| Data | Shared database with schema-per-module or table ownership |
| Communication | Internal APIs (in-process), event bus optional |
| Scaling | Horizontal scaling of the entire application |
| Team structure | Module ownership per team |

### Common Components

```text
┌─────────────────────────────────────────┐
│              Modular Monolith            │
│  ┌──────────┐ ┌──────────┐ ┌─────────┐ │
│  │ Module A  │ │ Module B │ │Module C │ │
│  │ (public   │ │ (public  │ │(public  │ │
│  │  API)     │ │  API)    │ │ API)    │ │
│  └────┬─────┘ └────┬─────┘ └───┬─────┘ │
│       │             │            │       │
│  ┌────▼─────────────▼────────────▼─────┐ │
│  │         Internal Event Bus          │ │
│  └─────────────────────────────────────┘ │
│       │             │            │       │
│  ┌────▼─────┐ ┌────▼─────┐ ┌───▼─────┐ │
│  │ Schema A │ │ Schema B │ │Schema C │ │
│  └──────────┘ └──────────┘ └─────────┘ │
│         ┌──── Shared Database ────┐     │
└─────────────────────────────────────────┘
```

### Patterns to Include

- **Module API boundary**: Each module exposes a public interface; internal classes are package-private
- **Event bus**: In-process event bus (Spring Events, MediatR) for decoupled communication
- **Schema ownership**: Each module owns its tables; cross-module joins prohibited
- **Anti-corruption layer**: Adapter classes between modules prevent tight coupling

### Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Module boundaries erode over time | Enforce via ArchUnit, module-info.java, or build tool constraints |
| Scaling limitations | Identify hot modules early; plan extraction path |
| Deployment coupling | Feature flags for independent module releases |

---

## 3. Serverless / FaaS

### Overview

Functions-as-a-Service with fully managed infrastructure. Each function handles a single responsibility, triggered by events (HTTP, queue, schedule, etc.).

### When to Use

- Highly variable or unpredictable workloads
- Cost optimization (pay-per-invocation)
- Event-driven processing pipelines
- Simple CRUD APIs with low latency requirements
- Rapid prototyping

### Key Characteristics

| Aspect | Approach |
|--------|----------|
| Deployment | Per-function or per-stack (SAM, Serverless Framework, CDK) |
| Data | Managed services (DynamoDB, Aurora Serverless, Cosmos DB) |
| Communication | Events (API Gateway → Lambda, SQS → Lambda, etc.) |
| Scaling | Automatic, per-function concurrency |
| Team structure | Feature teams owning function groups |

### Patterns to Include

- **API Gateway + Lambda**: HTTP routing to function handlers
- **Event-driven pipelines**: S3 → Lambda → DynamoDB, SQS → Lambda
- **Step Functions / Durable Functions**: Orchestration of multi-step workflows
- **Shared layers**: Common code in Lambda Layers or Azure Function extensions

### Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Cold starts | Provisioned concurrency, keep-warm strategies |
| Vendor lock-in | Abstract cloud-specific code behind interfaces |
| Debugging difficulty | Structured logging + distributed tracing (X-Ray, App Insights) |
| Execution time limits | Break long tasks into chained functions |

---

## 4. Event-Driven Architecture

### Overview

Components communicate by producing and consuming events. Emphasizes loose coupling, scalability, and real-time responsiveness.

### When to Use

- Systems with complex business workflows spanning multiple domains
- Real-time data processing requirements
- Need to decouple producers from consumers
- Audit trail / event history is important
- Integration of multiple systems with different update cycles

### Key Characteristics

| Aspect | Approach |
|--------|----------|
| Deployment | Per-service or per-handler |
| Data | Event store + materialized views, or database per consumer |
| Communication | Events via Kafka, EventBridge, RabbitMQ, or NATS |
| Scaling | Consumer-based horizontal scaling |
| Team structure | Event-ownership per team |

### Patterns to Include

- **Event Sourcing**: Persist state as a sequence of events
- **CQRS**: Separate read and write models
- **Saga / Choreography**: Business processes as a chain of events
- **Dead Letter Queue**: Failed event handling and retry
- **Schema Registry**: Event schema versioning (Avro, Protobuf)

### Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Event ordering | Partitioned topics (Kafka), sequence numbers |
| Debugging complexity | Correlation IDs, distributed tracing |
| Schema evolution | Schema registry with compatibility checks |
| Eventual consistency | Clear SLAs, compensating events |

---

## 5. Refactor in Place

### Overview

Retain the existing architecture but modernize internals: upgrade frameworks, refactor code structure, improve patterns, update dependencies. No structural decomposition.

### When to Use

- Architecture is fundamentally sound
- Risk of large-scale restructuring outweighs benefit
- Technology modernization is the primary goal (e.g., Java 8 → 21, Angular 1 → latest)
- Team is small and deployment simplicity is critical

### Key Characteristics

| Aspect | Approach |
|--------|----------|
| Deployment | Same as current |
| Data | Same as current |
| Communication | Same as current |
| Scaling | Same as current or incrementally improved |
| Team structure | Same as current |

### Patterns to Include

- **Strangler Fig**: Gradually replace components within the same deployment boundary
- **Branch by Abstraction**: Swap implementations behind interfaces
- **Feature Flags**: Control rollout of modernized components
- **Dependency Injection**: Introduce DI for testability and modularity

### Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Incomplete modernization | Track progress per module; set deadlines |
| Regression | Comprehensive test suite before refactoring |
| Scope creep | Strict focus on plan.json scope |

---

## Pattern Selection Guide

Use this decision matrix to recommend a pattern based on context:

| Factor | Microservices | Modular Monolith | Serverless | Event-Driven | Refactor |
|--------|:---:|:---:|:---:|:---:|:---:|
| Team size > 5 | ✅ | ✅ | ✅ | ✅ | ✅ |
| Independent deployment needed | ✅ | ❌ | ✅ | ✅ | ❌ |
| Variable scaling per component | ✅ | ❌ | ✅ | ✅ | ❌ |
| Strong consistency required | ❌ | ✅ | ❌ | ❌ | ✅ |
| Low operational complexity | ❌ | ✅ | ✅ | ❌ | ✅ |
| Rapid prototyping | ❌ | ✅ | ✅ | ❌ | ❌ |
| Complex domain workflows | ✅ | ✅ | ❌ | ✅ | ✅ |
| Audit trail / event history | ❌ | ❌ | ❌ | ✅ | ❌ |
| Minimize risk | ❌ | ✅ | ❌ | ❌ | ✅ |

Legend: ✅ = strong fit, ❌ = weak fit or not applicable

---

## Technology Recommendations by Pattern

### Microservices

| Layer | Recommended Technologies |
|-------|-------------------------|
| API Gateway | Kong, AWS API Gateway, Envoy, NGINX |
| Service Framework | Spring Boot, NestJS, Go kit, FastAPI |
| Service Mesh | Istio, Linkerd, Consul Connect |
| Messaging | Kafka, RabbitMQ, AWS SQS/SNS |
| Container Orchestration | Kubernetes, ECS, Nomad |
| Observability | OpenTelemetry, Prometheus, Grafana, Jaeger |

### Modular Monolith

| Layer | Recommended Technologies |
|-------|-------------------------|
| Framework | Spring Boot (modulith), NestJS, Django |
| Module enforcement | ArchUnit, jmolecules, ESLint boundaries |
| Internal events | Spring Events, MediatR, in-process EventEmitter |
| Database | PostgreSQL, MySQL — schema-per-module |

### Serverless

| Layer | Recommended Technologies |
|-------|-------------------------|
| Compute | AWS Lambda, Azure Functions, Google Cloud Functions |
| API | API Gateway, Azure API Management |
| Orchestration | AWS Step Functions, Azure Durable Functions |
| Storage | DynamoDB, Aurora Serverless, Cosmos DB |
| IaC | AWS SAM, Serverless Framework, CDK, Pulumi |

### Event-Driven

| Layer | Recommended Technologies |
|-------|-------------------------|
| Event Broker | Apache Kafka, AWS EventBridge, Azure Event Hubs |
| Schema Registry | Confluent Schema Registry, AWS Glue |
| Stream Processing | Kafka Streams, Apache Flink, Kinesis Data Analytics |
| Event Store | EventStoreDB, Kafka (log-compacted topics) |
