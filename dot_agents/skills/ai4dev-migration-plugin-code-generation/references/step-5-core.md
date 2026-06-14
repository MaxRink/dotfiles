# Step 5 — Core (Implementation - TDD GREEN)

Implement production code to make Step 4 tests pass.

## Overview

**TDD Loop:** Verify RED → Write Code → Verify GREEN (Unit + BDD)

**Rules:**

- Step 4 must be complete (all tests RED)
- NO test writing (tests from Step 4)
- Write MINIMAL production code only

## Prerequisites

**PRE-FLIGHT:** Verify ALL Tests tasks `passed` in tasks.json

**Load references:**

- `bdd-tdd-workflow.md` (TDD loop, implementation patterns)
- Language skill: `fundamentals.md`, `{framework}-core.md`, `{persistence}-patterns.md`, `coding-standards.md`
- If `database/schema.sql` exists from Setup: read it before generating entity/model classes to ensure ORM models match the generated schema (column types, constraints, relationships)

---

## TDD Loop (Per Component)

For each component from Step 4:

**1. Verify RED:**

```bash
mvn test -Dtest=EmailValidatorTest  # Expect: FAILURE ✓
```

**2. Write Implementation:**

```java
// src/main/java/.../EmailValidator.java
/**
 * @see BR-001, FR-001
 */
@Component  // or @ApplicationScoped (Quarkus)
public class EmailValidator {
    public ValidationResult validate(String email) {
        // Minimal code to pass unit tests
    }
}
```

**3. Verify Unit Tests GREEN:**

```bash
mvn test -Dtest=EmailValidatorTest  # Expect: 3/3 PASS ✓
```

**4. Verify BDD GREEN:**

```bash
mvn test -Dtest=CucumberRunnerIT -Dcucumber.filter.tags="@BR-001"  # Expect: PASS ✓
```

**5. Regression Check:**

```bash
mvn test  # Expect: All still passing ✓
```

**Max 3 attempts:** If still RED after 3 tries → HALT, report failure

---

## Language Patterns (Apply from Skills)

**Java:**

- Service: `@Service`, constructor injection, `@Transactional`
- Repository: `extends JpaRepository<Entity, ID>`, `Optional<T>`
- Controller: `@RestController`, `ResponseEntity<T>`, `@Valid`

**Python:**

- Service: `async def`, type hints, Pydantic DTOs
- Repository: `AsyncSession`, `select()`, `Optional`
- Router: `APIRouter`, `Depends`, HTTP status codes

See language skill references for details.

---

## Checkpoint & Progress

**Run all tests:** `mvn test` or `pytest tests/`

**Verify:**

- Unit: 15/15 GREEN ✓
- BDD: 7/7 GREEN ✓
- Total: 22/22 GREEN ✓
- Regressions: 0 ✓

**Batch checkpoint:**

```json
{
  "verification_type": "green",
  "unit_tests_passing": 15,
  "bdd_scenarios_passing": 7,
  "total": 22,
  "regressions": 0,
  "components_implemented": ["EmailValidator", "PasswordValidator"],
  "tdd_loops_successful": 2
}
```

**Progress:** `[Step 5/8] Core - Batch 2/4 ✓ | 22/22 GREEN | EmailValidator, PasswordValidator | Next: Batch 3/4`

---

## Step 5 Complete → Proceed to Step 6 (Integration)

See `tdd-loop-rules.md` for TDD workflow details.
