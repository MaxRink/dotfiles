# Environment Validation Checks

This reference defines environment prerequisite checks for each supported language/framework.

## Purpose

Before generating code, validate that the target runtime environment is properly configured.
This prevents generating code that cannot be compiled, tested, or run.

## When to Execute

Run environment validation **after** detecting the target stack from `technical-plan.md` but **before** generating the task list.

```text
Execution Order:
  Step 0a: Parse Arguments & Resolve Output Directory
  Step 0b: Load Prerequisites (technical-plan.md)
  Step 0c: Detect Target Stack
→ Step 0d: Validate Environment ← YOU ARE HERE
  Step 1: Generate Task List
  ...
```

## Validation Strategy

For each target language:

1. Check runtime is installed and in PATH
2. Verify version meets minimum requirements
3. Check build tools are available
4. Verify package manager is installed
5. Validate any required environment variables

## Language Detection

### From technical-plan.md

Extract from `technical-plan.md` § Architecture Overview → Technology Stack:

```markdown
## Architecture Overview

### Technology Stack

**Language**: Java 17
**Framework**: Spring Boot 3.2.0
**Build Tool**: Maven 3.9+
**Testing**: JUnit 5, Mockito
```

### From plan.json

If available, read from `plan.json`:

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

### Detection Logic

```text
1. Read technical-plan.md
2. Search for § Architecture Overview → Technology Stack
3. Extract "Language:" field → map to check script
4. If not found, read plan.json → target_stack.languages[0]
5. If still not found, HALT with error "Cannot detect target language"
```

### Language Mapping

| Detected Language | Check Script | Frameworks Checked |
|-------------------|--------------|-------------------|
| Java, java | `environment-check-java.sh` | Spring Boot |
| Python, python | `environment-check-python.sh` | FastAPI, Django, Flask |

## Check Script Execution

### How to Run

```text
1. Detect target language → language_key
2. Map language_key to check script filename
3. Read check script from references/
4. Execute via Bash tool
5. Capture exit code and output
6. Parse results
```

### Exit Codes

- **0**: All checks passed
- **1**: Critical failure (missing runtime, wrong version)
- **2**: Warning (optional tool missing)

### Example Execution

```bash
# Via Bash tool
cd skills/code-generation/references
bash environment-check-java.sh
```

## Check Results Handling

### Success (Exit Code 0)

```text
✓ Environment Validation Passed

Target Stack:
  Language: Java 17
  Framework: Spring Boot 3.2
  Build Tool: Maven 3.9.5

Environment:
  ✓ Java Runtime: OpenJDK 17.0.9
  ✓ Java Compiler: javac 17.0.9
  ✓ JAVA_HOME: /usr/lib/jvm/java-17-openjdk
  ✓ Maven: 3.9.5

Proceeding with code generation...
```

**Action**: Continue to Step 1 (Generate Task List)

### Failure (Exit Code 1)

```text
✗ Environment Validation Failed

Target Language: Java
Missing: Java Development Kit (JDK)

Current Status:
  ✓ Java Runtime (JRE) detected: Java 11.0.18
  ✗ Java Compiler (javac) not found
  ✗ JAVA_HOME not set

Required Actions:
  1. Install JDK (not just JRE):
     • Download from: https://adoptium.net/
     • Or use SDKMAN: sdk install java 21-tem

  2. Set JAVA_HOME environment variable:
     • Add to ~/.bashrc or ~/.zshrc:
       export JAVA_HOME=/path/to/jdk
       export PATH=$JAVA_HOME/bin:$PATH

  3. Verify installation:
     java -version
     javac -version
     echo $JAVA_HOME

After fixing the environment, re-run:
  /code-generation payment-processing
```

**Action**: HALT execution with error message

### Warning (Exit Code 2)

```text
⚠ Environment Validation Passed with Warnings

Target Stack:
  Language: Python 3.11
  Framework: FastAPI

Environment:
  ✓ Python 3.11.5 detected
  ✓ pip 23.2.1 available
  ✓ venv module available
  ⚠ uv not found (recommended for faster dependency management)

Optional: Install uv for better performance:
  curl -LsSf https://astral.sh/uv/install.sh | sh

Proceeding with code generation...
```

**Action**: Print warning, then continue to Step 1

## Multi-Language Projects

For polyglot projects (e.g., Java backend + React frontend):

```text
Detected Languages:
  1. Java (backend)
  2. TypeScript (frontend)

Running validations:
  [1/2] Java environment... ✓
  [2/2] Node.js environment... ✓

All environments validated successfully.
```

**Logic**:

1. Parse all languages from technical-plan.md
2. Run check script for each language
3. All must pass (exit code 0 or 2)
4. If any returns exit code 1: HALT

## Skipping Validation (Advanced)

For CI/CD environments where validation is guaranteed:

```bash
/code-generation payment-processing --skip-env-check
```

**Warning**: Only use this in controlled environments. Skipping validation may result in code generation failures.

## Language-Specific Details

### Java

See `environment-check-java.sh` for implementation.

**Checks**:

- Java runtime (JRE) version ≥ 11
- Java compiler (JDK) installed
- JAVA_HOME environment variable set
- Maven ≥ 3.6 OR Gradle ≥ 7.0

**Optional**:

- Spring Boot CLI (for Spring projects)

### Python

See `environment-check-python.sh` for implementation.

**Checks**:

- Python runtime version ≥ 3.9
- pip package manager
- venv module available
- uv (recommended) or poetry

**Optional**:

- uvicorn (for FastAPI projects)
- Alembic (for SQLAlchemy projects)

## Error Message Templates

### Missing Runtime

```text
✗ <Language> runtime not found in PATH

Install <Language>:
  • Official site: <URL>
  • Package manager: <command>
  • Version manager: <tool>

Verify installation:
  <language-command> --version
```

### Wrong Version

```text
✗ <Language> version too old

Current: <current-version>
Required: <minimum-version>+

Upgrade options:
  • Download latest: <URL>
  • Use version manager: <command>
```

### Missing Build Tool

```text
✗ Build tool not found: <tool>

Install <tool>:
  • Official guide: <URL>
  • Quick install: <command>

Verify installation:
  <tool> --version
```

### Missing Environment Variable

```text
✗ Environment variable not set: <VAR_NAME>

Set <VAR_NAME>:
  • Add to shell profile (~/.bashrc or ~/.zshrc):
    export <VAR_NAME>=<value>

  • Reload shell:
    source ~/.bashrc

Verify:
  echo $<VAR_NAME>
```

## Implementation in Workflow

See `skills/code-generation/SKILL.md` for integration:

```markdown
### Step 0d — Validate Environment

1. Load this reference file
2. Detect target language from technical-plan.md
3. Select appropriate check script
4. Execute check script via Bash tool
5. Parse exit code and output
6. If exit code 1: HALT with error
7. If exit code 0 or 2: Continue to Step 1
```

## Testing Check Scripts

You can test check scripts independently:

```bash
# Test Java checks
cd skills/code-generation/references
bash environment-check-java.sh

# Test Python checks
bash environment-check-python.sh

# Test all checks
for script in environment-check-*.sh; do
  echo "Testing $script..."
  bash "$script"
  echo ""
done
```
