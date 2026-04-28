# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""PNKLN Core Stack - Base Source Adapter

Abstract base class for all source adapters (YouTube, Twitter, News, RSS).
Defines common interface and shared functionality.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from datetime import datetime

import structlog

from ingestion.classification.tier_classifier import IngestedItem

logger = structlog.get_logger(__name__)


class SourceAdapter(ABC):
    """Abstract base class for source adapters.

    Each adapter is responsible for:
    1. Connecting to a specific data source (YouTube, Twitter, etc.)
    2. Fetching items based on queries or filters
    3. Normalizing data into IngestedItem format
    4. Tracking source-specific metrics and costs
    """

    def __init__(self, source_name: str):
        self.source_name = source_name
        self._items_fetched = 0
        self._cost_incurred = 0.0
        self._errors = 0
        logger.info(f"{source_name}_adapter_initialized")

    @abstractmethod
    async def fetch_items(
        self,
        queries: list[str] | None = None,
        max_items: int = 1000,
        since: datetime | None = None,
    ) -> AsyncIterator[IngestedItem]:
        """Fetch items from the source.

        Args:
            queries: Search queries or topics (source-specific)
            max_items: Maximum number of items to fetch
            since: Only fetch items newer than this timestamp

        Yields:
            IngestedItem objects

        """
        raise NotImplementedError

    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Validate API credentials for this source.

        Returns:
            True if credentials are valid, False otherwise

        """
        raise NotImplementedError

    @abstractmethod
    def get_cost_estimate(self, num_items: int) -> float:
        """Estimate cost for fetching N items from this source.

        Args:
            num_items: Number of items to estimate cost for

        Returns:
            Estimated cost in USD

        """
        raise NotImplementedError

    def _record_item_fetched(self, cost: float = 0.0) -> None:
        """Track metrics for a successfully fetched item."""
        self._items_fetched += 1
        self._cost_incurred += cost

    def _record_error(self) -> None:
        """Track error occurrence."""
        self._errors += 1

    def get_stats(self) -> dict:
        """Get adapter statistics."""
        return {
            "source": self.source_name,
            "items_fetched": self._items_fetched,
            "cost_incurred_usd": round(self._cost_incurred, 4),
            "errors": self._errors,
            "cost_per_item": (
                round(self._cost_incurred / self._items_fetched, 4)
                if self._items_fetched > 0
                else 0.0
            ),
        }

    async def close(self) -> None:
        """Close any open connections or cleanup resources.
        Override in subclasses if needed.
        """
        logger.info(f"{self.source_name}_adapter_closed", stats=self.get_stats())
