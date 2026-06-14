---
name: ai4dev-mara-plugin-data-architecture-patterns
description: >
  Guide for designing cognitive data products and implementing AI-first data architectures aligned with MARA principles.
  Use this skill when designing data platforms, choosing data architecture patterns, implementing knowledge graphs,
  working with feature stores, building cognitive data products, aligning with Pluto platform capabilities,
  or applying data mesh/data fabric approaches in telecom and AI-centric environments.
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/mara-plugin/skills/data-architecture-patterns by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Data Architecture Patterns

## Overview

This skill provides comprehensive guidance for designing and implementing AI-first data architectures aligned with the
MARA (Magenta AI-Centric Reference Architecture) framework. It enables AI agents to architect cognitive data products,
select appropriate data patterns across ingestion, storage, processing, and distribution layers, and implement
intelligent data platforms that support autonomous agents and real-time decision-making.

The skill focuses on transforming traditional data architectures into AI-native ecosystems where data products are
cognitive, governance is intelligent, and orchestration is semantic-aware.

## When to Use This Skill

Use this skill when:

- Designing new data platforms or modernizing existing ones with AI-first principles
- Selecting appropriate data architecture patterns for specific use cases (ingestion, storage, processing, distribution)
- Implementing cognitive data products with embedded semantics, features, and predictive signals
- Building knowledge graphs and ontologies for semantic data integration
- Designing feature stores for ML model training and inference
- Applying data mesh or data fabric architectural approaches
- Aligning data architecture with Pluto platform capabilities
- Implementing governance patterns with policy-as-code and intelligent guardrails
- Designing event-driven semantic orchestration for agent systems
- Creating real-time analytics pipelines with AI enrichment
- Optimizing data lifecycle and cost management with AI-driven decisions

## Core Principles of AI-First Data Architecture

The MARA framework defines 18 guiding principles for data architecture:

### 1. Cognitive Data as a Product

Every dataset is a **cognitive data product** — domain-owned, self-describing, with embedded semantics, analytics, and
governance. Owners manage schema, semantics, features, predictive signals, and lifecycle.

### 2. Domain-Oriented Cognitive Ownership (Data Mesh+)

Domains own and publish cognitive data products enriched with semantics and intelligence, while the global platform
orchestrates cross-domain insights and composes them into enterprise knowledge graphs.

### 3. Federated Governance with Intelligent Guardrails

Governance is federated with central global guardrails and local enforcement through policy-as-code and AI-enabled
monitoring, automated lineage, and ethical AI enforcement.

### 4. AI-First Data Design

Datasets designed upfront for AI/ML with features, labels, embeddings, predictive signals, freshness, and versioning as
core design elements. Feature stores and vector databases are standard capabilities.

### 5. Privacy & Compliance by Design (Trust-Centric)

Privacy and compliance embedded into design with AI-enabled classification, retention, and minimization. Automated DPIA checks, encryption, anonymization, and residency controls.

### 6. Contract-First Semantic Integration

Data contracts capture semantics, quality, and intent beyond schema. Schema registries evolve into semantic registries with validated contracts that preserve business meaning.

### 7. Event-Driven Semantic Orchestration

Domains, services, and agents connected by business events carrying context, semantics, and intent. Streaming-first pipelines propagate meaningful events to trigger AI/automation.

### 8. API-First & Agent-Ready Integration

Data and insights exposed via secure APIs and event interfaces, consumable by apps, UIs, and AI agents with proper governance and access controls.

### 9. Single Golden Sources + Cognitive Curated Layers

Canonical master data enriched with semantics and predictive insights. Gold layers become cognitive with curated KPIs and ML-ready features embedded.

### 10. Observable, Testable & Self-Healing (DataOps + AIOps)

Data systems are observable and self-healing with AI-driven anomaly detection, auto-remediation, automated testing, and closed-loop feedback.

### 11. Secure & Trustworthy by Default

Security, ethics, and trust embedded at every layer with RBAC/ABAC, encryption, fairness checks, audit trails, and explainable AI.

### 12. Cloud-Agnostic & Hybrid Cognitive Flexibility

Multi-cloud and hybrid flexibility with semantics and governance spanning boundaries, enabling local deployment with global semantic fabric participation.

### 13. Semantic Schema Evolution & Backward Compatibility

Schema changes respect technical compatibility and semantic meaning with versioning for ontologies, KPIs, and features.

### 14. Composable, Reusable Building Blocks

Reference templates for ingestion, semantic contracts, and cognitive product scaffolds enable fast composition with pluggable modules.

### 15. Cost & Lifecycle Awareness with Intelligence

Data lifecycle decisions informed by usage, value, and AI-driven optimization with intelligent retention, tiered storage, and dynamic cost controls.

### 16. Learning Loops & Continuous Improvement

