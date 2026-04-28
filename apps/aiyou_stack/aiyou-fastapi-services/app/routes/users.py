# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""User management endpoints.
Demonstrates pagination, filtering, and CRUD operations.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status

from app.auth import get_current_active_user, verify_api_key
from app.config import settings
from app.middleware.rate_limit import limiter
from app.models.response import APIResponse, PaginatedResponse
from app.models.user import User, UserResponse
from app.utils.pagination import paginate
from app.utils.response import paginated_response, success_response

router = APIRouter(prefix="/users", tags=["Users"])


# Mock user database
MOCK_USERS = [
    User(
        id=i,
        username=f"user{i}",
        email=f"user{i}@example.com",
        full_name=f"User {i}",
        is_active=True,
        is_superuser=False,
    )
    for i in range(1, 51)  # 50 mock users
]


@router.get(
    "",
    response_model=PaginatedResponse[UserResponse],
    summary="List Users",
    description="Get a paginated list of users. Supports filtering and sorting.",
)
@limiter.limit(f"{settings.rate_limit_times}/{settings.rate_limit_seconds}seconds")
async def list_users(
    request: Request,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 10,
    search: Annotated[str | None, Query(description="Search by username or email")] = None,
    is_active: Annotated[bool | None, Query(description="Filter by active status")] = None,
    api_key: Annotated[str | None, Depends(verify_api_key)] = None,
):
    """Get paginated list of users.

    Requires API key authentication.

    Query Parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 10, max: 100)
    - search: Search users by username or email
    - is_active: Filter by active status
    """
    # Filter users
    filtered_users = MOCK_USERS

    if search:
        search_lower = search.lower()
        filtered_users = [
            u
            for u in filtered_users
            if search_lower in u.username.lower() or search_lower in u.email.lower()
        ]

    if is_active is not None:
        filtered_users = [u for u in filtered_users if u.is_active == is_active]

    # Convert to UserResponse (exclude sensitive data)
    user_responses = [
        UserResponse(
            id=u.id,
            username=u.username,
            email=u.email,
            full_name=u.full_name,
            is_active=u.is_active,
            created_at=u.created_at or datetime.utcnow(),
        )
        for u in filtered_users
    ]

    # Paginate results
    paginated_data, pagination_meta = paginate(user_responses, page=page, page_size=page_size)

    return paginated_response(
        data=paginated_data,
        pagination=pagination_meta,
        message=f"Retrieved {len(paginated_data)} users",
    )


@router.get(
    "/{user_id}",
    response_model=APIResponse[UserResponse],
    summary="Get User by ID",
    description="Retrieve a specific user by their ID.",
)
@limiter.limit(f"{settings.rate_limit_times}/{settings.rate_limit_seconds}seconds")
async def get_user(
    request: Request,
    user_id: Annotated[int, Path(ge=1, description="User ID")],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Get user by ID.

    Requires JWT authentication.
    """
    # Find user
    user = next((u for u in MOCK_USERS if u.id == user_id), None)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    user_response = UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at or datetime.utcnow(),
    )

    return success_response(data=user_response, message="User retrieved successfully")


@router.delete(
    "/{user_id}",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Delete User",
    description="Delete a user by their ID.",
)
@limiter.limit("10/minute")  # Stricter rate limit for destructive operations
async def delete_user(
    request: Request,
    user_id: Annotated[int, Path(ge=1, description="User ID")],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Delete user by ID.

    Requires JWT authentication.
    Has stricter rate limiting (10 requests per minute).
    """
    # Check if user exists
    user = next((u for u in MOCK_USERS if u.id == user_id), None)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    # In production, delete from database
    # For demo, just remove from mock list
    MOCK_USERS.remove(user)

    return success_response(message=f"User {user_id} deleted successfully")


# Import at the end to avoid circular imports
from datetime import datetime  # noqa: E402
