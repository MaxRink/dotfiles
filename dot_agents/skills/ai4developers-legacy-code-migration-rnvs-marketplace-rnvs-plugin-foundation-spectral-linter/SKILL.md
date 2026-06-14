---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-foundation-spectral-linter
description: Validate OpenAPI specifications against OWASP API Security Top 10 and Deutsche Telekom G-API guidelines using Spectral CLI. Lints single or all specs and generates a structured issue overview report.
allowed-tools: Read, Bash, Write, Glob
user-invocable: true
model: inherit
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/foundation/skills/spectral-linter by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Spectral Linting Skill

## Purpose

Validate OpenAPI specifications against security standards and API design guidelines using the Spectral CLI. Supports
linting a single spec or all specs in a project, with two rulesets available. Generates a structured markdown report of
all findings.

## When to Use

- **Before committing OpenAPI spec changes**: Validate modified specs pass security and design rules
- **During API design reviews**: Check specs against OWASP and G-API standards
- **CI/CD gate validation**: Verify all specs pass before merge
- **Bulk audit**: Lint all OpenAPI specs in a project to get a full compliance overview

## Available Rulesets

| Ruleset             | Description                                                                            | Source                             |
|---------------------|----------------------------------------------------------------------------------------|------------------------------------|
| **OWASP** (default) | OWASP API Security Top 10 (2023 edition), evaluated by Deutsche Telekom Group Security | `owasp-linter-rules.spectral.yaml` |
| **G-API**           | Deutsche Telekom G-API guidelines v2.11.1 for API design quality                       | `gapi-linter-rules.spectral.yaml`  |

### OWASP Ruleset Highlights

Key rules enforced (severity levels configured by Group Security):

- **owasp:api2:2023-no-http-basic** (error) - No HTTP Basic auth
- **owasp:api2:2023-no-api-keys-in-url** (error) - No API keys in URL
- **owasp:api4:2023-integer-limit** (error) - Integer fields must have min/max
- **owasp:api4:2023-string-limit** (error) - String fields must have maxLength, enum, const, or format (date-time, date,
  time, uuid, ipv4, ipv6)
- **owasp:api8:2023-no-scheme-http** (error) - Server URLs must use HTTPS
- **owasp:api8:2023-define-error-validation** (error) - Error responses must be defined
- **owasp:api3:2023-no-additionalProperties** (warn) - Restrict additional properties
- **owasp:api4:2023-rate-limit** (warn) - Rate limiting headers expected
- **owasp:api4:2023-array-limit** (warn) - Array fields should have maxItems

### Rules Turned Off (by Group Security decision)

- `owasp:api2:2023-short-lived-access-tokens` - Off
- `owasp:api2:2023-jwt-best-practices` - Off
- `owasp:api4:2023-rate-limit-responses-429` - Off
- `owasp:api8:2023-define-cors-origin` - Off
- `owasp:api8:2023-define-error-responses-401` - Off
- `owasp:api8:2023-define-error-responses-500` - Off
- `owasp:api9:2023-inventory-access` - Off

## Prerequisites

- **Node.js and npm** must be installed on the machine
- No global installations required — all dependencies are installed locally via `npm install`

## Bundled Resources

This skill ships with everything needed to run Spectral linting. All resources are located in the skill's `resources/`
directory:

```
spectral-linter/
├── SKILL.md              # This file
└── resources/
    ├── package.json              # npm dependencies (spectral-cli, owasp-ruleset)
    ├── owasp-linter-rules.spectral.yaml   # OWASP API Security Top 10 ruleset
    ├── gapi-linter-rules.spectral.yaml    # Deutsche Telekom G-API guidelines ruleset
    ├── spectral-lint.sh           # Linux/Mac linting script
    └── spectral-lint.cmd          # Windows linting script
```

## Execution Workflow

When this skill is invoked, follow these steps **in order**:

### Step 0: Setup — Install Spectral into the Target Project

Before any linting can happen, the Spectral tooling must be installed into the target project. This step is **idempotent
** — it skips files that already exist and only runs `npm install` when needed.

#### 0a: Determine the installation directory

Locate where the OpenAPI specs live in the target project. Common locations:

- `src/interfaces/`
- `src/main/resources/api/`
- `api/`
- Project root

