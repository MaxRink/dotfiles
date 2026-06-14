---
name: ai4dev-migration-plugin-code-generation
description: TDD/BDD code generation from spec-specification artifacts with interactive directory selection and environment validation. Use when the user asks to "generate code", "implement the migration", "start coding", "create implementation", or "build the target". Generates tests first, then iterates implementation until tests pass.
argument-hint: <feature-name> [--output-dir <path>] [--resume] [--batch-size <N>] [--skip-env-check]
user-invocable: true
disable-model-invocation: true
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/migration-plugin/skills/code-generation by codex-knowledge-curation/scripts/persist_project_skills.py. -->

Delegate this task to the `one-modernizer:code-generation-agent` agent.

Feature: $ARGUMENTS

# Code Generation Skill

Generates production code using **Test-Driven Development (TDD)** and **Behavior-Driven Development (BDD)** methodology.
Tests are written first from approved specifications, then implementation code is generated iteratively until all tests pass.

## CRITICAL — Autonomous Execution

This skill executes **all steps end-to-end without stopping to ask the user for input, confirmation, or preference.**
The only reason to halt is a task failure after 3 retry attempts. See the agent definition for the complete list of forbidden behaviors.

## What This Skill Does

- Reads approved spec-specification artifacts (all 4 required: functional-requirements.md, technical-plan.md, nonfunctional-requirements.md, contracts.md)
- Generates an ordered task list with step-based tracking and dependencies
- Writes tests before implementation (TDD Red → Green cycle)
- Generates BDD feature files from business rules for human-readable behavioral specs
- Runs a retry loop (max 3 attempts) when tests fail, feeding failure context back
- Tracks progress in tasks.md and tasks.json throughout execution
- Halts on critical failures with clear diagnostics
- Reports completion to the main conversation when done

## Parameters

- **Feature Name** (`$1`): Required. The feature being generated (matches `.migration/<feature-name>/`).
- **`--resume`**: Optional. Resume from the last completed task instead of regenerating the task list.

## Prerequisites

| Artifact | Required | Source | Used For |
|----------|----------|--------|----------|
| `.migration/<feature-name>/spec-specification/functional-requirements.md` | **Yes** | `/spec-specification` | Functional requirements (FR IDs), use cases (UC IDs), BR-to-FR traceability matrix |
| `.migration/<feature-name>/spec-specification/technical-plan.md` | **Yes** | `/spec-specification` | Component specifications, technology stack, implementation phases |
| `.migration/<feature-name>/spec-specification/nonfunctional-requirements.md` | **Yes** | `/spec-specification` | NFR IDs (performance, security, reliability requirements) |
| `.migration/<feature-name>/spec-specification/contracts.md` | **Yes** | `/spec-specification` | API contracts (REST, messaging, database, file integration specs) |
| `.migration/<feature-name>/analysis/analysis.json` | Optional | `/analysis` | Business rule details, pseudocode, control flows |
| `.migration/<feature-name>/architect/target-architecture.md` | Optional | `/architect` | Architecture patterns, component relationships |

**Hard stop** if required artifacts are missing — validated by PreToolUse hook.

## When to Use

**Invoke this skill when:**

- All 4 spec-specification artifacts are approved and exist (functional-requirements.md, technical-plan.md, nonfunctional-requirements.md, contracts.md)
- You are ready to generate implementation code from approved specs
- You want test-first development with automated retry on failures
- You need BDD feature files for behavioral specification

## Output Structure

```text
.migration/<feature-name>/code-generation/
├── tasks.json                              # Machine-readable task list and progress
├── tasks.md                                # Human-readable progress tracker
├── database/                                   # DB schema artifacts (conditional)
│   ├── schema.sql                              # Complete DDL
│   ├── migrations/                             # Up/down migration scripts
│   ├── seeds/                                  # Test/seed data
│   └── docs/                                   # ERD.md, SCHEMA.md
├── src/                                    # Generated source code
│   ├── types/                              # Shared types and interfaces
│   ├── validators/                         # Validation logic
│   ├── services/                           # Business logic services
│   ├── controllers/                        # API handlers
│   └── ...                                 # Additional layers per technical-plan.md
├── tests/
│   ├── unit/                               # Unit test files
│   └── integration/                        # Integration test files
└── features/                               # BDD feature files
    └── <domain>/
        ├── <feature-name>.feature          # Gherkin scenarios
        └── steps/                          # Step definitions
            └── <step-name>.<ext>
```

