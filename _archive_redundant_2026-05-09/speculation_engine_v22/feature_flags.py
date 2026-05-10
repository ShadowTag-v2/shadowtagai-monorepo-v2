# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""GrowthBook-equivalent feature flags for the Speculation Engine.

Architecture:
  In-memory feature flag system that gates speculation engine features
  without requiring an external SaaS dependency (GrowthBook/LaunchDarkly).

  Flags are loaded from:
    1. Hardcoded defaults (development)
    2. Environment variables (SPECULATION_FLAG_<NAME>=1|0)
    3. JSON override file (.beads/feature_flags.json)
    4. Runtime overrides via set_flag()

  Priority: runtime > file > env > defaults

Usage::

    from speculation_engine.feature_flags import FeatureFlagStore, SpecFlags

    flags = FeatureFlagStore.create()
    if flags.is_enabled(SpecFlags.SEMANTIC_ROUTING):
        result = await mcp_route(query)
    else:
        result = keyword_route(query)
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class SpecFlags(StrEnum):
  """Speculation engine feature flags."""

  # Task 1: Use sequential-thinking MCP for auto_route() instead of keywords.
  SEMANTIC_ROUTING = "semantic_routing"
  # Task 2: Use asyncio.Queue instead of file-polling in consumer.
  ASYNC_CONSUMER = "async_consumer"
  # Task 4: Enable Stitch MCP plan visualization.
  STITCH_VISUALIZATION = "stitch_visualization"
  # Task 5: Record speculation results to telemetry in begin_plan_speculation.
  SPECULATION_TELEMETRY = "speculation_telemetry"
  # Task 6: Enable quality_score benchmarking against .beads/ audit logs.
  QUALITY_BENCHMARK = "quality_benchmark"
  # Task 7: Enable multi-agent mailbox for plan approval delegation.
  AGENT_MAILBOX = "agent_mailbox"
  # General: Enable proactive suggestion generation.
  PROACTIVE_SUGGESTIONS = "proactive_suggestions"
  # General: Enable CoW overlay during executing phase.
  COW_OVERLAY = "cow_overlay"
  # General: Enable speculative execution during research.
  SPECULATE_RESEARCH = "speculate_research"
  # General: Enable speculative execution during synthesis.
  SPECULATE_SYNTHESIS = "speculate_synthesis"


# Default flag values — conservative defaults for production safety
_DEFAULTS: dict[str, bool] = {
  SpecFlags.SEMANTIC_ROUTING: False,
  SpecFlags.ASYNC_CONSUMER: False,
  SpecFlags.STITCH_VISUALIZATION: False,
  SpecFlags.SPECULATION_TELEMETRY: True,
  SpecFlags.QUALITY_BENCHMARK: False,
  SpecFlags.AGENT_MAILBOX: False,
  SpecFlags.PROACTIVE_SUGGESTIONS: True,
  SpecFlags.COW_OVERLAY: True,
  SpecFlags.SPECULATE_RESEARCH: True,
  SpecFlags.SPECULATE_SYNTHESIS: True,
}


@dataclass
class FlagEvaluation:
  """Result of evaluating a feature flag."""

  flag: str
  enabled: bool
  source: str  # "default", "env", "file", "runtime"


