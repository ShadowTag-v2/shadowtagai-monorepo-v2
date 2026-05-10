# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""P5.4: Context Decay Warning System.

Monitors three orthogonal decay vectors and emits structured warnings:
  1. File reads exceeding 2000 lines → content overload warning
  2. Tool results exceeding 50K chars → result bloat warning
  3. Context window below 20% remaining → compaction urgency warning

Additional monitors:
  - Token count absolute threshold
  - Turn count threshold
  - Rolling read-size accumulator

Ported from Claude Code's contextCompaction.ts decay detection.
Integration: Called by the ContextCompactor and ClassifiedGateway
after each tool execution to check if auto-compaction should trigger.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# --- Thresholds ---

# P5.4 Spec thresholds
FILE_READ_LINE_THRESHOLD = 2000
TOOL_RESULT_CHAR_THRESHOLD = 50_000
CONTEXT_REMAINING_PERCENT_THRESHOLD = 20

# Legacy thresholds (kept for backward compat)
DEFAULT_TOKEN_THRESHOLD = 20_000
DEFAULT_TURN_THRESHOLD = 50


class DecaySeverity:
  """Warning severity levels."""

  INFO = "INFO"  # Advisory, no action needed
  WARNING = "WARNING"  # Should consider compaction
  CRITICAL = "CRITICAL"  # Must compact immediately


@dataclass
class DecayWarning:
  """A structured decay warning."""

  vector: str  # e.g., "file_read_oversize", "context_remaining_low"
  severity: str  # DecaySeverity value
  message: str
  value: int | float = 0
  threshold: int | float = 0

  def __str__(self) -> str:
    return f"[{self.severity}] {self.vector}: {self.message}"


@dataclass
class DecayCheckResult:
  """Result of a comprehensive decay check."""

  warnings: list[DecayWarning] = field(default_factory=list)
  should_compact: bool = False
  should_truncate_result: bool = False

  @property
  def has_warnings(self) -> bool:
    return len(self.warnings) > 0

  @property
  def max_severity(self) -> str:
    if not self.warnings:
      return DecaySeverity.INFO
    severities = [w.severity for w in self.warnings]
    if DecaySeverity.CRITICAL in severities:
      return DecaySeverity.CRITICAL
    if DecaySeverity.WARNING in severities:
      return DecaySeverity.WARNING
    return DecaySeverity.INFO

  def format_warnings(self) -> str:
    """Format all warnings into a single injection string."""
    if not self.warnings:
      return ""
    parts = [str(w) for w in self.warnings]
    return "<CONTEXT_DECAY_WARNING>\n" + "\n".join(parts) + "\n</CONTEXT_DECAY_WARNING>"