**Only these files/directories are allowed.** Do not create any files outside this structure. Completion and status reports are printed as messages, not written to files.

**Explicitly FORBIDDEN files:** COMPLETION-SUMMARY.md, README.md, SUMMARY.md, STATUS.md, or any file in the
code-generation root directory other than tasks.json and tasks.md. The agent enforces this via Gate 3.

## Workflow

The code generation workflow consists of 9 steps (0-8). Each step has detailed documentation in the `references/` directory.

**All batch execution steps (3-7) follow the same pattern** defined in `references/batch-execution-template.md`:

1. Print batch header
2. Load language-specific references (with caching — skip already-loaded refs)
3. Initialize batch state
4. Execute batch tasks (step-specific logic, state updates per-task not per-file)
5. Run batch checkpoint (step-specific verification)
6. Finalize batch
7. Print progress update + evaluate turn budget (graceful save if approaching limit)
8. Continue to next batch (no pause)

### Step 0 — Configuration & Validation

**See `references/step-0-configuration.md` for complete details.**

Configuration and validation steps that run before code generation begins:

- **0a**: Parse command-line arguments (`--output-dir`, `--resume`, `--batch-size`, `--skip-env-check`, `--force-restart`)
  - **If `--resume` flag is set**: Read existing tasks.json, determine resume point, skip directly to resume point (bypasses Steps 0b-0e, Steps 1-2)
  - **If `--resume` NOT set**: Continue with Steps 0b-0e (normal flow)
- **0b**: Resolve output directory with priority: CLI → Prompt → ENV → Default
  - **Interactive prompt** if `--output-dir` not provided: asks user for directory
  - Uses `$CODE_GEN_OUTPUT_DIR` environment variable as default if set
  - Falls back to `.migration/<feature-name>/code-generation/`
- **0c**: Verify prerequisites exist (functional-requirements.md, technical-plan.md, etc.)
  - **HOOK** (automatic): Validates spec artifact quality (BR IDs, required sections, Technology Stack)
  - Denies code generation if critical sections missing
- **0d**: Detect target stack (read technical-plan.md to extract language, frameworks, build tools)
  - **HOOK** (automatic): Validates target stack is approved
  - Java minimum version 17, Python minimum version 3.9
  - Denies if version too old or language unsupported
- **0e**: Validate environment (Java, Python)
  - Executes language-specific check scripts (environment-check-<language>.sh)
  - **HALT on critical failure** (exit code 1)
  - Continue with warnings (exit code 2)
  - Skip if `--skip-env-check` flag provided

### Step 1 — Load Context & Language Skills

**See `references/step-1-context-loading.md` for complete details.**

Load specification context and language-specific code generation guidance:

- **1a**: Validate and load all 4 required spec artifacts (functional-requirements.md, technical-plan.md, nonfunctional-requirements.md, contracts.md) plus optional artifacts (analysis.json, target-architecture.md)
- **1b**: Detect and load language-specific skill
  - Java + Spring Boot → `java-codegen` skill
  - Java + Quarkus → `quarkus-codegen` skill
  - Python → `python-codegen` skill
  - References loaded per-batch during execution (not all at once)

**Language Skills Available:**

| Language | Skill | References |
|----------|-------|------------|
| Java (Spring Boot) | `java-codegen` | fundamentals.md, springboot-core.md, springboot-security.md, testing.md, build-tools.md, jpa-patterns.md, microservices.md, concurrency.md, performance.md, coding-standards.md |
| Java (Quarkus) | `quarkus-codegen` | fundamentals.md, quarkus-core.md, quarkus-security.md, testing.md, build-tools.md, persistence-patterns.md, microservices.md, reactive-patterns.md, coding-standards.md |
| Python | `python-codegen` | fundamentals.md, fastapi-core.md, fastapi-security.md, testing.md, build-tools.md, sqlalchemy-patterns.md, async-patterns.md, coding-standards.md |
| DB Schema | `db-codegen` | postgresql-patterns.md, mysql-patterns.md, schema-design-rules.md, migration-patterns.md (loaded when contracts.md § 3 or technical-plan.md § 4 contains database contracts) |

