# Step 4 — Tests (BDD → TDD → All RED)

Write all test files and verify they fail before implementation exists.

## Overview

**BDD (What) → TDD (How) → Verify RED**

Phases:

1. **4a**: BDD scenarios (business acceptance)
2. **4b**: BDD step definitions (identify components)
3. **4c**: Unit tests (component tests)
4. **4d**: Verify all RED

**Rules:**

- NO production code (src/main/, src/app/)
- BDD defines WHAT → identifies components
- Unit tests define HOW → test components
- All tests must fail (RED)

## Prerequisites

**PRE-FLIGHT:** Verify ALL Setup tasks `passed` in tasks.json

**Load references:**

- `bdd-tdd-workflow.md` (BDD scenarios, step definitions, unit tests)
- Language skill: `testing.md`, `fundamentals.md`

---

## Phase 4a: BDD Scenarios (Define WHAT)

Extract from functional-requirements.md → Create .feature files with traceability tags.

```gherkin
# features/auth/user-registration.feature

@BR-001 @FR-001 @auth @smoke
Feature: User Registration - Email Validation
  As a system administrator
  I want to validate user email addresses
  So that only users with valid emails can register

  Background:
    Given the email validation service is available

  @BR-001 @FR-001 @auth @smoke
  Scenario: Valid email should be accepted
    Given a new user registration form
    When I submit with email "user@example.com"
    Then the email should be accepted

  @BR-001 @FR-001 @auth @edge-case
  Scenario Outline: Invalid email formats should be rejected
    Given a new user registration form
    When I submit with email "<email>"
    Then I should see error "Invalid email format"

    Examples:
      | email           |
      | invalid         |
      | @example.com    |
      | user@           |
```

**Run:** `mvn test -Dtest=CucumberRunnerIT` or `behave features/...` → **Expected:** UNDEFINED ✓ RED

---

## Phase 4b: BDD Step Definitions (Identify Components)

Generate test code for scenarios. Step definitions reveal needed components.

```java
// features/auth/steps/UserRegistrationSteps.java
// Use @Autowired (Spring) or @Inject (Quarkus)

@Inject  // or @Autowired
EmailValidator emailValidator;

@When("I submit with email {string}")
public void iSubmitWithEmail(String email) {
    result = emailValidator.validate(email);  // ← Identifies EmailValidator component
}

@Then("the email should be accepted")
public void theEmailShouldBeAccepted() {
    assertThat(result.isValid()).isTrue();    // ← Identifies ValidationResult.isValid()
}
```

**Python:**

```python
# features/auth/steps/registration_steps.py (behave)
# or tests/bdd/test_user_registration.py (pytest-bdd)

@when('I submit with email "{email}"')
def step_impl(context, email):
    validator = EmailValidator()              # ← Identifies EmailValidator component
    context.result = validator.validate(email)

@then('the email should be accepted')
def step_impl(context):
    assert context.result.is_valid is True    # ← Identifies ValidationResult.is_valid
```

**Components identified:** EmailValidator, ValidationResult, RegistrationRequest → These become Phase 4c targets.

**Run:** `mvn test` or `behave` → **Expected:** FAILURE (components don't exist) ✓ RED

---

## Phase 4c: Unit Tests (Test Components)

Write unit tests for components identified in Phase 4b.

```java
// src/test/java/.../EmailValidatorTest.java
/**
 * Derived from BDD: features/auth/user-registration.feature
 * Traces to: BR-001, FR-001
 */
@Test
@DisplayName("BR-001: Valid email should pass validation")
void validEmailShouldPassValidation() {
    ValidationResult result = validator.validate("user@example.com");
    assertThat(result.isValid()).isTrue();  // Component doesn't exist yet → RED
}
```

**Python:**

```python
# tests/unit/test_email_validator.py
def test_valid_email_should_pass(validator):
    """BR-001: Derived from BDD scenario"""
    result = validator.validate("user@example.com")
    assert result.is_valid is True  # Component doesn't exist yet → RED
```

**Run:** `mvn test -Dtest=EmailValidatorTest` or `pytest tests/unit/` → **Expected:** FAILURE ✓ RED

---

## Phase 4d: Verify All RED

**Run:** `mvn test` or `pytest tests/` → **Expected:** All RED (BDD UNDEFINED, Unit FAIL)

**Verify no production code:**

```bash
find src/main/java -name "*.java" -not -name "Application.java" | wc -l  # Expected: 0
```

**CRITICAL:** If any test PASSES or production code exists → HALT, fix, re-run.

**Update tasks.json:**

```json
{
  "task.status": "passed",
  "bdd_scenarios_written": 7,
  "unit_tests_written": 15,
  "all_verified_red": true,
  "no_production_code": true
}
```

---

## Checkpoint & Progress

**Batch checkpoint:**

```json
{
  "verification_type": "red",
  "bdd_scenarios": 2, "unit_tests": 3,
  "all_red": true, "no_production_code": true,
  "components_identified": ["EmailValidator", "ValidationResult"]
}
```

**Progress:** `[Step 4/8] Tests - Batch 2/3 ✓ | 2 BDD + 3 Unit = 5 RED ✓ | Next: Step 5`

---

## Step 4 Complete Summary

**Artifacts:** 7 BDD scenarios, 3 step files, 15 unit tests (all RED ✓)
**Components identified:** EmailValidator, PasswordValidator, UserService, UserController, ValidationResult
**Verified:** No production code exists → Ready for Step 5 (Implementation)

---

## Common Pitfalls

| Anti-Pattern | Fix |
|-------------|-----|
| Write implementation in Step 4 | Only tests in Step 4, code in Step 5 |
| Unit tests before BDD | BDD first (WHAT) → TDD (HOW) |
| Skip RED verification | Always run and verify RED |
| No assertions | Every test needs assertThat/assert |
| Over-mocking | Mock external deps only |
| Random unit tests | Derive from BDD components |

See `testing-anti-patterns.md` for details.
