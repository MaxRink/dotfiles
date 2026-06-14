
# Java Language Skill

Comprehensive Java language reference for idiomatic code generation during the TDD/BDD workflow.
Consult the topic-specific references as needed during each code-generation step.

## References

Available at [references/](references/) — load the ones relevant to the detected stack:

| Reference | When to Load | Used During |
|-----------|-------------|-------------|
| [references/fundamentals.md](references/fundamentals.md) | Always (Java target) | All steps — core syntax, OOP, collections, streams |
| [references/springboot-core.md](references/springboot-core.md) | Spring Boot in target frameworks | Setup, Core, Integration, Polish — REST APIs, Security, Data, Actuator, layered architecture, validation, caching, async, filters, observability |
| [references/springboot-security.md](references/springboot-security.md) | Spring Boot in target frameworks | Core, Integration, Polish — authn/authz, input validation, CSRF, CORS, secrets, security headers |
| [references/testing.md](references/testing.md) | Always (Java target) | Tests, Core, Integration — JUnit 5, Mockito, AssertJ, TDD workflow, MockMvc, @DataJpaTest, Testcontainers, JaCoCo, ArchUnit, Pact, PIT |
| [references/build-tools.md](references/build-tools.md) | Always (Java target) | Setup — Maven POM / Gradle Kotlin DSL, dependencies, CI/CD |
| [references/jpa-patterns.md](references/jpa-patterns.md) | JPA/Hibernate in target frameworks | Core, Integration — entity design, queries, transactions, caching |
| [references/microservices.md](references/microservices.md) | Spring Cloud / microservices in scope | Core, Integration — service discovery, resilience, event-driven |
| [references/concurrency.md](references/concurrency.md) | Concurrency required by technical plan | Core — threads, executors, CompletableFuture, virtual threads |
| [references/performance.md](references/performance.md) | Performance tuning in scope | Polish — GC tuning, profiling, JMH benchmarks |
| [references/coding-standards.md](references/coding-standards.md) | Always (Java target) | All steps — naming, immutability, Optional usage, streams, exceptions, logging |

## How This Skill Is Used

The `code-generation` Step 1b detects Java in `target_stack.languages` and loads this skill.
The agent then reads the relevant references based on the frameworks and infrastructure in the technical plan.

### Step-to-Reference Mapping

| Code-Gen Step | Primary References | What They Provide |
|---------------|-------------------|-------------------|
| **Setup** | `build-tools.md`, `springboot-core.md`, `coding-standards.md` | `pom.xml`/`build.gradle.kts` templates, directory layout, dependency manifests, project conventions |
| **Tests (TDD Red)** | `testing.md` | JUnit 5 conventions, Mockito patterns, TDD workflow, MockMvc, @DataJpaTest, BDD with Cucumber-JVM, Testcontainers, JaCoCo, ArchUnit, Pact, PIT |
| **Core (TDD Green)** | `fundamentals.md`, `springboot-core.md`, `springboot-security.md`, `testing.md`, `jpa-patterns.md`, `concurrency.md`, `coding-standards.md` | Idiomatic Java, Spring annotations, layered services, security, TDD red-green-refactor, entity design, thread-safe patterns, coding conventions |
| **Integration** | `springboot-core.md`, `springboot-security.md`, `testing.md`, `microservices.md` | Integration test slices, MockMvc, @SpringBootTest, service communication, resilience, filters, exception handling, security |
| **Polish** | `performance.md`, `springboot-core.md`, `springboot-security.md`, `coding-standards.md` | JVM tuning, structured logging, observability, rate limiting, security hardening, code quality standards |

## Java Project Conventions

### Directory Layout (Maven Standard)

```text
src/
├── main/
│   ├── java/com/example/<module>/
│   │   ├── controller/
│   │   ├── service/
│   │   ├── repository/
│   │   ├── model/
│   │   ├── dto/
│   │   └── config/
│   └── resources/
│       ├── application.yml
│       └── db/migration/
└── test/
    ├── java/com/example/<module>/
    │   ├── unit/
    │   └── integration/
    └── resources/
        └── application-test.yml
```

### Naming Conventions

See [references/coding-standards.md](references/coding-standards.md) for complete naming rules, immutability patterns, and code style.

Summary: PascalCase classes, camelCase methods, UPPER_SNAKE constants, `*Test` (unit) / `*IT` (integration) test classes, `*Config` configuration classes.

### Layer Architecture

```text
Controller → Service → Repository → Database
     ↓           ↓          ↓
   DTOs      Entities    Entities
```

- Controllers handle HTTP, validate input, delegate to services
- Services contain business logic, enforce rules, coordinate repositories
- Repositories handle data access (Spring Data JPA)
- DTOs for API boundary, Entities for persistence — never expose entities in APIs
