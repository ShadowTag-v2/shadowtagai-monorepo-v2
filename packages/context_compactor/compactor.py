# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AGNT Context Compactor — Orchestrates the 4-layer compaction pipeline.

The compactor tries layers in order of increasing aggressiveness:
  L1 → L2 → L3 → L4

If a layer achieves the target, subsequent layers are skipped.
Each layer's result is logged for telemetry.

Usage:
    compactor = ContextCompactor()
    result = compactor.run(messages, target_tokens=80_000, current_tokens=120_000)

Reference: AGNT STATE B Spec P1.1
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

from context_compactor.cache_break_detector import (
  CacheBreakDetector,
  CacheBreakReport,
)
from context_compactor.layers import (
  AUTOCOMPACT_BUFFER_TOKENS,
  WARNING_THRESHOLD_BUFFER_TOKENS,
  CompactionResult,
  Layer1CachedMC,
  Layer2TimeBased,
  Layer3APIManagement,
  Layer4FullCompaction,
  Message,
)
from context_compactor.micro_compact import (
  MicrocompactResult,
  microcompact_messages,
)

logger = logging.getLogger(__name__)


class ContextCompactor:
  """Orchestrates the 4-layer compaction pipeline.

  Attributes:
      telemetry_dir: Directory for writing telemetry JSONL.
      feature_flags: Runtime feature flag overrides.
  """

  def __init__(
    self,
    telemetry_dir: Path | None = None,
    feature_flags: dict[str, Any] | None = None,
  ) -> None:
    try:
      from config.feature_flags import flags

      default_flags = flags.all_flags()
    except ImportError, ModuleNotFoundError:
      default_flags = {"context_compaction": True}

    self._layers = [
      Layer1CachedMC(),
      Layer2TimeBased(),
      Layer3APIManagement(),
      Layer4FullCompaction(),
    ]
    self._telemetry_dir = telemetry_dir
    self._flags = feature_flags if feature_flags is not None else default_flags
    self._run_count = 0
    self._total_tokens_saved = 0
    self._cache_detector = CacheBreakDetector()
    self._last_cache_report: CacheBreakReport | None = None

  @property
  def is_enabled(self) -> bool:
    """Check if context compaction is enabled via feature flags."""
    return self._flags.get("context_compaction", False)

  @property
  def cache_detector(self) -> CacheBreakDetector:
    """Access the cache break detector for API param configuration."""
    return self._cache_detector

  @property
  def last_cache_report(self) -> CacheBreakReport | None:
    """The most recent cache break report, or None."""
    return self._last_cache_report

  @property
  def stats(self) -> dict[str, Any]:
    """Return cumulative compaction statistics."""
    return {
      "run_count": self._run_count,
      "total_tokens_saved": self._total_tokens_saved,
      "circuit_breaker_open": self._layers[3].circuit_open
      if isinstance(self._layers[3], Layer4FullCompaction)
      else False,
      "last_cache_preserved": self._last_cache_report.cache_broken is False
      if self._last_cache_report
      else None,
    }

  def should_compact(self, current_tokens: int, max_tokens: int) -> bool:
    """Determine if compaction should run based on token thresholds.

    Args:
        current_tokens: Current context window usage.
        max_tokens: Maximum context window size.

    Returns:
        True if compaction should run.
    """
    if not self.is_enabled:
      return False

    remaining = max_tokens - current_tokens
    return remaining < AUTOCOMPACT_BUFFER_TOKENS

  def should_warn(self, current_tokens: int, max_tokens: int) -> bool:
    """Check if a context decay warning should be emitted.

    Args:
        current_tokens: Current context window usage.
        max_tokens: Maximum context window size.

    Returns:
        True if warning threshold is breached.
    """
    remaining = max_tokens - current_tokens
    return remaining < WARNING_THRESHOLD_BUFFER_TOKENS

  def pre_compact(
    self,
    messages: list[Any],
    query_source: str | None = None,
  ) -> MicrocompactResult:
    """Run pre-request microcompaction (proactive phase).

    Should be called BEFORE each API request to shrink stale context
    when the prompt cache is cold (idle gap exceeds threshold).

    Args:
        messages: Raw message dicts (will be deep-copied if modified).
        query_source: Originating query source identifier.

    Returns:
        MicrocompactResult with possibly-modified messages.
    """
    return microcompact_messages(messages, query_source)

  def run(
    self,
    messages: list[Message],
    target_tokens: int,
    current_tokens: int,
    max_layer: int = 4,
  ) -> CompactionResult:
    """Execute the reactive compaction pipeline.

    Tries layers L1→L4 in order. Stops as soon as target is reached.
    Call `pre_compact()` first for proactive shrinking.

    Args:
        messages: Mutable list of conversation messages.
        target_tokens: Desired token count after compaction.
        current_tokens: Current total token count.
        max_layer: Maximum layer to attempt (1-4). Default: all.

    Returns:
        CompactionResult from the layer that achieved the target,
        or the last layer's result if none achieved it.
    """
    if not self.is_enabled:
      return CompactionResult(
        tokens_before=current_tokens,
        tokens_after=current_tokens,
        layer_used="disabled",
      )

    self._run_count += 1
    start_time = time.time()
    final_result = CompactionResult(tokens_before=current_tokens)
    running_tokens = current_tokens

    # Phase 1: Cache break pre-scan — snapshot anchored messages
    cache_anchors = self._cache_detector.pre_scan(messages)
    logger.debug(
      "Cache pre-scan: %d anchors identified",
      len(cache_anchors),
    )

    for layer in self._layers:
      if layer.aggressiveness > max_layer:
        break

      if running_tokens <= target_tokens:
        logger.info(
          "Target reached at %d tokens (target: %d) — skipping %s",
          running_tokens,
          target_tokens,
          layer.name,
        )
        break

      logger.info(
        "Running %s (current: %d, target: %d)",
        layer.name,
        running_tokens,
        target_tokens,
      )

      result = layer.compact(messages, target_tokens, running_tokens)
      running_tokens = result.tokens_after

      # Accumulate results
      final_result.tokens_saved += result.tokens_saved
      final_result.messages_modified += result.messages_modified
      final_result.errors.extend(result.errors)
      final_result.layer_used = result.layer_used
      final_result.cache_preserved = (
        final_result.cache_preserved and result.cache_preserved
      )

      # Log telemetry
      self._emit_telemetry(result, time.time() - start_time)

      if result.errors:
        logger.warning(
          "%s had errors: %s",
          layer.name,
          result.errors,
        )

    # Phase 2: Cache break post-verify — confirm cache integrity
    cache_report = self._cache_detector.post_verify(messages, cache_anchors)
    self._last_cache_report = cache_report

    if cache_report.cache_broken:
      final_result.cache_preserved = False
      logger.warning(
        "Cache break detected after compaction: vectors=%s, survival_rate=%.1f%%",
        [v.value for v in cache_report.vectors_triggered],
        cache_report.survival_rate,
      )
      # Emit cache break telemetry event
      self._emit_cache_break_telemetry(cache_report, time.time() - start_time)

    final_result.tokens_after = running_tokens
    self._total_tokens_saved += final_result.tokens_saved

    logger.info(
      "Compaction complete: %d → %d tokens (%.1f%% saved, layer: %s, cache_preserved: %s)",
      current_tokens,
      running_tokens,
      final_result.savings_pct,
      final_result.layer_used,
      final_result.cache_preserved,
    )

    return final_result

  def _emit_telemetry(self, result: CompactionResult, elapsed_ms: float) -> None:
    """Write compaction telemetry to .beads/telemetry.jsonl."""
    if not self._telemetry_dir:
      return

    event = {
      "event": "agnt_compact_result",
      "timestamp": time.time(),
      "layer": result.layer_used,
      "tokens_before": result.tokens_before,
      "tokens_after": result.tokens_after,
      "tokens_saved": result.tokens_saved,
      "savings_pct": result.savings_pct,
      "cache_preserved": result.cache_preserved,
      "messages_modified": result.messages_modified,
      "errors": result.errors,
      "elapsed_ms": round(elapsed_ms * 1000, 2),
    }

    self._write_telemetry_event(event)

  def _emit_cache_break_telemetry(
    self, report: CacheBreakReport, elapsed_ms: float
  ) -> None:
    """Write cache break detection telemetry."""
    if not self._telemetry_dir:
      return

    event = {
      "event": "agnt_cache_break_detected",
      "timestamp": time.time(),
      "vectors_triggered": [v.value for v in report.vectors_triggered],
      "anchors_surviving": report.anchors_surviving,
      "anchors_total": report.anchors_total,
      "survival_rate": report.survival_rate,
      "break_position": report.break_position,
      "elapsed_ms": round(elapsed_ms * 1000, 2),
    }

    self._write_telemetry_event(event)

  def _write_telemetry_event(self, event: dict[str, Any]) -> None:
    """Write a single telemetry event to the JSONL file."""
    if not self._telemetry_dir:
      return

    telemetry_file = self._telemetry_dir / "telemetry.jsonl"
    try:
      self._telemetry_dir.mkdir(parents=True, exist_ok=True)
      with open(telemetry_file, "a") as f:
        f.write(json.dumps(event) + "\n")
    except OSError:
      logger.warning("Failed to write telemetry to %s", telemetry_file)
