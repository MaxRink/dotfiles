
# Stack Analysis Reference

Reference files available (read from `skills/deep-explore/references/`):

1. [module-template.md](module-template.md) — structural template for per-module documentation
2. [extraction-checklist.md](extraction-checklist.md) — what to extract per module

Additional reference to consult for your stack's language:

1. [language-patterns.md](language-patterns.md) — grep patterns by language (read the section for your assigned language)

## Stack Deep Analysis

You analyze ONE technology stack (or one partition of a large stack).

**Strategy by effective_units in scope:**

| effective_units | Approach |
|-----------------|----------|
| < 50 | Read all source files |
| 50–200 | Grep-first: build file map, read key files deeply |
| 200–500 | Grep-first + sampling: entry points + one representative per pattern |

**Grep-first approach:**

Before reading any file, consult the language-patterns reference for your stack's
dominant language. Run 3-5 targeted Greps to build a file map. The results give
you file paths and line numbers — read those files, not everything.

If your stack's language isn't in the patterns reference, adapt the closest match.
The key structural elements to find:

- Classes/components and their hierarchies
- API endpoints or public interfaces
- Data models and database access
- Async/event handlers
- Technical debt markers (TODO/FIXME/HACK)

**Language-specific extraction guidance:**

- Java/Kotlin/Scala: classes, methods, annotations, Spring beans, JPA entities
- C/C++: headers (public interface), key implementation files, memory management
- SQL: all tables, procedures, triggers, views — read every `.sql` file fully
- COBOL: program structure, DATA DIVISION, key PROCEDURE DIVISION paragraphs
- Tcl: proc definitions, package structure, external calls
- IDL/WSDL: every interface definition and operation — read every file fully
- Go/Rust: public functions, struct definitions, interface implementations
- Python: classes, decorators, model definitions, route handlers
- TypeScript/JS: exports, decorators, route definitions, schema definitions

Use the module template and extraction checklist as structural guidance.
Write to the output path specified in your prompt.

## Integration Analysis

When your prompt specifies integration seam analysis instead of stack analysis:

Read every seam file identified. For each seam:

1. **Read the file** — understand what it does at the boundary
2. **Trace both sides** — what calls this? What does it call?
3. **Document the contract** — data crossing the boundary, failure modes
4. **Assess migration risk** — how hard to re-implement in new architecture

Seam types: JNI, CORBA, IDL consumers, embedded SQL (Pro*C/EXEC SQL),
COBOL calls (CICS), subprocess, IPC.

Write to the output path specified in your prompt.
