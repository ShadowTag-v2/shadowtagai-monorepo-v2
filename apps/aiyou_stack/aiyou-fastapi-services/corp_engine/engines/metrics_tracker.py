"""
Metrics Tracker
================
Enforces the "Ever Upward Sloping Graph" doctrine.
Intervention triggered if trajectory <= 0.

Stay Current Doctrine:
- Metrics must always trend positive
- Flat is unacceptable - growth or investigation
- Negative triggers immediate intervention
"""

import asyncio
import logging
import statistics
from collections import deque
from collections.abc import Callable
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MetricType(StrEnum):
    """Types of metrics tracked"""

    REVENUE = "revenue"
    COST_SAVINGS = "cost_savings"
    EFFICIENCY = "efficiency"
    USER_SATISFACTION = "user_satisfaction"
    API_PERFORMANCE = "api_performance"
    COMPLIANCE_SCORE = "compliance_score"
    VALUE_ADDED = "value_added"
    UPTIME = "uptime"


class TrajectoryStatus(StrEnum):
    """Status of metric trajectory"""

    STRONG_GROWTH = "strong_growth"  # > 5% growth
    GROWTH = "growth"  # 1-5% growth
    STABLE = "stable"  # 0-1% growth (warning zone)
    FLAT = "flat"  # 0% growth (intervention needed)
    DECLINING = "declining"  # Negative (critical)


class MetricDataPoint(BaseModel):
    """Single metric measurement"""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    value: float
    metric_type: MetricType
    tenant_id: str
    source: str  # What generated this metric


class TrajectoryAnalysis(BaseModel):
    """Analysis of metric trajectory"""

    metric_type: MetricType
    current_value: float
    previous_value: float
    change_percent: float
    trajectory: TrajectoryStatus
    trend_direction: str  # "up", "down", "flat"
    moving_average_7d: float
    moving_average_30d: float
    requires_intervention: bool
    intervention_reason: str | None = None


class TenantMetrics(BaseModel):
    """Aggregated metrics for a tenant"""

    tenant_id: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Current values
    total_value_added_usd: float = 0.0
    revenue_impact_usd: float = 0.0
    cost_savings_usd: float = 0.0
    efficiency_score: float = 100.0
    compliance_score: float = 100.0

    # Trajectory
    overall_trajectory: TrajectoryStatus = TrajectoryStatus.GROWTH
    metrics_requiring_attention: list[str] = Field(default_factory=list)

    # Historical
    days_of_data: int = 0
    all_time_value_usd: float = 0.0


