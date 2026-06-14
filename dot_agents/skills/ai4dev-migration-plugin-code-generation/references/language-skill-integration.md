# Language Skill Integration

This reference defines how language-specific skills (java-codegen, python-codegen) integrate with the batch execution workflow.

## Purpose

Enable language-aware code generation by:

- Loading language-specific references per batch
- Applying language conventions and patterns
- Using language-specific templates and frameworks
- Validating using language-specific rules

## Language Skill Detection

### From technical-plan.md

```markdown
## Architecture Overview

### Technology Stack

**Language**: Java 17
**Framework**: Spring Boot 3.2.0
**Build Tool**: Maven 3.9+
```

### From plan.json

```json
{
  "target_stack": {
    "languages": ["java"],
    "frameworks": ["spring-boot"],
    "build_tools": ["maven"],
    "version": {
      "java": "17",
      "spring_boot": "3.2.0"
    }
  }
}
```

### Language Mapping

| Detected Language | Skill Name | Skill Path |
|-------------------|------------|------------|
| java, Java | java-codegen | skills/code-generation/references/java/ |
| java, Java (Quarkus) | quarkus-codegen | skills/code-generation/references/quarkus/ |
| python, Python | python-codegen | skills/code-generation/references/python/ |

**Note**: For Java, the skill is selected based on the detected framework:

- Spring Boot → java-codegen
- Quarkus → quarkus-codegen

## Step-to-Reference Mapping

Each code-generation step uses specific references from the language skill.

### Java (java-codegen)

```text
Step              References to Load                                    What They Provide
──────────────────────────────────────────────────────────────────────────────────────────────
Setup             build-tools.md, springboot-core.md,                   pom.xml/build.gradle templates,
                  coding-standards.md                                   Maven/Gradle directory layout,
                                                                        Spring Boot project structure,
                                                                        dependency management,
                                                                        naming conventions

Tests             testing.md, fundamentals.md                           JUnit 5 + Mockito patterns,
                                                                        Test naming (*Test, *IT),
                                                                        MockMvc for controllers,
                                                                        @DataJpaTest for repositories,
                                                                        Testcontainers for integration,
                                                                        Cucumber-JVM for BDD,
                                                                        TDD workflow (red-green-refactor)

Core              fundamentals.md, springboot-core.md,                  Idiomatic Java (streams, Optional),
                  jpa-patterns.md, concurrency.md,                      Spring annotations (@Service, @Transactional),
                  springboot-security.md, coding-standards.md           Layered architecture (Controller → Service → Repository),
                                                                        JPA entity design, relationships,
                                                                        Thread-safe patterns,
                                                                        Security (authn/authz, input validation),
                                                                        Code quality standards

Integration       springboot-core.md, testing.md,                       @SpringBootTest for integration tests,
                  microservices.md, springboot-security.md              Component wiring (DI),
                                                                        REST API integration,
                                                                        Service-to-service communication,
                                                                        Security filters,
                                                                        Exception handling

Polish            performance.md, springboot-core.md,                   JVM tuning (GC, heap),
                  springboot-security.md, coding-standards.md           Structured logging (MDC),
                                                                        Observability (Actuator, Micrometer),
                                                                        Rate limiting,
                                                                        Security headers,
                                                                        Code cleanup
```

### Python (python-codegen)

```text
Step              References to Load                                    What They Provide
──────────────────────────────────────────────────────────────────────────────────────────────
Setup             build-tools.md, fastapi-core.md,                      pyproject.toml template (uv/poetry),
                  sqlalchemy-patterns.md, coding-standards.md           Project directory layout,
                                                                        FastAPI app factory,
                                                                        Alembic initialization,
                                                                        pydantic-settings config,
                                                                        naming conventions

Tests             testing.md, fundamentals.md                           pytest conventions (test_*.py),
                                                                        Fixtures and conftest.py,
                                                                        FastAPI TestClient,
                                                                        Async testing (@pytest.mark.asyncio),
                                                                        hypothesis for property testing,
                                                                        coverage targets (>90%),
                                                                        TDD workflow

Core              fundamentals.md, fastapi-core.md,                     Idiomatic Python (type hints, dataclasses),
                  fastapi-security.md, sqlalchemy-patterns.md,          FastAPI routing and DI,
                  async-patterns.md, coding-standards.md                Pydantic v2 schemas (DTOs),
                                                                        SQLAlchemy 2.0 models (async),
                                                                        BaseRepository pattern,
                                                                        Async patterns (TaskGroup, gather),
                                                                        JWT authentication,
                                                                        Code quality (ruff, mypy)

Integration       fastapi-core.md, testing.md,                          API integration tests (httpx.AsyncClient),
                  async-patterns.md, fastapi-security.md                Dependency injection overrides,
                                                                        Background tasks,
                                                                        Exception handlers,
                                                                        CORS and security middleware

Polish            fastapi-core.md, fastapi-security.md,                 Production defaults (uvicorn workers),
                  coding-standards.md, build-tools.md                   Security hardening (rate limiting, headers),
                                                                        Structured logging (structlog),
                                                                        OpenAPI customization,
                                                                        Quality gates (ruff strict, mypy strict)
```

