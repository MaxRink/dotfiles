# Python Fundamentals

> Scope: Python 3.11+ core syntax, type system, data structures, and error handling patterns for idiomatic code generation.

## Modern Syntax (3.11+)

### Structural Pattern Matching

```python
match command:
    case {"action": "create", "payload": dict() as data}:
        return create_resource(data)
    case {"action": "delete", "id": int(resource_id)}:
        return delete_resource(resource_id)
    case _:
        raise ValueError(f"Unknown command: {command}")
```

### Dataclasses (Prefer Frozen)

```python
from dataclasses import dataclass, field

@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str = "USD"

@dataclass(frozen=True)
class Order:
    id: str
    items: tuple[OrderItem, ...] = field(default_factory=tuple)  # immutable collection
```

## Type System

### Union Types and Optionals

```python
# 3.10+ union syntax — prefer over typing.Union
def process(value: int | str) -> str: ...
def find_user(user_id: int) -> User | None: ...
```

### Generics and TypeVar

```python
from typing import TypeVar, Generic

T = TypeVar("T")

class Repository(Generic[T]):
    def get_by_id(self, id: int) -> T | None: ...
    def save(self, entity: T) -> T: ...
```

### NewType for Domain Primitives

```python
from typing import NewType

UserId = NewType("UserId", int)
Email = NewType("Email", str)

def get_user(user_id: UserId) -> User: ...  # prevents accidental int pass
```

### Protocol for Structural Typing

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Publishable(Protocol):
    def publish(self) -> None: ...
    @property
    def topic(self) -> str: ...

# Any class with publish() and topic works — no inheritance needed
```

### TypedDict for Structured Dicts

```python
from typing import TypedDict, NotRequired

class UserPayload(TypedDict):
    name: str
    email: str
    age: NotRequired[int]
```

## Collections

```python
# Comprehensions — prefer over map/filter for readability
active = [u for u in users if u.is_active]
by_role = {u.id: u for u in users}
unique_emails = {u.email for u in users}

# itertools for lazy pipelines
from itertools import chain, islice, groupby
batches = [list(islice(it, n)) for it in [iter(items)] * n]
```

## Exception Handling

### Chain Exceptions — Always Use `from`

```python
try:
    result = external_api.fetch(resource_id)
except ConnectionError as err:
    raise ServiceUnavailableError(f"API unreachable: {resource_id}") from err
```

### Context Managers for Resource Cleanup

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def managed_transaction(session: AsyncSession):
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
```

### Never Use Bare `except`

```python
# BAD
try: ... except: pass

# GOOD — catch specific exceptions
try: ...
except (ValueError, KeyError) as err:
    logger.error("Processing failed", error=str(err))
    raise
```
