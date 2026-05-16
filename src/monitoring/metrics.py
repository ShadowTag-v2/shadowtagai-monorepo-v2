# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Metrics collection for monitoring and observability."""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime

from src.models import IngestedItem, Tier

logger = logging.getLogger(__name__)


@dataclass
class PipelineMetrics:
  """Metrics for entire pipeline run."""

  start_time: datetime
  end_time: datetime | None = None
  total_items: int = 0
  items_by_source: dict[str, int] = field(default_factory=dict)
  items_by_tier: dict[Tier, int] = field(default_factory=dict)
  total_cost: float = 0.0
  cost_by_source: dict[str, float] = field(default_factory=dict)
  avg_relevance: float = 0.0
  source_errors: dict[str, list[str]] = field(default_factory=dict)

  @property
  def runtime_seconds(self) -> float:
    """Calculate runtime in seconds."""
    if self.end_time is None:
      return 0.0
    return (self.end_time - self.start_time).total_seconds()

  @property
  def runtime_minutes(self) -> float:
    """Calculate runtime in minutes."""
    return self.runtime_seconds / 60.0

  @property
  def cost_per_item(self) -> float:
    """Calculate cost per item."""
    return self.total_cost / self.total_items if self.total_items > 0 else 0.0

  def to_dict(self) -> dict:
    """Convert to dictionary for logging."""
    return {
      "start_time": self.start_time.isoformat(),
      "end_time": self.end_time.isoformat() if self.end_time else None,
      "runtime_minutes": round(self.runtime_minutes, 2),
      "total_items": self.total_items,
      "items_by_source": self.items_by_source,
      "items_by_tier": {
        str(tier.name): count for tier, count in self.items_by_tier.items()
      },
      "total_cost": round(self.total_cost, 4),
      "cost_by_source": {
        source: round(cost, 4) for source, cost in self.cost_by_source.items()
      },
      "cost_per_item": round(self.cost_per_item, 6),
      "avg_relevance": round(self.avg_relevance, 3),
      "source_errors": self.source_errors,
    }


class MetricsCollector:
  """Collect and aggregate metrics from pipeline runs."""

  def __init__(self):
    """Initialize metrics collector."""
    self.current_run: PipelineMetrics | None = None

  def start_run(self):
    """Start a new pipeline run."""
    self.current_run = PipelineMetrics(start_time=datetime.now())
    logger.info("Pipeline run started", extra={"timestamp": datetime.now().isoformat()})

  def end_run(self):
    """End the current pipeline run."""
    if self.current_run:
      self.current_run.end_time = datetime.now()
      logger.info("Pipeline run completed", extra=self.current_run.to_dict())

  def record_items(self, source: str, items: list[IngestedItem]):
    """
    Record items collected from a source.

    Args:
        source: Source name
        items: List of ingested items

    """
    if not self.current_run:
      return

    # Count items
    self.current_run.total_items += len(items)
    self.current_run.items_by_source[source] = len(items)

    # Count by tier
    tier_counts: dict = defaultdict(int)
    for item in items:
      tier_counts[item.tier] += 1
    self.current_run.items_by_tier = dict(tier_counts)

    # Track cost
    source_cost = sum(item.cost for item in items)
    self.current_run.total_cost += source_cost
    self.current_run.cost_by_source[source] = source_cost

    # Calculate avg relevance
    if items:
      total_relevance = sum(item.relevance_score for item in items)
      self.current_run.avg_relevance = total_relevance / self.current_run.total_items

    logger.info(
      f"Recorded {len(items)} items from {source}",
      extra={
        "source": source,
        "items": len(items),
        "cost": round(source_cost, 4),
        "tier_distribution": {
          str(tier.name): count for tier, count in tier_counts.items()
        },
      },
    )

  def record_errors(self, source: str, errors: list[str]):
    """
    Record errors from a source.

    Args:
        source: Source name
        errors: List of error messages

    """
    if not self.current_run:
      return

    self.current_run.source_errors[source] = errors

    if errors:
      logger.warning(
        f"Source {source} encountered {len(errors)} errors",
        extra={"source": source, "errors": errors},
      )

  def get_summary(self) -> dict:
    """
    Get summary of current run.

    Returns:
        Run summary dictionary

    """
    if not self.current_run:
      return {"error": "No active run"}

    return self.current_run.to_dict()
