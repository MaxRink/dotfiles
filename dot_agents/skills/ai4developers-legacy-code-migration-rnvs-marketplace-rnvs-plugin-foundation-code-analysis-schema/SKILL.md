---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-foundation-code-analysis-schema
description: Provides the comprehensive JSON schema for Phase 1 code analysis output in the RNVS→VNRM migration workflow. This skill should be used when generating Phase 1 analysis.json output, validating Phase 1 results, or when downstream phases need to understand the structure of code analysis data. The schema captures legacy code components, dependencies, business rules, and migration-specific metadata needed for transformation planning.
allowed-tools: Read
user-invocable: false
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/foundation/skills/code-analysis-schema by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Code Analysis Schema

## Overview

Defines the structured JSON format for Phase 1 code analysis output in legacy-to-modern system migrations. The schema captures components, dependencies, business logic, and migration planning metadata in a machine-readable format optimized for downstream workflow phases.

## When to Use

- **Phase 1 Code Analysis**: Generate analysis.json following this schema
- **Output Validation**: Validate Phase 1 results against schema requirements
- **Downstream Phases**: Parse analysis.json to extract components, dependencies, and planning data
- **Migration Planning**: Extract effort estimates, risk assessments, and modernization opportunities

## Schema Overview

The complete JSON schema structure includes:

```json
{
  "feature_name": "string (kebab-case)",
  "feature_description": "High-level overview",
  "analysis_timestamp": "ISO8601",
  "source_files": [...],
  "components": [...],
  "functions": [...],
  "dependencies": [...],
  "database_entities": [...],
  "external_integrations": [...],
  "translations": [...],
  "architecture_notes": {...},
  "migration_assessment": {...}
}
```

### Key Sections

**Core Analysis**:
- `source_files`: All analyzed source files with language and purpose
- `components`: Primary analysis units with pseudocode and business rules
- `functions`: Detailed function-level analysis with complexity
- `dependencies`: Component-to-component and external dependencies

**Integration Points**:
- `database_entities`: Tables/views/procedures with access patterns
- `external_integrations`: External systems with protocols and criticality
- `translations`: German-English telecommunications terminology

**Migration Planning** (Critical for workflow):
- `architecture_notes`: Cross-cutting patterns, performance, security, compliance
- `migration_assessment`: Complexity, effort, risks, testing, API contracts, modernization opportunities

## Usage

### For Phase 1 Agents

Generate analysis.json following the schema structure.

**See [references/schema.json](references/schema.json) for complete JSON Schema.**

**See [references/example-generic-authentication.json](references/example-generic-authentication.json) for a complete generic example (User Authentication System).**

### For Validation

Validate generated analysis.json:

```bash
python3 scripts/validate_analysis.py /path/to/results/feature-name/phase1/analysis.json
```

The validator checks required fields, types, enum values, and referential integrity.

### For Downstream Phases

Parse analysis.json to extract:
- Components and dependencies for Phase 2 diagrams
- Business rules for Phase 3-4 analysis
- Migration assessment for effort planning
- API contracts for interface design
- Testing considerations for test scenario generation

**See [references/field_guide.md](references/field_guide.md) for detailed field explanations when parsing complex sections.**

## Best Practices

1. **Completeness**: Populate all required fields; optional fields provide value for downstream phases
2. **Traceability**: Always include source references (file:line) for verification
3. **Confidence Scoring**: Mark confidence level when analysis is uncertain
4. **Migration Context**: Always populate migration_assessment for planning purposes
5. **Business Rules**: Extract business rules explicitly - they drive modernization design
6. **RNVS Code Search Priority**: In RNVS systems, the most business logic resides in PL/SQL files (pack_body_*.sql, p_*.sql packages). Prioritize analyzing PL/SQL packages and procedures for business rule extraction before analyzing Java/C++ orchestration code.

## Progressive Disclosure

- **SKILL.md** (this file) - Overview, when to use, schema structure summary
- **[references/schema.json](references/schema.json)** - Complete JSON Schema with validation rules
- **[references/field_guide.md](references/field_guide.md)** - Detailed field-by-field documentation with examples and enums
- **[references/example-generic-authentication.json](references/example-generic-authentication.json)** - Complete generic example (User Authentication System)
- **scripts/validate_analysis.py** - Executable validator script (Python 3.10+)

**Load schema.json when**: Need to see complete JSON Schema structure with all validation rules

**Load field_guide.md when**: Need detailed explanations of individual fields, valid enum values, or usage examples

**Load example-generic-authentication.json when**: Need to see a complete working example with all fields populated

**Run validate_analysis.py**: For programmatic validation from command line (requires jsonschema library)
