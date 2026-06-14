
# Foundation Explorer Reference

## Output Conventions

- All output goes under `.migration/docs/`
- Overview files: `.migration/docs/overview/<file>.md`
- Use `##` / `###` headers consistently
- Concise bullets, no long paragraphs
- Every claim must reference a file path (`path/file:line`)
- Include enough context that an LLM reading the file understands the component without source code

## Step Instructions

Your prompt specifies which step to execute. Follow the instructions below for that step.

### Step 1 — Repository Structure

Document the repository layout from the technology map and a shallow directory scan.
**Do not read source files** — directory names and file counts are sufficient.

- **Top-level directories**: name, purpose, dominant file types (from technology map)
- **Organization pattern**: monorepo, modular monolith, microservices, layered, hexagonal — infer from directory structure
- **File statistics**: counts by extension and directory (from fingerprint data)
- **Build output directories**: dist, build, target, out — flag as skip dirs
- **Stack boundaries**: which directories belong to which technology stack

Write: `.migration/docs/overview/folder-structure.md`

### Step 2 — Tech Stack Detection

Read the root manifest files listed in your prompt. Then for each top-level directory
in the technology map, check for manifest files (`pom.xml`, `package.json`, `build.gradle`,
`go.mod`, `Cargo.toml`, `CMakeLists.txt`, etc.).

Document per stack:

- **Language and version** — from manifest or source file headers
- **Build system** — with version if detectable
- **Frameworks** — name, exact version, role
- **Databases** — type, name, version, config reference
- **Message systems** — Kafka, RabbitMQ, JMS, etc.
- **External dependencies** — from manifest files, categorized by purpose
- **CI/CD** — pipeline files, stages, deployment targets
- **Infrastructure** — Docker, Kubernetes, cloud services

Write: `.migration/docs/overview/tech-stack.md`

### Step 3 — Entry Points

Find every entry point using targeted Globs (not `**/*`):

- **Application bootstrap**: `**/main.*`, `**/Application.*`, `**/server.*`, `**/app.*`
- **COBOL programs**: `**/*.cbl`, `**/*.cob`
- **SQL entry points**: stored procedures, scheduled jobs
- **Scripts**: deploy/ or scripts/ directories
- **IDL/WSDL interfaces**: public interface definitions
- **Config-driven**: Spring XML beans with `init-method`, job schedulers

For each: file path, what it initializes, what it calls, its role.

Write: `.migration/docs/overview/entry-points.md`

### Step 4 — Stack Inventory

Using the technology map from your prompt, produce a confirmed inventory. Per stack:

- **Name** — human-readable label
- **Directory** — root path
- **Technology** — primary language/platform
- **File count** — from technology map
- **Purpose** — one paragraph
- **Public interface** — APIs, IDL, SQL procedures, shared libraries, message topics
- **Key dependencies** — other stacks or external systems (use integration seams)
- **Build artifact** — JAR, .so, schema, executable

Write: `.migration/docs/overview/stack-inventory.md`
