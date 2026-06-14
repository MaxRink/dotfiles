# Phase 1 Code Analysis Schema - Field Guide

Complete reference for all fields in analysis.json with explanations, valid values, and usage guidelines.

## Top-Level Fields

### feature_name (required)
- **Type**: string
- **Format**: kebab-case (lowercase with hyphens)
- **Example**: `"pda-import"`, `"number-portability"`, `"call-routing"`
- **Purpose**: Unique identifier for the feature being analyzed

### feature_description (required)
- **Type**: string
- **Min length**: 50 characters
- **Purpose**: High-level overview of feature purpose, scope, and business context
- **Should include**: What the feature does, why it exists, key business requirements
- **Example**: "The PDA Import feature is a critical data exchange system that imports porting data messages from external telecommunications network providers..."

### analysis_timestamp (required)
- **Type**: string (ISO8601 date-time)
- **Example**: `"2025-01-24T10:30:00.000Z"`
- **Purpose**: Records when analysis was performed for version tracking

---

## source_files (optional)

Array documenting all source files analyzed for this feature.

### path (required)
- **Type**: string
- **Format**: Relative path from repository root
- **Example**: `"script/start.pda_import.tcl"`, `"src/main/java/com/example/Service.java"`

### language (required)
- **Type**: enum
- **Valid values**: `"Java"`, `"PL/SQL"`, `"C++"`, `"TCL"`, `"JavaScript"`, `"Python"`, `"Shell"`
- **Purpose**: Identifies programming language for multi-language codebase tracking

### purpose (required)
- **Type**: string
- **Example**: `"Main orchestration script"`, `"Phone number validation service"`
- **Purpose**: Describes file's role in the feature

### lines_of_code (optional)
- **Type**: integer (≥0)
- **Purpose**: Size metric for effort estimation

### last_modified (optional)
- **Type**: string (ISO8601 date-time)
- **Purpose**: Tracks code freshness and maintenance activity

---

## components (required, min 1 item)

Primary analysis units representing logical system components.

### name (required)
- **Type**: string
- **Format**: PascalCase
- **Example**: `"PDAImportOrchestrator"`, `"NumberPortingController"`, `"RfNrMessageImport"`
- **Purpose**: Unique identifier for component

### type (required)
- **Type**: enum
- **Valid values**:
  - `"controller"`: HTTP/API request handlers
  - `"service"`: Business logic layer
  - `"repository"`: Data access layer
  - `"entity"`: Domain model/data structure
  - `"utility"`: Helper functions
  - `"orchestrator"`: Workflow coordination
  - `"processor"`: Data transformation/processing
  - `"validator"`: Validation logic

### language (required)
- **Type**: enum
- **Valid values**: `"Java"`, `"PL/SQL"`, `"C++"`, `"TCL"`, `"JavaScript"`, `"Python"`, `"Shell"`

### source (required)
- **Type**: string
- **Format**: `file:line_start-line_end`
- **Example**: `"script/start.pda_import.tcl:1-122"`
- **Purpose**: Source code traceability

### description (required)
- **Type**: string
- **Purpose**: Component purpose and functionality summary
- **Should include**: What it does, key responsibilities, business context

### pseudocode (required)
- **Type**: string
- **Min length**: 50 characters
- **Purpose**: Language-agnostic pseudocode representation of component logic
- **Format**: Structured pseudocode with control flow, function calls, business logic
- **Should include**: Initialization, main processing steps, decision points, error handling

### complexity (required)
- **Type**: enum
- **Valid values**:
  - `"low"`: Simple logic, few dependencies, straightforward flow
  - `"medium"`: Moderate logic, some dependencies, conditional flow
  - `"high"`: Complex logic, many dependencies, intricate control flow
- **Purpose**: Effort and risk estimation

### confidence (required)
- **Type**: enum
- **Valid values**:
  - `"low"`: Analysis incomplete or uncertain
  - `"medium"`: Most logic understood, some gaps
  - `"high"`: Complete understanding of component
- **Purpose**: Quality indicator for planning

### business_rules (optional)
- **Type**: array of strings
- **Example**: `["Files processed serially for data consistency", "Return codes 0-3 indicate success"]`
- **Purpose**: Explicit business constraints that drive design decisions
- **Should capture**: Validation rules, processing constraints, regulatory requirements

### dependencies (optional)
- **Type**: array of strings (component names)
- **Example**: `["FileProcessor", "DatabaseAccessLayer"]`
- **Purpose**: Component-level dependencies for architecture understanding

### database_access (optional)
- **Type**: array of strings (table/view names)
- **Example**: `["t_tr_tlnrfnr", "t_pi_portinfo"]`
- **Purpose**: Database entity references for migration planning

### external_systems (optional)
- **Type**: array of strings (system names)
- **Example**: `["BNetzA", "SQL*Plus", "FileSystem"]`
- **Purpose**: External integration points

