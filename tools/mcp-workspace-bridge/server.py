"""
server.py — MCP stdio wrapper for intent_sync.py

Exposes `fetch_and_embed_business_intent` as an MCP tool callable by
any agent via JSON-RPC 2.0 over stdin/stdout.

Architecture:
  Agent ──stdin──▶ server.py ──▶ intent_sync.py ──▶ Google Drive + Gemini
         stdout◀──           ◀──                  ◀──

Usage:
    python tools/mcp-workspace-bridge/server.py
    (then send JSON-RPC requests on stdin)

MCP config entry:
    "uphill-workspace-intake": {
        "command": "python",
        "args": ["tools/mcp-workspace-bridge/server.py"],
        "disabled": false
    }
"""

import json
import sys
import logging
import traceback

from intent_sync import fetch_and_embed_business_intent

logging.basicConfig(
    level=logging.INFO,
    format="[mcp-workspace-bridge] %(message)s",
    stream=sys.stderr,  # MCP: logs to stderr, responses to stdout
)
log = logging.getLogger(__name__)

# JSON-RPC 2.0 helpers
JSONRPC_VERSION = "2.0"


def _success(request_id, result):
    """Build a JSON-RPC 2.0 success response."""
    return json.dumps({
        "jsonrpc": JSONRPC_VERSION,
        "id": request_id,
        "result": result,
    })


def _error(request_id, code, message, data=None):
    """Build a JSON-RPC 2.0 error response."""
    err = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return json.dumps({
        "jsonrpc": JSONRPC_VERSION,
        "id": request_id,
        "error": err,
    })


# MCP tool manifest
TOOLS = [
    {
        "name": "fetch_and_embed_business_intent",
        "description": (
            "Autonomously reads human PRDs from Google Drive and embeds them "
            "into the Sovereign Memory (Gemini FileSearchStore). "
            "Returns status of documents found and embedded."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "drive_folder_id": {
                    "type": "string",
                    "description": "Google Drive folder ID containing PRD_ documents. Optional.",
                },
                "store_name": {
                    "type": "string",
                    "description": "Gemini FileSearchStore name to upload into. Optional.",
                },
            },
            "required": [],
        },
    },
]


def handle_request(request: dict) -> str:
    """Route a JSON-RPC 2.0 request to the appropriate handler."""
    method = request.get("method", "")
    request_id = request.get("id")
    params = request.get("params", {})

    # --- MCP Protocol Methods ---

    if method == "initialize":
        return _success(request_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": False},
            },
            "serverInfo": {
                "name": "uphill-workspace-intake",
                "version": "1.0.0",
            },
        })

    if method == "notifications/initialized":
        # Client acknowledgement — no response needed for notifications
        return ""

    if method == "tools/list":
        return _success(request_id, {"tools": TOOLS})

    if method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        if tool_name == "fetch_and_embed_business_intent":
            try:
                result = fetch_and_embed_business_intent(
                    drive_folder_id=arguments.get("drive_folder_id"),
                    store_name=arguments.get("store_name"),
                )
                return _success(request_id, {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2),
                        }
                    ],
                    "isError": "error" in result,
                })
            except Exception as exc:
                tb = traceback.format_exc()
                log.error(f"Tool execution failed: {exc}\n{tb}")
                return _success(request_id, {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "error": str(exc),
                                "traceback": tb,
                            }),
                        }
                    ],
                    "isError": True,
                })

        return _error(request_id, -32601, f"Unknown tool: {tool_name}")

    return _error(request_id, -32601, f"Unknown method: {method}")


def main():
    """Run the MCP stdio server loop."""
    log.info("MCP Workspace Bridge server started (stdio mode)")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
        except json.JSONDecodeError as exc:
            response = _error(None, -32700, f"Parse error: {exc}")
            sys.stdout.write(response + "\n")
            sys.stdout.flush()
            continue

        response = handle_request(request)
        if response:  # Skip empty responses (notifications)
            sys.stdout.write(response + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
