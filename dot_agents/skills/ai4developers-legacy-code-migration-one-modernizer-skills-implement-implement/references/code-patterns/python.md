# Python / FastAPI Code Patterns

## Project Structure

```
<service-name>/
├── pyproject.toml
├── Dockerfile
├── src/
│   └── <service_name>/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── routers/
│       │   └── orders.py
│       ├── services/
│       │   └── order_service.py
│       ├── domain/
│       │   ├── order.py
│       │   └── exceptions.py
│       ├── repositories/
│       │   └── order_repository.py
│       ├── schemas/
│       │   ├── requests.py
│       │   └── responses.py
│       └── events/
│           └── publisher.py
├── migrations/
│   └── versions/
│       └── 001_create_orders.py
└── tests/
    ├── conftest.py
    ├── test_order_service.py
    └── test_orders_api.py
```

## Domain Model

```python
from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum
from datetime import datetime


class OrderStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@dataclass
class Order:
    id: int | None = None
    customer_id: str = ""
    total: Decimal = Decimal("0")
    status: OrderStatus = OrderStatus.PENDING
    lines: list["OrderLine"] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class OrderLine:
    product_id: str
    quantity: int
    price: Decimal
```

## Repository

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, order: Order) -> Order:
        entity = OrderEntity(**order.__dict__)
        self._session.add(entity)
        await self._session.flush()
        order.id = entity.id
        return order

    async def find_by_id(self, order_id: int) -> Order | None:
        result = await self._session.execute(select(OrderEntity).where(OrderEntity.id == order_id))
        entity = result.scalar_one_or_none()
        return entity.to_domain() if entity else None

    async def find_by_customer(self, customer_id: str) -> list[Order]:
        result = await self._session.execute(
            select(OrderEntity).where(OrderEntity.customer_id == customer_id)
        )
        return [e.to_domain() for e in result.scalars()]
```

## Service

```python
class OrderService:
    def __init__(self, repo: OrderRepository, validator: OrderValidator, publisher: EventPublisher):
        self._repo = repo
        self._validator = validator
        self._publisher = publisher

    # Implements: BR-001
    async def create_order(self, request: CreateOrderRequest) -> Order:
        await self._validator.validate_credit_limit(request)

        order = Order(
            customer_id=request.customer_id,
            total=sum(line.price * line.quantity for line in request.lines),
            status=OrderStatus.PENDING,
            lines=[OrderLine(l.product_id, l.quantity, l.price) for l in request.lines],
        )

        order = await self._repo.create(order)
        await self._publisher.publish("orders.created", {"order_id": order.id, "customer_id": order.customer_id})
        return order
```

## Router (FastAPI)

```python
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=OrderResponse)
async def create_order(request: CreateOrderRequest, service: OrderService = Depends(get_order_service)):
    try:
        order = await service.create_order(request)
        return OrderResponse.from_domain(order)
    except CreditLimitExceededError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, service: OrderService = Depends(get_order_service)):
    order = await service.find_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderResponse.from_domain(order)
```

## Schemas (Pydantic)

```python
from pydantic import BaseModel, Field
from decimal import Decimal


class OrderLineRequest(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)
    price: Decimal = Field(gt=0)


class CreateOrderRequest(BaseModel):
    customer_id: str = Field(min_length=1)
    lines: list[OrderLineRequest] = Field(min_length=1)


class OrderResponse(BaseModel):
    id: int
    customer_id: str
    total: Decimal
    status: str
    created_at: str

    @classmethod
    def from_domain(cls, order: Order) -> "OrderResponse":
        return cls(
            id=order.id, customer_id=order.customer_id,
            total=order.total, status=order.status.value,
            created_at=order.created_at.isoformat(),
        )
```

## Exceptions

```python
class CreditLimitExceededError(Exception):
    def __init__(self, customer_id: str, requested: Decimal, available: Decimal):
        self.customer_id = customer_id
        self.requested = requested
        self.available = available
        super().__init__(f"Credit limit exceeded for {customer_id}: requested {requested}, available {available}")
```

## Tests (pytest)

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal


@pytest.fixture
def order_service():
    repo = AsyncMock(spec=OrderRepository)
    validator = AsyncMock(spec=OrderValidator)
    publisher = AsyncMock(spec=EventPublisher)
    return OrderService(repo, validator, publisher)


# Covers: TC-001
@pytest.mark.asyncio
async def test_create_order_valid_request(order_service):
    order_service._repo.create.return_value = Order(id=1, customer_id="CUST-1", total=Decimal("100"), status=OrderStatus.PENDING)

    request = CreateOrderRequest(customer_id="CUST-1", lines=[OrderLineRequest(product_id="P1", quantity=2, price=Decimal("50"))])
    result = await order_service.create_order(request)

    assert result.status == OrderStatus.PENDING
    order_service._publisher.publish.assert_called_once()


# Covers: TC-002
@pytest.mark.asyncio
async def test_create_order_credit_exceeded(order_service):
    order_service._validator.validate_credit_limit.side_effect = CreditLimitExceededError("CUST-1", Decimal("300"), Decimal("200"))

    request = CreateOrderRequest(customer_id="CUST-1", lines=[OrderLineRequest(product_id="P1", quantity=100, price=Decimal("500"))])

    with pytest.raises(CreditLimitExceededError):
        await order_service.create_order(request)
```
