# Step 2 — Generate Task List with Batching

Generate ordered task list covering all 5 steps (Setup, Tests, Core, Integration, Polish) with language-aware batch enrichment.

## Overview

This step:

1. Generates tasks from spec artifacts
2. Calculates batches with language-specific time estimates
3. Enriches batches with language context
4. Writes tasks.json with complete state schema
5. Prints execution plan

## Load References

```text
Read references/task-schema.json
Read references/task-template.md
Read references/step-workflow.md
Read references/batch-strategy.md
Read references/state-management.md
Read references/language-skill-integration.md
```

## Generate Tasks

Parse loaded specs to produce ordered task list.

### Task Generation Per Step

See `step-workflow.md` for detailed per-step task generation criteria.

**For each task, define:**

- `id`: T001, T002, T003, ...
- `title`: Human-readable task description
- `step`: setup | tests | core | integration | polish
- `dependencies`: Array of task IDs that must complete first
- `acceptance_criteria`: Array of criteria for task completion
- `related_fr_ids`: Array of Functional Requirement IDs (FR-001, FR-002) — NEW STRUCTURE
- `related_uc_ids`: Array of Use Case IDs (UC-001, UC-002) — NEW STRUCTURE
- `related_br_ids`: Array of Business Requirement IDs (BR-001, BR-002) — traced via FR IDs or direct (old structure)

### Example Tasks

**New Structure (with FR IDs, UC IDs):**

```json
[
  {
    "id": "T001",
    "title": "Create directory structure",
    "step": "setup",
    "dependencies": [],
    "acceptance_criteria": [
      "src/ directory exists",
      "tests/ directory exists"
    ],
    "related_fr_ids": [],
    "related_uc_ids": [],
    "related_br_ids": []
  },
  {
    "id": "T004",
    "title": "Write UserService tests",
    "step": "tests",
    "dependencies": ["T001", "T002", "T003"],
    "acceptance_criteria": [
      "Test file created",
      "All tests verified RED"
    ],
    "related_fr_ids": ["FR-001", "FR-002"],
    "related_uc_ids": ["UC-001"],
    "related_br_ids": ["BR-001", "BR-002"]
  }
]
```

**Old Structure (BR IDs only, deprecated but supported):**

```json
[
  {
    "id": "T001",
    "title": "Create directory structure",
    "step": "setup",
    "dependencies": [],
    "acceptance_criteria": [
      "src/ directory exists",
      "tests/ directory exists"
    ],
    "related_br_ids": []
  },
  {
    "id": "T004",
    "title": "Write UserService tests",
    "step": "tests",
    "dependencies": ["T001", "T002", "T003"],
    "acceptance_criteria": [
      "Test file created",
      "All tests verified RED"
    ],
    "related_br_ids": ["BR-001", "BR-002"]
  }
]
```

**Note:** When using old structure, `related_fr_ids` and `related_uc_ids` are omitted from tasks.

## Calculate Batches with Language Context

After generating all tasks, organize into batches with language enrichment.

### Step 1: Group Tasks by Step

```text
setup_tasks = [T001, T002, T003]
tests_tasks = [T004, T005, ..., T018]
core_tasks = [T019, T020, ..., T038]
integration_tasks = [T039, T040, ..., T043]
polish_tasks = [T044, T045]
```

### Database Schema Tasks (Conditional)

When `contracts.md` section 3 or `technical-plan.md` section 4 contains database contracts, add DB setup tasks to the Setup step:

