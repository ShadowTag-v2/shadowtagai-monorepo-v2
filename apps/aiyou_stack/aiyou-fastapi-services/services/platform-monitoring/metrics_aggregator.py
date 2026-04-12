"""
Platform Monitoring - Unified Metrics Aggregator

Aggregates metrics from:
- V2X Mesh Network (real-time vehicle communication)
- Gemini Ingestion Layer (nightly intelligence collection)

Provides unified observability for PNKLN Core Stack™
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import aiohttp


class ServiceType(Enum):
    """Service types in platform"""

    V2X_MESH = "v2x_mesh"
    INGESTION = "ingestion"
    MONITORING = "monitoring"


class HealthStatus(Enum):
    """Health status levels"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceMetrics:
    """Metrics for a single service"""

    service_name: str
    service_type: ServiceType
    timestamp: datetime

    # Performance
    requests_per_second: float = 0.0
    avg_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    error_rate: float = 0.0

    # Resources
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    active_connections: int = 0

    # Business
    items_processed: int = 0
    cost_dollars: float = 0.0

    # Health
    health_status: HealthStatus = HealthStatus.UNKNOWN
    uptime_seconds: float = 0.0


@dataclass
class PlatformMetrics:
    """Aggregated platform-wide metrics"""

    timestamp: datetime

    # Services
    total_services: int = 0
    healthy_services: int = 0
    degraded_services: int = 0
    unhealthy_services: int = 0

    # Performance (aggregated)
    platform_requests_per_second: float = 0.0
    platform_avg_latency_ms: float = 0.0
    platform_error_rate: float = 0.0

    # Resources (aggregated)
    platform_cpu_usage_percent: float = 0.0
    platform_memory_usage_mb: float = 0.0

    # Business (aggregated)
    daily_items_processed: int = 0
    daily_cost_dollars: float = 0.0
    monthly_cost_projection: float = 0.0

    # Service-specific
    v2x_metrics: ServiceMetrics | None = None
    ingestion_metrics: ServiceMetrics | None = None

    # Alerts
    active_alerts: list[str] = field(default_factory=list)


