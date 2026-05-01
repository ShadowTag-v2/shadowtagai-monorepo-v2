# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""array_utils — Functional array utilities.

Ported from Claude Code v2.1.91 `utils/array.ts` + `utils/objectGroupBy.ts`.
"""

from __future__ import annotations

from typing import TypeVar
from collections.abc import Callable, Hashable, Iterable

T = TypeVar("T")
K = TypeVar("K", bound=Hashable)


def intersperse(items: list[T], separator_fn: Callable[[int], T]) -> list[T]:
    """Insert separators between items using a factory function.

    >>> intersperse([1, 2, 3], lambda i: 0)
    [1, 0, 2, 0, 3]
    """
    result: list[T] = []
    for i, item in enumerate(items):
        if i > 0:
            result.append(separator_fn(i))
        result.append(item)
    return result


def count(items: Iterable[T], predicate: Callable[[T], object]) -> int:
    """Count items matching a predicate.

    Optimized for speed — single pass with no intermediate list.
    """
    n = 0
    for item in items:
        if predicate(item):
            n += 1
    return n


def uniq(items: Iterable[T]) -> list[T]:
    """Return unique items preserving first-seen order."""
    seen: set[int] = set()
    result: list[T] = []
    for item in items:
        item_hash = hash(item)
        if item_hash not in seen:
            seen.add(item_hash)
            result.append(item)
    return result


def group_by(
    items: Iterable[T],
    key_selector: Callable[[T, int], K],
) -> dict[K, list[T]]:
    """Group items by a key selector function.

    Mirrors ECMAScript ``Object.groupBy`` (TC39 Stage 4).

    >>> group_by(["a", "bb", "c", "dd"], lambda x, i: len(x))
    {1: ['a', 'c'], 2: ['bb', 'dd']}
    """
    result: dict[K, list[T]] = {}
    for index, item in enumerate(items):
        key = key_selector(item, index)
        if key not in result:
            result[key] = []
        result[key].append(item)
    return result
