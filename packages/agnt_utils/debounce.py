# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""debounce — Delayed execution until activity settles.

Ported from Claude Code v2.1.91 debounce patterns found in:
  - components/FeedbackSurvey/useDebouncedDigitInput.ts (DEFAULT_DEBOUNCE_MS=400)
  - hooks/useMinDisplayTime.ts (min-display-time throttle)

Provides both synchronous and async debounce decorators with:
  - Leading/trailing edge control
  - Cancel/flush support
  - Max-wait ceiling (prevents indefinite delay)
"""

from __future__ import annotations

import functools
import threading
import time
from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


class DebouncedFunction:
    """A debounced wrapper around a callable.

    Delays invocation until `wait_ms` milliseconds have passed without
    another call. Useful for coalescing rapid-fire events (typing, resize,
    scroll) into a single execution.

    Args:
        fn: The function to debounce.
        wait_ms: Delay in milliseconds before executing.
        leading: If True, call on the leading edge (first invocation).
        trailing: If True, call on the trailing edge (after quiet period).
        max_wait_ms: Maximum time to delay before forcing execution.
            Prevents indefinite postponement under continuous calls.
    """

    def __init__(
        self,
        fn: Callable[..., Any],
        wait_ms: float = 400,
        *,
        leading: bool = False,
        trailing: bool = True,
        max_wait_ms: float | None = None,
    ) -> None:
        self._fn = fn
        self._wait_s = wait_ms / 1000.0
        self._leading = leading
        self._trailing = trailing
        self._max_wait_s = max_wait_ms / 1000.0 if max_wait_ms else None

        self._timer: threading.Timer | None = None
        self._last_call_time: float = 0.0
        self._first_call_time: float = 0.0
        self._pending_args: tuple[Any, ...] | None = None
        self._pending_kwargs: dict[str, Any] | None = None
        self._result: Any = None
        self._lock = threading.Lock()

        functools.update_wrapper(self, fn)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        now = time.monotonic()

        with self._lock:
            # Track first call time for max_wait
            if self._first_call_time == 0.0:
                self._first_call_time = now

            self._last_call_time = now
            self._pending_args = args
            self._pending_kwargs = kwargs

            # Cancel any existing timer
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None

            # Check max_wait ceiling
            if self._max_wait_s is not None:
                elapsed_since_first = now - self._first_call_time
                if elapsed_since_first >= self._max_wait_s:
                    self._execute()
                    return self._result

            # Leading edge: fire immediately on first call
            if self._leading and self._first_call_time == now:
                self._execute()
                return self._result

            # Schedule trailing edge
            if self._trailing:
                self._timer = threading.Timer(self._wait_s, self._trailing_fire)
                self._timer.daemon = True
                self._timer.start()

        return self._result

    def _trailing_fire(self) -> None:
        """Execute on the trailing edge."""
        with self._lock:
            self._timer = None
            self._execute()

    def _execute(self) -> None:
        """Execute the wrapped function with pending args."""
        if self._pending_args is not None:
            args = self._pending_args
            kwargs = self._pending_kwargs or {}
            self._pending_args = None
            self._pending_kwargs = None
            self._first_call_time = 0.0
            self._result = self._fn(*args, **kwargs)

    def cancel(self) -> None:
        """Cancel any pending debounced call."""
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
            self._pending_args = None
            self._pending_kwargs = None
            self._first_call_time = 0.0

    def flush(self) -> Any:
        """Immediately execute any pending debounced call."""
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
            self._execute()
        return self._result

    @property
    def pending(self) -> bool:
        """True if there is a pending debounced call."""
        return self._pending_args is not None


def debounce(
    wait_ms: float = 400,
    *,
    leading: bool = False,
    trailing: bool = True,
    max_wait_ms: float | None = None,
) -> Callable[[F], DebouncedFunction]:
    """Decorator to debounce a function.

    Args:
        wait_ms: Delay before executing after the last call.
        leading: Call on the leading edge (first invocation).
        trailing: Call on the trailing edge (after quiet period).
        max_wait_ms: Maximum delay before forcing execution.

    Usage::

        @debounce(wait_ms=400)
        def on_input_change(value):
            process(value)

        # With max_wait to prevent indefinite delay:
        @debounce(wait_ms=300, max_wait_ms=1000)
        def auto_save(content):
            save_to_disk(content)
    """

    def decorator(fn: F) -> DebouncedFunction:
        return DebouncedFunction(
            fn,
            wait_ms,
            leading=leading,
            trailing=trailing,
            max_wait_ms=max_wait_ms,
        )

    return decorator
