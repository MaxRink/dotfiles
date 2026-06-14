# Deep Explore Output Format

## Output Directory

`.migration/docs/`

All output files are written here. Consumers read `index.json` first, then load only the sections they need.

### Directory Layout

```text
.migration/docs/
├── index.json                    # Mandatory manifest (always at root)
├── overview/                     # Repository-wide overview docs
│   ├── folder-structure.md       # Directory layout, org pattern, file stats
│   ├── tech-stack.md             # Languages, frameworks, databases, build tools
│   ├── entry-points.md           # Application, config, build, test entry points
│   ├── components.md             # Module/component identification
│   └── dependency-graph.md       # Mermaid inter-module dependency diagram
├── modules/                      # Per-module deep documentation
│   └── <module-name>.md          # One file per module (capped by tier)
└── cross-cutting/                # System-wide cross-cutting concerns
    ├── data-flow.md
    ├── dependencies.md
    ├── api-contracts.md
    ├── security.md
    ├── database-schema.md
    ├── testing.md
    ├── infrastructure.md
    └── technical-debt.md
```

Only `index.json` lives at the root. All section docs go into one of three subdirectories: `overview/`, `modules/`, or `cross-cutting/`.

## Mandatory Artifact

**`index.json`** — the manifest. Must always be produced. Contains:

- Repository metadata
- Scan details (tier, file counts, timestamp)
- `output_files` array listing every file produced with description
- Module summaries, tech stack, cross-cutting references
- Quality score

See `schemas/schema.json` for the full JSON schema.

## Scale Tiers

The agent detects repo size in Step 0 (two Glob calls) and adapts its strategy:

| Tier | Files | Scan Strategy | file_index (required) | Max Module Docs |
|------|-------|---------------|----------------------|-----------------|
| **Small** | < 500 | Full scan — read every relevant file | **Required** — per-file entries mapping each file to its module | Unlimited |
| **Medium** | 500–3,000 | Depth-limited — scan all top-level, sample inner modules | **Required** — source files only (skip configs, assets) | 40 |
| **Large** | 3,000–10,000 | Config-first + entry-point tracing — prioritize configs, trace from entry points | **Required** — pattern-based (glob patterns → module mapping) | 25 |
| **XL** | > 10,000 | Skeleton — root configs + module boundaries only | **Required** — pattern-based (coarse glob patterns for top-level module boundaries) | 15 |

## Section Files

### Always Produced

| File | Content |
|------|---------|
| `index.json` | Mandatory manifest with `output_files` discovery mechanism |
| `overview/tech-stack.md` | Programming languages, frameworks, databases, build tools, infrastructure |
| `overview/folder-structure.md` | Directory layout, organization pattern, file statistics |

### Produced When Relevant

| File | Produce when... |
|------|----------------|
| `overview/entry-points.md` | Entry points found (application, config, build, test) |
| `overview/components.md` | Distinct components or services identified |
| `overview/dependency-graph.md` | Inter-component dependencies exist |
| `modules/<name>.md` | Module has enough substance — classes, APIs, business logic. One per module, capped by tier. |
| `cross-cutting/data-flow.md` | Data flows between components or services |
| `cross-cutting/dependencies.md` | Dependency graph is non-trivial (circular deps, complex chains) |
| `cross-cutting/api-contracts.md` | REST/GraphQL/gRPC/CORBA/IDL/SOAP/event APIs found |
| `cross-cutting/security.md` | Security patterns span multiple modules |
| `cross-cutting/database-schema.md` | Database is non-trivial (multiple tables, relationships) |
| `cross-cutting/testing.md` | Tests exist across modules |
| `cross-cutting/infrastructure.md` | Infrastructure/deployment config exists |
| `cross-cutting/technical-debt.md` | Significant technical debt found |

## Section File Format Guidelines

- **Concise**: Bullets and short lines. Avoid long paragraphs.
- **Structured**: Use `##` / `###` headers consistently.
- **One concern per file**: No mixing of tech stack, structure, and components.
- **Machine- and human-readable**: Clear headers, paths in backticks, code blocks for signatures.
- **Evidence-based**: Every claim should reference a file path (`file/path:line` format).
- **LLM-optimized**: Include enough context that an LLM reading the file can understand the component without reading the source code.

## Documentation Depth

- **Module docs** (`modules/<name>.md`): See `module-template.md` for the full template and `extraction-checklist.md` for what to extract per module.
- **Cross-cutting docs** (`cross-cutting/*.md`): See `cross-cutting-templates.md` for the full templates per concern.

## Validation Rules

1. `index.json` exists and is valid JSON
2. `index.json` has required fields: `repository`, `scan`, `output_files`
3. `output_files` array lists every file that was produced
4. Every file listed in `output_files` exists on disk
5. No files exist in `.migration/docs/` that aren't listed in `output_files` (except `index.json` and `audit-report.md` at the root level)

## Consumer Workflow

1. Read `.migration/docs/index.json`
2. Check `output_files` to see what's available
3. Load `overview/` docs for high-level understanding
4. For module details: read individual `modules/<name>.md` files
5. For system-wide views: read `cross-cutting/*.md` files
