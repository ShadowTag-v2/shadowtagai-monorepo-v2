# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""WebSearchTool — Safe-Harbor web search via Antigravity MCP.

Routes Google queries to google-developer-knowledge MCP,
general queries to search_web with epistemic airgap.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any

from packages.agnt_tools.tool import ToolResult, ToolUseContext, build_tool

logger = logging.getLogger(__name__)

MAX_QUERY_LENGTH = 500

_GOOGLE_KW = frozenset({
    "firebase", "firestore", "cloud run", "gcp", "google cloud",
    "vertex ai", "gemini api", "android", "chrome devtools",
    "tensorflow", "flutter", "web.dev",
})


def _sanitize_query(query: str) -> str:
    cleaned = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", query)
    return re.sub(r"\s+", " ", cleaned).strip()[:MAX_QUERY_LENGTH]


def _is_google_query(query: str) -> bool:
    q = query.lower()
    return any(kw in q for kw in _GOOGLE_KW)


async def _call(inp: dict[str, Any], ctx: ToolUseContext) -> ToolResult:
    query = inp.get("query", "")
    if not query:
        return ToolResult(data={"error": "'query' required."})

    sanitized = _sanitize_query(query)
    if len(sanitized) < 3:
        return ToolResult(data={"error": "query too short."})

    t0 = time.monotonic()
    is_google = _is_google_query(sanitized)
    router = "google-developer-knowledge MCP" if is_google else "search_web"

    lines = [
        f"## Web Search: {sanitized}",
        f"**Router:** {router}",
        "",
        f"Use `{'search_documents' if is_google else 'search_web'}` with query: `{sanitized}`",
        "",
        f"*Routing in {(time.monotonic() - t0) * 1000:.1f}ms*",
    ]
    return ToolResult(data={"content": "\n".join(lines), "router": router, "query": sanitized})


async def _prompt(*, tools=None) -> str:
    return "WebSearch: routes Google docs to MCP, general to search_web."


async def _desc(input_args, *, is_non_interactive=False) -> str:
    return "Search the web with epistemic airgap routing."


def create_web_search_tool():
    return build_tool(
        name="WebSearch",
        input_schema={
            "type": "object",
            "properties": {"query": {"type": "string", "description": "Search query."}},
            "required": ["query"],
        },
        call_fn=_call, description_fn=_desc, prompt_fn=_prompt,
        is_read_only_fn=lambda _: True,
        user_facing_name_fn=lambda _=None: "WebSearch",
    )


__all__ = ["create_web_search_tool"]