### Quarkus (quarkus-codegen)

```text
Step              References to Load                                    What They Provide
──────────────────────────────────────────────────────────────────────────────────────────────
Setup             build-tools.md, quarkus-core.md,                      pom.xml/build.gradle with Quarkus plugin,
                  coding-standards.md                                   Maven/Gradle directory layout,
                                                                        Quarkus project structure,
                                                                        Quarkus extensions,
                                                                        naming conventions

Tests             testing.md, fundamentals.md                           @QuarkusTest + REST Assured patterns,
                                                                        Test naming (*Test, *IT),
                                                                        REST Assured for API tests,
                                                                        @TestProfile for test configs,
                                                                        Testcontainers for integration,
                                                                        TDD workflow (red-green-refactor)

Core              fundamentals.md, quarkus-core.md,                     Idiomatic Java (streams, Optional, records),
                  persistence-patterns.md, reactive-patterns.md,        CDI annotations (@ApplicationScoped, @Inject),
                  quarkus-security.md, coding-standards.md              JAX-RS REST resources,
                                                                        Panache repositories (Active Record/Repository),
                                                                        Mutiny reactive patterns (Uni, Multi),
                                                                        OIDC/JWT security,
                                                                        Code quality standards

Integration       quarkus-core.md, testing.md,                          @QuarkusTest for integration tests,
                  microservices.md, quarkus-security.md                 CDI dependency injection,
                                                                        REST Client (reactive),
                                                                        Fault tolerance (Retry, CircuitBreaker),
                                                                        Health checks,
                                                                        Security filters,
                                                                        Exception mappers

Polish            quarkus-core.md, quarkus-security.md,                 Native compilation configuration,
                  coding-standards.md, build-tools.md                   Structured logging (JBoss Logging),
                                                                        Observability (Health, Metrics, OpenTelemetry),
                                                                        Security hardening,
                                                                        Code cleanup,
                                                                        Native build optimization
```

## Batch Language Context Schema

Each batch in tasks.json includes language_context:

```json
{
  "id": "B001",
  "step": "setup",
  "batch_number": 1,
  "tasks": ["T001", "T002", "T003"],
  "language_context": {
    "skill": "java-codegen",
    "references": ["build-tools.md", "springboot-core.md", "coding-standards.md"],
    "templates": {
      "build_file": "pom.xml",
      "config_file": "application.yml",
      "test_config": "application-test.yml"
    },
    "conventions": {
      "directory_layout": "Maven standard (src/main/java, src/test/java)",
      "package_structure": "com.example.{module}/controller/service/repository/model/dto",
      "naming": {
        "classes": "PascalCase",
        "methods": "camelCase",
        "constants": "UPPER_SNAKE_CASE",
        "test_classes": "*Test for unit, *IT for integration"
      }
    },
    "test_framework": "JUnit 5 + Mockito + AssertJ",
    "test_command": "mvn test"
  }
}
```

## Reference Loading Strategy

### During Task Generation (Step 2)

```text
1. Detect target language from technical-plan.md
2. Map language to skill name
3. Load language skill SKILL.md to get reference table
4. For each step, determine which references are needed
5. Assign references to batches based on step

Example for Java + Spring Boot:
  Setup batches → references: ["build-tools.md", "springboot-core.md"]
  Tests batches → references: ["testing.md", "fundamentals.md"]
  Core batches  → references: ["fundamentals.md", "springboot-core.md", "jpa-patterns.md"]
```

### During Batch Execution (Steps 3-7)

```text
BEFORE executing each batch:

1. Read batch.language_context from tasks.json

2. IF language_context exists:
     FOR each reference in language_context.references:
       path = skills/{language_context.skill}/references/{reference}
       Read {path}
       Store content in memory as {reference_name}

3. Apply language-specific patterns:
   - File naming from conventions
   - Directory structure from templates
   - Code style from coding-standards
   - Test patterns from testing

4. Execute batch tasks using loaded references
```

