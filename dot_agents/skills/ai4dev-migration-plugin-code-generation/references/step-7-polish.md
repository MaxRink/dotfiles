# Step 7 — Polish

Add error handling, logging, documentation, and final refinements.

## Overview

Polish step adds production-readiness features:

- Error handling and validation
- Structured logging
- API documentation
- Code documentation (JavaDoc, docstrings)
- Final cleanup and verification

**CRITICAL**: No behavioral changes. Only add observability and documentation. All tests must continue to pass.

## Prerequisites

**PRE-FLIGHT:** Read tasks.json and verify ALL Integration step tasks have status `passed` before starting this step.

## Execute Batches Following Standard Template

See `batch-execution-template.md` for the complete batch execution loop (8 steps).

This file documents **Step-Specific Customization Points** only.

## Step-Specific: Task Execution (Template Step 4a)

For each task in the Polish batch:

### Load Language Context

Before executing tasks in each batch:

```text
Read batch.language_context from tasks.json

FOR each reference in language_context.references:
  Read skills/{language_context.skill}/references/{reference}

Example for Java Polish batch:
  Read skills/code-generation/references/java/performance.md
  Read skills/code-generation/references/java/springboot-security.md
  Read skills/code-generation/references/java/coding-standards.md

Example for Python Polish batch:
  Read skills/code-generation/references/python/fastapi-security.md
  Read skills/code-generation/references/python/coding-standards.md
```

### Add Error Handling

**Java (Spring Boot):**

```text
Apply springboot-core.md error handling patterns:

1. Global exception handler:
   @RestControllerAdvice
   public class GlobalExceptionHandler {
       @ExceptionHandler(EntityNotFoundException.class)
       public ResponseEntity<ErrorResponse> handleNotFound(EntityNotFoundException ex) {
           ErrorResponse error = new ErrorResponse(
               HttpStatus.NOT_FOUND.value(),
               ex.getMessage(),
               LocalDateTime.now()
           );
           return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
       }

       @ExceptionHandler(ValidationException.class)
       public ResponseEntity<ErrorResponse> handleValidation(ValidationException ex) {
           ErrorResponse error = new ErrorResponse(
               HttpStatus.BAD_REQUEST.value(),
               ex.getMessage(),
               LocalDateTime.now()
           );
           return ResponseEntity.badRequest().body(error);
       }
   }

2. Custom exceptions:
   public class EntityNotFoundException extends RuntimeException {
       public EntityNotFoundException(String entity, Long id) {
           super(String.format("%s not found with id: %d", entity, id));
       }
   }

3. Input validation:
   public UserDTO createUser(@Valid @RequestBody UserCreateRequest request) {
       // @Valid triggers Bean Validation
   }

   // DTO with validation
   public class UserCreateRequest {
       @NotBlank
       @Email
       private String email;

       @NotBlank
       @Size(min = 2, max = 100)
       private String name;
   }
```

**Python (FastAPI):**

```text
Apply fastapi-core.md error handling patterns:

1. Custom exception classes:
   class EntityNotFoundError(Exception):
       def __init__(self, entity: str, id: int):
           self.message = f"{entity} not found with id: {id}"
           super().__init__(self.message)

2. Exception handlers:
   from fastapi import HTTPException, status
   from fastapi.responses import JSONResponse

   @app.exception_handler(EntityNotFoundError)
   async def entity_not_found_handler(request, exc: EntityNotFoundError):
       return JSONResponse(
           status_code=status.HTTP_404_NOT_FOUND,
           content={"detail": exc.message}
       )

3. Input validation (Pydantic handles automatically):
   from pydantic import BaseModel, EmailStr, constr

   class UserCreateRequest(BaseModel):
       email: EmailStr
       name: constr(min_length=2, max_length=100)
```

### Add Structured Logging

**Java (SLF4J + Logback):**

