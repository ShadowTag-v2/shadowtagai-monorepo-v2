"""
Monitoring endpoints for health checks, metrics, and observability.
"""

from fastapi import APIRouter, Response

from app.monitoring.alerts import alert_manager
from app.monitoring.health import health_check, readiness_check
from app.monitoring.metrics import get_metrics, get_metrics_content_type

router = APIRouter(tags=["monitoring"])


@router.get("/health", summary="Liveness Probe")
async def liveness() -> dict:
    """
    Liveness probe endpoint.

    Returns basic health status indicating the application is alive.
    Used by orchestrators (K8s, Docker) to determine if the app should be restarted.
    """
    return await health_check()


@router.get("/ready", summary="Readiness Probe")
async def readiness() -> dict:
    """
    Readiness probe endpoint.

    Returns comprehensive health status including all dependencies.
    Used by orchestrators to determine if the app can receive traffic.
    """
    return await readiness_check()


@router.get("/metrics", summary="Prometheus Metrics")
async def metrics() -> Response:
    """
    Prometheus metrics endpoint.

    Returns metrics in Prometheus text format for scraping.
    """
    metrics_data = get_metrics()
    return Response(content=metrics_data, media_type=get_metrics_content_type())


@router.get("/monitoring/alerts", summary="Recent Alerts")
async def get_alerts(limit: int = 100) -> dict:
    """
    Get recent alerts.

    Args:
        limit: Maximum number of alerts to return (default: 100)

    Returns:
        List of recent alerts
    """
    alerts = alert_manager.get_recent_alerts(limit=limit)
    return {"alerts": alerts, "total": len(alerts)}
