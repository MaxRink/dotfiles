
# Python Language Skill

Comprehensive Python language reference for idiomatic code generation during the TDD/BDD workflow.
Consult the topic-specific references as needed during each code-generation step.

## References

Available at [references/](references/) — load the ones relevant to the detected stack:

| Reference | When to Load | Used During |
|-----------|-------------|-------------|
| [references/fundamentals.md](references/fundamentals.md) | Always (Python target) | All steps — type hints, dataclasses, pattern matching, exception handling |
| [references/fastapi-core.md](references/fastapi-core.md) | FastAPI in target frameworks | Setup, Core, Integration, Polish — routing, Pydantic v2 DTOs, DI, middleware, configuration |
| [references/fastapi-security.md](references/fastapi-security.md) | FastAPI in target frameworks | Core, Integration, Polish — JWT auth, CORS, rate limiting, input validation, security headers |
| [references/testing.md](references/testing.md) | Always (Python target) | Tests, Core, Integration — pytest, TDD workflow, async testing, FastAPI TestClient, hypothesis, coverage |
| [references/sqlalchemy-patterns.md](references/sqlalchemy-patterns.md) | SQLAlchemy in target frameworks | Setup, Core, Integration — models, BaseRepository, transactions, Alembic migrations |
| [references/build-tools.md](references/build-tools.md) | Always (Python target) | Setup — uv/poetry, pyproject.toml, ruff, mypy, CI/CD |
| [references/coding-standards.md](references/coding-standards.md) | Always (Python target) | All steps — naming, immutability, type-first, async-first, structured logging |
| [references/async-patterns.md](references/async-patterns.md) | Async/concurrency required by technical plan | Core, Integration — TaskGroup, gather, run_in_executor, background tasks |

## How This Skill Is Used

The `code-generation` Step 1b detects Python in `target_stack.languages` and loads this skill.
The agent then reads the relevant references based on the frameworks and infrastructure in the technical plan.

### Step-to-Reference Mapping

| Code-Gen Step | Primary References | What They Provide |
|---------------|-------------------|-------------------|
| **Setup** | `build-tools.md`, `fastapi-core.md`, `sqlalchemy-patterns.md`, `coding-standards.md` | `pyproject.toml` template, directory layout, dependency manifests, Alembic init, project conventions |
| **Tests (TDD Red)** | `testing.md` | pytest conventions, fixtures, TDD workflow, async testing, FastAPI TestClient, hypothesis, coverage goals |
| **Core (TDD Green)** | `fundamentals.md`, `fastapi-core.md`, `fastapi-security.md`, `testing.md`, `sqlalchemy-patterns.md`, `async-patterns.md`, `coding-standards.md` | Idiomatic Python, FastAPI routes, Pydantic DTOs, DI, security, TDD red-green-refactor, ORM models, async patterns, conventions |
| **Integration** | `fastapi-core.md`, `fastapi-security.md`, `testing.md`, `async-patterns.md` | Integration tests, API testing (httpx.AsyncClient), dependency overrides, background tasks, exception handling, security |
| **Polish** | `fastapi-core.md`, `fastapi-security.md`, `coding-standards.md`, `build-tools.md` | Production defaults, security hardening, structured logging, observability, quality gates (ruff, mypy, coverage) |

## Python Project Conventions

### Directory Layout

```text
src/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app factory, lifespan
│   ├── config.py            # pydantic-settings
│   ├── dependencies.py      # shared dependencies
│   ├── exceptions.py        # custom exceptions + handlers
│   ├── <module>/            # feature module (users/, orders/)
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   ├── service.py
│   │   ├── repository.py
│   │   └── dependencies.py
│   └── common/
│       ├── schemas.py       # shared schemas (pagination, errors)
│       └── repository.py    # BaseRepository generic
├── alembic/
│   ├── env.py
│   └── versions/
├── tests/
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── pyproject.toml
└── .env
```

### Naming Conventions

See [references/coding-standards.md](references/coding-standards.md) for complete naming rules, immutability patterns, and code style.

Summary: `snake_case` functions/variables, `PascalCase` classes, `UPPER_SNAKE` constants, `test_<behavior>` test functions, `test_<module>.py` test files, leading `_` for private.

### Layer Architecture

```text
Router → Service → Repository → Database
  ↓         ↓          ↓
Schemas  Models     Models
(DTOs)  (Domain)   (ORM)
```

- Routers handle HTTP, validate input via Pydantic, delegate to services
- Services contain business logic, enforce rules, coordinate repositories
- Repositories handle data access (SQLAlchemy) — never expose ORM models in APIs
- Schemas (DTOs) for API boundary, Models for persistence
