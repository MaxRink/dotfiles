# Step 0 — Configuration & Validation

Configuration and validation steps that run before code generation begins.

## Overview

Step 0 consists of 5 sub-steps:

- **0a**: Parse command-line arguments
- **0b**: Resolve output directory (with user prompt if needed)
- **0c**: Load prerequisites (spec artifacts)
- **0d**: Detect target stack (language, frameworks)
- **0e**: Validate development environment

## Step 0a — Parse Arguments & Check Resume

Extract parameters from `$ARGUMENTS`:

```text
Parse:
  - Feature name (required, first positional argument)
  - --output-dir <path> (optional)
  - --resume (optional flag)
  - --batch-size <N> (optional)
  - --skip-env-check (optional flag)
  - --force-restart (optional flag)

Store parsed values in memory for later use
```

### Check Resume Flag

```text
IF --resume flag is set:
  1. Determine output directory:
     - From --output-dir if provided
     - Otherwise: .migration/<feature-name>/code-generation/

  2. Read tasks.json from output directory

  3. Check execution.status:
     - If "completed": Print warning, ask user if they want to restart
     - If "failed" or "in_progress": Proceed with resume

  4. Load resume point:
     - current_step (e.g., "core")
     - current_batch (e.g., 3)
     - current_task (if in middle of batch)

  5. Print resume banner:
     "Resuming from: Step {step}, Batch {batch}, Task {task}"
     "Progress: {completed}/{total} tasks ({percentage}%)"

  6. Skip Steps 0b-0e, Steps 1-2

  7. Jump directly to the resume point in Steps 3-7
     - If resuming within a batch: reset failed task attempts to 0
     - Continue execution from that point

ELSE (--resume NOT set):
  Continue to Step 0b (normal flow)
```

## Step 0b — Resolve Output Directory

Determine where to write generated code using priority order.

### Priority Order

```text
1. Command-line argument (--output-dir) → Use immediately, no prompt
2. User prompt → Ask for directory interactively
3. Environment variable ($CODE_GEN_OUTPUT_DIR) → Use if user input empty
4. Default → .migration/<feature-name>/code-generation/
```

### If --output-dir Provided

```text
1. Extract path from argument
2. Normalize to absolute path
3. Log: "Output directory: <path> (command-line argument)"
4. Skip prompt, continue to Step 0c
```

### If --output-dir NOT Provided

```text
1. Read environment variable:
   Bash: echo $CODE_GEN_OUTPUT_DIR
   Store result as env_dir

2. Determine default for prompt:
   IF env_dir not empty:
     default = env_dir
   ELSE:
     default = ".migration/<feature-name>/code-generation"

3. Prompt user using AskUserQuestion:
   Question: "Output directory for code generation?\n  [default: <default>]\n▸ "

4. Handle response:
   IF user provides path:
     output_dir = user_input
     source = "user input"
   ELSE IF env_dir not empty:
     output_dir = env_dir
     source = "environment variable CODE_GEN_OUTPUT_DIR"
   ELSE:
     output_dir = default
     source = "default"

5. Log decision:
   "Output directory: <output_dir> (<source>)"
```

### Validate and Create Directory

```text
1. Convert to absolute path
2. Create directory if doesn't exist: mkdir -p <output_dir>
3. Verify writable: test -w <output_dir>
4. IF not writable: HALT with error
```

## Step 0c — Verify Prerequisites

Verify prerequisite artifacts exist in .migration/<feature-name>/:

```text
1. Verify files exist:
   - spec-specification/functional-requirements.md (required)
   - spec-specification/technical-plan.md (required)
   - spec-specification/nonfunctional-requirements.md (optional)
   - spec-specification/contracts.md (optional)
   - plan-migration/plan.json (optional)
   - analysis/analysis.json (optional)
   - architect/target-architecture.md (optional)

   IF functional-requirements.md or technical-plan.md missing:
     HALT with error: "Required spec artifacts not found"

2. HOOK: Validate spec artifact quality
   Hook: validate-code-gen-specs.js (PreToolUse hook for code-generation skill)
   Automatic: Runs when Skill tool is invoked with code-generation

   Hook validates:
     - functional-requirements.md has Functional Requirements section
     - functional-requirements.md has FR IDs (FR-001, FR-002, etc.)
     - functional-requirements.md has Traceability Matrix section
     - technical-plan.md has Technology Stack section
     - technical-plan.md has Component Specifications section
     - nonfunctional-requirements.md exists (optional - warns if missing)
     - contracts.md exists (optional - warns if missing)

   Hook behavior:
     - Denies tool use if critical validation fails (missing BR IDs, required sections)
     - Allows with warning if optional sections missing
     - Prints warnings to user but continues workflow

   Configured in: hooks/hooks.json (PreToolUse → Skill matcher)

Do NOT read file contents yet - that happens in Step 1a.
Only verify files are present and accessible.
```

## Step 0d — Detect Target Stack

