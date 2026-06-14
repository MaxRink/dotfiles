---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-workflow-13-source-code-generation-workflow
description: Generate or apply production-ready source code for VNRM microservices. NEW mode generates complete microservice to results/. CHANGE mode applies delta changes to existing repository.
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Task, AskUserQuestion
user-invocable: true
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/workflow/skills/13-source-code-generation-workflow by codex-knowledge-curation/scripts/persist_project_skills.py. -->

<required_reading>
Read `results/${FEATURE}/.workflow-state.md` before any operation.
This provides workflow mode (NEW or CHANGE), completed phases, and session context.
Use Mode from state file to determine Phase 13 (NEW) vs Phase 13.1 (CHANGE).
</required_reading>

<anti_hallucination_rules>
**CRITICAL**: Before generating ANY source code:

1. **Verify methods exist** - Only generate calls to methods defined in Phase 7/7.1 design
2. **Verify fields exist** - Only use entity fields from Phase 7/7.1 data model
3. **Verify imports resolve** - Only import classes that exist or will be generated
4. **Match test references** - Reference ACTUAL Phase 12 test methods, not invented ones
5. **Use Horizon, NOT Kafka** - VNRM uses Telekom Event Bus (HorizonClient)
6. **Follow package structure** - Use `de.telekom.vnrm.{submodule}` pattern
7. **No arbitrary business logic** - Only implement documented business rules from Phase 3
8. **Preserve existing code** - MODIFY operations must not break existing functionality

Failure to follow these rules causes compilation failures and integration issues.
</anti_hallucination_rules>

---

# Source Code Generation Workflow

## Purpose

Generate production-ready source code for VNRM microservices. Supports two modes:

- **Phase 13 (NEW mode)**: Generate complete microservice codebase (50-100 files) to results/ folder
- **Phase 13.1 (CHANGE mode)**: Apply targeted changes to existing VNRM repository (5-15 files)

## When to Use

- **Phase 13 (NEW)**: After Phase 7 microservice design, generate complete new microservice
- **Phase 13.1 (CHANGE)**: After Phase 7.1 delta design, apply changes to existing repository
- After Phase 12 unit tests are generated (tests to implement against)
- When you need to apply NEW and MODIFIED files

---

## PRE-FLIGHT VALIDATION CHECKLIST

**MANDATORY: Execute this checklist BEFORE starting any stage.**

```
□ Step 1: Read .workflow-state.md
  - Extract: workflow_mode (NEW or CHANGE)
  - Extract: feature_name
  - Verify: Phase 12 is marked complete

□ Step 2: Verify Input Files Exist
  NEW Mode:
    □ results/${FEATURE}/phase7/microservice-design.json
    □ results/${FEATURE}/phase12/unit-tests.json
    □ results/${FEATURE}/phase3/ruletable.json

  CHANGE Mode:
    □ results/${FEATURE}/phase6/vnrm-analysis.json (contains repository_path)
    □ results/${FEATURE}/phase7.1/microservice-delta.json
    □ results/${FEATURE}/phase12/unit-tests.json
    □ results/${FEATURE}/phase3/ruletable.json

□ Step 3: Determine Output Strategy
  NEW Mode → Output to: results/${FEATURE}/phase13/src/main/java/
  CHANGE Mode → Output to: ${repository_path}/src/main/java/

□ Step 4: Verify Repository Access (CHANGE Mode Only)
  - Read repository_path from phase6/vnrm-analysis.json
  - Verify path exists and is writable
  - Identify source_root (default: "src/main/java")

STOP if any checkbox fails. Report missing prerequisites.
```

## Key Difference: Phase 13 vs Phase 13.1

| Aspect | Phase 13 (NEW) | Phase 13.1 (CHANGE) |
|--------|----------------|---------------------|
| **Scope** | Complete microservice codebase | Only changed/new files |
| **Input** | Phase 7 full design | Phase 6 baseline + Phase 7.1 delta |
| **Output Size** | 50-100 files | 5-15 files |
| **Pattern** | Full project scaffold | Direct repository edits |
| **Target** | `results/${FEATURE}/phase13/` | **Actual VNRM repository** |
| **Tools Used** | Write only | **Edit + Write** |
| **Context** | No existing code | Existing codebase to modify |

