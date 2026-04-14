"""Health Check Endpoints

Operations:
- Kubernetes readiness/liveness probes
- Service monitoring
- Database connectivity check
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db
from app.services.health_service import HealthService

router = APIRouter()
settings = get_settings()


def get_health_service(db: AsyncSession = Depends(get_db)) -> HealthService:
    """Dependency to get HealthService instance."""
    return HealthService(db)


@router.get("/health")
async def health_check() -> dict:
    """Basic health check

    Operations:
    - Used by load balancers
    - No authentication required
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
    }


@router.get("/readiness")
async def readiness_check(service: HealthService = Depends(get_health_service)) -> dict:
    """Readiness check with database connectivity

    Operations:
    - Kubernetes readiness probe
    - Verifies database connection
    """
    return await service.check_db_connectivity()