Every cognitive data product embeds feedback loops where outcomes flow back to refine features, models, and policies continuously.

### 17. Human-in-Loop Governance

Explicit hooks for human judgment intervention with approval channels, feedback as first-class datasets, and model improvement from human input.

### 18. Collaborative Risk-Based Escalation

AI decisions carry risk scores dictating autonomy vs. escalation with standardized risk metadata and dynamic routing based on risk thresholds.

## Data Architecture Pattern Categories

### Pattern Selection Guide

When architecting data solutions, select patterns from these categories based on use case requirements:

1. **Integration & Ingestion** - How data enters the platform
2. **Storage & Organization** - How data is structured and stored
3. **Processing** - How data is transformed and enriched
4. **Distribution & Access** - How data is consumed
5. **Governance & Quality** - How data is governed and trusted
6. **Analytics & AI Enablement** - How intelligence is derived
7. **Architecture Topology** - Overall structural approach
8. **Operational Excellence** - How systems are monitored and optimized
9. **Orchestration** - How workflows and decisions are coordinated

## Comprehensive Pattern Reference

For detailed information on all data architecture patterns including descriptions, AI roles, telecom use cases, aligned principles, and priority levels, refer to:

**`references/data-architecture-patterns-comprehensive.md`** - Complete pattern catalog with 40+ patterns organized by category

This reference includes:

- Pattern descriptions and implementation details
- AI's role in each pattern with concrete examples
- Telecom-specific use cases
- Alignment with MARA AI principles
- Priority levels (High/Medium/Low)
- AI scope indicators

## Platform Capabilities Reference

For detailed platform capabilities organized by category, refer to:

**`references/data-platform-capabilities.md`** - Platform capabilities matrix

This reference covers:

- Ingestion & Integration Processing Pipelines
- Storage & Organization capabilities
- Governance & Quality tools
- Distribution & Access mechanisms
- Analytics & AI Capabilities
- Operational Excellence features

## Knowledge Graph & Ontology

Knowledge graphs and ontologies form the semantic backbone of cognitive data architectures.

### Key Concepts

**Knowledge Graph**: Structured representation where entities are nodes (Customer, Device, Service) with attributes and relationships (Connected, Has, Owns, Subscribed).

**Ontology**: Defines the schema/vocabulary for knowledge graphs, specifying classes, properties, rules, and constraints.

### Benefits for Telecom AI Systems

- **Unification** - Break down silos across OSS, BSS, CRM, Network, and Customer data
- **Semantic Backbone** - Standard meaning with connected entities and relationships
- **AI Enablement** - Supports recommendation, fraud detection, churn prediction, network optimization
- **Global-Local Collaboration** - Global ontology as single source of truth with local extensions
- **Trust & Explainability** - Makes AI auditable and explainable for regulated telecom
- **Business Value Focus** - Drives customer experience, operational efficiency, and compliance

For detailed knowledge graph patterns and implementation guidance, refer to:

**`references/knowledge-graph-ontology.md`** - Complete knowledge graph reference

## Cognitive Data Product Design

When designing cognitive data products, follow this template:

### Core Components

1. **Domain Ownership** - Clear ownership with defined responsibilities
2. **Semantic Schema** - Business-meaningful schema with ontology mapping
3. **Data Contract** - Technical and semantic guarantees with quality SLAs
4. **Embedded Features** - ML-ready features for model training/inference
5. **Predictive Signals** - AI-generated insights (risk scores, anomalies, recommendations)
6. **Quality Gates** - Automated validation and trust scoring
7. **Lineage & Observability** - Full traceability and monitoring
8. **API/Event Interface** - Agent-ready consumption mechanisms
9. **Feedback Loops** - Continuous improvement from outcomes

### Example: Customer Churn Cognitive Product

```yaml
Product: Customer360ChurnPredictor
Domain: Customer Analytics
Owner: Customer Insights Team

Components:
- Base Data: Customer profile, usage history, billing, complaints
- Semantic Schema: Mapped to Customer ontology (Subscriber, Plan, Device)
- Features: avg_data_usage_7d, call_drop_rate, payment_delay_frequency
- Predictive Signals: churn_risk_score (0-1), churn_reason, recommended_retention_action
- Quality SLA: 99.9% completeness, <24h latency, weekly model retraining
- Consumption: REST API, Kafka events, Feature Store access
- Governance: PII masked, GDPR-compliant, lineage tracked
```

For complete cognitive data product templates and examples, refer to:

**`references/cognitive-data-product-templates.md`** - Product design templates

## Pluto Platform Alignment

When implementing data architectures, align with Pluto platform capabilities:

