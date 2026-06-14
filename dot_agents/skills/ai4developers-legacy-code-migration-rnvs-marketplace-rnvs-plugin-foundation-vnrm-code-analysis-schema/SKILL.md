---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-foundation-vnrm-code-analysis-schema
description: Provides comprehensive JSON schema for VNRM microservice analysis output. This skill should be used when analyzing modern VNRM codebases, documenting microservice architectures, API contracts, and integration patterns.
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/foundation/skills/vnrm-code-analysis-schema by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# VNRM Code Analysis Schema

## Overview

Defines the structured JSON format for modern VNRM microservice analysis output. The schema captures microservices architecture, API contracts, database schemas, integration patterns, and operational characteristics in a machine-readable format optimized for system documentation, enhancement planning, and integration mapping.

## When to Use

- **VNRM Codebase Analysis**: Analyze existing VNRM microservices and document their architecture
- **API Contract Documentation**: Extract and document REST/gRPC API specifications
- **Database Schema Analysis**: Document PostgreSQL schemas and data models
- **Integration Mapping**: Map service-to-service dependencies and external integrations
- **Performance Assessment**: Capture operational metrics and performance characteristics
- **Enhancement Planning**: Identify opportunities for optimization and modernization
- **Test Infrastructure Analysis** (CHANGE mode): Capture existing test inventory for Phase 11/12 classification

## Schema Overview

> **Complete Schema**: See [references/vnrm-schema.json](references/vnrm-schema.json) for full JSON Schema.
> **Working Example**: See [references/vnrm-example.json](references/vnrm-example.json) for NUM service example.

### Critical Fields for Downstream Phases

| Field | Used By | Purpose |
|-------|---------|---------|
| `repository_path` | Phase 12, 13.1 | Absolute path to VNRM repo for applying code changes |
| `source_structure` | Phase 12, 13.1 | Source roots for computing file paths |
| `test_infrastructure` | Phase 11, 12 | Test inventory for REUSE/MODIFY/NEW classification |

> **Field Details**: See [references/vnrm-field-guide.md](references/vnrm-field-guide.md) for complete field documentation.

## Usage

### For VNRM Service Analysis

Generate analysis.json following the schema structure for modern microservices.

**See [references/vnrm-schema.json](references/vnrm-schema.json) for complete JSON Schema.**

**See [references/vnrm-example.json](references/vnrm-example.json) for complete working example.**

### For Service Documentation

Parse analysis.json to extract:
- API specifications for integration planning
- Database schemas for data modeling
- Integration patterns for service mapping
- Operational metrics for performance optimization
- Enhancement opportunities for modernization planning

**See [references/vnrm-field-guide.md](references/vnrm-field-guide.md) for detailed field explanations.**

### For Validation

Validate generated VNRM analysis.json:

```bash
# Basic validation
python3 scripts/validate_analysis.py /path/to/analysis.json

# Verbose mode with detailed error paths
python3 scripts/validate_analysis.py /path/to/analysis.json --verbose

# Validate the example reference file
python3 scripts/validate_analysis.py references/vnrm-example.json
```

## Key Differences from Legacy Code Analysis

### Modern Architecture Focus
- **Microservice Patterns**: Service boundaries, API contracts, database-per-service
- **Cloud-Native Patterns**: Resilience patterns, monitoring, observability
- **Event-Driven Architecture**: Message Bus integration, domain events, CQRS patterns
- **DevOps Integration**: CI/CD pipelines, containerization, deployment patterns

### VNRM-Specific Elements
- **Telecommunications Domain**: Number management, porting workflows, BNetzA compliance
- **State Machines**: Callnumber states, porting states, business process states
- **Regulatory Compliance**: GDPR, BNetzA requirements, audit trails
- **Performance Requirements**: HA (High Availability), OT (Office Time), BE (Best Effort) service levels

### Technology Stack Analysis
- **Spring Boot Patterns**: Configuration management, dependency injection, data access
- **PostgreSQL Features**: Partitioning, indexing strategies, JSON columns, audit tables
- **Resilience4j Integration**: Circuit breakers, retry policies, bulkhead patterns
- **Tardis Platform**: Authentication (Iris/Stargate), messaging (Horizon), monitoring

## Best Practices

### Analysis Approach
1. **Service Boundary Analysis**: Understand the bounded context and domain responsibility
2. **API Contract Extraction**: Document all REST endpoints with complete schemas
3. **Data Model Understanding**: Map JPA entities to business domain concepts
4. **Integration Mapping**: Trace all service dependencies and external integrations
5. **Operational Assessment**: Evaluate current performance and monitoring capabilities

### Documentation Quality
1. **Accuracy**: Reflect actual implementation, not just intended design
2. **Completeness**: Cover all API endpoints, database tables, and integrations
3. **Traceability**: Link code artifacts to business requirements
4. **Operational Context**: Include deployment, monitoring, and operational characteristics
5. **Enhancement Focus**: Identify concrete opportunities for improvement

### VNRM-Specific Considerations
1. **State Machine Documentation**: Capture complete state transition logic and business rules
2. **Regulatory Compliance**: Document how BNetzA and GDPR requirements are implemented
3. **Performance Classification**: Understand HA/OT/BE service level requirements
4. **Integration Dependencies**: Map critical dependencies like config-server and RDM services
5. **Telecommunications Context**: Understand number management, porting, and carrier operations

## Related Skills

| Skill | Relationship |
|-------|--------------|
| **06-vnrm-analysis-workflow** | Phase 6 workflow that generates analysis.json using this schema |
| **07-1-microservice-delta-workflow** | Phase 7.1 uses analysis.json as baseline for delta computation |
| **gap-analysis-workflow** | Phase 9 uses analysis.json for effective VNRM state |
| **12-unit-test-generation-workflow** | Phase 12 uses test_infrastructure for REUSE/MODIFY/NEW classification |
| **13-source-code-generation-workflow** | Phase 13.1 uses repository_path for direct code application |
