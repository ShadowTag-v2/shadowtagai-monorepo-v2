# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""LSP Client Service — Ported from Claude Code v2.1.91 lsp/LSPClient.ts.

JSON-RPC 2.0 based LSP client for subprocess language servers.

Reference: Claude Code v2.1.91 src/services/lsp/LSPClient.ts (448 lines)
"""

from __future__ import annotations

import json
import logging
import subprocess
import threading
from dataclasses import dataclass, field
from typing import Any
from collections.abc import Callable

logger = logging.getLogger(__name__)


def _encode_jsonrpc(
  method: str, params: Any = None, request_id: int | None = None
) -> bytes:
  msg: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
  if params is not None:
    msg["params"] = params
  if request_id is not None:
    msg["id"] = request_id
  body = json.dumps(msg).encode("utf-8")
  header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
  return header + body


@dataclass
class ServerCapabilities:
  hover_provider: bool = False
  definition_provider: bool = False
  references_provider: bool = False
  raw: dict[str, Any] = field(default_factory=dict)

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> ServerCapabilities:
    return cls(
      hover_provider=bool(data.get("hoverProvider")),
      definition_provider=bool(data.get("definitionProvider")),
      references_provider=bool(data.get("referencesProvider")),
      raw=data,
    )


class LSPClient:
  """LSP client wrapper for subprocess-based language servers."""

  def __init__(
    self, server_name: str, on_crash: Callable[[Exception], None] | None = None
  ) -> None:
    self.server_name = server_name
    self._on_crash = on_crash
    self._process: subprocess.Popen[bytes] | None = None
    self._is_initialized = False
    self._capabilities: ServerCapabilities | None = None
    self._request_id = 0
    self._pending_handlers: list[tuple[str, Callable[..., Any]]] = []
    self._lock = threading.Lock()

  @property
  def capabilities(self) -> ServerCapabilities | None:
    return self._capabilities

  @property
  def is_initialized(self) -> bool:
    return self._is_initialized

  def start(
    self,
    command: str,
    args: list[str] | None = None,
    *,
    env: dict[str, str] | None = None,
    cwd: str | None = None,
  ) -> None:
    import os

    full_env = {**os.environ, **(env or {})}
    self._process = subprocess.Popen(
      [command, *(args or [])],
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      env=full_env,
      cwd=cwd,
    )
    logger.debug(
      "LSP client started for %s (PID %d)", self.server_name, self._process.pid
    )

  def stop(self) -> None:
    proc = self._process
    if proc is None:
      return
    try:
      if proc.stdin and not proc.stdin.closed:
        self._request_id += 1
        proc.stdin.write(_encode_jsonrpc("shutdown", request_id=self._request_id))
        proc.stdin.flush()
        proc.stdin.write(_encode_jsonrpc("exit"))
        proc.stdin.flush()
    except (BrokenPipeError, OSError):
      pass
    try:
      proc.terminate()
      proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
      proc.kill()
    except OSError:
      pass
    self._process = None
    self._is_initialized = False
    self._capabilities = None

  def on_notification(self, method: str, handler: Callable[..., Any]) -> None:
    self._pending_handlers.append((method, handler))

  def cleanup(self) -> None:
    self.stop()
