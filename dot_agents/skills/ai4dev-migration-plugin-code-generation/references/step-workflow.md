````markdown
# Step Workflow — Detailed Guide

This reference describes each step of the code generation process in detail, including what each step produces, how tasks are structured, and decision criteria.

## Step Overview

```text
Step 1: Setup        → Foundation (structure, config, dependencies)
Step 2: Tests        → TDD Red (all tests fail — no implementation)
Step 3: Core         → TDD Green (implement until tests pass)
Step 4: Integration  → Wire components, integration tests
Step 5: Polish       → Error handling, logging, cleanup
```

Steps execute strictly in order. A step cannot start until the previous step is `completed`.

### Mandatory Pre-Flight Verification

Before starting ANY step (except Step 1), perform this check:

```text
PRE-FLIGHT for Step N:
  1. READ tasks.json
  2. FOR EACH task in Step N-1:
     - VERIFY status == "passed"
  3. IF any task is NOT "passed":
     - STOP — do not proceed to Step N
     - Complete or fix the remaining Step N-1 tasks first
  4. Only after ALL Step N-1 tasks are "passed" → proceed
```

### Task Tracking Per Task Completion

After a task completes (all files written, tests verified):

```text
AFTER task completion (not after each file write):
  1. UPDATE the corresponding task in tasks.json (status, attempts, test_results)
  2. UPDATE tasks.md with the matching status change
  3. Within a single task, write ALL source files and run tests BEFORE updating state
```

This reduces state update overhead while ensuring tasks.json reflects execution at task-level granularity. See `batch-execution-template.md` for the authoritative update pattern.

---

## Step 1 — Setup

### Purpose
Establish the project foundation so that subsequent steps can write code into a well-defined structure.

### Tasks To Generate

| Task Type | Description | Example |
|-----------|-------------|---------|
| Directory structure | Create source and test directory layout | `src/`, `tests/`, `features/` |
| Configuration files | Project config, linter, formatter, tsconfig, etc. | `tsconfig.json`, `.eslintrc` |
| Dependency manifest | Package file with all required dependencies | `package.json`, `requirements.txt`, `pom.xml` |
| Test configuration | Test runner setup, BDD framework config | `jest.config.ts`, `cucumber.js` |
| Shared utilities | Base classes, types, interfaces, constants | `src/types/index.ts`, `src/constants.ts` |
| Database schema | ERD, DDL, migrations, seed data, docs (conditional — when contracts.md § 3 present) | `database/schema.sql`, `database/docs/ERD.md`, `database/migrations/` |

### Decision Criteria

- Derive **technology stack** from `technical-plan.md` § Architecture Overview
- Derive **directory layout** from `technical-plan.md` § Component Specifications
- Derive **dependencies** from `technical-plan.md` § Technology Stack and Integration Implementation
- Include test framework + BDD framework as dev dependencies

### Language-Specific Setup Guidance

When language skills were loaded in Step 1b, apply their conventions to Setup tasks:

#### Java / Spring Boot Projects

Apply patterns from the `java-codegen` skill's references (`build-tools.md`, `springboot-core.md`, `testing.md`):

- **Directory layout**: Maven standard (`src/main/java/`, `src/test/java/`, `src/main/resources/`)
- **Build manifest**: `pom.xml` (Maven) or `build.gradle.kts` (Gradle) — use the template from `references/build-tools.md`
- **Dependencies**: Spring Boot starters, JUnit 5, Mockito, AssertJ as defined in the skill references
- **Test runner**: JUnit Platform via Maven Surefire / Failsafe plugins (or Gradle `useJUnitPlatform()`)
- **BDD framework**: Cucumber-JVM with `cucumber-spring` for Spring integration
- **Configuration**: `application.yml` with environment profiles (`local`, `test`, `prod`)
- **Java version**: Match the version from `technical-plan.md` (default to Java 21 if unspecified)

When JPA/Hibernate is in the target stack (see `references/jpa-patterns.md`):
- Include Spring Data JPA starter and database driver in dependencies
- Set `spring.jpa.open-in-view: false` in `application.yml`

When microservices are in scope (see `references/microservices.md`):
- Include Spring Cloud dependencies and Resilience4j starters
- Configure `bootstrap.yml` for Config Server if specified in technical-plan.md

#### Python / FastAPI Projects

Apply patterns from the `python-codegen` skill's references (`build-tools.md`, `fastapi-core.md`, `sqlalchemy-patterns.md`, `testing.md`):