```json
[
  {
    "id": "T-DB-001",
    "title": "Generate ERD diagram (database/docs/ERD.md)",
    "step": "setup",
    "dependencies": ["T001"],
    "acceptance_criteria": [
      "ERD.md exists with Mermaid erDiagram block",
      "All entities from spec artifacts included",
      "Relationships show correct cardinality",
      "PK, FK, UK markers present"
    ],
    "related_fr_ids": [],
    "related_uc_ids": [],
    "related_br_ids": []
  },
  {
    "id": "T-DB-002",
    "title": "Generate schema DDL (database/schema.sql)",
    "step": "setup",
    "dependencies": ["T-DB-001"],
    "acceptance_criteria": [
      "schema.sql contains valid DDL for target DB type",
      "All tables from ERD are present",
      "Constraints, indexes, triggers included"
    ],
    "related_fr_ids": [],
    "related_uc_ids": [],
    "related_br_ids": []
  },
  {
    "id": "T-DB-003",
    "title": "Generate migration scripts (database/migrations/ + framework path)",
    "step": "setup",
    "dependencies": ["T-DB-002"],
    "acceptance_criteria": [
      "Migration scripts are transactional (BEGIN/COMMIT)",
      "Both UP and DOWN migrations exist",
      "Framework-specific migration in correct path"
    ],
    "related_fr_ids": [],
    "related_uc_ids": [],
    "related_br_ids": []
  },
  {
    "id": "T-DB-004",
    "title": "Generate seed data (database/seeds/sample_data.sql)",
    "step": "setup",
    "dependencies": ["T-DB-002"],
    "acceptance_criteria": [
      "5-10 rows per table with realistic data",
      "FK references are valid",
      "Idempotent (ON CONFLICT DO NOTHING)"
    ],
    "related_fr_ids": [],
    "related_uc_ids": [],
    "related_br_ids": []
  },
  {
    "id": "T-DB-005",
    "title": "Generate schema documentation (database/docs/SCHEMA.md)",
    "step": "setup",
    "dependencies": ["T-DB-002"],
    "acceptance_criteria": [
      "Table-by-table documentation",
      "Index strategy explained",
      "Design decisions documented"
    ],
    "related_fr_ids": [],
    "related_uc_ids": [],
    "related_br_ids": []
  }
]
```

DB task IDs use the normal sequence (T004, T005, ...) — the `T-DB-NNN` prefix above is for illustration only. These tasks are appended to the Setup step task list.

**If no database contracts are detected**, these tasks are NOT generated and the Setup step contains only the standard project foundation tasks.

### Step 2: Calculate Batch Sizes

Use language-aware batch size calculation from `batch-strategy.md`:

```python
def calculate_batch_size(step_name, task_count, language):
    # Language-specific time estimates
    time_estimates = {
        "java": {"setup": 0.5, "tests": 0.7, "core": 2.5, ...},
        "python": {"setup": 0.3, "tests": 0.4, "core": 1.8, ...},
        "generic": {"setup": 0.3, "tests": 0.5, "core": 2.0, ...}
    }

    time_per_task = time_estimates[language][step_name]
    batch_size = int(5_MINUTES / time_per_task)  # 5-min time-box
    batch_size = min(batch_size, max_batch_sizes[step_name])

    return batch_size
```

**Example for Java (45 tasks):**

```text
Step          Tasks  Time/Task  Batch Size  Batches
──────────────────────────────────────────────────────
Setup            3     0.5 min      3 (all)       1
Tests           15     0.7 min          7         3
Core            20     2.5 min          2        10
Integration      5     3.5 min          1         5
Polish           2     1.2 min          2         1
──────────────────────────────────────────────────────
Total           45                              20
```

**Example for Python (45 tasks):**

```text
Step          Tasks  Time/Task  Batch Size  Batches
──────────────────────────────────────────────────────
Setup            3     0.3 min      3 (all)       1
Tests           15     0.4 min         12         2
Core            20     1.8 min          2        10
Integration      5     2.5 min          2         3
Polish           2     0.8 min          2         1
──────────────────────────────────────────────────────
Total           45                              17
```

User can override with `--batch-size <N>` flag.

### Step 3: Enrich Batches with Language Context

For each batch, add language-specific context from `language-skill-integration.md`:

```text
FOR each step (setup, tests, core, integration, polish):
  FOR each batch in step:
    1. Determine which language skill references apply
       (Use step-to-reference mapping from language-skill-integration.md)

    2. Add language_context to batch:
       {
         "skill": "java-codegen",
         "references": [...],  // Step-specific references
         "templates": {...},   // Language-specific templates
         "conventions": {...}, // Naming, structure conventions
         "test_framework": "...", // Test framework to use
         "test_command": "..." // Command to run tests
       }
```

