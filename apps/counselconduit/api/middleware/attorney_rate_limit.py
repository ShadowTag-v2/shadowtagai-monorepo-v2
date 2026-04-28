# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# apps/counselconduit/api/middleware/attorney_rate_limit.py
"""Per-attorney rate limiting for Vent Mode and Oracle Studio.

Applies a sliding-window rate limit keyed by attorney_id (not IP).
This prevents a single attorney from exhausting the shared LLM budget.

Limits:
- Vent Mode: 30 messages/hour per attorney
- Oracle Studio: 10 sessions/hour per attorney
- Magic Links: 20 creates/hour per attorney
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import Any

logger = logging.getLogger("counselconduit.attorney_rate_limit")

# In-memory sliding window (replace with Redis in production at scale)
_windows: dict[str, list[float]] = defaultdict(list)

# Limits per route prefix
_LIMITS: dict[str, tuple[int, int]] = {
    "/vent/message": (30, 3600),  # 30 per hour
    "/vent/start": (10, 3600),  # 10 per hour
    "/enclave/v1/query": (10, 3600),  # 10 per hour
    "/onboarding/create-matter": (20, 3600),  # 20 per hour
}

DEFAULT_LIMIT = (60, 3600)  # 60 per hour default


def check_attorney_rate_limit(
    attorney_id: str,
    route: str,
) -> dict[str, Any]:
    """Check if an attorney has exceeded their rate limit.

    Returns {"allowed": bool, "remaining": int, "reset_in": int}.
    """
    # Find the matching limit
    limit, window = DEFAULT_LIMIT
    for prefix, (lim, win) in _LIMITS.items():
        if route.startswith(prefix):
            limit, window = lim, win
            break

    key = f"{attorney_id}:{route}"
    now = time.time()

    # Clean expired entries
    _windows[key] = [t for t in _windows[key] if now - t < window]

    current = len(_windows[key])

    if current >= limit:
        oldest = min(_windows[key]) if _windows[key] else now
        reset_in = int(window - (now - oldest))
        logger.warning(
            "Rate limit exceeded: attorney=%s route=%s count=%d limit=%d",
            attorney_id,
            route,
            current,
            limit,
        )
        return {
            "allowed": False,
            "remaining": 0,
            "reset_in": max(reset_in, 0),
            "limit": limit,
        }

    # Record this request
    _windows[key].append(now)

    return {
        "allowed": True,
        "remaining": limit - current - 1,
        "reset_in": window,
        "limit": limit,
    }
