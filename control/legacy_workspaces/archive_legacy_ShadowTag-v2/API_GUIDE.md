# API Builder - Developer Guide

## Overview

This API Builder provides a complete, production-ready FastAPI framework with authentication, rate limiting, and beautiful documentation out of the box.

## Quick Start Examples

### 1. Authentication Flow

#### Register a User
```python
import requests

# Register new user
response = requests.post(
    "http://localhost:8000/api/v1/auth/register",
    json={
        "username": "developer",
        "email": "dev@example.com",
        "password": "SecurePass123!",
        "full_name": "John Developer"
    }
)
print(response.json())
```

#### Login and Get Tokens
```python
# Login to get access token
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    data={
        "username": "developer",
        "password": "SecurePass123!"
    }
)
tokens = response.json()["data"]["token"]
access_token = tokens["access_token"]
```

#### Use Access Token
```python
# Use the token to access protected endpoints
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(
    "http://localhost:8000/api/v1/auth/me",
    headers=headers
)
print(response.json())
```

### 2. API Key Authentication

```python
# Use API key for server-to-server communication
headers = {"X-API-Key": "your-api-key-here"}
response = requests.get(
    "http://localhost:8000/api/v1/users",
    headers=headers,
    params={"page": 1, "page_size": 10}
)
print(response.json())
```

### 3. Working with Paginated Responses

```python
# Get paginated list of users
response = requests.get(
    "http://localhost:8000/api/v1/users",
    headers={"X-API-Key": "your-api-key"},
    params={
        "page": 1,
        "page_size": 20,
        "search": "john",
        "is_active": True
    }
)

data = response.json()
users = data["data"]
pagination = data["pagination"]

print(f"Page {pagination['page']} of {pagination['total_pages']}")
print(f"Total users: {pagination['total_items']}")
print(f"Has next page: {pagination['has_next']}")
```

## Response Formats

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    "id": 1,
    "name": "Example"
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": "ValidationError",
  "message": "Invalid input data",
  "details": [
    {
      "field": "email",
      "message": "Invalid email format",
      "type": "value_error.email"
    }
  ],
  "path": "/api/v1/users"
}
```

### Paginated Response
```json
{
  "success": true,
  "message": "Retrieved 10 users",
  "data": [
    {"id": 1, "username": "user1"},
    {"id": 2, "username": "user2"}
  ],
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total_items": 50,
    "total_pages": 5,
    "has_next": true,
    "has_previous": false
  }
}
```

## Rate Limiting

### Default Limits
- **100 requests per 60 seconds** for regular endpoints
- **10 requests per minute** for destructive operations (delete, etc.)

### Rate Limit Headers
The API returns rate limit information in response headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

### Rate Limit Exceeded
```json
{
  "success": false,
  "error": "RateLimitExceeded",
  "message": "Too many requests. Please slow down.",
  "details": {
    "retry_after": "45 seconds",
    "limit": "100 requests per 60 seconds"
  },
  "path": "/api/v1/users"
}
```

## Creating New Endpoints

### Example: Create a New Resource

```python
# app/routes/products.py
from fastapi import APIRouter, Depends, status
from app.auth import get_current_active_user
from app.models.response import APIResponse
from app.utils.response import success_response
from pydantic import BaseModel

router = APIRouter(prefix="/products", tags=["Products"])


class Product(BaseModel):
    id: int
    name: str
    price: float
    description: str


@router.get(
    "",
    response_model=APIResponse[list[Product]],
    summary="List Products",
    description="Get all products"
)
async def list_products(
    current_user = Depends(get_current_active_user)
):
    products = [
        Product(id=1, name="Product 1", price=29.99, description="Description 1"),
        Product(id=2, name="Product 2", price=49.99, description="Description 2"),
    ]

    return success_response(
        data=products,
        message="Products retrieved successfully"
    )


@router.post(
    "",
    response_model=APIResponse[Product],
    status_code=status.HTTP_201_CREATED,
    summary="Create Product"
)
async def create_product(
    product: Product,
    current_user = Depends(get_current_active_user)
):
    # Save to database in production
    return success_response(
        data=product,
        message="Product created successfully"
    )
```

### Register the Router

```python
# app/main.py
from app.routes import products

app.include_router(products.router, prefix=settings.api_prefix)
```

## Database Operations

### Example: Query Users from Database

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_db, UserDB

async def get_users(db: AsyncSession):
    result = await db.execute(select(UserDB))
    users = result.scalars().all()
    return users
```

### Example: Create User in Database

```python
async def create_user(
    db: AsyncSession,
    username: str,
    email: str,
    hashed_password: str
):
    user = UserDB(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
```

## Testing

### Example Test

```python
# tests/test_auth.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_register_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "TestPass123!",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["username"] == "testuser"
```

## Best Practices

### 1. Always Use Type Hints
```python
from typing import List, Optional

async def get_users(
    page: int = 1,
    page_size: int = 10
) -> List[User]:
    ...
```

### 2. Use Pydantic for Validation
```python
from pydantic import BaseModel, Field, EmailStr

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
```

### 3. Use Dependency Injection
```python
from fastapi import Depends
from app.auth import get_current_active_user

@router.get("/protected")
async def protected_route(
    current_user = Depends(get_current_active_user)
):
    ...
```

### 4. Handle Errors Gracefully
```python
from fastapi import HTTPException, status

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await find_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    return success_response(data=user)
```

### 5. Use Response Models
```python
@router.get(
    "/users",
    response_model=PaginatedResponse[UserResponse]
)
async def list_users():
    ...
```

## Deployment Tips

1. **Security**: Change all default secrets in production
2. **Database**: Use connection pooling and proper indexes
3. **Caching**: Implement Redis caching for frequently accessed data
4. **Monitoring**: Add logging and error tracking (Sentry, etc.)
5. **Performance**: Use async operations for I/O-bound tasks
6. **Documentation**: Keep API documentation up to date

## Common Patterns

### Pattern 1: Pagination
```python
from app.utils.pagination import paginate

items = [...]  # Your data
paginated_data, pagination_meta = paginate(items, page=1, page_size=10)
return paginated_response(data=paginated_data, pagination=pagination_meta)
```

### Pattern 2: Error Handling
```python
from app.utils.response import error_response

try:
    result = await some_operation()
except ValueError as e:
    return error_response(
        error="ValueError",
        message=str(e),
        details={"field": "value"}
    )
```

### Pattern 3: Authentication
```python
# JWT Auth
@router.get("/me")
async def get_me(current_user = Depends(get_current_active_user)):
    return success_response(data=current_user)

# API Key Auth
@router.get("/public")
async def public_data(api_key = Depends(verify_api_key)):
    return success_response(data=data)
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Pydantic Documentation](https://docs.pydantic.dev)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org)
- [Alembic Documentation](https://alembic.sqlalchemy.org)

---

Need help? Check the main README.md or open an issue on GitHub.
