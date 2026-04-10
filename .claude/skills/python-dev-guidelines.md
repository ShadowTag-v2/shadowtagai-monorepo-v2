# Python Development Guidelines for PNKLN FastAPI Services

**Version**: 1.0.0
**Auto-activates**: When working with Python files, FastAPI routes, services, or API endpoints
**Scope**: Core Python/FastAPI development patterns for the PNKLN Core Stack

---

## Quick Reference

### Essential Commands
```bash
# Development server
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests with coverage (Judge #6: 98% required)
uv run pytest --cov --cov-fail-under=98 --cov-report=term-missing

# Format code
uv run ruff format .

# Type check (strict mode)
uv run mypy --strict .

# Lint
uv run ruff check .
```

### Project Structure
```
ShadowTag-v2-fastapi-services/
├── src/
│   ├── routes/          # FastAPI route handlers
│   ├── services/        # Business logic layer
│   ├── models/          # SQLAlchemy/Pydantic models
│   ├── schemas/         # Pydantic schemas for validation
│   ├── repositories/    # Database access layer
│   └── utils/           # Shared utilities
├── tests/               # Test files (mirror src/ structure)
├── configs/             # Configuration files
└── scripts/             # Utility scripts
```

---

## Core Principles

### 1. Type Hints Are Mandatory
Every function, method, and variable must have type hints. This is enforced by `mypy --strict`.

```python
# ✅ Good
def calculate_total(items: list[dict[str, Any]], tax_rate: float) -> Decimal:
    """Calculate total with tax."""
    subtotal = sum(Decimal(str(item["price"])) for item in items)
    return subtotal * (Decimal("1.0") + Decimal(str(tax_rate)))

# ❌ Bad - no type hints
def calculate_total(items, tax_rate):
    subtotal = sum(item["price"] for item in items)
    return subtotal * (1.0 + tax_rate)
```

### 2. Async/Await for I/O Operations
All database queries, API calls, and file operations must be async.

```python
# ✅ Good
async def get_user(user_id: int) -> User | None:
    async with get_db_session() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

# ❌ Bad - blocking I/O
def get_user(user_id: int) -> User | None:
    session = get_db_session()
    return session.query(User).filter(User.id == user_id).first()
```

### 3. Error Handling Is Non-Negotiable
Every external interaction (DB, API, file) must have proper error handling. See [error-handling.md](resources/python-dev-guidelines/error-handling.md) for comprehensive patterns.

```python
# ✅ Good
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

async def create_user(user_data: UserCreate) -> User:
    try:
        async with get_db_session() as session:
            user = User(**user_data.model_dump())
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
    except IntegrityError as e:
        logger.error(f"User creation failed: {e}")
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )
    except Exception as e:
        logger.exception("Unexpected error during user creation")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
```