---

## Phase 13 (NEW Mode) - Complete Microservice Generation

When `workflow_mode = "NEW"`, generate a complete microservice to results folder.

### NEW Mode Output Structure

```
results/${FEATURE}/phase13/
├── pom.xml                                    # Maven build file
├── src/main/java/de/telekom/vnrm/${submodule}/
│   ├── ${Module}Application.java              # Spring Boot main class
│   ├── controller/
│   │   └── ${Resource}Controller.java         # REST controllers
│   ├── service/
│   │   ├── ${Resource}Service.java            # Service interfaces
│   │   └── impl/
│   │       └── ${Resource}ServiceImpl.java    # Service implementations
│   ├── repository/
│   │   └── ${Resource}Repository.java         # JPA repositories
│   ├── entity/
│   │   ├── ${Resource}.java                   # JPA entities
│   │   └── ${Resource}Status.java             # Status enums
│   ├── dto/
│   │   ├── ${Resource}Request.java            # Request DTOs
│   │   └── ${Resource}Response.java           # Response DTOs
│   ├── mapper/
│   │   └── ${Resource}Mapper.java             # MapStruct mappers
│   ├── event/
│   │   ├── ${Event}Handler.java               # Horizon event handlers
│   │   └── ${Event}Payload.java               # Event DTOs
│   ├── config/
│   │   ├── ${Module}Properties.java           # Configuration properties
│   │   └── ${Module}Configuration.java        # Bean configuration
│   └── exception/
│       ├── ${Resource}NotFoundException.java  # Custom exceptions
│       └── GlobalExceptionHandler.java        # Exception handler
├── src/main/resources/
│   ├── application.yml                        # Application config
│   ├── application-local.yml                  # Local dev config
│   └── db/
│       └── changelog/
│           ├── db.changelog-master.yaml       # Liquibase master
│           └── changes/
│               └── V${version}__initial.yaml  # Initial schema
└── source-code.json                           # Generation metadata
```

### NEW Mode Generation Steps

1. **Generate pom.xml** with all dependencies (Spring Boot, Lombok, MapStruct, Horizon, Resilience4j)
2. **Generate Application class** with `@SpringBootApplication`
3. **Generate entities** from Phase 7 data model
4. **Generate repositories** with custom query methods
5. **Generate services** implementing Phase 3 business rules
6. **Generate controllers** for Phase 7 API endpoints
7. **Generate DTOs and mappers** for request/response transformation
8. **Generate event handlers** for Horizon integration
9. **Generate configuration** classes and application.yml
10. **Generate exceptions** and global exception handler
11. **Generate Liquibase migrations** for database schema
12. **Generate source-code.json** metadata file

### NEW Mode Metadata (source-code.json)

```json
{
  "phase": "Phase 13",
  "feature": "${FEATURE}",
  "mode": "NEW",
  "generated": "ISO-8601 timestamp",
  "summary": {
    "total_files": 50,
    "controllers": 3,
    "services": 5,
    "repositories": 4,
    "entities": 6,
    "dtos": 8,
    "event_handlers": 2,
    "config_files": 3,
    "migrations": 2
  },
  "business_rules_implemented": ["BR-001", "BR-002", "..."],
  "test_references": {
    "total": 50,
    "coverage": "100%"
  }
}
```

---

## Phase 13.1 (CHANGE Mode) - Delta Application

When `workflow_mode = "CHANGE"`, apply targeted changes to existing VNRM repository.

### Agent Guidance

When invoked as an agent for Phase 13.1, follow this methodology:

### Stage 1: Read Context and Locate VNRM Repository

Read all required inputs in parallel:

```
1. results/${FEATURE}/phase6/analysis.json
   - **CRITICAL**: Extract `repository_path` - the absolute path to the VNRM repo
   - Existing service structure
   - Current API contracts
   - Current database schema

2. results/${FEATURE}/phase13.1/computed-code-delta.json
   - Lists files to CREATE and MODIFY
   - Contains implementation requirements for each file

3. results/${FEATURE}/phase13.1/classification.json
   - REUSE/MODIFY/NEW classification per file
   - Complexity score and quality target

4. results/${FEATURE}/phase7.1/microservice-changes-design.json
   - API changes (endpoints_to_add, endpoints_to_modify)
   - Database changes (tables_to_add, columns_to_add)
   - Event changes (topics_to_add, subscriptions_to_add)

5. results/${FEATURE}/phase12/unit_tests/java/
   - Generated unit tests to implement against
```

