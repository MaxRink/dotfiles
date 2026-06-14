# Python Testing

> Scope: TDD workflow, pytest patterns (fixtures, parametrize, markers), mocking, async testing, FastAPI test client,
> database testing with real DB, property-based testing (hypothesis), coverage, and CI commands.

## TDD Workflow

```text
1. RED    — Write a failing test that defines expected behavior
2. GREEN  — Write the minimum code to make the test pass
3. REFACTOR — Clean up while keeping tests green
4. REPEAT — Next behavior increment
```

- Write tests **before** implementation code
- One assertion concept per test (multiple asserts OK if testing one behavior)
- Run tests after every change: `pytest -x` (stop on first failure)

## pytest Fundamentals

### Test File Layout

```text
tests/
├── conftest.py              # shared fixtures
├── unit/
│   ├── test_user_service.py
│   └── test_order_service.py
├── integration/
│   ├── conftest.py          # integration-specific fixtures (db, client)
│   ├── test_user_api.py
│   └── test_order_api.py
└── property/
    └── test_validators.py
```

### Naming Convention

- Files: `test_<module>.py`
- Classes: `TestUserService`, `TestOrderCreation`
- Functions: `test_<behavior>` — describe what, not how
  - GOOD: `test_create_user_returns_201`, `test_expired_token_raises_401`
  - BAD: `test_post_method`, `test_function_1`

### Fixtures

```python
import pytest
from httpx import AsyncClient, ASGITransport

@pytest.fixture
def user_data() -> dict:
    return {"name": "Alice", "email": "alice@example.com", "password": "Secret123"}

@pytest.fixture
async def async_client(app) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest.fixture(autouse=True)
async def clean_db(db_session):
    yield
    await db_session.rollback()
```

### Parametrize

```python
@pytest.mark.parametrize(
    "email, expected_valid",
    [
        ("user@example.com", True),
        ("user@", False),
        ("", False),
        ("user@example.co.uk", True),
    ],
)
def test_email_validation(email: str, expected_valid: bool):
    if expected_valid:
        assert EmailValidator.validate(email)
    else:
        with pytest.raises(ValueError):
            EmailValidator.validate(email)
```

### Markers

```python
# pyproject.toml
[tool.pytest.ini_options]
markers = [
    "unit: Unit tests (no I/O)",
    "integration: Integration tests (database, API)",
    "slow: Slow tests (skip in dev)",
]

# Usage
@pytest.mark.unit
def test_calculate_total(): ...

@pytest.mark.integration
async def test_create_user_api(): ...

# Run by marker
# pytest -m unit
# pytest -m "not slow"
```

## Mocking

```python
from unittest.mock import AsyncMock, patch

# pytest-mock fixture
async def test_user_service_creates_user(mocker):
    mock_repo = mocker.AsyncMock(spec=UserRepository)
    mock_repo.get_by_email.return_value = None
    mock_repo.create.return_value = User(id=1, name="Alice", email="alice@example.com")

    service = UserService(mock_repo)
    user = await service.create(UserCreate(name="Alice", email="alice@example.com", password="Secret123"))

    assert user.id == 1
    mock_repo.create.assert_awaited_once()

# patch decorator
@patch("app.users.service.send_welcome_email", new_callable=AsyncMock)
async def test_create_user_sends_email(mock_email):
    ...
    mock_email.assert_awaited_once_with("alice@example.com")
```

## Async Testing

```python
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"  # all async tests run automatically

# No need for @pytest.mark.asyncio with asyncio_mode = "auto"
async def test_fetch_user():
    result = await user_service.get_by_id(1)
    assert result is not None
```

## FastAPI Testing

### TestClient (sync) and AsyncClient (async)

```python
from httpx import AsyncClient, ASGITransport

@pytest.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

async def test_create_user(client: AsyncClient, user_data: dict):
    response = await client.post("/api/v1/users", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "password" not in data  # never expose password

async def test_unauthorized_access(client: AsyncClient):
    response = await client.get("/api/v1/profile")
    assert response.status_code == 401
```

### Dependency Overrides

```python
@pytest.fixture
def app():
    app = create_app()

    # Override database dependency for testing
    async def override_get_db():
        async with test_session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    yield app
    app.dependency_overrides.clear()
```

### Authenticated Test Requests

```python
@pytest.fixture
async def auth_client(client: AsyncClient, test_user: User) -> AsyncClient:
    token = create_access_token(data={"sub": str(test_user.id)})
    client.headers["Authorization"] = f"Bearer {token}"
    return client

async def test_get_profile(auth_client: AsyncClient):
    response = await auth_client.get("/api/v1/profile")
    assert response.status_code == 200
```

## Database Testing — Real DB, Not Mocks

```python
# conftest.py — use a real test database
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_db"

@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    async with async_sessionmaker(engine, expire_on_commit=False)() as session:
        yield session
        await session.rollback()  # each test gets clean state
```

### Testcontainers (Alternative)

```python
import pytest
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="session")
def postgres():
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg.get_connection_url().replace("psycopg2", "asyncpg")
```

## Property-Based Testing (Hypothesis)

```python
from hypothesis import given, strategies as st

@given(
    name=st.text(min_size=1, max_size=100),
    age=st.integers(min_value=0, max_value=150),
)
def test_user_creation_never_crashes(name: str, age: int):
    user = User(name=name, age=age)
    assert user.name == name

@given(amount=st.decimals(min_value=0, max_value=10000, places=2))
def test_price_calculation_is_non_negative(amount):
    result = calculate_tax(amount)
    assert result >= 0
```

## Test Data Builders

```python
@dataclass
class UserBuilder:
    name: str = "Test User"
    email: str = "test@example.com"
    password: str = "Secret123"
    is_active: bool = True

    def with_name(self, name: str) -> "UserBuilder":
        return UserBuilder(**{**self.__dict__, "name": name})

    def with_email(self, email: str) -> "UserBuilder":
        return UserBuilder(**{**self.__dict__, "email": email})

    def build(self) -> UserCreate:
        return UserCreate(**self.__dict__)

    async def create(self, session: AsyncSession) -> User:
        user = User(**self.__dict__, hashed_password=hash_password(self.password))
        session.add(user)
        await session.flush()
        return user
```

## Coverage

```toml
# pyproject.toml
[tool.coverage.run]
source = ["app"]
branch = true               # branch coverage > line coverage
omit = ["*/tests/*", "*/migrations/*"]

[tool.coverage.report]
fail_under = 80
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.",
]
```

## CI Commands

```bash
# Run all tests
pytest -x --tb=short

# Run with coverage
pytest --cov=app --cov-report=term-missing --cov-branch

# Run specific markers
pytest -m unit
pytest -m integration

# Run property-based tests
pytest tests/property/

# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Fail if coverage below threshold
pytest --cov=app --cov-fail-under=80
```