### modernization_notes (optional)
Object capturing modernization opportunities.

#### technical_debt
- **Type**: string
- **Example**: `"Uses TCL orchestration instead of modern workflow engine"`
- **Purpose**: Identifies code quality issues

#### refactoring_opportunities
- **Type**: array of strings
- **Example**: `["Extract validation logic to separate service", "Replace file polling with event-driven approach"]`
- **Purpose**: Improvement suggestions

#### modern_patterns
- **Type**: array of strings
- **Example**: `["Use Spring Batch for orchestration", "Implement circuit breaker for external calls"]`
- **Purpose**: Recommended patterns for VNRM implementation

### notes (optional)
- **Type**: string
- **Purpose**: Additional implementation observations or context

---

## functions (optional)

Detailed function-level analysis within components.

### name (required)
- **Type**: string
- **Example**: `"processImportFile"`, `"validatePortingDate"`

### component (required)
- **Type**: string (component name reference)
- **Purpose**: Links function to parent component

### signature (required)
- **Type**: string
- **Example**: `"import_phone_number_messages(log_path, log_name, input_filename, trace_level, OUT return_code)"`

### purpose (required)
- **Type**: string
- **Purpose**: What the function does

### pseudocode (required)
- **Type**: string
- **Purpose**: Language-agnostic function logic

### complexity (required)
- **Type**: enum
- **Valid values**: `"low"`, `"medium"`, `"high"`

### source_reference (required)
- **Type**: string
- **Format**: `file:line`
- **Example**: `"script/pda_import_aux.tcl:45"`

### parameters (optional)
- **Type**: array of strings
- **Format**: `"name: type"`
- **Example**: `["input_file: string", "trace_level: integer"]`

### return_type (optional)
- **Type**: string
- **Example**: `"integer (return code)"`, `"List<PhoneNumber>"`

### side_effects (optional)
- **Type**: array of strings
- **Example**: `["Database write", "File system modification", "External API call"]`
- **Purpose**: Documents non-pure function behavior

---

## dependencies (optional)

Component-to-component and external dependencies.

### from (required)
- **Type**: string (component name)

### to (required)
- **Type**: string (component name)

### type (required)
- **Type**: enum
- **Valid values**:
  - `"calls"`: Direct function/method invocation
  - `"uses"`: Utilizes functionality
  - `"extends"`: Inheritance
  - `"implements"`: Interface implementation
  - `"triggers"`: Event-based activation
  - `"depends_on"`: General dependency

### description (optional)
- **Type**: string
- **Purpose**: Nature of dependency

### criticality (optional)
- **Type**: enum
- **Valid values**: `"low"`, `"medium"`, `"high"`
- **Purpose**: Impact if dependency breaks

### migration_impact (optional)
- **Type**: string
- **Purpose**: Migration considerations for this dependency

---

## database_entities (optional)

Database tables, views, procedures accessed by the feature.

### name (required)
- **Type**: string
- **Example**: `"t_tr_tlnrfnr"`, `"v_active_numbers"`, `"p_import_data"`

### type (required)
- **Type**: enum
- **Valid values**: `"table"`, `"view"`, `"procedure"`, `"function"`, `"sequence"`

### description (optional)
- **Type**: string
- **Example**: `"Telephone numbers master table"`

### accessed_by (required)
- **Type**: array of strings (component names)
- **Purpose**: Which components interact with this entity

### access_pattern (optional)
- **Type**: enum
- **Valid values**: `"read"`, `"write"`, `"read_write"`

### criticality (optional)
- **Type**: enum
- **Valid values**: `"low"`, `"medium"`, `"high"`
- **Purpose**: Impact if entity is unavailable

### migration_strategy (optional)
- **Type**: enum
- **Valid values**:
  - `"migrate"`: Move as-is to new system
  - `"replace"`: Redesign with modern structure
  - `"consolidate"`: Merge with other entities
  - `"split"`: Decompose into multiple entities

---

## external_integrations (optional)

External systems, APIs, file systems, message queues.

### system (required)
- **Type**: string
- **Example**: `"BNetzA"`, `"Oracle Database"`, `"FileSystem"`

### protocol (required)
- **Type**: enum
- **Valid values**: `"REST"`, `"SOAP"`, `"Database"`, `"MessageQueue"`, `"FileSystem"`, `"FTP"`, `"Email"`, `"Custom"`

### description (optional)
- **Type**: string
- **Purpose**: Integration purpose and data exchanged

### used_by (required)
- **Type**: array of strings (component names)

### data_format (optional)
- **Type**: enum
- **Valid values**: `"JSON"`, `"XML"`, `"CSV"`, `"Binary"`, `"Custom"`

### frequency (optional)
- **Type**: enum
- **Valid values**: `"realtime"`, `"batch"`, `"scheduled"`, `"event-driven"`

