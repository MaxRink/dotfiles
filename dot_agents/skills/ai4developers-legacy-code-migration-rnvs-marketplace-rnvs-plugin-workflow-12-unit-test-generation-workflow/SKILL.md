---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-workflow-12-unit-test-generation-workflow
description: Comprehensive methodology for Phase 12 JUnit unit test generation. Generates production-ready unit tests for VNRM microservice components including controllers, services, repositories, and event handlers. Supports both NEW and CHANGE workflows with REUSE/MODIFY/NEW classification for CHANGE mode.
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/workflow/skills/12-unit-test-generation-workflow by codex-knowledge-curation/scripts/persist_project_skills.py. -->

<required_reading>
Read `results/${FEATURE}/.workflow-state.md` before any operation.
This provides workflow mode (NEW or CHANGE), completed phases, and session context.
Use Mode from state file instead of directory-based detection.
</required_reading>

<anti_hallucination_rules>
**CRITICAL**: Before generating ANY test code:

1. **Verify methods exist** - Only test methods that exist in production code
2. **Verify fields exist** - Only use entity fields from Phase 7/7.1 design
3. **Use TestDataBuilder** - Never instantiate entities directly with `new Entity()`
4. **Use mocks correctly** - Every @Mock field must be used in at least one test
5. **JUnit 5 only** - Use `org.junit.jupiter.api.*`, never `org.junit.*`
6. **AssertJ only** - Use `assertThat()`, never `assertEquals()` or `assertTrue()`
7. **No arbitrary counts** - Don't use `verify(..., times(N))` without justification

Failure to follow these rules causes compilation failures.
</anti_hallucination_rules>

---

## SCOPE LIMITATION

This skill is designed for the **RNVS → VNRM migration project** only. It is NOT a general-purpose unit test generator.

| Works With | Does NOT Work With |
|------------|-------------------|
| RNVS features (NBM, FNPORT, PDA, KONTES, RNB-PORT, etc.) | Arbitrary Java projects |
| VNRM microservice architecture | Non-VNRM codebases |
| Telekom infrastructure (Horizon event bus) | Kafka-based systems |
| Spring Boot + JUnit 5 + Mockito + AssertJ | Other frameworks |
| The 15-phase RNVS workflow | Standalone test generation |

**Hard Dependencies**:
- RNVS workflow phases (reads from Phase 6, 7, 7.1, 11)
- VNRM package structure: `de.telekom.vnrm.{submodule}`
- Telekom event bus: Horizon (not Kafka)
- Workflow state file: `results/${FEATURE}/.workflow-state.md`

---

## FEATURE-AGNOSTIC DESIGN

This skill works for **any RNVS feature** within the VNRM migration context. Examples in this document are illustrative - always derive actual entities, services, and packages from the feature's Phase 7/7.1 design.

### Entity Discovery Process

```
BEFORE generating ANY test code:

1. READ the feature's Phase 7 or 7.1 design file:
   - NEW mode: results/${FEATURE}/phase7/microservice-design.json
   - CHANGE mode: results/${FEATURE}/phase7.1/microservice-delta.json

2. EXTRACT actual entities from design:
   - data_model.entities[] → Entity classes to test
   - components.services[] → Service classes to test
   - components.controllers[] → Controller classes to test
   - components.repositories[] → Repository classes to test

3. DERIVE TestDataBuilder from extracted entities:
   - Create builder methods for EACH entity in the feature
   - Use ACTUAL field names from entity definitions
   - Use ACTUAL enum values from design

4. GENERATE tests for ACTUAL components, not example components
```

### Package Structure

Derive submodule and package from Phase 6/7 analysis:

| Feature | Submodule | Package Path |
|---------|-----------|--------------|
| NBM | num | `de.telekom.vnrm.num` |
| FNPORT | prt | `de.telekom.vnrm.prt` |
| RNB-PORT | fbpm | `de.telekom.vnrm.fbpm` |
| PDA | prt.pda | `de.telekom.vnrm.prt.pda` |
| KONTES | num.kontes | `de.telekom.vnrm.num.kontes` |

### Example Entities

Examples in this skill use illustrative entities. Substitute with actual entities from your feature's design:

| Example Entity | Substitute With |
|----------------|-----------------|
| `ProblemMessage` | Your feature's main entity (e.g., `NumberBlock`, `PortingOrder`) |
| `QueueStatus` | Your feature's status enum (e.g., `BlockStatus`, `PortingState`) |
| `*Service` | Your feature's service (e.g., `NumberBlockService`, `PortingService`) |

