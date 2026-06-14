---
name: ai4dev-mara-plugin-mara-technology-blueprint
description: This skill should be used when selecting AI platforms and technologies for MARA implementations, choosing between DT AI platforms (Onix, TARDIS MCP Gateway, LUMINA, Keystone AI), implementing agentic capabilities, configuring MCP integrations, setting up agent lifecycle management, or making technology decisions for AI-first architectures at Deutsche Telekom.
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/mara-plugin/skills/mara-technology-blueprint by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# MARA Technology Blueprint

## Overview

The Magenta AI-Centric Reference Architecture (MARA) Technology
Blueprint defines technology choices and recommendations for building,
deploying, operating, and governing Agentic AI systems across Deutsche
Telekom.

MARA enables teams to design and run AI agents using multiple frameworks
and platforms while ensuring enterprise-wide interoperability, security,
compliance, and governance. It serves as a common reference point across
NatCos and central platforms, balancing innovation speed with
architectural consistency.

## Key Objectives

1. **Interoperability** - Enable seamless integration between agents,
   platforms, and systems
2. **Governance** - Ensure compliant, auditable, and controlled AI operations
3. **Scalability** - Support growth from pilots to enterprise-wide deployments
4. **Reusability** - Maximize component sharing across teams and NatCos

## DT AI Platforms Overview

### Primary Platforms

| Platform       | Owner                 | Purpose                          |
|----------------|-----------------------|----------------------------------|
| **Onix**       | PIX - AI Products     | Agent management, knowledge hub, |
|                |                       | guardrails, evaluation           |
| **TARDIS**     | DHEI                  | Enterprise MCP with security     |
| **LUMINA**     | -                     | Agentic observability & tracing  |
| **Keystone AI**| EU IT                 | AI capabilities (Pluto Data)     |
| **Magenta**    | B2B IT - AI CoE       | Reusable AI components (B2B)     |
| **MLOps**      | Platform Engineering  | Kubeflow-based ML capabilities   |

### Platform Selection Guidance

**For Agent Lifecycle Management:**

- Use **Onix Agent Management Studio** for agent configuration, lifecycle, A/B experimentation
- Supports LangGraph and LMOS-based agents
- Self-service agent creation planned for Q1 2026

**For MCP Integration:**

- **TARDIS MCP Gateway is mandatory** for all MCP integrations
- Provides secure gateway, authentication, rate limiting, audit logging
- All MCP traffic must route through TARDIS

**For Observability:**

- Use **LUMINA Platform** with OpenTelemetry support
- Implement Open Telemetry (and possibly Open Inference) as standard

**For Knowledge Management:**

- Use **Onix Knowledge Hub** for ingestion, knowledge graphs, observability
- Based on UnifyApps iPaaS, ready Q1 2026

## MARA Capability Areas

MARA defines 12 capability areas (with sub-capabilities) across four focus
areas: Build, Interoperate, Productionize, and Library & Reuse.

### 1. Agent Lifecycle Management (Build-focused)

**Description:** Create, register, deploy, monitor, update, and retire
agents within an enterprise ecosystem.

**Technology Options:**

- Hybrid Platform approach combining best-in-class with DT enablers
- OpenAI Platform (ChatKit/Agents SDK/Agent Builder)
- Google Vertex AI (Google ADK)

**DT Platforms:**

- **Onix Agent Management Studio** - agent configuration, lifecycle, A/B experimentation
  - Current: Lifecycle management of live production agents
  - Roadmap: Self-service agent creation (Q1 2026)
- DT Technik evaluating Google Vertex AI, Nokia Data Robot, IBM WatsonX

**Recommendation:** Use Onix for agent lifecycle management with support
for LangGraph and LMOS agents.

### 2. Agentic Memory & Knowledge Management (Build-focused)

**Description:** Store, reason over, and evolve organizational knowledge
for autonomous, context-aware operations.

**Technology Options:**

- Memory: Mem0, Zep, LangGraph Memory (short & long-term)
- Knowledge: Qdrant, Onix Knowledge Hub

**DT Platforms:**

- **Onix Knowledge Hub** - Ingestion, Knowledge Graph, Observability, Evals
  - Based on UnifyApps iPaaS
  - Ready Q1 2026
- **KKM/CCM** - Customer contact management platform (for memory)

**Current Implementation:**