```text
Apply coding-standards.md logging patterns:

1. Add logger to each class:
   import org.slf4j.Logger;
   import org.slf4j.LoggerFactory;

   public class UserService {
       private static final Logger logger = LoggerFactory.getLogger(UserService.class);

       public UserDTO findById(Long id) {
           logger.debug("Finding user by id: {}", id);

           Optional<User> user = userRepository.findById(id);

           if (user.isEmpty()) {
               logger.warn("User not found with id: {}", id);
               throw new EntityNotFoundException("User", id);
           }

           logger.info("User found: {}", user.get().getEmail());
           return mapper.toDTO(user.get());
       }
   }

2. Configure logback.xml:
   <configuration>
       <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
           <encoder>
               <pattern>%d{ISO8601} [%thread] %-5level %logger{36} - %msg%n</pattern>
           </encoder>
       </appender>

       <root level="INFO">
           <appender-ref ref="CONSOLE" />
       </root>
   </configuration>

3. Logging levels:
   - DEBUG: Detailed flow information
   - INFO: Important business events
   - WARN: Recoverable issues (not found, validation failures)
   - ERROR: Exceptions and failures
```

**Python (structlog):**

```text
Apply coding-standards.md logging patterns:

1. Configure structured logging:
   import structlog

   structlog.configure(
       processors=[
           structlog.stdlib.filter_by_level,
           structlog.stdlib.add_logger_name,
           structlog.stdlib.add_log_level,
           structlog.processors.TimeStamper(fmt="iso"),
           structlog.processors.JSONRenderer()
       ],
       wrapper_class=structlog.stdlib.BoundLogger,
       logger_factory=structlog.stdlib.LoggerFactory(),
   )

   logger = structlog.get_logger()

2. Use in service:
   import structlog

   logger = structlog.get_logger(__name__)

   async def find_by_id(self, user_id: int) -> Optional[UserDTO]:
       logger.debug("finding_user", user_id=user_id)

       user = await self.user_repository.find_by_id(user_id)

       if not user:
           logger.warning("user_not_found", user_id=user_id)
           raise EntityNotFoundError("User", user_id)

       logger.info("user_found", user_id=user_id, email=user.email)
       return UserDTO.from_orm(user)
```

### Add API Documentation

**Java (SpringDoc OpenAPI):**

```text
1. Add annotations to controllers:
   @Operation(summary = "Get user by ID", description = "Retrieves a user by their ID")
   @ApiResponses(value = {
       @ApiResponse(responseCode = "200", description = "User found"),
       @ApiResponse(responseCode = "404", description = "User not found")
   })
   @GetMapping("/{id}")
   public ResponseEntity<UserDTO> getUser(
       @Parameter(description = "User ID") @PathVariable Long id
   ) {
       // ...
   }

2. Configure OpenAPI:
   @Configuration
   public class OpenApiConfig {
       @Bean
       public OpenAPI customOpenAPI() {
           return new OpenAPI()
               .info(new Info()
                   .title("User Management API")
                   .version("1.0.0")
                   .description("API for managing users"));
       }
   }

3. Access docs: http://localhost:8080/swagger-ui.html
```

**Python (FastAPI - automatic):**

```text
1. Add descriptions to routes:
   @router.get(
       "/{user_id}",
       response_model=UserDTO,
       summary="Get user by ID",
       description="Retrieves a user by their unique identifier",
       responses={
           200: {"description": "User found"},
           404: {"description": "User not found"}
       }
   )
   async def get_user(user_id: int) -> UserDTO:
       # ...

2. Add examples to Pydantic models:
   class UserDTO(BaseModel):
       id: int
       email: str
       name: str

       class Config:
           json_schema_extra = {
               "example": {
                   "id": 1,
                   "email": "user@example.com",
                   "name": "John Doe"
               }
           }

3. Access docs: http://localhost:8000/docs (Swagger UI)
```

### Add Code Documentation

**Java (JavaDoc):**

