"""State machine for gating message writes during an initial flush.

Direct port of src/bridge/flushGate.ts — this is a clean, pure data
structure with no network dependencies. Ported as-is.
"""

from __future__ import annotations

from typing import TypeVar

T = TypeVar("T")


class FlushGate[T]:
  """FIFO-bounded queue that gates message writes during initial flush.

  Lifecycle:
      start() → enqueue() returns True, items are queued
      end()   → returns queued items for draining, enqueue() returns False
      drop()  → discards queued items (permanent transport close)
      deactivate() → clears active flag without dropping items
  """

  __slots__ = ("_active", "_pending")

  def __init__(self) -> None:
    self._active: bool = False
    self._pending: list[T] = []

  @property
  def active(self) -> bool:
    """Whether flush is currently in progress."""
    return self._active

  @property
  def pending_count(self) -> int:
    """Number of items currently queued."""
    return len(self._pending)

  def start(self) -> None:
    """Mark flush as in-progress. enqueue() will start queuing items."""
    self._active = True

  def end(self) -> list[T]:
    """End the flush and return any queued items for draining.

    Caller is responsible for sending the returned items.
    """
    self._active = False
    items = self._pending[:]
    self._pending.clear()
    return items

  def enqueue(self, *items: T) -> bool:
    """Queue items if flush is active.

    Returns True if items were queued, False if flush is not active
    (caller should send directly).
    """
    if not self._active:
      return False
    self._pending.extend(items)
    return True

  def drop(self) -> int:
    """Discard all queued items (permanent transport close).

    Returns the number of items dropped.
    """
    self._active = False
    count = len(self._pending)
    self._pending.clear()
    return count

  def deactivate(self) -> None:
    """Clear the active flag without dropping queued items.

    Used when the transport is replaced — the new transport's flush
    will drain the pending items.
    """
    self._active = False
