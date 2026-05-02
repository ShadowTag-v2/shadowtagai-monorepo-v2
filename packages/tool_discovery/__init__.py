# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tool Discovery — Dynamic deferred tool loading with threshold-based auto-enable.

Synthesized from Claude Code v2.1.91 production patterns:
  - toolSearch.ts: ToolSearchMode, isToolSearchEnabled, isToolSearchEnabledOptimistic
  - toolSearch.ts L49: DEFAULT_AUTO_TOOL_SEARCH_PERCENTAGE = 10
  - toolSearch.ts L99: CHARS_PER_TOKEN = 2.5 approximation
  - toolSearch.ts L161: ToolSearchMode union type (tst / tst-auto / standard)
  - toolSearch.ts L239-252: modelSupportsToolReference negative test
  - toolSearch.ts L340-365: calculateDeferredToolDescriptionChars

Adds typed Python enums, configurable threshold calculator, and deferred
tool registry that CC handles through GrowthBook feature flags.

Usage:
    from tool_discovery import (
        ToolDiscovery, ToolSearchMode, ToolSearchConfig, DeferredToolEntry,
    )

    config = ToolSearchConfig(mode=ToolSearchMode.TST_AUTO, auto_percentage=10)
    discovery = ToolDiscovery(config=config, model="gemini-3.1-flash-lite")
    discovery.register_tool(DeferredToolEntry(name="mcp_firestore", ...))

    if discovery.is_enabled():
        deferred = discovery.get_deferred_tools()
"""

from tool_discovery.core import (
    DeferredToolEntry,
    ToolDiscovery,
    ToolSearchConfig,
    ToolSearchMode,
)

__all__ = [
    "DeferredToolEntry",
    "ToolDiscovery",
    "ToolSearchConfig",
    "ToolSearchMode",
]
