# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
FastMCP Echo Server
"""

from fastmcp import FastMCP

# Create server
mcp = FastMCP("Echo Server")


@mcp.tool
def echo(text: str) -> str:
    """Echo the input text"""
    return text
