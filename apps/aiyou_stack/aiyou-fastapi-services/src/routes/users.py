# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""User management API routes"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.user import UserCreate, UserResponse, UserUpdate
from src.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    """Create a new user

    Creates a user profile for tracking analytics.
    """
    # Check if user already exists
    existing_user = await UserService.get_user_by_id(db, user.user_id)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )

    created_user = await UserService.create_user(db, user)

    return created_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    """Get user by ID

    Retrieve detailed information about a specific user.
    """
    user = await UserService.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    """Update user information

    Update user properties, segment, cohort, or other attributes.
    """
    updated_user = await UserService.update_user(db, user_id, user_data)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return updated_user


@router.get("/", response_model=list[UserResponse])
async def list_users(
    segment: str = None,
    cohort: str = None,
    is_active: bool = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    """List users with filtering

    Retrieve a list of users, optionally filtered by segment, cohort, or active status.
    """
    users = await UserService.list_users(
        db,
        segment=segment,
        cohort=cohort,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )

    return users


@router.get("/meta/segments")
async def get_segments(db: AsyncSession = Depends(get_db)):  # noqa: B008
    """Get all user segments

    Returns a list of all unique user segments.
    """
    segments = await UserService.get_user_segments(db)

    return {"segments": segments}


@router.get("/meta/cohorts")
async def get_cohorts(db: AsyncSession = Depends(get_db)):  # noqa: B008
    """Get all user cohorts

    Returns a list of all unique user cohorts.
    """
    cohorts = await UserService.get_user_cohorts(db)

    return {"cohorts": cohorts}
