# DT AI Platform Capabilities Reference

This document provides detailed capabilities and roadmaps for Deutsche Telekom AI platforms referenced in the MARA Technology Blueprint.

## Onix Platform Suite

### Onix Agent Management Studio

**Owner:** PIX - AI Products
**Status:** Production (partial)

**Current Capabilities (Production):**

- Agent configuration and lifecycle management
- Agent A/B experimentation (from OneCMS)
- Analytics for Frag Magenta agents
- Support for LangGraph-based agents
- Support for LMOS-based agents

**Roadmap:**

- Self-service agent creation: Q1 2026

**Integration Points:**

- Frag Magenta
- OneBot
- Consumer AI applications

### Onix Knowledge Hub

**Owner:** PIX - AI Products
**Status:** Under development

**Planned Capabilities:**

- Knowledge ingestion pipelines
- Knowledge Graph management
- Observability for knowledge retrieval
- Evaluation suite for RAG quality

**Technology Stack:**

- Based on UnifyApps iPaaS

**Roadmap:**

- Ready: Q1 2026

**Current Alternative:**

- Wurtzel (DT home-grown RAG & ETL platform)
- Qdrant Vector DB

### Onix Guardrails

**Owner:** PIX - AI Products
**Status:** Under development

**Planned Capabilities:**

- Policy-based guardrails enforcement
- Pseudonymization (Microsoft Presidio-based models + LLM as Judge)
- Content moderation
- PII detection and redaction

**Roadmap:**

- Ready: Q2 2026

**Requirements:**

- Mandatory for all production agents
- Must align with DT AI Ethics guidelines

### Onix Evaluation Suite

**Owner:** PIX - AI Products
**Status:** Under development

**Planned Capabilities:**

- Performance benchmarking
- Quality assessment
- Behavioral validation
- Business metric tracking

**Roadmap:**

- Ready: Q1 2026

### Onix Test Automation Module

**Owner:** PIX - AI Products
**Status:** Under development

**Planned Capabilities:**

- Golden dataset creation
- Test case management
- Automated testing pipelines
- Regression testing

**Roadmap:**

- Ready: Q1 2026

### Onix Agent Runtime Cockpit

**Owner:** PIX - AI Products
**Status:** In roadmap

**Planned Capabilities:**

- Runtime registry for active agents
- Agent health monitoring
- Performance dashboards
- Deployment management

**Roadmap:**

- Ready: 1 month (from blueprint date)

### Onix SOP Module (Prompt Management)

**Owner:** PIX - AI Products
**Status:** Under development

**Planned Capabilities:**

- Prompt versioning and management
- AI-based prompt validations
- Prompt gap analysis
- Prompt analytics and insights
- Prompt testing framework

**Roadmap:**

- Ready: Q1 2026

### Onix Tool Builder

**Owner:** PIX - AI Products
**Status:** Under development

**Planned Capabilities:**

- Tool lifecycle management
- AI-based tool creation assistance
- Tool analytics and optimization
- Tool activation/deactivation controls
- Integration with TARDIS MCP Gateway

**Roadmap:**

- Ready: Q1 2026

---

## TARDIS MCP Gateway

**Owner:** DHEI
**Status:** Production

**MANDATORY for all MCP integrations**

**Current Capabilities:**

- Secure gateway for MCP connections
- Authentication and authorization
- Rate limiting
- Audit logging
- Security policy enforcement

**Documentation:**

- MCP Gateway docs: <https://wiki.telekom.de/pages/viewpage.action?spaceKey=DHEI&title=MCP+Gateway+and+Orchestration+MVP>
- MCP Server Specification: <https://wiki.telekom.de/pages/viewpage.action?pageId=3691938421>

**Integration Requirements:**

- All MCP integrations MUST route through TARDIS
- Required for security and governance compliance
- No exceptions for production deployments

---

## LUMINA Platform

**Owner:** TBD
**Status:** Under development

**Planned Capabilities:**

- Agentic observability
- OpenTelemetry integration
- Trace visualization
- Metrics aggregation
- Log management

**Standards:**

- Open Telemetry
- Open Inference (planned)

---

## OneBot Platform

**Owner:** Consumer AI
**Status:** Production

**Current Capabilities:**

- LangGraph-based Supervisor agent
- Intent Classification (Custom SLM under development)
- Disambiguation handling
- Planning and orchestration
- Response validation

**Roadmap:**

- New common App/Web SDK for Consumer AI and OneBot

**Multi-modality Support:**

- Voice: LiveKit/Elevenlabs

---

## Keystone AI

**Owner:** EU IT
**Status:** Under development

**Planned Capabilities:**

- AI capabilities leveraging Pluto Data platform
- Integration with EU IT systems

**Details:** Additional information to be gathered

---

## Magenta Mind

**Owner:** B2B IT - AI Center of Excellence
**Status:** Production

**Current Capabilities:**

- Reusable AI components for B2B
- AgentForce integration
- SAP integration (to be verified)

**Use Cases:**

- B2B customer solutions
- Enterprise AI applications

---

## Magenta MLOps

**Owner:** Platform Engineering Services
**Status:** Production

**Current Capabilities:**

- Kubeflow-based ML Ops
- Open source ML tooling
- Model deployment pipelines

**Deployments:**

- CDL (Poland)
- Other NatCos

---

## KKM/CCM (Customer Contact Management)

**Owner:** Global Platform
**Status:** Production

**Capabilities:**

- Customer contact storage from multiple channels
- Contact history management
- Being considered for agent memory storage

**Use Case:**

- Agentic memory for customer interactions

---

## Other Platforms Under Evaluation

### DT Technik Evaluations

Currently evaluating for AgentOps (Buy option):

- Google Vertex AI
- Nokia Data Robot
- IBM WatsonX Platform

**Note:** Databricks not part of evaluation

### MLOps Selections by NatCos

- **On-prem MLOps:** Data Robot
- **Cloud MLOps:** Vertex AI

---

## Platform Selection Decision Matrix

| Use Case | Primary Platform | Alternative | Timeline |
|----------|------------------|-------------|----------|
| Agent Lifecycle | Onix Agent Management Studio | Vertex AI, WatsonX | Now (partial), Q1 2026 (full) |
| Knowledge Management | Onix Knowledge Hub | Wurtzel + Qdrant | Q1 2026 |
| Guardrails | Onix Guardrails | Guardrails AI | Q2 2026 |
| MCP Security | TARDIS MCP Gateway | None (mandatory) | Now |
| Observability | LUMINA | Arize, LangFuse | TBD |
| Evaluation | Onix Evaluation Suite | DeepEval, Arize | Q1 2026 |
| Testing | Onix Test Automation | Cekura | Q1 2026 |
| Registry | Onix Runtime Cockpit | DT AI Marketplace + LeanIX | 1 month |
| Prompts | Onix SOP Module | Arize, Portkey | Q1 2026 |
| Tools | Onix Tool Builder | - | Q1 2026 |
| Model Gateway | Portkey | Magenta MLOps | Now |

---

## Integration Contacts

For integration support with DT platforms:

- **Onix Suite:** PIX - AI Products team
- **TARDIS MCP Gateway:** DHEI team
- **OneBot:** Consumer AI team
- **Magenta Mind:** B2B IT - AI CoE
- **LUMINA:** TBD

---

## References

- MARA Wiki: <https://wiki.telekom.de/spaces/EIAD/pages/3389124369>
- Technology Blueprint: <https://wiki.telekom.de/display/EIAD/MARA+Technology+Blueprint>
- Working Groups: <https://wiki.telekom.de/display/EIAD/Invitation+to+Collaborate>
