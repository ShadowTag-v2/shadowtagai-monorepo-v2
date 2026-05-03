# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""set_ops — Hot-path optimized set operations.

Ported from Claude Code v2.1.91 `utils/set.ts`.

The original code explicitly notes that these functions are "hot" and are
optimized for raw iteration speed rather than leveraging built-in set
operators. In Python, we retain the same imperative style for parity, but
also offer the `*_native` variants that use Python's built-in set algebra
for callers who prefer idiomatic Python.

Note: Python's built-in ``set.difference``, ``set.intersection``, etc.
are implemented in C and are typically faster than manual iteration for
large sets. The imperative versions here exist for API parity with the
upstream TypeScript codebase and for micro-benchmark consistency.
"""

from __future__ import annotations

from typing import AbstractSet, TypeVar
from collections.abc import Iterable

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Imperative (upstream-parity) variants
# ---------------------------------------------------------------------------
def difference[T](a: set[T], b: set[T]) -> set[T]:
    """Return elements in *a* that are not in *b*.

    Optimized for speed — iterates *a* once with O(1) ``has`` checks on *b*.
    """
    result: set[T] = set()
    for item in a:
        if item not in b:
            result.add(item)
    return result


def intersects[T](a: set[T], b: set[T]) -> bool:
    """Return ``True`` if *a* and *b* share at least one element.

    Short-circuits on the first match for hot-path performance.
    """
    if not a or not b:
        return False
    return any(item in b for item in a)


def every[T](a: AbstractSet[T], b: AbstractSet[T]) -> bool:
    """Return ``True`` if every element of *a* is also in *b*.

    Equivalent to ``a.issubset(b)`` but uses explicit iteration.
    """
    return all(item in b for item in a)


def union[T](a: set[T], b: set[T]) -> set[T]:
    """Return the union of *a* and *b* as a new set."""
    result: set[T] = set()
    for item in a:
        result.add(item)
    for item in b:
        result.add(item)
    return result


# ---------------------------------------------------------------------------
# Native (idiomatic Python) variants — use these when you don't need
# micro-benchmark parity with the TypeScript codebase.
# ---------------------------------------------------------------------------
def difference_native[T](a: set[T], b: set[T]) -> set[T]:
    """Return ``a - b`` using Python's built-in set difference."""
    return a - b


def intersects_native[T](a: set[T], b: set[T]) -> bool:
    """Return ``True`` if ``a`` and ``b`` are not disjoint."""
    return not a.isdisjoint(b)


def every_native[T](a: AbstractSet[T], b: AbstractSet[T]) -> bool:
    """Return ``True`` if ``a ⊆ b``."""
    return a.issubset(b)


def union_native[T](a: set[T], b: set[T]) -> set[T]:
    """Return ``a | b`` using Python's built-in set union."""
    return a | b


# ---------------------------------------------------------------------------
# Convenience
# ---------------------------------------------------------------------------
def symmetric_difference[T](a: set[T], b: set[T]) -> set[T]:
    """Return elements in either *a* or *b* but not both."""
    return a.symmetric_difference(b)


def intersection[T](a: set[T], b: set[T]) -> set[T]:
    """Return elements common to both *a* and *b*."""
    return a & b


def unique[T](items: Iterable[T]) -> list[T]:
    """Return unique items preserving first-seen order."""
    seen: set[T] = set()
    result: list[T] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
