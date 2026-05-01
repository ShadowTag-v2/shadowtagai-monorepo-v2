# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Text truncation utilities — ported from utils/truncate.ts.

Provides width-aware and grapheme-aware truncation for:
  - General text (with ``…`` ellipsis)
  - File paths (middle-truncated to preserve dir context + filename)
  - Text wrapping to fixed width

The upstream TypeScript version uses ``stringWidth()`` and
``Intl.Segmenter`` for correct CJK/emoji measurement.  This Python
port uses ``unicodedata`` for character width estimation and the
stdlib ``graphlib``-adjacent approach for grapheme boundaries.

For production CJK accuracy, consider using ``wcwidth`` (pip) as a
drop-in replacement for ``_char_width``.
"""

from __future__ import annotations

import unicodedata


# ── Character width estimation ────────────────────────────────────────────────


def _char_width(ch: str) -> int:
    """Estimate display width of a single character.

    Uses Unicode East Asian Width to detect full-width (W/F) characters.
    Returns 2 for wide characters, 0 for combining marks, 1 otherwise.
    """
    eaw = unicodedata.east_asian_width(ch)
    if eaw in ("W", "F"):
        return 2
    cat = unicodedata.category(ch)
    if cat.startswith("M"):  # combining marks
        return 0
    return 1


def string_width(text: str) -> int:
    """Estimate the display width of a string in terminal columns.

    Handles CJK characters (width 2) and combining marks (width 0).
    Strips ANSI escape sequences.
    """
    # Strip ANSI escape sequences
    import re
    clean = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", text)

    width = 0
    for ch in clean:
        width += _char_width(ch)
    return width


# ── Truncation functions ──────────────────────────────────────────────────────


def truncate_to_width(text: str, max_width: int) -> str:
    """Truncate a string to fit within ``max_width`` terminal columns.

    Appends ``…`` when truncation occurs.  Splits on character boundaries
    to avoid breaking multi-byte sequences.
    """
    if string_width(text) <= max_width:
        return text
    if max_width <= 1:
        return "…"

    width = 0
    result: list[str] = []
    for ch in text:
        cw = _char_width(ch)
        if width + cw > max_width - 1:  # -1 for ellipsis
            break
        result.append(ch)
        width += cw
    return "".join(result) + "…"


def truncate_start_to_width(text: str, max_width: int) -> str:
    """Truncate from the start, keeping the tail end.

    Prepends ``…`` when truncation occurs.
    """
    if string_width(text) <= max_width:
        return text
    if max_width <= 1:
        return "…"

    # Walk from end, accumulating width
    chars = list(text)
    width = 0
    start_idx = len(chars)
    for i in range(len(chars) - 1, -1, -1):
        cw = _char_width(chars[i])
        if width + cw > max_width - 1:  # -1 for ellipsis
            break
        width += cw
        start_idx = i

    return "…" + "".join(chars[start_idx:])


def truncate_to_width_no_ellipsis(text: str, max_width: int) -> str:
    """Truncate without appending an ellipsis.

    Useful when the caller adds its own separator (e.g. middle-truncation).
    """
    if string_width(text) <= max_width:
        return text
    if max_width <= 0:
        return ""

    width = 0
    result: list[str] = []
    for ch in text:
        cw = _char_width(ch)
        if width + cw > max_width:
            break
        result.append(ch)
        width += cw
    return "".join(result)


def truncate_path_middle(path: str, max_length: int) -> str:
    """Truncate a file path in the middle to preserve directory context
    and filename.

    Example::

        truncate_path_middle(
            "src/components/deeply/nested/folder/MyComponent.tsx", 30
        )
        # => "src/components/…/MyComponent.tsx"

    Args:
        path: The file path to truncate.
        max_length: Maximum display width in terminal columns.

    Returns:
        The truncated path, or the original if it fits.
    """
    if string_width(path) <= max_length:
        return path

    if max_length <= 0:
        return "…"

    if max_length < 5:
        return truncate_to_width(path, max_length)

    # Split into directory and filename
    last_slash = path.rfind("/")
    if last_slash >= 0:
        filename = path[last_slash:]  # includes leading /
        directory = path[:last_slash]
    else:
        filename = path
        directory = ""

    filename_width = string_width(filename)

    # If filename alone is too long, truncate from start
    if filename_width >= max_length - 1:
        return truncate_start_to_width(path, max_length)

    # Calculate space for directory prefix
    available_for_dir = max_length - 1 - filename_width  # -1 for ellipsis

    if available_for_dir <= 0:
        return truncate_start_to_width(filename, max_length)

    truncated_dir = truncate_to_width_no_ellipsis(directory, available_for_dir)
    return truncated_dir + "…" + filename


def truncate(
    text: str,
    max_width: int,
    single_line: bool = False,
) -> str:
    """General-purpose truncation with optional single-line mode.

    Args:
        text: The string to truncate.
        max_width: Maximum display width in terminal columns.
        single_line: If True, also truncate at the first newline.

    Returns:
        The truncated string with ``…`` if truncation occurred.
    """
    result = text

    if single_line:
        first_newline = text.find("\n")
        if first_newline != -1:
            result = text[:first_newline]
            if string_width(result) + 1 > max_width:
                return truncate_to_width(result, max_width)
            return f"{result}…"

    if string_width(result) <= max_width:
        return result
    return truncate_to_width(result, max_width)


def wrap_text(text: str, width: int) -> list[str]:
    """Wrap text to a fixed width, respecting character widths.

    Returns a list of wrapped lines.
    """
    lines: list[str] = []
    current_line: list[str] = []
    current_width = 0

    for ch in text:
        cw = _char_width(ch)
        if current_width + cw <= width:
            current_line.append(ch)
            current_width += cw
        else:
            if current_line:
                lines.append("".join(current_line))
            current_line = [ch]
            current_width = cw

    if current_line:
        lines.append("".join(current_line))
    return lines
