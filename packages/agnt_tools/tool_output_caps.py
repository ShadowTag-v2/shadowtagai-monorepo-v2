# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tool Output Caps — P0 #4 from Kairos Ultraplan.

Ported from: Claude Code src/services/toolLimits.ts + apiLimits.ts
Reference: Kairos Ultraplan lines 1304-1324

Enforces hard caps on tool output to prevent context window bloat:
  - DEFAULT_MAX_RESULT_SIZE_CHARS = 50,000 (per individual tool call)
  - MAX_TOOL_RESULTS_PER_MESSAGE_CHARS = 200,000 (aggregate per turn)

When a limit is exceeded, the overflow is written to disk and a truncated
preview with a file path reference is returned to the model instead of
the raw text.

Usage:
    from packages.agnt_tools.tool_output_caps import ToolOutputCaps
    caps = ToolOutputCaps()
    result = caps.enforce(tool_name="grep_search", output=huge_text)
"""

from __future__ import annotations

import hashlib
import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

logger = logging.getLogger("agnt.tool_output_caps")

# --- Constants (from toolLimits.ts) ------------------------------------------

DEFAULT_MAX_RESULT_SIZE_CHARS = int(
  os.environ.get("TOOL_MAX_RESULT_CHARS", "50000")
)  # 50K per tool
MAX_TOOL_RESULTS_PER_MESSAGE_CHARS = int(
  os.environ.get("TOOL_MAX_AGGREGATE_CHARS", "200000")
)  # 200K per turn

OVERFLOW_DIR = Path(
  os.environ.get(
    "TOOL_OVERFLOW_DIR",
    os.path.expanduser(
      "~/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/tool_overflow"
    ),
  )
)

# Preview: how many chars to show at start and end of truncated output
PREVIEW_HEAD_CHARS = 2000
PREVIEW_TAIL_CHARS = 1000


# --- Data Models -------------------------------------------------------------


@dataclass
class CapResult:
  """Result of applying output caps to a tool result."""

  tool_name: str
  original_chars: int
  returned_chars: int
  was_truncated: bool
  overflow_path: str = ""
  output: str = ""


@dataclass
class TurnBudget:
  """Tracks aggregate tool output budget for a single turn."""

  max_chars: int = MAX_TOOL_RESULTS_PER_MESSAGE_CHARS
  used_chars: int = 0
  tool_count: int = 0
  truncated_count: int = 0

  @property
  def remaining(self) -> int:
    return max(0, self.max_chars - self.used_chars)

  @property
  def exhausted(self) -> bool:
    return self.used_chars >= self.max_chars


# --- Core Implementation ----------------------------------------------------


class ToolOutputCaps:
  """Enforce per-tool and per-turn output size limits.

  This prevents context window bloat when tools return massive outputs
  (e.g., grep_search across large codebases, view_file on large files).

  When output exceeds the per-tool cap (50K chars):
    1. The full output is written to .beads/tool_overflow/<hash>.txt
    2. A truncated preview (head + tail + file reference) is returned
    3. The model can read the full output via the file path if needed

  When aggregate turn output exceeds 200K chars:
    1. Subsequent tools in the same turn are aggressively truncated
    2. The model is informed of the budget exhaustion
  """

  def __init__(
    self,
    per_tool_max: int = DEFAULT_MAX_RESULT_SIZE_CHARS,
    per_turn_max: int = MAX_TOOL_RESULTS_PER_MESSAGE_CHARS,
  ) -> None:
    self.per_tool_max = per_tool_max
    self.per_turn_max = per_turn_max
    self._turn_budget = TurnBudget(max_chars=per_turn_max)
    OVERFLOW_DIR.mkdir(parents=True, exist_ok=True)

  def new_turn(self) -> None:
    """Reset the turn budget for a new message turn."""
    self._turn_budget = TurnBudget(max_chars=self.per_turn_max)

  @property
  def budget(self) -> TurnBudget:
    """Current turn budget status."""
    return self._turn_budget

  def enforce(self, tool_name: str, output: str) -> CapResult:
    """Apply output caps to a single tool result.

    Args:
        tool_name: Name of the tool (for logging).
        output: Raw tool output string.

    Returns:
        CapResult with potentially truncated output.
    """
    original_chars = len(output)
    self._turn_budget.tool_count += 1

    # Determine effective cap (minimum of per-tool and remaining budget)
    effective_cap = min(self.per_tool_max, self._turn_budget.remaining)

    if original_chars <= effective_cap:
      # Under limit — pass through
      self._turn_budget.used_chars += original_chars
      return CapResult(
        tool_name=tool_name,
        original_chars=original_chars,
        returned_chars=original_chars,
        was_truncated=False,
        output=output,
      )

    # Over limit — truncate and write overflow to disk
    overflow_path = self._write_overflow(tool_name, output)

    # Build preview: head + ... + tail + file reference
    head = output[:PREVIEW_HEAD_CHARS]
    tail = output[-PREVIEW_TAIL_CHARS:] if len(output) > PREVIEW_TAIL_CHARS else ""

    truncated_output = (
      f"{head}\n\n"
      f"... [TRUNCATED: {original_chars:,} chars total, "
      f"showing {PREVIEW_HEAD_CHARS + PREVIEW_TAIL_CHARS:,} of {original_chars:,}] ...\n\n"
      f"{tail}\n\n"
      f"[Full output saved to: {overflow_path}]"
    )

    returned_chars = len(truncated_output)
    self._turn_budget.used_chars += returned_chars
    self._turn_budget.truncated_count += 1

    logger.info(
      "ToolOutputCaps: truncated %s output from %d to %d chars (overflow: %s)",
      tool_name,
      original_chars,
      returned_chars,
      overflow_path,
    )

    return CapResult(
      tool_name=tool_name,
      original_chars=original_chars,
      returned_chars=returned_chars,
      was_truncated=True,
      overflow_path=str(overflow_path),
      output=truncated_output,
    )

  def _write_overflow(self, tool_name: str, output: str) -> Path:
    """Write overflow content to disk for later retrieval."""
    # Generate deterministic filename from content hash
    content_hash = hashlib.sha256(output.encode()).hexdigest()[:12]
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    filename = f"{tool_name}_{timestamp}_{content_hash}.txt"
    overflow_path = OVERFLOW_DIR / filename

    overflow_path.write_text(output)
    return overflow_path

  def clear_overflow(self, max_age_hours: int = 24) -> int:
    """Clean up old overflow files.

    Args:
        max_age_hours: Delete overflow files older than this.

    Returns:
        Number of files cleaned up.
    """
    cleaned = 0
    now = datetime.now(UTC)
    for f in OVERFLOW_DIR.iterdir():
      if f.is_file() and f.suffix == ".txt":
        age_hours = (
          now - datetime.fromtimestamp(f.stat().st_mtime, tz=UTC)
        ).total_seconds() / 3600
        if age_hours > max_age_hours:
          f.unlink()
          cleaned += 1
    if cleaned:
      logger.info("ToolOutputCaps: cleaned %d overflow files", cleaned)
    return cleaned