- Frag Magenta uses Redis (short-term) and MongoDB (long-term) for memory
- Qdrant Vector DB with Wurtzel (DT home-grown RAG & ETL platform)

### 3. Agentic In-platform Guardrails (Build-focused)

**Description:** Built-in safety, policy, and control mechanisms within the AI platform.

**Technology Options:**

- Guardrails AI
- Microsoft Presidio-based models + LLM as Judge for pseudonymization

**DT Platforms:**

- **Onix Guardrails** - Policy-based guardrails, pseudonymization
  - Ready Q2 2026

**Requirements:** Mandatory for all production agents. Align with DT AI Ethics guidelines.

### 4. Agent-to-Agent Integration (Interoperate-focused)

**Description:** Enable autonomous agents to exchange information and
collaborate on multi-step tasks.

**Recommendation:** Use **A2A Protocol** for inter-agent communication.

### 5. Agentic Collaboration Orchestration (Interoperate-focused)

**Description:** Coordinate, schedule, and manage autonomous agents and their interactions.

**DT Platforms:**

- **OneBot** uses LangGraph for Supervisor agent with:
  - Intent Classification (Custom SLM under development)
  - Disambiguation, Planning, Response Validation, Orchestration
- New common App/Web SDK planned for Consumer AI and OneBot
- Voice & multi-modalities: LiveKit/Elevenlabs

### 6. MCP Management (Interoperate-focused) - CRITICAL

**Description:** Governance, orchestration, and lifecycle control of
agent-tool communication via MCP.

**Technology:** TARDIS MCP Gateway

**MARA Recommendation:**

- **TARDIS MCP Gateway is MANDATORY**
- All MCP integrations MUST route through TARDIS for security and governance
- Provides secure gateway, authentication, rate limiting, audit logging

**Resources:**

- MCP Gateway docs: `https://wiki.telekom.de/pages/viewpage.action?spaceKey=DHEI&title=MCP+Gateway+and+Orchestration+MVP`
- MCP Server Specification: `https://wiki.telekom.de/pages/viewpage.action?pageId=3691938421`

### 7. Tracing & Agentic Observability (Productionize-focused)

**Description:** Monitor, log, analyze, and visualize the full lifecycle
of agentic activity.

**Technology Options:**

- Arize, LangFuse (with OpenTelemetry)
- LUMINA Platform

**MARA Recommendation:**

- Open Telemetry (and possibly Open Inference) as standard
- LUMINA with support for Agentic Observability

### 8. Evaluation Framework (Productionize-focused)

**Description:** Assess, benchmark, and validate agentic performance
across technical, behavioral, business, and ethical dimensions.

**Technology Options:**

- DeepEval
- Arize

**DT Platforms:**

- **Onix Evaluation Suite** (under development)

### 9. Annotation & Testing Capabilities (Productionize-focused)

**Description:** Label, validate, simulate, and test agentic AI behavior.

**Technology Options:**

- Testing: Cekura
- Annotation & Labeling: Label Studio, Arize, Argilla

**DT Platforms:**

- **Onix Test Automation Module** - Golden dataset creation, test cases
  - Ready Q1 2026

### 10. Agentic Registry Management (Library & Reuse-focused)

**Description:** Centralized registry of all active and deployable agentic components.

**Technology Options:**

- Agent Catalog: DT AI Marketplace, Telekom LeanIX
- Runtime Registry: Onix Agent Runtime Cockpit

**DT Platforms:**

- **Onix Agent Runtime Cockpit** (Roadmap: 1 month)
- **DT AI Marketplace** for agent discovery
- **LeanIX** integration for enterprise architecture alignment

### 11. Prompt Management (Library & Reuse-focused)

**Description:** Create, organize, version, test, and optimize prompts.

**Technology Options:**

- Arize
- Portkey

**DT Platforms:**

- **Onix SOP Module** - Prompt management, versioning, AI validations,
  analytics, testing (Ready Q1 2026)

### 12. Agentic Tool Management (Library & Reuse-focused)

**Description:** Dynamically discover, select, orchestrate, and safely
execute tools and APIs.

**DT Platforms:**

- **Onix Tool Builder** - Tool lifecycle, AI creation, analytics, and
  optimization (Ready Q1 2026)
- **TARDIS MCP Gateway** for tool security and governance

### 13. Model Management & Gateway (Foundational AI/ML)