class ContextDecayMonitor:
  """Monitors context health and emits decay warnings.

  Tracks three P5.4 vectors plus legacy token/turn thresholds.
  Designed to be called after every tool execution.
  """

  def __init__(
    self,
    token_threshold: int = DEFAULT_TOKEN_THRESHOLD,
    turn_threshold: int = DEFAULT_TURN_THRESHOLD,
    max_context_tokens: int = 1_000_000,
  ) -> None:
    self.token_threshold = token_threshold
    self.turn_threshold = turn_threshold
    self.max_context_tokens = max_context_tokens

    # Rolling accumulators
    self._total_file_lines_read: int = 0
    self._total_tool_result_chars: int = 0

  # --- Public API ---

  def check_context_health(
    self,
    current_tokens: int,
    current_turns: int,
  ) -> str | None:
    """Legacy API: Check basic token/turn thresholds.

    Returns a warning string if thresholds are crossed, else None.
    Kept for backward compatibility with existing callers.
    """
    result = self.check_decay(
      current_tokens=current_tokens,
      current_turns=current_turns,
    )
    if result.has_warnings:
      return result.format_warnings()
    return None

  def check_decay(
    self,
    current_tokens: int = 0,
    current_turns: int = 0,
    file_read_lines: int = 0,
    tool_result_chars: int = 0,
  ) -> DecayCheckResult:
    """Comprehensive decay check across all vectors.

    Args:
        current_tokens: Current context window token count.
        current_turns: Number of conversation turns so far.
        file_read_lines: Lines returned by the most recent file read.
        tool_result_chars: Characters in the most recent tool result.

    Returns:
        DecayCheckResult with warnings and compaction recommendations.
    """
    result = DecayCheckResult()

    # --- Vector 1: File read oversize ---
    if file_read_lines > FILE_READ_LINE_THRESHOLD:
      severity = (
        DecaySeverity.CRITICAL
        if file_read_lines > FILE_READ_LINE_THRESHOLD * 3
        else DecaySeverity.WARNING
      )
      result.warnings.append(
        DecayWarning(
          vector="file_read_oversize",
          severity=severity,
          message=(
            f"File read returned {file_read_lines} lines (threshold: {FILE_READ_LINE_THRESHOLD}). Consider reading specific line ranges."
          ),
          value=file_read_lines,
          threshold=FILE_READ_LINE_THRESHOLD,
        )
      )
    self._total_file_lines_read += file_read_lines

    # --- Vector 2: Tool result bloat ---
    if tool_result_chars > TOOL_RESULT_CHAR_THRESHOLD:
      severity = (
        DecaySeverity.CRITICAL
        if tool_result_chars > TOOL_RESULT_CHAR_THRESHOLD * 3
        else DecaySeverity.WARNING
      )
      result.warnings.append(
        DecayWarning(
          vector="tool_result_bloat",
          severity=severity,
          message=(
            f"Tool result is {tool_result_chars:,} chars "
            f"(threshold: {TOOL_RESULT_CHAR_THRESHOLD:,}). "
            "Result should be truncated or summarized."
          ),
          value=tool_result_chars,
          threshold=TOOL_RESULT_CHAR_THRESHOLD,
        )
      )
      result.should_truncate_result = True
    self._total_tool_result_chars += tool_result_chars

    # --- Vector 3: Context window remaining ---
    if self.max_context_tokens > 0 and current_tokens > 0:
      remaining_pct = (
        (self.max_context_tokens - current_tokens) / self.max_context_tokens
      ) * 100
      if remaining_pct < CONTEXT_REMAINING_PERCENT_THRESHOLD:
        severity = (
          DecaySeverity.CRITICAL if remaining_pct < 10 else DecaySeverity.WARNING
        )
        result.warnings.append(
          DecayWarning(
            vector="context_remaining_low",
            severity=severity,
            message=(
              f"Context window {remaining_pct:.1f}% remaining "
              f"({current_tokens:,}/{self.max_context_tokens:,} tokens). "
              "Trigger compaction immediately."
            ),
            value=remaining_pct,
            threshold=CONTEXT_REMAINING_PERCENT_THRESHOLD,
          )
        )
        result.should_compact = True

    # --- Legacy: Token count absolute threshold ---
    if (
      current_tokens >= self.token_threshold
      and current_tokens > 0
      and not any(w.vector == "context_remaining_low" for w in result.warnings)
    ):
      result.warnings.append(
        DecayWarning(
          vector="token_count_high",
          severity=DecaySeverity.WARNING,
          message=(
            f"Tokens ({current_tokens:,}) exceed threshold ({self.token_threshold:,})."
          ),
          value=current_tokens,
          threshold=self.token_threshold,
        )
      )

    # --- Legacy: Turn count threshold ---
    if current_turns >= self.turn_threshold:
      result.warnings.append(
        DecayWarning(
          vector="turn_count_high",
          severity=DecaySeverity.WARNING,
          message=(
            f"Turns ({current_turns}) exceed threshold ({self.turn_threshold})."
          ),
          value=current_turns,
          threshold=self.turn_threshold,
        )
      )

    # Log warnings
    for w in result.warnings:
      if w.severity == DecaySeverity.CRITICAL:
        logger.warning("Context decay CRITICAL: %s", w.message)
      elif w.severity == DecaySeverity.WARNING:
        logger.info("Context decay WARNING: %s", w.message)

    return result

  def check_file_read(self, lines_returned: int) -> DecayCheckResult:
    """Convenience: check after a file read operation."""
    return self.check_decay(file_read_lines=lines_returned)

  def check_tool_result(self, result_chars: int) -> DecayCheckResult:
    """Convenience: check after receiving a tool result."""
    return self.check_decay(tool_result_chars=result_chars)

  def reset_accumulators(self) -> None:
    """Reset rolling accumulators (call between sessions)."""
    self._total_file_lines_read = 0
    self._total_tool_result_chars = 0

  @property
  def total_file_lines_read(self) -> int:
    """Total file lines read in this session."""
    return self._total_file_lines_read

  @property
  def total_tool_result_chars(self) -> int:
    """Total tool result characters in this session."""
    return self._total_tool_result_chars
