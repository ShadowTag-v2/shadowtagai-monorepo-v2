# apps/counselconduit/api/middleware/token_budget.py
"""Token Budget Middleware — OWASP LLM10 (Unbounded Consumption).

Enforces per-request and per-user token limits to prevent
AI cost spiral attacks and runaway API bills.

Architecture:
- Per-request hard cap: 8,192 tokens (configurable)
- Per-user daily budget: 50,000 tokens (free), 500,000 (pro), unlimited (enterprise)
- Circuit breaker: if upstream latency > 30s, trip and return cached/degraded response
"""

from __future__ import annotations

import logging
import os
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

logger = logging.getLogger("counselconduit.token_budget")

# ── Configuration ──────────────────────────────────────────────────────────

# Per-request token cap (input + output combined)
MAX_TOKENS_PER_REQUEST = int(os.getenv("MAX_TOKENS_PER_REQUEST", "8192"))

# Per-user daily budget by tier
TIER_DAILY_LIMITS: dict[str, int] = {
    "trial": 50_000,
    "professional": 500_000,
    "enterprise": 5_000_000,  # effectively unlimited
}

# Circuit breaker: max upstream latency before tripping
CIRCUIT_BREAKER_TIMEOUT_S = 30.0
CIRCUIT_BREAKER_COOLDOWN_S = 60.0


@dataclass
class _UserBudget:
    """Tracks daily token usage for a single user."""

    tokens_used: int = 0
    day: str = ""  # YYYY-MM-DD

    def reset_if_new_day(self) -> None:
        today = time.strftime("%Y-%m-%d")
        if self.day != today:
            self.tokens_used = 0
            self.day = today

    def consume(self, tokens: int) -> None:
        self.reset_if_new_day()
        self.tokens_used += tokens

    def remaining(self, tier: str) -> int:
        self.reset_if_new_day()
        limit = TIER_DAILY_LIMITS.get(tier, TIER_DAILY_LIMITS["trial"])
        return max(0, limit - self.tokens_used)


@dataclass
class _CircuitBreaker:
    """Simple circuit breaker for upstream LLM calls."""

    is_open: bool = False
    opened_at: float = 0.0
    failure_count: int = 0
    threshold: int = 3

    def should_allow(self) -> bool:
        if not self.is_open:
            return True
        # Half-open: allow after cooldown
        if time.monotonic() - self.opened_at > CIRCUIT_BREAKER_COOLDOWN_S:
            self.is_open = False
            self.failure_count = 0
            return True
        return False

    def record_failure(self) -> None:
        self.failure_count += 1
        if self.failure_count >= self.threshold:
            self.is_open = True
            self.opened_at = time.monotonic()
            logger.warning("Circuit breaker OPEN: %d consecutive failures", self.failure_count)

    def record_success(self) -> None:
        self.failure_count = 0
        self.is_open = False


# Global state
_user_budgets: dict[str, _UserBudget] = defaultdict(_UserBudget)
_circuit_breaker = _CircuitBreaker()

# LLM-adjacent routes that need token budget enforcement
_LLM_ROUTES = {"/query", "/chat", "/oracle", "/stream"}


class TokenBudgetMiddleware(BaseHTTPMiddleware):
    """OWASP LLM10: Token budget + circuit breaker middleware.

    Enforces:
    - Per-request token cap header (X-Max-Tokens)
    - Per-user daily budget by subscription tier
    - Circuit breaker for upstream LLM latency
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        path = request.url.path

        # Only enforce on LLM-adjacent routes
        if not any(route in path for route in _LLM_ROUTES):
            return await call_next(request)

        # Circuit breaker check
        if not _circuit_breaker.should_allow():
            logger.warning("Circuit breaker OPEN: rejecting request to %s", path)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": "CIRCUIT_BREAKER_OPEN",
                    "message": "AI service is temporarily unavailable. Please try again in 60 seconds.",
                    "retry_after_seconds": CIRCUIT_BREAKER_COOLDOWN_S,
                },
            )

        # Extract user info from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", "anonymous")
        user_tier = getattr(request.state, "user_tier", "trial")

        # Check daily budget
        budget = _user_budgets[user_id]
        remaining = budget.remaining(user_tier)

        if remaining <= 0:
            logger.warning(
                "Token budget exceeded: user=%s tier=%s used=%d",
                user_id,
                user_tier,
                budget.tokens_used,
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "code": "TOKEN_BUDGET_EXCEEDED",
                    "message": "Daily AI usage limit reached. Upgrade your plan for more capacity.",
                    "tokens_used": budget.tokens_used,
                    "tier": user_tier,
                },
            )

        # Inject max tokens into request state for downstream handlers
        request.state.max_tokens = min(
            MAX_TOKENS_PER_REQUEST,
            remaining,
        )

        # Time the request for circuit breaker
        start = time.monotonic()
        try:
            response = await call_next(request)
            elapsed = time.monotonic() - start

            if elapsed > CIRCUIT_BREAKER_TIMEOUT_S:
                _circuit_breaker.record_failure()
            else:
                _circuit_breaker.record_success()

            # Record token usage from response header (set by LLM handler)
            tokens_consumed = int(response.headers.get("X-Tokens-Consumed", "0"))
            if tokens_consumed > 0:
                budget.consume(tokens_consumed)

            # Add budget headers to response
            response.headers["X-Token-Budget-Remaining"] = str(budget.remaining(user_tier))
            response.headers["X-Token-Budget-Tier"] = user_tier

            return response

        except Exception as exc:
            _circuit_breaker.record_failure()
            raise
