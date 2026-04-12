"""
Health Check Endpoints

Provides health and readiness checks for the service.
"""

import sys
from datetime import datetime

import psutil
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Basic health check endpoint.

    Returns:
        Health status and basic system information
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "shadowtag-v2-api",
        "version": "2.0.0",
    }


@router.get("/health/detailed")
async def detailed_health():
    """
    Detailed health check with system metrics.

    Returns:
        Comprehensive health status including resource usage
    """
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "shadowtag-v2-api",
        "version": "2.0.0",
        "system": {
            "python_version": sys.version,
            "cpu_percent": cpu_percent,
            "memory": {
                "total_mb": memory.total / (1024 * 1024),
                "available_mb": memory.available / (1024 * 1024),
                "percent_used": memory.percent,
            },
            "disk": {
                "total_gb": disk.total / (1024**3),
                "used_gb": disk.used / (1024**3),
                "free_gb": disk.free / (1024**3),
                "percent_used": disk.percent,
            },
        },
    }


@router.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint.

    Returns:
        Service readiness status
    """
    # TODO: Add checks for database connectivity, etc.
    return {"ready": True, "timestamp": datetime.utcnow().isoformat()}
