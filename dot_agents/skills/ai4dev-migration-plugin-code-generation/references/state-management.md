# State Management Specification

This reference defines the state tracking and persistence mechanism for code generation.

## Purpose

Maintain complete execution state to enable:

- Progress tracking and reporting
- Resume after failures
- Audit trail of execution
- Time estimation and metrics

## State File Location

```text
<output-dir>/tasks.json
```

Example:

```text
.migration/payment-processing/code-generation/tasks.json
```

## Schema Definition

### Complete Schema

```json
{
  "schema_version": "2.0",
  "metadata": {
    "feature": "payment-processing",
    "output_dir": "/absolute/path/to/output",
    "output_dir_source": "command-line argument | user input | environment variable | default",
    "created_at": "2026-04-10T10:00:00Z",
    "updated_at": "2026-04-10T10:30:15Z",
    "created_by": "code-generation-agent"
  },
  "config": {
    "batch_strategy": "auto",
    "time_box_minutes": 5,
    "user_overrides": {
      "batch_size": null,
      "skip_env_check": false
    },
    "batch_sizes": {
      "setup": 3,
      "tests": 10,
      "core": 5,
      "integration": 3,
      "polish": 5
    },
    "target_stack": {
      "language": "java",
      "version": "17",
      "frameworks": ["spring-boot"],
      "build_tools": ["maven"]
    },
    "language_skill": {
      "name": "java-codegen",
      "loaded_references": [
        "fundamentals.md",
        "springboot-core.md",
        "testing.md",
        "build-tools.md",
        "jpa-patterns.md",
        "coding-standards.md"
      ]
    }
  },
  "execution": {
    "status": "in_progress | completed | failed",
    "current_step": "core",
    "current_batch": 2,
    "current_task": "T028",
    "started_at": "2026-04-10T10:00:00Z",
    "last_checkpoint": "2026-04-10T10:15:30Z",
    "completed_at": null,
    "estimated_completion": "2026-04-10T11:06:00Z"
  },
  "progress": {
    "total_tasks": 45,
    "completed_tasks": 23,
    "failed_tasks": 0,
    "skipped_tasks": 0,
    "percentage": 51,
    "total_batches": 10,
    "completed_batches": 6,
    "failed_batches": 0,
    "tests": {
      "total_tests_written": 15,
      "total_tests_passing": 27,
      "last_test_run": "2026-04-10T10:15:25Z"
    }
  },
  "steps": [
    {
      "name": "setup",
      "status": "completed",
      "task_count": 3,
      "batch_count": 1,
      "started_at": "2026-04-10T10:00:00Z",
      "completed_at": "2026-04-10T10:01:30Z",
      "duration_seconds": 90
    },
    {
      "name": "tests",
      "status": "completed",
      "task_count": 15,
      "batch_count": 2,
      "started_at": "2026-04-10T10:01:30Z",
      "completed_at": "2026-04-10T10:09:45Z",
      "duration_seconds": 495
    },
    {
      "name": "core",
      "status": "in_progress",
      "task_count": 20,
      "batch_count": 4,
      "current_batch": 2,
      "started_at": "2026-04-10T10:09:45Z",
      "completed_at": null
    },
    {
      "name": "integration",
      "status": "not_started",
      "task_count": 5,
      "batch_count": 2
    },
    {
      "name": "polish",
      "status": "not_started",
      "task_count": 2,
      "batch_count": 1
    }
  ],
  "batches": [
    {
      "id": "B001",
      "step": "setup",
      "batch_number": 1,
      "total_batches": 1,
      "tasks": ["T001", "T002", "T003"],
      "status": "completed",
      "started_at": "2026-04-10T10:00:00Z",
      "completed_at": "2026-04-10T10:01:30Z",
      "duration_seconds": 90,
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
          "package_structure": "com.example.payment/controller/service/repository/model/dto",
          "naming": {
            "classes": "PascalCase",
            "methods": "camelCase",
            "constants": "UPPER_SNAKE_CASE"
          }
        },
        "test_command": "mvn test"
      },
      "db_context": {
        "skill": "db-codegen",
        "db_type": "postgresql",
        "references": ["postgresql-patterns.md", "schema-design-rules.md", "migration-patterns.md"],
        "migration_framework": "flyway",
        "migration_path": "src/main/resources/db/migration/"
      },
      "checkpoint": {
        "verification_type": "structure",
        "verification_passed": true,
        "notes": "Directory structure and configs validated"
      }
    },
    {
      "id": "B002",
      "step": "tests",
      "batch_number": 1,
      "total_batches": 2,
      "tasks": ["T004", "T005", "T006", "T007", "T008", "T009", "T010", "T011", "T012", "T013"],
      "status": "completed",
      "started_at": "2026-04-10T10:01:30Z",
      "completed_at": "2026-04-10T10:06:15Z",
      "duration_seconds": 285,
      "language_context": {
        "skill": "java-codegen",
        "references": ["testing.md", "fundamentals.md"],
        "test_framework": "JUnit 5 + Mockito + AssertJ",
        "conventions": {
          "naming": {
            "test_classes": "*Test for unit, *IT for integration",
            "test_methods": "should{Behavior}_when{Condition}"
          }
        },
        "test_command": "mvn test"
      },
      "checkpoint": {
        "verification_type": "red",
        "tests_written": 10,
        "tests_verified_red": 10,
        "verification_passed": true,
        "notes": "All tests fail as expected (no implementation)"
      }
    },
    {
      "id": "B007",
      "step": "core",
      "batch_number": 2,
      "total_batches": 4,
      "tasks": ["T024", "T025", "T026", "T027", "T028"],
      "status": "in_progress",
      "started_at": "2026-04-10T10:14:00Z",
      "completed_at": null,
      "completed_tasks": ["T024", "T025", "T026", "T027"],
      "current_task": "T028",
      "language_context": {
        "skill": "java-codegen",
        "references": ["fundamentals.md", "springboot-core.md", "jpa-patterns.md", "coding-standards.md"],
        "layer_pattern": "Controller → Service → Repository",
        "conventions": {
          "annotations": ["@RestController", "@Service", "@Repository", "@Transactional"]
        },
        "test_command": "mvn test"
      },
      "checkpoint": null
    }
  ],
  "tasks": [
    {
      "id": "T001",
      "title": "Create directory structure",
      "step": "setup",
      "batch_id": "B001",
      "dependencies": [],
      "status": "passed",
      "attempts": 1,
      "started_at": "2026-04-10T10:00:00Z",
      "completed_at": "2026-04-10T10:00:15Z",
      "duration_seconds": 15,
      "acceptance_criteria": [
        "src/ directory exists",
        "tests/ directory exists",
        "features/ directory exists"
      ],
      "related_br_ids": []
    },
    {
      "id": "T027",
      "title": "Implement PaymentGatewayAdapter",
      "step": "core",
      "batch_id": "B007",
      "dependencies": ["T020", "T021"],
      "status": "passed",
      "attempts": 2,
      "started_at": "2026-04-10T10:17:00Z",
      "completed_at": "2026-04-10T10:19:30Z",
      "duration_seconds": 150,
      "acceptance_criteria": [
        "All unit tests pass",
        "Code implements BR-045, BR-046"
      ],
      "related_br_ids": ["BR-045", "BR-046"],
      "test_results": {
        "total_tests": 2,
        "passing_tests": 2,
        "test_files": ["tests/unit/PaymentGatewayAdapter.test.ts"]
      },
      "retry_history": [
        {
          "attempt": 1,
          "status": "failed",
          "error": "2/2 tests failing - missing validation logic",
          "timestamp": "2026-04-10T10:17:45Z"
        }
      ]
    },
    {
      "id": "T028",
      "title": "Implement InventoryService",
      "step": "core",
      "batch_id": "B007",
      "dependencies": ["T022"],
      "status": "in_progress",
      "attempts": 1,
      "started_at": "2026-04-10T10:19:30Z",
      "completed_at": null,
      "acceptance_criteria": [
        "All unit tests pass",
        "Code implements BR-050, BR-051, BR-052"
      ],
      "related_br_ids": ["BR-050", "BR-051", "BR-052"]
    }
  ],
  "errors": [
    {
      "timestamp": "2026-04-10T10:17:45Z",
      "task_id": "T027",
      "attempt": 1,
      "error_type": "test_failure",
      "message": "2/2 tests failing - missing validation logic",
      "resolution": "Added expiry date validation, retry succeeded"
    }
  ]
}
```