class MetricsAggregator:
    """
    Aggregates metrics from all platform services

    Provides unified observability and cost tracking
    """

    def __init__(
        self,
        v2x_endpoint: str = "http://v2x-mesh-gateway:8012",
        ingestion_endpoint: str = "http://gemini-ingestion-monitor:8080",
    ):
        self.v2x_endpoint = v2x_endpoint
        self.ingestion_endpoint = ingestion_endpoint

        self.service_metrics: dict[str, ServiceMetrics] = {}
        self.platform_metrics_history: list[PlatformMetrics] = []

        # Thresholds
        self.latency_threshold_ms = 100.0
        self.error_rate_threshold = 0.05
        self.cpu_threshold_percent = 80.0
        self.cost_daily_threshold = 5.0  # $5/day = $150/month

    async def collect_all_metrics(self) -> PlatformMetrics:
        """Collect metrics from all services"""
        # Collect in parallel
        tasks = [self._collect_v2x_metrics(), self._collect_ingestion_metrics()]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        v2x_metrics = results[0] if not isinstance(results[0], Exception) else None
        ingestion_metrics = results[1] if not isinstance(results[1], Exception) else None

        # Aggregate
        platform_metrics = self._aggregate_metrics(v2x_metrics, ingestion_metrics)

        # Store history
        self.platform_metrics_history.append(platform_metrics)
        if len(self.platform_metrics_history) > 1000:
            self.platform_metrics_history = self.platform_metrics_history[-500:]

        return platform_metrics

    async def _collect_v2x_metrics(self) -> ServiceMetrics:
        """Collect V2X mesh metrics"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.v2x_endpoint}/metrics", timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return self._parse_v2x_metrics(data)
        except Exception as e:
            print(f"Error collecting V2X metrics: {e}")
            return ServiceMetrics(
                service_name="v2x-mesh",
                service_type=ServiceType.V2X_MESH,
                timestamp=datetime.now(),
                health_status=HealthStatus.UNKNOWN,
            )

    async def _collect_ingestion_metrics(self) -> ServiceMetrics:
        """Collect Ingestion layer metrics"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.ingestion_endpoint}/metrics", timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return self._parse_ingestion_metrics(data)
        except Exception as e:
            print(f"Error collecting Ingestion metrics: {e}")
            return ServiceMetrics(
                service_name="gemini-ingestion",
                service_type=ServiceType.INGESTION,
                timestamp=datetime.now(),
                health_status=HealthStatus.UNKNOWN,
            )

    def _parse_v2x_metrics(self, data: dict) -> ServiceMetrics:
        """Parse V2X mesh metrics"""
        return ServiceMetrics(
            service_name="v2x-mesh",
            service_type=ServiceType.V2X_MESH,
            timestamp=datetime.now(),
            requests_per_second=data.get("messages_per_second", 0),
            avg_latency_ms=data.get("avg_latency_ms", 0),
            p99_latency_ms=data.get("p99_latency_ms", 0),
            error_rate=data.get("error_rate", 0),
            cpu_usage_percent=data.get("cpu_percent", 0),
            memory_usage_mb=data.get("memory_mb", 0),
            active_connections=data.get("active_peers", 0),
            items_processed=data.get("total_messages_processed", 0),
            cost_dollars=data.get("daily_cost", 0),
            health_status=self._determine_health(data),
            uptime_seconds=data.get("uptime_seconds", 0),
        )

    def _parse_ingestion_metrics(self, data: dict) -> ServiceMetrics:
        """Parse Ingestion layer metrics"""
        return ServiceMetrics(
            service_name="gemini-ingestion",
            service_type=ServiceType.INGESTION,
            timestamp=datetime.now(),
            requests_per_second=0,  # Batch job, not applicable
            avg_latency_ms=data.get("runtime_minutes", 0) * 60 * 1000,  # Convert to ms
            p99_latency_ms=0,
            error_rate=data.get("failed_jobs", 0) / max(1, data.get("total_jobs", 1)),
            cpu_usage_percent=data.get("cpu_percent", 0),
            memory_usage_mb=data.get("memory_mb", 0),
            active_connections=0,
            items_processed=data.get("total_items", 0),
            cost_dollars=data.get("monthly_cost", 0) / 30,  # Daily cost
            health_status=self._determine_health(data),
            uptime_seconds=data.get("last_run_age_seconds", 0),
        )

    def _determine_health(self, data: dict) -> HealthStatus:
        """Determine health status from metrics"""
        error_rate = data.get("error_rate", 0)
        latency = data.get("avg_latency_ms", 0)
        cpu = data.get("cpu_percent", 0)

        if error_rate > 0.10 or latency > 500 or cpu > 90:
            return HealthStatus.UNHEALTHY
        elif error_rate > 0.05 or latency > 200 or cpu > 80:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY

    def _aggregate_metrics(
        self, v2x: ServiceMetrics | None, ingestion: ServiceMetrics | None
    ) -> PlatformMetrics:
        """Aggregate service metrics into platform metrics"""
        platform = PlatformMetrics(timestamp=datetime.now())

        services = [s for s in [v2x, ingestion] if s is not None]
        platform.total_services = len(services)

        for service in services:
            if service.health_status == HealthStatus.HEALTHY:
                platform.healthy_services += 1
            elif service.health_status == HealthStatus.DEGRADED:
                platform.degraded_services += 1
            elif service.health_status == HealthStatus.UNHEALTHY:
                platform.unhealthy_services += 1

        # Aggregate performance
        if v2x:
            platform.platform_requests_per_second += v2x.requests_per_second
            platform.platform_avg_latency_ms = v2x.avg_latency_ms  # V2X dominates
            platform.platform_error_rate = max(platform.platform_error_rate, v2x.error_rate)

        # Aggregate resources
        platform.platform_cpu_usage_percent = sum(s.cpu_usage_percent for s in services) / max(
            1, len(services)
        )
        platform.platform_memory_usage_mb = sum(s.memory_usage_mb for s in services)

        # Aggregate business
        platform.daily_items_processed = sum(s.items_processed for s in services)
        platform.daily_cost_dollars = sum(s.cost_dollars for s in services)
        platform.monthly_cost_projection = platform.daily_cost_dollars * 30

        # Store service-specific
        platform.v2x_metrics = v2x
        platform.ingestion_metrics = ingestion

        # Generate alerts
        platform.active_alerts = self._generate_alerts(platform)

        return platform

    def _generate_alerts(self, metrics: PlatformMetrics) -> list[str]:
        """Generate alerts based on thresholds"""
        alerts = []

        if metrics.platform_error_rate > self.error_rate_threshold:
            alerts.append(
                f"HIGH_ERROR_RATE: {metrics.platform_error_rate * 100:.1f}% (threshold: {self.error_rate_threshold * 100}%)"
            )

        if metrics.platform_avg_latency_ms > self.latency_threshold_ms:
            alerts.append(
                f"HIGH_LATENCY: {metrics.platform_avg_latency_ms:.0f}ms (threshold: {self.latency_threshold_ms}ms)"
            )

        if metrics.platform_cpu_usage_percent > self.cpu_threshold_percent:
            alerts.append(
                f"HIGH_CPU: {metrics.platform_cpu_usage_percent:.0f}% (threshold: {self.cpu_threshold_percent}%)"
            )

        if metrics.daily_cost_dollars > self.cost_daily_threshold:
            alerts.append(
                f"HIGH_COST: ${metrics.daily_cost_dollars:.2f}/day (threshold: ${self.cost_daily_threshold})"
            )

        if metrics.unhealthy_services > 0:
            alerts.append(f"UNHEALTHY_SERVICES: {metrics.unhealthy_services} service(s) unhealthy")

        return alerts

    def get_cost_breakdown(self) -> dict[str, float]:
        """Get detailed cost breakdown"""
        if not self.platform_metrics_history:
            return {}

        latest = self.platform_metrics_history[-1]

        breakdown = {
            "v2x_mesh_daily": latest.v2x_metrics.cost_dollars if latest.v2x_metrics else 0,
            "ingestion_daily": latest.ingestion_metrics.cost_dollars
            if latest.ingestion_metrics
            else 0,
            "total_daily": latest.daily_cost_dollars,
            "total_monthly_projection": latest.monthly_cost_projection,
            "v2x_mesh_monthly": (latest.v2x_metrics.cost_dollars * 30) if latest.v2x_metrics else 0,
            "ingestion_monthly": (latest.ingestion_metrics.cost_dollars * 30)
            if latest.ingestion_metrics
            else 0,
        }

        return breakdown

    def get_performance_summary(self) -> dict[str, Any]:
        """Get performance summary"""
        if not self.platform_metrics_history:
            return {}

        latest = self.platform_metrics_history[-1]

        return {
            "timestamp": latest.timestamp.isoformat(),
            "services": {
                "total": latest.total_services,
                "healthy": latest.healthy_services,
                "degraded": latest.degraded_services,
                "unhealthy": latest.unhealthy_services,
            },
            "performance": {
                "requests_per_second": latest.platform_requests_per_second,
                "avg_latency_ms": latest.platform_avg_latency_ms,
                "error_rate": latest.platform_error_rate,
            },
            "resources": {
                "cpu_percent": latest.platform_cpu_usage_percent,
                "memory_mb": latest.platform_memory_usage_mb,
            },
            "business": {
                "daily_items": latest.daily_items_processed,
                "daily_cost": latest.daily_cost_dollars,
                "monthly_projection": latest.monthly_cost_projection,
            },
            "alerts": latest.active_alerts,
        }


# Example usage
if __name__ == "__main__":

    async def main():
        aggregator = MetricsAggregator()

        # Collect metrics
        metrics = await aggregator.collect_all_metrics()

        print("Platform Metrics:")
        print(f"  Services: {metrics.total_services} total, {metrics.healthy_services} healthy")
        print(
            f"  Performance: {metrics.platform_requests_per_second:.1f} req/s, {metrics.platform_avg_latency_ms:.0f}ms avg"
        )
        print(
            f"  Cost: ${metrics.daily_cost_dollars:.2f}/day (${metrics.monthly_cost_projection:.0f}/month projected)"
        )
        print(f"  Alerts: {len(metrics.active_alerts)}")
        for alert in metrics.active_alerts:
            print(f"    - {alert}")

    asyncio.run(main())
