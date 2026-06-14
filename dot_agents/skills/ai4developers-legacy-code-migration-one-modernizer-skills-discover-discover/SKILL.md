---
name: ai4developers-legacy-code-migration-one-modernizer-skills-discover-discover
description: "Discover and document a legacy codebase for migration. Scans source code, builds a knowledge graph via graphify, and produces structured documentation in .migration/. Use when the user wants to understand, map, or prepare a codebase for modernization — even if they just say 'analyze this project' or 'what does this code do' in the context of migration work."
---

<!-- Imported from ai4developers/legacy-code-migration/one-modernizer/skills/discover by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Discover & Document

You are a legacy code discovery expert. Your job is to deeply understand a codebase and produce structured documentation that enables accurate migration planning.

## Supporting Files

- **References**: Strategy docs and language-specific patterns
  - [references/parallel-strategy.md](references/parallel-strategy.md) — **READ THIS** for repos > 100k LOC. Defines the 4-phase parallel discovery architecture that achieves 95%+ accuracy.
  - [references/legacy-patterns.md](references/legacy-patterns.md) — COBOL, C/C++, VB6, Fortran detection patterns
  - [references/oracle-patterns.md](references/oracle-patterns.md) — PL/SQL patterns, PRAGMA, cursors, bulk ops, DBMS\_ packages
  - [references/batch-patterns.md](references/batch-patterns.md) — JCL, Control-M, Autosys, utility programs, GDGs
  - [references/sme-interview-protocol.md](references/sme-interview-protocol.md) — Role-specific structured interview questions
- **Templates**: Exact output format for generated docs (fill in every field)
  - [templates/module.md](templates/module.md) — per-module documentation
  - [templates/overview.md](templates/overview.md) — system-level overview
  - [templates/unknowns.md](templates/unknowns.md) — ambiguities and open questions
  - [templates/oracle-module.md](templates/oracle-module.md) — Oracle/DB-specific module docs
  - [templates/batch-topology.md](templates/batch-topology.md) — batch job topology
  - [templates/shared-structures.md](templates/shared-structures.md) — copybook/header inclusion chains
  - [templates/ownership-matrix.md](templates/ownership-matrix.md) — who owns what
  - [templates/compliance-constraints.md](templates/compliance-constraints.md) — regulatory constraints
  - [templates/sla-registry.md](templates/sla-registry.md) — SLA commitments
  - [templates/runtime-profile.md](templates/runtime-profile.md) — hot paths, dead code, data volumes
  - [templates/test-readiness.md](templates/test-readiness.md) — test coverage and validation strategy
- **Scripts**: Run these to handle scale, verify quality, and produce outputs
  - `scripts/chunk_repo.py` — partition large repos (2M+ LOC) into processable chunks
  - `scripts/verify_coverage.py` — check what % of source files are covered in docs
  - `scripts/accuracy_check.py` — spot-check that file/symbol references actually exist
  - `scripts/resolve_includes.py` — resolve COBOL COPY and C/C++ #include chains
  - `scripts/extract_batch.py` — parse JCL, Control-M, Autosys into batch topology
  - `scripts/batch_critical_path.py` — find critical chains and parallelization opportunities
  - `scripts/extract_oracle.py` — parse Oracle DDL/PL-SQL into object inventory
  - `scripts/ingest_oracle_metadata.py` — ingest DBA view exports into knowledge graph
  - `scripts/ingest_runtime.py` — ingest APM/AWR/coverage/log data
  - `scripts/dead_code_analysis.py` — cross-reference runtime data with graph for dead code
  - `scripts/test_inventory.py` — detect test frameworks, fixtures, coverage gaps

## Step 1: Gather Context & SME Interviews

Ask the user these questions interactively. Wait for answers before proceeding:

1. "What is this project? What does it do at a high level?"
2. "Are there any external docs I should consider? (Wiki pages, Confluence, local file paths, Jira — paste links or say 'none')"
3. "What's the primary language and tech stack?" — or offer to auto-detect
4. "Any critical business rules, domain knowledge, or gotchas?"

If the user says "just figure it out" or similar, auto-detect by scanning file extensions, project files (.csproj, .sln, Makefile, pom.xml, etc.), and structure.

**After auto-detection**, present stack-specific interview questions from [references/sme-interview-protocol.md](references/sme-interview-protocol.md):

- If COBOL/mainframe detected → ask Operations + DBA questions
- If Oracle/PL-SQL detected → ask full DBA interview
- If C/C++ detected → ask Architect questions
- For all large codebases → ask Developer ownership questions

Capture answers in:

- `.migration/discovery/ownership-matrix.md` (using template)
- `.migration/discovery/compliance-constraints.md` (using template)
- `.migration/discovery/sla-registry.md` (using template)

If the user cannot answer ownership/compliance questions now, note them in `.migration/discovery/unknowns.md` for follow-up.

## Step 2: Assess Scale & Choose Strategy

