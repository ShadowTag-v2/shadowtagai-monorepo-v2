# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Extract Memories Service — Durable memory extraction from sessions.

Ported from Claude Code v2.1.91 src/services/extractMemories/.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
import contextlib

logger = logging.getLogger(__name__)


@dataclass
class ExtractMemoriesConfig:
  min_messages_for_first_extraction: int = 6
  min_messages_between_extractions: int = 4
  cooldown_seconds: float = 30.0
  max_memory_entries: int = 100
  cadence_multiplier: float = 1.0
  generate_index: bool = False
  team_memory_enabled: bool = False


READ_ONLY_TOOLS = frozenset({"file_read", "grep", "glob", "repl"})
WRITE_TOOLS = frozenset({"file_edit", "file_write"})


@dataclass
class ExtractionState:
  last_extraction_uuid: str | None = None
  last_extraction_time: float = 0.0
  extraction_count: int = 0
  total_messages_processed: int = 0


@dataclass
class MemoryMessage:
  uuid: str
  type: str
  content: str = ""
  tool_calls: list[dict] = field(default_factory=list)


def is_model_visible(msg: MemoryMessage) -> bool:
  return msg.type in ("user", "assistant")


def count_model_visible_since(
  messages: list[MemoryMessage], since_uuid: str | None
) -> int:
  if since_uuid is None:
    return sum(1 for m in messages if is_model_visible(m))
  found_start = False
  count = 0
  for msg in messages:
    if not found_start:
      if msg.uuid == since_uuid:
        found_start = True
      continue
    if is_model_visible(msg):
      count += 1
  if not found_start:
    return sum(1 for m in messages if is_model_visible(m))
  return count


def can_use_tool_for_extraction(
  tool_name: str, tool_input: dict, memory_dir: str
) -> tuple[bool, str]:
  if tool_name in READ_ONLY_TOOLS:
    return True, "read-only tool"
  if tool_name == "bash":
    return False, "bash write commands not allowed"
  if tool_name in WRITE_TOOLS:
    fp = tool_input.get("file_path", "")
    if fp and fp.startswith(memory_dir):
      return True, "write to memory directory"
    return False, f"write outside memory: {fp}"
  return False, f"unknown tool: {tool_name}"


class ExtractMemoriesService:
  def __init__(
    self, memory_dir: str | Path, config: ExtractMemoriesConfig | None = None
  ):
    self.memory_dir = Path(memory_dir)
    self.config = config or ExtractMemoriesConfig()
    self.state = ExtractionState()

  def should_extract(self, messages: list[MemoryMessage]) -> bool:
    visible = count_model_visible_since(messages, self.state.last_extraction_uuid)
    threshold = (
      self.config.min_messages_for_first_extraction
      if self.state.extraction_count == 0
      else int(
        self.config.min_messages_between_extractions * self.config.cadence_multiplier
      )
    )
    if visible < threshold:
      return False
    now = time.monotonic()
    return not now - self.state.last_extraction_time < self.config.cooldown_seconds

  def mark_extraction_complete(self, messages: list[MemoryMessage]) -> None:
    self.state.extraction_count += 1
    self.state.last_extraction_time = time.monotonic()
    if messages:
      self.state.last_extraction_uuid = messages[-1].uuid

  def scan_memory_files(self) -> list[dict]:
    entries = []
    if not self.memory_dir.exists():
      return entries
    for p in sorted(self.memory_dir.iterdir()):
      if p.is_file() and p.suffix == ".md":
        with contextlib.suppress(OSError):
          entries.append({"path": str(p), "name": p.stem, "size": p.stat().st_size})
    return entries

  def reset(self) -> None:
    self.state = ExtractionState()


def health_check() -> bool:
  return True
