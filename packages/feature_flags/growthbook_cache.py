# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Dynamic GrowthBook remote config cache."""

import time
from typing import Any


class GrowthBookRemoteCache:
  """Cache for GrowthBook feature flags to prevent redundant network calls."""

  def __init__(self, ttl_seconds: int = 60):
    """
    Initialize the GrowthBook cache.

    Args:
        ttl_seconds (int): Time-to-live for cached flags in seconds.
    """
    self.ttl_seconds = ttl_seconds
    self._cache: dict[str, dict[str, Any]] = {}

  def set(self, key: str, value: Any) -> None:
    """
    Set a value in the cache.

    Args:
        key (str): The feature flag key.
        value (Any): The feature flag value.
    """
    self._cache[key] = {"value": value, "timestamp": time.time()}

  def get(self, key: str) -> Any | None:
    """
    Get a value from the cache if it hasn't expired.

    Args:
        key (str): The feature flag key.

    Returns:
        Optional[Any]: The cached value if valid, None otherwise.
    """
    if key not in self._cache:
      return None

    entry = self._cache[key]
    if time.time() - entry["timestamp"] > self.ttl_seconds:
      del self._cache[key]
      return None

    return entry["value"]

  def invalidate(self, key: str) -> None:
    """
    Invalidate a specific cache entry.

    Args:
        key (str): The feature flag key to invalidate.
    """
    if key in self._cache:
      del self._cache[key]

  def clear(self) -> None:
    """Clear all cached feature flags."""
    self._cache.clear()