The Spectral tooling is installed into a `spectral/` subfolder **next to or inside** the directory containing the
OpenAPI specs. If the specs are at the project root, install into `<project-root>/spectral/`.

**Examples:**

| Spec location           | Spectral install dir       |
|-------------------------|----------------------------|
| `src/interfaces/*.yaml` | `src/interfaces/spectral/` |
| `api/openapi.yaml`      | `api/spectral/`            |
| `openapi.yaml` (root)   | `spectral/`                |

#### 0b: Copy resources

Copy the bundled resources from this skill into the target install directory. The skill's resources are located at:

```
${SKILL_DIR}/resources/
```

Where `${SKILL_DIR}` is the directory containing this SKILL.md file.

Copy the following files into the install directory (skip if they already exist with identical content):

```bash
INSTALL_DIR="<target-project>/src/interfaces/spectral"  # adjust path

mkdir -p "${INSTALL_DIR}"

# Copy package.json, rulesets, and scripts
cp "${SKILL_DIR}/resources/package.json"                      "${INSTALL_DIR}/package.json"
cp "${SKILL_DIR}/resources/owasp-linter-rules.spectral.yaml"  "${INSTALL_DIR}/owasp-linter-rules.spectral.yaml"
cp "${SKILL_DIR}/resources/gapi-linter-rules.spectral.yaml"   "${INSTALL_DIR}/gapi-linter-rules.spectral.yaml"
cp "${SKILL_DIR}/resources/spectral-lint.sh"                  "${INSTALL_DIR}/spectral-lint.sh"
cp "${SKILL_DIR}/resources/spectral-lint.cmd"                 "${INSTALL_DIR}/spectral-lint.cmd"

# Make shell script executable (Linux/Mac)
chmod +x "${INSTALL_DIR}/spectral-lint.sh"
```

#### 0c: Install npm dependencies

Run `npm install` inside the install directory to fetch Spectral CLI and the OWASP ruleset:

```bash
cd "${INSTALL_DIR}" && npm install
```

This creates a local `node_modules/` with `@stoplight/spectral-cli` and `@stoplight/spectral-owasp-ruleset`. No global
install needed.

#### 0d: Verify installation

```bash
cd "${INSTALL_DIR}" && npx spectral --version
```

If this prints a version number, setup is complete.

#### 0e: Resulting project structure

After setup, the target project will have:

```
<target-project>/
├── src/interfaces/                    # (example spec location)
│   ├── FNCallnumberPortingMgmt/
│   │   └── spec/
│   │       └── FNCallnumberPortingMgmt.yaml
│   └── spectral/                      # ← installed by this skill
│       ├── package.json
│       ├── package-lock.json          # generated by npm install
│       ├── node_modules/              # generated by npm install
│       ├── owasp-linter-rules.spectral.yaml
│       ├── gapi-linter-rules.spectral.yaml
│       ├── spectral-lint.sh
│       └── spectral-lint.cmd
└── ...
```

#### 0f: Update .gitignore

After installation, ensure the target project's `.gitignore` excludes the generated `node_modules/` directory. Check the
project root `.gitignore` for an existing `node_modules` entry. If none exists, append it:

```bash
PROJECT_ROOT="<target-project>"

# Check if node_modules is already ignored
if ! grep -qE '^node_modules/?$' "${PROJECT_ROOT}/.gitignore" 2>/dev/null; then
  echo "" >> "${PROJECT_ROOT}/.gitignore"
  echo "# Spectral linter dependencies (auto-added)" >> "${PROJECT_ROOT}/.gitignore"
  echo "node_modules/" >> "${PROJECT_ROOT}/.gitignore"
fi
```

A bare `node_modules/` entry (without leading path) applies recursively, so it covers `spectral/node_modules/`
regardless of where the `spectral/` folder is placed.

The `package.json`, `package-lock.json`, rulesets, and scripts **should** be committed so other developers can just run
`npm install` in the `spectral/` directory.

### Step 1: Locate Specs

1. Find all OpenAPI spec files in the target project
2. If a specific spec was requested, verify it exists
3. If `--all` or no specific spec, discover all `.yaml`/`.yml`/`.json` files in the spec directory (excluding `target/`,
   `node_modules/`, `*owasp*`, `*spectral*`, `package*.json` files)

### Step 2: Select the Correct Script for the Shell

