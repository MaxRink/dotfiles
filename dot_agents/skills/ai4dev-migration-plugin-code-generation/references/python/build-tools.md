# Python Build Tools

> Scope: Package management (uv primary, poetry alternative), pyproject.toml structure, ruff linting/formatting, type checking (mypy/pyright/ty), and CI/CD pipeline configuration.

## uv (Primary — Astral)

```bash
# Project init
uv init myapp
cd myapp

# Add dependencies
uv add fastapi uvicorn[standard] sqlalchemy[asyncio] asyncpg pydantic-settings alembic
uv add python-jose[cryptography] passlib[bcrypt] python-multipart httpx

# Add dev dependencies
uv add --dev pytest pytest-asyncio pytest-cov pytest-mock httpx hypothesis
uv add --dev ruff mypy

# Sync from lockfile (CI / fresh clone)
uv sync

# Run commands in venv
uv run pytest
uv run alembic upgrade head
uv run uvicorn app.main:create_app --factory --reload
```

### uv Lockfile

- `uv.lock` — auto-generated, deterministic, cross-platform
- Always commit `uv.lock` to version control
- `uv sync` installs exact versions from lockfile

## poetry (Alternative)

```bash
poetry new myapp
poetry add fastapi uvicorn sqlalchemy asyncpg pydantic-settings
poetry add --group dev pytest pytest-asyncio pytest-cov ruff mypy

# Install from lockfile
poetry install

# Run commands
poetry run pytest
```

## pyproject.toml Structure

```toml
[project]
name = "myapp"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "sqlalchemy[asyncio]>=2.0",
    "asyncpg>=0.30",
    "pydantic-settings>=2.0",
    "alembic>=1.13",
    "python-jose[cryptography]>=3.3",
    "passlib[bcrypt]>=1.7",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "pytest-cov>=5.0",
    "pytest-mock>=3.14",
    "httpx>=0.27",
    "hypothesis>=6.100",
    "ruff>=0.8",
    "mypy>=1.13",
]

[tool.ruff]
target-version = "py311"
line-length = 120
src = ["src"]

[tool.ruff.lint]
select = [
    "E",     # pycodestyle errors
    "W",     # pycodestyle warnings
    "F",     # pyflakes
    "I",     # isort
    "N",     # pep8-naming
    "UP",    # pyupgrade
    "B",     # flake8-bugbear
    "A",     # flake8-builtins
    "S",     # flake8-bandit (security)
    "T20",   # flake8-print
    "SIM",   # flake8-simplify
    "RUF",   # ruff-specific rules
]
# ZERO noqa — fix the code, don't suppress warnings
ignore = []

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101"]  # allow assert in tests

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
docstring-code-format = true

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
# ZERO type: ignore — fix the types, don't suppress
plugins = ["pydantic.mypy"]

[tool.mypy.pydantic-mypy]
init_forbid_extra = true
init_typed = true

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow tests",
]

[tool.coverage.run]
source = ["app"]
branch = true
omit = ["*/tests/*", "*/migrations/*"]

[tool.coverage.report]
fail_under = 80
show_missing = true
```

## Ruff — Linting + Formatting

```bash
# Format code
ruff format .

# Lint with auto-fix
ruff check --fix .

# Lint without fix (CI mode)
ruff check .
```

### Key Principles

- **ZERO `# noqa`** — fix the underlying issue, never suppress
- Ruff replaces: black, isort, flake8, pycodestyle, pyflakes, and many plugins
- Run `ruff format` before `ruff check` (formatting first, then lint)

## Type Checking

### mypy (Established)

```bash
mypy src/
# or with strict mode
mypy --strict src/
```

### pyright (Microsoft — faster)

```bash
pyright src/
```

### ty (Astral — Rust-based, experimental)

```bash
ty check src/
```

### Key Principles

- **ZERO `# type: ignore`** — fix the types, don't suppress
- Enable `strict = true` in mypy from the start
- Use `reveal_type()` for debugging type inference
- Prefer `Protocol` over `ABC` for structural typing

## CI/CD — GitHub Actions

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Install dependencies
        run: uv sync

      - name: Format check
        run: uv run ruff format --check .

      - name: Lint
        run: uv run ruff check .

      - name: Type check
        run: uv run mypy src/

      - name: Test
        run: uv run pytest --cov=app --cov-report=term-missing --cov-fail-under=80
        env:
          DATABASE_URL: postgresql+asyncpg://test:test@localhost:5432/test_db
          SECRET_KEY: test-secret-key
```

## Quality Gates (Pre-merge)

| Gate | Command | Threshold |
|------|---------|-----------|
| Format | `ruff format --check .` | Zero diff |
| Lint | `ruff check .` | Zero findings |
| Types | `mypy --strict src/` | Zero errors |
| Tests | `pytest --cov-fail-under=80` | ≥80% branch coverage |
