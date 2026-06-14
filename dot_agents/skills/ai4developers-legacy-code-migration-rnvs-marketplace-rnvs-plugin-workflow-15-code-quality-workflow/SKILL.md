---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-workflow-15-code-quality-workflow
description: Comprehensive methodology for Phase 15 code quality check and go-live approval. Generates quality reports covering security, testing, performance, and documentation. UNIFIED - works for both NEW and CHANGE modes with mode-aware scope.
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/workflow/skills/15-code-quality-workflow by codex-knowledge-curation/scripts/persist_project_skills.py. -->

<required_reading>
Read `results/${FEATURE}/.workflow-state.md` before any operation.
This provides workflow mode (NEW or CHANGE), completed phases, and session context.
Use Mode from state file instead of .workflow-state.md.
</required_reading>

# Code Quality Analysis Methodology

## Purpose

Provides comprehensive methodology for **Phase 15 code quality check and go-live approval** - the FINAL phase of the RNVS→VNRM migration workflow:

- **Security Assessment**: Vulnerability scanning, dependency checks, code security analysis
- **Code Quality Metrics**: Complexity, maintainability, duplication, technical debt
- **Test Coverage Analysis**: Unit tests, integration tests, pass rates
- **Performance Baseline**: Response times, throughput, error rates
- **Documentation Completeness**: Required docs verification
- **Go-Live Decision**: Scoring system and approval recommendation

**Key Principle**: Phase 15 is UNIFIED - works for both NEW and CHANGE modes. Only the SCOPE differs (all code vs changed code). Output always goes to `results/phase15/`.

## When to Use

Use this skill when you need to:

- **Perform Security Scans** - Identify vulnerabilities in generated/modified code
- **Analyze Code Quality** - Measure complexity, duplication, maintainability
- **Verify Test Coverage** - Ensure adequate test coverage (80%+ target)
- **Establish Performance Baseline** - Benchmark response times and throughput
- **Check Documentation** - Verify all required docs are complete
- **Make Go-Live Decision** - Score and approve/reject for deployment

**Phase Integration**: Used by `/rnvs-workflow:phase15-check-code-quality` command after Phase 14.

## Agent Guidance

When you are invoked to perform Phase 15 code quality check:

**Input Files**:
- `results/${FEATURE}/.workflow-state.md` - Workflow mode
- `results/${FEATURE}/phase14/test_scripts/` - Test scripts for execution

**Mode-Specific Inputs**:
- NEW mode: `results/${FEATURE}/phase13/source_code/` - All generated code
- CHANGE mode: `results/${FEATURE}/phase13.1/applied-edits-log.json` - Applied changes

**Your Task** (8 Stages):

### Stage 1: Determine Mode and Scope

1. Read `.workflow-state.md` to get `workflow_mode`
2. **NEW mode**:
   - Analyze Phase 13 source_code/ for all quality checks
   - Run security scans on complete codebase
3. **CHANGE mode**:
   - Read Phase 13.1 applied-edits-log.json
   - Focus quality checks on changed/new files only
   - Reference Phase 6 baseline for context

**Output for both modes**: `results/${FEATURE}/phase15/` (same location)

### Stage 2: Security Assessment

Perform comprehensive security analysis:

**Security Check Categories**:

| Category | Checks |
|----------|--------|
| Dependency Vulnerabilities | Maven dependencies, pip packages, known CVEs |
| Code Security Issues | SQL injection, XSS, hardcoded secrets, auth flaws |
| Configuration Security | Exposed data, insecure defaults, CORS issues |

**Pattern Searches**:
- `password|secret|api_key|token` - Hardcoded credentials
- `executeQuery|eval\(|exec\(` - Injection vulnerabilities
- `@Query.*\$\{|String\.format.*sql` - SQL injection patterns

**Output**: `results/${FEATURE}/phase15/security_findings.txt`

### Stage 3: Code Quality Analysis

Analyze code quality metrics:

**Quality Metrics**:

| Metric | Target | Description |
|--------|--------|-------------|
| Maintainability Index | >65 | Code maintainability score |
| Cyclomatic Complexity | <10 avg | Average function complexity |
| Code Duplication | <5% | Duplicate code percentage |
| Technical Debt | <8 hours | Estimated remediation time |

**Quality Checks**:
- Java: Checkstyle, PMD, SpotBugs patterns
- Python: Flake8, Pylint, Black patterns
- General: Comment coverage, naming conventions

**Output**: `results/${FEATURE}/phase15/quality_findings.txt`

### Stage 4: Test Coverage Analysis

Verify test coverage and pass rates:

**Coverage Targets**:

| Type | Target | Description |
|------|--------|-------------|
| Line Coverage | ≥80% | Lines executed by tests |
| Branch Coverage | ≥75% | Branches executed by tests |
| Pass Rate | ≥95% | Tests passing |

**Data Sources**:
- Phase 12: Unit test results
- Phase 14: Integration/system test results

**Output**: `results/${FEATURE}/phase15/test_results.txt`

### Stage 5: Performance Baseline

Establish performance baseline metrics:

**Performance Metrics**:

