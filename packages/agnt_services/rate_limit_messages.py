# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Rate limit message generation — pure logic for rate limit UI strings.

Ported from src/services/rateLimitMessages.ts (Claude Code v2.1.91).

Generates user-facing rate limit messages based on limit state.
Decoupled from claude.ai auth — subscription info is passed in via
a ``RateLimitContext`` dataclass.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import StrEnum
from typing import Literal
from datetime import UTC

logger = logging.getLogger(__name__)


class RateLimitType(StrEnum):
    """Types of rate limits."""

    FIVE_HOUR = "five_hour"
    SEVEN_DAY = "seven_day"
    SEVEN_DAY_OPUS = "seven_day_opus"
    SEVEN_DAY_SONNET = "seven_day_sonnet"
    OVERAGE = "overage"


class LimitStatus(StrEnum):
    """Rate limit status from API headers."""

    ALLOWED = "allowed"
    ALLOWED_WARNING = "allowed_warning"
    REJECTED = "rejected"


RATE_LIMIT_ERROR_PREFIXES: tuple[str, ...] = (
    "You've hit your",
    "You've used",
    "You're now using extra usage",
    "You're close to",
    "You're out of extra usage",
)


def is_rate_limit_error_message(text: str) -> bool:
    """Check if a message is a rate limit error."""
    return any(text.startswith(p) for p in RATE_LIMIT_ERROR_PREFIXES)


@dataclass(frozen=True, slots=True)
class RateLimitContext:
    """Encapsulates all state needed for rate limit message generation."""

    status: LimitStatus = LimitStatus.ALLOWED
    rate_limit_type: RateLimitType | None = None
    resets_at: int | None = None  # Unix timestamp
    utilization: float | None = None  # 0.0 - 1.0
    is_using_overage: bool = False
    overage_status: LimitStatus | None = None
    overage_resets_at: int | None = None
    overage_disabled_reason: str | None = None
    # Subscription info (passed in, not fetched)
    subscription_type: str = "free"  # free, pro, max, team, enterprise
    has_extra_usage_enabled: bool = False
    has_billing_access: bool = False
    is_overage_provisioning_allowed: bool = True


@dataclass(frozen=True, slots=True)
class RateLimitMessage:
    """A rate limit message with severity."""

    message: str
    severity: Literal["error", "warning"]


WARNING_THRESHOLD = 0.7


def get_rate_limit_message(
    ctx: RateLimitContext,
    model: str = "",
) -> RateLimitMessage | None:
    """Get the appropriate rate limit message based on limit state.

    Returns None if no message should be shown.
    """
    # Overage scenarios first
    if ctx.is_using_overage:
        if ctx.overage_status == LimitStatus.ALLOWED_WARNING:
            return RateLimitMessage(
                message="You're close to your extra usage spending limit",
                severity="warning",
            )
        return None

    # ERROR: limits rejected
    if ctx.status == LimitStatus.REJECTED:
        return RateLimitMessage(message=_limit_reached_text(ctx, model), severity="error")

    # WARNING: approaching limits
    if ctx.status == LimitStatus.ALLOWED_WARNING:
        if ctx.utilization is not None and ctx.utilization < WARNING_THRESHOLD:
            return None

        # Don't warn non-billing team/enterprise with overages enabled
        is_team_ent = ctx.subscription_type in ("team", "enterprise")
        if is_team_ent and ctx.has_extra_usage_enabled and not ctx.has_billing_access:
            return None

        text = _early_warning_text(ctx)
        if text:
            return RateLimitMessage(message=text, severity="warning")

    return None


def get_rate_limit_error_message(ctx: RateLimitContext, model: str = "") -> str | None:
    """Get error message only (not warnings)."""
    msg = get_rate_limit_message(ctx, model)
    if msg and msg.severity == "error":
        return msg.message
    return None


def get_rate_limit_warning(ctx: RateLimitContext, model: str = "") -> str | None:
    """Get warning message only (not errors)."""
    msg = get_rate_limit_message(ctx, model)
    if msg and msg.severity == "warning":
        return msg.message
    return None


def format_reset_time(resets_at: int, relative: bool = True) -> str:
    """Format a reset timestamp for display."""
    import time
    from datetime import datetime

    now = time.time()
    dt = datetime.fromtimestamp(resets_at, tz=UTC)

    if not relative:
        return dt.strftime("%Y-%m-%d %H:%M UTC")

    diff = resets_at - now
    if diff <= 0:
        return "now"
    if diff < 3600:
        mins = int(diff / 60)
        return f"in {mins}m" if mins > 0 else "in <1m"
    if diff < 86400:
        hours = int(diff / 3600)
        return f"in {hours}h"
    days = int(diff / 86400)
    return f"in {days}d"


