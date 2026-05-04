# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Compact warning suppression state — ported from compactWarningState.ts.

Tracks whether the "context left until autocompact" warning should be
suppressed.  We suppress immediately after successful compaction since
we don't have accurate token counts until the next API response.

The React hook (compactWarningHook.ts) is NOT ported — it's a UI
concern.  This module exposes the pure state functions that
micro_compact.py and the CLI status modules can use directly.
"""

from __future__ import annotations

import threading

# Module-level state — shared across all threads in the same process.
# This mirrors Claude's ``createStore<boolean>(false)`` pattern.
_lock = threading.Lock()
_suppressed: bool = False


def suppress_compact_warning() -> None:
    """Suppress the compact warning.  Call after successful compaction."""
    global _suppressed
    with _lock:
        _suppressed = True


def clear_compact_warning_suppression() -> None:
    """Clear the compact warning suppression.

    Called at start of new compact attempt.
    """
    global _suppressed
    with _lock:
        _suppressed = False


def get_compact_warning_suppressed() -> bool:
    """Return whether the compact warning is currently suppressed."""
    with _lock:
        return _suppressed
