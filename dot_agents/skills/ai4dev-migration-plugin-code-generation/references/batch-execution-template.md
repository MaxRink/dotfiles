# Batch Execution Template

This template defines the standard batch execution pattern used by all code generation steps (Setup, Tests, Core, Integration, Polish).

## Purpose

Provide a consistent, reusable pattern for executing batches to:

- Eliminate duplication across steps
- Ensure consistent state management
- Standardize progress reporting
- Enable language-aware code generation

## Standard Batch Execution Loop

```text
FOR each batch in current_step.batches:

  ┌─────────────────────────────────────────────────────┐
  │ 1. PRINT BATCH HEADER                               │
  └─────────────────────────────────────────────────────┘

  Print: "[Step {step_number}/5] {step_name} - Batch {batch_number}/{total_batches}"

  Example:
    "[Step 3/5] Core - Batch 2/4"

  ┌─────────────────────────────────────────────────────┐
  │ 2. LOAD LANGUAGE-SPECIFIC REFERENCES                │
  └─────────────────────────────────────────────────────┘

  IMPORTANT: Use reference caching to conserve turns. Track which references
  have already been loaded in previous batches to avoid redundant reads.

  IF batch has language_context:
    1. Read batch from tasks.json
    2. Extract batch.language_context
    3. Compare batch.language_context.references with previously loaded references
    4. FOR each reference in language_context.references:
         IF reference was already loaded in a previous batch within the SAME step:
           SKIP — already in context, no need to re-read
         ELSE:
           path = skills/{language_context.skill}/references/{reference}
           Read {path} using Read tool
           Add to loaded_references tracker

    Example — Java Core batch 2/4 (batch 1/4 already loaded fundamentals.md + springboot-core.md):
      SKIP: fundamentals.md (already loaded)
      SKIP: springboot-core.md (already loaded)
      Read skills/code-generation/references/java/jpa-patterns.md (NEW for this batch)
      Read skills/code-generation/references/java/coding-standards.md (NEW for this batch)

    This saves 2-6 Read turns per batch (significant over 10-20 batches).

  ALSO load DB-specific references (if applicable):

  IF batch has db_context:
    1. Extract batch.db_context
    2. Apply same caching logic — skip already-loaded DB references
    3. FOR each NEW reference in db_context.references:
         path = skills/{db_context.skill}/references/{reference}
         Read {path} using Read tool

  ELSE (no language context - generic workflow):
    Skip language reference loading
    Use patterns from technical-plan.md only

  ┌─────────────────────────────────────────────────────┐
  │ 3. INITIALIZE BATCH STATE                           │
  └─────────────────────────────────────────────────────┘

  Update tasks.json:
    - batch.status = "in_progress"
    - batch.started_at = current_timestamp
    - execution.current_batch = batch_number

  Save tasks.json to disk

  ┌─────────────────────────────────────────────────────┐
  │ 4. EXECUTE BATCH TASKS                              │
  └─────────────────────────────────────────────────────┘

  FOR each task in batch.tasks:

    a. Execute step-specific task logic:
       ┌────────────────────────────────────────────┐
       │ STEP-SPECIFIC TASK EXECUTION               │
       │ (See individual step reference files)     │
       │                                            │
       │ - Setup: Create files, configs            │
       │ - Tests: Write test files, verify RED     │
       │ - Core: Implement code, verify GREEN      │
       │ - Integration: Wire components, test      │
       │ - Polish: Refactor, document, cleanup     │
       └────────────────────────────────────────────┘

       Apply language-specific patterns if language_context exists:
         - File naming from language_context.conventions.naming
         - Templates from language_context.templates
         - Code patterns from loaded language skill references
         - Test framework from language_context.test_framework

    b. Update task status ONCE after task completes (not after each file write):
       Update tasks.json:
         - task.status = "passed" (or "failed" after retries)
         - task.completed_at = current_timestamp
         - task.duration_seconds = elapsed_time
         - task.test_results = {...} (if applicable)

       Update tasks.md progress tracker

       NOTE: Within a single task, write ALL source files and run tests
       BEFORE updating state. This reduces tool calls from ~3 per file
       to ~1 per task for state management.

    c. Handle failures:
       IF task failed after 3 retries:
         - Update task.status = "failed"
         - Update batch.status = "failed"
         - Add error to errors array
         - Save state
         - HALT execution
         - Print resume instructions

    d. Continue to next task

  ┌─────────────────────────────────────────────────────┐
  │ 5. RUN BATCH CHECKPOINT                             │
  └─────────────────────────────────────────────────────┘

  ┌────────────────────────────────────────────┐
  │ STEP-SPECIFIC CHECKPOINT VERIFICATION      │
  │ (See individual step reference files)     │
  │                                            │
  │ - Setup: Verify structure, validate configs│
  │ - Tests: Verify all RED (tests fail)      │
  │ - Core: Verify all GREEN (tests pass)     │
  │ - Integration: Verify integration tests    │
  │ - Polish: Verify full test suite          │
  └────────────────────────────────────────────┘

  Run verification using language test framework if available:
    - Java: mvn test
    - Python: pytest tests/ -v
    - Generic: per technical-plan.md

  Update batch.checkpoint with results:
    - verification_type: "structure" | "red" | "green" | "integration" | "polish"
    - verification_passed: true | false
    - metrics: step-specific metrics (tests_passing, regressions, etc.)
    - notes: human-readable checkpoint summary

  IF checkpoint fails:
    - Update batch.status = "failed"
    - Add checkpoint failure to errors array
    - Save state
    - HALT execution
    - Print diagnostic information

  ┌─────────────────────────────────────────────────────┐
  │ 6. FINALIZE BATCH                                   │
  └─────────────────────────────────────────────────────┘

  Update tasks.json:
    - batch.status = "completed"
    - batch.completed_at = current_timestamp
    - batch.duration_seconds = elapsed_time
    - progress.completed_batches += 1
    - progress.completed_tasks = count of all completed tasks
    - progress.percentage = (completed_tasks / total_tasks) * 100

  Save tasks.json to disk

  ┌─────────────────────────────────────────────────────┐
  │ 7. PRINT PROGRESS + EVALUATE TURN BUDGET            │
  └─────────────────────────────────────────────────────┘

  Evaluate turn budget (see agent definition — Turn Budget Management):
    - Estimate turns consumed vs turns remaining
    - If approaching limit: execute Graceful Save Protocol and STOP
    - Otherwise: continue to progress reporting

  Calculate and print progress:

  "[Step {step_number}/5] {step_name} - Batch {batch_number}/{total_batches} completed ✓
   Tasks: {task_range} ({completed_in_batch}/{total_in_batch} passed)
   {step_specific_metrics}
   Progress: {completed_tasks}/{total_tasks} tasks ({percentage}%)
   Time: {elapsed_time} elapsed, ~{estimated_remaining} remaining
   Next: {next_batch_or_step}"

  Step-specific metrics examples:
    - Tests: "Tests: 10 RED verified"
    - Core: "Tests: 27 passing, 0 regressions"
    - Integration: "Integration tests: 5 passing"

  Language context (if applicable):
    Add: "Language: Java (Spring Boot)" or "Language: Python (FastAPI)"

  Example output:
    "[Step 3/5] Core - Batch 2/4 completed ✓
     Tasks: T024-T028 (5/5 passed)
     Tests: 27 passing, 0 regressions
     Language: Java (Spring Boot)
     Progress: 28/45 tasks (62%)
     Time: 32m elapsed, ~34m remaining
     Next: Core batch 3/4"

  ┌─────────────────────────────────────────────────────┐
  │ 8. CONTINUE TO NEXT BATCH (NO PAUSE)                │
  └─────────────────────────────────────────────────────┘

  Do NOT:
    - Ask user for confirmation
    - Wait for user input
    - Present options
    - Stop for approval

  Do:
    - Immediately proceed to next batch in sequence
    - Continue autonomous execution
    - Only halt on failures

END FOR
```