| Metric | Target | Description |
|--------|--------|-------------|
| Avg Response Time | <200ms | Average API response time |
| 95th Percentile | <500ms | 95% of requests under this time |
| Throughput | >100 req/s | Requests handled per second |
| Error Rate | <1% | Percentage of failed requests |

**Output**: `results/${FEATURE}/phase15/performance_baseline.txt`

### Stage 6: Documentation Completeness

Verify required documentation exists:

**Documentation Checklist**:
```
- [ ] Service README files
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Database schema documentation
- [ ] Deployment guide
- [ ] Configuration guide
- [ ] Test execution guide (Phase 14)
- [ ] Troubleshooting guide
- [ ] Architecture diagrams (Phase 8/8.1)
- [ ] Business logic documentation (Phases 3-5)
```

**Output**: `results/${FEATURE}/phase15/documentation_check.txt`

### Stage 7: Calculate Quality Score

Calculate comprehensive quality score (0-100):

**Scoring System**:

| Category | Points | Criteria |
|----------|--------|----------|
| **Security** | 25 | 0 critical: 25pts, 1-2 critical: 15pts, 3+: 0pts |
| **Code Quality** | 25 | No critical: 25pts, 1-5 critical: 15pts, 6+: 5pts |
| **Test Coverage** | 25 | ≥80%: 25pts, 70-79%: 15pts, <70%: 5pts |
| **Documentation** | 15 | All complete: 15pts, 80-99%: 10pts, <80%: 5pts |
| **Performance** | 10 | All SLAs met: 10pts, 80%+ SLAs: 5pts, <80%: 0pts |

**Go-Live Decision Matrix**:

| Score | Decision | Description |
|-------|----------|-------------|
| ≥85 | **APPROVED** | Ready for production deployment |
| 70-84 | **CONDITIONAL** | Deploy with documented conditions |
| <70 | **NOT APPROVED** | Requires remediation before deployment |

### Stage 8: Generate Quality Report

Create comprehensive quality report:

**Report Structure**:
```markdown
# Code Quality Report: ${FEATURE}

## Executive Summary
- Overall Quality Score: X/100
- Go-Live Readiness: Ready/Not Ready
- Critical Issues: X
- Blocker Issues: Y
- Recommendation: [Approve/Conditional/Reject]

## 1. Security Assessment
### 1.1 Security Scan Results
### 1.2 Security Findings
### 1.3 Security Recommendations

## 2. Code Quality Assessment
### 2.1 Code Quality Metrics
### 2.2 Quality Findings
### 2.3 Quality Recommendations

## 3. Test Results
### 3.1 Unit Test Results
### 3.2 Integration Test Results
### 3.3 Test Recommendations

## 4. Performance Assessment
### 4.1 Performance Metrics
### 4.2 Performance Baseline
### 4.3 Performance Recommendations

## 5. Documentation Assessment
### 5.1 Documentation Completeness
### 5.2 Documentation Quality

## 6. Deployment Readiness
### 6.1 Readiness Checklist
### 6.2 Blockers
### 6.3 Risks

## 7. Go-Live Decision
### 7.1 Recommendation
### 7.2 Justification
### 7.3 Conditions (if conditional)
### 7.4 Next Steps

## 8. Post-Go-Live Monitoring
### 8.1 Monitoring Plan
### 8.2 Support Plan
```

**Output**: `results/${FEATURE}/phase15/quality_report.md`

---

## Quick Reference

### Output Directory Structure

```
results/${FEATURE}/phase15/
├── security_findings.txt          # Security scan results
├── quality_findings.txt           # Code quality analysis
├── test_results.txt               # Test coverage and results
├── performance_baseline.txt       # Performance metrics
├── documentation_check.txt        # Documentation completeness
└── quality_report.md              # Comprehensive quality report
```

### Mode-Aware Scope

| Mode | Input Source | Scope | Output Location |
|------|--------------|-------|--------------------|
| **NEW** | Phase 13 source_code/ | All code | results/phase15/ |
| **CHANGE** | Phase 13.1 applied-edits-log.json | Changed code only | results/phase15/ |

### Quality Gates

| Gate | Target | Blocker? |
|------|--------|----------|
| Critical Security Vulnerabilities | 0 | Yes |
| High Security Vulnerabilities | ≤2 | Yes |
| Code Coverage | ≥80% | Yes |
| Test Pass Rate | ≥95% | Yes |
| Quality Score | ≥70 | Yes |

---

## Success Criteria

When using this skill, ensure:

- [ ] Workflow mode correctly determines scope (all vs changed)
- [ ] Security scan covers all relevant code
- [ ] Code quality metrics calculated accurately
- [ ] Test coverage meets 80% threshold
- [ ] Performance baseline established
- [ ] Documentation completeness verified
- [ ] Quality score calculated correctly
- [ ] Go-live decision is justified
- [ ] quality_report.md is comprehensive

---

## Related Skills

- **14-test-script-generation-workflow** - Phase 14 test scripts (input)
- **13-source-code-generation-workflow** - Phase 13.1 applied changes (CHANGE mode input)
- **code-generator** - Phase 13 source code (NEW mode input)

---

**This skill provides the complete methodology for the FINAL phase of the RNVS-VNRM migration workflow - quality check and go-live approval.**
