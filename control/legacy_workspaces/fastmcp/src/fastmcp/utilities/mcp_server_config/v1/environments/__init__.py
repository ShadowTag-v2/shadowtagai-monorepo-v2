# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Environment configuration for MCP servers."""

from fastmcp.utilities.mcp_server_config.v1.environments.base import Environment
from fastmcp.utilities.mcp_server_config.v1.environments.uv import UVEnvironment

__all__ = ["Environment", "UVEnvironment"]
