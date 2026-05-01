# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Effort level management — ported from utils/effort.ts + components/EffortIndicator.ts.

Manages the 4-tier effort system that controls how much reasoning compute
the model applies to a task. Sovereign implementation strips Anthropic's
ant-gates, GrowthBook feature flags, and subscription tier checks.

Effort levels:
    low     ○  Quick, straightforward implementation
    medium  ◐  Balanced approach with standard testing
    high    ●  Comprehensive implementation (API default)
    max     ◉  Maximum reasoning depth

Precedence chain:
    env EFFORT_LEVEL → explicit setting → model default → 'high'
"""

from __future__ import annotations

import os
from typing import Literal, Union

# ── Types ─────────────────────────────────────────────────────────────────────

EffortLevel = Literal["low", "medium", "high", "max"]
EffortValue = Union[EffortLevel, int]

EFFORT_LEVELS: tuple[EffortLevel, ...] = ("low", "medium", "high", "max")

# ── Symbols (from constants/figures.ts) ───────────────────────────────────────

EFFORT_SYMBOLS: dict[EffortLevel, str] = {
    "low": "○",  # U+25CB white circle
    "medium": "◐",  # U+25D0 circle with left half black
    "high": "●",  # U+25CF black circle
    "max": "◉",  # U+25C9 fisheye
}

# ── Descriptions ──────────────────────────────────────────────────────────────

EFFORT_DESCRIPTIONS: dict[EffortLevel, str] = {
    "low": "Quick, straightforward implementation with minimal overhead",
    "medium": "Balanced approach with standard implementation and testing",
    "high": "Comprehensive implementation with extensive testing and documentation",
    "max": "Maximum capability with deepest reasoning",
}

# ── Model defaults ────────────────────────────────────────────────────────────
# Maps model name substrings (lowercased) to their default effort level.
# Models not listed default to None (which resolves to 'high' in the API).

_MODEL_DEFAULTS: dict[str, EffortLevel] = {
    "opus": "medium",  # Opus defaults to medium to balance speed/intelligence
    "flash": "high",  # Flash models default to high
    "lite": "high",  # Lite models default to high
}

# Models that support the 'max' effort level.
_MAX_EFFORT_MODELS: frozenset[str] = frozenset(
    {
        "opus",
        "gemini-3.1-pro",
    }
)


# ── Validation ────────────────────────────────────────────────────────────────


def is_effort_level(value: str) -> bool:
    """Check if a string is a valid effort level."""
    return value in EFFORT_LEVELS


def is_valid_numeric_effort(value: int) -> bool:
    """Validate numeric effort values (must be integer)."""
    return isinstance(value, int)


def parse_effort_value(value: str | int | None) -> EffortValue | None:
    """Parse a raw value into a validated EffortValue.

    Accepts string effort levels ('low', 'medium', 'high', 'max'),
    integer values, or None. Returns None for invalid/empty input.
    """
    if value is None or value == "":
        return None

    if isinstance(value, int) and is_valid_numeric_effort(value):
        return value

    if isinstance(value, str):
        lower = value.lower()
        if is_effort_level(lower):
            return lower  # type: ignore[return-value]
        try:
            numeric = int(lower)
            if is_valid_numeric_effort(numeric):
                return numeric
        except ValueError:
            pass

    return None


def to_persistable_effort(value: EffortValue | None) -> EffortLevel | None:
    """Convert an effort value to a persistable level.

    Numeric values are session-scoped and not persisted.
    Returns None for non-persistable values.
    """
    if value in ("low", "medium", "high", "max"):
        return value  # type: ignore[return-value]
    return None


# ── Model support ─────────────────────────────────────────────────────────────


def model_supports_effort(model: str) -> bool:
    """Check if a model supports the effort parameter.

    Sovereign implementation: all known models support effort.
    """
    if os.environ.get("AGNT_ALWAYS_ENABLE_EFFORT"):
        return True
    # Default to True — effort is a standard parameter
    return True


def model_supports_max_effort(model: str) -> bool:
    """Check if a model supports the 'max' effort level."""
    m = model.lower()
    return any(pattern in m for pattern in _MAX_EFFORT_MODELS)


# ── Effort resolution ────────────────────────────────────────────────────────


def convert_effort_value_to_level(value: EffortValue) -> EffortLevel:
    """Convert any EffortValue (string or numeric) to an EffortLevel.

    Numeric mapping:
        ≤50  → low
        ≤85  → medium
        ≤100 → high
        >100 → max
    """
    if isinstance(value, str):
        return value if is_effort_level(value) else "high"

    if isinstance(value, int):
        if value <= 50:
            return "low"
        if value <= 85:
            return "medium"
        if value <= 100:
            return "high"
        return "max"

    return "high"


def get_default_effort_for_model(model: str) -> EffortValue | None:
    """Get the default effort level for a model.

    Walks the _MODEL_DEFAULTS table looking for substring matches.
    Returns None if no default is configured (API uses 'high').
    """
    m = model.lower()
    for pattern, level in _MODEL_DEFAULTS.items():
        if pattern in m:
            return level
    return None


def get_effort_env_override() -> EffortValue | None:
    """Read effort override from environment variable.

    Returns None if not set. Supports 'unset'/'auto' to explicitly
    clear effort (returns the sentinel None).
    """
    env_val = os.environ.get("AGNT_EFFORT_LEVEL", "")
    if not env_val:
        return None
    lower = env_val.lower()
    if lower in ("unset", "auto"):
        return None  # Explicit clear
    return parse_effort_value(env_val)


def resolve_applied_effort(
    model: str,
    app_state_effort: EffortValue | None = None,
) -> EffortValue | None:
    """Resolve the effort value that will actually be sent to the API.

    Precedence chain:
        env AGNT_EFFORT_LEVEL → app_state_effort → model default

    Returns None when no effort parameter should be sent.
    """
    env_override = get_effort_env_override()
    resolved = env_override or app_state_effort or get_default_effort_for_model(model)

    # API rejects 'max' on models that don't support it → downgrade to 'high'
    if resolved == "max" and not model_supports_max_effort(model):
        return "high"

    return resolved


def get_displayed_effort_level(
    model: str,
    app_state_effort: EffortValue | None = None,
) -> EffortLevel:
    """Resolve the effort level to show the user.

    Wraps resolve_applied_effort with 'high' fallback
    (what the API uses when no effort param is sent).
    """
    resolved = resolve_applied_effort(model, app_state_effort) or "high"
    return convert_effort_value_to_level(resolved)


# ── Display helpers ───────────────────────────────────────────────────────────


def effort_level_to_symbol(level: EffortLevel) -> str:
    """Map an effort level to its Unicode indicator symbol."""
    return EFFORT_SYMBOLS.get(level, EFFORT_SYMBOLS["high"])


def get_effort_suffix(
    model: str,
    effort_value: EffortValue | None = None,
) -> str:
    """Build the ' with {level} effort' suffix for display.

    Returns empty string if no explicit effort value is set.
    """
    if effort_value is None:
        return ""
    resolved = resolve_applied_effort(model, effort_value)
    if resolved is None:
        return ""
    return f" with {convert_effort_value_to_level(resolved)} effort"


def get_effort_notification_text(
    effort_value: EffortValue | None,
    model: str,
) -> str | None:
    """Build the effort-changed notification text.

    Returns None if the model doesn't support effort.
    Example: '◐ medium · /effort'
    """
    if not model_supports_effort(model):
        return None
    level = get_displayed_effort_level(model, effort_value)
    return f"{effort_level_to_symbol(level)} {level} · /effort"


def get_effort_description(value: EffortValue) -> str:
    """Get a human-readable description for an effort value."""
    level = convert_effort_value_to_level(value)
    return EFFORT_DESCRIPTIONS.get(level, EFFORT_DESCRIPTIONS["medium"])
