# Batch Processing Strategy

This reference defines the batch processing approach for code generation to optimize execution time and context management.

## Purpose

Break code generation into manageable batches to ensure:

- No single execution runs too long (target: 5 minutes per batch)
- State is saved frequently (after each batch)
- Progress is visible and resumable
- Context window stays clean

## Batch Configuration

### Time-Box Target

**Target Duration**: 5 minutes per batch

This ensures:

- Regular checkpoints for state saving
- User can see progress every 5 minutes
- Failures are isolated to small batches
- Easy to resume from last checkpoint

### Auto-Calculated Batch Sizes

```python
def calculate_batch_size(step_name, total_tasks, language="generic"):
    """
    Auto-calculate batch size based on estimated time per task.
    Target: Keep each batch under 5 minutes.
    Adjusts estimates based on target language characteristics.
    """
    TIME_BOX_MINUTES = 5

    # Language-specific time estimates per task (in minutes)
    time_estimates_by_language = {
        "java": {
            "setup": 0.5,       # pom.xml, configs (more verbose)
            "tests": 0.7,       # JUnit tests (more boilerplate)
            "core": 2.5,        # Spring components (annotations, layers)
            "integration": 3.5, # Integration tests (more setup)
            "polish": 1.2       # Documentation, logging
        },
        "python": {
            "setup": 0.3,       # pyproject.toml (concise)
            "tests": 0.4,       # pytest (concise, less boilerplate)
            "core": 1.8,        # FastAPI routes (concise)
            "integration": 2.5, # Async tests (moderate complexity)
            "polish": 0.8       # Type hints, ruff (automated)
        },
        "generic": {
            "setup": 0.3,       # 18 seconds per setup task
            "tests": 0.5,       # 30 seconds per test file
            "core": 2.0,        # 2 minutes per implementation (TDD loop)
            "integration": 3.0, # 3 minutes per integration task
            "polish": 1.0       # 1 minute per polish task
        }
    }

    # Get language-specific estimates, fallback to generic
    time_estimates = time_estimates_by_language.get(
        language.lower(),
        time_estimates_by_language["generic"]
    )

    time_per_task = time_estimates.get(step_name, 2.0)
    batch_size = max(1, int(TIME_BOX_MINUTES / time_per_task))

    # Cap batch sizes for context management
    max_batch_sizes = {
        "setup": 99,        # Setup is always small, run all at once
        "tests": 10,        # Max 10 test files per batch
        "core": 5,          # Max 5 implementations per batch
        "integration": 3,   # Max 3 integration tasks per batch
        "polish": 5         # Max 5 polish tasks per batch
    }

    batch_size = min(batch_size, max_batch_sizes.get(step_name, 5))

    # Calculate number of batches
    num_batches = math.ceil(total_tasks / batch_size)

    return {
        "batch_size": batch_size,
        "num_batches": num_batches,
        "estimated_minutes": (total_tasks * time_per_task),
        "estimated_minutes_per_batch": batch_size * time_per_task,
        "language": language
    }
```

### Language-Specific Batch Size Examples

**Java + Spring Boot (45 tasks):**

```text
Step          Tasks  Time/Task  Batch Size  Batches  Est. Time
─────────────────────────────────────────────────────────────────
Setup            3     0.5 min      3 (all)       1      2 min
Tests           15     0.7 min          7         3     11 min
Core            20     2.5 min          2         10    50 min
Integration      5     3.5 min          1         5     18 min
Polish           2     1.2 min          2         1      2 min
─────────────────────────────────────────────────────────────────
Total           45                               20     83 min
```

**Python + FastAPI (45 tasks):**

```text
Step          Tasks  Time/Task  Batch Size  Batches  Est. Time
─────────────────────────────────────────────────────────────────
Setup            3     0.3 min      3 (all)       1      1 min
Tests           15     0.4 min         10         2      6 min
Core            20     1.8 min          2         10    36 min
Integration      5     2.5 min          2         3     13 min
Polish           2     0.8 min          2         1      2 min
─────────────────────────────────────────────────────────────────
Total           45                               17     58 min
```

Note: Python is generally faster due to less boilerplate, more concise syntax, and faster test frameworks.

### Database Schema Task Time Estimates

When DB setup tasks are included (conditional on contracts.md § 3 presence), they add to the Setup step:

```text
DB Task                  Est. Time
──────────────────────────────────
Generate ERD diagram      0.5 min
Generate schema DDL       0.8 min
Generate migrations       0.5 min
Generate seed data        0.3 min
Generate documentation    0.3 min
──────────────────────────────────
Total DB tasks            2.4 min
```

These 5 tasks fit within the Setup batch alongside normal setup tasks (3 tasks ~1-2 min).
Combined total: ~4-5 min, within the 5-min time-box.
If the total exceeds the time-box, the auto-calculator splits Setup into 2 batches (normal setup + DB setup).

### Example Calculation

For a feature with 45 tasks:

