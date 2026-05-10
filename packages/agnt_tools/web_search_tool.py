# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""WebSearchTool — Safe-Harbor web search via Antigravity MCP.

Ported from src/tools/WebSearchTool/WebSearchTool.ts (415 lines).
Routes Google queries to google-developer-knowledge MCP,
general queries to search_web with epistemic airgap.

Upstream features ported:
  - Domain allow/block lists (mutually exclusive)
  - Query sanitization with length cap
  - MCP router classification (google-developer-knowledge vs search_web)
  - Concurrency safe, read-only
  - Always-passthrough permissions
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any

from packages.agnt_tools.tool import ToolResult, ToolUseContext, build_tool

logger = logging.getLogger(__name__)

WEB_SEARCH_TOOL_NAME = "WebSearch"
MAX_QUERY_LENGTH = 500
MAX_SEARCH_USES = 8  # Upstream hardcoded limit per search session

_GOOGLE_KW = frozenset(
  {
    "firebase",
    "firestore",
    "cloud run",
    "gcp",
    "google cloud",
    "vertex ai",
    "gemini api",
    "android",
    "chrome devtools",
    "tensorflow",
    "flutter",
    "web.dev",
    "cloud functions",
    "app engine",
    "bigquery",
    "kubernetes",
    "gke",
  }
)


def _sanitize_query(query: str) -> str:
  """Strip control chars and normalize whitespace."""
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
    return ToolResult(data={"error": "query too short (min 3 chars)."})

  # Domain filters (upstream: allowed_domains / blocked_domains, mutually exclusive)
  allowed_domains: list[str] | None = inp.get("allowed_domains")
  blocked_domains: list[str] | None = inp.get("blocked_domains")
  if allowed_domains and blocked_domains:
    return ToolResult(
      data={"error": "Cannot specify both allowed_domains and blocked_domains."}
    )

  t0 = time.monotonic()
  is_google = _is_google_query(sanitized)
  router = "google-developer-knowledge MCP" if is_google else "search_web"

  lines = [
    f"## Web Search: {sanitized}",
    f"**Router:** {router}",
    "",
    f"Use `{'search_documents' if is_google else 'search_web'}` with query: `{sanitized}`",
  ]

  # Append domain filter instructions if present
  if allowed_domains:
    lines.append(f"**Allowed domains:** {', '.join(allowed_domains)}")
  if blocked_domains:
    lines.append(f"**Blocked domains:** {', '.join(blocked_domains)}")

  lines.extend(
    [
      "",
      f"*Routing in {(time.monotonic() - t0) * 1000:.1f}ms*",
    ]
  )

  return ToolResult(
    data={
      "content": "\n".join(lines),
      "router": router,
      "query": sanitized,
      "allowed_domains": allowed_domains,
      "blocked_domains": blocked_domains,
    }
  )


async def _prompt(*, tools=None) -> str:
  return "WebSearch: routes Google docs to google-developer-knowledge MCP, general queries to search_web. Supports domain allow/block lists."


async def _desc(input_args, *, is_non_interactive=False) -> str:
  query = input_args.get("query", "") if isinstance(input_args, dict) else ""
  if query:
    return f"Search the web for: {query[:60]}"
  return "Search the web with epistemic airgap routing."


def create_web_search_tool():
  return build_tool(
    name=WEB_SEARCH_TOOL_NAME,
    input_schema={
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "The search query to use.",
        },
        "allowed_domains": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Only include search results from these domains.",
        },
        "blocked_domains": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Never include search results from these domains.",
        },
      },
      "required": ["query"],
    },
    call_fn=_call,
    description_fn=_desc,
    prompt_fn=_prompt,
    max_result_size_chars=100_000,
    search_hint="search the web for current information",
    should_defer=True,
    is_read_only_fn=lambda _: True,
    is_concurrency_safe_fn=lambda _: True,
    user_facing_name_fn=lambda _=None: "Web Search",
  )


__all__ = ["WEB_SEARCH_TOOL_NAME", "create_web_search_tool"]
