# Audit-Explore Validation Checklist

These are the 9 checks to run against deep-explore output. Execute them in order. Each check has explicit pass/fail criteria.

---

## Check 1: Structural Validation

**What**: Verify `index.json` exists, is valid JSON, and has all required fields.

**Steps**:

1. Read `.migration/docs/index.json`
2. Parse as JSON — must not throw
3. Verify required top-level fields exist: `repository`, `scan`, `output_files`
4. Verify `repository` has `path` and `name`
5. Verify `scan` has `timestamp`, `filesScanned`, `directoriesScanned`
6. Verify `output_files` is a non-empty array
7. Verify each entry in `output_files` has `path` and `description`

**Pass criteria**: All required fields present and correctly typed.

**Fail severity**: `critical` — the manifest is the entry point for all consumers.

---

## Check 2: File Existence

**What**: Every file listed in `output_files` must exist on disk.

**Steps**:

1. Read the `output_files` array from `index.json`
2. For each entry, use Glob to verify the file exists at `.migration/docs/<path>`
3. Record any missing files

**Pass criteria**: Every listed file exists on disk.

**Fail severity**: `critical` — missing files mean broken references for consumers.

---

## Check 3: Directory Compliance

**What**: All documentation files must live in the correct subdirectory. Only `index.json` (and
`audit-report.md`) should be at the root of `.migration/docs/`. Everything else must be in
`overview/`, `modules/`, or `cross-cutting/`.

**Steps**:

1. Glob `.migration/docs/*` (non-recursive, root level only)
2. Filter out `index.json` and `audit-report.md`
3. Any remaining files at root level are violations (directories like `overview/` are fine)

**Pass criteria**: No unexpected files at `.migration/docs/` root level.

**Fail severity**: `warning` — misplaced files don't break consumers but violate the spec.

---

## Check 4: file_index Completeness

**What**: The `file_index` field must be present, non-empty, and its patterns must actually cover
the codebase files comprehensively.

**Steps**:

**4a — Presence**:

1. Check that `file_index` key exists in the parsed `index.json`
2. Check that it is an object (not null, not an array)
3. Check that it has at least one key

**4b — Extension coverage**:

1. Scan the actual repository to discover all file extensions present (use Glob for common
   extensions)
2. For each extension with more than 5 files, verify at least one file_index pattern covers it
3. Flag any extension category with >5 files that has zero matching patterns:

   - Source code: `.cpp`, `.hpp`, `.h`, `.c`, `.java`, `.py`, `.js`, `.ts`, `.go`, `.rs`,
     `.rb`, `.groovy`, `.kt`, `.scala`, `.cs`
   - Scripts: `.sh`, `.bash`, `.tcl`, `.pl`, `.ksh`
   - Schema/contracts: `.idl`, `.proto`, `.wsdl`, `.xsd`, `.graphql`
   - Config: `.xml`, `.properties`, `.yaml`, `.yml`, `.json`, `.cfg`, `.conf`, `.toml`
   - Database: `.sql`, `.pc`
   - Build: `.mk`, `.gradle`, `.cmake`, `pom.xml`, `build.xml`

**4c — Directory coverage**:

1. List all top-level directories in the repository
2. For each directory that contains source or script files, verify at least one file_index
   pattern maps into it
3. Flag any source-containing directory completely absent from the file_index

**4d — Coverage ratio**:

1. Estimate total files matched by all file_index patterns (use Glob to test each pattern
   against the repo)
2. Compare against `scan.sourceFilesScanned` (or total source + supporting file count)
3. Calculate coverage percentage

**Pass criteria**:

- `file_index` exists as a non-empty object (4a)
- No file extension with >5 files is completely uncovered (4b)
- No source-containing directory is completely absent (4c)
- Coverage ratio is ≥ 90% of source files (4d)

**Fail severity**:

- 4a failing: `critical` — `file_index` is required by the spec for all tiers
- 4b failing: `critical` — missing extension categories mean entire file types are invisible to
  consumers
- 4c failing: `critical` — missing directories mean entire subsystems are invisible
- 4d coverage < 90%: `warning` — some files uncovered but majority present
- 4d coverage < 75%: `critical` — significant portion of codebase not indexed

**Evidence to record**: List of uncovered extensions with file counts, uncovered directories, and
the coverage ratio.

---

## Check 5: Quality Score Recalculation

**What**: Independently recalculate the quality score from the raw `metadata.coverage` numbers
and compare against the declared `metadata.quality_score`.

**Steps**:

1. Read `metadata.coverage` from `index.json`
2. Read `metadata.quality_score` from `index.json`
3. If `metadata` or `coverage` is missing → FAIL (critical: required field missing)
4. Recalculate using the formula:

```text
files_score     = (files_documented / files_total) × 25
modules_score   = (modules_documented / modules_detected) × 25
apis_score      = (apis_documented / apis_detected) × 20
models_score    = (models_documented / models_detected) × 15
xcut_score      = (cross_cutting_produced / cross_cutting_applicable) × 15

total = round(files_score + modules_score + apis_score + models_score + xcut_score)
```

1. If any denominator is 0, that criterion scores its full points (100% coverage assumed)
2. Compare `total` with declared `quality_score`
3. If the absolute difference is > 2 points → FAIL

**Pass criteria**: Declared quality score is within 2 points of the recalculated value.

**Fail severity**: `critical` — inflated scores mislead consumers about documentation completeness.

**Evidence to record**: Declared score, recalculated score, per-criterion breakdown.

---

## Check 6: Cross-Cutting Coverage

