# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Magic Docs — Auto-maintained markdown documentation.

Ported from Claude Code v2.1.91 services/MagicDocs/magicDocs.ts.

Architecture
~~~~~~~~~~~~
Magic Docs automatically maintains markdown files marked with a special header:

    # MAGIC DOC: [title]
    _[optional instructions]_

When a file with this header is read, it is registered for periodic background
updates. A background task (wired into KAIROS) re-reads the file, detects the
header, and uses a forked agent context to update the document content based on
new learnings from the conversation.

Design invariants (from Claude Code source):
- Only ``FILE_EDIT`` operations are allowed on Magic Doc files.
- Updates run only when conversation is idle (no tool calls in last turn).
- Tracked docs are de-registered when the file is deleted or the header removed.
- Gate: Original Claude Code requires ``USER_TYPE === 'ant'``. AGNT removes gate.
"""

from packages.magic_docs.detector import (
  clear_tracked_magic_docs,
  detect_magic_doc_header,
  get_tracked_magic_docs,
  register_magic_doc,
)
from packages.magic_docs.updater import update_magic_docs

__all__ = [
  "clear_tracked_magic_docs",
  "detect_magic_doc_header",
  "get_tracked_magic_docs",
  "register_magic_doc",
  "update_magic_docs",
]