## Update Frequency

### When to Update State

Update `tasks.json` after EVERY significant event:

```text
1. After task generation (Step 2):
   - Write complete tasks array
   - Write batches array
   - Set execution.status = "in_progress"

2. After starting each batch:
   - Update execution.current_batch
   - Update batch.status = "in_progress"
   - Update batch.started_at

3. After completing each task:
   - Update task.status
   - Update task.completed_at
   - Update task.duration_seconds
   - Update batch.completed_tasks array

4. After completing each batch:
   - Update batch.status = "completed"
   - Update batch.completed_at
   - Update batch.duration_seconds
   - Update batch.checkpoint
   - Update progress.completed_batches
   - Update progress.percentage

5. After completing each step:
   - Update step.status = "completed"
   - Update step.completed_at
   - Update step.duration_seconds

6. After fatal failure:
   - Update task.status = "failed"
   - Update batch.status = "failed"
   - Update execution.status = "failed"
   - Add to errors array

7. After successful completion:
   - Update execution.status = "completed"
   - Update execution.completed_at
   - Final metrics update
```

### Update Pattern

```text
AFTER completing each TASK (all file writes + test verification for that task):
  1. Update corresponding task in tasks.json
  2. Update tasks.md progress tracker
  3. Then proceed to next task

Within a single task, write ALL files and run tests BEFORE updating state.
This reduces state update overhead by ~50% while still ensuring tasks.json
reflects reality at task-level granularity.

DO NOT update tasks.json after every individual file write — only after the
task as a whole is complete (passed or failed).
```

