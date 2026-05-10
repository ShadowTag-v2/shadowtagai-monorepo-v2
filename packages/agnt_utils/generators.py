# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""generators — Async generator manipulation utilities.

Ported from Claude Code v2.1.91 `utils/generators.ts`.
Concurrent processing with concurrency cap, sequence consumption.
"""

from __future__ import annotations

import asyncio
from typing import TypeVar
from collections.abc import AsyncGenerator, AsyncIterator

T = TypeVar("T")

_NO_VALUE = object()


async def last[T](gen: AsyncIterator[T]) -> T:
  """Consume an async iterator and return its last yielded value.

  Raises ``ValueError`` if the iterator yields no items.
  """
  last_value: object = _NO_VALUE
  async for item in gen:
    last_value = item
  if last_value is _NO_VALUE:
    raise ValueError("No items in generator")
  return last_value  # type: ignore[return-value]


async def return_value[T](gen: AsyncGenerator[object, T]) -> T:
  """Consume an async generator and return its return value."""
  result = None
  try:
    while True:
      await gen.__anext__()
  except StopAsyncIteration as exc:
    result = exc.value
  return result  # type: ignore[return-value]


async def to_array[T](gen: AsyncIterator[T]) -> list[T]:
  """Collect all items from an async iterator into a list."""
  result: list[T] = []
  async for item in gen:
    result.append(item)
  return result


async def from_array[T](values: list[T]) -> AsyncGenerator[T]:
  """Create an async generator from a list of values."""
  for value in values:
    yield value


async def merge_concurrent[T](
  generators: list[AsyncIterator[T]],
  concurrency_cap: int | None = None,
) -> AsyncGenerator[T]:
  """Run async generators concurrently up to a cap, yielding values as they arrive.

  Args:
      generators: List of async iterators to consume concurrently.
      concurrency_cap: Maximum number of generators to run at once.
          ``None`` means unlimited (all run simultaneously).

  Yields:
      Values from all generators in order of completion.
  """
  if not generators:
    return

  cap = concurrency_cap if concurrency_cap is not None else len(generators)
  queue: asyncio.Queue[tuple[T | object, bool]] = asyncio.Queue()
  waiting = list(generators)
  active: set[asyncio.Task[None]] = set()
  sentinel = object()

  async def _consume(gen: AsyncIterator[T]) -> None:
    try:
      async for item in gen:
        await queue.put((item, False))
    finally:
      await queue.put((sentinel, True))

  # Start initial batch
  while len(active) < cap and waiting:
    gen = waiting.pop(0)
    task = asyncio.create_task(_consume(gen))
    active.add(task)

  finished_count = 0
  total = len(generators)

  while finished_count < total:
    item, is_done = await queue.get()
    if is_done:
      finished_count += 1
      # Start a new generator when one finishes
      if waiting:
        gen = waiting.pop(0)
        task = asyncio.create_task(_consume(gen))
        active.add(task)
    else:
      yield item  # type: ignore[misc]