def get_using_overage_text(ctx: RateLimitContext) -> str:
    """Get notification text for overage mode transitions."""
    reset_time = format_reset_time(ctx.resets_at) if ctx.resets_at else ""

    limit_name = ""
    if ctx.rate_limit_type == RateLimitType.FIVE_HOUR:
        limit_name = "session limit"
    elif ctx.rate_limit_type == RateLimitType.SEVEN_DAY:
        limit_name = "weekly limit"
    elif ctx.rate_limit_type == RateLimitType.SEVEN_DAY_OPUS:
        limit_name = "Opus limit"
    elif ctx.rate_limit_type == RateLimitType.SEVEN_DAY_SONNET:
        is_pro_ent = ctx.subscription_type in ("pro", "enterprise")
        limit_name = "weekly limit" if is_pro_ent else "Sonnet limit"

    if not limit_name:
        return "Now using extra usage"

    reset_msg = f" · Your {limit_name} resets {reset_time}" if reset_time else ""
    return f"You're now using extra usage{reset_msg}"


# -- internal helpers ---------------------------------------------------


def _limit_reached_text(ctx: RateLimitContext, model: str) -> str:
    """Generate the 'limit reached' error text."""
    reset_time = format_reset_time(ctx.resets_at) if ctx.resets_at else None
    overage_reset = format_reset_time(ctx.overage_resets_at) if ctx.overage_resets_at else None
    reset_msg = f" · resets {reset_time}" if reset_time else ""

    # Both subscription and overage exhausted
    if ctx.overage_status == LimitStatus.REJECTED:
        overage_reset_msg = ""
        if ctx.resets_at and ctx.overage_resets_at:
            if ctx.resets_at < ctx.overage_resets_at:
                overage_reset_msg = f" · resets {reset_time}"
            else:
                overage_reset_msg = f" · resets {overage_reset}"
        elif reset_time:
            overage_reset_msg = f" · resets {reset_time}"
        elif overage_reset:
            overage_reset_msg = f" · resets {overage_reset}"

        if ctx.overage_disabled_reason == "out_of_credits":
            return f"You're out of extra usage{overage_reset_msg}"
        return f"You've hit your limit{overage_reset_msg}"

    if ctx.rate_limit_type == RateLimitType.SEVEN_DAY_SONNET:
        is_pro_ent = ctx.subscription_type in ("pro", "enterprise")
        limit = "weekly limit" if is_pro_ent else "Sonnet limit"
        return f"You've hit your {limit}{reset_msg}"

    if ctx.rate_limit_type == RateLimitType.SEVEN_DAY_OPUS:
        return f"You've hit your Opus limit{reset_msg}"

    if ctx.rate_limit_type == RateLimitType.SEVEN_DAY:
        return f"You've hit your weekly limit{reset_msg}"

    if ctx.rate_limit_type == RateLimitType.FIVE_HOUR:
        return f"You've hit your session limit{reset_msg}"

    return f"You've hit your usage limit{reset_msg}"


def _early_warning_text(ctx: RateLimitContext) -> str | None:
    """Generate early warning text."""
    limit_name_map = {
        RateLimitType.SEVEN_DAY: "weekly limit",
        RateLimitType.FIVE_HOUR: "session limit",
        RateLimitType.SEVEN_DAY_OPUS: "Opus limit",
        RateLimitType.SEVEN_DAY_SONNET: "Sonnet limit",
        RateLimitType.OVERAGE: "extra usage",
    }

    if ctx.rate_limit_type is None:
        return None

    limit_name = limit_name_map.get(ctx.rate_limit_type)
    if limit_name is None:
        return None

    used = int(ctx.utilization * 100) if ctx.utilization else None
    reset_time = format_reset_time(ctx.resets_at) if ctx.resets_at else None

    if used and reset_time:
        return f"You've used {used}% of your {limit_name} · resets {reset_time}"
    if used:
        return f"You've used {used}% of your {limit_name}"

    if ctx.rate_limit_type == RateLimitType.OVERAGE:
        limit_name += " limit"

    if reset_time:
        return f"Approaching {limit_name} · resets {reset_time}"
    return f"Approaching {limit_name}"
