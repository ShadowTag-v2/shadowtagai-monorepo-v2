"""
Health check endpoint for service monitoring.

Provides:
- Service availability status
- API version information
- Current server timestamp
"""

from datetime import datetime

from fastapi import APIRouter

from app.config import settings
from app.models.schemas import HealthResponse

router = APIRouter(
    prefix="/health",
    tags=["health"],
    responses={
        200: {
            "description": "Service is healthy and operational",
            "model": HealthResponse,
        },
        500: {"description": "Service is experiencing issues"},
    },
)


@router.get(
    "",
    summary="Health check endpoint",
    description="""
    Verify that the API service is running and responsive.

    This endpoint is used by monitoring systems and load balancers to check
    service availability. It returns HTTP 200 if the service is healthy.

    **Use Cases:**
    - Service availability monitoring
    - Load balancer health checks
    - Deployment verification
    - System status dashboards
    """,
    response_model=HealthResponse,
    response_description="Service health information including status, timestamp, and version",
)
async def health_check() -> HealthResponse:
    """
    Check service health and return status information.

    Returns:
        HealthResponse: Service status, timestamp, and version

    Example Response:
        ```json
        {
            "status": "healthy",
            "timestamp": "2025-11-15T10:30:00.000000Z",
            "version": "1.0.0"
        }
        ```
    """
    return HealthResponse(
        status="healthy", timestamp=datetime.utcnow(), version=settings.APP_VERSION
    )
