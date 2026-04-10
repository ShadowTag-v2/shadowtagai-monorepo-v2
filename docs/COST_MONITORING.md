# Cost Monitoring Guide - Gemini Ingestion Layer

## Overview

The Gemini Ingestion Layer operates on a **$77/month budget** (~$2.57/day) to collect ~30,000 items per month, targeting a **cost per item of $0.0026**. This guide details cost tracking, monitoring, optimization strategies, and alerting.

## Budget Breakdown

### Monthly Budget: $77

| Component               | Monthly Cost | % of Budget | Notes                                                                |
| ----------------------- | ------------ | ----------- | -------------------------------------------------------------------- |
| **YouTube Data API v3** | $25          | 32%         | 10,000 quota units/day @ $0 (free tier), additional units @ $0.05/1k |
| **Twitter/X API v2**    | $20          | 26%         | Basic tier: $100/month (negotiated discount to $20)                  |
| **NewsAPI.org**         | $15          | 19%         | Developer plan: $449/month (using free tier + fallback)              |
| **Gemini 2.0 Pro API**  | $12          | 16%         | Relevance scoring: ~30k requests @ $0.0004/request                   |
| **GKE Compute**         | $3           | 4%          | CronJob runtime: ~45 min/day @ $0.10/hour                            |
| **Database Storage**    | $2           | 3%          | PostgreSQL: 10GB @ $0.20/GB                                          |
| **Buffer**              | $0           | 0%          | Remaining for overages                                               |

### Cost Per Item Target: $0.0026

```
Monthly Budget:     $77
Target Items/Month: 30,000
Cost Per Item:      $77 ÷ 30,000 = $0.0026
```

## Cost Tracking Implementation

### 1. API Call Cost Logging

Every API call must log its cost in structured format:

```python
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

@dataclass
class APICallCost:
    """Track cost of individual API calls."""
    timestamp: datetime
    source: str          # e.g., "youtube", "twitter", "newsapi"
    endpoint: str        # e.g., "/search/list", "/tweets/search"
    method: str          # e.g., "GET", "POST"
    cost: float          # USD
    items_returned: int  # Number of items from this call
    quota_used: Optional[int] = None  # For quota-based APIs (YouTube)

    def to_dict(self) -> dict:
        """Convert to dict for logging."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "endpoint": self.endpoint,
            "method": self.method,
            "cost_usd": round(self.cost, 6),
            "items_returned": self.items_returned,
            "cost_per_item": round(self.cost / self.items_returned, 6) if self.items_returned > 0 else 0,
            "quota_used": self.quota_used,
        }

def log_api_cost(call_cost: APICallCost):
    """Log API call cost in structured format."""
    logger.info(
        "api_call_cost",
        extra=call_cost.to_dict()
    )
```

### 2. Source-Specific Cost Calculators

#### YouTube Data API v3

```python
class YouTubeCostCalculator:
    """Calculate costs for YouTube Data API v3."""

    # YouTube API quota costs (per operation)
    QUOTA_COSTS = {
        "search": 100,
        "videos": 1,
        "channels": 1,
    }

    # Pricing (after free tier exhausted)
    COST_PER_QUOTA_UNIT = 0.00005  # $0.05 per 1,000 units

    def calculate_cost(self, operation: str, count: int = 1) -> float:
        """
        Calculate cost for YouTube API operation.

        Args:
            operation: API operation (search, videos, channels)
            count: Number of API calls

        Returns:
            float: Cost in USD
        """
        quota_cost = self.QUOTA_COSTS.get(operation, 1) * count
        # Free tier: 10,000 units/day
        # Assume we stay within free tier for now
        return 0.0  # Update if exceeding free tier

    def track_quota_usage(self, daily_quota_used: int) -> dict:
        """
        Track daily quota usage and project monthly cost.

        Args:
            daily_quota_used: Quota units used today

        Returns:
            dict: Quota status and projected cost
        """
        free_tier_limit = 10000
        remaining = max(0, free_tier_limit - daily_quota_used)

        if daily_quota_used <= free_tier_limit:
            projected_monthly_cost = 0.0
        else:
            overage = daily_quota_used - free_tier_limit
            projected_monthly_cost = overage * self.COST_PER_QUOTA_UNIT * 30

        return {
            "daily_quota_used": daily_quota_used,
            "free_tier_limit": free_tier_limit,
            "remaining_quota": remaining,
            "projected_monthly_cost": projected_monthly_cost,
            "status": "ok" if remaining > 1000 else "warning",
        }
```