- **Data Ingestion** - Leverage Pluto's API-based ingestion and CDC capabilities
- **Storage** - Use Pluto's lakehouse architecture with bronze/silver/gold layers
- **Processing** - Utilize Pluto's streaming and batch processing engines
- **Feature Management** - Integrate with Pluto's feature store
- **Governance** - Apply Pluto's policy-as-code and lineage tracking
- **Orchestration** - Use Pluto's event-driven orchestration layer
- **Analytics** - Leverage Pluto's real-time analytics and BI tools
- **AI/ML** - Connect to Pluto's model registry and MLOps capabilities

## Implementation Workflow

Follow this workflow when implementing data architecture solutions:

### 1. Understand Requirements

- Identify business use case and value drivers
- Define data sources, consumers, and SLAs
- Determine latency, volume, and quality requirements
- Assess compliance and governance needs

### 2. Select Architecture Patterns

- Review pattern catalog for applicable patterns
- Match patterns to requirements (latency, scale, AI needs)
- Consider hybrid approaches combining multiple patterns
- Validate alignment with MARA principles

### 3. Design Cognitive Data Products

- Define product boundaries and ownership
- Create semantic schema and ontology mappings
- Specify data contracts with quality SLAs
- Design embedded features and predictive signals
- Plan API/event interfaces for consumption

### 4. Implement Governance & Quality

- Define policy-as-code rules
- Set up trust gates and validation checkpoints
- Implement lineage tracking
- Configure observability and monitoring
- Establish feedback loops

### 5. Build & Deploy

- Implement ingestion pipelines
- Set up storage layers (bronze/silver/gold)
- Deploy processing workflows
- Configure distribution mechanisms
- Enable AI/ML capabilities

### 6. Operationalize

- Monitor SLAs and quality metrics
- Collect feedback from consumers
- Continuously improve features and predictions
- Optimize costs and performance
- Evolve based on learning loops

## Common Use Cases

### Network Anomaly Detection & Auto-Remediation

**Patterns**: Streaming Ingestion + Cognitive Event Pipelines + Real-Time Analytics + Policy Orchestration
**Approach**: Ingest 5G telemetry streams, detect anomalies with ML models inline, enrich with semantic context, trigger auto-remediation workflows

### Customer Churn Prevention

**Patterns**: Feature Store + Knowledge Graph + Reverse ETL + Decision Orchestration
**Approach**: Build Customer360 view combining usage, billing, complaints; compute churn risk features; push insights to CRM for proactive retention

### Fraud Detection in Real-Time

**Patterns**: API Ingestion + Stream Processing + Vector Database + Cognitive Event Pipelines
**Approach**: Capture transaction events, apply fraud models, search similar historical patterns, enrich with risk scores, route to fraud system

### Intelligent Customer Care

**Patterns**: Knowledge Graph + Vector Search/RAG + Semantic Layer
**Approach**: Build unified knowledge graph of customers, devices, network, policies; enable chatbot with RAG for context-aware responses

### Revenue Optimization

**Patterns**: Data Lakehouse + Feature Store + Reverse ETL + Learning Loops
**Approach**: Curate usage patterns, build propensity-to-buy features, push personalized offers to apps, capture outcomes for model improvement

## Key Resources

This skill includes the following reference materials:

- **references/data-architecture-patterns-comprehensive.md** - Complete catalog of 40+ patterns
- **references/data-platform-capabilities.md** - Platform capabilities matrix by category
- **references/knowledge-graph-ontology.md** - Knowledge graph and ontology patterns
- **references/cognitive-data-product-templates.md** - Product design templates and examples
- **references/data-architecture-principles.md** - Detailed principle descriptions with implications

## Best Practices

### Pattern Selection

- Start with use case requirements, not technology preferences
- Consider hybrid approaches combining multiple patterns
- Prioritize High priority patterns for initial implementation
- Validate alignment with multiple MARA principles

### Semantic Design

- Always define ontologies before implementing knowledge graphs
- Map data contracts to business glossary terms
- Embed semantic metadata at ingestion time
- Version ontologies alongside schemas

### AI Integration

- Design for AI consumption from the start (features, vectors, semantics)
- Embed predictions and risk scores into data products
- Use feature stores for consistency between training and inference
- Implement feedback loops for continuous model improvement

### Governance

- Implement policy-as-code for automated enforcement
- Use trust gates at storage layer boundaries
- Track lineage end-to-end for explainability
- Apply human-in-loop for high-risk decisions

### Performance

- Use streaming for latency-sensitive use cases
- Apply intelligent tiering for cost optimization
- Cache frequently-accessed features
- Monitor and optimize continuously with AIOps

## Additional Resources

Access the complete MARA framework documentation at the source:

- MARA AI Architecture Principles: <https://wiki.telekom.de/spaces/EIAD/pages/3342469641>
- Data Architecture Overview: <https://wiki.telekom.de/spaces/EIAD/pages/3359778066>
