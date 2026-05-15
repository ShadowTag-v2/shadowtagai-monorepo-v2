"""FIFO-bounded UUID set for echo/dedup filtering.

Direct port of BoundedUUIDSet from src/bridge/bridgeMessaging.ts.
Pure data structure, no network dependencies.
"""

from __future__ import annotations


class BoundedUUIDSet:
  """FIFO-bounded set backed by a circular buffer.

  Evicts the oldest entry when capacity is reached, keeping memory
  usage constant at O(capacity). Messages are added in chronological
  order, so evicted entries are always the oldest.
  """

  __slots__ = ("_capacity", "_ring", "_set", "_write_idx")

  def __init__(self, capacity: int) -> None:
    if capacity < 1:
      msg = f"capacity must be >= 1, got {capacity}"
      raise ValueError(msg)
    self._capacity: int = capacity
    self._ring: list[str | None] = [None] * capacity
    self._set: set[str] = set()
    self._write_idx: int = 0

  def add(self, uuid_str: str) -> None:
    """Add a UUID to the set, evicting the oldest if at capacity."""
    if uuid_str in self._set:
      return
    # Evict the entry at the current write position
    evicted = self._ring[self._write_idx]
    if evicted is not None:
      self._set.discard(evicted)
    self._ring[self._write_idx] = uuid_str
    self._set.add(uuid_str)
    self._write_idx = (self._write_idx + 1) % self._capacity

  def has(self, uuid_str: str) -> bool:
    """Check if a UUID is in the set."""
    return uuid_str in self._set

  def __contains__(self, uuid_str: str) -> bool:
    return self.has(uuid_str)

  def __len__(self) -> int:
    return len(self._set)

  def clear(self) -> None:
    """Remove all entries from the set."""
    self._set.clear()
    self._ring[:] = [None] * self._capacity
    self._write_idx = 0
