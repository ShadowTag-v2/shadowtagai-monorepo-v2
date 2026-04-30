from enum import StrEnum

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/unified", tags=["Unified Ecosystem"])


class HealthStatus(StrEnum):
    """System health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
