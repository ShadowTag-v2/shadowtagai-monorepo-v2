# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""string_utils — string accumulators, truncation, and formatting helpers.

Ported from Claude Code v2.1.91 ``stringUtils.ts``.
Provides safe string accumulation, regex escaping, pluralization,
full-width normalization, and line-based truncation.
"""

from __future__ import annotations

import re

# Keep in-memory accumulation modest to avoid blowing up RSS.
MAX_STRING_LENGTH = 2**25  # ~33 MB


def escape_regexp(pattern: str) -> str:
  """Escape special regex characters so *pattern* can be used as a literal."""
  return re.escape(pattern)


def capitalize_first(text: str) -> str:
  """Uppercase the first character, leaving the rest unchanged.

  Unlike ``str.capitalize()``, this does NOT lowercase the remaining
  characters.

  >>> capitalize_first("fooBar")
  'FooBar'
  """
  if not text:
    return text
  return text[0].upper() + text[1:]


def plural(n: int, word: str, plural_word: str | None = None) -> str:
  """Return singular or plural form of *word* based on *n*.

  >>> plural(1, "file")
  'file'
  >>> plural(3, "file")
  'files'
  >>> plural(2, "entry", "entries")
  'entries'
  """
  if plural_word is None:
    plural_word = word + "s"
  return word if n == 1 else plural_word


def first_line_of(text: str) -> str:
  """Return the first line without allocating a split array."""
  nl = text.find("\n")
  return text if nl == -1 else text[:nl]


def count_char(text: str, char: str, start: int = 0) -> int:
  """Count occurrences of *char* in *text* from *start* using index jumps."""
  count = 0
  idx = text.find(char, start)
  while idx != -1:
    count += 1
    idx = text.find(char, idx + 1)
  return count


def normalize_fullwidth_digits(text: str) -> str:
  """Convert full-width (zenkaku) digits ０-９ to half-width 0-9."""

  def _convert(m: re.Match[str]) -> str:
    return chr(ord(m.group(0)) - 0xFEE0)

  return re.sub(r"[０-９]", _convert, text)


def normalize_fullwidth_space(text: str) -> str:
  """Convert full-width ideographic space (U+3000) to ASCII space."""
  return text.replace("\u3000", " ")


def safe_join_lines(
  lines: list[str],
  delimiter: str = ",",
  max_size: int = MAX_STRING_LENGTH,
) -> str:
  """Join *lines* with *delimiter*, truncating if the result exceeds *max_size*."""
  truncation_marker = "...[truncated]"
  result = ""

  for line in lines:
    delim = delimiter if result else ""
    full_addition = delim + line

    if len(result) + len(full_addition) <= max_size:
      result += full_addition
    else:
      remaining = max_size - len(result) - len(delim) - len(truncation_marker)
      if remaining > 0:
        result += delim + line[:remaining] + truncation_marker
      else:
        result += truncation_marker
      return result

  return result


def truncate_to_lines(text: str, max_lines: int) -> str:
  """Truncate *text* to *max_lines*, adding an ellipsis if truncated."""
  lines = text.split("\n")
  if len(lines) <= max_lines:
    return text
  return "\n".join(lines[:max_lines]) + "…"


class EndTruncatingAccumulator:
  """String accumulator that truncates from the end when a size limit is hit.

  Prevents ``MemoryError`` while preserving the beginning of the output —
  ideal for daemon telemetry and shell command capture.

  >>> acc = EndTruncatingAccumulator(max_size=100)
  >>> acc.append("x" * 200)
  >>> acc.truncated
  True
  """

  __slots__ = ("_content", "_is_truncated", "_total_bytes", "_max_size")

  def __init__(self, max_size: int = MAX_STRING_LENGTH) -> None:
    self._content = ""
    self._is_truncated = False
    self._total_bytes = 0
    self._max_size = max_size

  def append(self, data: str | bytes) -> None:
    """Append *data*, truncating the end if the limit is exceeded."""
    text = data if isinstance(data, str) else data.decode("utf-8", errors="replace")
    self._total_bytes += len(text)

    if self._is_truncated and len(self._content) >= self._max_size:
      return

    if len(self._content) + len(text) > self._max_size:
      remaining = self._max_size - len(self._content)
      if remaining > 0:
        self._content += text[:remaining]
      self._is_truncated = True
    else:
      self._content += text

  def __str__(self) -> str:
    if not self._is_truncated:
      return self._content
    truncated_bytes = self._total_bytes - self._max_size
    truncated_kb = round(truncated_bytes / 1024)
    return self._content + f"\n... [output truncated - {truncated_kb}KB removed]"

  def clear(self) -> None:
    """Reset the accumulator."""
    self._content = ""
    self._is_truncated = False
    self._total_bytes = 0

  @property
  def length(self) -> int:
    """Current accumulated length."""
    return len(self._content)

  @property
  def truncated(self) -> bool:
    """Whether truncation has occurred."""
    return self._is_truncated

  @property
  def total_bytes(self) -> int:
    """Total bytes received before truncation."""
    return self._total_bytes
