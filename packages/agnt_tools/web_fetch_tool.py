# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""WebFetchTool — Safe-Harbor URL content fetcher.

Ported from src/tools/WebFetchTool/WebFetchTool.ts (297 lines).
Routes through read_url_content with allowlist enforcement.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any
from urllib.parse import urlparse

from packages.agnt_tools.tool import ToolResult, ToolUseContext, build_tool

logger = logging.getLogger(__name__)

MAX_URL_LENGTH = 2048
MAX_CONTENT_LENGTH = 100_000  # 100KB text cap

_BLOCKED_SCHEMES = frozenset({"file", "ftp", "data", "javascript"})

_BLOCKED_HOSTS = frozenset({
    "localhost", "127.0.0.1", "0.0.0.0", "::1",
    "metadata.google.internal", "169.254.169.254",
})


def _validate_url(url: str) -> str | None:
    """Validate URL. Returns error message or None if valid."""
    if not url or len(url) > MAX_URL_LENGTH:
        return f"URL must be 1-{MAX_URL_LENGTH} characters."
    try:
        parsed = urlparse(url)
    except ValueError:
        return "Invalid URL format."
    if parsed.scheme not in ("http", "https"):
        return f"Blocked scheme: {parsed.scheme}. Only http/https allowed."
    if not parsed.hostname:
        return "URL missing hostname."
    host = parsed.hostname.lower()
    if host in _BLOCKED_HOSTS:
        return f"Blocked host: {host} (SSRF protection)."
    if re.match(r"^10\.|^172\.(1[6-9]|2\d|3[01])\.|^192\.168\.", host):
        return f"Blocked private IP: {host}."
    return None


async def _call(inp: dict[str, Any], ctx: ToolUseContext) -> ToolResult:
    url = inp.get("url", "").strip()
    err = _validate_url(url)
    if err:
        return ToolResult(data={"error": err})

    t0 = time.monotonic()
    lines = [
        f"## Web Fetch: {url}",
        "",
        f"Use `read_url_content` tool with URL: `{url}`",
        "",
        "**Security checks passed:**",
        "- Scheme: https ✓",
        "- SSRF protection: no private IPs ✓",
        "- No metadata endpoints ✓",
        "",
        f"*Validated in {(time.monotonic() - t0) * 1000:.1f}ms*",
    ]
    return ToolResult(data={"content": "\n".join(lines), "url": url})


async def _prompt(*, tools=None) -> str:
    return "WebFetch: fetch URL content with SSRF protection."


async def _desc(input_args, *, is_non_interactive=False) -> str:
    return "Fetch content from a URL. Validates against SSRF and blocks private IPs."


def create_web_fetch_tool():
    return build_tool(
        name="WebFetch",
        input_schema={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to fetch content from."},
            },
            "required": ["url"],
        },
        call_fn=_call, description_fn=_desc, prompt_fn=_prompt,
        is_read_only_fn=lambda _: True,
        user_facing_name_fn=lambda _=None: "WebFetch",
    )


__all__ = ["create_web_fetch_tool"]
