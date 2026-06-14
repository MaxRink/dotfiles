# BDD & TDD Documentation Reference

Traceability matrix, living documentation, and reporting.

## Part 1: Traceability Chain

Complete BR → FR → BDD → Unit Test → Implementation traceability.

### Traceability Levels

```text
Business Rule (BR-001)
    ↓
Functional Requirement (FR-001)
    ↓
├─ BDD Scenario (@BR-001 @FR-001)
│  └─ Step Definition → identifies EmailValidator
│      └─ Implementation: EmailValidator.validate()
│
└─ Unit Test (@DisplayName "BR-001: ...")
   └─ EmailValidatorTest
       └─ Implementation: EmailValidator.validate()
```

### Tagging Requirements

**BDD Feature Files:**

```gherkin
@BR-001 @FR-001 @auth @smoke
Scenario: Valid email should be accepted
```

**Unit Tests:**

```java
@Test
@DisplayName("BR-001: Valid email should pass validation")
void validEmailShouldPassValidation() { ... }
```

**Implementation:**

```java
/**
 * Validates email addresses according to BR-001.
 * @see BR-001 Email validation rules
 * @see FR-001 Email format validation
 */
@Component
public class EmailValidator { ... }
```

---

## Part 2: Traceability Matrix Generation

### Matrix Schema

```json
{
  "traceability_matrix": {
    "generated_at": "2026-04-13T11:00:00Z",
    "feature": "user-registration",
    "coverage": {
      "business_rules": {"total": 5, "covered": 5, "percentage": 100},
      "functional_requirements": {"total": 8, "covered": 8, "percentage": 100},
      "bdd_scenarios": {"total": 12, "passed": 12, "percentage": 100},
      "unit_tests": {"total": 45, "passed": 45, "percentage": 100}
    },
    "mappings": [
      {
        "br_id": "BR-001",
        "fr_ids": ["FR-001"],
        "bdd_scenarios": [
          {
            "feature": "features/auth/user-registration.feature",
            "scenario": "Valid email should be accepted",
            "status": "passed",
            "tags": ["@BR-001", "@FR-001", "@smoke"]
          }
        ],
        "unit_tests": [
          {
            "test_class": "EmailValidatorTest",
            "test_method": "validEmailShouldPassValidation",
            "status": "passed",
            "location": "src/test/java/.../EmailValidatorTest.java:15"
          }
        ],
        "implementation": [
          {
            "class": "EmailValidator",
            "method": "validate",
            "location": "src/main/java/.../EmailValidator.java:20"
          }
        ]
      }
    ]
  }
}
```

### Generation Algorithm

```text
1. Extract BR IDs from functional-requirements.md
2. For each BR ID:
   a. Find FR IDs from traceability matrix
   b. Parse .feature files for @BR-XXX tags
   c. Find unit tests with "BR-XXX" in @DisplayName
   d. Find implementation with @see BR-XXX in JavaDoc
3. Calculate coverage metrics:
   - BRs with scenarios / Total BRs
   - FRs with tests / Total FRs
   - Scenarios passing / Total scenarios
4. Generate JSON + HTML
```

### HTML Report Template

```html
<!DOCTYPE html>
<html>
<head>
    <title>Traceability Matrix</title>
    <style>
        .coverage-100 { background: #d4edda; color: #155724; }
        .passed { color: green; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; }
    </style>
</head>
<body>
    <h1>Traceability Matrix</h1>
    <section>
        <h2>Coverage Summary</h2>
        <table>
            <tr><th>Category</th><th>Total</th><th>Covered</th><th>%</th></tr>
            <tr class="coverage-100">
                <td>Business Rules</td><td>5</td><td>5</td><td>100%</td>
            </tr>
            <tr class="coverage-100">
                <td>BDD Scenarios</td><td>12</td><td>12</td><td>100%</td>
            </tr>
            <tr class="coverage-100">
                <td>Unit Tests</td><td>45</td><td>45</td><td>100%</td>
            </tr>
        </table>
    </section>

    <section>
        <h2>BR-001: Email Validation</h2>
        <h4>BDD Scenarios (2)</h4>
        <ul>
            <li class="passed">✓ Valid email should be accepted</li>
            <li class="passed">✓ Invalid email should be rejected</li>
        </ul>
        <h4>Unit Tests (2)</h4>
        <ul>
            <li class="passed">✓ EmailValidatorTest.validEmailShouldPassValidation</li>
            <li class="passed">✓ EmailValidatorTest.invalidEmailShouldFailValidation</li>
        </ul>
        <h4>Implementation (1)</h4>
        <ul>
            <li>EmailValidator.validate() - src/main/java/.../EmailValidator.java:20</li>
        </ul>
    </section>
</body>
</html>
```

