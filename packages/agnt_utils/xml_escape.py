# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""xml_escape — XML/HTML entity escaping for prompt safety.

Ported from Claude Code v2.1.91 ``xml.ts``.
"""

from __future__ import annotations


def escape_xml(text: str) -> str:
    """Escape & < > for safe interpolation into XML text content."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def escape_xml_attr(text: str) -> str:
    """Escape for interpolation into a quoted attribute value."""
    return escape_xml(text).replace('"', "&quot;").replace("'", "&apos;")
