"""
Health Check Endpoints

Operations:
- Kubernetes readiness/liveness probes
- Service monitoring
- Database connectivity check
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db

router = APIRouter()
settings = get_settings()


@router.get("/health")
async def health_check() -> dict:
    """
    Basic health check

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
async def readiness_check(db: AsyncSession = Depends(get_db)) -> dict:
    """
    Readiness check with database connectivity

    Operations:
    - Kubernetes readiness probe
    - Verifies database connection
    """
    try:
        # Check database connectivity
        result = await db.execute(text("SELECT 1"))
        result.scalar_one()

        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return {"status": "not_ready", "database": "disconnected", "error": str(e)}
