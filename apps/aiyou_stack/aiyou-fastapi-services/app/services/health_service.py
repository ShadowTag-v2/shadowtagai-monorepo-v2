"""
Health Service Layer

Encapsulates database connectivity checks for readiness probes.
Route handlers must delegate here — no raw DB calls in routes.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class HealthService:
    """Service layer for health and readiness checks."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_db_connectivity(self) -> dict:
        """Execute a SELECT 1 probe and return readiness status."""
        try:
            result = await self.db.execute(text("SELECT 1"))
            result.scalar_one()
            return {"status": "ready", "database": "connected"}
        except Exception as e:
            return {"status": "not_ready", "database": "disconnected", "error": str(e)}