#### Twitter/X API v2

```python
class TwitterCostCalculator:
    """Calculate costs for Twitter/X API v2."""

    # Twitter API pricing (Basic tier)
    MONTHLY_FLAT_FEE = 20.0  # Negotiated from $100 to $20
    INCLUDED_REQUESTS = 10000  # Per month
    COST_PER_ADDITIONAL_REQUEST = 0.002  # $2 per 1,000 additional

    def calculate_daily_cost(self, requests_today: int, day_of_month: int) -> float:
        """
        Calculate Twitter API cost for today.

        Args:
            requests_today: Number of API requests made today
            day_of_month: Day of the month (1-30)

        Returns:
            float: Cost in USD for today
        """
        # Flat fee is amortized daily
        daily_flat_fee = self.MONTHLY_FLAT_FEE / 30

        # Check if we're over included requests for the month
        monthly_requests_so_far = requests_today * day_of_month
        if monthly_requests_so_far > self.INCLUDED_REQUESTS:
            overage = monthly_requests_so_far - self.INCLUDED_REQUESTS
            overage_cost = overage * self.COST_PER_ADDITIONAL_REQUEST
            return daily_flat_fee + (overage_cost / day_of_month)
        else:
            return daily_flat_fee
```

#### Gemini 2.0 Pro API

```python
class GeminiCostCalculator:
    """Calculate costs for Gemini 2.0 Pro API."""

    # Gemini pricing (as of 2025)
    COST_PER_INPUT_TOKEN = 0.00000025   # $0.25 per 1M tokens
    COST_PER_OUTPUT_TOKEN = 0.0000010   # $1.00 per 1M tokens

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate Gemini API cost.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            float: Cost in USD
        """
        input_cost = input_tokens * self.COST_PER_INPUT_TOKEN
        output_cost = output_tokens * self.COST_PER_OUTPUT_TOKEN
        return input_cost + output_cost

    def estimate_relevance_scoring_cost(self, num_items: int, avg_item_length: int = 500) -> float:
        """
        Estimate cost for relevance scoring.

        Args:
            num_items: Number of items to score
            avg_item_length: Average item length in tokens

        Returns:
            float: Estimated cost in USD
        """
        # Prompt overhead: ~100 tokens per item
        # Item content: avg_item_length tokens
        # Output: ~10 tokens (just a score)
        input_tokens_per_item = 100 + avg_item_length
        output_tokens_per_item = 10

        total_input = num_items * input_tokens_per_item
        total_output = num_items * output_tokens_per_item

        return self.calculate_cost(total_input, total_output)
```

### 3. Cost Aggregation & Reporting

```python
from collections import defaultdict
from typing import List

class CostAggregator:
    """Aggregate and report costs across all sources."""

    def __init__(self):
        self.costs: List[APICallCost] = []

    def add_cost(self, cost: APICallCost):
        """Add an API call cost to aggregator."""
        self.costs.append(cost)
        log_api_cost(cost)

    def get_daily_summary(self, date: datetime.date) -> dict:
        """
        Get cost summary for a specific day.

        Args:
            date: Date to summarize

        Returns:
            dict: Cost summary by source
        """
        daily_costs = [
            c for c in self.costs
            if c.timestamp.date() == date
        ]

        by_source = defaultdict(lambda: {"cost": 0.0, "items": 0, "calls": 0})

        for cost in daily_costs:
            by_source[cost.source]["cost"] += cost.cost
            by_source[cost.source]["items"] += cost.items_returned
            by_source[cost.source]["calls"] += 1

        total_cost = sum(s["cost"] for s in by_source.values())
        total_items = sum(s["items"] for s in by_source.values())

        return {
            "date": date.isoformat(),
            "total_cost": round(total_cost, 4),
            "total_items": total_items,
            "cost_per_item": round(total_cost / total_items, 6) if total_items > 0 else 0,
            "by_source": dict(by_source),
            "daily_budget": 2.57,
            "budget_utilization_pct": round(total_cost / 2.57 * 100, 1),
        }

    def get_monthly_projection(self, days_elapsed: int) -> dict:
        """
        Project monthly cost based on current usage.

        Args:
            days_elapsed: Number of days elapsed this month

        Returns:
            dict: Monthly projection
        """
        if days_elapsed == 0:
            return {"error": "No data yet this month"}

        month_costs = [
            c for c in self.costs
            if c.timestamp.month == datetime.now().month
        ]

        total_cost_so_far = sum(c.cost for c in month_costs)
        avg_daily_cost = total_cost_so_far / days_elapsed
        projected_monthly_cost = avg_daily_cost * 30

        return {
            "days_elapsed": days_elapsed,
            "cost_so_far": round(total_cost_so_far, 2),
            "avg_daily_cost": round(avg_daily_cost, 2),
            "projected_monthly_cost": round(projected_monthly_cost, 2),
            "monthly_budget": 77.0,
            "projected_variance": round(projected_monthly_cost - 77.0, 2),
            "on_track": projected_monthly_cost <= 77.0,
        }
```

