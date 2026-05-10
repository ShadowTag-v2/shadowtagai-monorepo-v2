# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Streaming Watchdog — Monitors async generators for stalls and timeouts.

Ported from src/services/watchdog.py with enhancements:
  - Inter-chunk stall detection (gap between yields)
  - Callback hooks for KAIROS heartbeat integration
  - Structured event logging
  - Configurable stall/timeout policies

Usage:
    watchdog = StreamingWatchdog(
        on_stall=lambda gap: logger.warning("Stall: %ss", gap),
        on_timeout=lambda elapsed: logger.error("Timeout: %ss", elapsed),
    )
    async for chunk in watchdog.watch(stream, timeout=30.0, stall_threshold=5.0):
        process(chunk)
"""

from __future__ import annotations

import logging
import time
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any
from collections.abc import Callable

logger = logging.getLogger(__name__)

# Type alias for callbacks
StallCallback = Callable[[float], None]  # receives gap_seconds
TimeoutCallback = Callable[[float], None]  # receives elapsed_seconds


@dataclass(slots=True)
class WatchdogStats:
  """Accumulated statistics from a watchdog session."""

  chunks_yielded: int = 0
  total_elapsed: float = 0.0
  max_gap: float = 0.0
  stall_count: int = 0
  timed_out: bool = False


class StreamingWatchdog:
  """Wraps an async generator to enforce timeout and stall detection.

  Enhanced from the original src/services/watchdog.py to track inter-chunk
  gaps and fire callbacks for integration with KAIROS heartbeat monitoring.
  """

  def __init__(
    self,
    *,
    on_stall: StallCallback | None = None,
    on_timeout: TimeoutCallback | None = None,
  ) -> None:
    self._on_stall = on_stall
    self._on_timeout = on_timeout
    self._stats = WatchdogStats()

  @property
  def stats(self) -> WatchdogStats:
    """Access accumulated statistics from the last watch() call."""
    return self._stats

  async def watch(
    self,
    stream: AsyncGenerator[Any],
    timeout: float = 30.0,
    stall_threshold: float = 5.0,
  ) -> AsyncGenerator[Any]:
    """Yields chunks from the stream while monitoring for stalls.

    Args:
        stream: The async generator to monitor.
        timeout: Maximum total time allowed for the stream (seconds).
        stall_threshold: Time between chunks that triggers a stall
            callback (seconds). Does NOT abort — only the total timeout
            raises TimeoutError.

    Yields:
        Chunks from the underlying stream.

    Raises:
        TimeoutError: If total timeout is exceeded.
    """
    stats = WatchdogStats()
    start_time = time.monotonic()
    last_chunk_time = start_time

    try:
      async for chunk in stream:
        now = time.monotonic()
        elapsed = now - start_time
        gap = now - last_chunk_time

        # Track max gap
        if gap > stats.max_gap:
          stats.max_gap = gap

        # Stall detection — fires callback but does NOT abort
        if gap > stall_threshold:
          stats.stall_count += 1
          logger.debug(
            "Watchdog stall detected: %.1fs gap (threshold: %.1fs)",
            gap,
            stall_threshold,
          )
          if self._on_stall:
            try:
              self._on_stall(gap)
            except Exception:
              logger.debug("Stall callback error", exc_info=True)

        # Total timeout — raises
        if elapsed > timeout:
          stats.timed_out = True
          stats.total_elapsed = elapsed
          logger.warning(
            "Watchdog timeout: %.1fs elapsed (limit: %.1fs)",
            elapsed,
            timeout,
          )
          if self._on_timeout:
            try:
              self._on_timeout(elapsed)
            except Exception:
              logger.debug("Timeout callback error", exc_info=True)
          raise TimeoutError(f"Stream exceeded total timeout of {timeout}s")

        last_chunk_time = now
        stats.chunks_yielded += 1
        yield chunk
    finally:
      stats.total_elapsed = time.monotonic() - start_time
      self._stats = stats
