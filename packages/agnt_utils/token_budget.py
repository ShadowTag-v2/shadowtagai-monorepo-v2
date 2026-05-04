# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Token budget parser — ported from utils/tokenBudget.ts.

Parses shorthand (+500k, +2M) and verbose ("use 2M tokens") budget
directives from user prompts. Regex patterns are kept identical to the
upstream TypeScript implementation for behavioral parity.
"""

from __future__ import annotations

import re
from typing import NamedTuple

# ── Patterns (identical to upstream) ──────────────────────────────────────────

# Shorthand (+500k) anchored to start/end to avoid false positives in
# natural language.
_SHORTHAND_START_RE = re.compile(r"^\s*\+(\d+(?:\.\d+)?)\s*(k|m|b)\b", re.I)

# End-anchored variant. Upstream avoids lookbehind for JSC perf;
# we capture the whitespace instead.
_SHORTHAND_END_RE = re.compile(r"\s\+(\d+(?:\.\d+)?)\s*(k|m|b)\s*[.!?]?\s*$", re.I)

# Verbose: "use 2M tokens" / "spend 500k tokens"
_VERBOSE_RE = re.compile(r"\b(?:use|spend)\s+(\d+(?:\.\d+)?)\s*(k|m|b)\s*tokens?\b", re.I)

_MULTIPLIERS = {
    "k": 1_000,
    "m": 1_000_000,
    "b": 1_000_000_000,
}


def _parse_budget_match(value: str, suffix: str) -> int:
    """Convert matched groups to an integer token count."""
    return int(float(value) * _MULTIPLIERS[suffix.lower()])


# ── Public API ────────────────────────────────────────────────────────────────


def parse_token_budget(text: str) -> int | None:
    """Parse a token budget from a user prompt string.

    Checks in order:
      1. Shorthand at start: ``"+500k fix this"``
      2. Shorthand at end:   ``"fix this +2M"``
      3. Verbose:            ``"use 2M tokens to refactor"``

    Returns:
        Token count as int, or None if no budget found.
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


class BudgetPosition(NamedTuple):
    """Character span of a budget directive in the input text."""

    start: int
    end: int


def find_token_budget_positions(text: str) -> list[BudgetPosition]:
    """Find all budget directive positions in text.

    Returns a list of (start, end) character spans. Deduplicates
    overlapping start/end shorthand matches on single-budget inputs.
    """
    positions: list[BudgetPosition] = []

    m = _SHORTHAND_START_RE.search(text)
    if m:
        offset = m.start() + len(m.group(0)) - len(m.group(0).lstrip())
        positions.append(BudgetPosition(offset, m.end()))

    m = _SHORTHAND_END_RE.search(text)
    if m:
        end_start = m.start() + 1  # +1: regex includes leading \s
        already_covered = any(end_start >= p.start and end_start < p.end for p in positions)
        if not already_covered:
            positions.append(BudgetPosition(end_start, m.end()))

    for m in _VERBOSE_RE.finditer(text):
        positions.append(BudgetPosition(m.start(), m.end()))

    return positions


def get_budget_continuation_message(
    pct: int,
    turn_tokens: int,
    budget: int,
) -> str:
    """Format the continuation message shown when a budget gate fires."""
    fmt_turn = f"{turn_tokens:,}"
    fmt_budget = f"{budget:,}"
    return f"Stopped at {pct}% of token target ({fmt_turn} / {fmt_budget}). Keep working \u2014 do not summarize."
