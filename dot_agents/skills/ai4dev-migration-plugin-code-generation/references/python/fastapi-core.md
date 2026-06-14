# FastAPI Core Patterns

> Scope: FastAPI application architecture, routing, Pydantic v2 DTOs, dependency injection, exception handling, middleware, configuration, and production defaults.

## Layer Architecture

```text
Router → Service → Repository → Database
  ↓         ↓          ↓
Schemas  Models     Models
(DTOs)  (Domain)   (ORM)
```

- **Routers** handle HTTP, validate input via Pydantic, delegate to services
- **Services** contain business logic, enforce rules, coordinate repositories
- **Repositories** handle data access (SQLAlchemy) — see [sqlalchemy-patterns.md](sqlalchemy-patterns.md)
- **Schemas** (DTOs) for API boundary, **Models** for persistence — never expose ORM models in APIs

## Project Structure

```text
src/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app factory, lifespan, middleware
│   ├── config.py                # pydantic-settings configuration
│   ├── dependencies.py          # shared dependencies (get_db, get_current_user)
│   ├── exceptions.py            # custom exception classes + handlers
│   ├── <module>/                # feature module (e.g., users/, orders/)
│   │   ├── __init__.py
│   │   ├── router.py            # APIRouter with route handlers
│   │   ├── schemas.py           # Pydantic request/response models
│   │   ├── models.py            # SQLAlchemy ORM models
│   │   ├── service.py           # business logic
│   │   ├── repository.py        # data access layer
│   │   └── dependencies.py      # module-specific dependencies
│   └── common/
│       ├── schemas.py           # shared schemas (pagination, errors)
│       └── repository.py        # BaseRepository generic
├── alembic/                     # database migrations
│   ├── env.py
│   └── versions/
├── tests/
│   ├── conftest.py              # shared fixtures
│   ├── unit/
│   └── integration/
├── pyproject.toml
└── .env
```

## Async Routes

```python
# BAD — blocking call in async route
@router.get("/users/{user_id}")
async def get_user(user_id: int):
    return db.query(User).get(user_id)  # blocks event loop

# GOOD — fully async
@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    user = await service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)

# BEST — async + proper status codes + dependency injection
@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    payload: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    user = await service.create(payload)
    return UserResponse.model_validate(user)
```

## Pydantic v2 Schemas (DTOs)

```python
from pydantic import BaseModel, ConfigDict, Field, field_validator, EmailStr

class UserBase(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str = Field(min_length=1, max_length=100)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain an uppercase letter")
        return v

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool

class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
```

### Pagination

```python
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Sequence

T = TypeVar("T")

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size

class PaginatedResponse(BaseModel, Generic[T]):
    items: Sequence[T]
    total: int
    page: int
    size: int
    pages: int
```

## Dependency Injection

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Session dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

# Repository dependency
def get_user_repository(
    session: AsyncSession = Depends(get_db),
) -> UserRepository:
    return UserRepository(session)

# Service dependency
def get_user_service(
    repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repo)

# Usage in router — full chain injected automatically
@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
): ...
```

## Exception Handling

```python
# exceptions.py
from fastapi import Request
from fastapi.responses import JSONResponse

class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

class NotFoundError(AppError):
    def __init__(self, resource: str, resource_id: int | str):
        super().__init__(f"{resource} {resource_id} not found", status_code=404)

class ConflictError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=409)

# Register in app factory
async def app_exception_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )

app.add_exception_handler(AppError, app_exception_handler)
```

### Using in Service Layer

```python
class UserService:
    async def get_by_id(self, user_id: int) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        return user

    async def create(self, payload: UserCreate) -> User:
        existing = await self.repo.get_by_email(payload.email)
        if existing:
            raise ConflictError(f"Email {payload.email} already registered")
        return await self.repo.create(payload)
```

## Middleware

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time, uuid
from starlette.middleware.base import BaseHTTPMiddleware

# CORS — see fastapi-security.md for production configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing + correlation ID
class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{duration:.4f}"
        return response
```

## Configuration

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "myapp"
    debug: bool = False

    # Database
    database_url: str
    db_pool_size: int = 5
    db_max_overflow: int = 10

    # Auth
    secret_key: str
    access_token_expire_minutes: int = 30

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

settings = Settings()
```

## App Factory with Lifespan

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
    )
    app.add_exception_handler(AppError, app_exception_handler)
    app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
    app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])
    return app
```

## Production Defaults

```python
# uvicorn config (run.py or CLI)
uvicorn.run(
    "app.main:create_app",
    factory=True,
    host="0.0.0.0",
    port=8000,
    workers=4,               # match CPU cores
    loop="uvloop",           # faster event loop
    http="httptools",        # faster HTTP parsing
    access_log=False,        # disable in prod, use middleware logging
    log_level="warning",
)
```

## Health Check

```python
@app.get("/health", include_in_schema=False)
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "disconnected"},
        )
```