---

## Part 3: Living Documentation

Auto-generated, always up-to-date documentation from BDD scenarios.

### Setup BDD Reporting

**Java (Maven):**

```xml
<dependency>
    <groupId>net.masterthought</groupId>
    <artifactId>maven-cucumber-reporting</artifactId>
    <version>5.7.7</version>
</dependency>

<plugin>
    <groupId>net.masterthought</groupId>
    <artifactId>maven-cucumber-reporting</artifactId>
    <executions>
        <execution>
            <phase>verify</phase>
            <goals><goal>generate</goal></goals>
            <configuration>
                <projectName>${project.name}</projectName>
                <outputDirectory>${project.build.directory}/cucumber-reports</outputDirectory>
                <inputDirectory>${project.build.directory}/cucumber-reports</inputDirectory>
                <jsonFiles><param>**/*.json</param></jsonFiles>
            </configuration>
        </execution>
    </executions>
</plugin>
```

**Python (behave):**

```bash
# Generate HTML report
behave -f html -o reports/behave-report.html

# Generate JSON + HTML
behave -f html -o reports/report.html -f json -o reports/report.json
```

**Python (pytest-bdd):**

```bash
# With pytest-html
pytest tests/bdd/ --html=reports/bdd-report.html --self-contained-html

# With Allure
pytest tests/bdd/ --alluredir=reports/allure-results
allure serve reports/allure-results
```

### Living Documentation Dashboard

```html
<!DOCTYPE html>
<html>
<head>
    <title>Living Documentation</title>
    <style>
        body { font-family: -apple-system, sans-serif; background: #f5f5f5; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
        .metric-card { background: white; padding: 20px; border-radius: 8px; }
        .metric-value { font-size: 36px; font-weight: bold; color: #4caf50; }
        .nav-links a { padding: 10px 20px; background: #2196f3; color: white; text-decoration: none; }
    </style>
</head>
<body>
    <header>
        <h1>📚 Living Documentation</h1>
        <p>User Registration - Generated 2026-04-13 11:06:30</p>
    </header>

    <div class="metrics">
        <div class="metric-card">
            <div class="metric-label">BDD Scenarios</div>
            <div class="metric-value">12/12</div>
            <div class="metric-label">100% Passing</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Unit Tests</div>
            <div class="metric-value">45/45</div>
            <div class="metric-label">100% Passing</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Code Coverage</div>
            <div class="metric-value">87%</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Requirements</div>
            <div class="metric-value">8/8</div>
            <div class="metric-label">100% Traced</div>
        </div>
    </div>

    <div class="nav-links">
        <a href="bdd-reports/features.html">🎭 BDD Scenarios</a>
        <a href="traceability-matrix.html">🔗 Traceability Matrix</a>
        <a href="../target/site/jacoco/index.html">📊 Code Coverage</a>
    </div>
</body>
</html>
```

---

## Part 4: CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Generate Living Documentation

on:
  push:
    branches: [main, develop]

jobs:
  documentation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Java
        uses: actions/setup-java@v3
        with:
          java-version: '17'

      - name: Run BDD Tests
        run: mvn verify

      - name: Generate Cucumber Reports
        run: mvn cucumber-reporting:generate

      - name: Generate Traceability Matrix
        run: |
          python scripts/generate-traceability-matrix.py \
            --cucumber target/cucumber-reports/cucumber.json \
            --output docs/traceability/matrix.html

      - name: Generate Living Documentation Dashboard
        run: |
          python scripts/generate-documentation-dashboard.py \
            --output docs/index.html

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
```

---

## Part 5: Documentation Output Structure

```text
.migration/<feature>/code-generation/
├── living-documentation.html       # Main dashboard
├── traceability-matrix.json        # Machine-readable
├── traceability-matrix.html        # Human-readable
└── bdd-report.html                 # BDD test results