## Language-Specific Patterns

### Java

**Directory Structure:**

```text
src/
├── main/
│   ├── java/com/example/{module}/
│   │   ├── controller/
│   │   │   └── {Entity}Controller.java
│   │   ├── service/
│   │   │   ├── {Entity}Service.java (interface)
│   │   │   └── {Entity}ServiceImpl.java
│   │   ├── repository/
│   │   │   └── {Entity}Repository.java (extends JpaRepository)
│   │   ├── model/
│   │   │   └── {Entity}.java (@Entity)
│   │   ├── dto/
│   │   │   ├── {Entity}RequestDTO.java
│   │   │   └── {Entity}ResponseDTO.java
│   │   └── config/
│   │       └── {Feature}Config.java
│   └── resources/
│       ├── application.yml
│       ├── application-test.yml
│       └── db/migration/
│           └── V1__initial_schema.sql
└── test/
    ├── java/com/example/{module}/
    │   ├── controller/
    │   │   └── {Entity}ControllerTest.java
    │   ├── service/
    │   │   └── {Entity}ServiceTest.java
    │   └── repository/
    │       └── {Entity}RepositoryIT.java
    └── resources/
        └── application-test.yml
```

**File Templates:**

`pom.xml` template (from build-tools.md):

- Spring Boot parent
- Dependencies: spring-boot-starter-web, spring-boot-starter-data-jpa, spring-boot-starter-test
- Plugins: maven-surefire-plugin, maven-failsafe-plugin

`{Entity}Controller.java` template (from springboot-core.md):

```java
@RestController
@RequestMapping("/api/v1/{entities}")
public class {Entity}Controller {
    private final {Entity}Service service;

    // Constructor injection, CRUD endpoints
}
```

### Python

**Directory Structure:**

```text
src/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app
│   ├── config.py                  # Settings
│   ├── dependencies.py            # DI
│   ├── {module}/
│   │   ├── __init__.py
│   │   ├── router.py              # FastAPI router
│   │   ├── schemas.py             # Pydantic DTOs
│   │   ├── models.py              # SQLAlchemy models
│   │   ├── service.py             # Business logic
│   │   ├── repository.py          # Data access
│   │   └── dependencies.py        # Module-specific DI
│   └── common/
│       ├── schemas.py             # Shared schemas
│       └── repository.py          # BaseRepository
├── alembic/
│   ├── env.py
│   └── versions/
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   └── test_{module}.py
│   └── integration/
│       └── test_{module}_api.py
├── pyproject.toml
└── .env
```

**File Templates:**

`pyproject.toml` template (from build-tools.md):

- uv or poetry dependency management
- Dependencies: fastapi, uvicorn, sqlalchemy, pydantic-settings
- Dev dependencies: pytest, pytest-asyncio, ruff, mypy, httpx

`{module}/router.py` template (from fastapi-core.md):

```python
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/{entities}", tags=["{entities}"])

@router.get("/")
async def list_{entities}(
    service: {Entity}Service = Depends(get_{entity}_service)
) -> list[{Entity}Schema]:
    # Implementation
```

## Test Framework Integration

### Java + JUnit 5

**Unit Test Pattern:**

```java
@ExtendWith(MockitoExtension.class)
class {Entity}ServiceTest {
    @Mock
    private {Entity}Repository repository;

    @InjectMocks
    private {Entity}ServiceImpl service;

    @Test
    void should{Behavior}_when{Condition}() {
        // Given
        // When
        // Then (AssertJ assertions)
    }
}
```

**Integration Test Pattern:**

```java
@SpringBootTest
@AutoConfigureMockMvc
class {Entity}ControllerIT {
    @Autowired
    private MockMvc mockMvc;

    @Test
    void should{Behavior}_when{HttpRequest}() throws Exception {
        mockMvc.perform(get("/api/v1/{entities}"))
            .andExpect(status().isOk());
    }
}
```

### Python + pytest

**Unit Test Pattern:**

```python
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.mark.asyncio
async def test_{behavior}_when_{condition}(
    {entity}_service: {Entity}Service,
    mock_{entity}_repository: Mock
):
    # Given
    mock_{entity}_repository.find_by_id.return_value = ...

    # When
    result = await {entity}_service.{method}(...)

    # Then
    assert result == ...
```

**Integration Test Pattern:**

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_{behavior}_via_api(client: AsyncClient):
    # When
    response = await client.get("/api/v1/{entities}")

    # Then
    assert response.status_code == 200
    assert len(response.json()) > 0
