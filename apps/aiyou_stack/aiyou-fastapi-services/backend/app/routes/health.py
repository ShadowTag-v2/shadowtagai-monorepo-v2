"""Health check endpoints.
"""

from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["health"])


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    timestamp: datetime
    version: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint.
    """
    return HealthResponse(status="healthy", timestamp=datetime.utcnow(), version="1.0.0")


@router.get("/", response_model=dict)
async def root():
    """Root endpoint.
    """
    return {
        "message": "AI Issue Chat Workflow API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }
