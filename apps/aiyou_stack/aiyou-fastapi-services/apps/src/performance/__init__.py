"""Performance monitoring integration for unified observability.

Integrates with Performance Engineer to provide:
- Real-time metrics collection
- Performance profiling
- Bottleneck detection
- Resource utilization tracking
"""

import asyncio
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from typing import Dict, List, Optional

import psutil

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for a component."""

    component_name: str
    timestamp: datetime = field(default_factory=datetime.now)

    # Timing
    duration_ms: float = 0.0
    cpu_time_ms: float = 0.0

    # Resource usage
    memory_used_mb: float = 0.0
    cpu_percent: float = 0.0

    # Throughput
    requests_per_second: float = 0.0
    items_per_second: float = 0.0

    # Errors
    error_count: int = 0
    error_rate: float = 0.0


class PerformanceMonitor:
    """Unified performance monitoring.

    Tracks:
    - Component-level performance
    - Resource utilization
    - Bottleneck identification
    - Historical trends
    """

    def __init__(self):
        self.metrics_history: list[PerformanceMetrics] = []
        self.active_traces: dict[str, float] = {}

        # System metrics
        self.process = psutil.Process()

    def start_trace(self, trace_id: str):
        """Start performance trace."""
        self.active_traces[trace_id] = time.time()

    def end_trace(self, trace_id: str, component_name: str) -> PerformanceMetrics:
        """End performance trace and record metrics."""
        start_time = self.active_traces.pop(trace_id, time.time())
        duration_ms = (time.time() - start_time) * 1000

        metrics = PerformanceMetrics(
            component_name=component_name,
            duration_ms=duration_ms,
            memory_used_mb=self.process.memory_info().rss / 1024 / 1024,
            cpu_percent=self.process.cpu_percent(),
        )

        self.metrics_history.append(metrics)

        # Keep last 1000 metrics
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]

        return metrics

    def decorator(self, component_name: str):
        """Decorator for automatic performance tracking."""

        def wrapper(func: Callable):
            if asyncio.iscoroutinefunction(func):

                @wraps(func)
                async def async_wrapped(*args, **kwargs):
                    trace_id = f"{component_name}_{time.time()}"
                    self.start_trace(trace_id)

                    try:
                        result = await func(*args, **kwargs)
                        return result
                    finally:
                        metrics = self.end_trace(trace_id, component_name)
                        logger.debug(f"{component_name} completed in {metrics.duration_ms:.2f}ms")

                return async_wrapped

            @wraps(func)
            def sync_wrapped(*args, **kwargs):
                trace_id = f"{component_name}_{time.time()}"
                self.start_trace(trace_id)

                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    metrics = self.end_trace(trace_id, component_name)
                    logger.debug(f"{component_name} completed in {metrics.duration_ms:.2f}ms")

            return sync_wrapped

        return wrapper

    def get_component_stats(self, component_name: str) -> dict:
        """Get statistics for a component."""
        component_metrics = [m for m in self.metrics_history if m.component_name == component_name]

        if not component_metrics:
            return {
                "component": component_name,
                "sample_count": 0,
                "error": "No metrics available",
            }

        durations = [m.duration_ms for m in component_metrics]
        memory_usage = [m.memory_used_mb for m in component_metrics]

        return {
            "component": component_name,
            "sample_count": len(component_metrics),
            "duration": {
                "avg_ms": sum(durations) / len(durations),
                "min_ms": min(durations),
                "max_ms": max(durations),
                "p95_ms": sorted(durations)[int(len(durations) * 0.95)]
                if len(durations) > 20
                else max(durations),
            },
            "memory": {
                "avg_mb": sum(memory_usage) / len(memory_usage),
                "max_mb": max(memory_usage),
            },
            "error_rate": sum(m.error_count for m in component_metrics) / len(component_metrics),
        }

    def get_bottlenecks(self, threshold_ms: float = 1000.0) -> list[dict]:
        """Identify performance bottlenecks."""
        component_stats = {}

        for metrics in self.metrics_history:
            if metrics.component_name not in component_stats:
                component_stats[metrics.component_name] = []
            component_stats[metrics.component_name].append(metrics.duration_ms)

        bottlenecks = []

        for component, durations in component_stats.items():
            avg_duration = sum(durations) / len(durations)

            if avg_duration > threshold_ms:
                bottlenecks.append(
                    {
                        "component": component,
                        "avg_duration_ms": avg_duration,
                        "max_duration_ms": max(durations),
                        "sample_count": len(durations),
                        "severity": "critical" if avg_duration > threshold_ms * 2 else "warning",
                    },
                )

        return sorted(bottlenecks, key=lambda x: -x["avg_duration_ms"])

    def get_system_resources(self) -> dict:
        """Get current system resource usage."""
        return {
            "cpu": {
                "percent": psutil.cpu_percent(interval=0.1),
                "count": psutil.cpu_count(),
            },
            "memory": {
                "total_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024,
                "available_gb": psutil.virtual_memory().available / 1024 / 1024 / 1024,
                "percent": psutil.virtual_memory().percent,
            },
            "disk": {
                "total_gb": psutil.disk_usage("/").total / 1024 / 1024 / 1024,
                "free_gb": psutil.disk_usage("/").free / 1024 / 1024 / 1024,
                "percent": psutil.disk_usage("/").percent,
            },
        }

    def generate_performance_report(self) -> dict:
        """Generate comprehensive performance report."""
        unique_components = set(m.component_name for m in self.metrics_history)

        component_reports = {}
        for component in unique_components:
            component_reports[component] = self.get_component_stats(component)

        return {
            "timestamp": datetime.now().isoformat(),
            "total_samples": len(self.metrics_history),
            "components": component_reports,
            "bottlenecks": self.get_bottlenecks(),
            "system_resources": self.get_system_resources(),
        }


# Global monitor instance
performance_monitor = PerformanceMonitor()
