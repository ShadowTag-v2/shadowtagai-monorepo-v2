"""PNKLN Core Stack - Cost Tracking and Budget Monitoring

Tracks costs across all pipeline operations and alerts when approaching budget limits.

Monitors:
- Source API costs (YouTube, Twitter, News)
- Gemini classification costs
- Total daily/monthly spend
- Budget utilization
"""

from dataclasses import dataclass
from datetime import datetime

import structlog
from prometheus_client import Counter, Gauge

from ingestion.core.config import get_config

logger = structlog.get_logger(__name__)


# Prometheus metrics for cost tracking
cost_total_usd = Gauge("ingestion_cost_total_usd", "Total cumulative cost in USD")
cost_by_source = Gauge("ingestion_cost_by_source_usd", "Cost by source in USD", ["source"])
cost_budget_utilization_pct = Gauge(
    "ingestion_cost_budget_utilization_pct", "Percentage of monthly budget used",
)
cost_overage_events = Counter("ingestion_cost_overage_total", "Number of times budget was exceeded")


@dataclass
class CostBreakdown:
    """Detailed cost breakdown for a pipeline run."""

    timestamp: datetime
    youtube_cost: float = 0.0
    twitter_cost: float = 0.0
    news_cost: float = 0.0
    classification_cost: float = 0.0
    total_cost: float = 0.0
    items_processed: int = 0
    cost_per_item: float = 0.0


@dataclass
class BudgetStatus:
    """Current budget utilization status."""

    monthly_budget: float
    current_spend: float
    remaining: float
    utilization_pct: float
    days_remaining_in_month: int
    projected_monthly_spend: float
    projected_overage: float
    is_over_budget: bool
    alert_threshold_reached: bool  # True if >80% budget used


