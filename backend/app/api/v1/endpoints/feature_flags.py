# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Feature Flags API endpoints.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.release import (
    FeatureFlagCreate,
    FeatureFlagResponse,
    FeatureFlagUpdate,
    FeatureFlagListResponse,
    FeatureFlagEvaluation,
)
from app.services.feature_flags import feature_flag_service

router = APIRouter(prefix="/feature-flags", tags=["feature-flags"])


@router.post("", response_model=FeatureFlagResponse, status_code=201)
async def create_feature_flag(
    flag_data: FeatureFlagCreate,
    db: AsyncSession = Depends(get_db),
) -> FeatureFlagResponse:
    """
    Create a new feature flag.

    Args:
        flag_data: Feature flag creation data
        db: Database session

    Returns:
        Created feature flag
    """
    # Check if key already exists
    existing = await feature_flag_service.get_flag(db, flag_data.key)
    if existing:
        raise HTTPException(status_code=400, detail=f"Feature flag with key '{flag_data.key}' already exists")

    flag = await feature_flag_service.create_flag(db, flag_data)
    return FeatureFlagResponse.model_validate(flag)


@router.get("", response_model=FeatureFlagListResponse)
async def list_feature_flags(
    db: AsyncSession = Depends(get_db),
    environment: str | None = Query(None),
    enabled: bool | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> FeatureFlagListResponse:
    """
    List all feature flags with pagination.

    Args:
        db: Database session
        environment: Filter by environment
        enabled: Filter by enabled status
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        Paginated list of feature flags
    """
    flags, total = await feature_flag_service.list_flags(
        db,
        environment=environment,
        enabled=enabled,
        skip=skip,
        limit=limit,
    )

    return FeatureFlagListResponse(
        total=total,
        items=[FeatureFlagResponse.model_validate(f) for f in flags],
        page=skip // limit + 1,
        page_size=limit,
    )


@router.get("/{flag_key}", response_model=FeatureFlagResponse)
async def get_feature_flag(
    flag_key: str,
    db: AsyncSession = Depends(get_db),
) -> FeatureFlagResponse:
    """
    Get feature flag by key.

    Args:
        flag_key: Feature flag key
        db: Database session

    Returns:
        Feature flag details
    """
    flag = await feature_flag_service.get_flag(db, flag_key)
    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag not found")

    return FeatureFlagResponse.model_validate(flag)


@router.patch("/{flag_key}", response_model=FeatureFlagResponse)
async def update_feature_flag(
    flag_key: str,
    flag_data: FeatureFlagUpdate,
    db: AsyncSession = Depends(get_db),
) -> FeatureFlagResponse:
    """
    Update feature flag.

    Args:
        flag_key: Feature flag key
        flag_data: Feature flag update data
        db: Database session

    Returns:
        Updated feature flag
    """
    flag = await feature_flag_service.update_flag(db, flag_key, flag_data)
    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag not found")

    return FeatureFlagResponse.model_validate(flag)


@router.delete("/{flag_key}", status_code=204)
async def delete_feature_flag(
    flag_key: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete feature flag.

    Args:
        flag_key: Feature flag key
        db: Database session
    """
    success = await feature_flag_service.delete_flag(db, flag_key)
    if not success:
        raise HTTPException(status_code=404, detail="Feature flag not found")


@router.post("/{flag_key}/enable", response_model=FeatureFlagResponse)
async def enable_feature_flag(
    flag_key: str,
    percentage: int | None = Query(None, ge=0, le=100, description="Percentage rollout (0-100)"),
    db: AsyncSession = Depends(get_db),
) -> FeatureFlagResponse:
    """
    Enable a feature flag with optional percentage rollout.

    Args:
        flag_key: Feature flag key
        percentage: Percentage of users to enable for (0-100)
        db: Database session

    Returns:
        Updated feature flag
    """
    flag = await feature_flag_service.enable_flag(db, flag_key, percentage)
    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag not found")

    return FeatureFlagResponse.model_validate(flag)


@router.post("/{flag_key}/disable", response_model=FeatureFlagResponse)
async def disable_feature_flag(
    flag_key: str,
    db: AsyncSession = Depends(get_db),
) -> FeatureFlagResponse:
    """
    Disable a feature flag.

    Args:
        flag_key: Feature flag key
        db: Database session

    Returns:
        Updated feature flag
    """
    flag = await feature_flag_service.disable_flag(db, flag_key)
    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag not found")

    return FeatureFlagResponse.model_validate(flag)


@router.post("/{flag_key}/evaluate", response_model=FeatureFlagEvaluation)
async def evaluate_feature_flag(
    flag_key: str,
    user_id: str | None = Query(None, description="User ID for evaluation"),
    context: dict[str, Any] | None = None,
    db: AsyncSession = Depends(get_db),
) -> FeatureFlagEvaluation:
    """
    Evaluate if a feature flag is enabled for a user.

    Args:
        flag_key: Feature flag key
        user_id: User ID for percentage rollout
        context: Additional context for targeting rules
        db: Database session

    Returns:
        Feature flag evaluation result
    """
    flag = await feature_flag_service.get_flag(db, flag_key)
    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag not found")

    enabled = await feature_flag_service.is_enabled(db, flag_key, user_id, context)

    return FeatureFlagEvaluation(
        key=flag_key,
        enabled=enabled,
        percentage=flag.percentage,
        metadata={
            "status": flag.status.value,
            "environment": flag.environment,
        },
    )
