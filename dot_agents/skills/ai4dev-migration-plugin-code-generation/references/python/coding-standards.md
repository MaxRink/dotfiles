# Python Coding Standards

> Scope: Naming conventions, immutability patterns, type-first development, async-first design, error handling, structured logging, and code organization for Python 3.11+ projects.

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Functions / methods | `snake_case` | `get_user_by_id()` |
| Variables | `snake_case` | `user_count` |
| Classes | `PascalCase` | `UserService`, `OrderRepository` |
| Constants | `UPPER_SNAKE` | `MAX_RETRIES`, `DEFAULT_PAGE_SIZE` |
| Modules / packages | `snake_case` | `user_service.py`, `auth/` |
| Type aliases | `PascalCase` | `UserId = NewType("UserId", int)` |
| Private | Leading `_` | `_validate_input()`, `_cache` |
| Test files | `test_<module>.py` | `test_user_service.py` |
| Test functions | `test_<behavior>` | `test_create_user_returns_201` |
| Fixtures | `snake_case` noun | `db_session`, `auth_client` |

## Immutability

```python
# Prefer frozen dataclasses for value objects
@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str = "USD"

# Avoid mutable default arguments
# BAD
def process(items: list[str] = []):  # shared mutable default
    items.append("new")

# GOOD
def process(items: list[str] | None = None):
    items = items or []

# Use tuple for immutable sequences
ALLOWED_ROLES: tuple[str, ...] = ("admin", "editor", "viewer")
```

## Type-First Development

```python
# Type ALL function signatures — no exceptions
def calculate_discount(price: Decimal, rate: float) -> Decimal: ...

# No `Any` — use specific types or generics
# BAD
def process(data: Any) -> Any: ...

# GOOD
def process(data: UserPayload) -> UserResponse: ...

# Use TypedDict over dict[str, Any]
class MetricsPayload(TypedDict):
    duration_ms: float
    status_code: int
    endpoint: str

# Use Protocol for structural typing (duck typing with types)
class Serializable(Protocol):
    def to_dict(self) -> dict[str, Any]: ...

# Use Literal for constrained strings
Status = Literal["pending", "active", "cancelled"]

# Check types at boundaries only — trust typed internals
```

## Async-First Design

```python
# Default to async for I/O operations
async def fetch_user(user_id: int) -> User: ...
async def save_order(order: Order) -> Order: ...

# Use sync for pure computation (CPU-bound)
def calculate_tax(amount: Decimal, rate: float) -> Decimal: ...

# Run sync blocking code in executor
import asyncio

async def process_image(data: bytes) -> bytes:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _resize_sync, data)
```

## Error Handling

```python
# Always chain exceptions with `from`
try:
    user = await repo.get_by_id(user_id)
except DatabaseError as err:
    raise ServiceError(f"Failed to fetch user {user_id}") from err

# Never bare except
# BAD
try: ... except: pass

# GOOD — catch specific exceptions
try: ...
except (ValueError, KeyError) as err:
    logger.error("Validation failed", error=str(err))
    raise

# Use custom exception hierarchy — see fastapi-core.md § Exception Handling
```

## Structured Logging

```python
# Decision heuristic:
# - Simple scripts        → print() + JSONL to file
# - FastAPI applications  → loguru or structlog
# - Large distributed     → structlog with JSON output

# loguru — simple, powerful, zero-config
from loguru import logger

logger.info("User created", user_id=user.id, email=user.email)
logger.error("Payment failed", order_id=order.id, error=str(err))

# Configuration
logger.add(
    "logs/app.log",
    rotation="100 MB",
    retention="30 days",
    compression="gz",
    serialize=True,        # JSON output
)

# NEVER log secrets — use token fingerprinting
def fingerprint(token: str) -> str:
    return f"{token[:4]}...{token[-4:]}" if len(token) > 8 else "***"

logger.info("Auth attempt", token=fingerprint(raw_token))
```

## Code Organization

```python
# Modules should be < 300 lines — split when larger
# One class per file for major classes (services, repositories)
# Group related utilities in a module

# Early returns — avoid deep nesting
# BAD
def process(user):
    if user:
        if user.is_active:
            if user.has_permission:
                return do_work(user)

# GOOD
def process(user):
    if not user:
        raise NotFoundError("User")
    if not user.is_active:
        raise InactiveUserError(user.id)
    if not user.has_permission:
        raise ForbiddenError("Missing permission")
    return do_work(user)

# No magic numbers
# BAD
if retries > 3: ...

# GOOD
MAX_RETRIES = 3
if retries > MAX_RETRIES: ...
```

## Import Order (Enforced by Ruff)

```python
# 1. Standard library
import asyncio
from datetime import datetime, timezone

# 2. Third-party
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# 3. Local
from app.users.service import UserService
from app.common.schemas import PaginatedResponse
```
