# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Time-based microcompact configuration — ported from timeBasedMCConfig.ts.

Triggers content-clearing microcompact when the gap since the last
main-loop assistant message exceeds a threshold.  The server-side
prompt cache has almost certainly expired, so clearing old tool results
before the request shrinks what gets rewritten.

Main thread only — subagents have short lifetimes where gap-based
eviction doesn't apply.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class TimeBasedMCConfig:
    """Configuration for time-based microcompaction."""

    enabled: bool = False
    gap_threshold_minutes: int = 60
    keep_recent: int = 5


_DEFAULTS = TimeBasedMCConfig()


def get_time_based_mc_config() -> TimeBasedMCConfig:
    """Resolve time-based MC config from env vars with safe defaults."""
    env_enabled = os.environ.get("COMPACT_TIME_BASED_MC_ENABLED", "")
    env_gap = os.environ.get("COMPACT_TIME_BASED_MC_GAP_MINUTES", "")
    env_keep = os.environ.get("COMPACT_TIME_BASED_MC_KEEP_RECENT", "")

    enabled = env_enabled.lower() in ("1", "true") if env_enabled else _DEFAULTS.enabled

    try:
        gap = int(env_gap) if env_gap else _DEFAULTS.gap_threshold_minutes
    except ValueError:
        gap = _DEFAULTS.gap_threshold_minutes

    try:
        keep = int(env_keep) if env_keep else _DEFAULTS.keep_recent
    except ValueError:
        keep = _DEFAULTS.keep_recent

    return TimeBasedMCConfig(enabled=enabled, gap_threshold_minutes=gap, keep_recent=keep)