---

# Unit Test Methodology

## Purpose

Provides comprehensive methodology for **Phase 12 unit test generation** - converting Phase 11 test scenarios into executable JUnit unit tests covering:

- **Controller Tests**: MockMvc API endpoint testing
- **Service Tests**: Business logic with mocked dependencies
- **Repository Tests**: Database interactions with TestContainers
- **Event Handler Tests**: Horizon (Telekom Event Bus) message processing with mocked HorizonClient
- **Utility Tests**: Helper classes and utilities

**Key Principle**: Phase 12 is UNIFIED - works for both NEW and CHANGE modes. Classification enables smart test generation in CHANGE mode.

## When to Use

Use this skill when you need to:

- **Generate Unit Tests** - Create JUnit 5 tests from Phase 11 test scenarios
- **Apply Test Patterns** - Mockito, MockMvc, TestContainers patterns
- **Handle CHANGE Mode** - Classify tests as REUSE/MODIFY/NEW based on Phase 6 test inventory
- **Ensure Coverage** - Target 80%+ line coverage for new/modified code
- **Follow TDD** - Red-green-refactor approach where applicable

**Phase Integration**: Used by `/rnvs-workflow:phase12-generate-unittests` command after Phase 11 system test scenarios.

---

## PRE-FLIGHT VALIDATION CHECKLIST

**MANDATORY: Execute this checklist BEFORE starting any stage.**

```
□ Step 1: Read .workflow-state.md
  - Extract: workflow_mode (NEW or CHANGE)
  - Extract: feature_name
  - Verify: Phase 11 is marked complete

□ Step 2: Verify Input Files Exist
  NEW Mode:
    □ results/${FEATURE}/phase11/system-test-scenarios.json
    □ results/${FEATURE}/phase7/microservice-design.json

  CHANGE Mode:
    □ results/${FEATURE}/phase11/system-test-scenarios.json
    □ results/${FEATURE}/phase6/vnrm-analysis.json (contains test_infrastructure)
    □ results/${FEATURE}/phase7.1/microservice-delta.json

□ Step 3: Determine Output Strategy
  NEW Mode → Output to: results/${FEATURE}/phase12/src/test/java/
  CHANGE Mode → Output to: ${repository_path}/${test_source_root}/ (from phase6)

□ Step 4: Verify Repository Access (CHANGE Mode Only)
  - Read repository_path from phase6/vnrm-analysis.json
  - Verify path exists and is writable
  - Identify test_source_root (default: "src/test/java")

STOP if any checkbox fails. Report missing prerequisites.
```

---

## Agent Guidance

When you are invoked to perform Phase 12 unit test generation:

**Input Files**:
- `results/${FEATURE}/phase11/system-test-scenarios.json` - Test scenarios to implement
- `results/${FEATURE}/phase11/PHASE11_SUMMARY.md` - Detailed scenario documentation

**Mode-Specific Inputs**:
- NEW mode: `results/${FEATURE}/phase7/microservice-design.json`
- CHANGE mode:
    - `results/${FEATURE}/phase6/vnrm-analysis.json` (baseline + test_infrastructure)
    - `results/${FEATURE}/phase7.1/microservice-delta.json` (delta)

**Your Task** (12 Stages with Quality Gates):
1. **Pre-flight Validation** - Verify all prerequisites
2. Load Phase 11 test scenarios and determine workflow mode
3. (CHANGE mode) Load existing test inventory for classification
4. Classify unit tests: Controller, Service, Repository, Event, Utility
   → **[GATE 1: Structure Validation]**
5. (CHANGE mode) Classify each test as REUSE/MODIFY/NEW
   → **[GATE 2: Classification Validation]** (CHANGE mode only)
6. Generate TestDataBuilder and test fixtures
7. Generate Mock configurations for external APIs
8. **(CHANGE mode) Apply tests to VNRM repository using Edit/Write tools**
   → **[GATE 5: Applied Edits Validation]** (CHANGE mode only)
9. Generate JUnit test classes (NEW mode only - CHANGE mode applies in Stage 8)
   → **[GATE 3: Code Quality Validation]**
10. Create test summary documentation and verification report
   → **[GATE 4: Coverage Validation]**
11. **Generate test-quality-report.json** - Compile all gate results
12. **Verify Compilation** - Run `mvn test-compile` to verify tests compile

**Outputs to Generate** (Mode-Dependent):