### criticality (optional)
- **Type**: enum
- **Valid values**: `"low"`, `"medium"`, `"high"`

### migration_strategy (optional)
- **Type**: enum
- **Valid values**:
  - `"preserve"`: Keep interface as-is (regulatory/external requirement)
  - `"modernize"`: Update to modern protocol/format
  - `"replace"`: Completely redesign integration

---

## translations (optional)

German-English telecommunications terminology.

### german (required)
- **Type**: string
- **Example**: `"Rufnummernblock"`

### english (required)
- **Type**: string
- **Example**: `"Number Block"`

### abbreviation (optional)
- **Type**: string
- **Example**: `"RNB"`

### context (required)
- **Type**: string
- **Purpose**: Telecommunications/business context where term is used

### occurrences (optional)
- **Type**: array of strings (`file:line` references)
- **Purpose**: Traceability for translation verification

### domain (optional)
- **Type**: enum
- **Valid values**: `"telecommunications"`, `"business"`, `"technical"`

---

## architecture_notes (optional)

Cross-cutting architectural observations and patterns.

### data_flow (optional)
- **Type**: string
- **Purpose**: Describes how data flows through the system

### processing_model (optional)
- **Type**: enum
- **Valid values**: `"batch"`, `"realtime"`, `"scheduled"`, `"event-driven"`, `"hybrid"`

### key_patterns (optional)
- **Type**: array of strings
- **Example**: `["ETL pipeline", "Event-driven processing", "Database-centric design"]`

### performance_considerations (optional)
- **Type**: array of strings
- **Example**: `["Parallel processing with 4 workers", "2-hour batch window"]`

### error_handling (optional)
- **Type**: string
- **Purpose**: Error handling approach and recovery mechanisms

### security_notes (optional)
- **Type**: string
- **Purpose**: Security mechanisms and considerations

### scalability_notes (optional)
- **Type**: string
- **Purpose**: Scalability approach and limitations

### regulatory_compliance (optional)
- **Type**: array of strings
- **Example**: `["BNetzA reporting", "GDPR data retention"]`

### technology_stack (optional)
Object documenting technologies used.

#### languages
- **Type**: array of strings

#### frameworks
- **Type**: array of strings

#### tools
- **Type**: array of strings

---

## migration_assessment (required)

Migration-specific planning metadata.

### overall_complexity (required)
- **Type**: enum
- **Valid values**:
  - `"low"`: Straightforward migration, few dependencies
  - `"medium"`: Moderate complexity, some challenges
  - `"high"`: Complex migration, many dependencies
  - `"very_high"`: Extremely complex, high risk

### estimated_effort_days (required)
- **Type**: number (≥0)
- **Purpose**: Development effort estimate in person-days

### risk_level (required)
- **Type**: enum
- **Valid values**: `"low"`, `"medium"`, `"high"`

### risk_factors (optional)
- **Type**: array of strings
- **Example**: `["Multi-language codebase", "Critical batch window", "Regulatory compliance"]`

### migration_priority (required)
- **Type**: enum
- **Valid values**: `"low"`, `"medium"`, `"high"`, `"critical"`

### blockers (optional)
- **Type**: array of strings
- **Purpose**: Migration impediments that must be resolved

### prerequisites (optional)
- **Type**: array of strings
- **Purpose**: What must be complete before starting this migration

### testing_considerations (optional)
Object documenting testing requirements.

#### critical_paths
- **Type**: array of strings
- **Purpose**: Must-test scenarios

#### data_migration_complexity
- **Type**: enum
- **Valid values**: `"low"`, `"medium"`, `"high"`

#### performance_test_requirements
- **Type**: array of strings

#### regulatory_test_requirements
- **Type**: array of strings

### api_contracts (optional)
Object documenting interface requirements.

#### interfaces_to_preserve
- **Type**: array of objects
- **Purpose**: Interfaces that must remain unchanged (regulatory/external)

#### new_interfaces_needed
- **Type**: array of objects
- **Purpose**: New interfaces to design

### modernization_opportunities (optional)
Object capturing improvement opportunities.

#### technical_debt_items
- **Type**: array of strings

#### performance_improvements
- **Type**: array of strings

#### architecture_improvements
- **Type**: array of strings

### data_migration (optional)
Object documenting data migration strategy.

#### historical_data_volume
- **Type**: string
- **Example**: `"10M records"`, `"500GB"`

#### migration_strategy
- **Type**: enum
- **Valid values**:
  - `"parallel_run"`: Run old and new systems simultaneously
  - `"big_bang"`: Switch at once
  - `"phased"`: Gradual rollout

#### rollback_complexity
- **Type**: enum
- **Valid values**: `"low"`, `"medium"`, `"high"`

#### data_validation_requirements
- **Type**: array of strings
- **Purpose**: Data integrity checks required