class CostTracker:
    """Tracks and monitors pipeline costs against budget.

    Features:
    - Real-time cost tracking per source
    - Budget utilization monitoring
    - Overage alerts
    - Projection of monthly spend
    - Historical cost data (if persistent storage enabled)
    """

    def __init__(self):
        self.config = get_config()
        self.monthly_budget = self.config.ingestion.cost_budget_usd

        # In-memory tracking (reset monthly)
        self._current_month_costs: list[CostBreakdown] = []
        self._current_month_start = self._get_month_start()

        # Alert thresholds
        self.alert_thresholds = [0.5, 0.75, 0.90, 1.0]  # 50%, 75%, 90%, 100%
        self._alerts_fired = set()

        logger.info("cost_tracker_initialized", monthly_budget=self.monthly_budget)

    def _get_month_start(self) -> datetime:
        """Get the start of the current month."""
        now = datetime.utcnow()
        return datetime(now.year, now.month, 1)

    def _check_month_rollover(self) -> None:
        """Check if we've entered a new month and reset tracking."""
        current_month_start = self._get_month_start()

        if current_month_start > self._current_month_start:
            logger.info(
                "month_rollover_detected",
                old_month=self._current_month_start.strftime("%Y-%m"),
                new_month=current_month_start.strftime("%Y-%m"),
                previous_month_spend=self.get_current_month_total(),
            )

            # Archive previous month's data (if storage available)
            # TODO: Save to database/BigQuery

            # Reset for new month
            self._current_month_costs = []
            self._current_month_start = current_month_start
            self._alerts_fired = set()

    def record_pipeline_run(
        self,
        youtube_cost: float = 0.0,
        twitter_cost: float = 0.0,
        news_cost: float = 0.0,
        classification_cost: float = 0.0,
        items_processed: int = 0,
    ) -> CostBreakdown:
        """Record costs from a pipeline run.

        Args:
            youtube_cost: Cost of YouTube API calls
            twitter_cost: Cost of Twitter API calls
            news_cost: Cost of news/RSS fetching
            classification_cost: Cost of Gemini classification
            items_processed: Number of items processed

        Returns:
            CostBreakdown with totals

        """
        self._check_month_rollover()

        total = youtube_cost + twitter_cost + news_cost + classification_cost
        cost_per_item = total / items_processed if items_processed > 0 else 0.0

        breakdown = CostBreakdown(
            timestamp=datetime.utcnow(),
            youtube_cost=youtube_cost,
            twitter_cost=twitter_cost,
            news_cost=news_cost,
            classification_cost=classification_cost,
            total_cost=total,
            items_processed=items_processed,
            cost_per_item=cost_per_item,
        )

        # Add to tracking
        self._current_month_costs.append(breakdown)

        # Update Prometheus metrics
        cost_total_usd.set(self.get_current_month_total())
        cost_by_source.labels(source="youtube").set(self._get_source_total("youtube"))
        cost_by_source.labels(source="twitter").set(self._get_source_total("twitter"))
        cost_by_source.labels(source="news").set(self._get_source_total("news"))
        cost_by_source.labels(source="classification").set(self._get_source_total("classification"))

        # Check for alerts
        self._check_alerts()

        logger.info(
            "cost_recorded",
            total_cost=total,
            items_processed=items_processed,
            cost_per_item=cost_per_item,
            month_to_date=self.get_current_month_total(),
        )

        return breakdown

    def get_current_month_total(self) -> float:
        """Get total spend for current month."""
        return sum(c.total_cost for c in self._current_month_costs)

    def _get_source_total(self, source: str) -> float:
        """Get total spend for a specific source this month."""
        if source == "youtube":
            return sum(c.youtube_cost for c in self._current_month_costs)
        if source == "twitter":
            return sum(c.twitter_cost for c in self._current_month_costs)
        if source == "news":
            return sum(c.news_cost for c in self._current_month_costs)
        if source == "classification":
            return sum(c.classification_cost for c in self._current_month_costs)
        return 0.0

    def get_budget_status(self) -> BudgetStatus:
        """Get current budget utilization status."""
        current_spend = self.get_current_month_total()
        remaining = self.monthly_budget - current_spend
        utilization_pct = (
            (current_spend / self.monthly_budget * 100) if self.monthly_budget > 0 else 0
        )

        # Calculate days remaining in month
        now = datetime.utcnow()
        next_month = datetime(now.year + (now.month // 12), (now.month % 12) + 1, 1)
        days_remaining = (next_month - now).days

        # Project monthly spend based on current burn rate
        days_elapsed = (now - self._current_month_start).days + 1
        daily_burn_rate = current_spend / days_elapsed if days_elapsed > 0 else 0
        days_in_month = (next_month - self._current_month_start).days
        projected_monthly_spend = daily_burn_rate * days_in_month

        projected_overage = max(0, projected_monthly_spend - self.monthly_budget)

        # Update Prometheus gauge
        cost_budget_utilization_pct.set(utilization_pct)

        return BudgetStatus(
            monthly_budget=self.monthly_budget,
            current_spend=round(current_spend, 2),
            remaining=round(remaining, 2),
            utilization_pct=round(utilization_pct, 1),
            days_remaining_in_month=days_remaining,
            projected_monthly_spend=round(projected_monthly_spend, 2),
            projected_overage=round(projected_overage, 2),
            is_over_budget=current_spend > self.monthly_budget,
            alert_threshold_reached=utilization_pct >= 80.0,
        )

    def _check_alerts(self) -> None:
        """Check if any budget alert thresholds have been crossed."""
        status = self.get_budget_status()

        for threshold in self.alert_thresholds:
            threshold_pct = threshold * 100

            if status.utilization_pct >= threshold_pct and threshold not in self._alerts_fired:
                self._alerts_fired.add(threshold)
                cost_overage_events.inc()

                logger.warning(
                    "budget_alert_triggered",
                    threshold_pct=threshold_pct,
                    current_utilization_pct=status.utilization_pct,
                    current_spend=status.current_spend,
                    monthly_budget=status.monthly_budget,
                    projected_overage=status.projected_overage,
                )

                # TODO: Send actual alerts (email, Slack, PagerDuty)

    def get_cost_estimate(
        self,
        youtube_items: int = 0,
        twitter_items: int = 0,
        news_items: int = 0,
        classify_all: bool = True,
    ) -> dict:
        """Estimate cost for a planned pipeline run.

        Args:
            youtube_items: Number of YouTube videos to fetch
            twitter_items: Number of tweets to fetch
            news_items: Number of news articles to fetch
            classify_all: Whether to classify all items

        Returns:
            Cost estimate breakdown

        """
        return self.config.get_cost_estimate(
            youtube_items=youtube_items,
            twitter_items=twitter_items,
            news_items=news_items,
            classify_all=classify_all,
        )

    def get_stats(self) -> dict:
        """Get comprehensive cost tracking statistics."""
        status = self.get_budget_status()

        return {
            "current_month": self._current_month_start.strftime("%Y-%m"),
            "runs_this_month": len(self._current_month_costs),
            "total_items_processed": sum(c.items_processed for c in self._current_month_costs),
            "budget_status": {
                "monthly_budget_usd": status.monthly_budget,
                "current_spend_usd": status.current_spend,
                "remaining_usd": status.remaining,
                "utilization_pct": status.utilization_pct,
                "is_over_budget": status.is_over_budget,
                "projected_monthly_spend_usd": status.projected_monthly_spend,
                "projected_overage_usd": status.projected_overage,
            },
            "cost_by_source": {
                "youtube": round(self._get_source_total("youtube"), 2),
                "twitter": round(self._get_source_total("twitter"), 2),
                "news": round(self._get_source_total("news"), 2),
                "classification": round(self._get_source_total("classification"), 2),
            },
            "avg_cost_per_item": round(
                self.get_current_month_total()
                / sum(c.items_processed for c in self._current_month_costs),
                4,
            )
            if self._current_month_costs
            else 0.0,
            "alerts_fired_count": len(self._alerts_fired),
        }


# Global cost tracker instance
_cost_tracker: CostTracker | None = None


def get_cost_tracker() -> CostTracker:
    """Get the global cost tracker instance."""
    global _cost_tracker

    if _cost_tracker is None:
        _cost_tracker = CostTracker()

    return _cost_tracker
