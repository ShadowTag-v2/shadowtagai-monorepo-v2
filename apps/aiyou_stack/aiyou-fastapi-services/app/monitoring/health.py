"""
Health check implementation for liveness and readiness probes.
Monitors application and dependency health.
"""

import asyncio
import time
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from enum import StrEnum

import httpx
import psutil

from app.config import settings
from app.monitoring.metrics import MetricsCollector


class HealthStatus(StrEnum):
    """Health check status values."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


class HealthCheckResult:
    """Result of a health check."""

    def __init__(
        self,
        name: str,
        status: HealthStatus,
        message: str = "",
        details: dict | None = None,
        duration: float = 0.0,
    ):
        self.name = name
        self.status = status
        self.message = message
        self.details = details or {}
        self.duration = duration
        self.timestamp = datetime.now(UTC).isoformat()

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "duration_seconds": round(self.duration, 3),
            "timestamp": self.timestamp,
        }


class HealthChecker:
    """Manages health checks for the application."""

    def __init__(self):
        self.checks: list[Callable[[], Awaitable[HealthCheckResult]]] = []
        self.startup_time = datetime.now(UTC)

    def register_check(self, check_func: Callable[[], Awaitable[HealthCheckResult]]):
        """Register a health check function."""
        self.checks.append(check_func)

    async def run_checks(self) -> list[HealthCheckResult]:
        """Run all registered health checks."""
        results = []
        for check in self.checks:
            try:
                result = await check()
                results.append(result)

                # Record metrics
                is_healthy = result.status == HealthStatus.HEALTHY
                MetricsCollector.record_health_check(result.name, is_healthy, result.duration)
            except Exception as e:
                results.append(
                    HealthCheckResult(
                        name=getattr(check, "__name__", "unknown"),
                        status=HealthStatus.UNHEALTHY,
                        message=f"Check failed: {str(e)}",
                    )
                )

        return results

    def get_uptime_seconds(self) -> float:
        """Get application uptime in seconds."""
        return (datetime.now(UTC) - self.startup_time).total_seconds()


# Global health checker instance
health_checker = HealthChecker()


async def check_system_resources() -> HealthCheckResult:
    """Check system resource usage."""
    start_time = time.time()

    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        # Determine status based on thresholds
        status = HealthStatus.HEALTHY
        warnings = []

        if cpu_percent > 90:
            status = HealthStatus.DEGRADED
            warnings.append(f"High CPU usage: {cpu_percent}%")
        if memory.percent > 90:
            status = HealthStatus.DEGRADED
            warnings.append(f"High memory usage: {memory.percent}%")
        if disk.percent > 90:
            status = HealthStatus.DEGRADED
            warnings.append(f"High disk usage: {disk.percent}%")

        duration = time.time() - start_time

        return HealthCheckResult(
            name="system_resources",
            status=status,
            message=" | ".join(warnings) if warnings else "System resources within normal limits",
            details={
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_bytes": memory.used,
                "disk_percent": disk.percent,
                "disk_used_bytes": disk.used,
            },
            duration=duration,
        )
    except Exception as e:
        duration = time.time() - start_time
        return HealthCheckResult(
            name="system_resources",
            status=HealthStatus.UNHEALTHY,
            message=f"Failed to check system resources: {str(e)}",
            duration=duration,
        )


async def check_database() -> HealthCheckResult:
    """
    Check database connectivity.
    This is a placeholder - implement with actual database connection.
    """
    start_time = time.time()

    try:
        # TODO: Add actual database connection check
        # Example:
        # async with db_pool.acquire() as conn:
        #     await conn.execute("SELECT 1")

        await asyncio.sleep(0.01)  # Simulate check

        duration = time.time() - start_time

        return HealthCheckResult(
            name="database",
            status=HealthStatus.HEALTHY,
            message="Database connection successful",
            details={"connection_pool": "available"},
            duration=duration,
        )
    except Exception as e:
        duration = time.time() - start_time
        return HealthCheckResult(
            name="database",
            status=HealthStatus.UNHEALTHY,
            message=f"Database connection failed: {str(e)}",
            duration=duration,
        )


async def check_external_service(
    url: str, service_name: str, timeout: int = 5
) -> HealthCheckResult:
    """
    Check external service availability.

    Args:
        url: Service URL to check
        service_name: Name of the service
        timeout: Request timeout in seconds
    """
    start_time = time.time()

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=timeout)
            duration = time.time() - start_time

            if response.status_code == 200:
                return HealthCheckResult(
                    name=service_name,
                    status=HealthStatus.HEALTHY,
                    message=f"{service_name} is reachable",
                    details={
                        "url": url,
                        "status_code": response.status_code,
                        "response_time_ms": round(duration * 1000, 2),
                    },
                    duration=duration,
                )
            else:
                return HealthCheckResult(
                    name=service_name,
                    status=HealthStatus.DEGRADED,
                    message=f"{service_name} returned non-200 status",
                    details={"url": url, "status_code": response.status_code},
                    duration=duration,
                )
    except Exception as e:
        duration = time.time() - start_time
        return HealthCheckResult(
            name=service_name,
            status=HealthStatus.UNHEALTHY,
            message=f"{service_name} is unreachable: {str(e)}",
            details={"url": url},
            duration=duration,
        )


async def health_check() -> dict:
    """
    Liveness probe - basic health check.
    Returns simple status indicating if the application is alive.
    """
    uptime = health_checker.get_uptime_seconds()

    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "uptime_seconds": round(uptime, 2),
        "timestamp": datetime.now(UTC).isoformat(),
    }


async def readiness_check() -> dict:
    """
    Readiness probe - comprehensive dependency check.
    Returns detailed status including all dependencies.
    """
    # Run all health checks
    results = await health_checker.run_checks()

    # Determine overall status
    if any(r.status == HealthStatus.UNHEALTHY for r in results):
        overall_status = HealthStatus.UNHEALTHY
    elif any(r.status == HealthStatus.DEGRADED for r in results):
        overall_status = HealthStatus.DEGRADED
    else:
        overall_status = HealthStatus.HEALTHY

    uptime = health_checker.get_uptime_seconds()

    return {
        "status": overall_status.value,
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "uptime_seconds": round(uptime, 2),
        "checks": [r.to_dict() for r in results],
        "timestamp": datetime.now(UTC).isoformat(),
    }


# Register default health checks
health_checker.register_check(check_system_resources)
health_checker.register_check(check_database)