## Cost Optimization Strategies

### 1. Caching

Implement aggressive caching to reduce duplicate API calls:

```python
from functools import lru_cache
from datetime import datetime, timedelta
import hashlib

class CachedAPIClient:
    """API client with built-in caching."""

    def __init__(self, cache_ttl_hours: int = 1):
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self.cache = {}

    def _cache_key(self, url: str, params: dict) -> str:
        """Generate cache key from URL and params."""
        params_str = str(sorted(params.items()))
        return hashlib.md5(f"{url}{params_str}".encode()).hexdigest()

    async def get(self, url: str, params: dict) -> dict:
        """
        Make GET request with caching.

        Args:
            url: URL to request
            params: Query parameters

        Returns:
            dict: Response data
        """
        cache_key = self._cache_key(url, params)

        # Check cache
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_ttl:
                logger.info(f"Cache hit for {url}", extra={"saved_cost": True})
                return cached_data

        # Cache miss - make actual request
        response = await self._make_request(url, params)
        self.cache[cache_key] = (response, datetime.now())
        return response
```

### 2. Batch Processing

Batch API calls when possible to reduce overhead:

```python
async def batch_gemini_scoring(items: List[IngestedItem], batch_size: int = 10) -> List[float]:
    """
    Score items in batches to optimize Gemini API usage.

    Args:
        items: Items to score
        batch_size: Number of items per batch

    Returns:
        List[float]: Relevance scores
    """
    scores = []

    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]

        # Single API call for multiple items
        prompt = "Score the relevance of these items:\n\n"
        for idx, item in enumerate(batch):
            prompt += f"{idx+1}. {item.title}: {item.content[:200]}\n"

        response = await gemini_client.generate(prompt)
        batch_scores = parse_scores(response)
        scores.extend(batch_scores)

    return scores
```

### 3. Smart Source Prioritization

Prioritize low-cost, high-value sources:

```python
class SourcePrioritizer:
    """Prioritize sources based on cost efficiency and value."""

    def __init__(self):
        self.source_metrics = {}

    def update_metrics(self, source: str, cost: float, items: int, avg_relevance: float):
        """Update metrics for a source."""
        if source not in self.source_metrics:
            self.source_metrics[source] = {
                "total_cost": 0.0,
                "total_items": 0,
                "total_relevance": 0.0,
                "calls": 0,
            }

        metrics = self.source_metrics[source]
        metrics["total_cost"] += cost
        metrics["total_items"] += items
        metrics["total_relevance"] += avg_relevance * items
        metrics["calls"] += 1

    def get_source_efficiency(self, source: str) -> float:
        """
        Calculate efficiency score for a source.

        Efficiency = (Relevance × Items) / Cost

        Returns:
            float: Efficiency score (higher is better)
        """
        metrics = self.source_metrics.get(source, {})
        if not metrics or metrics["total_cost"] == 0:
            return 0.0

        avg_relevance = metrics["total_relevance"] / metrics["total_items"]
        items_per_dollar = metrics["total_items"] / metrics["total_cost"]
        return avg_relevance * items_per_dollar

    def prioritize_sources(self, sources: List[str]) -> List[str]:
        """
        Sort sources by efficiency.

        Args:
            sources: List of source names

        Returns:
            List[str]: Sources sorted by efficiency (best first)
        """
        return sorted(sources, key=self.get_source_efficiency, reverse=True)
```

### 4. Fallback to Free Tiers

Use free alternatives when paid APIs are exhausted:

```python
class NewsCollector:
    """News collector with paid + free tier fallback."""

    def __init__(self):
        self.newsapi_key = os.getenv("NEWSAPI_KEY")
        self.free_rss_feeds = [
            "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
            "https://www.theguardian.com/world/rss",
            # ... more free RSS feeds
        ]

    async def collect(self) -> List[IngestedItem]:
        """Collect news with fallback strategy."""
        items = []

        # Try paid API first (if budget allows)
        if self.is_under_budget():
            try:
                items = await self.collect_from_newsapi()
            except Exception as e:
                logger.warning(f"NewsAPI failed: {e}, falling back to RSS")

        # Fallback to free RSS if paid API failed or budget exceeded
        if not items:
            items = await self.collect_from_rss_feeds()

        return items

    def is_under_budget(self) -> bool:
        """Check if we're under daily budget for NewsAPI."""
        # Check cost aggregator
        daily_cost = cost_aggregator.get_daily_summary(datetime.now().date())
        return daily_cost["total_cost"] < 2.00  # Reserve $0.57 for other sources
```