### Step 2 — Generate Task List with Batching

**See `references/step-2-task-generation.md` for complete details.**

**Load references** (needed for task generation):

- `references/task-schema.json` - Task schema
- `references/task-template.md` - Tasks.md format
- `references/step-workflow.md` - Per-step task generation criteria
- `references/batch-strategy.md` - Batch sizing and time estimates
- `references/state-management.md` - State schema v2.0
- `references/language-skill-integration.md` - Language context mappings

Generate ordered task list covering all 5 steps (Setup, Tests, Core, Integration, Polish) with language-aware batch enrichment:

1. **Generate tasks** from spec artifacts (using step-workflow.md criteria)
2. **Calculate batches** with language-specific time estimates (using batch-strategy.md)
   - Java tasks take longer (more verbose): setup=0.5min, tests=0.7min, core=2.5min
   - Python tasks are faster (more concise): setup=0.3min, tests=0.4min, core=1.8min
3. **Enrich batches** with language context (using language-skill-integration.md)
   - Add skill name, references, templates, conventions, test_command
4. **Write tasks.json** with complete state schema v2.0 (using state-management.md schema)
5. **Print execution plan** with batch breakdown
6. **Continue immediately to Step 3** (no pause or confirmation)

**Example batch calculation (Java, 45 tasks):**

- Setup: 1 batch, 3 tasks (~2 min)
- Tests: 3 batches, 15 tasks (~11 min)
- Core: 10 batches, 20 tasks (~50 min)
- Integration: 5 batches, 5 tasks (~18 min)
- Polish: 1 batch, 2 tasks (~2 min)
- **Total**: 20 batches, ~83 minutes

### Step 3 — Setup

**See `references/step-3-setup.md` for complete details.**

**See `references/batch-execution-template.md` for the standard batch execution loop.**

Execute Setup batch (typically 1 batch with all setup tasks):

**Step-Specific Customization:**

- **Task execution**: Create directory structure, build files, config files using language-specific templates
  - Java: pom.xml, src/main/java, src/test/java, application.yml
  - Python: pyproject.toml, src/app, tests/, alembic/
- **Database schema tasks** (conditional — when contracts.md § 3 or technical-plan.md § 4 contains database contracts):
  - Load `db-codegen` skill references (DB-type-specific patterns, migration-patterns.md, schema-design-rules.md)
  - Generate ERD diagram (database/docs/ERD.md)
  - Generate schema DDL (database/schema.sql)
  - Generate migration scripts (database/migrations/ + framework-specific path)
  - Generate seed data (database/seeds/sample_data.sql)
  - Generate schema documentation (database/docs/SCHEMA.md)
- **Checkpoint verification**: Validate structure, build config (mvn validate, uv sync --check), test runner ready, schema valid (if DB tasks present)
- **Progress output**: Structure validated ✓

**Continue immediately to Step 4 (Tests).**

### Step 4 — Tests (TDD Red)

**See `references/step-4-tests.md` for complete details.**

**See `references/batch-execution-template.md` for the standard batch execution loop.**

**PRE-FLIGHT**: Verify ALL Setup tasks have status `passed` before starting.

**Load deferred reference**: Read `references/bdd-feature-template.md` before writing BDD features.

Execute Tests batches (typically 2-3 batches):

**Step-Specific Customization:**

- **Task execution**: Write unit tests, integration test stubs, BDD feature files using language test frameworks
  - Java: JUnit 5, Mockito, AssertJ, Cucumber-JVM
  - Python: pytest, FastAPI TestClient, behave
  - **CRITICAL**: Run each test to verify RED (must fail - no implementation exists yet)
- **Checkpoint verification**: Run all tests in batch, verify ALL FAIL (RED state)
- **Progress output**: Tests written: X, RED verified: X

**Continue immediately to Step 5 (Core).**