Run the chunking script to understand repo size:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/chunk_repo.py .
```

This writes `.migration/discovery/chunks.json` with LOC counts and module groupings.

**Decision point:**

- **Small repo** (< 100k LOC, 1-3 chunks): proceed with Steps 3-8 sequentially below
- **Large repo** (100k+ LOC, 4+ chunks): read [references/parallel-strategy.md](references/parallel-strategy.md) and follow its 4-phase parallel architecture instead. Spawn documenter agents for each module in parallel to maintain accuracy at scale.

## Step 3: Build the Knowledge Graph

Run from the project root directory. Define a shorthand first:

```bash
OM="${CLAUDE_PLUGIN_DATA}/venv/bin/one-modernizer"
GRAPH=.migration/discovery/graphify-out/graph.json
GRAPHIFY_OUT=.migration/discovery/graphify-out "$OM" extract . --out .migration/discovery --no-cluster; GRAPHIFY_OUT=.migration/discovery/graphify-out "$OM" cluster-only .migration/discovery --graph "$GRAPH"
```

Note: `extract` may exit with code 1 if no LLM API key is set — AST extraction still works without an LLM. Use `;` not `&&` so clustering runs regardless.

On Windows, replace `venv/bin/` with `venv/Scripts/` in the `OM` path.

This produces:

- `.migration/discovery/graphify-out/graph.json` — queryable knowledge graph
- `.migration/discovery/graphify-out/graph.html` — interactive visualization
- `.migration/discovery/graphify-out/GRAPH_REPORT.md` — god nodes, communities, surprising connections

After building, read `.migration/discovery/graphify-out/GRAPH_REPORT.md` to understand the codebase structure.

### Step 3b: Oracle DB Discovery (if Oracle/PL-SQL detected)

Run when `.pls`, `.pkb`, `.pks`, `.trg`, `.fnc`, `.prc` files are present, or user provides DDL dumps:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/extract_oracle.py .
```

If the user can provide DBA view exports (CSV/JSON), ingest them:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/ingest_oracle_metadata.py . --file <path> --type dba_objects
python3 ${CLAUDE_SKILL_DIR}/scripts/ingest_oracle_metadata.py . --file <path> --type dba_dependencies
python3 ${CLAUDE_SKILL_DIR}/scripts/ingest_oracle_metadata.py . --file <path> --type dba_tab_columns
```

Ask the user: "Do you have Oracle DBA exports (DBA_OBJECTS, DBA_DEPENDENCIES, DBA_TAB_COLUMNS as CSV)? These dramatically improve dependency mapping."

Use [references/oracle-patterns.md](references/oracle-patterns.md) to identify Oracle-specific complexity.

### Step 3c: Batch Topology Discovery (if JCL/batch detected)

Run when `.jcl` or `.proc` files are present:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/extract_batch.py .
python3 ${CLAUDE_SKILL_DIR}/scripts/batch_critical_path.py .
```

Use [references/batch-patterns.md](references/batch-patterns.md) to interpret JCL patterns. For large batch estates, spawn a `batch-analyst` agent for detailed topology documentation.

### Step 3d: Inclusion Chain Resolution (if COBOL or C/C++ detected)

Run when `.cbl`, `.cob`, `.cpy`, `.h`, or `.hpp` files are present:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/resolve_includes.py .
```

If copybooks are in a non-standard location, ask the user and pass `--include-path`:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/resolve_includes.py . --include-path /path/to/COPYLIB
```

## Step 4: Deep Exploration — Read EVERY Source File

**Skip this step if using the parallel strategy from Step 2** — the documenter agents handle it per-module.

The graph gives you structure. Now you need to understand what the code actually DOES. Read every source file.

1. **Read ALL source files** — use Glob to list them, then Read each one. For large repos, process chunk by chunk per `chunks.json`.

2. **For each file, understand**:
   - What does this file do? (its role in the system)
   - What are its public interfaces?
   - What business logic does it contain?
   - What external systems does it talk to?
   - What data does it transform?
   - What error handling exists?

3. **Use the graph for relationships** (using `$OM` and `$GRAPH` from Step 3):

```bash
"$OM" query "entry points and main services" --graph "$GRAPH"
"$OM" query "external dependencies and interfaces" --graph "$GRAPH"
"$OM" path "<ModuleA>" "<ModuleB>" --graph "$GRAPH"
```

4. **Don't forget non-code files** — config files, SQL scripts, build files, deployment configs, docker files.

### Step 4b: Runtime Intelligence (if operational data available)

Ask the user: "Do you have any operational data I can use? (APM exports, Oracle AWR reports, code coverage reports, program execution logs as CSV)"

If yes, ingest each data source:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/ingest_runtime.py . --file <path> --type apm
python3 ${CLAUDE_SKILL_DIR}/scripts/ingest_runtime.py . --file <path> --type awr
python3 ${CLAUDE_SKILL_DIR}/scripts/ingest_runtime.py . --file <path> --type coverage
python3 ${CLAUDE_SKILL_DIR}/scripts/ingest_runtime.py . --file <path> --type log_frequency
```

Then run dead code analysis:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/dead_code_analysis.py .
```

