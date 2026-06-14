# Code Review Concern Templates

> Produce only sections relevant to what was found.
> Skip any section where grep found no matches and no issues were identified.
> Every finding must cite `file:line`.

---

## Template 1: quality-findings.md

### Grep patterns to run first

```text
Grep: "TODO|FIXME|HACK|XXX"                    glob: all source files
Grep: "\b[0-9]{2,}\b"                          glob: all source files  (magic numbers — exclude test fixtures)
Grep: "^\s{16,}"                               glob: *.{js,ts,py,java,cs}  (deep nesting ≥ 4 levels)
Grep: "console\.log|System\.out\.print|print\(" glob: src/**/*  (debug output left in)
Grep: "pass$"                                  glob: **/*.py  (empty function bodies)
```

For tier `small`: read all source files fully after grep.
For tier `medium`/`large`: read only files with grep matches + entry-point files.

### Checklist

- Naming: descriptive variables/functions/classes, no abbreviations, UPPER_CASE constants
- Functions: single responsibility, < 50 lines, clear I/O, minimal side effects
- Classes: SOLID principles (SRP, OCP, LSP, ISP, DIP)
- Error handling: all errors caught, meaningful messages, no silent failures
- Code quality: no DRY violations, no dead code, no magic numbers, consistent formatting

### Output structure

```markdown
# Quality Findings

## Critical
- **[file:line]** <finding>
  Remediation: <specific fix>

## Warning
- **[file:line]** <finding>
  Remediation: <specific fix>

## Minor
- **[file:line]** <finding>
  Remediation: <specific fix>

## Checklist
| Check | Result |
|-------|--------|
| Naming conventions | PASS / FAIL |
| Function length (< 50 lines) | PASS / FAIL |
| Single responsibility | PASS / FAIL |
| Error handling | PASS / FAIL |
| No dead code | PASS / FAIL |
| No magic numbers | PASS / FAIL |
| DRY — no duplication | PASS / FAIL |
```

---

## Template 2: security-findings.md

### Grep patterns to run first

> Use `extension_inventory` to skip patterns whose glob targets an extension not present in the codebase (e.g. skip JS XSS patterns if no `.js`/`.ts` files exist).

```text
# XSS
Grep: "innerHTML\s*="                                                  glob: **/*.{js,ts,jsx,tsx,html}
Grep: "document\.write\("                                              glob: **/*.{js,ts,jsx,tsx}
Grep: "eval\("                                                         glob: **/*.{js,ts,jsx,tsx,py}
Grep: "dangerouslySetInnerHTML"                                        glob: **/*.{jsx,tsx}

# SQL injection
Grep: "f['\"].*SELECT|f['\"].*INSERT|f['\"].*UPDATE|f['\"].*DELETE"   glob: **/*.py
Grep: "\"SELECT.*\+|'SELECT.*\+"                                       glob: **/*.{java,cs,js,ts}
Grep: "execute\([^)]*%[sd]"                                            glob: **/*.py
Grep: "string\.Format.*SELECT"                                         glob: **/*.cs

# Hardcoded secrets (case-insensitive)
Grep: "(password|passwd|secret|api_key|apikey|token)\s*=\s*['\"][^'\"]{6,}"  glob: **/*
Grep: "sk-[a-zA-Z0-9]{20,}"                                           glob: **/*
Grep: "BEGIN (RSA|EC|OPENSSH) PRIVATE KEY"                            glob: **/*

# Code injection
Grep: "exec\(|subprocess\.call\(|os\.system\("                        glob: **/*.py
Grep: "Runtime\.exec\("                                                glob: **/*.java
```

### Checklist

- No hardcoded secrets or credentials
- SQL injection prevention (parameterised queries)
- XSS prevention (no raw HTML injection)
- Input validation at all entry points
- Proper authentication and authorization checks
- No vulnerable dependency versions (check manifest files)

### Output structure

```markdown
# Security Findings

## Critical
- **[file:line]** <finding>
  Remediation: <specific fix>

## Warning
- **[file:line]** <finding>
  Remediation: <specific fix>

## Minor
- **[file:line]** <finding>
  Remediation: <specific fix>

## Checklist
| Check | Result |
|-------|--------|
| No hardcoded secrets | PASS / FAIL |
| SQL injection prevention | PASS / FAIL |
| XSS prevention | PASS / FAIL |
| Input validation | PASS / FAIL |
| Authentication checks | PASS / FAIL |
| Authorization checks | PASS / FAIL |
```

