"""
ShadowTag-v4 MCP Integration Module
============================

Provides MCP (Model Context Protocol) tool integration for minion swarm.
"""

from .gemini_bridge import GeminiMCPBridge, MCPToolRequest, MCPToolResponse

__all__ = ["GeminiMCPBridge", "MCPToolRequest", "MCPToolResponse"]
