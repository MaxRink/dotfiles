
# Quarkus Language Skill

Comprehensive Java Quarkus language reference for idiomatic code generation during the TDD/BDD workflow.
Consult the topic-specific references as needed during each code-generation step.

## References

Available at [references/](references/) — load the ones relevant to the detected stack:

| Reference | When to Load | Used During |
|-----------|-------------|-------------|
| [references/fundamentals.md](references/fundamentals.md) | Always (Quarkus target) | All steps — core Java syntax, OOP, collections, streams, records |
| [references/quarkus-core.md](references/quarkus-core.md) | Always (Quarkus target) | Setup, Core, Integration, Polish — REST APIs, CDI, Configuration, Panache, Health, Metrics, layered architecture |
| [references/quarkus-security.md](references/quarkus-security.md) | Always (Quarkus target) | Core, Integration, Polish — OIDC, JWT, RBAC, input validation, CSRF, CORS, secrets, security headers |
| [references/testing.md](references/testing.md) | Always (Quarkus target) | Tests, Core, Integration — @QuarkusTest, REST Assured, Mockito, TDD workflow, @TestProfile, Testcontainers, JaCoCo |
| [references/build-tools.md](references/build-tools.md) | Always (Quarkus target) | Setup — Maven/Gradle with Quarkus plugin, dependencies, native compilation, CI/CD |
| [references/persistence-patterns.md](references/persistence-patterns.md) | Hibernate/Panache in target frameworks | Core, Integration — Panache repositories, entity design, queries, transactions |
| [references/microservices.md](references/microservices.md) | MicroProfile / microservices in scope | Core, Integration — REST Client, fault tolerance, health checks, service discovery |
| [references/reactive-patterns.md](references/reactive-patterns.md) | Reactive required by technical plan | Core — Mutiny Uni/Multi, reactive REST, reactive database access |
| [references/coding-standards.md](references/coding-standards.md) | Always (Quarkus target) | All steps — naming, immutability, CDI best practices, exceptions, logging |

## How This Skill Is Used

The `code-generation` Step 1b detects Quarkus in `target_stack.frameworks` and loads this skill.
The agent then reads the relevant references based on the frameworks and infrastructure in the technical plan.

### Step-to-Reference Mapping

| Code-Gen Step | Primary References | What They Provide |
|---------------|-------------------|-------------------|
| **Setup** | `build-tools.md`, `quarkus-core.md`, `coding-standards.md` | `pom.xml`/`build.gradle.kts` with Quarkus plugin, directory layout, dependency manifests, project conventions |
| **Tests (TDD Red)** | `testing.md` | @QuarkusTest conventions, REST Assured patterns, TDD workflow, @TestProfile, Testcontainers, JaCoCo |
| **Core (TDD Green)** | `fundamentals.md`, `quarkus-core.md`, `quarkus-security.md`, `testing.md`, `persistence-patterns.md`, `reactive-patterns.md`, `coding-standards.md` | Idiomatic Java, Quarkus annotations, CDI, REST resources, security, TDD red-green-refactor, Panache patterns, reactive Mutiny, coding conventions |
| **Integration** | `quarkus-core.md`, `quarkus-security.md`, `testing.md`, `microservices.md` | Integration test slices, REST Assured, @QuarkusTest, REST Client, fault tolerance, health checks, exception handling, security |
| **Polish** | `quarkus-core.md`, `quarkus-security.md`, `coding-standards.md`, `build-tools.md` | Native compilation, structured logging, observability, security hardening, code quality standards |

## Quarkus Project Conventions

### Directory Layout (Maven Standard)

```text
src/
├── main/
│   ├── java/com/example/<module>/
│   │   ├── resource/              # REST endpoints
│   │   ├── service/               # Business logic
│   │   ├── repository/            # Panache repositories
│   │   ├── entity/                # JPA entities
│   │   ├── dto/                   # DTOs
│   │   └── config/                # Configuration beans
│   └── resources/
│       ├── application.properties
│       ├── application-dev.properties
│       ├── application-prod.properties
│       └── db/migration/          # Flyway migrations
└── test/
    ├── java/com/example/<module>/
    │   ├── resource/              # Resource tests
    │   └── integration/           # Integration tests
    └── resources/
        └── application-test.properties
```

### Naming Conventions

See [references/coding-standards.md](references/coding-standards.md) for complete naming rules, CDI patterns, and code style.

Summary: PascalCase classes, camelCase methods, UPPER_SNAKE constants, `*Test` (unit) / `*IT` (integration) test classes, `*Resource` for REST endpoints, `*Repository` for Panache repositories.

### Layer Architecture

```text
Resource → Service → Repository → Database
    ↓          ↓          ↓
  DTOs     Entities   Entities
```

- Resources handle HTTP (JAX-RS), validate input, delegate to services
- Services contain business logic, enforce rules, coordinate repositories
- Repositories handle data access (Panache)
- DTOs for API boundary, Entities for persistence — never expose entities in APIs