```

## Validation Rules

### Java

From coding-standards.md:

- All classes have proper JavaDoc
- No raw types (use generics)
- Prefer immutability (final fields, records)
- Use Optional for nullable returns
- Use streams for collections
- No `@SuppressWarnings` without justification
- Exception messages are descriptive

From testing.md:

- Test coverage ≥ 80% (JaCoCo)
- All public methods have tests
- Use @DisplayName for readable test names
- No test interdependencies

### Python

From coding-standards.md:

- Type hints on all public functions
- No `# type: ignore` without comment
- No `# noqa` without specific code
- Prefer dataclasses over dicts
- Use structural pattern matching (3.10+)
- Async-first for I/O operations
- Structured logging (never print)

From testing.md:

- Test coverage ≥ 90% (pytest-cov)
- All public functions have tests
- Use descriptive test names (test_should_X_when_Y)
- Fixtures in conftest.py

## Batch Size Optimization by Language

Adjust batch sizes based on language characteristics:

### Java

```python
# Java has more boilerplate → slightly larger batches
time_estimates_java = {
    "setup": 0.5,      # pom.xml, configs (more verbose)
    "tests": 0.7,      # JUnit tests (more verbose)
    "core": 2.5,       # Spring components (more annotations)
    "integration": 3.5, # Integration tests (more setup)
    "polish": 1.2      # Documentation, logging
}
```

### Python

```python
# Python is more concise → smaller batches, faster
time_estimates_python = {
    "setup": 0.3,      # pyproject.toml (concise)
    "tests": 0.4,      # pytest (concise)
    "core": 1.8,       # FastAPI routes (concise)
    "integration": 2.5, # Async tests (moderate)
    "polish": 0.8      # Type hints, ruff
}
```

## Example: Java Batch Execution

```text
Batch B004 (Core, Java + Spring Boot + JPA):

1. Load language context from tasks.json:
   {
     "skill": "java-codegen",
     "references": ["fundamentals.md", "springboot-core.md", "jpa-patterns.md"],
     "conventions": { "package_structure": "com.example.payment/..." }
   }

2. Read references:
   Read skills/code-generation/references/java/fundamentals.md
   Read skills/code-generation/references/java/springboot-core.md
   Read skills/code-generation/references/java/jpa-patterns.md

3. Execute tasks using patterns from references:

   Task T019: Implement UserService
     → Create UserService.java interface (from springboot-core.md layering)
     → Create UserServiceImpl.java (from springboot-core.md @Service pattern)
     → Use Optional<User> for findById (from fundamentals.md Optional usage)
     → Use @Transactional from jpa-patterns.md

   Task T020: Implement PaymentRepository
     → Extend JpaRepository<Payment, Long> (from jpa-patterns.md)
     → Add custom query methods (from jpa-patterns.md query patterns)
     → Use @Query for complex queries (from jpa-patterns.md)

4. Run tests using language test framework:
   Bash: mvn test -Dtest={Entity}ServiceTest
```

## Example: Python Batch Execution

```text
Batch B002 (Tests, Python + FastAPI + pytest):

1. Load language context from tasks.json:
   {
     "skill": "python-codegen",
     "references": ["testing.md", "fastapi-core.md"],
     "test_framework": "pytest + FastAPI TestClient"
   }

2. Read references:
   Read skills/code-generation/references/python/testing.md
   Read skills/code-generation/references/python/fastapi-core.md

3. Execute tasks using patterns from references:

   Task T004: Write UserService tests
     → Create tests/unit/test_user_service.py
     → Use pytest fixtures from testing.md
     → Use AsyncMock for async methods (from testing.md async patterns)
     → Test naming: test_should_create_user_when_valid_data

   Task T005: Write API tests
     → Create tests/integration/test_user_api.py
     → Use FastAPI TestClient (from fastapi-core.md)
     → Override dependencies for testing (from testing.md DI overrides)

4. Run tests using language test framework:
   Bash: pytest tests/unit/test_user_service.py -v
```

## Example: Quarkus Batch Execution

```text
Batch B004 (Core, Quarkus + Panache):

1. Load language context from tasks.json:
   {
     "skill": "quarkus-codegen",
     "references": ["fundamentals.md", "quarkus-core.md", "persistence-patterns.md"],
     "conventions": { "package_structure": "com.example.payment/resource/service/repository" }
   }

2. Read references:
   Read skills/code-generation/references/quarkus/fundamentals.md
   Read skills/code-generation/references/quarkus/quarkus-core.md
   Read skills/code-generation/references/quarkus/persistence-patterns.md

3. Execute tasks using patterns from references:

   Task T019: Implement UserResource
     → Create UserResource.java (from quarkus-core.md @Path pattern)
     → Use JAX-RS annotations (@GET, @POST, @Path)
     → Inject UserService with @Inject (from quarkus-core.md CDI)
     → Return Uni<T> for reactive endpoints (from reactive-patterns.md)

   Task T020: Implement UserRepository
     → Extend PanacheRepository<User> (from persistence-patterns.md)
     → Add custom query methods using Panache patterns
     → Use @ApplicationScoped for CDI (from quarkus-core.md)

4. Run tests using language test framework:
   Bash: ./mvnw test -Dtest=UserResourceTest
```

