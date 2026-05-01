"""Unicode Sanitization for Hidden Character Attack Mitigation.

This module implements security measures against Unicode-based hidden character
attacks, specifically targeting ASCII Smuggling and Hidden Prompt Injection
vulnerabilities. These attacks use invisible Unicode characters (such as Tag
characters, format controls, private use areas, and noncharacters) to hide
malicious instructions that are invisible to users but processed by AI models.

The vulnerability was demonstrated in HackerOne report #3086545 targeting
Claude Desktop's MCP (Model Context Protocol) implementation, where attackers
could inject hidden instructions using Unicode Tag characters that would be
executed by Claude but remain invisible to users.

Reference: https://embracethered.com/blog/posts/2024/hiding-and-finding-text-with-unicode-tags/

This implementation provides comprehensive protection by:
  1. Applying NFKC Unicode normalization to handle composed character sequences
  2. Removing dangerous Unicode categories while preserving legitimate text
  3. Supporting recursive sanitization of complex nested data structures
  4. Maintaining performance with efficient processing

The sanitization is ALWAYS enabled to protect against these attacks.

Ported from: Claude Code utils/sanitization.ts
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

__all__ = [
    "partially_sanitize_unicode",
    "recursively_sanitize_unicode",
    "SanitizationOverflowError",
]

# Safety limit to prevent infinite loops during iterative normalization.
MAX_ITERATIONS = 10

# --- Dangerous Unicode ranges (Method 2: explicit fallback) ---
# These explicit ranges catch characters that may survive NFKC normalization
# or environments where unicodedata coverage is incomplete.
_ZERO_WIDTH_RE = re.compile(r"[\u200B-\u200F]")  # Zero-width spaces, LTR/RTL marks
_DIRECTIONAL_RE = re.compile(r"[\u202A-\u202E]")  # Directional formatting
_ISOLATES_RE = re.compile(r"[\u2066-\u2069]")  # Directional isolates
_BOM_RE = re.compile(r"[\uFEFF]")  # Byte order mark
_BMP_PRIVATE_USE_RE = re.compile(r"[\uE000-\uF8FF]")  # BMP private use area

# --- Dangerous Unicode categories (Method 1: category-based) ---
# Cf = Format, Co = Private Use, Cn = Unassigned
_DANGEROUS_CATEGORIES = frozenset({"Cf", "Co", "Cn"})


def _strip_dangerous_categories(text: str) -> str:
    """Remove characters in Unicode categories Cf, Co, and Cn.

    Python's ``re`` module does not natively support ``\\p{Cf}`` property
    classes, so we use ``unicodedata.category()`` per-character. This is
    equivalent to the TypeScript ``/[\\p{Cf}\\p{Co}\\p{Cn}]/gu`` regex.
    """
    return "".join(ch for ch in text if unicodedata.category(ch) not in _DANGEROUS_CATEGORIES)


class SanitizationOverflowError(RuntimeError):
    """Raised when iterative sanitization fails to converge.

    This should only ever happen if there is a bug or if someone purposefully
    created a deeply nested Unicode string designed to evade sanitization.
    """


def partially_sanitize_unicode(prompt: str) -> str:
    """Sanitize a string by removing dangerous invisible Unicode characters.

    Applies iterative NFKC normalization followed by stripping of dangerous
    Unicode categories (Cf / Co / Cn) and explicit dangerous character ranges.
    The iteration continues until the output stabilises or the safety cap of
    ``MAX_ITERATIONS`` is reached.

    Args:
        prompt: The raw input string, potentially containing hidden Unicode
            characters injected by an attacker.

    Returns:
        The sanitized string with all dangerous invisible characters removed.

    Raises:
        SanitizationOverflowError: If convergence is not reached within
            ``MAX_ITERATIONS`` passes.
    """
    current = prompt
    previous = ""
    iterations = 0

    while current != previous and iterations < MAX_ITERATIONS:
        previous = current

        # Step 1: NFKC normalization — collapses composed sequences.
        current = unicodedata.normalize("NFKC", current)

        # Step 2 (Method 1): Strip dangerous Unicode property categories.
        current = _strip_dangerous_categories(current)

        # Step 3 (Method 2): Explicit character-range fallback.
        current = _ZERO_WIDTH_RE.sub("", current)
        current = _DIRECTIONAL_RE.sub("", current)
        current = _ISOLATES_RE.sub("", current)
        current = _BOM_RE.sub("", current)
        current = _BMP_PRIVATE_USE_RE.sub("", current)

        iterations += 1

    if iterations >= MAX_ITERATIONS:
        raise SanitizationOverflowError(f"Unicode sanitization reached maximum iterations ({MAX_ITERATIONS}) for input: {prompt[:100]!r}")

    return current


def recursively_sanitize_unicode(value: Any) -> Any:
    """Recursively sanitize Unicode in nested data structures.

    Walks dicts, lists, tuples, and sets, applying
    :func:`partially_sanitize_unicode` to every string leaf (including dict
    keys). Non-string primitives (int, float, bool, None) are returned
    unchanged.

    Args:
        value: Any Python value — string, list, dict, set, tuple, or scalar.

    Returns:
        A copy of *value* with all string leaves sanitized.
    """
    if isinstance(value, str):
        return partially_sanitize_unicode(value)

    if isinstance(value, list):
        return [recursively_sanitize_unicode(item) for item in value]

    if isinstance(value, tuple):
        return tuple(recursively_sanitize_unicode(item) for item in value)

    if isinstance(value, set):
        return {recursively_sanitize_unicode(item) for item in value}

    if isinstance(value, dict):
        return {recursively_sanitize_unicode(k): recursively_sanitize_unicode(v) for k, v in value.items()}

    # Primitives (int, float, bool, None, etc.) pass through unchanged.
    return value
