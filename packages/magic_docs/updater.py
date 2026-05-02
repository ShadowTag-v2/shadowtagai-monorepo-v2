# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Magic Docs background updater.

Ported from Claude Code v2.1.91 services/MagicDocs/magicDocs.ts.

The original uses runAgent() with a forked subagent context. Our port uses
a simpler file-read → detect-header → generate-update → write approach,
since the AGNT architecture delegates LLM calls to the Gemini bridge layer.
"""

from __future__ import annotations

import logging
import pathlib
import time

from packages.magic_docs.detector import (
    detect_magic_doc_header,
    get_tracked_magic_docs,
    unregister_magic_doc,
)

logger = logging.getLogger("magic_docs")

# Minimum interval between updates for a single doc (seconds).
_MIN_UPDATE_INTERVAL = 60.0

# Track last update timestamps per file path.
_last_update_times: dict[str, float] = {}


def _read_magic_doc(path: str) -> str | None:
    """Read a Magic Doc file, returning content or None if inaccessible."""
    try:
        return pathlib.Path(path).read_text(encoding="utf-8")
    except (OSError, PermissionError, UnicodeDecodeError) as e:
        logger.warning("Cannot read Magic Doc %s: %s", path, e)
        return None


def _should_update(path: str) -> bool:
    """Check if a doc should be updated based on rate limiting."""
    last = _last_update_times.get(path, 0.0)
    return (time.time() - last) >= _MIN_UPDATE_INTERVAL


def update_single_magic_doc(
    path: str,
    *,
    dry_run: bool = False,
) -> str | None:
    """Update a single Magic Doc.

    Reads the file, detects the header, and generates an update prompt.
    In a full implementation, this would delegate to the Gemini bridge
    for LLM-driven document updates.

    Args:
        path: Absolute path to the Magic Doc file.
        dry_run: If True, return the update prompt without executing.

    Returns:
        The generated update prompt text, or None if doc is invalid/deleted.
    """
    content = _read_magic_doc(path)
    if content is None:
        unregister_magic_doc(path)
        return None

    header = detect_magic_doc_header(content)
    if header is None:
        # File no longer has Magic Doc header — unregister.
        unregister_magic_doc(path)
        return None

    # Build the update prompt (from Claude Code's prompts.ts pattern)
    instructions_block = ""
    if header.instructions:
        instructions_block = f"\n\nInstructions from the author:\n{header.instructions}"

    prompt = (
        f"You are updating a Magic Doc titled '{header.title}'.\n\n"
        f"Current document content:\n```\n{content}\n```{instructions_block}\n\n"
        f"File path: {path}\n\n"
        "Update the document with any new relevant information from the "
        "conversation context. Only modify content below the header line. "
        "Preserve the # MAGIC DOC: header and any instructions line."
    )

    if not dry_run:
        _last_update_times[path] = time.time()

    return prompt


def update_magic_docs(
    *,
    dry_run: bool = False,
) -> dict[str, str | None]:
    """Update all tracked Magic Docs.

    Returns:
        Dict mapping file path → update prompt (or None if doc was invalid).
    """
    docs = get_tracked_magic_docs()
    if not docs:
        return {}

    results: dict[str, str | None] = {}
    for doc in docs:
        if not _should_update(doc.path):
            logger.debug("Skipping %s — rate limited", doc.path)
            continue

        result = update_single_magic_doc(doc.path, dry_run=dry_run)
        results[doc.path] = result

    updated = sum(1 for v in results.values() if v is not None)
    if updated:
        logger.info("Updated %d/%d Magic Doc(s)", updated, len(docs))

    return results
