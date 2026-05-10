# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Entry point for Jules MCP Server.

Enables execution via `python -m jules_mcp_server`.
"""

import logging

from jules_mcp_server.server import mcp

if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  mcp.run(transport="stdio")
