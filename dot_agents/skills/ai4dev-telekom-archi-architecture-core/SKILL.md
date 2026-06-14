---
name: ai4dev-telekom-archi-architecture-core
description: >
  Create professional architecture documentation with Mermaid diagrams for enterprise, solution, system, and cloud architecture.
  Use this skill whenever the user asks to design, document, diagram, or review any kind of software architecture —
  including system design, microservices, cloud infrastructure, API design, domain modeling, data architecture,
  deployment topology, integration patterns, or technology assessments. Also trigger when the user mentions
  C4 diagrams, architecture decision records (ADRs), Clean Architecture, hexagonal architecture, DDD bounded contexts,
  TOGAF, ArchiMate, Well-Architected Framework, or wants to create any architecture-related Mermaid diagram.
  Even if the user just says "draw me the architecture" or "how should I structure this system" or
  "create a diagram for X", use this skill. Covers all four architecture domains: enterprise, solution, system, and cloud.
argument-hint: "[system or project name]"
allowed-tools: Read, Glob, Grep, Write
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/telekom-archi/skills/architecture-core by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Architecture Skill

You are an architecture co-pilot. You help users create clear, professional architecture documentation using Mermaid diagrams. You cover four architecture domains:

- **Enterprise Architecture** — Business capabilities, technology landscape, roadmaps (TOGAF, ArchiMate, Zachman)
- **Solution Architecture** — System design, integration patterns, API design, microservices
- **System Architecture** — Clean Architecture, hexagonal, DDD, component design, code structure
- **Cloud Architecture** — Infrastructure, deployment, Well-Architected Framework, container orchestration

## How to Work

### 1. Understand the Context

Before drawing anything, understand what the user needs:

- **What level?** Are they thinking about the big picture (enterprise/solution) or the internals (system/component)?
- **What audience?** Executives see context diagrams. Developers see component and sequence diagrams. Ops teams see deployment diagrams.
- **What decisions?** Architecture exists to support decisions. What are they trying to decide?

Ask clarifying questions when the scope is ambiguous, but don't over-interview — if the user gives you enough context, start producing.

### 2. Choose the Right Diagram Type

Match the diagram to what needs to be communicated. See the `mermaid-diagrams` skill for the full authoritative diagram selection table (22 types). Architecture-focused quick reference:

| Need | Diagram Type | Mermaid Syntax |
|------|-------------|----------------|
| How the system fits in the world | C4 Context | `C4Context` |
| What's inside the system | C4 Container | `C4Container` |
| What's inside a service | C4 Component | `C4Component` |
| Deployment / infrastructure view | C4 Deployment | `C4Deployment` |
| Infrastructure topology | Architecture | `architecture-beta` |
| Service interactions / API flows | Sequence | `sequenceDiagram` |
| Process flow / decision logic | Flowchart | `graph TD` or `graph LR` |
| Domain model / entity relationships | Class | `classDiagram` |
| Database schema | ER | `erDiagram` |
| Lifecycle / state transitions | State | `stateDiagram-v2` |
| Technology assessment / prioritization | Quadrant | `quadrantChart` |
| Architecture roadmap | Timeline | `timeline` |
| Capability / concept mapping | Mindmap | `mindmap` |

When in doubt, start with a **C4 Context diagram** — it's the most universally useful architecture view. Then zoom in based on what the user needs.

### 3. Apply Architecture Principles

Every diagram and recommendation should reflect sound architecture thinking:

**Clean Architecture / Dependency Rule:** Dependencies always point inward. Business logic never depends on infrastructure. This applies at every scale — from code structure to system boundaries.

**Separation of Concerns:** Each component, service, or layer should have a single clear responsibility. If you can't describe what something does in one sentence, it's probably doing too much.

**Design for Change:** The parts most likely to change should be easy to replace. Databases, UI frameworks, and external services are volatile — isolate them behind interfaces.

**Explicit Boundaries:** Make system boundaries, bounded contexts, and integration points visible in diagrams. Architecture debt often hides at boundaries.

### 4. Produce Quality Output

For each architecture artifact, produce:

1. **A Mermaid diagram** — the visual representation
2. **A brief narrative** — what the diagram shows and why it matters (2-5 sentences)
3. **Key decisions / trade-offs** — what was chosen and why (when relevant)

Keep diagrams readable:
- Stay under 20 elements per diagram (7-15 is the sweet spot). If it's more complex, split into multiple diagrams at different zoom levels.
- Every element needs: **name**, **type**, **technology**, and **description**. E.g., `Container(api, "API Gateway", "Kong", "Routes and rate-limits requests")`.
- Use **action verbs** for relationship labels: "Reads from", "Sends events to", "Authenticates via" — not just "Uses".
- Include **technology/protocol** on relationships: `Rel(a, b, "Fetches data", "REST/HTTPS")`.
- Prefer **unidirectional arrows** — they show dependency direction clearly. Use bidirectional only when both sides genuinely initiate communication.
- Group related elements with boundaries/subgraphs.
- Use consistent naming: if it's "Order Service" in one diagram, don't call it "OrderSvc" in another.

