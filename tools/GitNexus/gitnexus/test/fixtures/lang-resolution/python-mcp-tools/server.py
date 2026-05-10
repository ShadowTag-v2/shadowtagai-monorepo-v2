# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.


@mcp.tool()
def get_weather(city: str) -> str:
  """Get weather for a city."""
  return f"Weather in {city}: sunny"


@mcp.tool()
def search_docs(query: str) -> list:
  """Search documentation."""
  return []
