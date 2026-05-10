# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Session Memory — Threshold-gated session note extraction.

Ported from src/services/SessionMemory/ (sessionMemory.ts + sessionMemoryUtils.ts).

Thresholds (matching upstream defaults):
  - minimumMessageTokensToInit: 10,000 tokens
  - minimumTokensBetweenUpdate: 5,000 token growth
  - toolCallsBetweenUpdates: 3 tool calls
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

EXTRACTION_WAIT_TIMEOUT_S = 15.0
EXTRACTION_STALE_THRESHOLD_S = 60.0


@dataclass
class SessionMemoryConfig:
  """Extraction threshold configuration."""

  minimum_message_tokens_to_init: int = 10_000
  minimum_tokens_between_update: int = 5_000
  tool_calls_between_updates: int = 3


@dataclass
class ExtractionState:
  """Mutable state for extraction lifecycle."""

  config: SessionMemoryConfig = field(default_factory=SessionMemoryConfig)
  last_summarized_message_id: str | None = None
  last_memory_message_uuid: str | None = None
  tokens_at_last_extraction: int = 0
  initialized: bool = False
  extraction_started_at: float | None = None
  _lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False)

  def mark_started(self) -> None:
    self.extraction_started_at = time.monotonic()

  def mark_completed(self) -> None:
    self.extraction_started_at = None

  @property
  def is_extracting(self) -> bool:
    return self.extraction_started_at is not None

  def record_token_count(self, current_tokens: int) -> None:
    self.tokens_at_last_extraction = current_tokens

  def has_met_init_threshold(self, current_tokens: int) -> bool:
    return current_tokens >= self.config.minimum_message_tokens_to_init

  def has_met_update_threshold(self, current_tokens: int) -> bool:
    growth = current_tokens - self.tokens_at_last_extraction
    return growth >= self.config.minimum_tokens_between_update

  def reset(self) -> None:
    self.last_summarized_message_id = None
    self.last_memory_message_uuid = None
    self.tokens_at_last_extraction = 0
    self.initialized = False
    self.extraction_started_at = None
    self.config = SessionMemoryConfig()


def count_tool_calls_since(
  messages: list[dict[str, Any]], since_uuid: str | None
) -> int:
  """Count tool_use blocks in assistant messages after cursor UUID."""
  count = 0
  found = since_uuid is None
  for msg in messages:
    if not found:
      if msg.get("uuid") == since_uuid:
        found = True
      continue
    if msg.get("type") != "assistant":
      continue
    content = msg.get("content", [])
    if isinstance(content, list):
      count += sum(
        1 for b in content if isinstance(b, dict) and b.get("type") == "tool_use"
      )
  return count


def should_extract_memory(
  messages: list[dict[str, Any]],
  state: ExtractionState,
  current_token_count: int,
) -> bool:
  """Check if session memory extraction should run."""
  if not state.initialized:
    if not state.has_met_init_threshold(current_token_count):
      return False
    state.initialized = True

  has_met_tokens = state.has_met_update_threshold(current_token_count)
  tool_calls = count_tool_calls_since(messages, state.last_memory_message_uuid)
  has_met_tools = tool_calls >= state.config.tool_calls_between_updates

  has_tools_last = _has_tool_calls_in_last_turn(messages)

  should = (has_met_tokens and has_met_tools) or (has_met_tokens and not has_tools_last)
  if should and messages:
    last = messages[-1]
    if last.get("uuid"):
      state.last_memory_message_uuid = last["uuid"]
  return should


def _has_tool_calls_in_last_turn(messages: list[dict[str, Any]]) -> bool:
  for msg in reversed(messages):
    if msg.get("type") == "assistant":
      content = msg.get("content", [])
      if isinstance(content, list):
        return any(isinstance(b, dict) and b.get("type") == "tool_use" for b in content)
      return False
  return False


class SessionMemoryManager:
  """Manages session memory extraction lifecycle."""

  def __init__(
    self,
    *,
    memory_dir: Path | None = None,
    state: ExtractionState | None = None,
  ) -> None:
    self._memory_dir = memory_dir or Path.home() / ".claude" / "memory"
    self._state = state or ExtractionState()

  @property
  def state(self) -> ExtractionState:
    return self._state

  @property
  def memory_path(self) -> Path:
    return self._memory_dir / "session_memory.md"

  def configure(self, config: SessionMemoryConfig) -> None:
    self._state.config = config

  def should_extract(self, messages: list[dict[str, Any]], token_count: int) -> bool:
    return should_extract_memory(messages, self._state, token_count)

  async def extract(self, messages: list[dict[str, Any]], token_count: int) -> bool:
    """Run extraction with sequential locking. Returns True on success."""
    async with self._state._lock:
      self._state.mark_started()
      try:
        _current = await self._read_memory()
        logger.debug(
          "Session memory extraction: %d msgs, %d tokens",
          len(messages),
          token_count,
        )
        self._state.record_token_count(token_count)
        if messages:
          last = messages[-1]
          if last.get("uuid"):
            self._state.last_summarized_message_id = last["uuid"]
        return True
      except Exception:
        logger.debug("Extraction error", exc_info=True)
        return False
      finally:
        self._state.mark_completed()

  async def wait_for_extraction(
    self, timeout: float = EXTRACTION_WAIT_TIMEOUT_S
  ) -> None:
    deadline = time.monotonic() + timeout
    while self._state.is_extracting:
      if self._state.extraction_started_at is not None:
        age = time.monotonic() - self._state.extraction_started_at
        if age > EXTRACTION_STALE_THRESHOLD_S:
          return
      if time.monotonic() > deadline:
        return
      await asyncio.sleep(1.0)

  async def get_memory_content(self) -> str | None:
    content = await self._read_memory()
    return content or None

  async def _read_memory(self) -> str:
    try:
      return self.memory_path.read_text(encoding="utf-8")
    except FileNotFoundError:
      return ""

  def reset(self) -> None:
    self._state.reset()
