"""
Base Collector Interface
All source collectors inherit from this base class
"""

import time
from abc import ABC, abstractmethod
from typing import Any

from ..core.gemini_ingestion import IngestedItem, Source


class BaseCollector(ABC):
    """Abstract base class for all source collectors"""

    def __init__(self, api_key: str | None = None, config: dict[str, Any] | None = None):
        self.api_key = api_key
        self.config = config or {}
        self.rate_limit_delay = self.config.get("rate_limit_delay", 1.0)  # seconds between requests
        self.max_retries = self.config.get("max_retries", 3)
        self.timeout = self.config.get("timeout", 30)

    @abstractmethod
    def collect(self, source: Source, target_count: int) -> list[IngestedItem]:
        """
        Collect items from source

        Args:
            source: Source configuration
            target_count: Target number of items to collect

        Returns:
            List of ingested items
        """
        pass

    def _respect_rate_limit(self):
        """Sleep to respect rate limiting"""
        time.sleep(self.rate_limit_delay)

    def _calculate_cost(self, api_calls: int, tokens_used: int = 0) -> float:
        """
        Calculate cost of API usage

        Args:
            api_calls: Number of API calls made
            tokens_used: Number of tokens/units used

        Returns:
            Cost in USD
        """
        # Override in subclass with actual pricing
        return api_calls * 0.01  # Default $0.01 per call
