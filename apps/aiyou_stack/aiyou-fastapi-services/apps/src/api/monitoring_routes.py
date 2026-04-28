# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""FastAPI routes for monitoring, metrics, and alerting.

Endpoints:
- GET /api/dashboard - Unified metrics dashboard
- GET /api/dashboard/health - Health check with score
- GET /api/dashboard/sla - SLA compliance metrics
- GET /api/alerts - List active alerts
- POST /api/alerts/{alert_id}/acknowledge - Acknowledge alert
- POST /api/alerts/{alert_id}/resolve - Resolve alert
- POST /api/alerts/{alert_id}/snooze - Snooze alert
- GET /api/performance - Performance metrics
- GET /api/ml/anomalies - ML-detected anomalies
- GET /api/ml/predictions - ML predictions
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.alerts import AlertPriority, get_alerting_system
from src.dashboard import get_dashboard
from src.performance import performance_monitor

router = APIRouter(prefix="/api", tags=["monitoring"])


# Response models
class HealthResponse(BaseModel):
    """Health check response."""

    timestamp: str
    health_score: float
    status: str
    components: dict


class DashboardResponse(BaseModel):
    """Dashboard data response."""

    timestamp: str
    health_score: float
    status: str
    ingestion: dict
    performance: dict
    ml_insights: dict
    revenue: dict
    cost: dict
    alerts: dict
    trends: dict


class AlertResponse(BaseModel):
    """Alert response."""

    id: str
    timestamp: str
    title: str
    message: str
    priority: str
    category: str
    predicted_event: str
    predicted_time: str
    confidence: float
    time_to_event: float
    recommendations: list[str]
    acknowledged: bool
    resolved: bool


class AlertActionRequest(BaseModel):
    """Alert action request."""

    snooze_minutes: int | None = None


# Dashboard endpoints
@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard_data():
    """Get unified dashboard data.

    Returns complete system snapshot including:
    - Ingestion metrics
    - Performance metrics
    - ML insights
    - Revenue/usage
    - Cost tracking
    - Active alerts
    - Trends
    """
    dashboard = get_dashboard()
    await dashboard.get_current_snapshot()

    # Generate fresh alerts
    await get_alerting_system().check_and_alert()

    data = dashboard.get_dashboard_data()

    return DashboardResponse(**data)


@router.get("/dashboard/health", response_model=HealthResponse)
async def get_health_status():
    """Get system health status.

    Returns:
    - Overall health score (0-100)
    - Status (healthy/degraded/critical)
    - Component breakdown

    """
    dashboard = get_dashboard()
    snapshot = await dashboard.get_current_snapshot()

    return HealthResponse(
        timestamp=snapshot.timestamp.isoformat(),
        health_score=snapshot.health_score,
        status=snapshot.status,
        components={
            "ingestion": snapshot.ingestion.get("status", "unknown"),
            "performance": "healthy" if not snapshot.performance.get("bottlenecks") else "degraded",
            "ml": "healthy"
            if snapshot.ml_insights.get("critical_anomalies", 0) == 0
            else "degraded",
            "cost": snapshot.cost.get("status", "unknown"),
        },
    )


@router.get("/dashboard/sla")
async def get_sla_compliance():
    """Get SLA compliance metrics.

    Returns compliance status for:
    - Data quality (>15% Tier 1)
    - Cost control (<$77/month)
    - Performance (no critical bottlenecks)
    """
    dashboard = get_dashboard()
    return dashboard.get_sla_compliance()


