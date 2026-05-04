# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Mock Rate Limits — Batch 6 port from Claude Code v2.1.91.

Provides mock rate limit responses for testing and development.
Used by the VCR system to replay rate-limited API interactions.

Ported from: external_repos/claude_code_services/mockRateLimits.ts
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class RateLimitInfo:
    """Rate limit information for a specific model/tier."""

    requests_per_minute: int
    tokens_per_minute: int
    tokens_per_day: int
    input_tokens_per_minute: int | None = None
    output_tokens_per_minute: int | None = None


# Default rate limits by model tier (from CC mockRateLimits.ts)
MODEL_RATE_LIMITS: dict[str, RateLimitInfo] = {
    "claude-sonnet-4-20250514": RateLimitInfo(
        requests_per_minute=50,
        tokens_per_minute=80_000,
        tokens_per_day=1_000_000,
        input_tokens_per_minute=60_000,
        output_tokens_per_minute=16_000,
    ),
    "claude-3-5-haiku-20241022": RateLimitInfo(
        requests_per_minute=100,
        tokens_per_minute=100_000,
        tokens_per_day=5_000_000,
        input_tokens_per_minute=80_000,
        output_tokens_per_minute=32_000,
    ),
    "default": RateLimitInfo(
        requests_per_minute=50,
        tokens_per_minute=40_000,
        tokens_per_day=500_000,
    ),
}


@dataclass
class RateLimitTracker:
    """Track API rate limit consumption for local enforcement.

    Used to prevent hitting actual API rate limits by tracking
    request and token consumption per minute/day windows.
    """

    _request_timestamps: list[float] = field(default_factory=list)
    _token_counts: list[tuple[float, int]] = field(default_factory=list)
    _daily_tokens: int = 0
    _daily_reset_time: float = 0.0

    def record_request(self, token_count: int = 0) -> None:
        """Record a request with optional token count."""
        now = time.monotonic()
        self._request_timestamps.append(now)
        if token_count > 0:
            self._token_counts.append((now, token_count))
            self._daily_tokens += token_count

    def requests_in_window(self, window_seconds: float = 60.0) -> int:
        """Count requests within the time window."""
        cutoff = time.monotonic() - window_seconds
        self._request_timestamps = [t for t in self._request_timestamps if t > cutoff]
        return len(self._request_timestamps)

    def tokens_in_window(self, window_seconds: float = 60.0) -> int:
        """Count tokens consumed within the time window."""
        cutoff = time.monotonic() - window_seconds
        self._token_counts = [(t, c) for t, c in self._token_counts if t > cutoff]
        return sum(c for _, c in self._token_counts)

    def would_exceed_limit(
        self,
        model: str = "default",
        estimated_tokens: int = 0,
    ) -> bool:
        """Check if a request would exceed rate limits.

        Args:
            model: Model name for tier-specific limits.
            estimated_tokens: Estimated token consumption for the request.

        Returns:
            True if the request would exceed limits.
        """
        limits = MODEL_RATE_LIMITS.get(model, MODEL_RATE_LIMITS["default"])

        if self.requests_in_window() >= limits.requests_per_minute:
            return True

        if self.tokens_in_window() + estimated_tokens > limits.tokens_per_minute:
            return True

        return self._daily_tokens + estimated_tokens > limits.tokens_per_day

    def reset_daily(self) -> None:
        """Reset daily token counter."""
        self._daily_tokens = 0
        self._daily_reset_time = time.monotonic()
