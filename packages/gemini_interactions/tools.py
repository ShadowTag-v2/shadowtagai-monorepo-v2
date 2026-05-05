# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tool definitions for the Gemini Interactions API.

Each factory function returns a dict matching the Interactions API tool schema.
Using typed builders prevents schema drift and enforces correct structure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ToolDefinition:
    """Typed wrapper around an Interactions API tool dict."""

    type: str
    config: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to the wire format expected by client.interactions.create()."""
        result = {"type": self.type}
        result.update(self.config)
        return result


def google_search_tool(
    *,
    search_types: list[str] | None = None,
) -> dict[str, Any]:
    """Google Search grounding tool.

    Args:
        search_types: Optional list like ["web_search", "image_search"].
    """
    tool: dict[str, Any] = {"type": "google_search"}
    if search_types:
        tool["search_types"] = search_types
    return tool


def url_context_tool() -> dict[str, Any]:
    """URL Context tool — read and summarize web pages."""
    return {"type": "url_context"}


def code_execution_tool() -> dict[str, Any]:
    """Code Execution tool — run Python for calculations/analysis."""
    return {"type": "code_execution"}


def mcp_server_tool(
    *,
    name: str,
    url: str,
    headers: dict[str, str] | None = None,
    allowed_tools: list[str] | None = None,
) -> dict[str, Any]:
    """Remote MCP server tool.

    Args:
        name: Display name (snake_case, no hyphens).
        url: Full URL for the Streamable HTTP MCP endpoint.
        headers: Optional auth headers (e.g., {"Authorization": "Bearer ..."}).
        allowed_tools: Optional list restricting which server tools are callable.
    """
    tool: dict[str, Any] = {
        "type": "mcp_server",
        "name": name,
        "url": url,
    }
    if headers:
        tool["headers"] = headers
    if allowed_tools:
        tool["allowed_tools"] = allowed_tools
    return tool


def function_tool(
    *,
    name: str,
    description: str,
    parameters: dict[str, Any],
) -> dict[str, Any]:
    """Custom function calling tool.

    Args:
        name: Function name (e.g., "get_weather").
        description: What the function does.
        parameters: JSON Schema object describing parameters.
    """
    return {
        "type": "function",
        "name": name,
        "description": description,
        "parameters": parameters,
    }


def computer_use_tool(
    *,
    environment: str = "browser",
    display_width_px: int = 1024,
    display_height_px: int = 768,
) -> dict[str, Any]:
    """Computer Use tool — for gemini-2.5-computer-use-preview models.

    Enables the model to interact with a screen environment by
    producing actions (click, type, scroll, screenshot, etc.).

    Args:
        environment: Execution environment — "browser" or "desktop".
        display_width_px: Screen width in pixels.
        display_height_px: Screen height in pixels.
    """
    return {
        "type": "computer_use",
        "computer_use": {
            "environment": environment,
            "display_width_px": display_width_px,
            "display_height_px": display_height_px,
        },
    }


def file_search_tool(
    *,
    file_ids: list[str] | None = None,
    vector_store_ids: list[str] | None = None,
) -> dict[str, Any]:
    """File Search tool — ground responses in uploaded files.

    Enables retrieval-augmented generation over files previously
    uploaded via the Files API.

    Args:
        file_ids: List of file resource names (e.g., ["files/abc123"]).
        vector_store_ids: List of vector store IDs for pre-indexed search.
    """
    tool: dict[str, Any] = {"type": "file_search"}
    config: dict[str, Any] = {}
    if file_ids:
        config["file_ids"] = file_ids
    if vector_store_ids:
        config["vector_store_ids"] = vector_store_ids
    if config:
        tool["file_search"] = config
    return tool
