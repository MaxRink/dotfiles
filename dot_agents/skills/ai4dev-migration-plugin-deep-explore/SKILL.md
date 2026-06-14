---
name: ai4dev-migration-plugin-deep-explore
description: Deep exploration and documentation of any codebase. Produces adaptive, scale-aware documentation covering tech stack, architecture, modules, APIs, data models, business logic, data flows, dependencies, and cross-cutting concerns. Use when the user wants to explore, document, understand, or analyze a codebase.
user-invocable: true
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/migration-plugin/skills/deep-explore by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Deep Explore — Orchestrator Workflow

You are the orchestrator. You do NOT read source files yourself.
You read the fingerprint, spawn waves of sub-agents via the Agent tool,
validate outputs between waves, and build the final index.

**Sub-agents available:**

| Agent name | Wave | Reference file |
|-----------|------|----------------|
| `one-modernizer:foundation-explorer` | 1 | `skills/deep-explore/references/foundation-reference.md` |
| `one-modernizer:stack-analyzer` | 2 | `skills/deep-explore/references/stack-analysis-reference.md` |
| `one-modernizer:cross-cutting-analyzer` | 3 | `skills/deep-explore/references/cross-cutting-reference.md` |
| `one-modernizer:mermaid-diagram-creator` | 3 | mermaid-diagrams skill (preloaded) |

**Key rules:**

- Sub-agents return only `DONE: <file> written`. Read files from disk between waves.
- Do NOT paste the full fingerprint into sub-agent prompts — pass only what each agent needs.
- Spawn all agents in a wave in a single message for parallelism.

## Step 0 — Load Fingerprint

Read `.migration/fingerprint.json` in full — this is your source of truth
for every downstream decision. If the file is missing, run `Glob("**/*")`
excluding standard skip dirs and proceed with minimal info.

The fingerprint includes repo scale, language/source-language breakdown,
directory map, integration seams, entry points, signals (CI/CD, DB, APIs),
microservice cluster detection, largest files, git metrics, build tools,
dependency counts, env surface, import graph, and more. Use whichever
fields fit each step.

Two fields you MUST honor throughout:

- `glob_exclude` — append to every sub-agent's Glob call
- `tier` — picks depth strategy (small/medium/large/xl)

If `microservice_cluster.detected` is true, prefer spawning one stack
agent per service in Wave 2 over `effective_units` splitting.

## Step 1 — Read Reference Files

Read these now — you need them for Step 5 (Finalize):

1. [references/schemas/schema.json](references/schemas/schema.json)
2. [references/examples/example-index.json](references/examples/example-index.json)
3. [references/completion-template.md](references/completion-template.md)
4. [references/output-format.md](references/output-format.md)

## Step 2 — Wave 1: Foundation (4 parallel agents)

Spawn all four in a **single message**. Each gets only the data it needs:

**Agent 1 — Repository Structure:**

- Data: tier, glob_exclude, technology_map (dir names + file counts + dominant_language only)
- Output: `.migration/docs/overview/folder-structure.md`

**Agent 2 — Tech Stack Detection:**

- Data: tier, glob_exclude, root_manifests list, technology_map keys
- Output: `.migration/docs/overview/tech-stack.md`

**Agent 3 — Entry Points:**

- Data: tier, glob_exclude, entry_point_hints list
- Output: `.migration/docs/overview/entry-points.md`

**Agent 4 — Stack Inventory:**

- Data: tier, glob_exclude, technology_map (full), integration_seams
- Output: `.migration/docs/overview/stack-inventory.md`

### Validate Wave 1

After all agents return, Glob for `".migration/docs/overview/*.md"`.
Verify all 4 files exist and each has > 5 lines. Re-spawn any missing/empty agent.

## Step 3 — Wave 2: Stack Deep Analysis

Read `.migration/docs/overview/stack-inventory.md` to confirm the stack list.

### Splitting strategy

Use `effective_units` from the fingerprint's `technology_map`:

| effective_units | Strategy |
|----------------|----------|
| ≤ 500 | One agent for the whole stack |
| 501–1,500 | Split into 2 groups by subdirectory |
| > 1,500 | Split into groups of ≤ 500 each |

### Per-stack agent prompt

Give each agent only its slice of the fingerprint:

```text
Analyze the <stack-name> stack.
Directory: <dir>
Dominant language: <language>
Extensions: <top extensions>
Effective units: <eu>
Tier: <tier>
GLOB EXCLUDE: <glob_exclude>
Write to: .migration/docs/modules/<stack-name>.md
```