```text
Add JavaDoc to public classes and methods:

/**
 * Service for managing users.
 * Provides CRUD operations and business logic for user entities.
 */
@Service
public class UserServiceImpl implements UserService {

    /**
     * Finds a user by their unique identifier.
     *
     * @param id the user ID to search for
     * @return an Optional containing the user if found
     * @throws EntityNotFoundException if user with given ID does not exist
     */
    @Override
    public Optional<UserDTO> findById(Long id) {
        // ...
    }
}
```

**Python (Docstrings):**

```text
Add docstrings to classes and functions:

class UserService:
    """Service for managing users.

    Provides CRUD operations and business logic for user entities.
    """

    async def find_by_id(self, user_id: int) -> Optional[UserDTO]:
        """Find a user by their unique identifier.

        Args:
            user_id: The user ID to search for

        Returns:
            UserDTO if found, None otherwise

        Raises:
            EntityNotFoundError: If user with given ID does not exist
        """
        # ...
```

### Run Full Test Suite

**After each polish task**, run the full test suite to ensure no behavioral changes:

**Java:**

```bash
mvn verify
```

**Python:**

```bash
pytest tests/ -v
```

**Expected**: All tests still PASS. Polish tasks should NOT change behavior.

### Update Task Status

```text
Update tasks.json:
  - task.status = "passed"
  - task.test_results = {
      "full_test_suite_run": true,
      "tests_passing": 67,
      "regressions": 0
    }
  - task.completed_at = current_timestamp

Update tasks.md progress tracker
```

## Step-Specific: Checkpoint Verification (Template Step 5)

After all tasks in batch complete, verify full test suite still passes.

### Run Full Test Suite

Run all tests (unit + integration + BDD):

**Java:**

```bash
cd <output-dir>
mvn clean verify
```

**Python:**

```bash
cd <output-dir>
pytest tests/ -v
# Also run coverage
pytest tests/ --cov=app --cov-report=term-missing
```

### Verify No Behavioral Changes

```text
Expected result: ALL tests still PASS

Verification:
  - Total tests should match Core + Integration test count
  - All tests must pass
  - No regressions from polish changes

IF any test FAILS:
  - Polish task introduced behavioral change (not allowed)
  - Revert the change causing failure
  - Re-run tests
```

### Code Quality Checks

**Java:**

```bash
# Run static analysis
mvn checkstyle:check
mvn pmd:check

# Check test coverage
mvn jacoco:report
```

**Python:**

```bash
# Run linting
ruff check .

# Check type hints
mypy app/

# Check formatting
black --check .
```

### Update Checkpoint

```json
{
  "batch": {
    "checkpoint": {
      "verification_type": "polish",
      "verification_passed": true,
      "total_tests_passing": 67,
      "unit_tests": 45,
      "integration_tests": 15,
      "bdd_scenarios": 7,
      "code_quality_passed": true,
      "notes": "All polish tasks complete, all tests passing"
    }
  }
}
```

## Step-Specific: Progress Output (Template Step 7)

```text
[Step 5/5] Polish - Batch 1/1 completed ✓
  Tasks: T044-T045 (2/2 passed)
  Full test suite: 67 tests passing (45 unit, 15 integration, 7 BDD)
  Code quality: All checks passed ✓
  Checkpoint: Production-ready ✓
  Language: Java (Spring Boot)
  Progress: 45/45 tasks (100%)
  Time: 66m elapsed
  Next: Completion
```

## Continue

Proceed immediately to Step 8 (Completion). Do NOT pause or ask for confirmation.

## Typical Polish Tasks

**Common polish tasks:**

- Add global exception handlers
- Add structured logging to all layers
- Generate API documentation (OpenAPI/Swagger)
- Add JavaDoc/docstrings to public APIs
- Add input validation
- Add request/response logging middleware
- Add health check endpoints
- Add metrics/monitoring endpoints
- Configure CORS
- Add security headers
- Final code cleanup (remove TODOs, debug code)
- Update README with setup instructions

**What NOT to do:**

- Don't add new features
- Don't change existing behavior
- Don't refactor core logic (only polish)
- Don't add untested code
