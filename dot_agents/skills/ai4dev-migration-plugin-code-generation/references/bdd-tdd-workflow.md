# BDD & TDD Workflow Reference

Complete guide for BDD scenarios, step definitions, unit tests, and TDD loop.

## Quick Reference

**Flow:** BDD (What) → TDD (How) → Code → Verify

**Step 4:** Write tests (BDD scenarios → step definitions → unit tests) → All RED
**Step 5:** Write implementation (TDD loop) → All GREEN

---

## Part 1: BDD Feature Files (Gherkin)

### Template Structure

```gherkin
@BR-XXX @FR-XXX @domain @smoke
Feature: {Feature Name}
  As a {role}
  I want {capability}
  So that {benefit}

  Background:
    Given {common setup}

  @BR-XXX @FR-XXX @domain @smoke
  Scenario: {Happy path}
    Given {precondition}
    When {action}
    Then {expected result}
    And {additional verification}

  @BR-XXX @FR-XXX @domain @edge-case
  Scenario Outline: {Edge cases}
    Given {precondition}
    When {action with <parameter>}
    Then {expected result}

    Examples:
      | parameter | expected |
      | value1    | result1  |
      | value2    | result2  |
```

### Required Tags

Every scenario MUST have:

- `@BR-XXX` - Business Rule ID (traceability)
- `@FR-XXX` - Functional Requirement ID (traceability)
- `@domain` - Business domain (auth, payment, order, etc.)
- Optional: `@smoke`, `@edge-case`, `@integration`

### Example: Email Validation

```gherkin
@BR-001 @FR-001 @auth @smoke
Feature: User Registration - Email Validation

  @BR-001 @FR-001 @auth @smoke
  Scenario: Valid email should be accepted
    Given a new user registration form
    When I submit with email "user@example.com"
    Then the email should be accepted

  @BR-001 @FR-001 @auth @edge-case
  Scenario Outline: Invalid email formats rejected
    Given a new user registration form
    When I submit with email "<email>"
    Then I should see error "Invalid email format"

    Examples:
      | email        |
      | invalid      |
      | @example.com |
      | user@        |
```

---

## Part 2: BDD Step Definitions

Step definitions reveal what components to build.

### Java (Cucumber)

**Spring Boot:**

```java
@CucumberContextConfiguration
@SpringBootTest
public class UserRegistrationSteps {
    @Autowired
    private EmailValidator emailValidator;  // Component identified

    private ValidationResult result;

    @When("I submit with email {string}")
    public void iSubmitWithEmail(String email) {
        result = emailValidator.validate(email);  // → EmailValidator needed
    }

    @Then("the email should be accepted")
    public void theEmailShouldBeAccepted() {
        assertThat(result.isValid()).isTrue();    // → ValidationResult needed
    }
}
```

**Quarkus:**

```java
public class UserRegistrationSteps {
    @Inject
    EmailValidator emailValidator;

    // Same step methods as Spring Boot
}
```

**Cucumber Runner:**

```java
@Suite
@IncludeEngines("cucumber")
@SelectClasspathResource("features")
@ConfigurationParameter(key = Constants.GLUE_PROPERTY_NAME, value = "com.example.features")
@ConfigurationParameter(key = Constants.FILTER_TAGS_PROPERTY_NAME, value = "not @wip")
@ConfigurationParameter(key = Constants.PLUGIN_PROPERTY_NAME,
    value = "pretty, html:target/cucumber-reports/cucumber.html, json:target/cucumber-reports/cucumber.json")
public class CucumberRunnerIT {}
```

### Python (behave)

```python
# features/auth/steps/registration_steps.py
from behave import given, when, then
from app.validators import EmailValidator

@when('I submit with email "{email}"')
def step_impl(context, email):
    validator = EmailValidator()              # Component identified
    context.result = validator.validate(email)

@then('the email should be accepted')
def step_impl(context):
    assert context.result.is_valid is True

# features/environment.py
def before_scenario(context, scenario):
    context.db_session = next(get_test_db())

def after_scenario(context, scenario):
    context.db_session.rollback()
    context.db_session.close()
```

### Python (pytest-bdd)

```python
# tests/bdd/test_user_registration.py
from pytest_bdd import scenarios, given, when, then, parsers

scenarios('features/auth/user_registration.feature')

@pytest.fixture
def context():
    return {'request': {}, 'result': None}

@when(parsers.parse('I submit with email "{email}"'))
def submit_email(email, context):
    validator = EmailValidator()
    context['result'] = validator.validate(email)

@then('the email should be accepted')
def email_accepted(context):
    assert context['result'].is_valid is True
```

---

## Part 3: Unit Tests (Derived from BDD)

Write unit tests for components identified in step definitions.

### Java (JUnit 5)

```java
/**
 * Unit tests for EmailValidator.
 * Derived from: features/auth/user-registration.feature
 * Traces to: BR-001, FR-001
 */
@ExtendWith(MockitoExtension.class)
class EmailValidatorTest {
    private EmailValidator validator;

    @BeforeEach
    void setUp() {
        validator = new EmailValidator();
    }

    @Test
    @DisplayName("BR-001: Valid email should pass validation")
    void validEmailShouldPassValidation() {
        ValidationResult result = validator.validate("user@example.com");
        assertThat(result.isValid()).isTrue();
    }

    @Test
    @DisplayName("BR-001: Invalid email should fail validation")
    void invalidEmailShouldFailValidation() {
        ValidationResult result = validator.validate("invalid");
        assertThat(result.isValid()).isFalse();
        assertThat(result.getError()).isEqualTo("Invalid email format");
    }
}
```