```text
Step          Tasks  Batch Size  Batches  Est. Time
─────────────────────────────────────────────────────
Setup            3      3 (all)       1      1 min
Tests           15         10         2      8 min
Core            20          5         4     40 min
Integration      5          3         2     15 min
Polish           2          2         1      2 min
─────────────────────────────────────────────────────
Total           45                   10     66 min
```

## Batch Execution Flow

### Per-Batch Loop

```text
FOR each batch in step:

  1. Print batch header:
     "[Step X/5] <StepName> - Batch Y/Z"

  2. Load batch tasks from tasks.json

  3. FOR each task in batch:
       a. Execute task logic (write files, run tests, etc.)
       b. Update task status immediately:
          - tasks.json: status = "passed" or "failed"
          - tasks.md: mark task complete
       c. If task fails after 3 retries:
          - Mark task as "failed"
          - Mark batch as "failed"
          - Save state
          - HALT (print resume instructions)

  4. After all tasks in batch complete:
     a. Run checkpoint verification
     b. Update batch status to "completed"
     c. Save state to tasks.json
     d. Print progress message

  5. Continue to next batch (no pause)

END FOR
```

### Checkpoint Verification

After each batch completes, run verification:

```text
CHECKPOINT after batch B:

  1. For Tests step:
     - Run all test files written so far
     - Verify they all FAIL (RED) - no implementation exists yet
     - If any test PASSES: flag as vacuous test, needs rewrite

  2. For Core step:
     - Run all tests associated with tasks in this batch
     - Verify they all PASS (GREEN) - implementation correct
     - If any test FAILS: retry loop should have caught this

  3. For Integration step:
     - Run integration tests written in this batch
     - Verify they PASS

  4. For all steps:
     - Run regression check: ensure previous tests still pass
     - Count passing tests
     - Log checkpoint result

  5. If checkpoint FAILS:
     - Mark batch as "failed"
     - Save state
     - HALT with diagnostic message

  6. If checkpoint PASSES:
     - Update progress metrics
     - Continue to next batch
```

## State Management

### Batch Metadata in tasks.json

```json
{
  "metadata": {
    "feature": "payment-processing",
    "output_dir": "/path/to/output",
    "output_dir_source": "command-line argument",
    "created_at": "2026-04-10T10:00:00Z",
    "updated_at": "2026-04-10T10:15:00Z"
  },
  "config": {
    "batch_strategy": "auto",
    "time_box_minutes": 5,
    "batch_sizes": {
      "setup": 3,
      "tests": 10,
      "core": 5,
      "integration": 3,
      "polish": 5
    }
  },
  "execution": {
    "status": "in_progress",
    "current_step": "core",
    "current_batch": 2,
    "started_at": "2026-04-10T10:00:00Z",
    "last_checkpoint": "2026-04-10T10:15:00Z",
    "estimated_completion": "2026-04-10T11:06:00Z"
  },
  "progress": {
    "total_tasks": 45,
    "completed_tasks": 23,
    "failed_tasks": 0,
    "percentage": 51,
    "total_batches": 10,
    "completed_batches": 6
  },
  "batches": [
    {
      "id": "B001",
      "step": "setup",
      "batch_number": 1,
      "tasks": ["T001", "T002", "T003"],
      "status": "completed",
      "started_at": "2026-04-10T10:00:00Z",
      "completed_at": "2026-04-10T10:01:30Z",
      "duration_seconds": 90
    },
    {
      "id": "B002",
      "step": "tests",
      "batch_number": 1,
      "tasks": ["T004", "T005", "T006", "T007", "T008", "T009", "T010", "T011", "T012", "T013"],
      "status": "completed",
      "started_at": "2026-04-10T10:01:30Z",
      "completed_at": "2026-04-10T10:06:15Z",
      "duration_seconds": 285,
      "checkpoint": {
        "tests_written": 10,
        "tests_verified_red": 10,
        "verification_passed": true
      }
    },
    {
      "id": "B007",
      "step": "core",
      "batch_number": 2,
      "tasks": ["T024", "T025", "T026", "T027", "T028"],
      "status": "in_progress",
      "started_at": "2026-04-10T10:14:00Z",
      "completed_tasks": ["T024", "T025", "T026", "T027"],
      "current_task": "T028"
    }
  ],
  "tasks": [
    {
      "id": "T001",
      "title": "Create directory structure",
      "step": "setup",
      "status": "passed",
      "batch_id": "B001"
    }
    // ... more tasks
  ]
}
```

### Task Status Values

- `not_started` - Task not yet executed
- `in_progress` - Task currently being executed
- `passed` - Task completed successfully
- `failed` - Task failed after retries
- `skipped` - Task skipped due to dependency failure

## Progress Reporting

### After Each Batch

Print concise progress update:

```text
[Step 3/5] Core - Batch 2/4 completed ✓
  Tasks: T024-T028 (5/5 passed)
  Tests: 27 passing, 0 regressions
  Progress: 23/45 tasks (51%)
  Time: 2m 15s elapsed, ~3m 45s remaining
  Next: Core batch 3/4
```

