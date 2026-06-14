# Step 6 — Integration

Wire components together and verify end-to-end functionality.

## Overview

Integration step connects all components:

- Configure dependency injection
- Wire routing and modules
- Write integration tests
- Verify end-to-end flows work correctly

**Focus**: Component integration, not individual component behavior (already verified in Core).

## Prerequisites

**PRE-FLIGHT:** Read tasks.json and verify ALL Core step tasks have status `passed` before starting this step.

## Execute Batches Following Standard Template

See `batch-execution-template.md` for the complete batch execution loop (8 steps).

This file documents **Step-Specific Customization Points** only.

## Step-Specific: Task Execution (Template Step 4a)

For each task in the Integration batch:

### Load Language Context

Before executing tasks in each batch:

```text
Read batch.language_context from tasks.json

FOR each reference in language_context.references:
  Read skills/{language_context.skill}/references/{reference}

Example for Java Integration batch:
  Read skills/code-generation/references/java/springboot-core.md
  Read skills/code-generation/references/java/testing.md
  Read skills/code-generation/references/java/microservices.md (if applicable)

Example for Python Integration batch:
  Read skills/code-generation/references/python/fastapi-core.md
  Read skills/code-generation/references/python/testing.md
  Read skills/code-generation/references/python/async-patterns.md
```

### Wire Components (Dependency Injection)

**Java (Spring Boot):**

```text
Apply springboot-core.md patterns:

1. Configuration classes:
   @Configuration
   public class AppConfig {
       @Bean
       public SomeService someService() {
           return new SomeServiceImpl();
       }
   }

2. Component scanning:
   @SpringBootApplication
   @ComponentScan(basePackages = "com.example")
   public class Application {
       public static void main(String[] args) {
           SpringApplication.run(Application.class, args);
       }
   }

3. Auto-configuration (if using Spring Boot):
   - Use @EnableAutoConfiguration
   - Configure application.yml for datasource, JPA, etc.

4. Profile-specific configs:
   - application.yml (default)
   - application-dev.yml
   - application-prod.yml
```

**Python (FastAPI):**

```text
Apply fastapi-core.md patterns:

1. Application factory:
   from fastapi import FastAPI
   from app.routers import user_router, order_router

   def create_app() -> FastAPI:
       app = FastAPI(title="API", version="1.0.0")

       # Include routers
       app.include_router(user_router)
       app.include_router(order_router)

       return app

2. Dependency injection setup:
   from fastapi import Depends
   from app.database import get_session
   from app.repositories.user_repository import UserRepository

   def get_user_repository(
       session: AsyncSession = Depends(get_session)
   ) -> UserRepository:
       return UserRepository(session)

3. Database connection:
   from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
   from sqlalchemy.orm import sessionmaker

   engine = create_async_engine(DATABASE_URL)
   async_session = sessionmaker(engine, class_=AsyncSession)

   async def get_session() -> AsyncSession:
       async with async_session() as session:
           yield session

4. Middleware and startup:
   @app.on_event("startup")
   async def startup():
       await init_database()

   app.add_middleware(CORSMiddleware, ...)
```

### Wire Routing and Modules

**Java (Spring Boot):**

```text
1. Controller registration (automatic via @RestController):
   - Spring auto-discovers @RestController classes
   - Map endpoints via @RequestMapping, @GetMapping, etc.

2. Security configuration (if applicable):
   @Configuration
   @EnableWebSecurity
   public class SecurityConfig {
       @Bean
       public SecurityFilterChain filterChain(HttpSecurity http) {
           // Configure security
       }
   }
```

**Python (FastAPI):**

```text
1. Router registration:
   from app.routers.users import router as user_router
   from app.routers.orders import router as order_router

   app.include_router(user_router, prefix="/api")
   app.include_router(order_router, prefix="/api")

2. Exception handlers:
   @app.exception_handler(ValidationError)
   async def validation_exception_handler(request, exc):
       return JSONResponse(status_code=422, content={"detail": exc.errors()})
```

### Write Integration Tests

Integration tests verify that wired components work together correctly.

**Java (Spring Boot Test):**