## Cost Monitoring Dashboard

### Grafana Panels

#### 1. Daily Cost Trend

```promql
# Daily cost by source
sum by (source) (increase(ingestion_api_cost_usd_total[1d]))
```

#### 2. Cost Per Item Trend

```promql
# 7-day rolling average cost per item
avg_over_time(
  sum(increase(ingestion_api_cost_usd_total[1d])) /
  sum(increase(ingestion_items_collected_total[1d]))
[7d])
```

#### 3. Budget Utilization

```promql
# Daily budget utilization percentage
(sum(increase(ingestion_api_cost_usd_total[1d])) / 2.57) * 100
```

#### 4. Monthly Projection

```promql
# Projected monthly cost based on current trend
(
  sum(increase(ingestion_api_cost_usd_total[1d]))
  * 30
)
```

### Prometheus Metrics

```python
from prometheus_client import Counter, Gauge, Histogram

# Cost metrics
api_cost_total = Counter(
    "ingestion_api_cost_usd_total",
    "Total API cost in USD",
    ["source", "endpoint"]
)

cost_per_item = Gauge(
    "ingestion_cost_per_item_usd",
    "Current cost per item in USD"
)

daily_budget_utilization = Gauge(
    "ingestion_daily_budget_utilization_percent",
    "Daily budget utilization percentage"
)

cost_distribution = Histogram(
    "ingestion_api_call_cost_usd",
    "Distribution of individual API call costs",
    buckets=[0.0001, 0.001, 0.01, 0.1, 1.0]
)
```

## Alerting

### Cost Alert Thresholds

```yaml
# Critical Alerts
- alert: DailyCostOverrun
  expr: sum(increase(ingestion_api_cost_usd_total[1d])) > 3.00
  for: 1h
  annotations:
    summary: "Daily cost exceeded $3.00"
    severity: critical

- alert: MonthlyProjectionOverrun
  expr: |
    (
      sum(increase(ingestion_api_cost_usd_total[1d]))
      * (30 - day_of_month())
    ) > 90
  for: 6h
  annotations:
    summary: "Projected monthly cost exceeds $90"
    severity: critical

# Warning Alerts
- alert: CostPerItemHigh
  expr: |
    (
      sum(increase(ingestion_api_cost_usd_total[1d])) /
      sum(increase(ingestion_items_collected_total[1d]))
    ) > 0.004
  for: 3d
  annotations:
    summary: "Cost per item above $0.004 for 3 days"
    severity: warning

- alert: SourceCostAnomalous
  expr: |
    (
      sum by (source) (increase(ingestion_api_cost_usd_total[1h]))
      > 2 * avg_over_time(sum by (source) (increase(ingestion_api_cost_usd_total[1h]))[7d])
    )
  annotations:
    summary: "Source cost anomaly detected"
    severity: warning
```

## Cost Reporting

### Daily Cost Email Report

```python
def generate_daily_cost_report(date: datetime.date) -> str:
    """Generate daily cost report for email."""
    summary = cost_aggregator.get_daily_summary(date)

    report = f"""
# Daily Cost Report - {date.isoformat()}

## Summary
- **Total Cost**: ${summary['total_cost']:.2f}
- **Total Items**: {summary['total_items']}
- **Cost Per Item**: ${summary['cost_per_item']:.4f}
- **Budget Utilization**: {summary['budget_utilization_pct']:.1f}% of ${summary['daily_budget']:.2f}

## By Source
"""

    for source, metrics in summary["by_source"].items():
        cost_per_item = metrics["cost"] / metrics["items"] if metrics["items"] > 0 else 0
        report += f"""
### {source.title()}
- Cost: ${metrics['cost']:.2f}
- Items: {metrics['items']}
- API Calls: {metrics['calls']}
- Cost/Item: ${cost_per_item:.4f}
"""

    return report
```

## References

- [Architecture Documentation](./ARCHITECTURE.md)
- [Quality Gates](./QUALITY_GATES.md)
- [API Pricing Documentation](https://cloud.google.com/pricing)