**What**: Verify that cross-cutting documentation exists for concerns actually present in the
codebase.

**Steps**:

For each concern below, check if it's present in the codebase, then verify the corresponding doc
exists:

| Concern | Codebase signal (use Grep/Glob) | Expected doc |
|---------|-------------------------------|--------------|
| APIs | Grep for route decorators, endpoint definitions, controller classes, `@Get`, `@Post`, `@RequestMapping`, `router.get`, `app.get`, `@api_view`, CORBA IDL files, WSDL/SOAP definitions | `cross-cutting/api-contracts.md` |
| Database | Grep for migration files, schema definitions, `CREATE TABLE`, ORM models, `@Entity`, `@Table`, `.schema` | `cross-cutting/database-schema.md` |
| Security | Grep for auth middleware, `@Authenticated`, JWT handling, CORS config, security headers, `passport`, `bcrypt`, `@PreAuthorize` | `cross-cutting/security.md` |
| Testing | Glob for test files (`**/*.test.*`, `**/*.spec.*`, `**/test_*.py`, `**/*_test.go`) | `cross-cutting/testing.md` |
| Infrastructure | Glob for `Dockerfile`, `docker-compose*`, `*.tf`, `k8s/`, `kubernetes/`, `.github/workflows/*`, `.gitlab-ci.yml` | `cross-cutting/infrastructure.md` |

**For each concern**:

1. Search the codebase for the signals listed above
2. If signals are found → check that the corresponding doc exists in `output_files` and on disk
3. If signals are found but the doc is missing → record as FAIL for that concern

**Pass criteria**: Every applicable cross-cutting concern has its corresponding doc.

**Fail severity**: `warning` — missing cross-cutting docs reduce completeness but don't break the
manifest.

---

## Check 7: Evidence Spot-Check

**What**: Verify that file:line references in module documentation actually exist in source code.

**Steps**:

1. List all module docs from `output_files` (paths matching `modules/*.md`)
2. Pick up to 3 module docs at random (or all if fewer than 3 exist)
3. For each selected module doc:

   - a. Read the file
   - b. Extract file:line references (pattern: backtick or plain text matching
     `<path>:<lineNumber>`)
   - c. Pick up to 2 references at random
   - d. For each reference, use Read to verify the file exists and the line number is within
     range
   - e. Optionally verify the content at that line is relevant to the claim (not a blank line
     or comment unrelated to the documented item)

4. Record any stale or broken references

**Pass criteria**: All sampled references point to existing files with valid line numbers.

**Fail severity**: `warning` — stale references degrade trust but don't break the structural
contract.

**Evidence to record**: Which references were checked, which passed, which failed (with expected
vs actual).

---

## Check 8: Module Template Adherence

**What**: Every module doc must have at minimum three required sections: **Overview**,
**Components**, **Dependencies**.

**Steps**:

1. List all module docs from `output_files` (paths matching `modules/*.md`)
2. For each module doc:

   - a. Read the file
   - b. Search for `## Overview` (or `# Module:` followed by `## Overview`)
   - c. Search for `## Components`
   - d. Search for `## Dependencies`
   - e. Record any missing required sections

**Pass criteria**: Every module doc contains all three required section headers.

**Fail severity**: `warning` — missing template sections reduce documentation consistency.

**Evidence to record**: Which module docs were checked, which sections are missing from which
docs.

---

## Check 9: Coverage Accuracy

**What**: Verify that the declared `metadata.coverage` numbers are accurate — not inflated or
fabricated. The raw coverage numbers drive the quality score, so if they're wrong, the score is
meaningless.

**Steps**:

**9a — files_documented vs file_index**:

1. Count the actual files matched by file_index patterns (from Check 4d)
2. Compare against `coverage.files_documented`
3. If the declared number exceeds the actual matched count by more than 10% → FAIL

**9b — files_total vs scan**:

1. Compare `coverage.files_total` against `scan.sourceFilesScanned`
2. They should be consistent — if `files_total` is significantly lower than
   `sourceFilesScanned`, the denominator was deflated to inflate the coverage ratio

**9c — modules count**:

1. Count module docs in `output_files` (paths matching `modules/*.md`)
2. Compare against `coverage.modules_documented`
3. Count module entries in `modules` array of `index.json`
4. Compare against `coverage.modules_detected`
5. Both should match exactly

**9d — cross_cutting count**:

1. Count cross-cutting docs in `output_files` (paths matching `cross-cutting/*.md`)
2. Compare against `coverage.cross_cutting_produced`
3. Compare `coverage.cross_cutting_applicable` against the actual codebase signals from Check 6

**9e — APIs and models (spot-check)**:

1. Pick 2–3 module docs, count the API endpoints and data models actually documented in them
2. Extrapolate roughly and compare against `coverage.apis_documented` and
   `coverage.models_documented`
3. Flag if the declared count seems implausibly high relative to what's actually in the docs

**Pass criteria**:

- files_documented within 10% of actual file_index matches (9a)
- files_total consistent with scan.sourceFilesScanned (9b)
- Module counts match exactly (9c)
- Cross-cutting counts match exactly (9d)
- API/model counts are plausible (9e)

**Fail severity**:

- 9a inflated by >10%: `critical` — quality score is based on fabricated numbers
- 9b deflated denominator: `critical` — quality score is artificially inflated
- 9c/9d mismatch: `warning` — bookkeeping error
- 9e implausible: `warning` — suggests estimation rather than actual counting

**Evidence to record**: Declared vs actual for each metric, with the discrepancy percentage.
