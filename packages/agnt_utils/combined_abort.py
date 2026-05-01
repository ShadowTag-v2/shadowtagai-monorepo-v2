# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""combined_abort — Combined cancellation signal with timeout cleanup.

Ported from Claude Code v2.1.91 `utils/combinedAbortSignal.ts`.

Uses threading.Event instead of AbortSignal (JS). The key insight:
AbortSignal.timeout() timers in Bun/Node accumulate in native memory
(~2.4KB/call) until they fire. This implementation uses explicit
threading.Timer + cancel() so the timer is freed immediately on cleanup.
"""

from __future__ import annotations

import threading
from collections.abc import Callable


class CombinedAbort:
    """A combined cancellation primitive that fires when any source fires.

    Attributes:
        event: A ``threading.Event`` that is set when cancellation occurs.
        cleanup: A callable that removes listeners and clears timers.
    """

    __slots__ = ("event", "cleanup")

    def __init__(
        self,
        event: threading.Event,
        cleanup: Callable[[], None],
    ) -> None:
        self.event = event
        self.cleanup = cleanup

    @property
    def is_cancelled(self) -> bool:
        return self.event.is_set()

    def wait(self, timeout: float | None = None) -> bool:
        """Block until cancelled or timeout. Returns True if cancelled."""
        return self.event.wait(timeout=timeout)


def create_combined_abort(
    *events: threading.Event | None,
    timeout_seconds: float | None = None,
) -> CombinedAbort:
    """Create a combined abort that fires when any input event fires or timeout elapses.

    Args:
        *events: Zero or more ``threading.Event`` instances to monitor.
        timeout_seconds: Optional timeout in seconds. Uses ``threading.Timer``
            with explicit ``cancel()`` so the timer is freed on cleanup
            (avoiding the ~2.4KB/call memory leak from ``AbortSignal.timeout``).

    Returns:
        A ``CombinedAbort`` with ``.event`` (the combined Event) and
        ``.cleanup()`` (call to release resources).
    """
    combined = threading.Event()

    # Fast path: if any source is already set, return immediately
    for ev in events:
        if ev is not None and ev.is_set():
            combined.set()
            return CombinedAbort(event=combined, cleanup=lambda: None)

    timer: threading.Timer | None = None
    monitor_threads: list[threading.Thread] = []
    _stop = threading.Event()

    def _trigger() -> None:
        combined.set()
        _stop.set()

    # Set up timeout timer
    if timeout_seconds is not None:
        timer = threading.Timer(timeout_seconds, _trigger)
        timer.daemon = True
        timer.start()

    # Monitor each source event in a background thread
    for ev in events:
        if ev is None:
            continue

        def _monitor(source: threading.Event) -> None:
            while not _stop.is_set():
                if source.wait(timeout=0.05):
                    _trigger()
                    return

        t = threading.Thread(target=_monitor, args=(ev,), daemon=True)
        t.start()
        monitor_threads.append(t)

    def _cleanup() -> None:
        _stop.set()
        if timer is not None:
            timer.cancel()

    return CombinedAbort(event=combined, cleanup=_cleanup)