### Progress Calculation

```python
def calculate_progress(tasks, batches):
    """Calculate overall progress metrics."""
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t['status'] == 'passed'])
    failed_tasks = len([t for t in tasks if t['status'] == 'failed'])

    completed_batches = len([b for b in batches if b['status'] == 'completed'])
    total_batches = len(batches)

    percentage = int((completed_tasks / total_tasks) * 100)

    # Time estimation
    elapsed_seconds = sum(b.get('duration_seconds', 0)
                         for b in batches
                         if b['status'] == 'completed')

    if completed_batches > 0:
        avg_batch_seconds = elapsed_seconds / completed_batches
        remaining_batches = total_batches - completed_batches
        estimated_remaining_seconds = avg_batch_seconds * remaining_batches
    else:
        estimated_remaining_seconds = 0

    return {
        "percentage": percentage,
        "completed_tasks": completed_tasks,
        "total_tasks": total_tasks,
        "elapsed_minutes": elapsed_seconds // 60,
        "remaining_minutes": estimated_remaining_seconds // 60
    }
```

## Resume Logic

### Automatic Resume Detection

When code generation starts:

```text
IF tasks.json exists AND --force-restart NOT set:

  1. Read tasks.json
  2. Check execution.status:

     IF status == "completed":
       → Print: "Code generation already completed for <feature>"
       → Ask: "Start fresh? (y/n)"
       → If no: EXIT

     IF status == "in_progress" OR "failed":
       → Print: "Resuming from last checkpoint..."
       → Load current_step, current_batch, current_task
       → Skip all completed batches
       → Resume from current_task in current_batch

  3. Continue execution from resume point

ELSE:
  → Start fresh from beginning
```

### Resume Command

```bash
# Explicit resume
/code-generation payment-processing --resume

# Detected automatically if tasks.json exists
/code-generation payment-processing
```

### Resume Example

```text
$ /code-generation payment-processing

Resuming from saved state...
  Feature: payment-processing
  Output: ./src/generated (from previous run)
  Last checkpoint: Core batch 2/4, task T027
  Progress: 23/45 tasks (51%), 6/10 batches completed
  Estimated time remaining: ~25 minutes

Continuing execution...

[Step 3/5] Core - Batch 2/4 (resumed)
  Task T028: Implement InventoryService... ✓ (3 tests passing)
  Checkpoint: 30 tests passing, 0 regressions ✓

[Step 3/5] Core - Batch 3/4
  Task T029: Implement EmailService... ✓ (2 tests passing)
  ...
```

## Failure Handling

### Task Failure

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
  /code-generation:status payment-processing
```

### Batch Checkpoint Failure

```text
[Step 3/5] Core - Batch 2/4
  Task T024: Implement UserService... ✓
  Task T025: Implement PaymentService... ✓
  Task T026: Implement OrderService... ✓
  Task T027: Implement ProductService... ✓
  Task T028: Implement CartService... ✓

Running checkpoint...
  ✗ Regression detected: T020 (PaymentService) now failing
  Previous: 22 tests passing
  Current: 21 tests passing

✗ Batch checkpoint failed - regression introduced

Analysis:
  Recently modified: CartService
  Likely cause: Shared dependency conflict

State saved. Review and fix, then resume.
```

## Large Codebase Optimization

### Module-Based Batching

For projects with >50 tasks, use module-based batching:

```text
Instead of:
  Core Batch 1: [T021-T025] (5 tasks, mixed modules)
  Core Batch 2: [T026-T030] (5 tasks, mixed modules)

Use:
  Core Batch 1: User Module [T021-T024] (4 tasks, same module)
  Core Batch 2: Payment Module [T025-T029] (5 tasks, same module)
  Core Batch 3: Order Module [T030-T034] (5 tasks, same module)

Benefits:
  - Related code stays together in context
  - Fewer cross-module dependencies within batch
  - Easier to reason about failures
```

### Batch Grouping Rules

```text
1. Group by module/domain (highest priority)
2. Respect dependency order within module
3. Keep batch size under max limit
4. Shared/utility code goes in first batch
```

## Performance Metrics

Track and display metrics:

```text
Batch Performance Summary:
  Average batch duration: 4m 30s
  Fastest batch: B001 (Setup) - 1m 30s
  Slowest batch: B007 (Core batch 2) - 8m 45s
  Total test runs: 156
  Total retry attempts: 5
  Success rate: 96.7%
```

## Command-Line Overrides

Allow batch size override:

```bash
# Use smaller batches (more frequent checkpoints)
/code-generation payment-processing --batch-size 3

# Use larger batches (fewer checkpoints, faster if reliable)
/code-generation payment-processing --batch-size 10

# Disable batching (run all tasks in step at once - risky)
/code-generation payment-processing --batch-size 0
```

**Warning**: Large batch sizes risk longer recovery time on failure.
