# Default Golden Principles

These principles are shipped with the plugin and reflect patterns observed across
multiple migration audits. They reduce false positives and ensure consistent,
fair evaluation by the llm-as-judge.

Learned principles (stored in `$CLAUDE_PLUGIN_DATA/golden-principles/`) supplement
but never override these defaults.

---

## GP-001: Build command variants in illustrative snippets are observational, not failures

- **Severity**: OBS
- **Applies to**: audit-explore, Check 7 (Evidence Spot-Check)
- **Pattern**: A documentation snippet shows a CLI flag or build command that
  differs slightly from what the source code actually uses
  (e.g., `cobc -x -free` vs fixed-format source).
- **Rationale**: Illustrative snippets in documentation may simplify or
  generalise commands for readability. Only flag as FAIL if the discrepancy
  is systematic across the entire document, not for isolated variants.

---

## GP-002: IDE/editor config files excluded from file_index are not orphans

- **Severity**: OBS
- **Applies to**: audit-explore, Check 4 (file_index Completeness)
- **Pattern**: Files like `.vscode/settings.json`, `.idea/`, or
  `.editorconfig` appear in documentation but are excluded from `file_index`
  via `skip_dirs` or `skip_patterns` in `fingerprint.json`.
- **Rationale**: These files are intentionally excluded from indexing because
  they are user-specific configuration, not application source code. Their
  mention in docs does not constitute a coverage gap.

---

## GP-003: Transitive framework dependencies are not application-level patterns

- **Severity**: OBS
- **Applies to**: audit-explore, Check 6 (Cross-Cutting Coverage)
- **Pattern**: A dependency tree includes libraries (e.g., `pyjwt`,
  `cryptography`, `jackson-databind`) that are transitive dependencies of a
  framework or SDK, not direct application choices.
- **Rationale**: The presence of a transitive dependency does not mean the
  application implements the corresponding cross-cutting concern. For example,
  `pyjwt` pulled in by an MCP SDK does not mean the app has an authentication
  layer that needs documenting.

---

## GP-004: Small repos achieve high coverage naturally

- **Severity**: OBS
- **Applies to**: audit-explore, Check 9 (Coverage Accuracy)
- **Pattern**: A repository with fewer than 10 source files achieves 90-100%
  coverage scores across all dimensions.
- **Rationale**: Small codebases have fewer files, modules, and APIs, making
  full coverage straightforward. High scores in small repos are expected, not
  suspicious. Do not penalise or flag as "trivially achieved" — validate the
  numbers are accurate, not whether the repo is complex enough to deserve them.

---

## GP-005: Natural language pseudocode is acceptable

- **Severity**: OBS
- **Applies to**: audit-analysis, Check 5 (Pseudocode Presence)
- **Pattern**: The `pseudocode` field in business rules or control flows uses
  plain English descriptions rather than formal notation (e.g., no
  `IF/THEN/ELSE` keywords, no indented blocks).
- **Rationale**: The purpose of pseudocode is to convey logic clearly. Natural
  language that accurately describes the flow is valid. Only flag as a warning
  if the pseudocode is empty, a single word, or simply restates the summary
  without adding detail.

---

## GP-006: Generated/config file business rules may have lower confidence

- **Severity**: OBS
- **Applies to**: audit-analysis, Check 3 (Source Evidence Spot-Check)
- **Pattern**: A business rule extracted from a generated file
  (e.g., `package-lock.json`, `*.min.js`, CI config) has
  `confidence: low` or `confidence: medium`, and the `location` file:line
  reference points to a generated or configuration file.
- **Rationale**: Business rules in generated or configuration files are
  inherently less precise — the "source" is often a build tool or template,
  not human-authored logic. Lower confidence is the correct assessment, not
  an evidence quality issue.

---

## GP-007: Schema deviations with correct content need reformatting, not regeneration

- **Severity**: WARNING
- **Applies to**: audit-analysis, Check 1 (Schema Compliance)
- **Pattern**: The `analysis.json` contains all required information but uses
  non-standard field names, ID formats, or structural organisation
  (e.g., `description` instead of `summary`, `BR-NNN` instead of `BR001`).
- **Rationale**: When the content is substantively correct but the shape is
  wrong, the fix is reformatting the existing output to match the schema — not
  discarding it and starting over. Flag as a structural issue with clear
  remediation steps showing the mapping from actual to expected fields.

---

## GP-008: Absent cross-cutting docs for concerns with no codebase signals are correct

- **Severity**: OBS
- **Applies to**: audit-explore, Check 6 (Cross-Cutting Coverage)
- **Pattern**: A cross-cutting concern (e.g., Database, Security,
  Infrastructure) has no corresponding documentation file, and the codebase
  shows no signals for that concern (no DB drivers, no auth middleware,
  no Dockerfiles, etc.).
- **Rationale**: Cross-cutting documentation should only exist for concerns
  the codebase actually implements. Absence of a `database.md` in a project
  with no database is correct behaviour, not a documentation gap. Only flag
  if codebase signals exist but the doc is missing.