- **Directory layout**: `src/app/` with feature modules (`users/`, `orders/`), each containing `router.py`, `schemas.py`, `models.py`, `service.py`, `repository.py`
- **Build manifest**: `pyproject.toml` — use the template from `references/build-tools.md`
- **Package manager**: uv (primary) or poetry — `uv sync` to install from lockfile
- **Dependencies**: FastAPI, uvicorn, SQLAlchemy 2.0, asyncpg, pydantic-settings, Alembic as defined in the skill references
- **Dev dependencies**: pytest, pytest-asyncio, pytest-cov, pytest-mock, httpx, hypothesis, ruff, mypy
- **Test runner**: pytest with `asyncio_mode = "auto"` in pyproject.toml
- **BDD framework**: pytest-bdd or behave with step definitions
- **Configuration**: pydantic-settings `Settings` class with `.env` file, environment-aware
- **Python version**: Match the version from `technical-plan.md` (default to Python 3.11 if unspecified)
- **Linting / Formatting**: ruff (replaces black + isort + flake8), ZERO `# noqa` tolerance
- **Type checking**: mypy with `strict = true`, ZERO `# type: ignore` tolerance

When SQLAlchemy is in the target stack (see `references/sqlalchemy-patterns.md`):
- Configure async engine with `create_async_engine` and `async_sessionmaker`
- Initialize Alembic with async `env.py` configuration
- Set `pool_pre_ping=True` for connection health checking

When async/concurrency is in scope (see `references/async-patterns.md`):
- Use `asyncio.TaskGroup` (3.11+) for structured concurrency
- Configure thread pool executor for sync blocking calls

### Completion Criteria

- All directories exist
- Config files are valid (parseable)
- Dependency manifest includes all required packages
- Test runner can be invoked (even with 0 tests)

---

## Step 2 — Tests (TDD Red)

### Pre-Flight

Read tasks.json. Verify ALL Step 1 (Setup) tasks have status `passed`. If not, go back and complete them.

### Purpose
Write all unit tests and BDD feature files BEFORE any implementation code exists. This is the "Red" step — every test must fail because the implementations don't exist yet.

### Tasks To Generate

| Task Type | Description | Source |
|-----------|-------------|--------|
| Unit tests per component | Test file for each component in technical-plan.md | Component Specifications |
| BDD feature files | Gherkin scenarios from business rules | functional-requirements.md § Functional Requirements |
| BDD step definitions | Step definition stubs | Derived from feature files |
| Integration test stubs | Test files for cross-component interactions | Integration Implementation |

### How to Derive Tests from Specs

1. **Read `functional-requirements.md`** — each Functional Requirement (FR ID) and Use Case (UC ID) becomes one or more test cases
2. **Read `technical-plan.md`** — each Component Specification defines the unit under test
3. **Map FR IDs to components** — use the Traceability Matrix from functional-requirements.md (BR → FR → Component)
4. **Read BDD template** — see `references/bdd-feature-template.md` for Gherkin conventions

### Test Naming Convention

```text
tests/unit/<component-name>.<test-ext>
tests/integration/<interaction-name>.<test-ext>
features/<domain>/<feature-name>.feature
features/<domain>/steps/<step-name>.<ext>
```

### Watch It Fail — Mandatory RED Verification

After writing each test file, **run the tests and verify they fail**:

```text
For each test file written:
  1. RUN the test file using the project's test runner
  2. VERIFY every test in the file FAILS (expected: no implementation exists)
  3. IF any test PASSES:
     - STOP — this test is vacuous or testing mock behavior
     - DELETE the passing test
     - REWRITE it to test real behavior
     - RE-RUN to verify it now fails
  4. Record the failure output as evidence of RED state
```

This prevents false-positive tests that pass regardless of implementation.

### Completion Criteria

