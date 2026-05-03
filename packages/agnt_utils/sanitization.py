# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""sanitization — Unicode hidden-character attack mitigation.

Ported from Claude Code v2.1.91 ``sanitization.ts``.
Implements defenses against ASCII Smuggling and Hidden Prompt Injection
as demonstrated in HackerOne report #3086545.

Protects against invisible Unicode characters (Tag characters, format
controls, private-use areas, noncharacters) that AI models process but
users cannot see.

Reference:
    https://embracethered.com/blog/posts/2024/hiding-and-finding-text-with-unicode-tags/
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, TypeVar, overload

T = TypeVar("T")

# Maximum NFKC normalization iterations before we treat input as hostile.
_MAX_ITERATIONS = 10

# ── Explicit fallback ranges ──────────────────────────────────────────────────
# These cover the most commonly abused codepoints even on runtimes without
# full Unicode property support in their regex engine.
_ZWSP_AND_MARKS = re.compile(r"[\u200B-\u200F]")
_DIRECTIONAL_FMT = re.compile(r"[\u202A-\u202E]")
_DIRECTIONAL_ISO = re.compile(r"[\u2066-\u2069]")
_BOM = re.compile(r"\uFEFF")
_BMP_PRIVATE = re.compile(r"[\uE000-\uF8FF]")

# ── Unicode category filter ──────────────────────────────────────────────────
# Categories Cf (format), Co (private-use), Cn (unassigned) match the
# original TS regex ``/[\p{Cf}\p{Co}\p{Cn}]/gu``.
_DANGEROUS_CATEGORIES = frozenset({"Cf", "Co", "Cn"})


def _strip_dangerous_categories(text: str) -> str:
    """Remove characters in Cf/Co/Cn Unicode categories."""
    return "".join(
        ch for ch in text if unicodedata.category(ch) not in _DANGEROUS_CATEGORIES
    )


def partially_sanitize_unicode(prompt: str) -> str:
    """Iteratively sanitize a string against Unicode hidden-character attacks.

    Applies NFKC normalization and removes characters in dangerous Unicode
    categories (Cf, Co, Cn) plus explicit fallback ranges for zero-width
    spaces, directional overrides, BOM, and BMP private-use area.

    Raises ``ValueError`` if the sanitization loop does not converge within
    ``_MAX_ITERATIONS`` passes — this should only happen on adversarially
    crafted input.
    """
    current = prompt
    previous = ""

    for _iteration in range(_MAX_ITERATIONS):
        previous = current

        # NFKC normalization — decomposes composed sequences.
        current = unicodedata.normalize("NFKC", current)

        # Primary: strip dangerous Unicode property classes.
        current = _strip_dangerous_categories(current)

        # Fallback: explicit ranges.
        current = _ZWSP_AND_MARKS.sub("", current)
        current = _DIRECTIONAL_FMT.sub("", current)
        current = _DIRECTIONAL_ISO.sub("", current)
        current = _BOM.sub("", current)
        current = _BMP_PRIVATE.sub("", current)

        if current == previous:
            return current

    raise ValueError(
        f"Unicode sanitization did not converge after {_MAX_ITERATIONS} "
        f"iterations for input: {prompt[:100]!r}"
    )


# ── Recursive sanitizer ──────────────────────────────────────────────────────


@overload
def recursively_sanitize_unicode(value: str) -> str: ...


@overload
def recursively_sanitize_unicode(value: list[Any]) -> list[Any]: ...


@overload
def recursively_sanitize_unicode(value: dict[str, Any]) -> dict[str, Any]: ...


@overload
def recursively_sanitize_unicode[T](value: T) -> T: ...


def recursively_sanitize_unicode(value: Any) -> Any:
    """Recursively sanitize all strings in a nested data structure.

    Walks dicts (sanitizing both keys and values), lists, and bare strings.
    Non-string primitives (int, float, bool, None) are returned unchanged.
    """
    if isinstance(value, str):
        return partially_sanitize_unicode(value)

    if isinstance(value, list):
        return [recursively_sanitize_unicode(item) for item in value]

    if isinstance(value, dict):
        return {
            recursively_sanitize_unicode(k): recursively_sanitize_unicode(v)
            for k, v in value.items()
        }

    # Primitives pass through unchanged.
    return value