### Step 5 — Core (TDD Green)

**See `references/step-5-core.md` for complete details.**

**See `references/batch-execution-template.md` for the standard batch execution loop.**

**PRE-FLIGHT**: Verify ALL Tests step tasks have status `passed` before starting. **Do NOT write any src/ file until verified.**

**Load deferred references**: Read `references/tdd-loop-rules.md` and `references/testing-anti-patterns.md` before writing implementation.

Execute Core batches (typically 3-10 batches depending on size):

**Step-Specific Customization:**

- **Task execution**: Implement production code using TDD loop (RED → GREEN)
  - Run tests to verify RED
  - Write minimal implementation using language-specific patterns
  - Java: Service/Repository/Controller layers, @Service, @Repository, @Transactional
  - Python: service modules, async def, FastAPI routers, Pydantic DTOs
  - Run tests to verify GREEN
- **Checkpoint verification**: Run all tests (current + previous batches), verify ALL PASS, check for regressions
- **Progress output**: Tests passing: X, regressions: 0

**Self-review checkpoint** after all Core batches complete (see `references/step-workflow.md`).

**Continue immediately to Step 6 (Integration).**

### Step 6 — Integration

**See `references/step-6-integration.md` for complete details.**

**See `references/batch-execution-template.md` for the standard batch execution loop.**

**PRE-FLIGHT**: Verify ALL Core step tasks have status `passed` before starting.

Execute Integration batches (typically 1-2 batches):

**Step-Specific Customization:**

- **Task execution**: Wire components together, write integration tests
  - Configure dependency injection (Spring DI, FastAPI Depends)
  - Register routers/controllers
  - Write end-to-end integration tests (@SpringBootTest, TestClient)
- **Checkpoint verification**: Run integration tests, verify unit tests still pass (no regressions)
- **Progress output**: Integration tests: X passing, unit tests: Y passing, regressions: 0

**Self-review checkpoint** after all Integration batches complete.

**Continue immediately to Step 7 (Polish).**

### Step 7 — Polish

**See `references/step-7-polish.md` for complete details.**

**See `references/batch-execution-template.md` for the standard batch execution loop.**

**PRE-FLIGHT**: Verify ALL Integration step tasks have status `passed` before starting.

Execute Polish batches (typically 1 batch):

**Step-Specific Customization:**

- **Task execution**: Add production-readiness features (NO behavioral changes)
  - Error handling (global exception handlers, custom exceptions)
  - Structured logging (SLF4J, structlog)
  - API documentation (SpringDoc OpenAPI, FastAPI automatic docs)
  - Code documentation (JavaDoc, docstrings)
  - **CRITICAL**: Run full test suite after each task to ensure no behavioral changes
- **Checkpoint verification**: Run full test suite (unit + integration + BDD), verify all still PASS, check code quality
- **Progress output**: Full test suite: X tests passing, code quality checks passed

**Continue immediately to Step 8 (Completion).**

### Step 8 — Completion

**See `references/step-8-completion.md` for complete details.**

After all Polish batches complete successfully:

1. **Final verification**: Run full test suite one final time, count metrics (tests, files, LOC)
2. **Update final state**: Set execution.status = "completed", progress.percentage = 100
3. **Print completion report**: Comprehensive summary with next steps

**Example completion report:**

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Code Generation Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Feature: payment-processing
Output: ./src/generated
Language: Java (Spring Boot 3.2, Maven 3.9)

Summary:
  Tasks: 45 total, 45 passed, 0 failed
  Batches: 10 total, 10 completed
  Tests: 67 passing (45 unit, 15 integration, 7 BDD)
  Duration: 66m 30s
  Files generated: 52 files

Next steps:
  • Review generated code: cd ./src/generated
  • Run tests: mvn test
  • Start application: mvn spring-boot:run
  • API docs: http://localhost:8080/swagger-ui.html
  • Deploy or integrate into main codebase
```

## Edge Cases and Failure Handling

### Task Failure After Max Retries

When a task fails after 3 retry attempts:

```text
[Step 3/5] Core - Batch 2/4
  Task T027: Implement PaymentGatewayAdapter... ⚠ (retry 1/3)
  Task T027: Implement PaymentGatewayAdapter... ⚠ (retry 2/3)
  Task T027: Implement PaymentGatewayAdapter... ✗ (failed after 3 attempts)

