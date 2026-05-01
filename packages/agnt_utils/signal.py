# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""signal — Tiny listener-set primitive for pure event signals.

Ported from Claude Code v2.1.91 `utils/signal.ts`.

Collapses the ~8-line ``listeners = set(); subscribe(); notify()``
boilerplate that was duplicated ~15x across the codebase into a
one-liner factory.

Distinct from a store (AppState, createStore) — there is no snapshot,
no get_state. Use this when subscribers only need to know "something
happened", optionally with event args, not "what is the current value".

Usage::

    changed = create_signal()
    unsub = changed.subscribe(lambda: print("changed!"))
    changed.emit()    # prints "changed!"
    unsub()           # unsubscribes
    changed.emit()    # no output

With typed args::

    on_error = create_signal()
    on_error.subscribe(lambda msg, code: print(f"Error {code}: {msg}"))
    on_error.emit("not found", 404)
"""

from __future__ import annotations

from typing import Any
from collections.abc import Callable


class Signal:
    """A synchronous event signal with subscribe/emit/clear semantics.

    Listeners are stored in a ``set`` for O(1) add/remove. Iteration
    order is insertion order (Python 3.7+).
    """

    __slots__ = ("_listeners",)

    def __init__(self) -> None:
        self._listeners: set[Callable[..., Any]] = set()

    def subscribe(self, listener: Callable[..., Any]) -> Callable[[], None]:
        """Add a listener. Returns an unsubscribe callable."""
        self._listeners.add(listener)

        def _unsubscribe() -> None:
            self._listeners.discard(listener)

        return _unsubscribe

    def emit(self, *args: Any, **kwargs: Any) -> None:
        """Call all subscribed listeners with the given arguments."""
        for listener in list(self._listeners):  # snapshot to allow unsub during emit
            listener(*args, **kwargs)

    def clear(self) -> None:
        """Remove all listeners. Useful in dispose/reset paths."""
        self._listeners.clear()

    @property
    def listener_count(self) -> int:
        """Return the number of active listeners."""
        return len(self._listeners)

    def __repr__(self) -> str:
        return f"Signal(listeners={self.listener_count})"


def create_signal() -> Signal:
    """Factory function that mirrors the upstream ``createSignal()`` API."""
    return Signal()
