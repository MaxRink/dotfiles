# FastAPI Security

> Scope: Authentication (JWT/OAuth2), authorization, CORS, rate limiting, input validation, SQL injection prevention, secrets management, and security headers for FastAPI applications.

## JWT Authentication

```python
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")

def verify_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id: int | None = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return TokenPayload(user_id=user_id, exp=payload["exp"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Current User Dependency

```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
) -> User:
    payload = verify_token(token)
    user = await user_service.get_by_id(payload.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user

async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
```

### Token Endpoint

```python
from fastapi.security import OAuth2PasswordRequestForm

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    user = await auth_service.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    access_token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=access_token, token_type="bearer")
```

## Password Hashing

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

## CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

# DEVELOPMENT — permissive (never in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PRODUCTION — restrictive
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,     # explicit whitelist
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600,                             # preflight cache 10 min
)
```

## Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Per-route limits
@router.post("/auth/token")
@limiter.limit("5/minute")
async def login(request: Request, ...): ...

@router.get("/users")
@limiter.limit("60/minute")
async def list_users(request: Request, ...): ...
```

## Input Validation

### Pydantic Validators — Defense in Depth

```python
from pydantic import BaseModel, Field, field_validator
import re

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def no_reserved_names(cls, v: str) -> str:
        reserved = {"admin", "root", "system", "api"}
        if v.lower() in reserved:
            raise ValueError("This username is reserved")
        return v
```

### Path Parameter Validation

```python
from fastapi import Path, Query

@router.get("/users/{user_id}")
async def get_user(
    user_id: int = Path(gt=0, description="User ID"),
): ...

@router.get("/search")
async def search(
    q: str = Query(min_length=1, max_length=200),
    limit: int = Query(default=20, ge=1, le=100),
): ...
```

## SQL Injection Prevention

```python
# ALWAYS use SQLAlchemy parameterized queries — NEVER string interpolation

# BAD
await session.execute(text(f"SELECT * FROM users WHERE id = {user_id}"))

# GOOD — parameterized
await session.execute(text("SELECT * FROM users WHERE id = :id"), {"id": user_id})

# BEST — use ORM queries (inherently parameterized)
stmt = select(User).where(User.id == user_id)
result = await session.execute(stmt)
```

## Secrets Management

```python
# NEVER hardcode secrets — use environment variables via pydantic-settings
class Settings(BaseSettings):
    secret_key: str                  # required, no default
    database_url: str                # required, no default
    api_key: str                     # required, no default

# .env file (never committed — add to .gitignore)
SECRET_KEY=your-secret-here
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db

# In docker-compose or CI, use environment variables or secret managers
```

## Security Headers Middleware

```python
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response
```

## Route Protection Patterns

```python
# Public route — no auth
@router.get("/health")
async def health(): ...

# Authenticated route
@router.get("/profile")
async def get_profile(user: User = Depends(get_current_user)): ...

# Admin-only route
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: User = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
): ...

# Resource-owner check
@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    ...
```
