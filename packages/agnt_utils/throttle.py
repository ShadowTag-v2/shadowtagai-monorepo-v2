# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""throttle — Rate-limiting decorator for hot-path functions.

Ported from Claude Code v2.1.91 throttle patterns found in:
  - utils/cleanup.ts (cleanupOldVersionsThrottled)
  - hooks/fileSuggestions.ts (REFRESH_THROTTLE_MS)
  - utils/queryHelpers.ts (TOOL_PROGRESS_THROTTLE_MS)

Provides both synchronous and async throttle decorators with:
  - Leading/trailing edge control
  - Cooldown-based suppression (marker file or in-memory)
  - Cancel/flush support
"""

from __future__ import annotations

import functools
import time
from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


class ThrottledFunction:
    """A throttled wrapper around a callable.

    Ensures the wrapped function is called at most once every `interval_ms`
    milliseconds. Supports leading edge (call immediately, suppress until
    cooldown) and trailing edge (call after cooldown with last args).

    Args:
        fn: The function to throttle.
        interval_ms: Minimum time between calls in milliseconds.
        leading: If True, call on the leading edge (first invocation).
        trailing: If True, call on the trailing edge (after cooldown, with
            the most recent arguments).
    """

    def __init__(
        self,
        fn: Callable[..., Any],
        interval_ms: float = 1000,
        *,
        leading: bool = True,
        trailing: bool = True,
    ) -> None:
        self._fn = fn
        self._interval_s = interval_ms / 1000.0
        self._leading = leading
        self._trailing = trailing

        self._last_call_time: float = 0.0
        self._pending_args: tuple[Any, ...] | None = None
        self._pending_kwargs: dict[str, Any] | None = None
        self._timer: Any = None
        self._result: Any = None

        functools.update_wrapper(self, fn)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        now = time.monotonic()
        elapsed = now - self._last_call_time

        if elapsed >= self._interval_s:
            # Cooldown has passed
            if self._leading:
                self._last_call_time = now
                self._result = self._fn(*args, **kwargs)
                return self._result
            else:
                # No leading edge — schedule trailing
                self._pending_args = args
                self._pending_kwargs = kwargs
                if self._timer is None:
                    self._schedule_trailing()
                return self._result
        else:
            # Still in cooldown — store args for trailing edge
            self._pending_args = args
            self._pending_kwargs = kwargs
            if self._trailing and self._timer is None:
                remaining = self._interval_s - elapsed
                self._schedule_trailing(remaining)
            return self._result

    def _schedule_trailing(self, delay: float | None = None) -> None:
        """Schedule a trailing edge call using threading.Timer."""
        import threading

        if delay is None:
            delay = self._interval_s

        def _fire() -> None:
            self._timer = None
            if self._pending_args is not None:
                self._last_call_time = time.monotonic()
                self._result = self._fn(*self._pending_args, **(self._pending_kwargs or {}))
                self._pending_args = None
                self._pending_kwargs = None

        self._timer = threading.Timer(delay, _fire)
        self._timer.daemon = True
        self._timer.start()

    def cancel(self) -> None:
        """Cancel any pending trailing edge call."""
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
        self._pending_args = None
        self._pending_kwargs = None

    def flush(self) -> Any:
        """Immediately execute any pending trailing edge call."""
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
        if self._pending_args is not None:
            self._last_call_time = time.monotonic()
            self._result = self._fn(*self._pending_args, **(self._pending_kwargs or {}))
            self._pending_args = None
            self._pending_kwargs = None
        return self._result

    @property
    def last_call_time(self) -> float:
        """Monotonic timestamp of the last actual invocation."""
        return self._last_call_time


def throttle(
    interval_ms: float = 1000,
    *,
    leading: bool = True,
    trailing: bool = True,
) -> Callable[[F], ThrottledFunction]:
    """Decorator to throttle a function.

    Args:
        interval_ms: Minimum time between calls in milliseconds.
        leading: Call on the leading edge.
        trailing: Call on the trailing edge.

    Usage::

        @throttle(interval_ms=5000)
        def refresh_cache():
            ...

        # Or with leading=False for trailing-only:
        @throttle(interval_ms=1000, leading=False)
        def log_progress(pct):
            print(f"{pct}%")
    """

    def decorator(fn: F) -> ThrottledFunction:
        return ThrottledFunction(fn, interval_ms, leading=leading, trailing=trailing)

    return decorator


# ---------------------------------------------------------------------------
# Cooldown-based throttle (marker file pattern)
# ---------------------------------------------------------------------------


class CooldownThrottle:
    """Time-based cooldown that suppresses execution for a fixed window.

    Ported from Claude Code's marker-file throttle pattern used in
    `cleanupOldVersionsThrottled()` and autoDream scan throttle.

    Args:
        cooldown_ms: Minimum time between allowed executions.
        name: Label for logging/debugging.
    """

    def __init__(self, cooldown_ms: float = 86_400_000, *, name: str = "") -> None:
        self._cooldown_s = cooldown_ms / 1000.0
        self._name = name
        self._last_execution: float = 0.0

    def should_run(self) -> bool:
        """Return True if the cooldown has elapsed."""
        if self._last_execution == 0.0:
            return True
        return (time.monotonic() - self._last_execution) >= self._cooldown_s

    def mark_executed(self) -> None:
        """Record that execution just happened."""
        self._last_execution = time.monotonic()

    def time_until_next_ms(self) -> float:
        """Milliseconds until the next allowed execution."""
        if self._last_execution == 0.0:
            return 0.0
        elapsed = time.monotonic() - self._last_execution
        remaining = self._cooldown_s - elapsed
        return max(0.0, remaining * 1000)

    def reset(self) -> None:
        """Reset the cooldown, allowing immediate execution."""
        self._last_execution = 0.0
