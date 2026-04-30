# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AGNT Feature Flag System.

Ported from: GrowthBook with CLAUDE_INTERNAL_FC_OVERRIDES
Reference: AGNT STATE B Spec P4.1

Usage:
    export AGNT_FC_OVERRIDES='{"context_compaction":true,"vcr_mode":"record"}'

    from config.feature_flags import flags
    if flags.is_enabled("context_compaction"):
        run_compaction()

    vcr_mode = flags.get_string("vcr_mode", default="off")
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


# Default feature flag values
# These mirror the production defaults; overrides come from env var
_DEFAULTS: dict[str, Any] = {
    # Phase 1: Context Efficiency
    "context_compaction": False,
    "cache_break_detection": False,
    "autocompact_buffer_tokens": 13_000,
    "warning_threshold_buffer_tokens": 20_000,
    "max_consecutive_compact_failures": 3,
    # Phase 2: Permission Architecture
    "xml_classifier": False,
    "classifier_model": "gemini-3.1-flash-lite-preview-thinking",
    "classifier_max_tokens_stage1": 256,
    "subcommand_security_cap": 50,
    # Phase 3: Memory & Observability
    "vcr_mode": "off",  # off | record | replay | diff
    "telemetry_enabled": True,
    "telemetry_buffer_size": 10,
    "session_memory_compact": False,
    # Phase 4: Developer Experience
    "dump_prompts": False,
    "plan_mode_v2": False,
    "plan_interview_phase": False,
    # Phase 5: Security Hardening
    "fail_closed_default": True,
    "assistant_text_exclusion": True,
    "context_decay_warnings": True,
    "file_read_budget": 2000,
    "tool_result_max_chars": 50_000,
    # Phase 6: Speculation Engine (CC speculation.ts port)
    "speculation_enabled": True,
    "speculation_max_turns": 20,
    "speculation_max_messages": 100,
    "speculation_overlay_isolation": True,
    # Phase 7: Nag Protocol (complexity-proportional prompts)
    "nag_prompt_precompute": True,
    "nag_prompt_cache_ms": 30_000,
    "nag_prompt_min_count": 5,
    "nag_prompt_max_count": 22,
}


class FeatureFlags:
    """Runtime feature flag system with JSON override support.

    Loads defaults from _DEFAULTS, then applies overrides from
    the AGNT_FC_OVERRIDES environment variable (JSON string).

    Thread-safe: reads are lock-free after init; hot-reload mutates atomically.
    """

    def __init__(self) -> None:
        self._flags: dict[str, Any] = dict(_DEFAULTS)
        self._overrides: dict[str, Any] = {}
        self._load_overrides()

    def _load_overrides(self) -> None:
        """Load overrides from AGNT_FC_OVERRIDES env var."""
        raw = os.environ.get("AGNT_FC_OVERRIDES", "")
        if not raw:
            return

        try:
            overrides = json.loads(raw)
            if not isinstance(overrides, dict):
                logger.warning("AGNT_FC_OVERRIDES is not a JSON object — ignoring")
                return

            self._overrides = overrides
            self._flags.update(overrides)

            logger.info(
                "Feature flags: %d overrides applied from AGNT_FC_OVERRIDES",
                len(overrides),
            )
        except json.JSONDecodeError as e:
            logger.warning("AGNT_FC_OVERRIDES parse error: %s", e)

    def reload(self) -> None:
        """Hot-reload overrides from env var."""
        self._flags = dict(_DEFAULTS)
        self._overrides = {}
        self._load_overrides()

    def is_enabled(self, flag: str) -> bool:
        """Check if a boolean flag is enabled.

        Returns False for unknown flags (fail-closed).
        """
        value = self._flags.get(flag)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes")
        return False

    def get_int(self, flag: str, default: int = 0) -> int:
        """Get an integer flag value."""
        value = self._flags.get(flag)
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                pass
        return default

    def get_string(self, flag: str, default: str = "") -> str:
        """Get a string flag value."""
        value = self._flags.get(flag)
        if value is not None:
            return str(value)
        return default

    def get_raw(self, flag: str) -> Any:
        """Get a flag value without type conversion."""
        return self._flags.get(flag)

    def all_flags(self) -> dict[str, Any]:
        """Return all current flag values."""
        return dict(self._flags)

    def active_overrides(self) -> dict[str, Any]:
        """Return only the overridden flags."""
        return dict(self._overrides)

    def __repr__(self) -> str:
        return f"FeatureFlags(total={len(self._flags)}, overrides={len(self._overrides)})"


# Singleton instance — importable from anywhere
flags = FeatureFlags()
