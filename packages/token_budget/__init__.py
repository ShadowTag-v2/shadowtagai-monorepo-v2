# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Token Budget — Parse and manage user-specified token budget directives.

Ported from src/utils/tokenBudget.ts (Claude Code v2.1.91).

Supports three syntaxes:
  - Shorthand start: "+500k" at message start
  - Shorthand end:   "+2m" at message end
  - Verbose:         "use 1.5m tokens" anywhere

Usage:
    from token_budget import parse_token_budget, find_token_budget_positions

    budget = parse_token_budget("+500k do the thing")
    assert budget == 500_000

    positions = find_token_budget_positions("use 2m tokens please")
    # [TokenBudgetPosition(start=0, end=14)]
"""

from __future__ import annotations

import re
from dataclasses import dataclass

__all__ = [
    "TokenBudgetPosition",
    "get_budget_continuation_message",
    "find_token_budget_positions",
    "parse_token_budget",
]

# ---------------------------------------------------------------------------
# Compiled regex patterns — mirrors tokenBudget.ts exactly
# ---------------------------------------------------------------------------

# Shorthand (+500k) anchored to start/end to avoid false positives.
_SHORTHAND_START_RE = re.compile(r"^\s*\+(\d+(?:\.\d+)?)\s*(k|m|b)\b", re.IGNORECASE)

# End-anchored shorthand. The leading \s prevents mid-word matches.
_SHORTHAND_END_RE = re.compile(r"\s\+(\d+(?:\.\d+)?)\s*(k|m|b)\s*[.!?]?\s*$", re.IGNORECASE)

# Verbose form: "use 1.5m tokens" / "spend 2m tokens" anywhere.
_VERBOSE_RE = re.compile(r"\b(?:use|spend)\s+(\d+(?:\.\d+)?)\s*(k|m|b)\s*tokens?\b", re.IGNORECASE)

_MULTIPLIERS: dict[str, int] = {
    "k": 1_000,
    "m": 1_000_000,
    "b": 1_000_000_000,
}


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class TokenBudgetPosition:
    """Character-offset span of a budget directive inside user text."""

    start: int
    end: int


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def _parse_budget_match(value: str, suffix: str) -> int:
    """Convert a matched numeric string + suffix into an absolute token count."""
    return int(float(value) * _MULTIPLIERS[suffix.lower()])


def parse_token_budget(text: str) -> int | None:
    """Extract a token budget from user text.

    Checks shorthand-start, shorthand-end, and verbose patterns in priority
    order. Returns the first match, or ``None`` if no directive is found.
    """
    m = _SHORTHAND_START_RE.search(text)
    if m:
        return _parse_budget_match(m.group(1), m.group(2))

    m = _SHORTHAND_END_RE.search(text)
    if m:
        return _parse_budget_match(m.group(1), m.group(2))

    m = _VERBOSE_RE.search(text)
    if m:
        return _parse_budget_match(m.group(1), m.group(2))

    return None


def find_token_budget_positions(text: str) -> list[TokenBudgetPosition]:
    """Locate all budget directive spans inside *text*.

    Returns a list of ``TokenBudgetPosition`` objects (may be empty).
    Guards against double-counting when start and end patterns overlap.
    """
    positions: list[TokenBudgetPosition] = []

    # --- shorthand start ---
    m = _SHORTHAND_START_RE.search(text)
    if m:
        # Offset to the trimmed start of the match.
        trimmed_len = len(m.group(0)) - len(m.group(0).lstrip())
        offset = m.start() + trimmed_len
        positions.append(TokenBudgetPosition(start=offset, end=m.end()))

    # --- shorthand end ---
    m = _SHORTHAND_END_RE.search(text)
    if m:
        end_start = m.start() + 1  # +1: regex includes leading \s
        already_covered = any(p.start <= end_start < p.end for p in positions)
        if not already_covered:
            positions.append(TokenBudgetPosition(start=end_start, end=m.end()))

    # --- verbose (all occurrences) ---
    for m in _VERBOSE_RE.finditer(text):
        positions.append(TokenBudgetPosition(start=m.start(), end=m.end()))

    return positions


def get_budget_continuation_message(
    pct: int,
    turn_tokens: int,
    budget: int,
) -> str:
    """Build the system injection that tells the model to keep working.

    Mirrors ``getBudgetContinuationMessage`` in tokenBudget.ts.
    """
    fmt_turn = f"{turn_tokens:,}"
    fmt_budget = f"{budget:,}"
    return f"Stopped at {pct}% of token target ({fmt_turn} / {fmt_budget}). Keep working \u2014 do not summarize."
