# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Cost tracking and budget monitoring."""

import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime

logger = logging.getLogger(__name__)


@dataclass
class APICallCost:
    """Track cost of individual API calls."""

    timestamp: datetime
    source: str  # e.g., "youtube", "twitter", "newsapi"
    endpoint: str  # e.g., "/search/list", "/tweets/search"
    method: str  # e.g., "GET", "POST"
    cost: float  # USD
    items_returned: int  # Number of items from this call
    quota_used: int | None = None  # For quota-based APIs (YouTube)

    def to_dict(self) -> dict:
        """Convert to dict for logging."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "endpoint": self.endpoint,
            "method": self.method,
            "cost_usd": round(self.cost, 6),
            "items_returned": self.items_returned,
            "cost_per_item": (round(self.cost / self.items_returned, 6) if self.items_returned > 0 else 0),
            "quota_used": self.quota_used,
        }


class CostTracker:
    """
    Track and monitor API costs.

    Budget:
    - Monthly: $77
    - Daily: $2.57
    - Target cost/item: $0.0026

    """

    MONTHLY_BUDGET = 77.0
    DAILY_BUDGET = 2.57
    TARGET_COST_PER_ITEM = 0.0026

    def __init__(self):
        """Initialize cost tracker."""
        self.costs: list[APICallCost] = []

    def add_cost(self, cost: APICallCost):
        """
        Add an API call cost.

        Args:
            cost: API call cost to track

        """
        self.costs.append(cost)
        logger.info("api_call_cost", extra=cost.to_dict())

    def get_daily_summary(self, target_date: date) -> dict:
        """
        Get cost summary for a specific day.

        Args:
            target_date: Date to summarize

        Returns:
            Daily cost summary

        """
        daily_costs = [c for c in self.costs if c.timestamp.date() == target_date]

        by_source: dict = defaultdict(lambda: {"cost": 0.0, "items": 0, "calls": 0})

        for cost in daily_costs:
            by_source[cost.source]["cost"] += cost.cost
            by_source[cost.source]["items"] += cost.items_returned
            by_source[cost.source]["calls"] += 1

        total_cost = sum(s["cost"] for s in by_source.values())
        total_items = sum(s["items"] for s in by_source.values())

        return {
            "date": target_date.isoformat(),
            "total_cost": round(total_cost, 4),
            "total_items": total_items,
            "cost_per_item": (round(total_cost / total_items, 6) if total_items > 0 else 0),
            "by_source": dict(by_source),
            "daily_budget": self.DAILY_BUDGET,
            "budget_utilization_pct": round(total_cost / self.DAILY_BUDGET * 100, 1),
            "under_budget": total_cost <= self.DAILY_BUDGET,
            "under_target_cost_per_item": ((total_cost / total_items <= self.TARGET_COST_PER_ITEM) if total_items > 0 else True),
        }

    def get_monthly_projection(self, days_elapsed: int) -> dict:
        """
        Project monthly cost based on current usage.

        Args:
            days_elapsed: Number of days elapsed this month

        Returns:
            Monthly projection

        """
        if days_elapsed == 0:
            return {"error": "No data yet this month"}

        month_costs = [c for c in self.costs if c.timestamp.month == datetime.now().month]

        total_cost_so_far = sum(c.cost for c in month_costs)
        avg_daily_cost = total_cost_so_far / days_elapsed
        projected_monthly_cost = avg_daily_cost * 30

        return {
            "days_elapsed": days_elapsed,
            "cost_so_far": round(total_cost_so_far, 2),
            "avg_daily_cost": round(avg_daily_cost, 2),
            "projected_monthly_cost": round(projected_monthly_cost, 2),
            "monthly_budget": self.MONTHLY_BUDGET,
            "projected_variance": round(projected_monthly_cost - self.MONTHLY_BUDGET, 2),
            "on_track": projected_monthly_cost <= self.MONTHLY_BUDGET,
        }

    def check_budget_status(self) -> dict:
        """
        Check current budget status.

        Returns:
            Budget status with alerts

        """
        today = date.today()
        daily_summary = self.get_daily_summary(today)
        monthly_projection = self.get_monthly_projection(today.day)

        alerts = []

        # Daily budget check
        if daily_summary["total_cost"] > 3.00:
            alerts.append({"level": "critical", "message": "Daily cost exceeded $3.00"})
        elif daily_summary["total_cost"] > self.DAILY_BUDGET:
            alerts.append(
                {
                    "level": "warning",
                    "message": f"Daily cost ${daily_summary['total_cost']:.2f} exceeds budget ${self.DAILY_BUDGET}",
                }
            )

        # Cost per item check
        if daily_summary["total_items"] > 0:
            cost_per_item = daily_summary["cost_per_item"]
            if cost_per_item > 0.004:
                alerts.append(
                    {
                        "level": "warning",
                        "message": f"Cost per item ${cost_per_item:.4f} exceeds warning threshold $0.004",
                    }
                )

        # Monthly projection check
        if not isinstance(monthly_projection, dict) or "error" not in monthly_projection:
            if monthly_projection["projected_monthly_cost"] > 90:
                alerts.append(
                    {
                        "level": "critical",
                        "message": f"Projected monthly cost ${monthly_projection['projected_monthly_cost']:.2f} exceeds $90",
                    }
                )
            elif monthly_projection["projected_monthly_cost"] > self.MONTHLY_BUDGET:
                alerts.append(
                    {
                        "level": "warning",
                        "message": f"Projected monthly cost ${monthly_projection['projected_monthly_cost']:.2f} exceeds budget",
                    }
                )

        return {
            "timestamp": datetime.now().isoformat(),
            "daily_summary": daily_summary,
            "monthly_projection": monthly_projection,
            "alerts": alerts,
            "overall_status": "critical" if any(a["level"] == "critical" for a in alerts) else ("warning" if alerts else "ok"),
        }