## State Transitions

### Execution Status

```text
not_started → in_progress → completed
                    ↓
                 failed
                    ↓
              needs_resume (turn budget exhausted — graceful save)
```

### Task Status

```text
not_started → in_progress → passed
                    ↓
                 failed
                    ↓
               (manual fix)
                    ↓
              in_progress (retry)
```

### Batch Status

```text
not_started → in_progress → completed
                    ↓
                 failed
```

## Resume Logic Implementation

### Load State and Determine Resume Point

```python
def determine_resume_point(tasks_json):
    """
    Analyze tasks.json and find where to resume.
    Returns: (step_name, batch_id, task_id)
    """
    execution = tasks_json['execution']

    # Case 1: Already completed
    if execution['status'] == 'completed':
        return None, None, None  # Nothing to resume

    # Case 2: Failed, in progress, or needs_resume (turn budget exhausted)
    current_step = execution['current_step']
    current_batch = execution['current_batch']
    current_task = execution.get('current_task')

    # Find the batch
    batches = tasks_json['batches']
    batch = next(b for b in batches
                 if b['step'] == current_step
                 and b['batch_number'] == current_batch)

    # Find incomplete tasks in this batch
    batch_tasks = batch['tasks']
    tasks = tasks_json['tasks']

    for task_id in batch_tasks:
        task = next(t for t in tasks if t['id'] == task_id)
        if task['status'] in ['not_started', 'in_progress', 'failed']:
            return current_step, batch['id'], task_id

    # All tasks in current batch done, move to next batch
    next_batch_number = current_batch + 1
    next_batch = next((b for b in batches
                      if b['step'] == current_step
                      and b['batch_number'] == next_batch_number), None)

    if next_batch:
        first_task = next_batch['tasks'][0]
        return current_step, next_batch['id'], first_task

    # Current step complete, move to next step
    steps = tasks_json['steps']
    current_step_idx = next(i for i, s in enumerate(steps)
                           if s['name'] == current_step)
    next_step = steps[current_step_idx + 1]
    next_batch = next(b for b in batches if b['step'] == next_step['name'])

    return next_step['name'], next_batch['id'], next_batch['tasks'][0]
```

## Validation

### Schema Validation

Before writing state, validate structure:

```python
def validate_state(state):
    """Validate state structure before writing."""
    required_keys = ['metadata', 'config', 'execution', 'progress',
                     'steps', 'batches', 'tasks']

    for key in required_keys:
        assert key in state, f"Missing required key: {key}"

    # Validate metadata
    assert 'feature' in state['metadata']
    assert 'output_dir' in state['metadata']

    # Validate tasks
    for task in state['tasks']:
        assert 'id' in task
        assert 'status' in task
        assert task['status'] in ['not_started', 'in_progress', 'passed', 'failed', 'skipped']

    # Validate batches
    for batch in state['batches']:
        assert 'id' in batch
        assert 'step' in batch
        assert 'tasks' in batch

    return True
```

## Concurrency Safety

### File Locking

Use atomic writes to prevent corruption:

```python
def save_state_atomic(state, output_dir):
    """
    Atomically write state to prevent corruption.
    """
    import json
    import tempfile
    import shutil

    tasks_json_path = f"{output_dir}/tasks.json"

    # Write to temporary file first
    with tempfile.NamedTemporaryFile(mode='w', delete=False,
                                    dir=output_dir,
                                    prefix='.tasks.json.tmp') as tmp:
        json.dump(state, tmp, indent=2)
        tmp_path = tmp.name

    # Atomic rename
    shutil.move(tmp_path, tasks_json_path)
```

## Migration from v1.0

If old format detected, migrate:

```python
def migrate_state_v1_to_v2(old_state):
    """Migrate from schema v1.0 to v2.0."""
    new_state = {
        "schema_version": "2.0",
        "metadata": old_state.get('metadata', {}),
        "config": {
            "batch_strategy": "auto",
            "batch_sizes": calculate_batch_sizes(old_state['tasks'])
        },
        "execution": {
            "status": old_state.get('status', 'not_started'),
            "current_step": old_state.get('current_step'),
            # ... map other fields
        },
        # ... continue mapping
    }
    return new_state
```