Read technical-plan.md specifically to extract target stack information.

**Note**: Full content extraction happens in Step 1a. This step only reads the Technology Stack section.

### From technical-plan.md

```text
Read .migration/<feature-name>/spec-specification/technical-plan.md

Parse § Architecture Overview → Technology Stack:

Extract:
  - Language (e.g., "Java 17", "Python 3.11")
  - Frameworks (e.g., ["Spring Boot 3.2", "FastAPI"])
  - Build tools (e.g., ["Maven 3.9+", "uv"])

Example:
  **Language**: Java 17
  **Framework**: Spring Boot 3.2.0
  **Build Tool**: Maven 3.9+

Store:
  target_language = "java"
  target_version = "17"
  frameworks = ["spring-boot"]
  build_tools = ["maven"]
```

### From plan.json (Fallback)

```text
IF technical-plan.md doesn't have clear stack info:
  Read plan.json → target_stack:
    {
      "languages": ["java"],
      "frameworks": ["spring-boot"],
      "build_tools": ["maven"],
      "version": {
        "java": "17",
        "spring_boot": "3.2.0"
      }
    }
```

### Language Mapping

```text
Map detected language to skill name:
  java, Java → java-codegen
  python, Python → python-codegen

Unsupported languages will be rejected by validation hook.
```

### Validate Target Stack

```text
HOOK: Validate target stack is approved/supported
Hook: validate-code-gen-stack.js (PreToolUse hook for code-generation skill)
Automatic: Runs when Skill tool is invoked with code-generation

Hook validates:
  - Language version meets minimum requirements
    • Java: minimum 17
    • Python: minimum 3.9
  - Frameworks are approved/supported
    • Java: Spring Boot (approved), Quarkus (allowed)
    • Python: FastAPI (approved), Django/Flask (allowed)
  - Only Java and Python are supported

Hook behavior:
  - Denies tool use if language version too old or unsupported
  - Allows with warning if non-standard framework or preview language
  - Extracts stack info from technical-plan.md Technology Stack section

Configured in: hooks/hooks.json (PreToolUse → Skill matcher)

Example validations:
  Java 17 + Spring Boot → Approved (continues)
  Java 11 + Spring Boot → Denied (Java 11 too old, minimum 17)
  Python 3.11 + FastAPI → Approved (continues)
  Python 3.8 + FastAPI → Denied (Python 3.8 too old, minimum 3.9)
  Python 3.11 + Django → Allowed with warning (non-standard framework)
```

## Step 0e — Validate Environment

Validate development environment before code generation.

### If --skip-env-check Flag

```text
Print warning:
  "⚠ Skipping environment validation (--skip-env-check flag)"
  "This may result in failures if environment is not configured."

Skip to Step 1
```

### Otherwise Run Validation

**Note**: Environment checks use built-in shell scripts (not hooks) for direct execution.

```text
1. Map target_language to check script:
   java → environment-check-java.sh
   python → environment-check-python.sh

   Note: Only Java and Python are supported. Other languages will be
   rejected by the validation hook in Step 0d.

2. Execute environment check:
   cd skills/code-generation/references
   bash environment-check-<language>.sh

3. Capture exit code and output

4. Handle results:

   EXIT CODE 0 (Success):
     Parse and print validation summary
     Continue to Step 1

   EXIT CODE 1 (Critical Failure):
     Print error output (includes installation instructions)
     HALT with error message:
       "✗ Environment validation failed. Fix issues and re-run."
     DO NOT proceed to Step 1

   EXIT CODE 2 (Success with Warnings):
     Print validation summary with warnings
     Continue to Step 1

7. For multi-language projects:
   Run checks for ALL detected languages
   All must pass (exit 0 or 2)
   If ANY returns exit 1: HALT
```

### Example Output (Success)

```text
[Step 0e] Environment Validation

Detected Stack:
  Language: Java 17
  Framework: Spring Boot 3.2
  Build Tool: Maven

Running checks...
  ✓ Java 17.0.9 detected
  ✓ javac 17.0.9 available
  ✓ JAVA_HOME: /usr/lib/jvm/java-17-openjdk
  ✓ Maven 3.9.5 available

✓ Environment validated successfully

Proceeding to code generation...
```

### Example Output (Failure)

```text
[Step 0e] Environment Validation

Detected Stack:
  Language: Python 3.11
  Framework: FastAPI

Running checks...
  ✗ Python 3.8 detected (minimum: 3.9+)
  ✓ pip 23.0 available
  ✗ uv not found

✗ Environment validation failed

Issues:
  1. Python too old (3.8, need 3.9+)
     Install: https://python.org/downloads/

  2. uv not found
     Install: curl -LsSf https://astral.sh/uv/install.sh | sh

Fix these issues and re-run:
  /code-generation <feature-name>
```

## Continue to Step 1

After all Step 0 sub-steps complete successfully, proceed to Step 1 — Load Context & Language Skills.
