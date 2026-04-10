"""
Unified Metrics Dashboard - Single pane of glass for all observability.

Combines:
- Ingestion pipeline metrics (sources, tiers, compliance)
- Performance metrics (latency, throughput, bottlenecks)
- ML anomaly detection (alerts, predictions)
- Monetization metrics (revenue, usage, conversions)
- Cost tracking (budget utilization, projections)

Features:
- Real-time unified view
- Historical trends
- Predictive alerts
- Revenue analytics
- SLA compliance tracking
"""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class DashboardSnapshot:
    """Complete system snapshot at a point in time."""

    timestamp: datetime = field(default_factory=datetime.now)

    # Ingestion metrics
    ingestion: dict = field(default_factory=dict)

    # Performance metrics
    performance: dict = field(default_factory=dict)

    # ML predictions and anomalies
    ml_insights: dict = field(default_factory=dict)

    # Monetization metrics
    revenue: dict = field(default_factory=dict)

    # Cost tracking
    cost: dict = field(default_factory=dict)

    # Overall health
    health_score: float = 0.0
    status: str = "unknown"  # healthy, degraded, critical


@dataclass
class Alert:
    """Unified alert from any subsystem."""

    timestamp: datetime
    source: str  # ingestion, performance, ml, cost, revenue
    severity: str  # info, warning, critical
    category: str
    message: str
    metric_name: str | None = None
    current_value: float | None = None
    threshold: float | None = None
    recommendation: str | None = None