**NEW Mode** (Generate to results folder with Maven-standard structure):
```
results/${FEATURE}/phase12/
├── src/test/java/de/telekom/vnrm/{submodule}/
│   ├── controller/
│   │   └── *ControllerTest.java
│   ├── service/
│   │   └── *ServiceTest.java
│   ├── repository/
│   │   └── *RepositoryTest.java
│   ├── event/
│   │   └── *EventHandlerTest.java
│   └── testutil/
│       ├── TestDataBuilder.java
│       └── MockApiConfigurations.java
├── unit-tests.json                  # Test metadata
├── test-quality-report.json         # Quality gate results
├── traceability-matrix.json         # BR→TS→Test mapping
└── PHASE12_SUMMARY.md               # Documentation
```

**CHANGE Mode** (Generate to results folder, apply to VNRM repo separately):
```
results/${FEATURE}/phase12/
├── src/test/java/de/telekom/vnrm/{submodule}/
│   ├── service/
│   │   └── *ServiceTest.java        # NEW/MODIFY tests
│   ├── event/
│   │   └── *EventHandlerTest.java   # NEW/MODIFY tests
│   └── testutil/
│       └── TestDataBuilder.java
├── test-classification.json         # REUSE/MODIFY/NEW classification
├── unit-tests.json                  # Test metadata
├── test-quality-report.json         # Quality gate results
├── traceability-matrix.json         # BR→TS→Test mapping
└── PHASE12_SUMMARY.md               # Documentation
```

**Note**: In CHANGE mode, tests are generated to results folder first. Apply to VNRM repository using:
```bash
cp -r results/${FEATURE}/phase12/src/test/java/* ${repository_path}/src/test/java/
```


**Critical Requirements**:
- Use **JUnit 5** with `@Test`, `@BeforeEach`, `@DisplayName`
- Use **Mockito** for mocking: `@Mock`, `@InjectMocks`, `@MockBean`
- Use **MockMvc** for controller tests with `@WebMvcTest`
- Use **TestContainers** for repository tests with `@DataJpaTest`
- Use **mocked HorizonClient** for event handler tests (Telekom Event Bus)
- Follow **TDD approach**: Write failing test, implement, refactor
- Target **80%+ coverage** for new/modified components
- **ALWAYS generate TestDataBuilder** with entity builders

---

## Quick Reference

### Unit Test Classification by Component

| Component Type | Test Class Suffix | Framework | Mocking Strategy | Annotations |
|----------------|-------------------|-----------|------------------|-------------|
| Controller | `*ControllerTest` | MockMvc | @MockBean | `@WebMvcTest` |
| Service | `*ServiceTest` | JUnit 5 | @Mock + @InjectMocks | `@ExtendWith(MockitoExtension.class)` |
| Repository | `*RepositoryTest` | TestContainers | @DataJpaTest | `@DataJpaTest`, `@Testcontainers` |
| Event Handler | `*EventHandlerTest` | Mockito | @Mock HorizonClient | `@ExtendWith(MockitoExtension.class)` |
| Utility | `*UtilTest` | JUnit 5 | None (unit) | `@ExtendWith(MockitoExtension.class)` |

### CHANGE Mode Classification

| Classification | When to Use | Action | Expected % |
|----------------|-------------|--------|------------|
| **REUSE** | Existing test covers unchanged component | Log reference only | 30-50% |
| **MODIFY** | Existing test covers changed component | Add new test methods via Edit | 20-30% |
| **NEW** | No existing test for new component | Create full test class via Write | 30-40% |

### Test File Naming and Package Structure

**Standard Maven test source structure** (applies to both modes):

```
src/test/java/de/telekom/vnrm/{submodule}/
├── controller/                          # @WebMvcTest controllers
│   └── *ControllerTest.java
├── service/                             # @ExtendWith(MockitoExtension) services
│   └── *ServiceTest.java
├── repository/                          # @DataJpaTest with TestContainers
│   └── *RepositoryTest.java
├── event/                               # Event handlers with mocked HorizonClient
│   └── *EventHandlerTest.java
├── resilience/                          # Circuit breaker tests (if applicable)
│   └── *CircuitBreakerTest.java
└── testutil/                            # Test utilities (REQUIRED)
    ├── TestDataBuilder.java             # Fluent entity builders
    └── MockApiConfigurations.java       # External API mocks
```

**Submodule derived from Phase 6/7** (examples):
| Feature | Submodule | Package Path |
|---------|-----------|--------------|
| RNB-PORT | fbpm | `de.telekom.vnrm.fbpm` |
| NBM | num | `de.telekom.vnrm.num` |
| FNPORT | prt | `de.telekom.vnrm.prt` |
| PDA | prt.pda | `de.telekom.vnrm.prt.pda` |
| KONTES | num.kontes | `de.telekom.vnrm.num.kontes` |

