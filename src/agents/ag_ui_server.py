# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""AG-UI SSE Server — Standalone HTTP server for real-time agent events.

Provides two endpoints:
  GET /ag-ui/events   — SSE stream (text/event-stream)
  GET /ag-ui/state    — JSON state snapshot
  GET /ag-ui/health   — Health check

This server runs as a lightweight asyncio HTTP handler (no framework
dependency). It can be started standalone or embedded in a larger ASGI app.

Usage::
    python -m agents.ag_ui_server --port 8787

    # Or from Python:
    from agents.ag_ui_server import AGUIServer
    server = AGUIServer(bridge)
    await server.start(port=8787)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import time
from http import HTTPStatus

from agents.ag_ui_bridge import AGUIBridge, AGUIEvent, AGUIEventType

logger = logging.getLogger("ag-ui-server")


class AGUIServer:
  """Async HTTP server for AG-UI SSE protocol.

  Uses raw asyncio to avoid adding FastAPI/Starlette as a dependency.
  Handles SSE keep-alive, client reconnection via Last-Event-ID,
  and concurrent client connections.
  """

  def __init__(self, bridge: AGUIBridge | None = None) -> None:
    self.bridge = bridge or AGUIBridge()
    self._clients: list[asyncio.StreamWriter] = []
    self._server: asyncio.Server | None = None
    self._running = False

  async def start(self, host: str = "0.0.0.0", port: int = 8787) -> None:
    """Start the SSE server."""
    self._running = True
    self._server = await asyncio.start_server(self._handle_connection, host, port)
    logger.info("🌐 AG-UI SSE server listening on %s:%d", host, port)
    async with self._server:
      await self._server.serve_forever()

  async def stop(self) -> None:
    """Gracefully stop the server."""
    self._running = False
    if self._server:
      self._server.close()
      await self._server.wait_closed()
    for writer in self._clients:
      writer.close()
    self._clients.clear()
    logger.info("🛑 AG-UI SSE server stopped")

  async def _handle_connection(
    self,
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
  ) -> None:
    """Handle an incoming HTTP connection."""
    try:
      request_line = await asyncio.wait_for(reader.readline(), timeout=10)
      if not request_line:
        writer.close()
        return
      request_text = request_line.decode("utf-8", errors="replace").strip()
      # Parse basic HTTP request line
      parts = request_text.split(" ")
      method = parts[0] if len(parts) >= 1 else "GET"
      path = parts[1] if len(parts) >= 2 else "/"

      # Read headers (to extract Last-Event-ID)
      headers: dict[str, str] = {}
      while True:
        header_line = await asyncio.wait_for(reader.readline(), timeout=5)
        decoded = header_line.decode("utf-8", errors="replace").strip()
        if not decoded:
          break
        if ":" in decoded:
          key, val = decoded.split(":", 1)
          headers[key.strip().lower()] = val.strip()

      if method != "GET":
        await self._send_response(
          writer, HTTPStatus.METHOD_NOT_ALLOWED, {"error": "GET only"}
        )
        return

      if path == "/ag-ui/events":
        await self._handle_sse(writer, headers)
      elif path == "/ag-ui/state":
        await self._send_response(
          writer, HTTPStatus.OK, self.bridge.get_state_snapshot()
        )
      elif path == "/ag-ui/health":
        await self._send_response(
          writer,
          HTTPStatus.OK,
          {
            "status": "healthy",
            "server": "ag-ui",
            "uptime_events": self.bridge._event_counter,
            "timestamp": time.time(),
          },
        )
      else:
        await self._send_response(writer, HTTPStatus.NOT_FOUND, {"error": "Not found"})
    except (asyncio.TimeoutError, ConnectionError):
      pass
    except Exception as e:
      logger.warning("Connection error: %s", e)
    finally:
      try:
        writer.close()
        await writer.wait_closed()
      except Exception:
        pass

  async def _handle_sse(
    self,
    writer: asyncio.StreamWriter,
    headers: dict[str, str],
  ) -> None:
    """Handle SSE streaming connection."""
    # Send SSE headers
    response_header = (
      "HTTP/1.1 200 OK\r\n"
      "Content-Type: text/event-stream\r\n"
      "Cache-Control: no-cache\r\n"
      "Connection: keep-alive\r\n"
      "Access-Control-Allow-Origin: *\r\n"
      "\r\n"
    )
    writer.write(response_header.encode())
    await writer.drain()

    self._clients.append(writer)
    logger.info("📡 SSE client connected (total=%d)", len(self._clients))

    # Send backlog from Last-Event-ID
    last_id = int(headers.get("last-event-id", "0"))
    backlog = self.bridge.stream(since_id=last_id)
    for event in backlog:
      writer.write(event.to_sse().encode())
    if backlog:
      await writer.drain()

    # Keep-alive loop
    try:
      while self._running:
        # Send heartbeat every 15s
        heartbeat = f": heartbeat {int(time.time())}\n\n"
        writer.write(heartbeat.encode())
        await writer.drain()
        await asyncio.sleep(15)
    except (ConnectionError, BrokenPipeError):
      pass
    finally:
      if writer in self._clients:
        self._clients.remove(writer)
      logger.info("📡 SSE client disconnected (total=%d)", len(self._clients))

  async def broadcast(self, event: AGUIEvent) -> None:
    """Push an event to all connected SSE clients."""
    sse_data = event.to_sse().encode()
    disconnected: list[asyncio.StreamWriter] = []
    for client in self._clients:
      try:
        client.write(sse_data)
        await client.drain()
      except (ConnectionError, BrokenPipeError):
        disconnected.append(client)
    for client in disconnected:
      self._clients.remove(client)

  async def _send_response(
    self,
    writer: asyncio.StreamWriter,
    status: HTTPStatus,
    body: dict,
  ) -> None:
    """Send a JSON HTTP response."""
    body_bytes = json.dumps(body, indent=2).encode()
    header = (
      f"HTTP/1.1 {status.value} {status.phrase}\r\n"
      f"Content-Type: application/json\r\n"
      f"Content-Length: {len(body_bytes)}\r\n"
      f"Access-Control-Allow-Origin: *\r\n"
      f"\r\n"
    ).encode()
    writer.write(header + body_bytes)
    await writer.drain()


def main() -> None:
  """CLI entry point for standalone AG-UI server."""
  parser = argparse.ArgumentParser(description="AG-UI SSE Server")
  parser.add_argument("--port", type=int, default=8787, help="Port to listen on")
  parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
  args = parser.parse_args()

  logging.basicConfig(level=logging.INFO, format="%(name)s | %(message)s")
  bridge = AGUIBridge()
  server = AGUIServer(bridge)

  # Emit a startup event
  bridge.emit(
    AGUIEventType.SYSTEM_HEALTH, {"status": "server_started", "port": args.port}
  )

  try:
    asyncio.run(server.start(host=args.host, port=args.port))
  except KeyboardInterrupt:
    logger.info("Server shutdown requested")


if __name__ == "__main__":
  main()
