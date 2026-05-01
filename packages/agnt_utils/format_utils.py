# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""format_utils — Human-readable display formatters.

Ported from Claude Code v2.1.91 `utils/format.ts`.
Formatters for file sizes, durations, numbers, tokens, and relative times.
"""

from __future__ import annotations

import math
from datetime import datetime, UTC


def format_file_size(size_in_bytes: int) -> str:
    """Format a byte count to a human-readable string (KB, MB, GB).

    >>> format_file_size(1536)
    '1.5KB'
    """
    kb = size_in_bytes / 1024
    if kb < 1:
        return f"{size_in_bytes} bytes"
    if kb < 1024:
        formatted = f"{kb:.1f}".rstrip("0").rstrip(".")
        return f"{formatted}KB"
    mb = kb / 1024
    if mb < 1024:
        formatted = f"{mb:.1f}".rstrip("0").rstrip(".")
        return f"{formatted}MB"
    gb = mb / 1024
    formatted = f"{gb:.1f}".rstrip("0").rstrip(".")
    return f"{formatted}GB"


def format_seconds_short(ms: float) -> str:
    """Format milliseconds as seconds with 1 decimal place (e.g. 1234 → '1.2s')."""
    return f"{ms / 1000:.1f}s"


def format_duration(
    ms: float,
    *,
    hide_trailing_zeros: bool = False,
    most_significant_only: bool = False,
) -> str:
    """Format milliseconds to a human-readable duration string."""
    if ms < 60000:
        if ms == 0:
            return "0s"
        if ms < 1:
            return f"{ms / 1000:.1f}s"
        return f"{int(ms // 1000)}s"

    days = int(ms // 86400000)
    hours = int((ms % 86400000) // 3600000)
    minutes = int((ms % 3600000) // 60000)
    seconds = round((ms % 60000) / 1000)

    # Handle rounding carry-over
    if seconds == 60:
        seconds = 0
        minutes += 1
    if minutes == 60:
        minutes = 0
        hours += 1
    if hours == 24:
        hours = 0
        days += 1

    if most_significant_only:
        if days > 0:
            return f"{days}d"
        if hours > 0:
            return f"{hours}h"
        if minutes > 0:
            return f"{minutes}m"
        return f"{seconds}s"

    hide = hide_trailing_zeros
    if days > 0:
        if hide and hours == 0 and minutes == 0:
            return f"{days}d"
        if hide and minutes == 0:
            return f"{days}d {hours}h"
        return f"{days}d {hours}h {minutes}m"
    if hours > 0:
        if hide and minutes == 0 and seconds == 0:
            return f"{hours}h"
        if hide and seconds == 0:
            return f"{hours}h {minutes}m"
        return f"{hours}h {minutes}m {seconds}s"
    if minutes > 0:
        if hide and seconds == 0:
            return f"{minutes}m"
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def format_number(number: int | float) -> str:
    """Format a number with compact notation (e.g. 1321 → '1.3k')."""
    if abs(number) >= 1_000_000_000:
        return f"{number / 1_000_000_000:.1f}b"
    if abs(number) >= 1_000_000:
        return f"{number / 1_000_000:.1f}m"
    if abs(number) >= 1_000:
        return f"{number / 1_000:.1f}k"
    return str(int(number)) if number == int(number) else str(number)


def format_tokens(count: int) -> str:
    """Format a token count with compact notation, stripping '.0'."""
    return format_number(count).replace(".0", "")


_INTERVALS = [
    ("y", 31536000),
    ("mo", 2592000),
    ("w", 604800),
    ("d", 86400),
    ("h", 3600),
    ("m", 60),
    ("s", 1),
]


def format_relative_time(
    dt: datetime,
    *,
    now: datetime | None = None,
) -> str:
    """Format a datetime as a relative time string (e.g. '3h ago', 'in 2d')."""
    if now is None:
        now = datetime.now(UTC)
    # Ensure both are timezone-aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    if now.tzinfo is None:
        now = now.replace(tzinfo=UTC)

    diff_seconds = int((dt - now).total_seconds())

    for unit, interval_secs in _INTERVALS:
        if abs(diff_seconds) >= interval_secs:
            value = math.trunc(diff_seconds / interval_secs)
            if diff_seconds < 0:
                return f"{abs(value)}{unit} ago"
            return f"in {value}{unit}"

    return "0s ago" if diff_seconds <= 0 else "in 0s"


def format_relative_time_ago(
    dt: datetime,
    *,
    now: datetime | None = None,
) -> str:
    """Format a past datetime as a relative time string (always 'ago')."""
    if now is None:
        now = datetime.now(UTC)
    return format_relative_time(dt, now=now)
