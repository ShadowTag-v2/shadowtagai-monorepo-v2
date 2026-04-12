"""
Metrics Collector for Prometheus

Tracks key metrics:
- Items/Day
- Sources count
- Cost/Item
- Runtime efficiency
"""

from datetime import datetime
from typing import Any


class MetricsCollector:
    """
    Collect and expose metrics for Prometheus.

    Key Metrics:
    - gemini_ingestion_items_total: Total items ingested
    - gemini_ingestion_sources_count: Unique sources used
    - gemini_ingestion_cost_per_item: Cost per item in USD
    - gemini_ingestion_runtime_seconds: Runtime in seconds
    - gemini_ingestion_tier_distribution: Items by tier (1/2/3)
    """

    def __init__(self):
        self.metrics: dict[str, Any] = {}
        self.reset()

    def reset(self):
        """Reset metrics for new run"""
        self.metrics = {
            "items_total": 0,
            "sources_count": 0,
            "cost_per_item": 0.0,
            "runtime_seconds": 0.0,
            "tier_1_count": 0,
            "tier_2_count": 0,
            "tier_3_count": 0,
            "timestamp": datetime.utcnow(),
        }

    def record_run(self, stats: dict[str, Any]):
        """Record metrics from an ingestion run"""
        self.metrics.update(
            {
                "items_total": stats.get("items_ingested", 0),
                "sources_count": stats.get("unique_sources", 0),
                "cost_per_item": stats.get("cost_per_item", 0.0),
                "runtime_seconds": stats.get("runtime_minutes", 0) * 60,
                "tier_1_count": stats.get("tier_1_count", 0),
                "tier_2_count": stats.get("tier_2_count", 0),
                "tier_3_count": stats.get("tier_3_count", 0),
                "timestamp": datetime.utcnow(),
            }
        )

    def get_prometheus_format(self) -> str:
        """
        Export metrics in Prometheus text format.

        Returns:
            Prometheus-formatted metrics
        """
        lines = []
        lines.append("# HELP gemini_ingestion_items_total Total items ingested")
        lines.append("# TYPE gemini_ingestion_items_total counter")
        lines.append(f"gemini_ingestion_items_total {self.metrics['items_total']}")

        lines.append("# HELP gemini_ingestion_sources_count Unique sources count")
        lines.append("# TYPE gemini_ingestion_sources_count gauge")
        lines.append(f"gemini_ingestion_sources_count {self.metrics['sources_count']}")

        lines.append("# HELP gemini_ingestion_cost_per_item Cost per item in USD")
        lines.append("# TYPE gemini_ingestion_cost_per_item gauge")
        lines.append(f"gemini_ingestion_cost_per_item {self.metrics['cost_per_item']}")

        lines.append("# HELP gemini_ingestion_runtime_seconds Runtime in seconds")
        lines.append("# TYPE gemini_ingestion_runtime_seconds gauge")
        lines.append(f"gemini_ingestion_runtime_seconds {self.metrics['runtime_seconds']}")

        lines.append("# HELP gemini_ingestion_tier_count Items by tier")
        lines.append("# TYPE gemini_ingestion_tier_count gauge")
        lines.append(f'gemini_ingestion_tier_count{{tier="1"}} {self.metrics["tier_1_count"]}')
        lines.append(f'gemini_ingestion_tier_count{{tier="2"}} {self.metrics["tier_2_count"]}')
        lines.append(f'gemini_ingestion_tier_count{{tier="3"}} {self.metrics["tier_3_count"]}')

        return "\n".join(lines) + "\n"

    def get_stats(self) -> dict[str, Any]:
        """Get current metrics as dict"""
        return self.metrics.copy()
