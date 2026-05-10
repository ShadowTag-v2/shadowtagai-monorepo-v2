# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Thinking Config — Manage extended-thinking mode for LLM inference.

Ported from src/utils/thinking.ts (Claude Code v2.1.91, 156 lines).

Batch 2 Security Constraints:
  - NO GrowthBook feature flags — local overrides only (AGNT_FC_OVERRIDES)
  - NO bun:bundle build gates — everything is runtime-gated
  - NO React theme colors (rainbow_*) — text-only backend
  - Model support checks adapted for Gemini model family

Usage:
    from thinking_config import (
        ThinkingConfig,
        has_ultrathink_keyword,
        find_thinking_trigger_positions,
        model_supports_thinking,
        should_enable_thinking_by_default,
    )

    cfg = ThinkingConfig(type="adaptive")
    assert has_ultrathink_keyword("please ultrathink about this")
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Literal

__all__ = [
  "ThinkingConfig",
  "ThinkingTriggerPosition",
  "has_ultrathink_keyword",
  "find_thinking_trigger_positions",
  "model_supports_thinking",
  "model_supports_adaptive_thinking",
  "should_enable_thinking_by_default",
  "is_ultrathink_enabled",
]

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ThinkingConfig:
  """Configuration for extended thinking mode.

  type="adaptive"  — model chooses thinking depth per turn
  type="enabled"   — forced thinking with a fixed budget
  type="disabled"  — thinking entirely off
  """

  type: Literal["adaptive", "enabled", "disabled"]
  budget_tokens: int = 0


@dataclass(frozen=True, slots=True)
class ThinkingTriggerPosition:
  """Character-offset span of an ultrathink keyword in user text."""

  word: str
  start: int
  end: int


# ---------------------------------------------------------------------------
# Compiled regex — matches "ultrathink" as a whole word
# ---------------------------------------------------------------------------

_ULTRATHINK_RE = re.compile(r"\bultrathink\b", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Feature gate — local override only (Batch 2: P4.1)
# ---------------------------------------------------------------------------


def _get_fc_overrides() -> dict[str, bool]:
  """Parse AGNT_FC_OVERRIDES env var into a flag → bool map.

  Format: ``AGNT_FC_OVERRIDES="flag1=true,flag2=false"``
  """
  raw = os.environ.get("AGNT_FC_OVERRIDES", "")
  if not raw:
    return {}
  overrides: dict[str, bool] = {}
  for pair in raw.split(","):
    pair = pair.strip()
    if "=" not in pair:
      continue
    key, val = pair.split("=", 1)
    overrides[key.strip()] = val.strip().lower() in ("true", "1", "yes")
  return overrides


def is_ultrathink_enabled() -> bool:
  """Runtime gate for ultrathink mode.

  Original TS uses ``feature('ULTRATHINK')`` (build gate) **and**
  GrowthBook ``tengu_turtle_carbon``. We replace both with local
  override via ``AGNT_FC_OVERRIDES=ultrathink=true``.  Defaults to
  ``True`` (enabled) when no override is present — matching upstream
  GrowthBook default.
  """
  overrides = _get_fc_overrides()
  return overrides.get("ultrathink", True)


# ---------------------------------------------------------------------------
# Keyword detection
# ---------------------------------------------------------------------------


def has_ultrathink_keyword(text: str) -> bool:
  """Check if *text* contains the ``ultrathink`` keyword."""
  return bool(_ULTRATHINK_RE.search(text))


def find_thinking_trigger_positions(text: str) -> list[ThinkingTriggerPosition]:
  """Locate all ``ultrathink`` keyword spans inside *text*."""
  return [
    ThinkingTriggerPosition(word=m.group(0), start=m.start(), end=m.end())
    for m in _ULTRATHINK_RE.finditer(text)
  ]


# ---------------------------------------------------------------------------
# Model capability detection — adapted for Gemini model family
# ---------------------------------------------------------------------------

# Models known to support extended thinking.
_THINKING_MODELS: frozenset[str] = frozenset(
  {
    "gemini-3.1-pro",
    "gemini-3.1-flash",
    "gemini-3-pro",
    "gemini-3-flash",
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-3.1-flash-lite-preview-thinking",
  }
)

# Models known to support adaptive (dynamic depth) thinking.
_ADAPTIVE_THINKING_MODELS: frozenset[str] = frozenset(
  {
    "gemini-3.1-pro",
    "gemini-3-pro",
    "gemini-2.5-pro",
  }
)


def _canonicalize_model(model: str) -> str:
  """Normalize a model identifier to its canonical short name."""
  # Strip provider prefixes (models/xxx, publishers/google/models/xxx)
  parts = model.rsplit("/", 1)
  return parts[-1].lower().strip()


def model_supports_thinking(model: str) -> bool:
  """Check if *model* supports extended thinking.

  Adapted from upstream ``modelSupportsThinking`` — uses Gemini model
  family instead of Claude/Anthropic model names.
  """
  canonical = _canonicalize_model(model)

  # Exact match first
  if canonical in _THINKING_MODELS:
    return True

  # Prefix match for versioned variants (e.g. gemini-3.1-pro-002)
  return any(canonical.startswith(prefix) for prefix in _THINKING_MODELS)


def model_supports_adaptive_thinking(model: str) -> bool:
  """Check if *model* supports adaptive (auto-depth) thinking.

  Adapted from upstream ``modelSupportsAdaptiveThinking``.
  """
  canonical = _canonicalize_model(model)
  if canonical in _ADAPTIVE_THINKING_MODELS:
    return True
  return any(canonical.startswith(prefix) for prefix in _ADAPTIVE_THINKING_MODELS)


def should_enable_thinking_by_default() -> bool:
  """Whether thinking mode should be ON by default.

  Checks ``MAX_THINKING_TOKENS`` env var first, then falls back to
  ``True`` — matching upstream default where thinking is enabled
  unless explicitly disabled.
  """
  max_tokens = os.environ.get("MAX_THINKING_TOKENS")
  if max_tokens is not None:
    try:
      return int(max_tokens) > 0
    except ValueError:
      return True

  # AGNT_FC_OVERRIDES can disable thinking globally
  overrides = _get_fc_overrides()
  if "thinking_enabled" in overrides:
    return overrides["thinking_enabled"]

  # Default: enabled (mirrors upstream)
  return True