**Description:** Model gateway, model management, and ML enablement capabilities.

**Technology Options:**

- Model Gateway: Portkey
- MLOps: Magenta MLOps, Google Vertex AI

**DT Platforms:**

- **Magenta MLOps** (used in CDL, Poland)

## Technology Selection Workflow

### Step 1: Identify Capability Needs

Map requirements to the 13 MARA capability areas.

### Step 2: Check DT Platform Availability

Consult `references/dt-platform-capabilities.md` for current platform
status and roadmaps.

### Step 3: Apply Mandatory Requirements

- MCP integrations → TARDIS MCP Gateway (mandatory)
- Production agents → Onix Guardrails (mandatory)
- Observability → OpenTelemetry standard

### Step 4: Evaluate Technology Options

For capabilities without mandated platforms, evaluate options based on:

- Integration with existing DT platforms
- Roadmap alignment
- Team expertise
- Total cost of ownership

### Step 5: Document Decisions

Record technology choices with rationale referencing MARA capabilities.

## Integration Patterns

### MCP Integration Pattern (Mandatory)

All MCP server integrations follow this pattern:

```text
Agent → TARDIS MCP Gateway → MCP Server → External Service
              ↓
      [Authentication]
      [Rate Limiting]
      [Audit Logging]
      [Security Policies]
```

### Agent Orchestration Pattern

```text
User Request → OneBot/Supervisor Agent
                       ↓
              [Intent Classification]
              [Planning & Disambiguation]
                       ↓
              Specialized Agents (via A2A)
                       ↓
              Tools (via MCP/TARDIS)
```

### Observability Pattern

```text
Agent Activity → OpenTelemetry SDK → LUMINA Platform
                                           ↓
                                   [Traces, Metrics, Logs]
                                   [Dashboards & Alerts]
```

## Quick Reference: Platform by Capability

| Capability        | Primary Platform              | Fallback/Alternative |
|-------------------|-------------------------------|----------------------|
| Agent Lifecycle   | Onix Agent Management Studio  | Vertex AI, WatsonX   |
| Memory            | Redis/MongoDB + Onix Hub      | Mem0, Zep            |
| Knowledge         | Onix Knowledge Hub + Qdrant   | Wurtzel              |
| Guardrails        | Onix Guardrails               | Guardrails AI        |
| A2A Communication | A2A Protocol                  | -                    |
| Orchestration     | LangGraph (OneBot)            | -                    |
| MCP Management    | **TARDIS MCP Gateway**        | None (mandatory)     |
| Observability     | LUMINA + OpenTelemetry        | Arize, LangFuse      |
| Evaluation        | Onix Evaluation Suite         | DeepEval, Arize      |
| Testing           | Onix Test Automation          | Cekura               |
| Registry          | Onix Runtime Cockpit + LeanIX | DT AI Marketplace    |
| Prompts           | Onix SOP Module               | Arize, Portkey       |
| Tools             | Onix Tool Builder             | -                    |
| Model Gateway     | Portkey                       | Magenta MLOps        |

## Resources

### Reference Files

- **`references/dt-platform-capabilities.md`** - DT platform capabilities
  and roadmaps
- **`references/capability-implementation-guide.md`** - Implementation
  patterns for each capability

### External Resources

- MARA Wiki: `https://wiki.telekom.de/spaces/EIAD/pages/3389124369`
- TARDIS MCP Gateway: `https://wiki.telekom.de/pages/viewpage.action?spaceKey=DHEI&title=MCP+Gateway+and+Orchestration+MVP`
- Working Groups: `https://wiki.telekom.de/display/EIAD/Invitation+to+Collaborate`

## Working Groups

Join MARA working groups to contribute:

| Working Group              | Schedule        | Focus               |
|----------------------------|-----------------|---------------------|
| MARA Framework Definition  | -               | Framework, patterns |
| App Architecture Transform | Tue 13:30 CET   | Legacy to DPS       |
| AI Platform (Gov/Guardrail)| Wed 15:00 CET   | Platform, guardrails|
| Data Architecture          | Wed 10:00 CEST  | Knowledge graphs    |
| UI/UX & Integration        | Wed 12:00 CET   | Dynamic UI          |
| Architecture as Code       | Thu 12:30 CET   | OneArch, tooling    |
| Security                   | Mon 14:30 CET   | Security policies   |