**Note**: Derive actual submodule from `results/${FEATURE}/phase6/vnrm-analysis.json` or `phase7/microservice-design.json`.

---

## Instructions

### Stage 1: Pre-flight Validation

**Objective**: Ensure all prerequisites are met before starting.

**Actions**:
```
1. Read results/${FEATURE}/.workflow-state.md
   Extract: workflow_mode, feature_name, completed_phases

2. VERIFY Phase 11 is complete:
   - Check "Phase 11" in completed_phases list
   - If missing, STOP and report: "Phase 11 must be complete before Phase 12"

3. VERIFY Input files exist:
   - Glob for results/${FEATURE}/phase11/system-test-scenarios.json
   - If missing, STOP and report: "Missing Phase 11 test scenarios"

4. MODE-SPECIFIC verification:
   IF workflow_mode == "CHANGE":
     - Glob for results/${FEATURE}/phase6/vnrm-analysis.json
     - Extract repository_path and test_source_root
     - Verify repository_path exists (use Bash: test -d "${repository_path}")
     - If path invalid, STOP and report: "Cannot access VNRM repository"

   IF workflow_mode == "NEW":
     - Create output directory: results/${FEATURE}/phase12/src/test/java/
```

**Gate Criteria**: All verifications pass. If any fail, stop and report.

### Stage 2: Load Phase 11 Test Scenarios and Phase 3 Business Rules

**Objective**: Load test scenarios, design context, and business rules for traceability.

**Actions**:
1. Read `results/${FEATURE}/phase11/system-test-scenarios.json`
2. Extract:
    - `test_scenarios[]` - Array of test scenarios
    - `test_summary.total_test_scenarios` - Count
    - `test_summary.test_categories` - Categories breakdown
3. Read design context:
    - NEW mode: `results/${FEATURE}/phase7/microservice-design.json`
    - CHANGE mode: `results/${FEATURE}/phase7.1/microservice-delta.json`
4. Extract component list from design:
    - `new_components[]` - Components requiring NEW tests
    - `modified_components[]` - Components requiring MODIFY tests
5. **Load Phase 3 business rules for traceability**:
    - Read `results/${FEATURE}/phase3/ruletable.json`
    - Extract `business_rules[]` array
    - Build Map: `rule_id` → `rule_description`
6. **Cross-reference scenarios with business rules**:
    - Each scenario should reference `business_rule_ids[]`
    - Build: Map `scenario_id` → List of `business_rule_id`

**Expected Output**: Test scenario list, component inventory, and business rule mapping.


### Stage 3: Load Existing Test Inventory (CHANGE Mode Only)

**Objective**: Build existing test coverage map from Phase 6.

**When to Execute**: Only when `workflow_mode = "CHANGE"`

**Actions**:
1. Read `results/${FEATURE}/phase6/vnrm-analysis.json`
2. Extract `test_infrastructure` containing test_framework, test_source_root, and test_inventory[]
3. Build coverage map: `Map<ProductionClass, TestClass>` from test_inventory
4. Note which components have existing tests

**Expected Output**: `existingTestMap` with production class → test class mappings.

### Stage 4: Classify Components for Testing

**Objective**: Categorize all components requiring tests.

**Classification Algorithm**:
```
FOR each scenario in phase11/system-test-scenarios.json:
  SWITCH scenario.type:
    CASE "E2E":
      → Map to Controller tests
      → Extract: endpoint, HTTP method, request/response
    CASE "integration":
      → Map to Service tests
      → Extract: service methods, business rules
    CASE "performance":
      → Map to Service stress tests
      → Extract: throughput requirements
    CASE "security":
      → Map to Controller security tests
      → Extract: auth requirements

FOR each component in phase7.1/microservice-delta.json:
  SWITCH component.type:
    CASE "Service":
      → Create ServiceTest with mocked dependencies
    CASE "Controller":
      → Create ControllerTest with MockMvc
    CASE "Repository":
      → Create RepositoryTest with TestContainers
    CASE "Resilience":
      → Create integration test with failure simulation
    CASE "Validator":
      → Create unit test with edge cases
```

**Output**: `componentTestMap` with test assignments.

### Stage 5: Classify Tests as REUSE/MODIFY/NEW (CHANGE Mode)

**Objective**: Determine action for each required test.

