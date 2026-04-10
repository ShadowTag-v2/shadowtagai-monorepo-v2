"""
Cor Tool Registry

Central registration point for all MCP tools including:
- Internal tools (file search, code search, doc retrieval)
- External tools (web search)

This module provides the interface between Cor orchestrator
and tool implementations.
"""

from dataclasses import dataclass
from typing import Any

from pnkln.tools.web_search import create_web_search_tool


# ============================================================================
# TOOL REGISTRY
# ============================================================================
@dataclass
class ToolDefinition:
    """MCP tool definition."""

    name: str
    description: str
    parameters: dict
    handler: Any  # Tool class or function


class ToolRegistry:
    """
    Central registry for all available tools.

    Tools register themselves here and Cor orchestrator
    discovers and executes them based on intent routing.
    """

    def __init__(self):
        """Initialize empty registry."""
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool_def: dict) -> None:
        """
        Register a tool.

        Args:
            tool_def: Tool definition dict with name, description, parameters, handler
        """
        tool = ToolDefinition(
            name=tool_def["name"],
            description=tool_def["description"],
            parameters=tool_def["parameters"],
            handler=tool_def["handler"],
        )

        self._tools[tool.name] = tool
        print(f"✅ Registered tool: {tool.name}")

    def get(self, name: str) -> ToolDefinition:
        """Get tool by name."""
        if name not in self._tools:
            raise KeyError(f"Tool not found: {name}")
        return self._tools[name]

    def list_tools(self) -> list[str]:
        """List all registered tool names."""
        return list(self._tools.keys())

    def get_all(self) -> dict[str, ToolDefinition]:
        """Get all registered tools."""
        return self._tools.copy()


# ============================================================================
# GLOBAL REGISTRY INSTANCE
# ============================================================================
_registry = ToolRegistry()


def get_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    return _registry


# ============================================================================
# AUTO-REGISTRATION
# ============================================================================
def register_default_tools():
    """Register all default tools on module import."""

    # Register web search tool
    _registry.register(create_web_search_tool())

    # TODO: Register internal tools
    # - file_search
    # - code_search
    # - doc_retrieval
    # - repository_search


# Auto-register on import
register_default_tools()
