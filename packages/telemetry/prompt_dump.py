# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AGNT Prompt Dump Capability — P4.2 Implementation.

Ported from: api/dumpPrompts.ts (3 ant gates)
Reference: AGNT STATE B Spec P4.2

When AGNT_DUMP_PROMPTS=1, writes full Gemini API payloads to
brain/{conv}/prompt_dumps/ for debugging and analysis.

Usage:
    from telemetry.prompt_dump import PromptDumper
    dumper = PromptDumper(dump_dir=Path("brain/conv-123/prompt_dumps"))
    dumper.dump_request(model, messages, params)
    dumper.dump_response(response_data)
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class PromptDumper:
  """Records full API payloads for debugging.

  Gated by AGNT_DUMP_PROMPTS env var or explicit enable.
  """

  def __init__(self, dump_dir: Path | None = None, enabled: bool | None = None) -> None:
    from config.feature_flags import flags

    self._enabled = enabled if enabled is not None else flags.is_enabled("dump_prompts")
    self._dump_dir = dump_dir
    self._sequence = 0

  @property
  def is_enabled(self) -> bool:
    return self._enabled

  def dump_request(
    self, model: str, messages: list[dict], params: dict[str, Any] | None = None
  ) -> Path | None:
    """Dump an outgoing API request."""
    if not self._enabled or not self._dump_dir:
      return None
    self._sequence += 1
    payload = {
      "type": "request",
      "sequence": self._sequence,
      "timestamp": time.time(),
      "model": model,
      "message_count": len(messages),
      "messages": messages,
      "params": params or {},
    }
    return self._write(f"req_{self._sequence:04d}.json", payload)

  def dump_response(
    self, response: dict[str, Any], latency_ms: float = 0
  ) -> Path | None:
    """Dump an incoming API response."""
    if not self._enabled or not self._dump_dir:
      return None
    payload = {
      "type": "response",
      "sequence": self._sequence,
      "timestamp": time.time(),
      "latency_ms": latency_ms,
      "response": response,
    }
    return self._write(f"res_{self._sequence:04d}.json", payload)

  def _write(self, filename: str, data: dict) -> Path:
    """Write a dump file."""
    self._dump_dir.mkdir(parents=True, exist_ok=True)
    path = self._dump_dir / filename
    with open(path, "w") as f:
      json.dump(data, f, indent=2, default=str)
    logger.debug("Prompt dump written: %s", path)
    return path
