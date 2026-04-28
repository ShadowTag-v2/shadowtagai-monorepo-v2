# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Health check endpoints.

Provides endpoints for monitoring application health and readiness.
"""

from datetime import datetime

from fastapi import APIRouter, status
from pydantic import BaseModel

from src.core.config import settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    timestamp: datetime
    environment: str
    version: str


class ReadinessResponse(BaseModel):
    """Readiness check response model."""

    ready: bool
    checks: dict
    timestamp: datetime


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Returns the health status of the application",
)
async def health_check() -> HealthResponse:
    """Health check endpoint.

    Returns basic health information about the application.
    Used by Kubernetes liveness probes.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        environment=settings.ENVIRONMENT,
        version="1.0.0",
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness Check",
    description="Returns the readiness status of the application",
)
async def readiness_check() -> ReadinessResponse:
    """Readiness check endpoint.

    Verifies that the application is ready to serve traffic.
    Used by Kubernetes readiness probes.
    """
    checks = {
        "api": True,
        # Add more checks as needed:
        # "database": await check_database_connection(),
        # "cache": await check_cache_connection(),
        # "external_api": await check_external_api(),
    }

    ready = all(checks.values())

    return ReadinessResponse(
        ready=ready,
        checks=checks,
        timestamp=datetime.utcnow(),
    )
