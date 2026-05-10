"""Token estimation for context budget management.

Ported from Claude Code `tokenEstimation.ts`.
Provider-agnostic rough estimation with file-type-aware ratios
and per-block content analysis.

Architecture:
  - `rough_token_estimate()` → fast chars/bytes heuristic
  - `estimate_for_file_type()` → extension-aware (JSON denser)
  - `estimate_for_content_block()` → structured content blocks
  - `estimate_for_messages()` → full message array estimation
  - `TokenBudgetTracker` → running budget with threshold alerts
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)

# --- Constants ---

# Default bytes-per-token ratio (BPE tokenizers average ~4 bytes/token for English)
DEFAULT_BYTES_PER_TOKEN = 4

# File-type specific ratios
_FILE_TYPE_RATIOS: dict[str, int] = {
  "json": 2,
  "jsonl": 2,
  "jsonc": 2,
  # XML/HTML have lots of single-char tokens (<, >, /, =)
  "xml": 3,
  "html": 3,
  "svg": 3,
  # YAML is closer to natural language
  "yaml": 4,
  "yml": 4,
  # Code is typically 3-4 bytes/token
  "py": 4,
  "ts": 4,
  "js": 4,
  "rs": 4,
  "go": 4,
  "cs": 4,
}

# Conservative estimate for image/document blocks
# Matches Claude's vision pricing: (width * height) / 750
# Capped at ~2000 for typical documents
IMAGE_TOKEN_ESTIMATE = 2000


class ContentBlockType(StrEnum):
  """Types of content blocks in a message."""

  TEXT = "text"
  IMAGE = "image"
  DOCUMENT = "document"
  TOOL_USE = "tool_use"
  TOOL_RESULT = "tool_result"
  THINKING = "thinking"
  REDACTED_THINKING = "redacted_thinking"


@dataclass
class ContentBlock:
  """A content block within a message.

  Attributes:
      block_type: The type of content block.
      text: Text content (for text, thinking blocks).
      data: Raw data (for redacted_thinking, image source).
      name: Tool name (for tool_use blocks).
      input_data: Tool input (for tool_use blocks).
      content: Nested content (for tool_result blocks).
  """

  block_type: ContentBlockType
  text: str = ""
  data: str = ""
  name: str = ""
  input_data: Any = None
  content: list[ContentBlock] | str | None = None


@dataclass
class Message:
  """A conversation message for token estimation.

  Attributes:
      role: 'user', 'assistant', or 'system'.
      content: String or list of ContentBlocks.
  """

  role: str
  content: str | list[ContentBlock]


@dataclass
class TokenBudget:
  """Token budget state with threshold tracking.

  Attributes:
      max_tokens: Maximum allowed input tokens.
      current_tokens: Current estimated token count.
      warning_threshold: Fraction (0-1) at which to warn.
      critical_threshold: Fraction (0-1) at which to trigger compaction.
  """

  max_tokens: int
  current_tokens: int = 0
  warning_threshold: float = 0.75
  critical_threshold: float = 0.90

  @property
  def utilization(self) -> float:
    """Current utilization as a fraction."""
    if self.max_tokens == 0:
      return 0.0
    return self.current_tokens / self.max_tokens

  @property
  def remaining(self) -> int:
    """Remaining tokens before max."""
    return max(0, self.max_tokens - self.current_tokens)

  @property
  def is_warning(self) -> bool:
    """True if utilization exceeds warning threshold."""
    return self.utilization >= self.warning_threshold

  @property
  def is_critical(self) -> bool:
    """True if utilization exceeds critical threshold."""
    return self.utilization >= self.critical_threshold


@dataclass
class TokenBudgetTracker:
  """Running token budget tracker with auto-alert capabilities.

  Tracks token counts across messages, tools, and system prompts.
  Emits warnings when thresholds are crossed.

  Attributes:
      budget: The token budget configuration and state.
      message_tokens: Tokens from conversation messages.
      tool_tokens: Tokens from tool definitions.
      system_tokens: Tokens from system prompt.
      history: List of (label, token_count) entries for audit.
  """

  budget: TokenBudget
  message_tokens: int = 0
  tool_tokens: int = 0
  system_tokens: int = 0
  history: list[tuple[str, int]] = field(default_factory=list)

  def add_messages(self, messages: list[Message], label: str = "messages") -> int:
    """Estimate and add token count for messages.

    Args:
        messages: List of messages to estimate.
        label: Label for audit history.

    Returns:
        Estimated token count for these messages.
    """
    tokens = estimate_for_messages(messages)
    self.message_tokens += tokens
    self.budget.current_tokens = self._total()
    self.history.append((label, tokens))
    self._check_thresholds(label)
    return tokens

  def add_system_prompt(self, prompt: str, label: str = "system") -> int:
    """Estimate and add token count for system prompt.

    Args:
        prompt: System prompt text.
        label: Label for audit history.

    Returns:
        Estimated token count.
    """
    tokens = rough_token_estimate(prompt)
    self.system_tokens += tokens
    self.budget.current_tokens = self._total()
    self.history.append((label, tokens))
    self._check_thresholds(label)
    return tokens

  def add_tools(
    self, tool_definitions: list[dict[str, Any]], label: str = "tools"
  ) -> int:
    """Estimate token count for tool definitions.

    Args:
        tool_definitions: List of tool definition dicts.
        label: Label for audit history.

    Returns:
        Estimated token count.
    """
    serialized = _safe_json_serialize(tool_definitions)
    tokens = rough_token_estimate(serialized)
    self.tool_tokens += tokens
    self.budget.current_tokens = self._total()
    self.history.append((label, tokens))
    self._check_thresholds(label)
    return tokens

  def reset(self) -> None:
    """Reset all token counts to zero."""
    self.message_tokens = 0
    self.tool_tokens = 0
    self.system_tokens = 0
    self.budget.current_tokens = 0
    self.history.clear()

  def summary(self) -> dict[str, Any]:
    """Return a summary of the current budget state.

    Returns:
        Dictionary with utilization metrics.
    """
    return {
      "max_tokens": self.budget.max_tokens,
      "current_tokens": self.budget.current_tokens,
      "utilization": round(self.budget.utilization, 3),
      "remaining": self.budget.remaining,
      "breakdown": {
        "messages": self.message_tokens,
        "tools": self.tool_tokens,
        "system": self.system_tokens,
      },
      "is_warning": self.budget.is_warning,
      "is_critical": self.budget.is_critical,
    }

  def _total(self) -> int:
    return self.message_tokens + self.tool_tokens + self.system_tokens

  def _check_thresholds(self, label: str) -> None:
    if self.budget.is_critical:
      logger.warning(
        "Token budget CRITICAL after '%s': %d/%d (%.1f%%)",
        label,
        self.budget.current_tokens,
        self.budget.max_tokens,
        self.budget.utilization * 100,
      )
    elif self.budget.is_warning:
      logger.info(
        "Token budget warning after '%s': %d/%d (%.1f%%)",
        label,
        self.budget.current_tokens,
        self.budget.max_tokens,
        self.budget.utilization * 100,
      )


# --- Core Estimation Functions ---


def rough_token_estimate(
  content: str, bytes_per_token: int = DEFAULT_BYTES_PER_TOKEN
) -> int:
  """Estimate token count from character length.

  Uses a simple bytes-per-token heuristic. BPE tokenizers
  average ~4 bytes per token for English text.

  Args:
      content: The text to estimate tokens for.
      bytes_per_token: Average bytes per token (default 4).

  Returns:
      Estimated token count.
  """
  if not content:
    return 0
  return round(len(content) / bytes_per_token)


def bytes_per_token_for_file_type(file_extension: str) -> int:
  """Get the bytes-per-token ratio for a file type.

  Dense formats like JSON have many single-character tokens
  ({, }, :, etc.) making the real ratio closer to 2.

  Args:
      file_extension: File extension without dot (e.g., 'json', 'py').

  Returns:
      Bytes-per-token ratio for the file type.
  """
  ext = file_extension.lstrip(".")
  return _FILE_TYPE_RATIOS.get(ext, DEFAULT_BYTES_PER_TOKEN)


def estimate_for_file_type(content: str, file_extension: str) -> int:
  """Estimate tokens using file-type-aware ratio.

  Important when API-based counting is unavailable — an underestimate
  can let oversized tool results slip into the conversation.

  Args:
      content: File content.
      file_extension: File extension (with or without dot).

  Returns:
      Estimated token count.
  """
  return rough_token_estimate(
    content,
    bytes_per_token_for_file_type(file_extension),
  )


def estimate_for_content_block(block: ContentBlock) -> int:
  """Estimate tokens for a single content block.

  Handles different block types with appropriate heuristics:
  - text: standard rough estimation
  - image/document: conservative 2000 tokens
  - tool_use: name + serialized input
  - tool_result: recursive on nested content
  - thinking: standard rough estimation

  Args:
      block: Content block to estimate.

  Returns:
      Estimated token count.
  """
  match block.block_type:
    case ContentBlockType.TEXT:
      return rough_token_estimate(block.text)

    case ContentBlockType.IMAGE | ContentBlockType.DOCUMENT:
      return IMAGE_TOKEN_ESTIMATE

    case ContentBlockType.TOOL_USE:
      serialized_input = _safe_json_serialize(block.input_data or {})
      return rough_token_estimate(block.name + serialized_input)

    case ContentBlockType.TOOL_RESULT:
      if isinstance(block.content, str):
        return rough_token_estimate(block.content)
      if isinstance(block.content, list):
        return sum(estimate_for_content_block(b) for b in block.content)
      return 0

    case ContentBlockType.THINKING:
      return rough_token_estimate(block.text)

    case ContentBlockType.REDACTED_THINKING:
      return rough_token_estimate(block.data)

    case _:
      # Unknown block type — serialize and estimate
      serialized = _safe_json_serialize(
        {"type": block.block_type, "text": block.text, "data": block.data}
      )
      return rough_token_estimate(serialized)


def estimate_for_message(message: Message) -> int:
  """Estimate tokens for a single message.

  Args:
      message: Message with role and content.

  Returns:
      Estimated token count.
  """
  # ~4 tokens for message framing (role, delimiters)
  overhead = 4

  if isinstance(message.content, str):
    return overhead + rough_token_estimate(message.content)

  if isinstance(message.content, list):
    return overhead + sum(
      estimate_for_content_block(block) for block in message.content
    )

  return overhead


def estimate_for_messages(messages: list[Message]) -> int:
  """Estimate total tokens for a list of messages.

  Args:
      messages: List of conversation messages.

  Returns:
      Total estimated token count.
  """
  return sum(estimate_for_message(m) for m in messages)


# --- Utilities ---


def _safe_json_serialize(value: Any) -> str:
  """Safely serialize a value to JSON string.

  Args:
      value: Value to serialize.

  Returns:
      JSON string, or fallback representation on failure.
  """
  try:
    return json.dumps(value, separators=(",", ":"), default=str)
  except TypeError, ValueError:
    return "[unable to serialize]"
