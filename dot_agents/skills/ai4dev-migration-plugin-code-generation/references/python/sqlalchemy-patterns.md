# SQLAlchemy Patterns

> Scope: SQLAlchemy 2.0 async setup, model design (DeclarativeBase/Mapped), BaseRepository generics, transactions, eager loading, Alembic migrations, and connection pooling.

## Async Engine Setup

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

engine = create_async_engine(
    settings.database_url,          # postgresql+asyncpg://...
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_pre_ping=True,             # detect stale connections
    echo=settings.debug,            # SQL logging in dev only
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
```

## Model Design

```python
from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now(), server_default=func.now()
    )

class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)

    orders: Mapped[list["Order"]] = relationship(back_populates="user", lazy="selectin")

class Order(TimestampMixin, Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(20), default="pending")

    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")
```

## BaseRepository (Generic CRUD)

```python
from typing import TypeVar, Generic, Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T", bound=Base)

class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: type[T]):
        self.session = session
        self.model = model

    async def get_by_id(self, id: int) -> T | None:
        return await self.session.get(self.model, id)

    async def get_all(self, offset: int = 0, limit: int = 20) -> Sequence[T]:
        stmt = select(self.model).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count(self) -> int:
        stmt = select(func.count()).select_from(self.model)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def create(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: T) -> T:
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: T) -> None:
        await self.session.delete(entity)
        await self.session.flush()

# Concrete repository — extends with domain-specific queries
class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
```

## Transaction Management

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def transactional(session: AsyncSession):
    """Use as context manager for explicit transaction boundaries."""
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise

# Usage in service
async def transfer_funds(self, from_id: int, to_id: int, amount: Decimal):
    async with transactional(self.session) as session:
        sender = await self.repo.get_by_id(from_id)
        receiver = await self.repo.get_by_id(to_id)
        sender.balance -= amount
        receiver.balance += amount
```

### Session-per-Request Pattern (via Dependency)

```python
# In most cases, the DI-managed session handles commit/rollback:
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

## Eager Loading — Prevent N+1

```python
from sqlalchemy.orm import selectinload, joinedload

# selectinload — separate IN query (good for collections)
stmt = select(User).options(selectinload(User.orders)).where(User.id == user_id)

# joinedload — single JOIN query (good for single relationships)
stmt = select(Order).options(joinedload(Order.user)).where(Order.id == order_id)

# Nested eager loading
stmt = (
    select(User)
    .options(selectinload(User.orders).selectinload(Order.items))
    .where(User.id == user_id)
)
```

## Alembic Migrations

### Setup

```bash
alembic init alembic
```

```python
# alembic/env.py — async configuration
from app.models import Base
target_metadata = Base.metadata

# Use async engine
from sqlalchemy.ext.asyncio import create_async_engine

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    engine = create_async_engine(settings.database_url)
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()
```

### Common Commands

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "add users table"

# Apply all migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history --verbose
```

### Enum Handling in Migrations

```python
# When adding enum columns, create the type explicitly
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create enum type first
    status_enum = sa.Enum("pending", "active", "cancelled", name="order_status")
    status_enum.create(op.get_bind())

    op.add_column("orders", sa.Column("status", status_enum, nullable=False, server_default="pending"))

def downgrade():
    op.drop_column("orders", "status")
    sa.Enum(name="order_status").drop(op.get_bind())
```

## Connection Pooling

```python
engine = create_async_engine(
    settings.database_url,
    pool_size=5,             # steady-state connections
    max_overflow=10,         # burst connections above pool_size
    pool_timeout=30,         # seconds to wait for connection
    pool_recycle=1800,       # recycle connections after 30 min
    pool_pre_ping=True,      # test connection health before use
)
```