This overlays runtime activity on the knowledge graph, identifying hot paths and dead code candidates.

## Step 5: Document Everything

For each module/community from the graph report:

1. Read the appropriate template and fill in EVERY field:
   - Standard modules → `templates/module.md`
   - Oracle/DB-heavy modules → `templates/oracle-module.md`
   - Batch processing → `templates/batch-topology.md`
2. Write to `.migration/discovery/modules/<name>.md`

Also write `.migration/discovery/unknowns.md` using `templates/unknowns.md`.

Use [references/legacy-patterns.md](references/legacy-patterns.md) to identify module boundaries, interfaces, and business rules for the detected language.

**Completeness requirements:**

- Every source file must appear in at least one module doc
- Every public class/method/endpoint must be documented
- Every external call (DB, HTTP, file, queue) must be listed with exact target
- Every business rule (if/else logic that makes a domain decision) must be captured with `file:line`
- Every configuration value that affects behavior must be noted
- The full request/data flow from entry point to exit must be traceable through the docs

Every claim MUST have a `file:line` citation. No exceptions.

### Step 5b: Test Asset Inventory

Run the test inventory scanner:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/test_inventory.py .
```

Document findings using `templates/test-readiness.md` and write to `.migration/discovery/test-readiness.md`.

## Step 6: Clarify Unknowns

When you encounter ambiguous logic or missing context, ask the user for clarification interactively before finalizing.

Skip this step if the user indicated "just figure it out" in Step 1 — instead, document all ambiguities in `.migration/discovery/unknowns.md` with `UNKNOWN:` prefixes and confidence levels.

## Step 7: Verify & Fix Loop

Run verification scripts and iterate until quality targets are met:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/verify_coverage.py .
python3 ${CLAUDE_SKILL_DIR}/scripts/accuracy_check.py .
```

**Targets: coverage >= 95%, accuracy >= 95%**

Fix loop (max 3 iterations):

1. If coverage < 95% → identify uncovered directories, add module docs for them
2. If accuracy < 95% → read failed claims, check actual source, fix or remove hallucinated references
3. Re-run both scripts after fixes

If targets aren't met after 3 iterations, report current scores to user with specific remaining gaps.

## Step 8: Final Output

Once verification passes, the `.migration/discovery/` directory contains the complete discovery output:

- `.migration/discovery/modules/*.md` — per-module documentation with `file:line` citations
- `.migration/discovery/overview.md` — system-level summary
- `.migration/discovery/unknowns.md` — ambiguities and open questions
- `.migration/discovery/graphify-out/graph.json` — queryable knowledge graph
- `.migration/discovery/graphify-out/GRAPH_REPORT.md` — god nodes, communities, connections
- `.migration/discovery/index.json` — machine-readable summary for LLM consumption in subsequent pipeline steps

Plus any optional outputs produced by sub-steps:

- `.migration/discovery/oracle/` — DB object inventory and dependencies (if Step 3b ran)
- `.migration/discovery/batch/` — batch topology and critical paths (if Step 3c ran)
- `.migration/discovery/includes/` — copybook/header resolution (if Step 3d ran)
- `.migration/discovery/runtime/` — usage profiles and dead code (if Step 4b ran)
- `.migration/discovery/test-inventory.json` — test asset inventory (if Step 5b ran)

### Step 8b: Architecture Diagrams

After documentation is complete, generate `.migration/discovery/architecture.md` containing architecture diagrams as embedded Mermaid and PlantUML code blocks. Architects can read this directly in GitLab/GitHub/Confluence or render with any plugin.

Include these diagrams:

1. **System context** — the system as a box, all external actors/systems (users, partner APIs, databases, MQ, batch feeds)
2. **Service interactions** — modules/services as nodes, arrows showing calls with protocol labels (HTTP, MQ, DB, file, CICS)
3. **Main request flows** — sequence diagrams for the top 3-5 critical end-to-end paths
4. **Data flow** — sources, transformations, stores, sinks
5. **Batch topology** — job chains and dataset dependencies (only if Step 3c ran)

**Diagram rules:** max 15 nodes per diagram (split if larger), one-line description above each, both Mermaid and PlantUML blocks, only use evidenced interactions.

## Rules

- NEVER guess at business logic — flag it in unknowns.md and ask
- Preserve exact names from source (class names, method names, table names, config keys)
- Document data transformations precisely (field mappings, type conversions)
- Note every external interface (HTTP, DB, file I/O, message queues, gRPC)
- Identify batch vs online/interactive processing paths
- Track shared data structures (shared projects, common libraries, base classes)
- The `.migration/discovery/` directory is the ONLY output location
- If graphify fails or produces an empty graph, fall back to manual code exploration (Glob + Read + Grep) and still produce the documentation
- For repos > 100k LOC, always chunk first — do not attempt to read the entire codebase in one pass
- All sub-steps (3b, 3c, 3d, 4b, 5b) are **optional and auto-detected** — only run them when relevant artifacts are present