**Always detect the active shell before choosing the script.** On Windows, the shell may be `cmd.exe`, PowerShell, or
Git Bash (MSYS2/MinGW). The user's configured shell determines which script to run:

| Shell                                      | Script to use       | How to detect                                            |
|--------------------------------------------|---------------------|----------------------------------------------------------|
| **Bash** (Linux, Mac, Git Bash on Windows) | `spectral-lint.sh`  | `$SHELL` contains `bash` or `$MSYSTEM` is set (Git Bash) |
| **cmd.exe** (Windows native)               | `spectral-lint.cmd` | `%COMSPEC%` is set, no `$SHELL`                          |
| **PowerShell** (Windows)                   | `spectral-lint.cmd` | `$PSVersionTable` is set                                 |

**Rule**: If the current shell is `bash` (including Git Bash on Windows), **always use the `.sh` script**. The `.cmd`
script only works in `cmd.exe` or PowerShell.

### Step 3: Run Spectral Linting

Execute linting from the `spectral/` install directory using the bundled scripts:

```bash
INSTALL_DIR="<target-project>/src/interfaces/spectral"  # adjust path

# Using the shell script (Linux, Mac, Git Bash on Windows)
bash "${INSTALL_DIR}/spectral-lint.sh" "<path-to-spec>" [--ruleset owasp|gapi] [--verbose]

# Lint all specs
bash "${INSTALL_DIR}/spectral-lint.sh" "<specs-directory>" --all

# Or run npx directly from the spectral/ directory
cd "${INSTALL_DIR}" && npx spectral lint "<path-to-spec>" --ruleset "${INSTALL_DIR}/owasp-linter-rules.spectral.yaml"
```

```cmd
REM Using the cmd script (Windows cmd.exe or PowerShell)
<target-project>\src\interfaces\spectral\spectral-lint.cmd "<path-to-spec>" [--ruleset owasp|gapi] [--verbose]
```

Capture the full output including all errors, warnings, and info messages.

### Script Options

| Option             | Description                                             |
|--------------------|---------------------------------------------------------|
| `<spec-path>`      | Path to OpenAPI spec file or directory                  |
| `--all`            | Lint all OpenAPI specs found in the spec directory      |
| `--ruleset <name>` | Choose ruleset: `owasp` (default) or `gapi`             |
| `--verbose`        | Enable verbose Spectral output for detailed diagnostics |
| `--help`           | Display usage help                                      |

### Step 4: Parse Results

From the Spectral output, extract:

- **Errors** (severity: error) - Must be fixed
- **Warnings** (severity: warn) - Should be fixed
- **Info** (severity: info) - Informational, review recommended
- **Hints** (severity: hint) - Optional improvements

### Step 5: Generate Report

Create or update a report file `SPECTRAL_LINTING_REPORT_<spec-name>.md` with this structure:

# Spectral Linting Report: <Spec Name>

**Spec**: `<path-to-spec>`
**Ruleset**: OWASP / G-API
**Date**: YYYY-MM-DD
**Status**: PASSED | FAILED | WARNINGS

## Summary

| Severity  | Count |
|-----------|-------|
| Errors    | N     |
| Warnings  | N     |
| Info      | N     |
| Hints     | N     |
| **Total** | **N** |

## Errors

| # | Rule                         | Location                                                              | Description                   | Suggested Fix                        |
|---|------------------------------|-----------------------------------------------------------------------|-------------------------------|--------------------------------------|
| 1 | owasp:api4:2023-string-limit | paths./api/v1/orders.get.responses.200.content.schema.properties.name | String must specify maxLength | Add `maxLength: 255` to the property |

## Warnings

| # | Rule                       | Location                 | Description                   | Suggested Fix                              |
|---|----------------------------|--------------------------|-------------------------------|--------------------------------------------|
| 1 | owasp:api4:2023-rate-limit | paths./api/v1/orders.get | Rate limiting headers missing | Add `X-RateLimit-Limit` header to response |

## Info

| # | Rule                           | Location                  | Description                    |
|---|--------------------------------|---------------------------|--------------------------------|
| 1 | owasp:api1:2023-no-numeric-ids | paths./api/v1/orders.{id} | Consider using non-numeric IDs |

## Remediation Guide

### Common Fixes

