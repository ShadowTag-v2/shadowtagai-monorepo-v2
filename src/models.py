# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Data models for Gemini Ingestion Layer."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Tier(Enum):
  """Item tier classification."""

  TIER_1 = 1  # High-value (20% target)
  TIER_2 = 2  # Medium-value (50% target)
  TIER_3 = 3  # Low-value (30% max)


@dataclass
class IngestedItem:
  """Standardized data structure for all ingested items."""

  id: str
  source: str  # Required: e.g., "youtube", "twitter", "newsapi"
  tier: Tier  # Required: tier classification
  relevance_score: float  # Required: 0.0-1.0
  title: str
  content: str
  url: str
  published_at: datetime
  cost: float  # Required: API cost for this item
  metadata: dict = field(default_factory=dict)

  def __post_init__(self):
    """Validate item after initialization."""
    if not 0.0 <= self.relevance_score <= 1.0:
      msg = f"Relevance score must be 0.0-1.0, got {self.relevance_score}"
      raise ValueError(msg)
    if self.cost < 0:
      msg = f"Cost cannot be negative, got {self.cost}"
      raise ValueError(msg)


@dataclass
class CollectionMetrics:
  """Metrics for a collection run."""

  source: str
  items_collected: int
  runtime_seconds: float
  total_cost: float
  avg_relevance: float
  tier_distribution: dict[Tier, int]
  errors: list[str] = field(default_factory=list)
  timestamp: datetime = field(default_factory=datetime.now)

  @property
  def cost_per_item(self) -> float:
    """Calculate cost per item."""
    return self.total_cost / self.items_collected if self.items_collected > 0 else 0.0

  @property
  def success_rate(self) -> float:
    """Calculate success rate (0.0-1.0)."""
    total_attempts = self.items_collected + len(self.errors)
    return self.items_collected / total_attempts if total_attempts > 0 else 0.0
