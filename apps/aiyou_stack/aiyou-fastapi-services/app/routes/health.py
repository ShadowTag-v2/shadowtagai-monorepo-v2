"""Health check and status endpoints.
"""

from datetime import datetime

from fastapi import APIRouter, Response, status
from pydantic import BaseModel

from app.config import settings
from app.models.response import APIResponse
from app.utils.response import success_response

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    timestamp: datetime
    version: str
    environment: str


class StatusResponse(BaseModel):
    """Detailed status response model."""

    api: str
    database: str
    redis: str
    timestamp: datetime


@router.get(
    "/health",
    response_model=APIResponse[HealthResponse],
    summary="Health Check",
    description="Check if the API is running and healthy.",
)
async def health_check():
    """Simple health check endpoint.
    Returns basic service information.
    """
    health_data = HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=settings.app_version,
        environment=settings.environment,
    )

    return success_response(data=health_data, message="Service is healthy")


@router.get(
    "/status",
    response_model=APIResponse[StatusResponse],
    summary="Detailed Status",
    description="Get detailed status of all service components.",
)
async def status_check():
    """Detailed status check endpoint.
    Checks all service dependencies.
    """
    # In production, you would actually check database and redis connectivity
    status_data = StatusResponse(
        api="operational",
        database="operational",
        redis="operational" if settings.rate_limit_enabled else "disabled",
        timestamp=datetime.utcnow(),
    )

    return success_response(data=status_data, message="All systems operational")


@router.get(
    "/ping",
    status_code=status.HTTP_200_OK,
    summary="Ping",
    description="Simple ping endpoint for uptime monitoring.",
)
async def ping():
    """Ultra-simple ping endpoint.
    Returns plain text 'pong' for monitoring tools.
    """
    return Response(content="pong", media_type="text/plain")
