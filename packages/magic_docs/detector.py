# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Magic Doc header detection and tracking.

Ported from Claude Code v2.1.91 services/MagicDocs/magicDocs.ts.
"""

from __future__ import annotations

import pathlib
import re
import threading
from dataclasses import dataclass
from typing import Optional

# Magic Doc header pattern: # MAGIC DOC: [title]
# Matches at the start of the file (first line)
MAGIC_DOC_HEADER_PATTERN = re.compile(r"^#\s*MAGIC\s+DOC:\s*(.+)$", re.IGNORECASE | re.MULTILINE)

# Pattern to match italics on the line immediately after the header
ITALICS_PATTERN = re.compile(r"^[_*](.+?)[_*]\s*$", re.MULTILINE)


@dataclass(frozen=True, slots=True)
class MagicDocHeader:
    """Parsed Magic Doc header information.

    Attributes:
        title: The document title from the header.
        instructions: Optional instructions from the italicized line.
    """

    title: str
    instructions: Optional[str] = None


@dataclass(frozen=True, slots=True)
class MagicDocInfo:
    """Tracking info for a registered Magic Doc.

    Attributes:
        path: Absolute path to the Magic Doc file.
    """

    path: str


# Thread-safe tracking of registered Magic Docs.
_tracked_lock = threading.Lock()
_tracked_magic_docs: dict[str, MagicDocInfo] = {}


def detect_magic_doc_header(content: str) -> Optional[MagicDocHeader]:
    """Detect if file content contains a Magic Doc header.

    Returns:
        MagicDocHeader with title and optional instructions, or None.
    """
    match = MAGIC_DOC_HEADER_PATTERN.search(content)
    if not match or not match.group(1):
        return None

    title = match.group(1).strip()

    # Look for italics on the next line after the header
    header_end = match.end()
    after_header = content[header_end:]

    # Match: newline, optional blank line, then content line
    next_line_match = re.match(r"^\s*\n(?:\s*\n)?(.+?)(?:\n|$)", after_header)

    if next_line_match and next_line_match.group(1):
        next_line = next_line_match.group(1)
        italics_match = ITALICS_PATTERN.match(next_line)
        if italics_match and italics_match.group(1):
            return MagicDocHeader(
                title=title,
                instructions=italics_match.group(1).strip(),
            )

    return MagicDocHeader(title=title)


def register_magic_doc(file_path: str | pathlib.Path) -> bool:
    """Register a file as a Magic Doc for background updates.

    Only registers once per file path.

    Returns:
        True if newly registered, False if already tracked.
    """
    path_str = str(file_path)
    with _tracked_lock:
        if path_str in _tracked_magic_docs:
            return False
        _tracked_magic_docs[path_str] = MagicDocInfo(path=path_str)
        return True


def unregister_magic_doc(file_path: str | pathlib.Path) -> bool:
    """Remove a Magic Doc from tracking.

    Returns:
        True if was tracked, False if not found.
    """
    path_str = str(file_path)
    with _tracked_lock:
        return _tracked_magic_docs.pop(path_str, None) is not None


def get_tracked_magic_docs() -> list[MagicDocInfo]:
    """Get a snapshot of all tracked Magic Docs."""
    with _tracked_lock:
        return list(_tracked_magic_docs.values())


def clear_tracked_magic_docs() -> int:
    """Clear all tracked Magic Docs. Returns count cleared."""
    with _tracked_lock:
        count = len(_tracked_magic_docs)
        _tracked_magic_docs.clear()
        return count
