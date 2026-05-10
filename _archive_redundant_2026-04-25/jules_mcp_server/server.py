# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Jules MCP Server — Exposes Jules SDLC capabilities via FastMCP."""

import logging
from typing import Any

from mcp.server.fastmcp import FastMCP
from jules_orchestrator.client import JulesClient, JulesAPIError

# Initialize FastMCP server
mcp = FastMCP("Jules MCP Server")

logger = logging.getLogger(__name__)


def _get_client() -> JulesClient:
  """Instantiate the JulesClient.
  It automatically reads JULES_API_KEY from the environment.
  """
  return JulesClient()


@mcp.tool()
def jules_list_sources() -> list[dict[str, Any]]:
  """List available sources (repositories) on Jules."""
  client = _get_client()
  try:
    return client.list_sources()
  except JulesAPIError as e:
    logger.error("Failed to list sources: %s", e)
    return [{"error": str(e)}]
  except Exception as e:
    logger.exception("Unexpected error in jules_list_sources")
    return [{"error": str(e)}]


@mcp.tool()
def jules_execute_task(
  source_name: str, task_description: str, automation_mode: str = "AUTO_CREATE_PR"
) -> dict[str, Any]:
  """
  Create a new Jules session within a source and poll until it reaches a terminal state.

  Args:
      source_name: The name of the source (repository) to operate on.
      task_description: The description of the task for Jules to execute.
      automation_mode: The automation mode (default "AUTO_CREATE_PR").
  """
  client = _get_client()
  try:
    # Create session
    session = client.create_session(
      source_name=source_name,
      automation_mode=automation_mode,
      task_description=task_description,
    )
    session_name = session.get("name")
    if not session_name:
      return {
        "error": "Session creation succeeded but returned no session name.",
        "response": session,
      }

    # Poll session until terminal state
    result = client.poll_session(session_name)
    return result
  except JulesAPIError as e:
    logger.error("Failed to execute task: %s", e)
    return {"error": str(e)}
  except Exception as e:
    logger.exception("Unexpected error in jules_execute_task")
    return {"error": str(e)}


@mcp.tool()
def jules_approve_plan(session_name: str, message: str = "") -> dict[str, Any]:
  """
  Approve a pending plan for a Jules session.

  Args:
      session_name: The full resource name of the session.
      message: Optional message to include with the approval.
  """
  client = _get_client()
  try:
    return client.approve_plan(session_name=session_name, message=message)
  except JulesAPIError as e:
    logger.error("Failed to approve plan: %s", e)
    return {"error": str(e)}
  except Exception as e:
    logger.exception("Unexpected error in jules_approve_plan")
    return {"error": str(e)}


@mcp.tool()
def jules_interact(session_name: str, text: str) -> dict[str, Any]:
  """
  Send an interaction to an active Jules session.

  Args:
      session_name: The full resource name of the session.
      text: The text interaction to send to the session.
  """
  client = _get_client()
  try:
    return client.interact(session_name=session_name, text=text)
  except JulesAPIError as e:
    logger.error("Failed to interact with session: %s", e)
    return {"error": str(e)}
  except Exception as e:
    logger.exception("Unexpected error in jules_interact")
    return {"error": str(e)}


if __name__ == "__main__":
  # Run over stdio for MCP clients
  mcp.run(transport="stdio")