```text
Create integration test:
  - Location: src/test/java/com/example/integration/{Feature}IT.java
  - Use @SpringBootTest for full context
  - Use TestRestTemplate or MockMvc for API testing
  - Use @Transactional for database cleanup

Example:
  @SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
  @Transactional
  class UserIntegrationTest {
      @Autowired
      private TestRestTemplate restTemplate;

      @Test
      void shouldCreateAndRetrieveUser() {
          // Arrange
          UserCreateRequest request = new UserCreateRequest("test@example.com");

          // Act - Create user
          ResponseEntity<UserDTO> createResponse = restTemplate.postForEntity(
              "/api/users", request, UserDTO.class
          );

          // Assert - Created
          assertThat(createResponse.getStatusCode()).isEqualTo(HttpStatus.CREATED);
          Long userId = createResponse.getBody().getId();

          // Act - Retrieve user
          ResponseEntity<UserDTO> getResponse = restTemplate.getForEntity(
              "/api/users/" + userId, UserDTO.class
          );

          // Assert - Retrieved
          assertThat(getResponse.getStatusCode()).isEqualTo(HttpStatus.OK);
          assertThat(getResponse.getBody().getEmail()).isEqualTo("test@example.com");
      }
  }
```

**Python (FastAPI TestClient):**

```text
Create integration test:
  - Location: tests/integration/test_{feature}_integration.py
  - Use TestClient from fastapi.testclient
  - Use async fixtures for database setup/teardown

Example:
  from fastapi.testclient import TestClient
  from app.main import create_app
  import pytest

  @pytest.fixture
  def client():
      app = create_app()
      return TestClient(app)

  @pytest.fixture
  async def setup_database():
      # Setup database
      await init_test_db()
      yield
      # Cleanup
      await clear_test_db()

  def test_should_create_and_retrieve_user(client, setup_database):
      # Arrange
      user_data = {"email": "test@example.com", "name": "Test User"}

      # Act - Create user
      create_response = client.post("/api/users", json=user_data)

      # Assert - Created
      assert create_response.status_code == 201
      user_id = create_response.json()["id"]

      # Act - Retrieve user
      get_response = client.get(f"/api/users/{user_id}")

      # Assert - Retrieved
      assert get_response.status_code == 200
      assert get_response.json()["email"] == "test@example.com"
```

### Run Integration Tests

**Java:**

```bash
# Run specific integration test
mvn verify -Dit.test=UserIntegrationTest

# Or run all integration tests
mvn verify
```

**Python:**

```bash
# Run specific integration test
pytest tests/integration/test_user_integration.py -v

# Or run all integration tests
pytest tests/integration/ -v
```

### TDD Loop for Integration

```text
FOR each integration task:

  1. Write integration test (TDD loop)
     - Write test for end-to-end flow
     - Run test, verify RED

  2. Wire components or add glue code
     - Configure DI
     - Register routes
     - Add any missing adapters

  3. Run test, verify GREEN
     - Test should now pass
     - If fails after 3 retries: HALT

  4. Mark task as passed
```

### Update Task Status

```text
Update tasks.json:
  - task.status = "passed"
  - task.test_results = {
      "integration_tests_run": 3,
      "integration_tests_passed": 3,
      "verified_green": true
    }
  - task.completed_at = current_timestamp

Update tasks.md progress tracker
```

## Step-Specific: Checkpoint Verification (Template Step 5)

After all tasks in batch complete, verify all integration tests pass and unit tests still pass.

### Run All Integration Tests

**Java:**

```bash
cd <output-dir>
mvn verify
```

**Python:**

```bash
cd <output-dir>
pytest tests/integration/ -v
```

### Verify No Regressions in Unit Tests

Also run unit tests to ensure integration work didn't break existing functionality:

**Java:**

```bash
mvn test
```

**Python:**

```bash
pytest tests/unit/ -v
```

### Update Checkpoint

```json
{
  "batch": {
    "checkpoint": {
      "verification_type": "integration",
      "verification_passed": true,
      "integration_tests_passing": 5,
      "unit_tests_passing": 27,
      "regressions": 0,
      "notes": "All components wired successfully"
    }
  }
}
```

## Step-Specific: Progress Output (Template Step 7)

```text
[Step 4/5] Integration - Batch 2/2 completed ✓
  Tasks: T042-T044 (3/3 passed)
  Integration tests: 5 passing
  Unit tests: 27 passing, 0 regressions
  Checkpoint: All components wired ✓
  Language: Java (Spring Boot)
  Progress: 44/45 tasks (98%)
  Time: 58m elapsed, ~2m remaining
  Next: Polish step
```

## Self-Review Checkpoint

After all Integration batches complete, perform self-review per `references/step-workflow.md` § Self-Review Checkpoints.

**Review:**

1. All integration tests passing
2. All unit tests still passing (no regressions)
3. DI configuration correct
4. Routing/module registration complete
5. End-to-end flows work as expected

## Continue

Proceed immediately to Step 7 (Polish). Do NOT pause or ask for confirmation.

## Common Integration Tasks

**Typical integration tasks:**

- Configure Spring Boot Application class
- Register FastAPI routers
- Set up database connection pooling
- Configure security filters/middleware
- Wire external service clients
- Set up messaging/event handlers
- Configure caching
- Set up health checks and metrics endpoints
