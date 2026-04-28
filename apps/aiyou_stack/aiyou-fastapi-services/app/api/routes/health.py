# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Health check endpoints"""

from datetime import datetime

from fastapi import APIRouter, status

from app.core.settings import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check if the service is running",
)
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Check if the service is ready to accept requests",
)
async def readiness_check():
    """Readiness check endpoint

    Verifies that all required dependencies and configurations are available
    """
    checks = {
        "api_key_configured": settings.ANTHROPIC_API_KEY is not None,
        "environment": settings.ENVIRONMENT,
    }

    all_ready = all(checks.values())

    return {
        "status": "ready" if all_ready else "not_ready",
        "checks": checks,
        "timestamp": datetime.now().isoformat(),
    }


@router.get(
    "/live",
    status_code=status.HTTP_200_OK,
    summary="Liveness check",
    description="Check if the service is alive",
)
async def liveness_check():
    """Liveness check for Kubernetes/container orchestration"""
    return {"status": "alive", "timestamp": datetime.now().isoformat()}