**After reading, verify**:
- `repository_path` exists and is accessible
- The repository structure matches Phase 6 analysis

### Stage 2: Apply NEW Files to VNRM Repository

For each file in `files_to_create`:

1. **Determine file type** (controller, service, repository, dto, migration)
2. **Read corresponding pattern** from `patterns/` directory
3. **Use Write tool** to create file in ACTUAL VNRM repo:
   - Target: `${repository_path}/src/main/java/.../NewController.java`
   - **NOT**: `results/${FEATURE}/phase13.1/source_code/...`
4. **Generate complete file** with:
   - Package declaration matching existing structure
   - All required imports
   - Class annotations (Spring Boot: @RestController, @Service, etc.)
   - Methods implementing the requirements
   - Javadoc comments with business rule references
   - Test method references

### Stage 3: Apply MODIFY Files to VNRM Repository

For each file in `files_to_modify`:

1. **Read existing file** from `${repository_path}/...`
2. **Use Edit tool** to apply changes:
   - Add new imports at top of imports section
   - Add new fields after existing fields
   - Add new methods after existing methods
3. **Preserve existing code** - only add, don't remove
4. **Log each edit operation** for the manifest

### Stage 4: Apply Database Migrations to VNRM Repository

For each entry in `migrations_needed`:

1. **List existing migrations** in `${repository_path}/src/main/resources/db/migration/`
2. **Determine next version number** (if V5 exists, use V6)
3. **Use Write tool** to create migration:
   - Target: `${repository_path}/src/main/resources/db/migration/V{N}__${description}.sql`

### Stage 5: Security Scan

Run security scan on all modified/created files in the VNRM repo:
- Check for SQL injection vulnerabilities
- Check for XSS vulnerabilities
- Check for hardcoded credentials
- Check for insecure randomness

Write results to `results/${FEATURE}/phase13.1/security_scan.txt`.

### Stage 6: Generate Applied Edits Log

Create `results/${FEATURE}/phase13.1/applied-edits-log.json` with:
```json
{
  "applied_at": "ISO timestamp",
  "feature": "feature-name",
  "repository_path": "/path/to/vnrm-repo",
  "files_created": [
    {
      "path": "src/main/java/com/vnrm/feature/controller/NewController.java",
      "absolute_path": "/path/to/vnrm-repo/src/main/java/.../NewController.java",
      "bytes": 2540,
      "implements": ["API-001", "BR-FEAT-005"]
    }
  ],
  "files_modified": [
    {
      "path": "src/main/java/com/vnrm/feature/service/ExistingService.java",
      "absolute_path": "/path/to/vnrm-repo/src/main/java/.../ExistingService.java",
      "edits_applied": 3,
      "changes": ["Added validateConfiguration method", "Added checkDependencies method"]
    }
  ],
  "migrations_created": [
    {
      "path": "src/main/resources/db/migration/V5__add_feature_config_table.sql",
      "absolute_path": "/path/to/vnrm-repo/src/main/resources/db/migration/V5__add_feature_config_table.sql"
    }
  ],
  "security_scan_status": "PASS"
}
```

### Stage 7: Generate Code Changes Manifest

Create `results/${FEATURE}/phase13.1/code-changes-manifest.json` summarizing all changes for documentation.

---

## Code Change Classification

Files are classified into three categories:

| Classification | Description | Action |
|----------------|-------------|--------|
| **REUSE** | Existing file, no changes needed | Skip |
| **MODIFY** | Existing file, add methods/fields | Generate Edit instructions |
| **NEW** | File does not exist | Generate complete file |

---

## Spring Boot Change Patterns

### New Controller

```java
package de.telekom.vnrm.${module}.controller;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import javax.validation.Valid;

/**
 * Controller for ${feature} operations.
 * Implements: ${api_requirement_ids}
 * Tested by: ${test_class}
 */
@RestController
@RequestMapping("/api/v1/${resource}")
@RequiredArgsConstructor
@Slf4j
public class ${FeatureName}Controller {

    private final ${FeatureName}Service ${featureName}Service;

    // Endpoints...
}
```