✗ Batch 2/4 failed at task T027

Error Details:
  Task: T027 - Implement PaymentGatewayAdapter
  Test failures: 2/2 tests failing
  Error: Missing validation logic for card expiry

State saved to: ./src/generated/tasks.json

To resume after fixing:
  1. Review error above
  2. Manually fix the issue if needed
  3. Run: /code-generation payment-processing --resume

Or to see detailed status:
  /mstatus payment-processing
```

**Action:**

1. Update task.status = "failed"
2. Add entry to errors array in tasks.json
3. Update batch.status = "failed"
4. Update execution.status = "failed"
5. Save state
6. HALT execution
7. Print resume instructions

See `references/tdd-loop-rules.md` § Halt on Failure for the full TDD retry procedure.

### Batch Checkpoint Failure

When checkpoint verification fails:

```text
[Step 3/5] Core - Batch 3/4
  Tasks: T029-T033 (5/5 completed)

Running checkpoint...
  ✗ Regression detected
  Previously: 27 tests passing
  Currently: 26 tests passing
  Failed: T025 (PaymentService.test - timeout)

✗ Batch checkpoint failed - regression introduced

Analysis:
  Recent changes: OrderService implementation
  Likely cause: Shared database connection pool exhaustion

State saved. Fix regression and resume.
```

**Action:**

1. Update batch.status = "failed"
2. Update batch.checkpoint.verification_passed = false
3. Add regression details to errors array
4. Save state
5. HALT execution
6. Print diagnostic information

### Resume After Failure

When user runs `/code-generation <feature> --resume`:

```text
1. Read tasks.json
2. Check execution.status:
   - If "completed": Ask if user wants to restart
   - If "failed" or "in_progress": Auto-resume

3. Load resume point:
   - current_step
   - current_batch
   - current_task (if in middle of batch)

4. Skip completed batches

5. Resume from failed/incomplete task:
   - Reset task.attempts = 0 if previously failed
   - Continue execution from that point

6. Print resume banner:
   "Resuming from: Step 3/5 Core, Batch 2/4, Task T027"
```

**Example:**

```bash
$ /code-generation payment-processing --resume

Resuming from saved state...
  Feature: payment-processing
  Output: ./src/generated (from previous run)
  Last checkpoint: Core batch 2/4, task T027 (failed)
  Progress: 23/45 tasks (51%), 6/10 batches completed

Resetting failed task T027 for retry...

Continuing execution...

[Step 3/5] Core - Batch 2/4 (resumed)
  Task T027: Implement PaymentGatewayAdapter... ✓ (2 tests passing)
  Task T028: Implement InventoryService... ✓ (3 tests passing)
  Checkpoint: 30 tests passing, 0 regressions ✓

[Step 3/5] Core - Batch 3/4
  Task T029: Implement EmailService... ✓
  ...
```

### Very Large Codebase (>10 Components)

See `references/step-workflow.md` § Large Codebase Strategy for batch-by-module approach and batch checkpoint procedure.

### Resume Quick Reference

- `--resume` flag reads existing `tasks.json`
- Skips all tasks with status `passed`
- Re-attempts tasks with status `failed` (resets attempts to 0)
- Continues with `not-started` tasks in sequence

### Missing Optional Artifacts

- If `analysis.json` is not available, derive edge cases from functional-requirements.md acceptance criteria
- If `target-architecture.md` is not available, derive architecture from technical-plan.md only
- Log informational message but do not halt

**Note:** The 4 core spec files (functional-requirements.md, technical-plan.md, nonfunctional-requirements.md, contracts.md) are all REQUIRED and validated in Step 1a.

## Quality Guarantees

- **Golden rule enforced** — see `references/tdd-loop-rules.md` § Critical Rules
- **BR traceability** — every test references at least one BR ID; every implementation cites its BR IDs in comments
- **Self-review checkpoints** — after Core and Integration steps; see `references/step-workflow.md` § Self-Review Checkpoints
- **Anti-pattern prevention** — see `references/testing-anti-patterns.md`

## Example Usage

```bash
# Interactive mode (will prompt for output directory)
/code-generation payment-processing

