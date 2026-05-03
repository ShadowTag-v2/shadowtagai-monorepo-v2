# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""sequential — async sequential execution wrapper.

Ported from Claude Code v2.1.91 ``sequential.ts``.
Prevents race conditions by ensuring concurrent calls to a wrapped
async function are executed one at a time in FIFO order, each receiving
its own return value.

Usage::

    from packages.agnt_utils.sequential import sequential

    @sequential
    async def write_config(path: str, data: dict) -> None:
        ...  # only one call runs at a time

    # Or wrap an existing function:
    safe_write = sequential(write_config_impl)
"""

from __future__ import annotations

import asyncio
import functools
from collections import deque
from typing import Any, TypeVar
from collections.abc import Awaitable, Callable

R = TypeVar("R")


def sequential[R](
    fn: Callable[..., Awaitable[R]],
) -> Callable[..., Awaitable[R]]:
    """Wrap an async function so concurrent invocations execute sequentially.

    Each call receives its own return value (or exception).  Order is FIFO.
    The wrapper is reentrant-safe: items enqueued while the processor is
    running are drained in the same loop iteration, avoiding a second
    ``processQueue`` coroutine.
    """
    queue: deque[tuple[tuple[Any, ...], dict[str, Any], asyncio.Future[R]]] = deque()
    processing = False

    async def _process() -> None:
        nonlocal processing
        if processing:
            return
        processing = True
        try:
            while queue:
                args, kwargs, future = queue.popleft()
                if future.cancelled():
                    continue
                try:
                    result = await fn(*args, **kwargs)
                    if not future.done():
                        future.set_result(result)
                except BaseException as exc:
                    if not future.done():
                        future.set_exception(exc)
        finally:
            processing = False
            # Drain any items added while we were in the finally block.
            if queue:
                asyncio.ensure_future(_process())

    @functools.wraps(fn)
    async def wrapper(*args: Any, **kwargs: Any) -> R:
        loop = asyncio.get_running_loop()
        future: asyncio.Future[R] = loop.create_future()
        queue.append((args, kwargs, future))
        asyncio.ensure_future(_process())
        return await future

    # Expose queue length for diagnostics.
    wrapper.pending = lambda: len(queue)  # type: ignore[attr-defined]
    return wrapper