- **String fields without maxLength**: Add `maxLength`, `enum`, `const`, or use
  `format: date-time|date|time|uuid|ipv4|ipv6`
- **Integer fields without bounds**: Add `minimum` and `maximum` constraints
- **Array fields without limits**: Add `maxItems` constraint
- **Missing error responses**: Add 4XX and 5XX response definitions
- **HTTP server URLs**: Change `http://` to `https://` in server URLs

### Step 6: Summary Output

When linting multiple specs, provide a final summary:

## Linting Summary

| Spec                            | Status | Errors | Warnings | Info  |
|---------------------------------|--------|--------|----------|-------|
| FNCallnumberPortingMgmt.yaml    | FAILED | 5      | 3        | 1     |
| FNCallnumberPortingMgmtBff.yaml | PASSED | 0      | 1        | 0     |
| **Total**                       |        | **5**  | **4**    | **1** |

## Report Location

Reports are written to the `docs/spectral-linting/` directory of the target project:

```
docs/spectral-linting/
├── SPECTRAL_LINTING_REPORT_FNCallnumberPortingMgmt.md
├── SPECTRAL_LINTING_REPORT_FNCallnumberPortingMgmtBff.md
└── ...
```

## Common OWASP Fixes Reference

| Rule                                      | Issue                           | Fix                                                                 |
|-------------------------------------------|---------------------------------|---------------------------------------------------------------------|
| `owasp:api4:2023-string-limit`            | String without maxLength        | Add `maxLength`, `enum`, `const`, or `format: date-time\|uuid\|...` |
| `owasp:api4:2023-integer-limit`           | Integer without min/max         | Add `minimum` and `maximum`                                         |
| `owasp:api4:2023-array-limit`             | Array without maxItems          | Add `maxItems`                                                      |
| `owasp:api8:2023-no-scheme-http`          | Server URL uses HTTP            | Change to `https://`                                                |
| `owasp:api2:2023-no-http-basic`           | HTTP Basic auth used            | Switch to OAuth2 or Bearer                                          |
| `owasp:api2:2023-no-api-keys-in-url`      | API key in query param          | Move API key to header                                              |
| `owasp:api8:2023-define-error-validation` | Missing error responses         | Add 400, 4XX, 5XX responses                                         |
| `owasp:api3:2023-no-additionalProperties` | Unrestricted properties         | Add `additionalProperties: false`                                   |
| `owasp:api4:2023-string-restricted`       | String without pattern          | Add `pattern` or `format` constraint                                |
| `owasp:api2:2023-write-restricted`        | Write endpoint without security | Add security scheme to POST/PUT/PATCH/DELETE                        |

## Exit Codes

| Code | Meaning                          |
|------|----------------------------------|
| 0    | All specs passed linting         |
| 1    | One or more specs failed linting |

## Integration with Development Workflow

### OpenAPI Spec Modification Workflow

1. Edit the OpenAPI YAML spec
2. **Run spectral linting** (this skill)
3. Fix all errors (mandatory)
4. Fix all warnings (recommended, exceptions must be documented)
5. Regenerate code: `mvn openapi-generator:generate`
6. Update tests to match spec changes

### CI/CD Integration

```yaml
# GitLab CI example
spectral-lint:
  stage: validate
  script:
    - cd src/interfaces/spectral && npm install
    - cd src/interfaces/spectral && npx spectral lint "../FNCallnumberPortingMgmt/spec/FNCallnumberPortingMgmt.yaml" --ruleset owasp-linter-rules.spectral.yaml
  allow_failure: false
```

```yaml
# GitHub Actions example
- name: Spectral Lint
  run: |
    cd src/interfaces/spectral && npm install
    cd src/interfaces/spectral && ./spectral-lint.sh ../FNCallnumberPortingMgmt/spec/FNCallnumberPortingMgmt.yaml --all
```

## Best Practices

1. **Lint early, lint often** - Run linting immediately after any spec change
2. **Fix errors before warnings** - Errors are security-relevant, warnings are quality-relevant
3. **Document exceptions** - If a warning cannot be fixed, document the reason in the spec as a comment
4. **Use both rulesets** - OWASP for security, G-API for design quality
5. **Keep reports updated** - Regenerate reports before committing spec changes
6. **Automate in CI/CD** - Add linting as a mandatory pipeline step
