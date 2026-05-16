# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Base Source Class.

Abstract base for all data source implementations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class IngestionItem:
  """Standard data item from any source."""

  source: str  # Source name (e.g., "youtube", "twitter")
  item_id: str  # Unique ID from source
  url: str  # Source URL
  title: str
  content: str
  author: str = ""
  domain: str = ""
  timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
  metadata: dict[str, Any] = field(default_factory=dict)

  # Classification fields (filled by tier classifier)
  tier: str | None = None
  relevance_score: float = 0.0
  completeness_score: float = 0.0


class BaseSource(ABC):
  """Abstract base class for all sources."""

  def __init__(self, name: str, config: dict[str, Any]):
    self.name = name
    self.config = config
    self.stats = {
      "items_fetched": 0,
      "errors": 0,
      "api_calls": 0,
    }

  @abstractmethod
  async def fetch(self, limit: int = 100) -> list[IngestionItem]:
    """Fetch items from source."""
    pass

  def get_stats(self) -> dict[str, Any]:
    """Get source statistics."""
    return {"source": self.name, **self.stats}