### Python (pytest)

```python
# tests/unit/test_email_validator.py
"""
Unit tests for EmailValidator.
Derived from: features/auth/user_registration.feature
Traces to: BR-001, FR-001
"""

@pytest.fixture
def validator():
    return EmailValidator()

def test_valid_email_should_pass(validator):
    """BR-001: Valid email should pass validation"""
    result = validator.validate("user@example.com")
    assert result.is_valid is True

def test_invalid_email_should_fail(validator):
    """BR-001: Invalid email should fail validation"""
    result = validator.validate("invalid")
    assert result.is_valid is False
    assert result.error == "Invalid email format"
```

---

## Part 4: TDD Loop (Implementation)

**5-Step Process per Component:**

### 1. Verify RED

```bash
mvn test -Dtest=EmailValidatorTest
# Expected: FAILURE (component doesn't exist)
```

### 2. Write Implementation

```java
/**
 * Validates email addresses.
 * @see BR-001 Email validation rules
 * @see FR-001 Email format validation
 */
@Component  // or @ApplicationScoped (Quarkus)
public class EmailValidator {
    private static final Pattern EMAIL_PATTERN =
        Pattern.compile("^[A-Za-z0-9+_.-]+@(.+)$");

    public ValidationResult validate(String email) {
        if (email == null || email.isEmpty()) {
            return ValidationResult.error("Invalid email format");
        }

        if (!EMAIL_PATTERN.matcher(email).matches()) {
            return ValidationResult.error("Invalid email format");
        }

        return ValidationResult.success();
    }
}
```

### 3. Verify Unit Tests GREEN

```bash
mvn test -Dtest=EmailValidatorTest
# Expected: 2/2 PASS ✓
```

### 4. Verify BDD GREEN

```bash
mvn test -Dtest=CucumberRunnerIT -Dcucumber.filter.tags="@BR-001"
# Expected: 2/2 scenarios PASS ✓
```

### 5. Regression Check

```bash
mvn test
# Expected: All tests still passing ✓
```

**Retry Logic:** Max 3 attempts. If still RED after 3 tries → HALT and report failure.

---

## Part 5: TDD Rules & Discipline

### Golden Rule

**NO production code without a failing test first.**

### Enforcement Checks

**Step 4 (Tests):**

```bash
# Verify no production code exists
find src/main/java -name "*.java" -not -name "Application.java" | wc -l
# Expected: 0

# Verify all tests RED
mvn test
# Expected: All FAIL or UNDEFINED
```

**Step 5 (Core):**

```bash
# Pre-flight: Verify Step 4 complete
# Only then write production code
```

### When to HALT

1. **Test passes in RED phase** → Test is invalid
2. **Test fails after 3 GREEN attempts** → Implementation wrong
3. **Production code found in Step 4** → Delete and restart
4. **Circular dependencies detected** → Architectural issue

### Common Anti-Patterns

| Anti-Pattern | Fix |
|-------------|-----|
| Write code before tests | Write tests first, always |
| Tests with no assertions | Every test needs assertions |
| Over-mocking | Mock external deps only |
| Skip RED verification | Always verify RED |
| Modify tests to pass | Fix implementation, not tests |

---

## Part 6: Running Tests

### Java Commands

```bash
# BDD only
mvn test -Dtest=CucumberRunnerIT

# BDD with tag filter
mvn test -Dtest=CucumberRunnerIT -Dcucumber.filter.tags="@smoke"

# Unit test
mvn test -Dtest=EmailValidatorTest

# All tests
mvn verify
```

### Python Commands

```bash
# BDD (behave)
behave
behave features/auth/user_registration.feature
behave --tags=@smoke

# BDD (pytest-bdd)
pytest tests/bdd/
pytest tests/bdd/test_user_registration.py
pytest -m smoke tests/bdd/

# Unit tests
pytest tests/unit/
pytest tests/unit/test_email_validator.py -v

# All tests
pytest tests/ -v
```

---

## Part 7: Component Patterns

### Validators

**Java:**

```java
@Component
public class EmailValidator {
    public ValidationResult validate(String email) {
        // Validation logic
    }
}
```

**Python:**

```python
class EmailValidator:
    def validate(self, email: str) -> ValidationResult:
        # Validation logic
```

### Services

**Java:**

```java
@Service
public class UserService {
    private final UserRepository repository;

    public UserService(UserRepository repository) {
        this.repository = repository;
    }

    @Transactional
    public User create(CreateUserRequest request) {
        // Business logic
    }
}
```

**Python:**

```python
class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create(self, request: CreateUserRequest) -> User:
        # Business logic
```

### Repositories

**Java (Spring Data JPA):**

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);
}
```

**Python (SQLAlchemy):**

```python
class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
```

---

## Quick Decision Tree

```text
Starting Step 4 (Tests)?
├─ Write BDD scenarios (.feature files)
├─ Generate BDD step definitions
│  └─ Identify needed components
└─ Write unit tests for those components
   └─ All RED? → Proceed to Step 5

Starting Step 5 (Implementation)?
├─ For each component:
│  ├─ Verify RED
│  ├─ Write minimal implementation
│  ├─ Verify unit tests GREEN
│  ├─ Verify BDD GREEN
│  └─ Regression check
└─ All GREEN? → Step 5 complete
```
