---
name: ai4dev-tmforum-plugin-oda-architecture
description: TM Forum Open Digital Architecture (ODA) framework for cloud-native telecommunications. Use this skill when designing ODA components, understanding ODA Canvas platform, implementing cloud-native telecom architectures, or applying ODA principles for modular, scalable systems.
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/tmforum-plugin/skills/oda-architecture by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# ODA Architecture

## Overview

This skill provides guidance on TM Forum Open Digital Architecture (ODA) - a framework for building cloud-native, component-based telecommunications platforms through modular, API-first design.

## When to Use This Skill

Use when designing ODA components, implementing cloud-native telecom architectures, modernizing monolithic systems, or creating microservices aligned with TM Forum standards.

## ODA Core Principles

### 1. Component-Based Architecture

- Modular, independently deployable components
- Each component owns a specific business capability
- Loose coupling through APIs
- Independent lifecycle management

### 2. API-First Approach

- TMF Open APIs as integration contracts
- Standard APIs for interoperability
- Versioned API contracts
- Event-driven communication

### 3. Cloud-Native Design

- Container-based (Docker/Kubernetes)
- Horizontal scalability
- Built-in resilience and fault tolerance
- Comprehensive observability

### 4. Data Ownership

- Database per component (no shared databases)
- SID-aligned data models
- Eventual consistency through events

## ODA Component Model

An ODA Component delivers a specific business capability and:

- Exposes TMF Open APIs
- Owns its data and business logic
- Can be independently deployed and scaled
- Integrates with ODA Canvas platform

**Component Types**:

- **Core**: Business capabilities (Product, Customer, Order)
- **Common**: Shared services (Identity, Notification)
- **Enabler**: Platform services (API Gateway, Event Bus)

## ODA Canvas Platform

ODA Canvas is the runtime platform providing:

1. **Component Management**: Registration, discovery, lifecycle
2. **API Management**: Gateway, auth, rate limiting
3. **Event Management**: Event bus and routing
4. **Identity & Access**: OAuth2, RBAC
5. **Observability**: Logging, metrics, tracing

## Component Design Patterns

### Pattern 1: Event-Driven Orchestration

Coordinate multi-component workflows asynchronously through events.

**Example**:

```text
Order Component → OrderCreated event
Fulfillment Component ← processes order → OrderFulfilled event
Inventory Component ← updates inventory
```

### Pattern 2: API Gateway

Single entry point for authentication, rate limiting, request aggregation.

### Pattern 3: Saga Pattern

Manage distributed transactions across components (choreography or orchestration).

### Pattern 4: Strangler Fig

Gradually migrate legacy systems by:

1. Identify bounded context
2. Build new ODA component
3. Route traffic through gateway
4. Shift traffic gradually
5. Decommission legacy

## Component Examples

### Product Catalog Component

- **APIs Exposed**: TMF620 Product Catalog
- **Events**: ProductOfferingCreated, ProductOfferingChanged
- **Data**: Product offerings, specifications, categories

### Order Management Component

- **APIs Exposed**: TMF622 Product Ordering, TMF641 Service Ordering
- **APIs Consumed**: TMF620 (validation), TMF679 (feasibility)
- **Events Published**: OrderCreated, OrderStateChange
- **Events Subscribed**: ServiceOrderCompleted

## Design Checklist

- [ ] Clear business capability and bounded context
- [ ] TMF API exposures defined
- [ ] Dependencies documented (APIs consumed)
- [ ] Event definitions (published/subscribed)
- [ ] Data ownership (no shared DB)
- [ ] Horizontal scalability
- [ ] Health checks and monitoring
- [ ] Security (auth/authz)
- [ ] Deployment artifacts (Helm charts)
- [ ] API documentation (OpenAPI)

## Deployment (Kubernetes)

**Key Resources**:

- Deployment with replicas, resource limits, health probes
- Service (ClusterIP)
- HorizontalPodAutoscaler (CPU/memory based)
- ConfigMaps and Secrets for configuration

**Observability**:

- Structured JSON logs to stdout
- Prometheus metrics at `/metrics`
- Distributed tracing (Jaeger/OpenTelemetry)
- Grafana dashboards

## Technology Stack

**Languages/Frameworks**: Spring Boot, Node.js (Express/NestJS), Python (FastAPI), Go

**Databases**: PostgreSQL, MongoDB, Redis

**Messaging**: Kafka, RabbitMQ, NATS

**API Gateway**: Kong, Apigee

**Service Mesh**: Istio, Linkerd