**Classification Logic**:
```
FOR each component in Phase 7/7.1 design:
  has_existing_test = component exists in Phase 6 test_inventory
  is_modified = component in Phase 7.1 modified_components
  is_new = component in Phase 7.1 new_components

  IF has_existing_test AND NOT is_modified:
    → REUSE: "Component unchanged, existing test sufficient"
  ELSE IF has_existing_test AND is_modified:
    → MODIFY: "Add tests for new/changed behavior"
  ELSE:
    → NEW: "No existing test, create new test class"
```

**Generate test-classification.json** with:
- `classification_summary`: counts for reuse/modify/new/total
- `classifications[]`: for each component - name, classification (REUSE/MODIFY/NEW), reason, action, existing test path (if applicable)

### Stage 6: Generate TestDataBuilder and Fixtures

**Objective**: Create reusable test data factories with fluent API.

**MANDATORY - Always generate TestDataBuilder with FLUENT BUILDER PATTERN**


**Key Pattern**: Use `TestDataBuilder.aEntity().withXxx().build()` not direct setters.

**TestDataBuilder Generation Process**:
```
1. READ Phase 7/7.1 design file for your feature
2. EXTRACT all entities from data_model.entities[]
3. FOR EACH entity, generate:
   a. valid{Entity}() - Returns entity with all required fields set
   b. {entity}WithStatus(status) - Returns entity with specific status
   c. invalid{Entity}() - Returns entity with validation errors
4. Use ACTUAL field names from entity definitions
```

**Generate TestDataBuilder.java** in `testutil/` package with:
- Package: `de.telekom.vnrm.{submodule}.testutil` (derive submodule from Phase 6/7)
- For EACH entity in `data_model.entities[]`:
  - `validEntity()` - returns entity with all required fields set
  - `entityWithStatus(status)` - returns entity with specific status
  - `invalidEntity()` - returns entity with validation errors for negative tests
- For audit/history entities: `statusChange(from, to)` method
- For related entities: `pendingRelated()`, `failedRelated()` methods
- Use ACTUAL field names and enum values from Phase 7/7.1 design

### Stage 7: Generate Mock Configurations

**Objective**: Create mock configurations for external APIs.

**Generate MockApiConfigurations.java** in `testutil/` package with:
- `@TestConfiguration` class
- `@Bean @Primary` mock RestTemplate
- For EACH external API in Phase 7/7.1 integrations:
  - `mockApiSuccess(restTemplate)` - configure success response
  - `mockApiFailure(restTemplate)` - configure exception throw
  - `mockApiValidation(restTemplate, valid)` - configure validation response
- Circuit breaker helpers: `mockCircuitBreakerClosed()`, `mockCircuitBreakerOpen()`
- Use ACTUAL API names from Phase 7/7.1 design (e.g., RNPS, BNetzA, Carrier)

### Stage 8: Generate Tests for CHANGE Mode

**CHANGE Mode Strategy**: Generate tests to results folder first, then apply to repository.

This approach ensures:
- Full traceability of generated tests in `results/${FEATURE}/phase12/`
- Safe review before applying to production repository
- Consistent structure with NEW mode for easier maintenance

**Step 1: Resolve Repository Paths (for reference)**
```
Read results/${FEATURE}/phase6/vnrm-analysis.json
Extract:
  - repository_path: Absolute path to VNRM repository
  - source_structure.test_source_root: Relative path (default: "src/test/java")

Store for later application:
  target_base = ${repository_path}/${test_source_root}
```

**Step 2: Generate to Results Folder**
All tests go to: `results/${FEATURE}/phase12/src/test/java/de/telekom/vnrm/{submodule}/`

- REUSE tests: Do NOT generate (reference existing tests in repository)
- MODIFY tests: Generate new test methods for changed components
- NEW tests: Generate complete new test classes

**Step 3: Generate TestDataBuilder and Mocks**
1. Write TestDataBuilder.java to `results/${FEATURE}/phase12/src/test/java/.../testutil/`
2. Write MockApiConfigurations.java to same location

**Step 4: Application Instructions**
After generation, apply tests to VNRM repository:
```bash
# Copy generated tests to repository
cp -r results/${FEATURE}/phase12/src/test/java/* ${repository_path}/src/test/java/

# Verify compilation
cd ${repository_path} && mvn test-compile
```

**Step 6: Generate Applied Tests Log**
Create `results/${FEATURE}/phase12/applied-test-edits-log.json` with:
- `applied_at`, `workflow_mode`, `repository_path`, `test_source_root`
- `summary`: counts for tests_reused, tests_modified, tests_created, utility_files_created
- `tests_reused[]`: unchanged tests with class name and reason
- `tests_modified[]`: modified tests with path, methods added, edit operation
- `tests_created[]`: new tests with path and method list
- `utilities_created[]`: utility files with paths