- Every component in technical-plan.md has a corresponding test file
- Every FR ID from functional-requirements.md appears in at least one test or scenario
- All tests compile/parse but fail (no implementation) — **verified by running them**
- BDD feature files have proper tags (@BR###, @domain)

---

## Step 3 — Core (TDD Green)

### Pre-Flight

Read tasks.json. Verify ALL Step 2 (Tests) tasks have status `passed`. **Do NOT write any file under `src/` until this verification passes.** If any Tests task is not `passed`, go back and complete it.

### Purpose
Implement the minimum production code to make tests pass. This is the "Green" step — each task generates implementation code and then runs its associated tests. Uses the TDD retry loop (max 3 attempts).

### Tasks To Generate

One task per component from `technical-plan.md` § Component Specifications, ordered by dependency:

| Task Type | Description | Dependencies |
|-----------|-------------|-------------|
| Domain models / entities | Data structures, types | Setup tasks |
| Repository / data access | Database interaction layer | Models |
| Services / business logic | Core business rule implementations | Repository + Models |
| Controllers / handlers | HTTP/API handlers | Services |
| Middleware / interceptors | Cross-cutting concerns | Services |

### Dependency Ordering Rules

1. **Leaf-first**: Implement components with no internal dependencies first
2. **Layer-by-layer**: Data layer → Business layer → Presentation layer
3. **Shared before specific**: Utilities and shared types before domain-specific code
4. **Interface before implementation**: If using dependency injection, define interfaces first

### TDD Loop Per Task

See `tdd-loop-rules.md` for the full algorithm (sub-steps, retry logic, failure feedback format, halt procedure).

### Completion Criteria

- All unit tests pass for every completed Core task
- Each implementation file references the BR IDs it implements (in code comments)
- No test modifications (tests written in Step 2 are authoritative)

---

## Step 4 — Integration

### Pre-Flight

Read tasks.json. Verify ALL Step 3 (Core) tasks have status `passed`. If not, go back and complete them.

### Purpose
Wire components together and verify cross-component behavior. Uses the same TDD retry loop for integration tests.

### Tasks To Generate

| Task Type | Description | Dependencies |
|-----------|-------------|-------------|
| Component wiring | Dependency injection, module registration | All Core tasks |
| API route registration | Wire controllers to routes | Controllers |
| Database setup | Migration scripts, seed data | Repository tasks |
| External integrations | Client configurations, adapters | Services |
| Integration tests | Cross-component test execution | All above |

### Integration Test Scope

Integration tests verify:
- Components communicate correctly through defined interfaces
- Data flows end-to-end through the layers
- External integration points handle connection, timeout, and error scenarios
- Business workflows spanning multiple components produce correct outcomes

### Completion Criteria

- All integration tests pass
- Components are wired and functional as a system
- External integration points have adapter implementations
- Database migrations/schemas are defined

---

## Step 5 — Polish

### Pre-Flight

Read tasks.json. Verify ALL Step 4 (Integration) tasks have status `passed`. If not, go back and complete them.

### Purpose
Refactor for production readiness without changing behavior. All existing tests must continue to pass after each polish task.

### Tasks To Generate

| Task Type | Description | Dependencies |
|-----------|-------------|-------------|
| Error handling | Try/catch, error classes, error responses | Core + Integration |
| Input validation | Request validation, sanitization | Controllers |
| Logging | Structured logging at key points | All components |
| Documentation | JSDoc/docstrings, README | All components |
| Code cleanup | Remove TODOs, dead code, improve naming | All |

### Constraints

- **No behavioral changes** — all existing tests must still pass
- **No new features** — only improve quality of existing code
- **Run full test suite** after each polish task to ensure no regressions

### Completion Criteria

- Full test suite passes (unit + integration + BDD)
- Error handling covers identified edge cases
- Logging provides observability at key decision points
- Code is clean, documented, and follows project conventions

---

## Self-Review Checkpoints

Perform a two-stage self-review after completing all tasks in the Core step and again after the Integration step:

### After Core (Step 3)

1. **Spec compliance** — Verify every FR ID from functional-requirements.md has a corresponding implementation. Check that no requirements were missed or invented.
2. **Code quality** — Verify implementations are minimal (no speculative features), properly structured, and follow conventions from technical-plan.md.
3. If issues found, fix before proceeding to Integration.

### After Integration (Step 4)

1. **Spec compliance** — Verify all integration points from technical-plan.md § Integration Implementation are covered. Check that data flows match the specified architecture.
2. **Code quality** — Verify wiring is clean, no circular dependencies, error propagation is correct across component boundaries.
3. If issues found, fix before proceeding to Polish.

---

## Large Codebase Strategy

When the technical plan specifies many components (>10), generate in batches:

1. **Batch by module** — group components by their domain module
2. **Complete one module end-to-end** before starting the next (Tests → Core → Integration per module)
3. **Shared infrastructure first** — generate shared types, utilities, and base classes before any module
4. **Cross-module integration last** — wire modules together after each is individually complete

### Batch Checkpoints

Within any step, after completing every **3 tasks**, pause and run a verification checkpoint:

```text
AFTER every 3 tasks within a step:
  1. RUN the full test suite written so far
  2. VERIFY all previously-passing tests still pass (no regressions)
  3. IF any previously-passing test now fails:
     - STOP — a regression was introduced
     - IDENTIFY which of the last 3 tasks caused the regression
     - FIX the regression before continuing
  4. LOG the checkpoint result in tasks.md:
     "Batch checkpoint after T00X: <N> tests passing, 0 regressions"
```

This prevents context drift and catches regressions early rather than discovering them at the end of a long step.

````
