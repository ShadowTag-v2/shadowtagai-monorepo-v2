# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Async Suggestion Consumer — asyncio.Queue replacement for file-polling.

Replaces the file-based SuggestionConsumer with an in-memory asyncio.Queue
for interactive mode, eliminating filesystem latency and enabling real-time
suggestion delivery between KAIROS producer and the interactive consumer.

Architecture:
  Producer (KAIROS daemon) → asyncio.Queue → Consumer (interactive session)

  The file-based consumer (consumer.py) remains for daemon/batch mode.
  This module is used when SpecFlags.ASYNC_CONSUMER is enabled.

Usage::

    from speculation_engine.async_consumer import AsyncSuggestionConsumer

    consumer = AsyncSuggestionConsumer()

    # Producer side (KAIROS daemon or orchestrator)
    await consumer.publish(SuggestionEntry(text="Run tests", timestamp=time.time()))

    # Consumer side (interactive session)
    entry = await consumer.get_suggestion(timeout=5.0)
    if entry:
        await consumer.accept(entry)
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import time
from dataclasses import dataclass, field

from speculation_engine.consumer import SuggestionEntry, SUGGESTION_TTL_SECONDS

logger = logging.getLogger(__name__)


@dataclass
class AsyncSuggestionConsumer:
  """Async in-memory suggestion consumer using asyncio.Queue.

  Replaces file-based polling with zero-latency in-process delivery.

  Attributes:
      _queue: Internal asyncio.Queue for suggestion delivery.
      _ttl: Maximum suggestion age in seconds.
      _accepted_count: Number of accepted suggestions (for telemetry).
      _dismissed_count: Number of dismissed suggestions (for telemetry).
      _last_entry: Most recently retrieved entry (for peek).
  """

  _queue: asyncio.Queue[SuggestionEntry] = field(
    default_factory=lambda: asyncio.Queue(maxsize=10)
  )
  _ttl: float = SUGGESTION_TTL_SECONDS
  _accepted_count: int = 0
  _dismissed_count: int = 0
  _last_entry: SuggestionEntry | None = None

  async def publish(self, entry: SuggestionEntry) -> bool:
    """Publish a suggestion to the queue.

    Non-blocking: if the queue is full, drops the oldest entry.

    Args:
        entry: The suggestion to publish.

    Returns:
        True if published successfully.
    """
    # Drop stale entries from the queue before publishing
    await self._drain_stale()

    try:
      if self._queue.full():
        # Drop oldest entry (non-blocking)
        with contextlib.suppress(asyncio.QueueEmpty):
          self._queue.get_nowait()

      self._queue.put_nowait(entry)
      logger.debug("Published suggestion: '%s'", entry.text[:40])
      return True
    except asyncio.QueueFull:
      logger.warning("Suggestion queue full, dropping: '%s'", entry.text[:40])
      return False

  async def get_suggestion(self, *, timeout: float = 5.0) -> SuggestionEntry | None:
    """Get the next fresh suggestion from the queue.

    Blocks up to `timeout` seconds waiting for a suggestion.
    Skips stale entries automatically.

    Args:
        timeout: Maximum seconds to wait. 0 for non-blocking.

    Returns:
        The next fresh SuggestionEntry, or None if none available.
    """
    deadline = time.monotonic() + timeout

    while True:
      remaining = deadline - time.monotonic()
      if remaining <= 0:
        return None

      try:
        if timeout == 0:
          entry = self._queue.get_nowait()
        else:
          entry = await asyncio.wait_for(self._queue.get(), timeout=remaining)
      except TimeoutError, asyncio.QueueEmpty:
        return None

      # Skip stale entries
      if entry.is_fresh:
        self._last_entry = entry
        return entry
      logger.debug(
        "Skipping stale suggestion (%.0fs old): '%s'",
        entry.age_seconds,
        entry.text[:40],
      )

  async def accept(self, entry: SuggestionEntry) -> None:
    """Mark a suggestion as accepted and log telemetry.

    Args:
        entry: The suggestion that was accepted.
    """
    from speculation_engine.suggestion import SuggestionOutcome, log_suggestion_outcome

    outcome = SuggestionOutcome(
      suggestion=entry.text,
      was_accepted=True,
      generation_request_id=entry.generation_request_id,
      displayed_at=entry.timestamp,
    )
    log_suggestion_outcome(outcome, entry.text)
    self._accepted_count += 1
    logger.info("Async suggestion accepted: '%s'", entry.text[:40])

  async def dismiss(self, entry: SuggestionEntry) -> None:
    """Mark a suggestion as dismissed and log telemetry.

    Args:
        entry: The suggestion that was dismissed.
    """
    from speculation_engine.suggestion import SuggestionOutcome, log_suggestion_outcome

    outcome = SuggestionOutcome(
      suggestion=entry.text,
      was_accepted=False,
      generation_request_id=entry.generation_request_id,
      displayed_at=entry.timestamp,
    )
    log_suggestion_outcome(outcome, "")
    self._dismissed_count += 1
    logger.debug("Async suggestion dismissed: '%s'", entry.text[:40])

  async def _drain_stale(self) -> int:
    """Remove all stale entries from the queue.

    Returns:
        Number of entries drained.
    """
    drained = 0
    fresh_entries: list[SuggestionEntry] = []

    while not self._queue.empty():
      try:
        entry = self._queue.get_nowait()
        if entry.is_fresh:
          fresh_entries.append(entry)
        else:
          drained += 1
      except asyncio.QueueEmpty:
        break

    # Re-enqueue fresh entries
    for entry in fresh_entries:
      try:
        self._queue.put_nowait(entry)
      except asyncio.QueueFull:
        break

    if drained > 0:
      logger.debug("Drained %d stale suggestions from async queue", drained)
    return drained

  @property
  def pending_count(self) -> int:
    """Number of suggestions waiting in the queue."""
    return self._queue.qsize()

  @property
  def stats(self) -> dict:
    """Return consumer statistics for telemetry."""
    return {
      "pending": self.pending_count,
      "accepted": self._accepted_count,
      "dismissed": self._dismissed_count,
      "total_processed": self._accepted_count + self._dismissed_count,
    }

  def cache_status(self) -> dict:
    """Return cache status summary matching SuggestionConsumer API.

    Provides heartbeat-compatible status for KAIROS integration.
    """
    if self._queue.empty():
      return {"state": "empty", "suggestion": None, "age_s": None, "quality": None}

    if self._last_entry and self._last_entry.is_fresh:
      return {
        "state": "fresh",
        "suggestion": self._last_entry.text[:40],
        "age_s": round(self._last_entry.age_seconds, 1),
        "quality": self._last_entry.quality_score,
      }
    return {"state": "pending", "suggestion": None, "age_s": None, "quality": None}