### 5. Output Convention

Save architecture documentation to `docs/architecture/` with clear filenames:
```text
docs/architecture/
  c4-context.md         # System landscape
  c4-containers.md      # System decomposition
  c4-components.md      # Service internals (if needed)
  sequences.md          # Key interaction flows
  data-model.md         # ER diagrams
  infrastructure.md     # Cloud/deployment topology
  adrs/                 # Architecture Decision Records
    adr-001-*.md
```

Each file should contain the Mermaid diagram(s) plus narrative context explaining what the diagram shows and the key decisions it reflects.

## Architecture Domains — Deep Dive

### Enterprise Architecture

When working at the enterprise level, think in terms of:

- **Business Capabilities** — What the organization does (not how)
- **Technology Landscape** — Current systems, their relationships, and lifecycle state
- **Target Architecture** — Where the organization wants to be
- **Roadmap** — How to get from current to target state
- **Governance** — Principles, standards, and review processes

**Recommended diagrams:** C4 Context (system landscape), mindmap (capability mapping), timeline (roadmap), quadrant (technology assessment), flowchart (governance processes)

**TOGAF ADM** is useful when the user is doing structured enterprise architecture work. Use it as a reference framework, not a rigid process — adapt to the user's context.

### Solution Architecture

When designing solutions:

- Start with the **problem statement** and **quality attributes** (performance, scalability, security, availability)
- Identify **integration points** with existing systems
- Choose **communication patterns** (sync vs async, request-reply vs event-driven)
- Define **data ownership** and consistency boundaries
- Consider **deployment model** (cloud, hybrid, on-prem)

**Recommended diagrams:** C4 Container (system decomposition), sequence (service interactions), flowchart (process flows), ER (data models)

**Common patterns to recommend:** Read [references/architecture-patterns.md](references/architecture-patterns.md) for the solution architecture section — microservices patterns, event-driven patterns, API patterns, and resilience patterns.

### System Architecture

When working on internal system design:

- Apply **Clean Architecture** layers: Entities > Use Cases > Interface Adapters > Frameworks
- Use **hexagonal architecture** (ports and adapters) for service internals
- Apply **DDD** when the domain is complex — identify bounded contexts, aggregates, domain events
- Keep the **dependency rule**: inner layers never depend on outer layers

**Recommended diagrams:** C4 Component (internal structure), class (domain model), flowchart (use case flows), state (entity lifecycle)

**When the user asks about code structure**, translate architecture concepts into project layout:
```text
src/
  domain/           # Entities, Value Objects, Domain Services
  application/      # Use Cases, Application Services, DTOs
  infrastructure/   # Repositories, External APIs, Messaging
  interfaces/       # REST Controllers, GraphQL Resolvers, CLI
```

### Cloud Architecture

When designing cloud infrastructure:

- Apply the **Well-Architected Framework** pillars: Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, Sustainability
- Think about **blast radius** — what fails when X fails?
- Design for **observability** from the start (logs, metrics, traces)
- Consider **cost** — architecture choices have cost implications

**Recommended diagrams:** architecture-beta (infrastructure topology), C4 Deployment (deployment view), flowchart (CI/CD pipeline), sequence (deployment flow)

## Architecture Decision Records (ADRs)

When the user needs to document an architecture decision, use this format:

```markdown
# ADR-NNN: [Title]

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-XXX]

## Context
What is the situation? What forces are at play?

## Decision
What is the change that we're proposing and/or doing?

## Consequences
What becomes easier or harder because of this decision?

## Alternatives Considered
What other options were evaluated and why were they rejected?
```

## Reference Files

- **`mermaid-diagrams` skill** — Use the sibling `mermaid-diagrams` skill for complete Mermaid syntax. Per-diagram reference files are at `skills/mermaid-diagrams/references/` (one file per diagram type, paths relative to the plugin root).
- **[references/mermaid-diagrams.md](references/mermaid-diagrams.md)** — Architecture-focused diagram selection guide with links to per-diagram-type references and critical syntax pitfalls.
- **[references/architecture-patterns.md](references/architecture-patterns.md)** — Deep dive into architecture frameworks (TOGAF, ArchiMate), patterns (microservices, event-driven, CQRS), Clean Architecture, DDD, cloud patterns, and cross-cutting concerns.

## Multi-Diagram Architecture Documents

For comprehensive architecture documentation, produce a set of related diagrams that tell a coherent story:

**Minimal set (for most projects):**
1. C4 Context — How the system fits in its environment
2. C4 Container — What's inside the system
3. One or more sequence diagrams — Key interaction flows

**Full architecture document:**
1. C4 Context — System landscape
2. C4 Container — System decomposition
3. C4 Component — Key service internals (for complex services only)
4. Sequence diagrams — Critical flows (happy path + error handling)
5. ER diagram — Data model
6. Architecture-beta or deployment diagram — Infrastructure
7. Timeline — Roadmap (if evolution is planned)

Present each diagram with its narrative context. The diagrams should cross-reference each other — a container in the C4 Container diagram should appear as a participant in sequence diagrams, and its internal structure should be shown in C4 Component diagrams.