### New Service Method

```java
/**
 * ${method_description}
 * Implements: ${business_rule_id}
 * Tested by: ${test_method}
 */
@Transactional
public ${ReturnType} ${methodName}(${Parameters}) {
    log.info("${method_name} called with: {}", ${param});
    // Implementation...
}
```

### New Repository Query

```java
/**
 * ${query_description}
 * Used by: ${service_method}
 */
@Query("SELECT e FROM ${Entity} e WHERE ${condition}")
List<${Entity}> ${findByCondition}(@Param("param") ${ParamType} param);
```

---

## Database Migration Patterns

### Flyway Migration (V{N}__)

```sql
-- V${version}__${description}.sql
-- Feature: ${feature_name}
-- Implements: ${requirement_ids}

-- Forward migration
CREATE TABLE ${table_name} (
    id BIGSERIAL PRIMARY KEY,
    ${columns}
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_${table}_${column} ON ${table_name}(${column});

-- Add to existing table
ALTER TABLE ${existing_table}
ADD COLUMN ${new_column} ${data_type};
```

---

## Quality Gates

All generated code must pass these 5 gates:

### Gate 1: Structure Validation

| Check | Criteria | Pass If |
|-------|----------|---------|
| Package structure | `de.telekom.vnrm.{submodule}` | All files in correct packages |
| Annotations | Spring Boot annotations present | @Service, @Repository, @RestController |
| Imports | All imports resolve | No missing dependencies |
| Naming | Follows VNRM conventions | Controller, Service, Repository suffixes |

### Gate 2: Business Rule Coverage

| Check | Criteria | Pass If |
|-------|----------|---------|
| API coverage | Phase 7/7.1 endpoints | 100% endpoints have controllers |
| Service coverage | Phase 7/7.1 business rules | 100% rules implemented |
| DB coverage | Phase 7/7.1 schema changes | 100% tables/columns in migrations |

### Gate 3: Test Reference Validation

| Check | Criteria | Pass If |
|-------|----------|---------|
| Public methods | Reference Phase 12 tests | 100% methods have `Tested by:` |
| Business rules | Reference Phase 3 rules | 100% methods have `Implements:` |
| RNVS source | Reference legacy code | 100% methods have `RNVS Source:` |

### Gate 4: Security Validation

| Check | Criteria | Pass If |
|-------|----------|---------|
| SQL injection | No string concatenation in queries | 0 violations |
| XSS | No raw user input in responses | 0 violations |
| Credentials | No hardcoded secrets | 0 violations |
| Input validation | @Valid on request bodies | 100% endpoints |

### Gate 5: Compilation Verification

| Check | Criteria | Pass If |
|-------|----------|---------|
| Compile | `mvn test-compile` | BUILD SUCCESS |
| No errors | Compilation output | 0 errors |
| Warnings | Compilation warnings | < 10 warnings |

**BLOCKING**: All 5 gates must PASS before Phase 13 is complete.

---

## Output Structure

### Changes Applied to VNRM Repository

```
${VNRM_REPOSITORY_PATH}/                    ← ACTUAL changes applied here
├── src/main/java/com/vnrm/.../
│   ├── controller/
│   │   └── NewFeatureController.java       ← NEW (Write tool)
│   ├── service/
│   │   └── ExistingService.java            ← MODIFIED (Edit tool)
│   ├── repository/
│   │   └── NewFeatureRepository.java       ← NEW (Write tool)
│   └── dto/
│       └── FeatureRequest.java             ← NEW (Write tool)
└── src/main/resources/db/migration/
    └── V5__add_feature_config_table.sql    ← NEW (Write tool)
```

### Metadata in Results Directory

```
results/${FEATURE}/phase13.1/              ← Metadata only (NOT source code)
├── computed-code-delta.json               # From validation (Step 1)
├── classification.json                    # From validation (Step 1)
├── changes-quality-report.json            # From validation (Step 1)
├── applied-edits-log.json                 # Generated by agent (Stage 6)
├── code-changes-manifest.json             # Generated by agent (Stage 7)
└── security_scan.txt                      # Generated by agent (Stage 5)
```

**Key Point**: No `source_code/` directory - all source files go directly into the VNRM repository.

