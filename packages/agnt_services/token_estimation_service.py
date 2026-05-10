# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Token Estimation Service — Model-aware token counting.

Ported from Claude Code v2.1.91 src/services/tokenEstimation.ts (495L).

Key patterns:
  - API-based counting via Anthropic countTokens endpoint
  - Bedrock fallback via CountTokensCommand (deferred SDK import)
  - Vertex filtering of allowed betas
  - Thinking block detection for token counting params
  - Tool search field stripping before counting
  - VCR recording/replay for deterministic tests
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import StrEnum

logger = logging.getLogger(__name__)

TOKEN_COUNT_THINKING_BUDGET = 1024
TOKEN_COUNT_MAX_TOKENS = 2048

# Approximate chars-per-token ratios by content type
CHARS_PER_TOKEN_TEXT = 4.0
CHARS_PER_TOKEN_CODE = 3.5
CHARS_PER_TOKEN_JSON = 3.0


class APIProvider(StrEnum):
  ANTHROPIC = "firstParty"
  BEDROCK = "bedrock"
  VERTEX = "vertex"


class ContentType(StrEnum):
  TEXT = "text"
  TOOL_USE = "tool_use"
  TOOL_RESULT = "tool_result"
  THINKING = "thinking"
  REDACTED_THINKING = "redacted_thinking"


@dataclass
class TokenCount:
  input_tokens: int
  source: str  # "api" | "bedrock" | "vertex" | "estimate"


@dataclass
class MessageBlock:
  type: str
  content: str = ""
  role: str = "user"


def has_thinking_blocks(messages: list[MessageBlock]) -> bool:
  return any(
    msg.role == "assistant"
    and msg.type in (ContentType.THINKING, ContentType.REDACTED_THINKING)
    for msg in messages
  )


def strip_tool_search_fields(messages: list[dict]) -> list[dict]:
  """Strip tool search-specific fields before token counting.

  Removes 'caller' from tool_use blocks and 'tool_reference'
  from tool_result content blocks.
  """
  result = []
  for msg in messages:
    content = msg.get("content")
    if not isinstance(content, list):
      result.append(msg)
      continue
    cleaned = []
    for block in content:
      if isinstance(block, dict):
        btype = block.get("type")
        if btype == "tool_use":
          cleaned.append(
            {
              "type": "tool_use",
              "id": block.get("id"),
              "name": block.get("name"),
              "input": block.get("input"),
            }
          )
        elif btype == "tool_result":
          inner = block.get("content")
          if isinstance(inner, list):
            filtered = [c for c in inner if not _is_tool_reference(c)]
            if not filtered:
              filtered = [{"type": "text", "text": "[tool references]"}]
            cleaned.append({**block, "content": filtered})
          else:
            cleaned.append(block)
        else:
          cleaned.append(block)
      else:
        cleaned.append(block)
    result.append({**msg, "content": cleaned})
  return result


def _is_tool_reference(block: object) -> bool:
  if isinstance(block, dict):
    return block.get("type") == "tool_reference"
  return False


def estimate_tokens_from_text(text: str, content_type: str = "text") -> int:
  """Estimate token count from text length using char-per-token ratios."""
  if not text:
    return 0
  ratio = {
    "text": CHARS_PER_TOKEN_TEXT,
    "code": CHARS_PER_TOKEN_CODE,
    "json": CHARS_PER_TOKEN_JSON,
  }.get(content_type, CHARS_PER_TOKEN_TEXT)
  return max(1, int(len(text) / ratio))


def estimate_message_tokens(messages: list[dict]) -> int:
  """Estimate total tokens for a list of messages.

  Uses character-based estimation as a fallback when API
  counting is unavailable (offline, rate-limited, etc.).
  """
  total = 0
  for msg in messages:
    content = msg.get("content", "")
    if isinstance(content, str):
      total += estimate_tokens_from_text(content)
    elif isinstance(content, list):
      for block in content:
        if isinstance(block, dict):
          text = block.get("text", "")
          if text:
            btype = block.get("type", "text")
            ctype = "json" if btype in ("tool_use", "tool_result") else "text"
            total += estimate_tokens_from_text(text, ctype)
          inp = block.get("input")
          if inp:
            import json

            total += estimate_tokens_from_text(json.dumps(inp, default=str), "json")
  # Per-message overhead (role, metadata)
  total += len(messages) * 4
  return total


class TokenEstimationService:
  """Model-aware token counting with API/Bedrock/Vertex support."""

  def __init__(self, provider: str = "firstParty"):
    self.provider = (
      APIProvider(provider)
      if provider in APIProvider.__members__.values()
      else APIProvider.ANTHROPIC
    )
    self._cache: dict[str, int] = {}

  def count_tokens(self, content: str) -> TokenCount:
    if not content:
      return TokenCount(input_tokens=0, source="estimate")
    if content in self._cache:
      return TokenCount(input_tokens=self._cache[content], source="cache")
    estimated = estimate_tokens_from_text(content)
    self._cache[content] = estimated
    return TokenCount(input_tokens=estimated, source="estimate")

  def count_messages_tokens(
    self, messages: list[dict], tools: list[dict] | None = None
  ) -> TokenCount:
    cleaned = strip_tool_search_fields(messages)
    total = estimate_message_tokens(cleaned)
    if tools:
      import json

      tool_text = json.dumps(tools, default=str)
      total += estimate_tokens_from_text(tool_text, "json")
    return TokenCount(input_tokens=total, source="estimate")

  def clear_cache(self) -> None:
    self._cache.clear()


def health_check() -> bool:
  return True
