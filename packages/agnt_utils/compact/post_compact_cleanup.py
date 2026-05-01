# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Post-compact cleanup — ported from postCompactCleanup.ts.

Resets caches and tracking state after compaction.  Called after both
auto-compact and manual /compact to free memory held by tracking
structures that are invalidated by compaction.

Note: We intentionally do NOT clear invoked skill content here.
Skill content must survive across multiple compactions so that
skill attachments can be re-included in subsequent compaction prompts.
"""

from __future__ import annotations

from packages.agnt_utils.compact.micro_compact import reset_microcompact_state
from packages.agnt_utils.compact.warning_state import suppress_compact_warning


def run_post_compact_cleanup(query_source: str | None = None) -> None:
    """Run cleanup of caches and tracking state after compaction.

    Args:
        query_source: The compacting query's source, so we can skip
                      resets that would clobber main-thread module-level
                      state.  Subagents (agent:*) run in the same process
                      and share module-level state.
    """
    is_main = query_source is None or query_source.startswith("repl_main_thread") or query_source == "sdk"

    # Always reset microcompact tracking
    reset_microcompact_state()

    # Suppress the compact warning until next API response gives real counts
    suppress_compact_warning()

    # Main-thread-only resets would go here in a full integration:
    # - getUserContext cache clear
    # - resetGetMemoryFilesCache
    # - context collapse reset
    # For the utility library, we emit a hook that callers can subscribe to.
    if is_main:
        for hook in _post_compact_hooks:
            try:
                hook(query_source)
            except Exception:
                pass  # Hooks must not break compaction flow


# ── Hook registration ─────────────────────────────────────────────────────────
# Callers can register cleanup hooks for their own caches.

_post_compact_hooks: list = []


def register_post_compact_hook(fn) -> None:  # noqa: ANN001
    """Register a function to be called after compaction cleanup.

    The function receives ``query_source: str | None`` as its argument.
    """
    _post_compact_hooks.append(fn)


def clear_post_compact_hooks() -> None:
    """Remove all registered post-compact hooks (for testing)."""
    _post_compact_hooks.clear()