# With output directory specified (no prompt)
/code-generation payment-processing --output-dir ./src/generated

# Using environment variable for default
export CODE_GEN_OUTPUT_DIR=/tmp/codegen
/code-generation payment-processing

# Resume after fixing a failed task
/code-generation payment-processing --resume

# Custom batch size (override auto-calculation)
/code-generation payment-processing --batch-size 3

# Skip environment validation (CI/CD environments)
/code-generation payment-processing --skip-env-check --output-dir ./build

# Force restart (ignore existing state)
/code-generation payment-processing --force-restart --output-dir ./new-output
```

## Execution Example

```text
$ /code-generation payment-processing

Output directory for code generation?
  [default: .migration/payment-processing/code-generation]
▸ ./output

[Step 0e] Environment Validation
Detected Stack: Java 17, Quarkus 3.8, Maven
  ✓ Java 17.0.9 detected
  ✓ javac available
  ✓ JAVA_HOME set
  ✓ Maven 3.9.5 available

Code Generation Plan:
  Feature: payment-processing
  Output: ./output
  Total tasks: 45 across 5 steps
  Total batches: 10
  Estimated time: ~66 minutes

Batch breakdown:
  Setup: 1 batch, 3 tasks (~1 min)
  Tests: 2 batches, 15 tasks (~8 min)
  Core: 4 batches, 20 tasks (~40 min)
  Integration: 2 batches, 5 tasks (~15 min)
  Polish: 1 batch, 2 tasks (~2 min)

Starting execution...

[Step 1/5] Setup - Batch 1/1
  Task T001: Create directory structure... ✓
  Task T002: Generate pom.xml... ✓
  Task T003: Configure test framework... ✓
  Checkpoint: Structure validated ✓
  Completed: 3/3 tasks (1m 20s)

[Step 2/5] Tests - Batch 1/2
  Task T004: Write UserService tests... ✓
  Task T005: Write PaymentService tests... ✓
  Task T006: Write OrderService tests... ✓
  Task T007: Write ProductService tests... ✓
  Task T008: Write CartService tests... ✓
  Task T009: Write AuthController tests... ✓
  Task T010: Write OrderController tests... ✓
  Task T011: Write BDD feature: User checkout... ✓
  Task T012: Write BDD feature: Payment... ✓
  Task T013: Write BDD step definitions... ✓
  Checkpoint: 10 tests RED verified ✓
  Progress: 13/45 tasks (29%)
  Time: 6m 15s elapsed, ~60m remaining
  Next: Tests batch 2/2

[Step 2/5] Tests - Batch 2/2
  ...

[Step 3/5] Core - Batch 1/4
  Task T019: Implement UserService... ✓ (3 tests passing)
  Task T020: Implement PaymentService... ✓ (2 tests passing)
  Task T021: Implement OrderService... ✓ (4 tests passing)
  Task T022: Implement ProductService... ✓ (2 tests passing)
  Task T023: Implement CartService... ✓ (3 tests passing)
  Checkpoint: 14 tests passing, 0 regressions ✓
  Progress: 23/45 tasks (51%)
  Time: 24m elapsed, ~42m remaining
  Next: Core batch 2/4

[Step 3/5] Core - Batch 2/4
  ...

[Step 5/5] Polish - Batch 1/1
  Task T044: Add error handling... ✓
  Task T045: Add structured logging... ✓
  Checkpoint: Full test suite (67 tests) passing ✓
  Progress: 45/45 tasks (100%)
  Time: 66m 30s elapsed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Code Generation Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Feature: payment-processing
Output: ./output

Summary:
  Tasks: 45 total, 45 passed, 0 failed
  Batches: 10 total, 10 completed
  Tests: 67 passing (45 unit, 15 integration, 7 BDD scenarios)
  Duration: 66m 30s
  Files generated: 52 files

Next steps:
  • Review generated code: cd ./output
  • Run tests: mvn test
  • Deploy or integrate into main codebase
```
