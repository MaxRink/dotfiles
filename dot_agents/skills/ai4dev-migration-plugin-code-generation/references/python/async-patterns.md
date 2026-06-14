# Async Patterns

> Scope: asyncio fundamentals, concurrency primitives (TaskGroup, gather), sync-in-async bridging, and background task patterns for Python 3.11+ and FastAPI.

## asyncio Fundamentals

```python
import asyncio

# Coroutine — define with async def, call with await
async def fetch_data(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# Run from sync context (entry point only)
asyncio.run(fetch_data("https://api.example.com"))
```

## Concurrency with TaskGroup (3.11+)

```python
# TaskGroup — structured concurrency, auto-cancels on failure
async def fetch_all_data(user_id: int) -> UserDashboard:
    async with asyncio.TaskGroup() as tg:
        profile_task = tg.create_task(fetch_profile(user_id))
        orders_task = tg.create_task(fetch_orders(user_id))
        prefs_task = tg.create_task(fetch_preferences(user_id))

    # All tasks completed (or exception raised)
    return UserDashboard(
        profile=profile_task.result(),
        orders=orders_task.result(),
        preferences=prefs_task.result(),
    )
```

### asyncio.gather (Pre-3.11 or When Partial Failure OK)

```python
# gather — runs concurrently, return_exceptions prevents cancellation
results = await asyncio.gather(
    fetch_users(),
    fetch_orders(),
    return_exceptions=True,  # returns exceptions instead of raising
)

for result in results:
    if isinstance(result, Exception):
        logger.error("Task failed", error=str(result))
```

### When to Use Which

| Pattern | Use When |
|---------|----------|
| `TaskGroup` | All tasks must succeed (default), structured cancellation needed |
| `gather` | Partial failure OK (`return_exceptions=True`), simple fan-out |
| `await` sequential | Tasks depend on previous result |

## Semaphore — Rate Limiting Concurrent Work

```python
# Limit concurrent external API calls
semaphore = asyncio.Semaphore(10)

async def rate_limited_fetch(url: str) -> dict:
    async with semaphore:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()

# Fan out with bounded concurrency
async def fetch_many(urls: list[str]) -> list[dict]:
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(rate_limited_fetch(url)) for url in urls]
    return [t.result() for t in tasks]
```

## Sync in Async — run_in_executor

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

# For CPU-bound or blocking library calls
executor = ThreadPoolExecutor(max_workers=4)

async def process_image(data: bytes) -> bytes:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, _resize_sync, data)

def _resize_sync(data: bytes) -> bytes:
    """Pure sync function — runs in thread pool."""
    from PIL import Image
    import io
    img = Image.open(io.BytesIO(data))
    img.thumbnail((800, 800))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
```

## Async Context Managers and Generators

```python
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# Async context manager for resource lifecycle
@asynccontextmanager
async def managed_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    client = httpx.AsyncClient(timeout=30)
    try:
        yield client
    finally:
        await client.aclose()

# Async generator for streaming
async def stream_records(query) -> AsyncGenerator[Record, None]:
    async with get_session() as session:
        result = await session.stream(query)
        async for row in result:
            yield row
```

## Background Tasks

### FastAPI BackgroundTasks (In-Process)

```python
from fastapi import BackgroundTasks

async def send_welcome_email(email: str) -> None:
    """Fire-and-forget task after response is sent."""
    await email_client.send(to=email, template="welcome")

@router.post("/users", status_code=201)
async def create_user(
    payload: UserCreate,
    background_tasks: BackgroundTasks,
    service: UserService = Depends(get_user_service),
):
    user = await service.create(payload)
    background_tasks.add_task(send_welcome_email, user.email)
    return UserResponse.model_validate(user)
```

### Celery (Distributed Task Queue)

```python
# For long-running, distributed, or scheduled tasks
from celery import Celery

celery_app = Celery("worker", broker="redis://localhost:6379/0")

@celery_app.task
def generate_report(report_id: int) -> None:
    """Runs in a separate worker process."""
    ...

# Dispatch from FastAPI
@router.post("/reports")
async def create_report(payload: ReportCreate):
    report = await service.create(payload)
    generate_report.delay(report.id)  # async dispatch
    return {"id": report.id, "status": "processing"}
```

### ARQ (Async Alternative to Celery)

```python
# Lightweight async task queue built on Redis
from arq import create_pool
from arq.connections import RedisSettings

async def send_notification(ctx, user_id: int, message: str) -> None:
    await notification_service.send(user_id, message)

# Enqueue
redis = await create_pool(RedisSettings())
await redis.enqueue_job("send_notification", user_id=1, message="Hello")
```

### When to Use Which

| Pattern | Use When |
|---------|----------|
| `BackgroundTasks` | Quick tasks after response (email, logging), no retry needed |
| Celery | Distributed workers, scheduled jobs, retry policies, task chains |
| ARQ | Async-native, lightweight, Redis-backed, fewer deps than Celery |