## Step-Specific Customization Points

Each step customizes these parts of the template:

### 1. Task Execution Logic (Step 4a)

**Setup Step:**

- Create directory structure per language conventions
- Generate build files (pom.xml, pyproject.toml, package.json)
- Create configuration files
- Initialize project foundation

**Tests Step:**

- Write unit test files using language test framework
- Write integration test stubs
- Write BDD feature files
- Run each test to verify RED (must fail)

**Core Step:**

- Run tests to verify RED
- Implement production code using TDD loop
- Apply language-specific patterns (layers, DI, etc.)
- Run tests to verify GREEN (must pass)

**Integration Step:**

- Wire components together (DI, routing, modules)
- Write integration tests
- Run integration tests

**Polish Step:**

- Add error handling
- Add structured logging
- Add documentation
- Run full test suite to ensure no regressions

### 2. Checkpoint Verification (Step 5)

**Setup Step:**

- Verify directory structure exists and matches language conventions
- Validate build config files (XML, TOML, JSON)
- Verify test runner can be invoked

**Tests Step:**

- Run all tests written in batch
- Verify ALL tests FAIL (RED state - no implementation exists)
- Count tests written and verified RED

**Core Step:**

- Run all tests (current batch + previous batches)
- Verify ALL tests PASS (GREEN state)
- Check for regressions (previously passing tests still pass)
- Count passing tests

**Integration Step:**

- Run integration tests
- Verify all integration tests PASS
- Verify unit tests still pass (no regressions)

**Polish Step:**

- Run full test suite (unit + integration + BDD)
- Verify all tests still PASS
- Verify no behavioral changes

### 3. Progress Metrics (Step 7)

**Setup Step:**