class UnifiedMetricsDashboard:
    """
    Unified observability dashboard.

    Aggregates metrics from:
    - Ingestion pipeline (SourceManager, TierClassifier)
    - Performance monitoring (PerformanceMonitor)
    - ML anomaly detection (MLAnomalyDetectionSystem)
    - Monetization (UsageTracker, StripeIntegration)
    - Cost tracking (CostSpikeDetector)
    """

    def __init__(
        self,
        ingestion_manager=None,
        performance_monitor=None,
        ml_detector=None,
        usage_tracker=None,
        cost_detector=None,
    ):
        self.ingestion_manager = ingestion_manager
        self.performance_monitor = performance_monitor
        self.ml_detector = ml_detector
        self.usage_tracker = usage_tracker
        self.cost_detector = cost_detector

        # Alert history
        self.alerts: list[Alert] = []

        # Snapshot history
        self.snapshots: list[DashboardSnapshot] = []

    async def get_current_snapshot(self) -> DashboardSnapshot:
        """
        Get current unified snapshot of all systems.

        Returns:
            DashboardSnapshot with all current metrics
        """
        snapshot = DashboardSnapshot()

        # 1. Ingestion metrics
        if self.ingestion_manager:
            snapshot.ingestion = {
                "coverage": self.ingestion_manager.get_coverage_stats(),
                "tiers": self.ingestion_manager.tier_classifier.get_tier_distribution()
                if hasattr(self.ingestion_manager, "tier_classifier")
                else {},
                "status": "operational",
            }

        # 2. Performance metrics
        if self.performance_monitor:
            perf_report = self.performance_monitor.generate_performance_report()
            snapshot.performance = {
                "components": perf_report.get("components", {}),
                "bottlenecks": perf_report.get("bottlenecks", []),
                "system_resources": perf_report.get("system_resources", {}),
                "total_samples": perf_report.get("total_samples", 0),
            }

        # 3. ML insights
        if self.ml_detector:
            ml_data = self.ml_detector.get_dashboard_data()
            snapshot.ml_insights = {
                "anomaly_count_24h": ml_data.get("anomaly_count_24h", 0),
                "critical_anomalies": ml_data.get("critical_anomalies", 0),
                "cost_prediction": ml_data.get("cost_prediction", (0.0, 0.0)),
                "at_risk_sources": ml_data.get("at_risk_sources", 0),
            }

        # 4. Revenue metrics
        if self.usage_tracker:
            snapshot.revenue = {
                "mrr": await self._calculate_mrr(),
                "active_subscriptions": await self._count_active_subscriptions(),
                "usage_stats": self.usage_tracker.get_usage_stats(),
                "conversion_rate": await self._calculate_conversion_rate(),
            }

        # 5. Cost tracking
        if self.cost_detector:
            cost_stats = self.cost_detector.get_stats()
            snapshot.cost = {
                "current": cost_stats.get("current_cost", 0.0),
                "budget": cost_stats.get("budget", 77.0),
                "utilization": cost_stats.get("utilization_percent", 0.0),
                "projected": cost_stats.get("projected_monthly_cost", 0.0),
                "status": cost_stats.get("status", "unknown"),
                "throttle_active": cost_stats.get("throttle_active", False),
            }

        # Calculate overall health score
        snapshot.health_score = self._calculate_health_score(snapshot)
        snapshot.status = self._determine_status(snapshot.health_score)

        # Store snapshot
        self.snapshots.append(snapshot)
        if len(self.snapshots) > 1000:
            self.snapshots = self.snapshots[-1000:]

        return snapshot

    def _calculate_health_score(self, snapshot: DashboardSnapshot) -> float:
        """
        Calculate overall system health score (0-100).

        Weights:
        - Ingestion health: 30%
        - Performance health: 25%
        - ML anomalies: 20%
        - Cost health: 15%
        - Revenue health: 10%
        """
        score = 0.0

        # Ingestion health (30 points)
        if snapshot.ingestion:
            tiers = snapshot.ingestion.get("tiers", {})
            tier1_pct = tiers.get("tier_1", {}).get("percentage", 0.0)
            # Good: >20%, Fair: 10-20%, Poor: <10%
            if tier1_pct >= 20:
                score += 30
            elif tier1_pct >= 10:
                score += 20
            else:
                score += 10

        # Performance health (25 points)
        if snapshot.performance:
            bottlenecks = snapshot.performance.get("bottlenecks", [])
            critical_bottlenecks = [b for b in bottlenecks if b.get("severity") == "critical"]

            if len(critical_bottlenecks) == 0:
                score += 25
            elif len(critical_bottlenecks) <= 2:
                score += 15
            else:
                score += 5

        # ML anomalies (20 points)
        if snapshot.ml_insights:
            critical = snapshot.ml_insights.get("critical_anomalies", 0)
            if critical == 0:
                score += 20
            elif critical <= 3:
                score += 10
            else:
                score += 0

        # Cost health (15 points)
        if snapshot.cost:
            utilization = snapshot.cost.get("utilization", 0.0)
            if utilization < 75:
                score += 15
            elif utilization < 90:
                score += 10
            else:
                score += 0

        # Revenue health (10 points)
        if snapshot.revenue:
            mrr = snapshot.revenue.get("mrr", 0.0)
            # Healthy revenue growth
            if mrr >= 1000:
                score += 10
            elif mrr >= 500:
                score += 7
            elif mrr >= 100:
                score += 5
            else:
                score += 0

        return min(100.0, score)

    def _determine_status(self, health_score: float) -> str:
        """Determine overall status from health score."""
        if health_score >= 80:
            return "healthy"
        elif health_score >= 60:
            return "degraded"
        else:
            return "critical"

    async def _calculate_mrr(self) -> float:
        """Calculate Monthly Recurring Revenue."""
        if not self.usage_tracker:
            return 0.0

        # Sum all active subscriptions
        # In production, this would query Stripe API
        # For now, estimate based on usage
        return 0.0  # Placeholder

    async def _count_active_subscriptions(self) -> int:
        """Count active paying customers."""
        if not self.usage_tracker:
            return 0
        return 0  # Placeholder

    async def _calculate_conversion_rate(self) -> float:
        """Calculate trial-to-paid conversion rate."""
        # Placeholder for actual implementation
        return 0.0

    async def generate_alerts(self, snapshot: DashboardSnapshot) -> list[Alert]:
        """
        Generate alerts from current snapshot.

        Args:
            snapshot: Current system snapshot

        Returns:
            List of alerts requiring attention
        """
        alerts = []

        # Cost alerts
        if snapshot.cost:
            utilization = snapshot.cost.get("utilization", 0.0)
            if utilization >= 90:
                alerts.append(
                    Alert(
                        timestamp=datetime.now(),
                        source="cost",
                        severity="critical",
                        category="budget",
                        message=f"Budget utilization at {utilization:.1f}% - throttling active",
                        current_value=utilization,
                        threshold=90.0,
                        recommendation="Review cost drivers or increase budget",
                    )
                )
            elif utilization >= 75:
                alerts.append(
                    Alert(
                        timestamp=datetime.now(),
                        source="cost",
                        severity="warning",
                        category="budget",
                        message=f"Budget utilization at {utilization:.1f}%",
                        current_value=utilization,
                        threshold=75.0,
                        recommendation="Monitor closely, consider optimizations",
                    )
                )

        # Performance alerts
        if snapshot.performance:
            bottlenecks = snapshot.performance.get("bottlenecks", [])
            for bottleneck in bottlenecks:
                if bottleneck.get("severity") == "critical":
                    alerts.append(
                        Alert(
                            timestamp=datetime.now(),
                            source="performance",
                            severity="critical",
                            category="bottleneck",
                            message=f"Critical bottleneck in {bottleneck.get('component')}",
                            metric_name=bottleneck.get("component"),
                            current_value=bottleneck.get("avg_duration_ms"),
                            recommendation="Investigate and optimize component",
                        )
                    )

        # ML anomaly alerts
        if snapshot.ml_insights:
            critical_count = snapshot.ml_insights.get("critical_anomalies", 0)
            if critical_count > 0:
                alerts.append(
                    Alert(
                        timestamp=datetime.now(),
                        source="ml",
                        severity="warning",
                        category="anomaly",
                        message=f"{critical_count} critical anomalies detected",
                        current_value=float(critical_count),
                        recommendation="Review anomaly details and root cause",
                    )
                )

            at_risk = snapshot.ml_insights.get("at_risk_sources", 0)
            if at_risk > 0:
                alerts.append(
                    Alert(
                        timestamp=datetime.now(),
                        source="ml",
                        severity="warning",
                        category="source_health",
                        message=f"{at_risk} sources at risk of failure",
                        current_value=float(at_risk),
                        recommendation="Enable circuit breakers or review source health",
                    )
                )

        # Ingestion alerts
        if snapshot.ingestion:
            tiers = snapshot.ingestion.get("tiers", {})
            tier1_pct = tiers.get("tier_1", {}).get("percentage", 0.0)
            if tier1_pct < 10:
                alerts.append(
                    Alert(
                        timestamp=datetime.now(),
                        source="ingestion",
                        severity="warning",
                        category="quality",
                        message=f"Low quality: only {tier1_pct:.1f}% Tier 1 items",
                        current_value=tier1_pct,
                        threshold=10.0,
                        recommendation="Review collection criteria and source selection",
                    )
                )

        # Store alerts
        self.alerts.extend(alerts)
        if len(self.alerts) > 500:
            self.alerts = self.alerts[-500:]

        return alerts

    def get_dashboard_data(self) -> dict:
        """
        Get complete dashboard data for UI rendering.

        Returns:
            Dictionary with all dashboard sections
        """
        if not self.snapshots:
            return {"error": "No snapshots available"}

        latest = self.snapshots[-1]

        # Get recent alerts (last 24h)
        recent_alerts = [
            a for a in self.alerts if a.timestamp >= datetime.now() - timedelta(hours=24)
        ]

        return {
            "timestamp": latest.timestamp.isoformat(),
            "health_score": latest.health_score,
            "status": latest.status,
            "ingestion": latest.ingestion,
            "performance": latest.performance,
            "ml_insights": latest.ml_insights,
            "revenue": latest.revenue,
            "cost": latest.cost,
            "alerts": {
                "critical": len([a for a in recent_alerts if a.severity == "critical"]),
                "warning": len([a for a in recent_alerts if a.severity == "warning"]),
                "total": len(recent_alerts),
                "recent": [
                    {
                        "timestamp": a.timestamp.isoformat(),
                        "source": a.source,
                        "severity": a.severity,
                        "category": a.category,
                        "message": a.message,
                        "recommendation": a.recommendation,
                    }
                    for a in recent_alerts[-10:]  # Last 10 alerts
                ],
            },
            "trends": self._calculate_trends(),
        }

    def _calculate_trends(self) -> dict:
        """Calculate trends from historical snapshots."""
        if len(self.snapshots) < 2:
            return {}

        # Compare last 2 snapshots
        current = self.snapshots[-1]
        previous = self.snapshots[-2] if len(self.snapshots) > 1 else current

        trends = {}

        # Health score trend
        trends["health_score_change"] = current.health_score - previous.health_score

        # Cost trend
        if current.cost and previous.cost:
            current_util = current.cost.get("utilization", 0.0)
            prev_util = previous.cost.get("utilization", 0.0)
            trends["cost_utilization_change"] = current_util - prev_util

        # Quality trend
        if current.ingestion and previous.ingestion:
            current_tier1 = (
                current.ingestion.get("tiers", {}).get("tier_1", {}).get("percentage", 0.0)
            )
            prev_tier1 = (
                previous.ingestion.get("tiers", {}).get("tier_1", {}).get("percentage", 0.0)
            )
            trends["tier1_percentage_change"] = current_tier1 - prev_tier1

        return trends

    def get_sla_compliance(self) -> dict:
        """
        Calculate SLA compliance metrics.

        SLAs:
        - Uptime: 99.9%
        - Ingestion latency: <45 min for nightly run
        - API response time: p95 <500ms
        - Data quality: >15% Tier 1
        """
        if not self.snapshots:
            return {}

        latest = self.snapshots[-1]

        return {
            "data_quality": {
                "target": 15.0,
                "current": latest.ingestion.get("tiers", {})
                .get("tier_1", {})
                .get("percentage", 0.0),
                "compliant": latest.ingestion.get("tiers", {})
                .get("tier_1", {})
                .get("percentage", 0.0)
                >= 15.0,
            },
            "cost_control": {
                "target": 77.0,
                "current": latest.cost.get("current", 0.0),
                "projected": latest.cost.get("projected", 0.0),
                "compliant": latest.cost.get("projected", 0.0) <= 77.0,
            },
            "performance": {
                "critical_bottlenecks": len(
                    [
                        b
                        for b in latest.performance.get("bottlenecks", [])
                        if b.get("severity") == "critical"
                    ]
                ),
                "compliant": len(
                    [
                        b
                        for b in latest.performance.get("bottlenecks", [])
                        if b.get("severity") == "critical"
                    ]
                )
                == 0,
            },
        }


# Global dashboard instance
unified_dashboard = None


def get_dashboard() -> UnifiedMetricsDashboard:
    """Get or create global dashboard instance."""
    global unified_dashboard
    if unified_dashboard is None:
        unified_dashboard = UnifiedMetricsDashboard()
    return unified_dashboard


def initialize_dashboard(
    ingestion_manager=None,
    performance_monitor=None,
    ml_detector=None,
    usage_tracker=None,
    cost_detector=None,
):
    """
    Initialize global dashboard with component references.

    Args:
        ingestion_manager: SourceManager instance
        performance_monitor: PerformanceMonitor instance
        ml_detector: MLAnomalyDetectionSystem instance
        usage_tracker: UsageTracker instance
        cost_detector: CostSpikeDetector instance
    """
    global unified_dashboard
    unified_dashboard = UnifiedMetricsDashboard(
        ingestion_manager=ingestion_manager,
        performance_monitor=performance_monitor,
        ml_detector=ml_detector,
        usage_tracker=usage_tracker,
        cost_detector=cost_detector,
    )
    logger.info("Unified metrics dashboard initialized")
    return unified_dashboard
