# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Memoization utilities — ported from utils/memoize.ts.

Two memoization strategies:
  1. TTL (time-to-live): write-through cache that serves stale while
     refreshing in background. Prevents cache stampede.
  2. LRU (least recently used): bounded-size cache for pure functions
     where staleness isn't relevant, only memory is.

Upstream relied on LRUCache (npm) and jsonStringify. We use
functools.lru_cache for LRU and json.dumps for key serialization.
"""

from __future__ import annotations

import functools
import json
import logging
import threading
import time
from typing import Any, TypeVar
from collections.abc import Callable

logger = logging.getLogger(__name__)

R = TypeVar("R")


# ── TTL memoization ───────────────────────────────────────────────────────────


class _TTLEntry:
  __slots__ = ("value", "timestamp", "refreshing")

  def __init__(self, value: Any, timestamp: float) -> None:
    self.value = value
    self.timestamp = timestamp
    self.refreshing = False


def memoize_with_ttl[R](
  fn: Callable[..., R],
  cache_lifetime_s: float = 300.0,
) -> Callable[..., R]:
  """Memoize with write-through TTL cache.

  Behavior:
    - Fresh: return immediately
    - Stale: return stale value, refresh in background
    - Cold miss: block and compute

  Args:
      fn: Function to memoize.
      cache_lifetime_s: Cache lifetime in seconds (default 5 min).

  Returns:
      Memoized function with a ``.cache_clear()`` method.
  """
  cache: dict[str, _TTLEntry] = {}
  lock = threading.Lock()

  def wrapper(*args: Any, **kwargs: Any) -> R:
    key = json.dumps((args, sorted(kwargs.items())), default=str)
    now = time.monotonic()

    with lock:
      entry = cache.get(key)

      # Cold miss
      if entry is None:
        value = fn(*args, **kwargs)
        cache[key] = _TTLEntry(value, now)
        return value

      # Fresh
      if now - entry.timestamp <= cache_lifetime_s:
        return entry.value

      # Stale — return stale, refresh in background
      if not entry.refreshing:
        entry.refreshing = True
        stale_entry = entry

        def _refresh() -> None:
          try:
            new_value = fn(*args, **kwargs)
            with lock:
              if cache.get(key) is stale_entry:
                cache[key] = _TTLEntry(new_value, time.monotonic())
          except Exception:
            logger.exception("TTL refresh failed for %s", key[:80])
            with lock:
              if cache.get(key) is stale_entry:
                del cache[key]

        t = threading.Thread(target=_refresh, daemon=True)
        t.start()

      return entry.value

  def cache_clear() -> None:
    with lock:
      cache.clear()

  wrapper.cache_clear = cache_clear  # type: ignore[attr-defined]
  return wrapper


# ── LRU memoization ───────────────────────────────────────────────────────────


def memoize_with_lru[R](
  fn: Callable[..., R],
  *,
  maxsize: int = 100,
  cache_key: Callable[..., str] | None = None,
) -> Callable[..., R]:
  """Memoize with bounded LRU cache.

  If ``cache_key`` is provided, it's called with the same args to produce
  a string key. Otherwise, functools.lru_cache is used directly.

  Args:
      fn: Function to memoize.
      maxsize: Maximum cache entries.
      cache_key: Optional custom key function.

  Returns:
      Memoized function with ``.cache_info()`` and ``.cache_clear()``.
  """
  if cache_key is None:
    # Use stdlib LRU directly
    return functools.lru_cache(maxsize=maxsize)(fn)

  # Custom key function → manual LRU via OrderedDict
  from collections import OrderedDict

  _cache: OrderedDict[str, Any] = OrderedDict()
  _lock = threading.Lock()

  def wrapper(*args: Any, **kwargs: Any) -> R:
    key = cache_key(*args, **kwargs)
    with _lock:
      if key in _cache:
        _cache.move_to_end(key)
        return _cache[key]

    value = fn(*args, **kwargs)
    with _lock:
      _cache[key] = value
      if len(_cache) > maxsize:
        _cache.popitem(last=False)
    return value

  def cache_clear() -> None:
    with _lock:
      _cache.clear()

  def cache_info() -> dict[str, int]:
    with _lock:
      return {"size": len(_cache), "maxsize": maxsize}

  wrapper.cache_clear = cache_clear  # type: ignore[attr-defined]
  wrapper.cache_info = cache_info  # type: ignore[attr-defined]
  return wrapper
