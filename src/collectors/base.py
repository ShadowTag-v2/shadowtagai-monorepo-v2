# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Base source collector interface."""

import asyncio
import time
from abc import ABC, abstractmethod
from functools import wraps

from src.models import IngestedItem


def rate_limit(max_per_second: float = 1.0):
  """
  Decorator to rate limit async functions.

  Args:
      max_per_second: Maximum calls per second (default: 1.0)

  """
  min_interval = 1.0 / max_per_second
  last_called = [0.0]

  def decorator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
      elapsed = time.time() - last_called[0]
      if elapsed < min_interval:
        await asyncio.sleep(min_interval - elapsed)
      last_called[0] = time.time()
      return await func(*args, **kwargs)

    return wrapper

  return decorator


class SourceCollector(ABC):
  """Base class for all source collectors."""

  def __init__(self):
    """Initialize source collector."""
    self._items_collected = 0
    self._errors: list[str] = []

  @abstractmethod
  async def collect(self) -> list[IngestedItem]:
    """
    Collect items from source.

    MUST include retry logic and error handling.
    MUST respect rate limiting.
    MUST check robots.txt for web scraping.

    Returns:
        List of ingested items with tier classification and cost tracking

    """

  @abstractmethod
  async def check_health(self) -> bool:
    """
    Health check before collection.

    Returns:
        True if source is healthy and ready for collection

    """

  @property
  @abstractmethod
  def source_name(self) -> str:
    """
    Unique source identifier.

    Returns:
        Source name (e.g., "youtube", "twitter", "newsapi")

    """

  @property
  @abstractmethod
  def expected_items_per_day(self) -> int:
    """
    Expected number of items per collection run.

    Returns:
        Expected items per day

    """

  async def collect_with_retry(
    self, max_retries: int = 3, base_delay: float = 2.0
  ) -> list[IngestedItem]:
    """
    Collect with exponential backoff retry.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds (doubles each retry)

    Returns:
        List of ingested items

    """
    for attempt in range(max_retries + 1):
      try:
        return await self.collect()
      except Exception as e:
        self._errors.append(f"Attempt {attempt + 1} failed: {e}")
        if attempt < max_retries:
          delay = base_delay * (2**attempt)
          await asyncio.sleep(delay)
        else:
          # All retries exhausted
          return []
    return []
