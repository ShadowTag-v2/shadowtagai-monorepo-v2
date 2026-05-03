# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Circular buffer — ported from utils/CircularBuffer.ts.

Fixed-size ring buffer with O(1) add and O(k) get_recent/to_list.
Used for rolling windows of log entries, metrics samples, etc.
"""

from __future__ import annotations

from typing import TypeVar

T = TypeVar("T")


class CircularBuffer[T]:
    """A fixed-size circular buffer that evicts oldest items on overflow.

    >>> buf = CircularBuffer(3)
    >>> buf.add(1); buf.add(2); buf.add(3); buf.add(4)
    >>> buf.to_list()
    [2, 3, 4]
    >>> buf.get_recent(2)
    [3, 4]
    """

    __slots__ = ("_buffer", "_capacity", "_head", "_size")

    def __init__(self, capacity: int) -> None:
        if capacity < 1:
            msg = "capacity must be >= 1"
            raise ValueError(msg)
        self._buffer: list[T | None] = [None] * capacity
        self._capacity = capacity
        self._head = 0
        self._size = 0

    def add(self, item: T) -> None:
        """Add an item. Evicts the oldest if full."""
        self._buffer[self._head] = item
        self._head = (self._head + 1) % self._capacity
        if self._size < self._capacity:
            self._size += 1

    def add_all(self, items: list[T]) -> None:
        """Add multiple items in order."""
        for item in items:
            self.add(item)

    def get_recent(self, count: int) -> list[T]:
        """Return the most recent *count* items (oldest-first within window)."""
        result: list[T] = []
        start = 0 if self._size < self._capacity else self._head
        available = min(count, self._size)
        for i in range(available):
            idx = (start + self._size - available + i) % self._capacity
            result.append(self._buffer[idx])  # type: ignore[arg-type]
        return result

    def to_list(self) -> list[T]:
        """Return all items from oldest to newest."""
        if self._size == 0:
            return []
        result: list[T] = []
        start = 0 if self._size < self._capacity else self._head
        for i in range(self._size):
            idx = (start + i) % self._capacity
            result.append(self._buffer[idx])  # type: ignore[arg-type]
        return result

    def clear(self) -> None:
        """Remove all items."""
        self._buffer = [None] * self._capacity
        self._head = 0
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __bool__(self) -> bool:
        return self._size > 0

    def __repr__(self) -> str:
        return f"CircularBuffer(capacity={self._capacity}, size={self._size})"