# Alert endpoints
@router.get("/alerts", response_model=list[AlertResponse])
async def list_alerts(
    category: str | None = Query(
        None,
        description="Filter by category (cost, performance, quality, source_health)",
    ),
    priority: str | None = Query(None, description="Filter by priority (info, warning, critical)"),
):
    """List active predictive alerts.

    Query parameters:
    - category: Filter by alert category
    - priority: Filter by priority level

    Returns list of active alerts sorted by priority and time to event.
    """
    alerting = get_alerting_system()

    # Convert priority string to enum
    priority_enum = None
    if priority:
        try:
            priority_enum = AlertPriority[priority.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid priority: {priority}") from None

    alerts = alerting.get_active_alerts(category=category, priority=priority_enum)

    return [
        AlertResponse(
            id=a.id,
            timestamp=a.timestamp.isoformat(),
            title=a.title,
            message=a.message,
            priority=a.priority.value,
            category=a.category,
            predicted_event=a.predicted_event,
            predicted_time=a.predicted_time.isoformat(),
            confidence=a.confidence,
            time_to_event=a.time_to_event,
            recommendations=a.recommendations,
            acknowledged=a.acknowledged,
            resolved=a.resolved,
        )
        for a in alerts
    ]


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """Acknowledge an alert."""
    alerting = get_alerting_system()

    if alerting.acknowledge_alert(alert_id):
        return {"status": "success", "message": f"Alert {alert_id} acknowledged"}
    raise HTTPException(status_code=404, detail="Alert not found")


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Resolve an alert."""
    alerting = get_alerting_system()

    if alerting.resolve_alert(alert_id):
        return {"status": "success", "message": f"Alert {alert_id} resolved"}
    raise HTTPException(status_code=404, detail="Alert not found")


@router.post("/alerts/{alert_id}/snooze")
async def snooze_alert(alert_id: str, request: AlertActionRequest):
    """Snooze an alert for specified minutes."""
    if not request.snooze_minutes:
        raise HTTPException(status_code=400, detail="snooze_minutes required")

    alerting = get_alerting_system()

    if alerting.snooze_alert(alert_id, request.snooze_minutes):
        return {
            "status": "success",
            "message": f"Alert {alert_id} snoozed for {request.snooze_minutes} minutes",
        }
    raise HTTPException(status_code=404, detail="Alert not found")


@router.get("/alerts/stats")
async def get_alert_statistics():
    """Get alerting statistics."""
    alerting = get_alerting_system()
    return alerting.get_alert_stats()


# Performance endpoints
@router.get("/performance")
async def get_performance_metrics():
    """Get performance monitoring data.

    Returns:
    - Component statistics
    - Bottlenecks
    - System resources

    """
    return performance_monitor.generate_performance_report()


@router.get("/performance/components/{component_name}")
async def get_component_performance(component_name: str):
    """Get detailed performance stats for a specific component."""
    stats = performance_monitor.get_component_stats(component_name)

    if "error" in stats:
        raise HTTPException(status_code=404, detail=stats["error"])

    return stats


@router.get("/performance/bottlenecks")
async def get_performance_bottlenecks(threshold_ms: float = Query(1000.0)):
    """Get performance bottlenecks.

    Query parameters:
    - threshold_ms: Minimum average duration to be considered a bottleneck
    """
    return {
        "bottlenecks": performance_monitor.get_bottlenecks(threshold_ms),
        "threshold_ms": threshold_ms,
    }


# ML endpoints
@router.get("/ml/anomalies")
async def get_ml_anomalies(
    hours: int = Query(24, description="Hours of history to retrieve"),
    severity: str | None = Query(
        None,
        description="Filter by severity (low, medium, high, critical)",
    ),
):
    """Get ML-detected anomalies.

    Query parameters:
    - hours: How many hours of history to include
    - severity: Filter by severity level
    """
    # This would connect to actual ML detector instance
    # For now, return placeholder
    return {
        "message": "ML anomaly detection endpoint",
        "hours": hours,
        "severity": severity,
        "anomalies": [],
    }


@router.get("/ml/predictions")
async def get_ml_predictions():
    """Get ML predictions.

    Returns:
    - Cost predictions (end of month projection)
    - Source failure predictions
    - Quality trends

    """
    # This would connect to actual ML detector instance
    return {
        "cost_prediction": {
            "predicted_monthly_cost": 0.0,
            "confidence": 0.0,
            "budget": 77.0,
            "will_exceed": False,
        },
        "source_failures": {
            "at_risk_count": 0,
            "sources": [],
        },
        "quality_trend": {
            "current_tier1_pct": 0.0,
            "predicted_tier1_pct": 0.0,
            "trend": "stable",
        },
    }