class MetricsTracker:
    """
    The Ever-Upward Guardian.

    Core Doctrine:
    - All metrics must trend upward
    - Flat (<=0% growth) triggers intervention
    - Automatic alerts to Economic Juggernaut
    - Dashboard always shows positive trajectory

    Intervention Protocol:
    1. Flat for 24h → Alert
    2. Flat for 48h → Economic Juggernaut analysis
    3. Flat for 72h → Escalate to governance
    4. Declining → Immediate intervention
    """

    WINDOW_SIZE = 30  # Days of data to keep
    ALERT_THRESHOLD_HOURS = 24

    def __init__(self):
        self._metrics: dict[str, dict[MetricType, deque]] = {}  # tenant_id -> type -> points
        self._tenant_summaries: dict[str, TenantMetrics] = {}
        self._intervention_callbacks: list[Callable] = []
        self._alert_callbacks: list[Callable] = []
        self._running = False

    # =========================================================================
    # Recording Metrics
    # =========================================================================

    def record(
        self, tenant_id: str, metric_type: MetricType, value: float, source: str = "system"
    ) -> MetricDataPoint:
        """Record a metric data point"""
        point = MetricDataPoint(
            value=value,
            metric_type=metric_type,
            tenant_id=tenant_id,
            source=source,
        )

        # Initialize storage if needed
        if tenant_id not in self._metrics:
            self._metrics[tenant_id] = {}
        if metric_type not in self._metrics[tenant_id]:
            self._metrics[tenant_id][metric_type] = deque(maxlen=self.WINDOW_SIZE * 24)

        self._metrics[tenant_id][metric_type].append(point)

        # Update summary
        self._update_tenant_summary(tenant_id)

        # Check trajectory
        asyncio.create_task(self._check_trajectory(tenant_id, metric_type))

        return point

    def record_batch(
        self, tenant_id: str, metrics: dict[MetricType, float], source: str = "system"
    ) -> list[MetricDataPoint]:
        """Record multiple metrics at once"""
        points = []
        for metric_type, value in metrics.items():
            point = self.record(tenant_id, metric_type, value, source)
            points.append(point)
        return points

    # =========================================================================
    # Trajectory Analysis
    # =========================================================================

    def analyze_trajectory(self, tenant_id: str, metric_type: MetricType) -> TrajectoryAnalysis:
        """Analyze the trajectory of a specific metric"""
        points = self._get_points(tenant_id, metric_type)

        if len(points) < 2:
            return TrajectoryAnalysis(
                metric_type=metric_type,
                current_value=points[-1].value if points else 0.0,
                previous_value=0.0,
                change_percent=0.0,
                trajectory=TrajectoryStatus.STABLE,
                trend_direction="flat",
                moving_average_7d=points[-1].value if points else 0.0,
                moving_average_30d=points[-1].value if points else 0.0,
                requires_intervention=False,
            )

        current = points[-1].value
        previous = points[-2].value

        # Calculate change
        change_pct = ((current - previous) / previous * 100) if previous != 0 else 0.0

        # Calculate moving averages
        ma_7d = self._calculate_moving_average(points, 7)
        ma_30d = self._calculate_moving_average(points, 30)

        # Determine trajectory
        trajectory = self._determine_trajectory(change_pct)

        # Determine if intervention needed
        requires_intervention = trajectory in [TrajectoryStatus.FLAT, TrajectoryStatus.DECLINING]
        intervention_reason = None
        if trajectory == TrajectoryStatus.FLAT:
            intervention_reason = "Metric growth has stalled - investigation required"
        elif trajectory == TrajectoryStatus.DECLINING:
            intervention_reason = "CRITICAL: Metric is declining - immediate action required"

        return TrajectoryAnalysis(
            metric_type=metric_type,
            current_value=current,
            previous_value=previous,
            change_percent=change_pct,
            trajectory=trajectory,
            trend_direction="up" if change_pct > 0 else ("down" if change_pct < 0 else "flat"),
            moving_average_7d=ma_7d,
            moving_average_30d=ma_30d,
            requires_intervention=requires_intervention,
            intervention_reason=intervention_reason,
        )

    def _determine_trajectory(self, change_pct: float) -> TrajectoryStatus:
        """Determine trajectory status from change percentage"""
        if change_pct > 5.0:
            return TrajectoryStatus.STRONG_GROWTH
        elif change_pct > 1.0:
            return TrajectoryStatus.GROWTH
        elif change_pct > 0.0:
            return TrajectoryStatus.STABLE
        elif change_pct == 0.0:
            return TrajectoryStatus.FLAT
        else:
            return TrajectoryStatus.DECLINING

    def _calculate_moving_average(self, points: list[MetricDataPoint], days: int) -> float:
        """Calculate moving average for N days"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        recent_points = [p for p in points if p.timestamp > cutoff]

        if not recent_points:
            return points[-1].value if points else 0.0

        return statistics.mean(p.value for p in recent_points)

    # =========================================================================
    # Intervention System
    # =========================================================================

    async def _check_trajectory(self, tenant_id: str, metric_type: MetricType) -> None:
        """Check trajectory and trigger intervention if needed"""
        analysis = self.analyze_trajectory(tenant_id, metric_type)

        if analysis.requires_intervention:
            await self._trigger_intervention(tenant_id, analysis)

    async def _trigger_intervention(self, tenant_id: str, analysis: TrajectoryAnalysis) -> None:
        """Trigger intervention for a problematic metric"""
        logger.warning(
            f"INTERVENTION TRIGGERED: {tenant_id} - {analysis.metric_type.value} "
            f"- {analysis.trajectory.value}: {analysis.intervention_reason}"
        )

        # Execute callbacks
        for callback in self._intervention_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(tenant_id, analysis)
                else:
                    callback(tenant_id, analysis)
            except Exception as e:
                logger.error(f"Intervention callback error: {e}")

        # Update tenant summary
        summary = self._tenant_summaries.get(tenant_id)
        if summary and analysis.metric_type.value not in summary.metrics_requiring_attention:
            summary.metrics_requiring_attention.append(analysis.metric_type.value)

    def register_intervention_callback(self, callback: Callable) -> None:
        """Register callback for intervention triggers"""
        self._intervention_callbacks.append(callback)

    def register_alert_callback(self, callback: Callable) -> None:
        """Register callback for alerts"""
        self._alert_callbacks.append(callback)

    # =========================================================================
    # Reporting
    # =========================================================================

    def get_tenant_metrics(self, tenant_id: str) -> TenantMetrics:
        """Get aggregated metrics for a tenant"""
        return self._tenant_summaries.get(tenant_id, TenantMetrics(tenant_id=tenant_id))

    def get_dashboard_data(self, tenant_id: str) -> dict[str, Any]:
        """
        Get data formatted for dashboard display.
        Always shows the positive trajectory story.
        """
        summary = self.get_tenant_metrics(tenant_id)
        trajectories = {}

        for metric_type in MetricType:
            analysis = self.analyze_trajectory(tenant_id, metric_type)
            trajectories[metric_type.value] = {
                "current": analysis.current_value,
                "change_percent": analysis.change_percent,
                "trajectory": analysis.trajectory.value,
                "ma_7d": analysis.moving_average_7d,
                "ma_30d": analysis.moving_average_30d,
                "status": "healthy" if not analysis.requires_intervention else "attention",
            }

        return {
            "tenant_id": tenant_id,
            "updated_at": datetime.utcnow().isoformat(),
            "summary": summary.model_dump(),
            "trajectories": trajectories,
            "overall_health": self._calculate_overall_health(tenant_id),
            "value_created_today": self._get_value_created_today(tenant_id),
        }

    def get_trajectory_chart_data(
        self, tenant_id: str, metric_type: MetricType, days: int = 30
    ) -> list[dict[str, Any]]:
        """Get data for trajectory chart"""
        points = self._get_points(tenant_id, metric_type)
        cutoff = datetime.utcnow() - timedelta(days=days)

        return [
            {
                "timestamp": p.timestamp.isoformat(),
                "value": p.value,
            }
            for p in points
            if p.timestamp > cutoff
        ]

    def _calculate_overall_health(self, tenant_id: str) -> str:
        """Calculate overall health score"""
        declining_count = 0
        flat_count = 0

        for metric_type in MetricType:
            analysis = self.analyze_trajectory(tenant_id, metric_type)
            if analysis.trajectory == TrajectoryStatus.DECLINING:
                declining_count += 1
            elif analysis.trajectory == TrajectoryStatus.FLAT:
                flat_count += 1

        if declining_count > 0:
            return "critical"
        elif flat_count > 2:
            return "warning"
        elif flat_count > 0:
            return "attention"
        else:
            return "healthy"

    def _get_value_created_today(self, tenant_id: str) -> float:
        """Get value created in the last 24 hours"""
        points = self._get_points(tenant_id, MetricType.VALUE_ADDED)
        cutoff = datetime.utcnow() - timedelta(hours=24)

        today_points = [p for p in points if p.timestamp > cutoff]
        if not today_points:
            return 0.0

        return sum(p.value for p in today_points)

    # =========================================================================
    # Internal Helpers
    # =========================================================================

    def _get_points(self, tenant_id: str, metric_type: MetricType) -> list[MetricDataPoint]:
        """Get data points for a metric"""
        if tenant_id not in self._metrics:
            return []
        if metric_type not in self._metrics[tenant_id]:
            return []
        return list(self._metrics[tenant_id][metric_type])

    def _update_tenant_summary(self, tenant_id: str) -> None:
        """Update tenant summary with latest data"""
        if tenant_id not in self._tenant_summaries:
            self._tenant_summaries[tenant_id] = TenantMetrics(tenant_id=tenant_id)

        summary = self._tenant_summaries[tenant_id]
        summary.updated_at = datetime.utcnow()

        # Update current values from latest points
        for metric_type in MetricType:
            points = self._get_points(tenant_id, metric_type)
            if points:
                latest = points[-1].value
                if metric_type == MetricType.VALUE_ADDED:
                    summary.total_value_added_usd = latest
                elif metric_type == MetricType.REVENUE:
                    summary.revenue_impact_usd = latest
                elif metric_type == MetricType.COST_SAVINGS:
                    summary.cost_savings_usd = latest
                elif metric_type == MetricType.EFFICIENCY:
                    summary.efficiency_score = latest
                elif metric_type == MetricType.COMPLIANCE_SCORE:
                    summary.compliance_score = latest

        # Calculate all-time value
        value_points = self._get_points(tenant_id, MetricType.VALUE_ADDED)
        summary.all_time_value_usd = sum(p.value for p in value_points)

        # Determine overall trajectory
        trajectories = [self.analyze_trajectory(tenant_id, mt).trajectory for mt in MetricType]

        if TrajectoryStatus.DECLINING in trajectories:
            summary.overall_trajectory = TrajectoryStatus.DECLINING
        elif TrajectoryStatus.FLAT in trajectories:
            summary.overall_trajectory = TrajectoryStatus.FLAT
        elif all(
            t in [TrajectoryStatus.STRONG_GROWTH, TrajectoryStatus.GROWTH] for t in trajectories
        ):
            summary.overall_trajectory = TrajectoryStatus.STRONG_GROWTH
        else:
            summary.overall_trajectory = TrajectoryStatus.GROWTH

    # =========================================================================
    # Lifecycle
    # =========================================================================

    async def start(self) -> None:
        """Start the metrics tracker"""
        self._running = True
        logger.info("Metrics Tracker started - Ever Upward Guardian activated")

    async def stop(self) -> None:
        """Stop the metrics tracker"""
        self._running = False
        logger.info("Metrics Tracker stopped")


# Global instance
metrics_tracker = MetricsTracker()