---

## Traceability Requirements

Every generated method MUST include full traceability:

```java
/**
 * Create new ${resource}.
 *
 * Implements: ${FEATURE}-BR-XXX - Business rule description
 * RNVS Source: ${rnvs_file}:${line} - Legacy code reference
 * Tested by: ${Resource}ControllerTest.shouldCreate${Resource}()
 * Tested by: ${Resource}ControllerTest.shouldRejectInvalidRequest()
 */
@PostMapping
public ResponseEntity<${Resource}Response> create${Resource}(...) {
```

### Traceability Format

| Annotation | Format | Example |
|------------|--------|---------|
| **Implements** | `${FEATURE}-BR-XXX - Description` | `RNBPORT-BR-046 - Queue status transitions` |
| **RNVS Source** | `${file}:${line}` | `problem_handler.tcl:234-289` |
| **Tested by** | `${TestClass}.${testMethod}()` | `ProblemQueueServiceTest.shouldCreatePmr()` |

### Why Traceability Matters

1. **Code Review**: Reviewers can verify business rule implementation
2. **Testing**: Developers can find related tests quickly
3. **Maintenance**: Future maintainers understand code purpose
4. **Audit**: Regulatory compliance requires traceable requirements

---

## Available Pattern Files

Reference these patterns when generating code:

| Pattern File | Use For |
|--------------|---------|
| `patterns/controller-change-patterns.md` | REST controllers, endpoints |
| `patterns/service-change-patterns.md` | Service classes, business logic |
| `patterns/repository-change-patterns.md` | JPA repositories, queries |
| `patterns/entity-patterns.md` | JPA entities, enums, auditing |
| `patterns/event-handler-patterns.md` | Horizon event handlers |
| `patterns/event-payload-patterns.md` | Event DTOs |
| `patterns/config-patterns.md` | Configuration properties classes |
| `patterns/exception-patterns.md` | Custom exceptions, global handler |
| `patterns/dto-mapper-patterns.md` | Request/Response DTOs, MapStruct |
| `patterns/migration-patterns.md` | Flyway SQL migrations |
| `patterns/liquibase-patterns.md` | Liquibase YAML migrations |
| `patterns/pom-xml-patterns.md` | Maven POM configuration |
| `patterns/application-yml-patterns.md` | Spring Boot configuration |
| `patterns/resilience-patterns.md` | Circuit breakers, retries, fallbacks |

---

## Success Criteria

Phase 13.1 is complete when:

- [ ] `repository_path` from Phase 6 is verified accessible
- [ ] All `files_to_create` have been written to the VNRM repository using Write tool
- [ ] All `files_to_modify` have been edited in the VNRM repository using Edit tool
- [ ] All database migrations have been created in `${repository_path}/src/main/resources/db/migration/`
- [ ] Security scan passes (no critical vulnerabilities)
- [ ] `applied-edits-log.json` exists with all applied changes documented
- [ ] `code-changes-manifest.json` exists with all mappings
- [ ] `security_scan.txt` exists with results

---

## Output Schema Definitions