**Example: Java Setup Batch**

```json
{
  "id": "B001",
  "step": "setup",
  "batch_number": 1,
  "total_batches": 1,
  "tasks": ["T001", "T002", "T003"],
  "status": "not_started",
  "language_context": {
    "skill": "java-codegen",
    "references": [
      "build-tools.md",
      "springboot-core.md",
      "coding-standards.md"
    ],
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
        "constants": "UPPER_SNAKE_CASE"
      }
    },
    "test_command": "mvn test"
  }
}
```

**Example: Python Tests Batch**

```json
{
  "id": "B002",
  "step": "tests",
  "batch_number": 1,
  "total_batches": 2,
  "tasks": ["T004", ..., "T015"],
  "status": "not_started",
  "language_context": {
    "skill": "python-codegen",
    "references": [
      "testing.md",
      "fastapi-core.md"
    ],
    "test_framework": "pytest + FastAPI TestClient",
    "conventions": {
      "naming": {
        "test_files": "test_*.py",
        "test_functions": "test_should_{behavior}_when_{condition}"
      }
    },
    "test_command": "pytest tests/ -v"
  }
}
```

### Step 4: Assign Batch IDs to Tasks

```text
FOR each task:
  Find which batch it belongs to
  Set task.batch_id = batch.id
```

## Write State File

Write complete state to `<output-dir>/tasks.json` per `state-management.md` schema v2.0:

```json
{
  "schema_version": "2.0",
  "metadata": {
    "feature": "<feature-name>",
    "output_dir": "<output-directory>",
    "output_dir_source": "command-line argument | user input | environment variable | default",
    "created_at": "<timestamp>",
    "updated_at": "<timestamp>",
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
      "tests": 7,
      "core": 2,
      "integration": 1,
      "polish": 2
    },
    "target_stack": {
      "language": "java",
      "version": "17",
      "frameworks": ["spring-boot"],
      "build_tools": ["maven"]
    },
    "language_skill": {
      "name": "java-codegen",
      "loaded_references": [...]
    }
  },
  "execution": {
    "status": "in_progress",
    "current_step": "setup",
    "current_batch": 1,
    "current_task": null,
    "started_at": "<timestamp>",
    "last_checkpoint": null,
    "completed_at": null,
    "estimated_completion": "<timestamp>"
  },
  "progress": {
    "total_tasks": 45,
    "completed_tasks": 0,
    "failed_tasks": 0,
    "skipped_tasks": 0,
    "percentage": 0,
    "total_batches": 20,
    "completed_batches": 0,
    "failed_batches": 0,
    "tests": {
      "total_tests_written": 0,
      "total_tests_passing": 0,
      "last_test_run": null
    }
  },
  "steps": [
    {
      "name": "setup",
      "status": "not_started",
      "task_count": 3,
      "batch_count": 1
    },
    // ... other steps
  ],
  "batches": [
    // ... all batches with language_context
  ],
  "tasks": [
    // ... all tasks with batch_id
  ],
  "errors": []
}
```

Also write `<output-dir>/tasks.md` per `task-template.md`.

## Print Task Summary

Print execution plan to user:

```text
Code Generation Plan:
  Feature: <feature-name>
  Output: <output-directory>
  Language: Java (Spring Boot 3.2, Maven)
  Total tasks: 45 across 5 steps
  Total batches: 20
  Estimated time: ~83 minutes

Batch breakdown:
  Setup: 1 batch, 3 tasks (~2 min)
  Tests: 3 batches, 15 tasks (~11 min)
  Core: 10 batches, 20 tasks (~50 min)
  Integration: 5 batches, 5 tasks (~18 min)
  Polish: 1 batch, 2 tasks (~2 min)

Starting execution...
```

## Continue to Step 3

**CRITICAL**: Immediately proceed to Step 3 after writing the task list.

**DO NOT:**

- Stop to present the task list to the user
- Ask for confirmation or approval
- Wait for user input
- Present options

**DO:**

- Continue automatically to Step 3 (Setup)
- Begin batch execution immediately