```text
Tasks: T001-T003 (3/3 passed)
Checkpoint: Structure validated ✓
```

**Tests Step:**

```text
Tasks: T004-T013 (10/10 passed)
Tests: 10 RED verified
Checkpoint: All tests fail as expected ✓
```

**Core Step:**

```text
Tasks: T024-T028 (5/5 passed)
Tests: 27 passing, 0 regressions
Checkpoint: All implementations complete ✓
```

**Integration Step:**

```text
Tasks: T039-T041 (3/3 passed)
Integration tests: 5 passing
Unit tests: 27 passing, 0 regressions
```

**Polish Step:**

```text
Tasks: T044-T045 (2/2 passed)
Full test suite: 67 tests passing
Code quality: All checks passed ✓
```

## Language-Specific Behavior

When `batch.language_context` exists:

### Reference Loading (Step 2)

The template automatically loads language-specific references based on the step.

See `language-skill-integration.md` for complete step-to-reference mappings:

- Java: Which java-codegen references to load per step
- Python: Which python-codegen references to load per step

### Pattern Application (Step 4a)

Use loaded language references to apply:

- **File naming**: From language_context.conventions.naming
- **Directory structure**: From language_context.conventions.directory_layout
- **Code templates**: From language_context.templates
- **Test framework**: From language_context.test_framework
- **Code patterns**: From loaded skill references (e.g., Spring Boot patterns, FastAPI patterns)

### Test Execution (Steps 4b, 5)

Use language-specific test command:

- Java: `mvn test` or `gradle test`
- Python: `pytest tests/ -v`
- From: `language_context.test_command`

## State Management

The template ensures consistent state updates:

### Before Batch

```json
{
  "batch": {
    "status": "not_started"
  }
}
```

### During Batch

```json
{
  "batch": {
    "status": "in_progress",
    "started_at": "2026-04-10T10:00:00Z",
    "completed_tasks": ["T001", "T002"],
    "current_task": "T003"
  }
}
```

### After Batch

```json
{
  "batch": {
    "status": "completed",
    "started_at": "2026-04-10T10:00:00Z",
    "completed_at": "2026-04-10T10:05:30Z",
    "duration_seconds": 330,
    "checkpoint": {
      "verification_type": "red",
      "verification_passed": true,
      "tests_written": 10
    }
  }
}
```

## Error Handling

The template handles failures consistently:

### Task Failure

```text
Task T027 failed after 3 retry attempts
→ Update task.status = "failed"
→ Update batch.status = "failed"
→ Add to errors array
→ Save state
→ HALT
→ Print resume instructions
```

### Checkpoint Failure

```text
Batch checkpoint failed (regression detected)
→ Update batch.status = "failed"
→ Update checkpoint.verification_passed = false
→ Add diagnostic info to errors array
→ Save state
→ HALT
→ Print diagnostic information
```

## Usage in Step Files

Step-specific files reference this template:

**Example from step-3-setup.md:**

```markdown
# Step 3 — Setup

Execute Setup batch using the standard batch execution template.

See `batch-execution-template.md` for the complete loop structure.

## Step-Specific: Task Execution

[Only Setup-specific logic]

## Step-Specific: Checkpoint Verification

[Only Setup-specific checkpoint logic]
```

This eliminates duplication and ensures consistency across all steps.

## Sub-Agent Execution Mode

The standard batch execution loop above describes the **internal logic** of batch execution. In practice, the main `code-generation-agent` delegates
each batch to a `code-generation-batch-agent` sub-agent rather than executing the loop directly.

### How It Works

The main agent acts as **orchestrator**:

1. Builds a self-contained prompt with all batch context (tasks, references, spec paths)
2. Spawns `code-generation-batch-agent` with that prompt
3. Sub-agent executes the full loop above (steps 1-8) within its own turn budget
4. Sub-agent updates tasks.json/tasks.md directly on disk
5. Sub-agent returns structured result (BATCH COMPLETE or BATCH FAILED)
6. Orchestrator reads tasks.json to verify, prints progress, continues

### Benefits

- **Fresh turn budget per batch**: Each sub-agent gets 50 turns, vs main agent burning through 250 total
- **Clean context window**: No accumulated state from previous batches
- **Isolation**: A sub-agent crash doesn't lose orchestrator state
- **Scalable**: Can handle any number of batches regardless of total task count

### What the Sub-Agent Receives

See `code-generation-batch-agent.md` for the full input/output contract. Key elements:

- Feature name + output directory
- Step name + batch ID
- Task list with acceptance criteria
- Language context (references to load, conventions, test command)
- Spec artifact paths
- Current test state

### What the Sub-Agent Does NOT Receive

- Previous batch context or history (clean slate)
- Main agent's accumulated conversation
- Other batches' task details

This means the sub-agent prompt must be **self-contained** — the orchestrator assembles all needed context before spawning.