For split stacks, add: `You are documenting part <N> of <M>. Only cover subdirectories: <list>. Write to: .migration/docs/modules/<stack-name>-part-<N>.md`

### Integration analysis (if seams detected)

Spawn alongside stack agents:

```text
Analyze integration seams (not a stack analysis).
SEAM FILES: <seams array — label + files only>
Stack directories: <list>
GLOB EXCLUDE: <glob_exclude>
Write to: .migration/docs/cross-cutting/integration-seams.md
```

### Merge step (split stacks only)

After partition agents finish, spawn a merge agent per split stack:

```text
Merge all part files for <stack-name>.
Read: .migration/docs/modules/<stack-name>-part-*.md
Write: .migration/docs/modules/<stack-name>.md
Preserve all detail. Remove duplicate headers. Delete part files after merging.
```

### Validate Wave 2

Glob for `".migration/docs/modules/*.md"`. Verify each expected stack has a file
with > 10 lines. Re-spawn any missing/empty agent.

## Step 4 — Wave 3: Cross-Cutting + Diagrams

Determine which concerns apply using the extension inventory and seams:

| Concern | Spawn when |
|---------|-----------|
| `database-schema.md` | `.sql`, `.pc`, `.ddl`, `.ora`, `.plsql` in inventory |
| `api-contracts.md` | `.idl`, `.wsdl`, `.proto`, `.graphql` in inventory, or seam `corba`/`idl-consumer` |
| `security.md` | seam labels `jni-native`, `jni-java`, or security-related dirs |
| `data-flow.md` | integration seams detected, or multiple stacks |
| `dependencies.md` | more than 2 stacks in technology map |
| `infrastructure.md` | `.yml`/`.yaml` in deploy/, kubernetes/, docker/, or Dockerfile |
| `testing.md` | test dirs or `*test*`/`*spec*` files found |
| `technical-debt.md` | always |

**Per-concern agent prompt** — give module doc paths, not fingerprint:

```text
Analyze cross-cutting concern: <concern-name>
Stack doc files to read: <list of .migration/docs/modules/*.md paths>
GLOB EXCLUDE: <glob_exclude>
Write to: .migration/docs/cross-cutting/<concern-name>.md
```

**Diagram agent prompt** — give all doc file paths:

```text
Generate Mermaid diagrams for the codebase documentation.
Documentation files: <list all .md paths under .migration/docs/>
Output directory: .migration/docs/overview/

ALWAYS produce:
- Stack dependency graph → NEW file .migration/docs/overview/dependency-graph.md

Produce when they add value (READ existing file, then APPEND diagram):
- Architecture overview (C4) → append to overview/stack-inventory.md
- Integration sequence diagrams → append to cross-cutting/integration-seams.md
- Data flow diagrams → append to cross-cutting/data-flow.md
- ERD → append to cross-cutting/database-schema.md
```

## Step 5 — Finalize

After all waves complete, you build the index and quality score yourself.

### Build index.json

Read all files under `.migration/docs/`. Build the manifest per schema.json:

- `repository`: path and name
- `scan`: timestamp, tier, total file count, skip dirs
- `project`: name, description from README or manifest
- `stacks`: array from stack-inventory.md — `{ name, directory, technology, file_count, summary, doc_file, public_interface }`
- `integration_seams`: array if produced — `{ label, description, files[] }`
- `technology_stack`: aggregated languages, frameworks, databases, build_tools
- `file_index`: pattern-based mapping covering ≥ 90% of total files
- `cross_cutting`: list of cross-cutting docs with paths
- `output_files`: every file under .migration/docs/ with description
- `metadata`: generated_at, quality_score (0–100), coverage object

Use schema.json and example-index.json from Step 1. Write: `.migration/docs/index.json`

### Quality Score

Use completion-template.md from Step 1. Calculate score (0–100) from 5 criteria:
files documented, modules documented, APIs documented, data models documented, cross-cutting produced.

## Completion

```text
Deep exploration complete.
Output: .migration/docs/index.json
Quality score: <score>/100
```

## Troubleshooting

- **Sub-agent fails**: Re-spawn only that agent. Do not restart the wave.
- **Stack too large**: Partition using subdirs from fingerprint. Max 500 eu per agent.
- **No stack boundaries**: Treat as one stack with grep-first + sampling.
- **index.json validation fails**: Re-run Build index.json in Step 5.
- **Extension coverage < 90%**: Add glob patterns for missing extensions.