target/                              # Java
├── cucumber-reports/
│   └── cucumber-html-reports/
└── site/jacoco/                     # Coverage

htmlcov/                             # Python
reports/
├── behave-report.html
└── coverage.html
```

---

## Part 6: Quality Gates

### After Step 4 (Tests)

- [ ] All BDD scenarios have @BR tags
- [ ] All BDD scenarios have step definitions
- [ ] All unit tests reference BR in @DisplayName
- [ ] All tests verified RED
- [ ] No production code exists

### After Step 5 (Core)

- [ ] All unit tests GREEN
- [ ] All BDD scenarios GREEN
- [ ] Implementation has BR documentation
- [ ] No regressions

### After Step 8 (Completion)

- [ ] 100% BR coverage
- [ ] 100% FR coverage
- [ ] Traceability matrix generated
- [ ] Living documentation generated
- [ ] All tests passing
- [ ] No orphaned scenarios
- [ ] No untested requirements

---

## Part 7: Metrics & Reporting

### Coverage Metrics

```json
{
  "metrics": {
    "business_rules_coverage": 100,
    "functional_requirements_coverage": 100,
    "bdd_scenarios": {
      "total": 12,
      "passed": 12,
      "failed": 0,
      "percentage": 100
    },
    "unit_tests": {
      "total": 45,
      "passed": 45,
      "failed": 0,
      "percentage": 100
    },
    "code_coverage": {
      "line_coverage": 87,
      "branch_coverage": 82
    }
  }
}
```

### Impact Analysis

Shows what tests/code are affected by a requirement change:

```text
IMPACT ANALYSIS: BR-001

If BR-001 changes, the following will be affected:

BDD Scenarios (2):
  • features/auth/user-registration.feature:10
  • features/auth/user-registration.feature:16

Unit Tests (2):
  • EmailValidatorTest.validEmailShouldPassValidation
  • EmailValidatorTest.invalidEmailShouldFailValidation

Implementation (1):
  • EmailValidator.validate()

RECOMMENDATION: Re-run all 4 tests after modifying EmailValidator
```

---

## Part 8: Commands Reference

### Generate Reports

**Java:**

```bash
mvn verify                                    # All tests + reports
mvn cucumber-reporting:generate              # BDD report only
open target/cucumber-reports/cucumber-html-reports/overview-features.html
open target/site/jacoco/index.html           # Coverage
```

**Python:**

```bash
# BDD reports
behave -f html -o reports/bdd-report.html
pytest tests/bdd/ --html=reports/bdd-report.html

# Coverage
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

### Generate Traceability Matrix

```bash
# Custom script (example)
python scripts/generate-traceability-matrix.py \
  --spec .migration/<feature>/spec-specification/functional-requirements.md \
  --features features/ \
  --tests src/test/java/ \
  --output .migration/<feature>/code-generation/traceability-matrix.html
```

### Validation Checks

```bash
# Verify all BDD scenarios have @BR tags
grep -r "@BR-" features/ | wc -l

# Count scenarios vs BR IDs
grep "Scenario" features/ | wc -l

# Verify no orphaned scenarios (missing @BR tag)
find features/ -name "*.feature" -exec grep -L "@BR-" {} \;
```

---

## Quick Reference

**Traceability Chain:**

```text
BR → FR → BDD Scenario (@tags) → Unit Test (@DisplayName) → Implementation (@see)
```

**Quality Gates:**

```text
Step 4: All tests RED, @BR tags present
Step 5: All tests GREEN, @see BR in code
Step 8: Traceability matrix 100%, living docs generated
```

**Reports Generated:**

```text
- traceability-matrix.html (BR → Test → Code mapping)
- living-documentation.html (Dashboard with metrics)
- bdd-report.html (Cucumber/behave scenarios)
- coverage report (JaCoCo/pytest-cov)
```
