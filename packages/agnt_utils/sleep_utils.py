# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""sleep_utils — cancellable async sleep and timeout guards.

Ported from Claude Code v2.1.91 ``sleep.ts``.
"""

from __future__ import annotations

import asyncio
from typing import TypeVar

T = TypeVar("T")


async def cancellable_sleep(
  seconds: float,
  *,
  abort_event: asyncio.Event | None = None,
  raise_on_abort: bool = False,
) -> None:
  """Abort-responsive async sleep.

  Resolves after *seconds*, or immediately when *abort_event* is set.
  If *raise_on_abort* is True, raises ``asyncio.CancelledError`` on abort.
  """
  if abort_event is not None and abort_event.is_set():
    if raise_on_abort:
      raise asyncio.CancelledError("aborted before sleep started")
    return

  if abort_event is None:
    await asyncio.sleep(seconds)
    return

  try:
    await asyncio.wait_for(abort_event.wait(), timeout=seconds)
    # Event was set — we were aborted.
    if raise_on_abort:
      raise asyncio.CancelledError("aborted during sleep")
  except TimeoutError:
    # Normal expiry — sleep completed.
    pass


async def with_timeout(
  coro: asyncio.coroutines,
  seconds: float,
  message: str = "Operation timed out",
) -> T:
  """Race a coroutine against a timeout.

  Raises ``TimeoutError(message)`` if *coro* doesn't settle within *seconds*.
  """
  try:
    return await asyncio.wait_for(coro, timeout=seconds)
  except TimeoutError:
    raise TimeoutError(message) from None
