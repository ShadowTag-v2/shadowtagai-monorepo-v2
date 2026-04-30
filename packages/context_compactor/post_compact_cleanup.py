# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Post-compaction cleanup — centralized cache and state invalidation.

Ported from: compact/postCompactCleanup.ts
Reference: AGNT STATE B Spec P1.3

Call after both auto-compact and manual /compact to free memory held
by tracking structures that are invalidated by compaction.

Design decisions (from upstream):
  - Skill content is NOT cleared — invoked_skills must survive across
    compactions so the full skill text can be re-injected.
  - querySource threading prevents subagent compactions from corrupting
    main-thread module-level state (context-collapse store, memory caches).
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Main-thread query sources — only these should reset shared state
# ---------------------------------------------------------------------------
_MAIN_THREAD_SOURCES = frozenset(
    {
        "repl_main_thread",
        "main",
        "sdk",
    }
)


def is_main_thread_compact(query_source: str | None) -> bool:
    """Check if the compaction is running on the main thread.

    Subagents (agent:*) share module-level state with the main thread.
    Only reset shared caches for main-thread compacts to prevent
    corrupting the main thread's state.
    """
    if query_source is None:
        return True  # undefined is safe for main-thread-only callers
    return query_source in _MAIN_THREAD_SOURCES


class PostCompactCleanupState:
    """Tracks state that needs invalidation after compaction.

    Each cleanup target is registered as a callback. This centralizes
    the cleanup logic so all compaction paths (auto, manual, session
    memory, reactive) share the same teardown sequence.
    """

    def __init__(self) -> None:
        self._cleanup_hooks: list[tuple[str, Any]] = []
        self._main_thread_hooks: list[tuple[str, Any]] = []

    def register_hook(
        self,
        name: str,
        callback: Any,
        *,
        main_thread_only: bool = False,
    ) -> None:
        """Register a cleanup callback.

        Args:
            name: Human-readable name for logging.
            callback: Callable to invoke during cleanup.
            main_thread_only: If True, only runs for main-thread compacts.
        """
        if main_thread_only:
            self._main_thread_hooks.append((name, callback))
        else:
            self._cleanup_hooks.append((name, callback))

    def run(self, query_source: str | None = None) -> dict[str, bool]:
        """Execute all registered cleanup hooks.

        Args:
            query_source: The compacting query's source identifier.

        Returns:
            Dict mapping hook name to success/failure status.
        """
        results: dict[str, bool] = {}
        is_main = is_main_thread_compact(query_source)

        # Always-run hooks
        for name, callback in self._cleanup_hooks:
            try:
                callback()
                results[name] = True
            except Exception:
                logger.warning("Cleanup hook '%s' failed", name, exc_info=True)
                results[name] = False

        # Main-thread-only hooks
        if is_main:
            for name, callback in self._main_thread_hooks:
                try:
                    callback()
                    results[name] = True
                except Exception:
                    logger.warning(
                        "Main-thread cleanup hook '%s' failed",
                        name,
                        exc_info=True,
                    )
                    results[name] = False

        logger.info(
            "Post-compact cleanup: %d/%d hooks succeeded (main_thread=%s)",
            sum(results.values()),
            len(results),
            is_main,
        )
        return results


# Module-level singleton
_cleanup_state = PostCompactCleanupState()


def register_cleanup_hook(
    name: str,
    callback: Any,
    *,
    main_thread_only: bool = False,
) -> None:
    """Register a post-compaction cleanup hook."""
    _cleanup_state.register_hook(name, callback, main_thread_only=main_thread_only)


def run_post_compact_cleanup(query_source: str | None = None) -> dict[str, bool]:
    """Run all post-compaction cleanup hooks.

    Call this after both auto-compact and manual /compact.
    """
    return _cleanup_state.run(query_source)