### 4. Test-Driven Development (TDD)
Write tests BEFORE or alongside implementation. Coverage must be ≥98% (Judge #6 requirement).

```python
# tests/test_user_service.py
import pytest
from src.services.user_service import create_user
from src.schemas.user import UserCreate

@pytest.mark.asyncio
async def test_create_user_success():
    """Test successful user creation."""
    user_data = UserCreate(
        email="test@example.com",
        name="Test User"
    )

    user = await create_user(user_data)

    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.id is not None

@pytest.mark.asyncio
async def test_create_user_duplicate_email():
    """Test user creation with duplicate email."""
    user_data = UserCreate(email="existing@example.com", name="Test")

    with pytest.raises(HTTPException) as exc_info:
        await create_user(user_data)

    assert exc_info.value.status_code == 400
    assert "already exists" in exc_info.value.detail
```

---

## FastAPI Architecture Patterns

### Layered Architecture
Follow strict separation of concerns:

1. **Routes** (`src/routes/`): HTTP layer, request/response handling
2. **Services** (`src/services/`): Business logic, orchestration
3. **Repositories** (`src/repositories/`): Data access, queries
4. **Models** (`src/models/`): Database models (SQLAlchemy)
5. **Schemas** (`src/schemas/`): Pydantic models for validation

See [architecture.md](resources/python-dev-guidelines/architecture.md) for detailed patterns.

### Route Example
```python
# src/routes/users.py
from fastapi import APIRouter, Depends, HTTPException
from src.schemas.user import UserCreate, UserResponse
from src.services.user_service import UserService

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """
    Create a new user.

    Args:
        user_data: User creation data
        service: User service (injected)

    Returns:
        Created user

    Raises:
        HTTPException: 400 if user exists, 500 on server error
    """
    return await service.create_user(user_data)
```

### Service Example
```python
# src/services/user_service.py
from src.schemas.user import UserCreate, UserResponse
from src.repositories.user_repository import UserRepository
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user."""
        try:
            # Business logic here
            existing = await self.repository.get_by_email(user_data.email)
            if existing:
                raise HTTPException(400, "User already exists")

            user = await self.repository.create(user_data)
            return UserResponse.model_validate(user)

        except HTTPException:
            raise
        except Exception as e:
            logger.exception("User creation failed")
            raise HTTPException(500, "Internal server error")
```

### Repository Example
```python
# src/repositories/user_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.user import User
from src.schemas.user import UserCreate

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_data: UserCreate) -> User:
        """Create user in database."""
        user = User(**user_data.model_dump())
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
```

---

## Pydantic Schemas

### Request/Response Separation
```python
# src/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserBase(BaseModel):
    """Base user fields."""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)

class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    """User update schema (all fields optional)."""
    email: EmailStr | None = None
    name: str | None = Field(None, min_length=1, max_length=100)

class UserResponse(UserBase):
    """User response schema."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

---

## Dependency Injection

Use FastAPI's dependency injection for services, repositories, and database sessions.

```python
# src/dependencies.py
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import async_session_factory
from src.repositories.user_repository import UserRepository
from src.services.user_service import UserService

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with async_session_factory() as session:
        yield session

async def get_user_repository(
    session: AsyncSession = Depends(get_db_session)
) -> UserRepository:
    """Get user repository."""
    return UserRepository(session)

async def get_user_service(
    repository: UserRepository = Depends(get_user_repository)
) -> UserService:
    """Get user service."""
    return UserService(repository)
```

---

## Configuration Management

### Environment Variables
```python
# src/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings."""
    # Database
    database_url: str

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Google Cloud
    google_cloud_project: str
    vertex_ai_location: str = "us-central1"

    # Security
    secret_key: str

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings."""
    return Settings()
```

---

## Logging

### Structured Logging
```python
import logging
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger(__name__)

# Usage
logger.info("user_created", user_id=user.id, email=user.email)
logger.error("database_error", error=str(e), query=query)
```

---

## Testing Patterns

### Fixtures
```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from src.models.base import Base

@pytest.fixture
async def db_session() -> AsyncSession:
    """Create test database session."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        yield session

    await engine.dispose()

@pytest.fixture
def user_repository(db_session: AsyncSession) -> UserRepository:
    """Create user repository."""
    return UserRepository(db_session)
```

### Mock External Services
```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_vertex_ai_integration():
    """Test Vertex AI integration with mocking."""
    mock_model = AsyncMock()
    mock_model.predict.return_value = {"predictions": [0.95]}

    with patch("src.services.ml_service.get_model") as mock_get_model:
        mock_get_model.return_value = mock_model

        result = await ml_service.predict({"input": "test"})

        assert result["predictions"][0] == 0.95
        mock_model.predict.assert_called_once()
```

---

## Progressive Disclosure Resources

For detailed guidance on specific topics, see:

- **[architecture.md](resources/python-dev-guidelines/architecture.md)** - Detailed layered architecture patterns
- **[error-handling.md](resources/python-dev-guidelines/error-handling.md)** - Comprehensive error handling strategies
- **[testing.md](resources/python-dev-guidelines/testing.md)** - Testing patterns, fixtures, coverage strategies
- **[async-patterns.md](resources/python-dev-guidelines/async-patterns.md)** - Advanced async/await patterns
- **[database.md](resources/python-dev-guidelines/database.md)** - SQLAlchemy patterns, migrations, transactions
- **[api-design.md](resources/python-dev-guidelines/api-design.md)** - REST API design, versioning, documentation

---

## Common Pitfalls

### 1. Mixing Async and Sync Code
```python
# ❌ Bad - blocks event loop
async def get_data():
    with open("file.txt") as f:  # Blocking!
        return f.read()

# ✅ Good - uses async file I/O
async def get_data():
    async with aiofiles.open("file.txt") as f:
        return await f.read()
```

### 2. Not Using Context Managers for DB Sessions
```python
# ❌ Bad - session might not close
async def bad_query():
    session = get_session()
    result = await session.execute(query)
    return result

# ✅ Good - session always closes
async def good_query():
    async with get_db_session() as session:
        result = await session.execute(query)
        return result
```

### 3. Missing Type Hints on Returns
```python
# ❌ Bad - mypy can't verify
async def get_user(id: int):
    return await repository.get(id)

# ✅ Good - explicit return type
async def get_user(id: int) -> User | None:
    return await repository.get(id)
```

---

## Quality Checklist

Before committing code, verify:

- [ ] All functions have type hints
- [ ] All async operations use `await`
- [ ] Error handling covers all external interactions
- [ ] Tests written (coverage ≥98%)
- [ ] Docstrings on public functions
- [ ] No blocking I/O in async functions
- [ ] Database sessions use context managers
- [ ] Pydantic schemas for all API inputs/outputs
- [ ] Logging on error paths
- [ ] Configuration from environment variables

---

**Related Skills**: vertex-ai-workbench, testing-coverage, database-verification
**Hooks**: This skill auto-activates when editing Python files or when keywords like "fastapi", "route", "service" appear in prompts.