## Fallback for Unsupported Languages

If no language skill exists:

```text
1. Log warning: "No language skill found for {language}, using generic workflow"
2. Use generic file naming (lowercase, underscores)
3. Use generic test framework detection (presence of test files)
4. Rely on technical-plan.md for all patterns
5. No language-specific validation
```

## Database Skill Integration

The `db-codegen` skill is loaded alongside language skills when spec artifacts contain database contracts.

### DB Skill Detection

```text
1. Check contracts.md for "## 3. Database Contracts"
2. Check technical-plan.md for "## 4. Data Implementation" with schema changes

IF either contains database specifications:
  - Extract DB type (PostgreSQL, MySQL, MongoDB, SQLite)
  - Set db_skill = "db-codegen"
  - Determine migration framework from language + framework:
    Java + Spring Boot  → flyway, path: src/main/resources/db/migration/
    Java + Quarkus      → flyway, path: src/main/resources/db/migration/
    Python + FastAPI    → alembic, path: alembic/versions/
    Python + Django     → django, path: {app}/migrations/
    Generic             → raw-sql, path: database/migrations/
```

### DB Context Schema

Each Setup batch includes optional `db_context` alongside `language_context`:

```json
{
  "id": "B001",
  "step": "setup",
  "tasks": ["T001", "T002", "T003", "T004", "T005", "T006", "T007", "T008"],
  "language_context": {
    "skill": "java-codegen",
    "references": ["build-tools.md", "springboot-core.md", "coding-standards.md"]
  },
  "db_context": {
    "skill": "db-codegen",
    "db_type": "postgresql",
    "references": ["postgresql-patterns.md", "schema-design-rules.md", "migration-patterns.md"],
    "migration_framework": "flyway",
    "migration_path": "src/main/resources/db/migration/"
  }
}
```

### Step-to-Reference Mapping for db-codegen

```text
Step              References to Load                              What They Provide
──────────────────────────────────────────────────────────────────────────────────────────────
Setup             {db-type}-patterns.md,                          DB-specific DDL patterns (UUID, timestamps,
                  schema-design-rules.md,                         JSON columns, indexes, constraints),
                  migration-patterns.md                           universal design rules, ERD conventions,
                                                                  migration framework templates

Integration       migration-patterns.md                           Migration execution wiring, seed data loading
```

### DB Reference Loading During Batch Execution

```text
BEFORE executing Setup batch (if db_context exists):

  1. Read batch.db_context from tasks.json

  2. FOR each reference in db_context.references:
       path = skills/{db_context.skill}/references/{reference}
       Read {path}
       Store content in memory for this batch

  Example for PostgreSQL + Java:
    Read skills/code-generation/references/db/postgresql-patterns.md
    Read skills/code-generation/references/db/schema-design-rules.md
    Read skills/code-generation/references/db/migration-patterns.md
```

### No DB Context — No-Op

If `db_context` is absent from the batch, skip DB reference loading entirely. Standard language skill execution proceeds unchanged.

## Integration Checklist

When adding a new language skill:

- [ ] Create skill directory: `skills/{language}-codegen/`
- [ ] Create SKILL.md with reference table
- [ ] Create references for each step (setup, tests, core, integration, polish)
- [ ] Add environment check script: `environment-check-{language}.sh`
- [ ] Update language-skill-integration.md with step-to-reference mapping
- [ ] Update batch-strategy.md with language-specific time estimates
- [ ] Test with sample feature migration

When adding a new database skill:

- [ ] Create skill directory: `skills/{db}-codegen/`
- [ ] Create SKILL.md with reference table
- [ ] Create DB-type-specific pattern references
- [ ] Add migration framework mapping in migration-patterns.md
- [ ] Update language-skill-integration.md DB Skill Detection section
- [ ] Update batch-strategy.md with DB task time estimates
- [ ] Update guard-writes.js ALLOWED_DIRS if new output directories needed
- [ ] Test with sample feature migration containing DB contracts