### source-code.json (NEW Mode)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["phase", "feature", "mode", "generated", "summary"],
  "properties": {
    "phase": { "const": "Phase 13" },
    "feature": { "type": "string" },
    "mode": { "const": "NEW" },
    "generated": { "type": "string", "format": "date-time" },
    "summary": {
      "type": "object",
      "properties": {
        "total_files": { "type": "integer" },
        "controllers": { "type": "integer" },
        "services": { "type": "integer" },
        "repositories": { "type": "integer" },
        "entities": { "type": "integer" },
        "dtos": { "type": "integer" },
        "event_handlers": { "type": "integer" },
        "config_files": { "type": "integer" },
        "migrations": { "type": "integer" }
      }
    },
    "business_rules_implemented": {
      "type": "array",
      "items": { "type": "string" }
    },
    "test_references": {
      "type": "object",
      "properties": {
        "total": { "type": "integer" },
        "coverage": { "type": "string" }
      }
    },
    "files": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "path": { "type": "string" },
          "type": { "type": "string" },
          "implements": { "type": "array", "items": { "type": "string" } }
        }
      }
    }
  }
}
```

### code-changes-manifest.json (CHANGE Mode)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["phase", "feature", "mode", "generated", "status"],
  "properties": {
    "phase": { "const": "Phase 13.1" },
    "feature": { "type": "string" },
    "mode": { "const": "CHANGE" },
    "generated": { "type": "string", "format": "date-time" },
    "status": { "enum": ["COMPLETE", "PARTIAL", "FAILED"] },
    "target_repository": {
      "type": "object",
      "properties": {
        "name": { "type": "string" },
        "path": { "type": "string" },
        "base_package": { "type": "string" }
      }
    },
    "summary": {
      "type": "object",
      "properties": {
        "total_files": { "type": "integer" },
        "entities": { "type": "integer" },
        "services": { "type": "integer" },
        "event_handlers": { "type": "integer" },
        "events": { "type": "integer" },
        "config": { "type": "integer" },
        "exceptions": { "type": "integer" },
        "database_migrations": { "type": "integer" }
      }
    },
    "classification": {
      "type": "object",
      "properties": {
        "MODIFY": {
          "type": "object",
          "properties": {
            "count": { "type": "integer" },
            "components": { "type": "array", "items": { "type": "string" } }
          }
        },
        "NEW": {
          "type": "object",
          "properties": {
            "count": { "type": "integer" },
            "components": { "type": "array", "items": { "type": "string" } }
          }
        }
      }
    },
    "files": {
      "type": "object",
      "properties": {
        "entities": { "type": "array" },
        "services": { "type": "array" },
        "events": { "type": "array" },
        "config": { "type": "array" },
        "exceptions": { "type": "array" },
        "database": { "type": "array" }
      }
    },
    "horizon_events": {
      "type": "object",
      "properties": {
        "event_bus": { "const": "Horizon (Telekom Event Bus)" },
        "subscribed": { "type": "array", "items": { "type": "string" } },
        "published": { "type": "array", "items": { "type": "string" } }
      }
    }
  }
}
```

---

## PHASE13_SUMMARY.md Template

Generate this summary file upon completion:

```markdown
# Phase 13 Summary - ${FEATURE}

**Generated**: ${ISO_TIMESTAMP}
**Mode**: ${NEW|CHANGE}
**Status**: ${COMPLETE|PARTIAL}

## Overview

${Brief description of what was generated}

## Files Generated

| Category | Count | Files |
|----------|-------|-------|
| Entities | ${N} | ${list} |
| Services | ${N} | ${list} |
| Event Handlers | ${N} | ${list} |
| DTOs | ${N} | ${list} |
| Config | ${N} | ${list} |
| Exceptions | ${N} | ${list} |
| Migrations | ${N} | ${list} |
| **Total** | **${N}** | |

## Business Rules Implemented

| Rule ID | Description | Implemented In |
|---------|-------------|----------------|
| ${FEATURE}-BR-XXX | ${description} | ${service/method} |

## Technology Stack

- **Event Bus**: Horizon (Telekom Event Bus)
- **Framework**: Spring Boot 3.x
- **Database**: PostgreSQL with Liquibase
- **Resilience**: Resilience4j circuit breakers

## Quality Gates

| Gate | Status | Details |
|------|--------|---------|
| Structure | ${PASS/FAIL} | ${details} |
| Business Rules | ${PASS/FAIL} | ${coverage}% |
| Test References | ${PASS/FAIL} | ${coverage}% |
| Security | ${PASS/FAIL} | ${violations} violations |
| Compilation | ${PASS/FAIL} | ${mvn_result} |

## Next Steps

Proceed to **Phase 14: Test Script Generation**
```

---

## Package Naming Convention

**IMPORTANT**: All generated code must use the standard VNRM package structure:

```
de.telekom.vnrm.${submodule}
```

Examples:
- `de.telekom.vnrm.fbpm` - Fixed Block Porting Management
- `de.telekom.vnrm.num` - Number Management
- `de.telekom.vnrm.prt` - Porting Management

**DO NOT** use:
- `com.vnrm.*` (incorrect)
- `de.telekom.${other}.*` (non-standard)

---

## Related Skills

- `microservice-delta-design-guide` - Phase 7.1 delta model patterns
- `control-flow-delta-design-guide` - Phase 8.1 control flow changes
- `12-unit-test-generation-workflow` - Phase 12 test generation patterns
