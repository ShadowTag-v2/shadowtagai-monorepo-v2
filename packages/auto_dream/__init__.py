"""AutoDream — Background memory consolidation.

Ported from Claude Code's ``autoDream.ts`` — fires a 4-phase memory
consolidation prompt as a background task when time-gate passes AND
enough sessions have accumulated since the last consolidation.

Gate order (cheapest first):
    1. **Time**: hours since last consolidation >= min_hours (one stat)
    2. **Sessions**: transcript count with mtime > last_consolidated >= min_sessions
    3. **Lock**: no other process mid-consolidation

Phases:
    1. **Orient** — ``ls`` the memory directory, read the entrypoint index
    2. **Gather** — Grep session transcripts for recent signal
    3. **Consolidate** — Write or update memory files
    4. **Prune** — Update the index, remove stale entries
"""

from packages.auto_dream.consolidation import (
    AutoDreamConfig,
    AutoDreamResult,
    ConsolidationLock,
    build_consolidation_prompt,
    check_dream_gates,
    record_consolidation,
)

__all__ = [
    "AutoDreamConfig",
    "AutoDreamResult",
    "ConsolidationLock",
    "build_consolidation_prompt",
    "check_dream_gates",
    "record_consolidation",
]