### Stage 9: Generate Unit Test Classes

**Objective**: Generate JUnit test classes following Spring Boot patterns.

**OUTPUT TARGET (both modes generate to results folder)**:
- **NEW mode**: Write test files to `results/${FEATURE}/phase12/src/test/java/de/telekom/vnrm/{submodule}/`
- **CHANGE mode**: Write test files to `results/${FEATURE}/phase12/src/test/java/de/telekom/vnrm/{submodule}/`
  - REUSE tests: Not generated (reference existing tests in repository)
  - MODIFY tests: Generate new test methods for changed components
  - NEW tests: Generate complete new test classes

#### Controller Test Pattern (WebMvcTest)

Generate controller tests with:
- `@WebMvcTest(ControllerClass.class)` annotation
- `@Autowired MockMvc` and `ObjectMapper`
- `@MockBean` for service dependencies
- `@Nested` classes for each endpoint (POST, GET, PUT, DELETE)
- Use `mockMvc.perform()` with `post()`, `get()`, etc.
- Assert with `status().isOk()`, `jsonPath()` matchers
- Use `TestDataBuilder` for request/response objects

#### Service Test Pattern (Mockito)

Generate service tests with:
- `@ExtendWith(MockitoExtension.class)` annotation
- `@Mock` for repository and dependency mocks
- `@InjectMocks` for service implementation
- `@Captor` for argument capture verification
- `@BeforeEach` setup with `TestDataBuilder`
- Verify interactions with `verify()` and `ArgumentCaptor`
- Assert with AssertJ `assertThat()`

#### Repository Test Pattern (TestContainers)

Generate repository tests with:
- `@DataJpaTest` and `@Testcontainers` annotations
- `@AutoConfigureTestDatabase(replace = NONE)`
- PostgreSQL container with `@Container`
- `@DynamicPropertySource` for datasource config
- `@Autowired` repository under test
- Test CRUD operations and custom query methods
- Use `TestDataBuilder` for test entities

### Stage 10: Create Test Summary and Verification

**Objective**: Generate documentation and verify test quality.

**Generate unit-tests.json** with:
- `phase`, `feature`, `workflow_mode`, `generated`, `status`
- `test_summary`: total classes, methods, coverage target, framework
- `classification_summary`: reuse/modify/new counts
- `test_classes[]`: each class with package, path, methods, mocked dependencies
- `utilities_generated[]`: list of utility files created

### Stage 10.5: Generate Traceability Matrix

**Objective**: Create bidirectional traceability from business rules to unit tests.

**Generate traceability-matrix.json** with:
- `traceability_summary`: rule counts, scenario counts, coverage percentages
- `traceability_matrix[]`: for each business rule, linked test scenarios and unit tests
- `coverage_gaps[]`: any rules/scenarios without test coverage

### Stage 11: Generate Quality Report

**Objective**: Compile all quality gate results into a single report.

**Generate test-quality-report.json** with:
- `overall_status`: PASS/FAIL
- `gates`: results for each quality gate (structure, classification, code quality, coverage, applied edits)
- `summary`: total errors, warnings, recommendation


### Stage 12: Verify Compilation

**Objective**: Ensure all generated tests compile successfully.

**For NEW mode**:
```bash
# Create minimal pom.xml for test compilation verification
cd results/${FEATURE}/phase12/

# Verify syntax by attempting compilation (optional - full verification in Phase 13)
echo "Compilation verification deferred to Phase 13 integration"
```

**For CHANGE mode**:
```bash
# Verify tests compile in actual repository
cd ${repository_path}

# Run test compilation
mvn clean test-compile -DskipTests 2>&1 | tee phase12-compile.log

# Check for errors
if grep -q "BUILD FAILURE" phase12-compile.log; then
    echo "COMPILATION FAILED - Review errors and fix"
    grep -A5 "\[ERROR\]" phase12-compile.log
    exit 1
fi

echo "All tests compile successfully"
```

**Pass Criteria**:
- `mvn test-compile` returns SUCCESS
- No syntax errors in generated test files
- All imports resolve correctly

---

## Advanced Test Patterns

### Parameterized Tests

Use `@ParameterizedTest` with `@CsvSource` for state transition validation:
- Test valid transitions (NEW → IN_PROGRESS → COMPLETED)
- Test invalid transitions (reverse, skip states)
- Use feature's actual status enum values

