# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Release Manager API endpoints.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.release import DeploymentStatus
from app.schemas.release import (
    ReleaseCreate,
    ReleaseResponse,
    ReleaseUpdate,
    ReleaseListResponse,
    DeploymentCreate,
    DeploymentResponse,
    DeploymentListResponse,
    RollbackRequest,
    RollbackResponse,
    HealthCheckResult,
)
from app.services.release_manager import release_manager_service
from app.core.logger import logger

router = APIRouter(prefix="/releases", tags=["releases"])


# ==================== Release Endpoints ====================


@router.post("", response_model=ReleaseResponse, status_code=201)
async def create_release(
    release_data: ReleaseCreate,
    db: AsyncSession = Depends(get_db),
) -> ReleaseResponse:
    """
    Create a new release.

    Args:
        release_data: Release creation data
        db: Database session

    Returns:
        Created release
    """
    # Check if version already exists
    existing = await release_manager_service.get_release_by_version(db, release_data.version)
    if existing:
        raise HTTPException(status_code=400, detail=f"Release version {release_data.version} already exists")

    release = await release_manager_service.create_release(db, release_data)
    return ReleaseResponse.model_validate(release)


@router.get("", response_model=ReleaseListResponse)
async def list_releases(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
) -> ReleaseListResponse:
    """
    List all releases with pagination.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        active_only: Filter for active releases only

    Returns:
        Paginated list of releases
    """
    releases, total = await release_manager_service.list_releases(
        db,
        skip=skip,
        limit=limit,
        active_only=active_only,
    )

    return ReleaseListResponse(
        total=total,
        items=[ReleaseResponse.model_validate(r) for r in releases],
        page=skip // limit + 1,
        page_size=limit,
    )


@router.get("/{release_id}", response_model=ReleaseResponse)
async def get_release(
    release_id: int,
    db: AsyncSession = Depends(get_db),
) -> ReleaseResponse:
    """
    Get release by ID.

    Args:
        release_id: Release ID
        db: Database session

    Returns:
        Release details
    """
    release = await release_manager_service.get_release(db, release_id)
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")

    return ReleaseResponse.model_validate(release)


@router.patch("/{release_id}", response_model=ReleaseResponse)
async def update_release(
    release_id: int,
    release_data: ReleaseUpdate,
    db: AsyncSession = Depends(get_db),
) -> ReleaseResponse:
    """
    Update release.

    Args:
        release_id: Release ID
        release_data: Release update data
        db: Database session

    Returns:
        Updated release
    """
    release = await release_manager_service.update_release(db, release_id, release_data)
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")

    return ReleaseResponse.model_validate(release)


@router.post("/{release_id}/activate", response_model=ReleaseResponse)
async def activate_release(
    release_id: int,
    db: AsyncSession = Depends(get_db),
) -> ReleaseResponse:
    """
    Set release as active.

    Args:
        release_id: Release ID
        db: Database session

    Returns:
        Activated release
    """
    release = await release_manager_service.set_active_release(db, release_id)
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")

    return ReleaseResponse.model_validate(release)


# ==================== Deployment Endpoints ====================


@router.post("/deployments", response_model=DeploymentResponse, status_code=201)
async def create_deployment(
    deployment_data: DeploymentCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> DeploymentResponse:
    """
    Create and execute a deployment.

    Args:
        deployment_data: Deployment creation data
        background_tasks: Background tasks
        db: Database session

    Returns:
        Created deployment (execution happens in background)
    """
    # Verify release exists
    release = await release_manager_service.get_release(db, deployment_data.release_id)
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")

    # Create deployment
    deployment = await release_manager_service.create_deployment(db, deployment_data)

    # Execute deployment in background
    background_tasks.add_task(
        _execute_deployment_background,
        deployment.id,
    )

    return DeploymentResponse.model_validate(deployment)


async def _execute_deployment_background(deployment_id: int):
    """Background task to execute deployment."""
    from app.database.session import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        try:
            await release_manager_service.deploy(db, deployment_id)
        except Exception as e:
            logger.error(f"Background deployment error: {e}")


@router.get("/deployments", response_model=DeploymentListResponse)
async def list_deployments(
    db: AsyncSession = Depends(get_db),
    environment: str | None = Query(None),
    release_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> DeploymentListResponse:
    """
    List deployments with optional filters.

    Args:
        db: Database session
        environment: Filter by environment
        release_id: Filter by release ID
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        Paginated list of deployments
    """
    deployments, total = await release_manager_service.list_deployments(
        db,
        environment=environment,
        release_id=release_id,
        skip=skip,
        limit=limit,
    )

    return DeploymentListResponse(
        total=total,
        items=[DeploymentResponse.model_validate(d) for d in deployments],
        page=skip // limit + 1,
        page_size=limit,
    )


@router.get("/deployments/{deployment_id}", response_model=DeploymentResponse)
async def get_deployment(
    deployment_id: int,
    db: AsyncSession = Depends(get_db),
) -> DeploymentResponse:
    """
    Get deployment by ID.

    Args:
        deployment_id: Deployment ID
        db: Database session

    Returns:
        Deployment details
    """
    deployment = await release_manager_service.get_deployment(db, deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    return DeploymentResponse.model_validate(deployment)


# ==================== Rollback Endpoints ====================


@router.post("/deployments/{deployment_id}/rollback", response_model=RollbackResponse)
async def rollback_deployment(
    deployment_id: int,
    rollback_data: RollbackRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> RollbackResponse:
    """
    Rollback a deployment to the previous stable release.

    Args:
        deployment_id: Deployment ID to rollback
        rollback_data: Rollback request data
        background_tasks: Background tasks
        db: Database session

    Returns:
        Rollback response with new deployment
    """
    # Verify deployment exists
    deployment = await release_manager_service.get_deployment(db, deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    # Check deployment status
    if deployment.status not in [DeploymentStatus.DEPLOYED, DeploymentStatus.FAILED]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot rollback deployment with status: {deployment.status}",
        )

    try:
        # Execute rollback
        rollback_deployment = await release_manager_service.rollback_deployment(
            db,
            deployment_id,
            reason=rollback_data.reason,
            force=rollback_data.force,
        )

        return RollbackResponse(
            success=rollback_deployment.status == DeploymentStatus.DEPLOYED,
            rollback_deployment_id=rollback_deployment.id,
            message="Rollback initiated successfully" if rollback_deployment.status == DeploymentStatus.DEPLOYED else "Rollback failed",
            previous_deployment=DeploymentResponse.model_validate(deployment),
            new_deployment=DeploymentResponse.model_validate(rollback_deployment),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Rollback error: {e}")
        raise HTTPException(status_code=500, detail="Rollback failed")


# ==================== Health Check Endpoints ====================


@router.post("/health-check", response_model=HealthCheckResult)
async def perform_health_check(
    service_url: str = Query(..., description="Service URL to health check"),
    health_endpoint: str = Query("/health", description="Health check endpoint"),
) -> HealthCheckResult:
    """
    Perform health check on a service.

    Args:
        service_url: Base URL of the service
        health_endpoint: Health check endpoint path

    Returns:
        Health check result
    """
    result = await release_manager_service.perform_health_check(
        service_url,
        health_endpoint,
    )
    return result