---

## Template 3: performance-findings.md

### Grep patterns to run first

> Use `extension_inventory` to skip patterns whose glob targets an extension not present in the codebase (e.g. skip async JS patterns if no `.js`/`.ts` files exist).

```text
# N+1 query patterns
Grep: "\.forEach.*await"                         glob: **/*.{js,ts}
Grep: "for.*in.*await"                           glob: **/*.{js,ts}
Grep: "for.*\n.*\.(find|query|filter|fetch)\("   glob: **/*.{py,rb}  (multiline)

# Over-fetching
Grep: "SELECT \*"                                glob: **/*
Grep: "\.find\(\)|\.findAll\(\)|\.all\(\)"       glob: **/*.{java,py,js,ts,rb}

# Blocking I/O in async context
Grep: "readFileSync|writeFileSync|execSync"      glob: **/*.{js,ts}
Grep: "time\.sleep|Thread\.sleep"               glob: **/*.{py,java}

# Resource leaks
Grep: "new.*Connection\(|\.open\("              glob: **/*  (verify corresponding close exists)

# Unbounded loops
Grep: "while True:|while \(true\)"              glob: **/*
```

### Checklist

- No N+1 query patterns
- No SELECT * (over-fetching)
- No blocking synchronous I/O in async contexts
- Connections and file handles closed properly
- No unbounded loops without exit conditions
- Caching used where appropriate

### Output structure

```markdown
# Performance Findings

## Critical
(performance issues are rarely critical — use only for confirmed infinite loops or guaranteed OOM)

## Warning
- **[file:line]** <finding>
  Remediation: <specific fix>

## Minor
- **[file:line]** <finding>
  Remediation: <specific fix>

## Checklist
| Check | Result |
|-------|--------|
| No N+1 queries | PASS / FAIL |
| No SELECT * | PASS / FAIL |
| No blocking synchronous I/O (in async context) | PASS / FAIL |
| Connection / resource management | PASS / FAIL |
| No unbounded loops | PASS / FAIL |
```

---

## Template 4: testing-findings.md

### Grep patterns to run first

```text
# Find test files (Glob, not Grep)
Glob: .migration/<feature>/code-generation/tests/**/*
Glob: .migration/<feature>/code-generation/**/*test*
Glob: .migration/<feature>/code-generation/**/*spec*
Glob: .migration/<feature>/code-generation/features/**/*  (BDD)

# Test anti-patterns
Grep: "time\.sleep|setTimeout.*[0-9]{3,}"   glob: **/test*  (flaky timing dependencies)
Grep: "assert True$|assertTrue\(True"       glob: **/*      (trivial/always-pass assertions)
Grep: "^\s*pass$"                           glob: **/*.py   (empty test bodies)
Grep: "TODO|FIXME"                          glob: **/test*  (incomplete tests)
Grep: "\.only\(|\.skip\("                  glob: **/*.{js,ts}  (focused / skipped tests)
```

If no test files are found at all → record as `critical`.
Compare test file count vs source file count — if ratio < 0.5, note as `warning`.

### Checklist

- Test files present for all source modules
- Unit tests cover public interfaces
- Edge cases and error paths tested
- No flaky timing dependencies (`time.sleep`, `setTimeout` in tests)
- No trivial or empty test bodies
- Tests are readable and well-named
- No focused (`.only`) or permanently skipped tests left in

### Output structure

```markdown
# Testing Findings

## Critical
- **[finding]** No test files found under code-generation/tests/
  Remediation: Add unit tests covering all public interfaces

## Warning
- **[file:line]** <finding>
  Remediation: <specific fix>

## Minor
- **[file:line]** <finding>
  Remediation: <specific fix>

## Checklist
| Check | Result |
|-------|--------|
| Test files present | PASS / FAIL |
| Unit tests for all source files | PASS / FAIL |
| Edge cases covered | PASS / FAIL |
| Error cases tested | PASS / FAIL |
| No flaky timing dependencies | PASS / FAIL |
| Tests readable and well-named | PASS / FAIL |
| No empty / trivial test bodies | PASS / FAIL |
```
