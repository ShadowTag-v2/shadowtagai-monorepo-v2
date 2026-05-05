# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Gemini Interactions API — Unified client for live pair-programming.

The Interactions API (v1beta) is the next-generation interface for Gemini,
replacing generateContent with a unified, stateful, tool-orchestrated API.

Architecture:
  Transport:     google-genai SDK (client.interactions.create/get)
  State:         Server-side via previous_interaction_id (stateful mode)
  Streaming:     SSE with content.delta events + automatic reconnection
  Tools:         Google Search, URL Context, Code Execution, MCP servers,
                 Function Calling, Computer Use, File Search
  Models:        gemini-3-flash-preview, gemini-3-pro-preview, gemini-3.1-*

Public API:
  - InteractionsClient: Main client (create, get, stream, function call loop)
  - InteractionResult: Typed wrapper around raw interaction response
  - StreamEvent: Typed stream event (content.delta, interaction.complete, etc.)
  - StreamAccumulator: Index-based output reconstruction from streaming
  - EventType: Enumeration of SSE event types
  - ToolDefinition: Typed tool config (function, google_search, mcp_server, etc.)
"""

from gemini_interactions.client import (
    EventType,
    InteractionsClient,
    InteractionResult,
    StreamAccumulator,
    StreamEvent,
)
from gemini_interactions.session import ConversationSession
from gemini_interactions.tools import (
    ToolDefinition,
    computer_use_tool,
    code_execution_tool,
    file_search_tool,
    function_tool,
    google_search_tool,
    mcp_server_tool,
    url_context_tool,
)

__all__ = [
    # Client
    "EventType",
    "InteractionsClient",
    "InteractionResult",
    "StreamAccumulator",
    "StreamEvent",
    # Session management (best practices)
    "ConversationSession",
    # Tool builders
    "ToolDefinition",
    "computer_use_tool",
    "code_execution_tool",
    "file_search_tool",
    "function_tool",
    "google_search_tool",
    "mcp_server_tool",
    "url_context_tool",
]

