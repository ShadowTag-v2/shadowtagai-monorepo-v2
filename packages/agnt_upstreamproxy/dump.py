"""Prompt dump writer — AGNT_DUMP_PROMPTS disk logger.

When AGNT_DUMP_PROMPTS=1, writes all outbound LLM request payloads
to disk as JSONL for debugging/auditing. No network egress.
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any
import contextlib

logger = logging.getLogger(__name__)


class PromptDumper:
  """Writes outbound LLM payloads to disk when enabled.

  Activated by AGNT_DUMP_PROMPTS=1 env var. Writes to
  .beads/prompt_dump.jsonl by default.
  """

  __slots__ = ("_enabled", "_log_path", "_file")

  def __init__(self, log_dir: str | None = None) -> None:
    self._enabled = os.environ.get("AGNT_DUMP_PROMPTS", "0") == "1"
    if self._enabled:
      base = log_dir or os.path.join(os.getcwd(), ".beads")
      Path(base).mkdir(parents=True, exist_ok=True)
      self._log_path = os.path.join(base, "prompt_dump.jsonl")
    else:
      self._log_path = ""
    self._file = None

  @property
  def enabled(self) -> bool:
    return self._enabled

  def dump(self, url: str, payload: dict[str, Any]) -> None:
    """Write a request payload to the dump file."""
    if not self._enabled:
      return
    record = {
      "ts": time.time(),
      "url": url,
      "payload": payload,
    }
    try:
      if self._file is None:
        self._file = open(  # noqa: SIM115
          self._log_path, "a", encoding="utf-8"
        )
      self._file.write(json.dumps(record, default=str) + "\n")
      self._file.flush()
    except OSError as exc:
      logger.warning("Prompt dump failed: %s", exc)

  def close(self) -> None:
    """Close the dump file."""
    if self._file:
      with contextlib.suppress(OSError):
        self._file.close()
      self._file = None