### Edge Case Tests

Use `@Nested` classes for edge case grouping:
- Null input handling with `assertThrows()`
- Empty collection handling
- Boundary value testing
- Exception message assertions with `assertThat(ex.getMessage()).contains()`

---

## Horizon Event Handler Test Pattern

VNRM uses **Horizon** (Telekom's Event Bus) for asynchronous messaging. Test event handlers with mocked `HorizonClient`:

```java
@ExtendWith(MockitoExtension.class)
@DisplayName("Event Handler Tests")
class EventHandlerTest {

    @Mock
    private HorizonClient horizonClient;

    @Mock
    private ProcessingService processingService;

    @InjectMocks
    private MessageEventHandler eventHandler;

    @Captor
    private ArgumentCaptor<HorizonEvent<?>> responseCaptor;

    @Test
    @DisplayName("Should process message and publish response")
    void shouldProcessAndPublishResponse() {
        // Given
        var message = TestDataBuilder.validMessage();
        var incomingEvent = HorizonEvent.of(message)
            .withEventType("message.received")
            .withCorrelationId(UUID.randomUUID().toString())
            .build();

        when(processingService.process(any())).thenReturn(ProcessingResult.success("REF-123"));
        when(horizonClient.publish(any())).thenReturn(CompletableFuture.completedFuture(null));

        // When
        eventHandler.handle(incomingEvent);

        // Then
        verify(processingService).process(message);
        verify(horizonClient).publish(responseCaptor.capture());

        var publishedEvent = responseCaptor.getValue();
        assertThat(publishedEvent.getEventType()).isEqualTo("message.processed");
        assertThat(publishedEvent.getCorrelationId()).isEqualTo(incomingEvent.getCorrelationId());
    }

    @Test
    @DisplayName("Should handle processing failure gracefully")
    void shouldHandleProcessingFailure() {
        // Given
        var incomingEvent = HorizonEvent.of(TestDataBuilder.validMessage())
            .withEventType("message.received")
            .build();

        when(processingService.process(any())).thenThrow(new ProcessingException("Validation failed"));
        when(horizonClient.publish(any())).thenReturn(CompletableFuture.completedFuture(null));

        // When
        eventHandler.handle(incomingEvent);

        // Then - Error event published
        verify(horizonClient).publish(responseCaptor.capture());
        assertThat(responseCaptor.getValue().getEventType()).isEqualTo("message.error");
    }
}
```

---

## Circuit Breaker Test Pattern (Resilience4j)

```java
@SpringBootTest
@DisplayName("Circuit Breaker Tests")
class CircuitBreakerTest {

    @Autowired
    private ExternalClient client;

    @Autowired
    private CircuitBreakerRegistry circuitBreakerRegistry;

    @MockBean
    private RestTemplate restTemplate;

    private CircuitBreaker circuitBreaker;

    @BeforeEach
    void setUp() {
        circuitBreaker = circuitBreakerRegistry.circuitBreaker("external");
        circuitBreaker.reset();
    }

    @Test
    @DisplayName("Should open circuit after failures")
    void shouldOpenCircuitAfterFailures() {
        // Given - Always fail
        when(restTemplate.postForObject(anyString(), any(), any()))
            .thenThrow(new RestClientException("Connection refused"));

        // When - Make failing calls
        for (int i = 0; i < 5; i++) {
            try { client.call(TestDataBuilder.validRequest()); } catch (Exception ignored) {}
        }

        // Then
        assertThat(circuitBreaker.getState()).isEqualTo(CircuitBreaker.State.OPEN);
    }

    @Test
    @DisplayName("Should reject calls when circuit is open")
    void shouldRejectWhenOpen() {
        // Given
        circuitBreaker.transitionToOpenState();

        // When/Then
        assertThrows(CallNotPermittedException.class, () ->
            client.call(TestDataBuilder.validRequest())
        );
        verify(restTemplate, never()).postForObject(anyString(), any(), any());
    }
}
```

---

## Output Files Reference

| File | Purpose | Mode |
|------|---------|------|
| `unit-tests.json` | Test metadata and summary | Both |
| `test-classification.json` | REUSE/MODIFY/NEW decisions | CHANGE only |
| `test-quality-report.json` | Quality gate results | Both |
| `traceability-matrix.json` | Business rule → test mapping | Both |
| `PHASE12_SUMMARY.md` | Human-readable summary | Both |

---

## Success Criteria

When using this skill, ensure:

### Pre-Generation (Anti-Hallucination)
- [x] Follow anti-hallucination rules (see top of skill)
- [x] Verified all methods/fields exist in source before testing them
- [x] All @Mock fields are actually used in at least one test
- [x] No JUnit 4 imports - only JUnit 5

### Structure & Classification
- [x] Pre-flight validation passes before starting
- [x] All Phase 11 E2E scenarios have corresponding unit tests
- [x] CHANGE mode correctly classifies REUSE/MODIFY/NEW
- [x] Gate 1 (Structure) passes - 100% component coverage
- [x] Gate 2 (Classification) passes - valid REUSE/MODIFY/NEW assignments

### Code Quality
- [x] Controller tests use `@WebMvcTest` with MockMvc
- [x] Service tests use `@ExtendWith(MockitoExtension.class)` with proper mocking
- [x] Repository tests use `@DataJpaTest` with TestContainers
- [x] All test methods have `@DisplayName` annotations
- [x] All tests use AssertJ assertions (not JUnit assertions)
- [x] All tests follow Given-When-Then structure
- [x] Gate 3 (Code Quality) passes - 0 errors

### Test Utilities
- [x] **TestDataBuilder generated with all entity builders**
- [x] **MockApiConfigurations generated for external APIs**
- [x] No direct entity instantiation in tests (use builders)

### Coverage & Edge Cases
- [x] Target 80%+ line coverage for new/modified code
- [x] At least 30% of tests cover edge cases
- [x] Parameterized tests used for validation rules
- [x] Gate 4 (Coverage) passes - meets targets

### Traceability
- [x] All test methods include scenario ID suffix (e.g., `_TSPPM001`)
- [x] All test classes have traceability table in JavaDoc
- [x] traceability-matrix.json generated with BR→TS→Test mapping
- [x] Business rule coverage >= 90%
- [x] Scenario coverage >= 95%

### Documentation & Verification
- [x] applied-test-edits-log.json documents all changes (CHANGE mode)
- [x] test-classification.json provides rationale (CHANGE mode)
- [x] test-quality-report.json generated with all gate results
- [x] Gate 5 (Applied Edits) passes - all files created/modified correctly
- [x] Tests compile successfully (`mvn test-compile`)
- [x] All output files match expected structure

---

## Common Mistakes to Avoid

### Anti-Hallucination Mistakes

| Mistake | Correct Approach |
|---------|------------------|
| Inventing methods that don't exist | Read source code first, only test actual methods |
| Inventing entity fields | Verify field names from entity class definitions |
| Using `when()` on non-existent mock methods | Check dependency interface before mocking |
| Arbitrary `times(N)` verification counts | Only use counts with clear justification |
| Declaring unused `@Mock` fields | Every mock must be used in at least one test |
| Direct entity instantiation `new Entity()` | Always use TestDataBuilder |

### Framework Mistakes

| Mistake | Correct Approach |
|---------|------------------|
| `import org.junit.Test;` (JUnit 4) | Use `org.junit.jupiter.api.Test` (JUnit 5) |
| `assertEquals(expected, actual)` | Use AssertJ: `assertThat(actual).isEqualTo(expected)` |
| `@Before` annotation | Use `@BeforeEach` (JUnit 5) |
| `@RunWith(...)` | Use `@ExtendWith(...)` (JUnit 5) |
| Missing `@DisplayName` | Every test method needs descriptive display name |

### Workflow Mistakes

| Mistake | Correct Approach |
|---------|------------------|
| Skipping results folder generation | Both modes generate to results folder first, then apply to repository |
| Missing TestDataBuilder | Always generate TestDataBuilder with all entity builders |
| Using `@Test` only for controller tests | Use `@WebMvcTest` with MockMvc |
| Not classifying tests in CHANGE mode | Always generate test-classification.json |
| Skipping pre-flight validation | Execute checklist before any stage |
| Not logging applied edits | Generate applied-test-edits-log.json |
| Skipping quality gates | Execute all 5 gates and generate test-quality-report.json |
| Not verifying compilation | Run `mvn test-compile` to verify tests compile |

---

## Related Skills

- **11-system-test-workflow** - Phase 11 test scenario definition (input)
- **06-vnrm-analysis-workflow** - Phase 6 test infrastructure (CHANGE mode input)
- **07-1-microservice-delta-workflow** - Phase 7.1 component changes
- **13-source-code-generation-workflow** - Phase 13 source code (next phase)

---

**This skill provides the complete methodology for generating production-ready JUnit unit tests in the RNVS-VNRM migration workflow.**