@dataclass
class FeatureFlagStore:
  """In-memory feature flag store with layered resolution.

  Resolution order (highest priority first):
    1. Runtime overrides (set_flag)
    2. File overrides (.beads/feature_flags.json)
    3. Environment variables (SPECULATION_FLAG_<NAME>)
    4. Hardcoded defaults

  Attributes:
      _defaults: Base default values.
      _env_overrides: Values from environment variables.
      _file_overrides: Values from JSON override file.
      _runtime_overrides: Values set at runtime via set_flag().
      _evaluation_log: History of flag evaluations for telemetry.
  """

  _defaults: dict[str, bool] = field(default_factory=lambda: dict(_DEFAULTS))
  _env_overrides: dict[str, bool] = field(default_factory=dict)
  _file_overrides: dict[str, bool] = field(default_factory=dict)
  _runtime_overrides: dict[str, bool] = field(default_factory=dict)
  _evaluation_log: list[FlagEvaluation] = field(default_factory=list)

  @classmethod
  def create(cls, *, flags_file: Path | None = None) -> FeatureFlagStore:
    """Factory that loads from environment and optional JSON file.

    Args:
        flags_file: Path to feature flags JSON file.
            Defaults to .beads/feature_flags.json.
    """
    store = cls()

    # Load environment overrides
    for flag in SpecFlags:
      env_key = f"SPECULATION_FLAG_{flag.value.upper()}"
      env_val = os.environ.get(env_key)
      if env_val is not None:
        store._env_overrides[flag.value] = env_val.lower() in (
          "1",
          "true",
          "yes",
          "on",
        )
        logger.debug(
          "Flag %s = %s (from env %s)", flag, store._env_overrides[flag.value], env_key
        )

    # Load file overrides
    if flags_file is None:
      beads_dir = Path(os.environ.get("BEADS_DIR", ".beads"))
      flags_file = beads_dir / "feature_flags.json"

    if flags_file.exists():
      try:
        data = json.loads(flags_file.read_text())
        for key, value in data.items():
          if isinstance(value, bool):
            store._file_overrides[key] = value
          elif isinstance(value, dict):
            # Support nested { "enabled": bool, "percentage": float }
            store._file_overrides[key] = bool(value.get("enabled", False))
        logger.debug("Loaded %d flags from %s", len(store._file_overrides), flags_file)
      except (json.JSONDecodeError, OSError) as e:
        logger.warning("Failed to load feature flags from %s: %s", flags_file, e)

    return store

  def is_enabled(self, flag: str | SpecFlags) -> bool:
    """Check if a feature flag is enabled.

    Args:
        flag: The flag name or SpecFlags enum value.

    Returns:
        True if the flag is enabled after layered resolution.
    """
    flag_name = flag.value if isinstance(flag, SpecFlags) else flag

    # Resolution order: runtime > file > env > defaults
    if flag_name in self._runtime_overrides:
      value = self._runtime_overrides[flag_name]
      source = "runtime"
    elif flag_name in self._file_overrides:
      value = self._file_overrides[flag_name]
      source = "file"
    elif flag_name in self._env_overrides:
      value = self._env_overrides[flag_name]
      source = "env"
    else:
      value = self._defaults.get(flag_name, False)
      source = "default"

    evaluation = FlagEvaluation(flag=flag_name, enabled=value, source=source)
    self._evaluation_log.append(evaluation)
    return value

  def set_flag(self, flag: str | SpecFlags, enabled: bool) -> None:
    """Set a runtime override for a feature flag.

    Args:
        flag: The flag name or SpecFlags enum value.
        enabled: Whether the flag should be enabled.
    """
    flag_name = flag.value if isinstance(flag, SpecFlags) else flag
    self._runtime_overrides[flag_name] = enabled
    logger.info("Runtime flag override: %s = %s", flag_name, enabled)

  def clear_runtime_overrides(self) -> None:
    """Clear all runtime overrides, reverting to file/env/defaults."""
    self._runtime_overrides.clear()

  def get_all_flags(self) -> dict[str, dict[str, Any]]:
    """Return all flags with their current values and sources.

    Returns:
        Dict mapping flag names to {enabled, source} dicts.
    """
    result: dict[str, dict[str, Any]] = {}
    for flag in SpecFlags:
      flag_name = flag.value
      if flag_name in self._runtime_overrides:
        result[flag_name] = {
          "enabled": self._runtime_overrides[flag_name],
          "source": "runtime",
        }
      elif flag_name in self._file_overrides:
        result[flag_name] = {
          "enabled": self._file_overrides[flag_name],
          "source": "file",
        }
      elif flag_name in self._env_overrides:
        result[flag_name] = {"enabled": self._env_overrides[flag_name], "source": "env"}
      else:
        result[flag_name] = {
          "enabled": self._defaults.get(flag_name, False),
          "source": "default",
        }
    return result

  def save_to_file(self, flags_file: Path | None = None) -> None:
    """Persist current runtime overrides to the flags JSON file.

    Args:
        flags_file: Path to save to. Defaults to .beads/feature_flags.json.
    """
    if flags_file is None:
      beads_dir = Path(os.environ.get("BEADS_DIR", ".beads"))
      flags_file = beads_dir / "feature_flags.json"

    flags_file.parent.mkdir(parents=True, exist_ok=True)

    # Merge all layers for the saved file
    merged = dict(self._defaults)
    merged.update(self._env_overrides)
    merged.update(self._file_overrides)
    merged.update(self._runtime_overrides)

    flags_file.write_text(json.dumps(merged, indent=2, sort_keys=True) + "\n")
    logger.info("Feature flags saved to %s", flags_file)

  @property
  def evaluation_history(self) -> list[FlagEvaluation]:
    """Return the evaluation history for telemetry/debugging."""
    return list(self._evaluation_log)
