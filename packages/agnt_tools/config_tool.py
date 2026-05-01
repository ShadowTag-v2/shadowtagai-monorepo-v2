# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AGNT Config Tool — Live Runtime Flag Modification.

Ported from: Claude Code ConfigTool + GrowthBook /config Gates tab
Reference: AGNT STATE B Spec P4.1, hidden_tools_port_spec.md §2

Architecture (derived from CC growthbook.ts lines 206-290):
    1. Env var overrides (AGNT_FC_OVERRIDES) take highest priority
    2. Config file overrides (.beads/agnt_config.json) are second
    3. Compiled defaults (_DEFAULTS in feature_flags.py) are last
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_MONOREPO_ROOT = Path(__file__).resolve().parent.parent.parent
_CONFIG_PATH = _MONOREPO_ROOT / ".beads" / "agnt_config.json"

_FLAG_CATEGORIES: dict[str, list[str]] = {
    "Context Efficiency": [
        "context_compaction",
        "cache_break_detection",
        "autocompact_buffer_tokens",
        "warning_threshold_buffer_tokens",
        "max_consecutive_compact_failures",
    ],
    "Permission Architecture": [
        "xml_classifier",
        "classifier_model",
        "classifier_max_tokens_stage1",
        "subcommand_security_cap",
    ],
    "Memory & Observability": [
        "vcr_mode",
        "telemetry_enabled",
        "telemetry_buffer_size",
        "session_memory_compact",
    ],
    "Developer Experience": [
        "dump_prompts",
        "plan_mode_v2",
        "plan_interview_phase",
    ],
    "Security Hardening": [
        "fail_closed_default",
        "assistant_text_exclusion",
        "context_decay_warnings",
        "file_read_budget",
        "tool_result_max_chars",
    ],
    "Speculation Engine": [
        "speculation_enabled",
        "speculation_max_turns",
        "speculation_max_messages",
        "speculation_overlay_isolation",
    ],
    "Nag Protocol": [
        "nag_prompt_precompute",
        "nag_prompt_cache_ms",
        "nag_prompt_min_count",
        "nag_prompt_max_count",
    ],
}


@dataclass
class ConfigChange:
    """Record of a single config change for audit trail."""

    flag: str
    old_value: Any
    new_value: Any
    timestamp: float = field(default_factory=time.time)
    source: str = "config_tool"


class ConfigTool:
    """Live runtime feature flag modification tool.

    Mirrors CC's /config Gates tab (growthbook.ts lines 206-290).
    Priority: AGNT_FC_OVERRIDES env > .beads/agnt_config.json > defaults.
    Thread-safe: JSON writes are atomic via tempfile+rename.
    """

    def __init__(self, config_path: Path | None = None) -> None:
        self._config_path = config_path or _CONFIG_PATH
        self._change_log: list[ConfigChange] = []
        self._ensure_config_exists()

    def _ensure_config_exists(self) -> None:
        if not self._config_path.exists():
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            self._write_config(
                {
                    "version": "1.0.0",
                    "growthBookOverrides": {},
                    "speculationEnabled": True,
                    "nagPromptPrecompute": True,
                    "nagPromptCacheMs": 30000,
                }
            )

    def _read_config(self) -> dict[str, Any]:
        try:
            with open(self._config_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"growthBookOverrides": {}}

    def _write_config(self, config: dict[str, Any]) -> None:
        config["lastModified"] = time.time()
        tmp_path = self._config_path.with_suffix(".tmp")
        with open(tmp_path, "w") as f:
            json.dump(config, f, indent=2, default=str)
            f.write("\n")
        tmp_path.rename(self._config_path)

    def _get_overrides(self) -> dict[str, Any]:
        return self._read_config().get("growthBookOverrides", {})

    def _set_overrides(self, overrides: dict[str, Any]) -> None:
        config = self._read_config()
        config["growthBookOverrides"] = overrides
        self._write_config(config)

    def set(self, flag: str, value: Any) -> ConfigChange:
        """Set a flag override. Mirrors CC setGrowthBookConfigOverride."""
        overrides = self._get_overrides()
        old_value = overrides.get(flag)
        overrides[flag] = value
        self._set_overrides(overrides)
        change = ConfigChange(flag=flag, old_value=old_value, new_value=value)
        self._change_log.append(change)
        self._sync_to_env(overrides)
        logger.info("Config: %s = %r (was %r)", flag, value, old_value)
        return change

    def get(self, flag: str) -> Any:
        """Get a flag's current override value."""
        return self._get_overrides().get(flag)

    def clear(self, flag: str) -> ConfigChange | None:
        """Remove a single override, reverting to compiled default."""
        overrides = self._get_overrides()
        if flag not in overrides:
            return None
        old_value = overrides.pop(flag)
        self._set_overrides(overrides)
        self._sync_to_env(overrides)
        change = ConfigChange(flag=flag, old_value=old_value, new_value=None)
        self._change_log.append(change)
        return change

    def clear_all(self) -> int:
        """Clear all overrides. Mirrors CC clearGrowthBookConfigOverrides."""
        overrides = self._get_overrides()
        count = len(overrides)
        self._set_overrides({})
        self._sync_to_env({})
        for flag, value in overrides.items():
            self._change_log.append(ConfigChange(flag=flag, old_value=value, new_value=None))
        return count

    def list_overrides(self) -> dict[str, Any]:
        """List only overridden flags."""
        return self._get_overrides()

    def list_all(self) -> dict[str, dict[str, Any]]:
        """List all flags grouped by category with override status."""
        try:
            from config.feature_flags import flags

            all_flags = flags.all_flags()
        except ImportError:
            # Feature flags module not available — show overrides only
            all_flags = self._get_overrides()

        overrides = self._get_overrides()
        result: dict[str, dict[str, Any]] = {}
        seen: set[str] = set()
        for cat, names in _FLAG_CATEGORIES.items():
            cat_data: dict[str, Any] = {}
            for name in names:
                if name in all_flags:
                    cat_data[name] = {
                        "value": all_flags[name],
                        "overridden": name in overrides,
                    }
                    seen.add(name)
            if cat_data:
                result[cat] = cat_data
        uncategorized = {k: {"value": v, "overridden": k in overrides} for k, v in all_flags.items() if k not in seen}
        if uncategorized:
            result["Uncategorized"] = uncategorized
        return result

    def format_table(self) -> str:
        """Format all flags as a readable table (Gates tab display)."""
        all_data = self.list_all()
        lines = [
            "╔══════════════════════════════════════════════════════╗",
            "║          AGNT Feature Flags — Gates Tab             ║",
            "╚══════════════════════════════════════════════════════╝",
        ]
        for category, flags_dict in all_data.items():
            lines.append(f"\n  ▸ {category}")
            lines.append("  " + "─" * 52)
            for name, info in flags_dict.items():
                marker = " ★" if info["overridden"] else "  "
                value = info["value"]
                display = ("✓ ON" if value else "✗ OFF") if isinstance(value, bool) else str(value)
                lines.append(f"  {marker} {name:<40} {display}")
        overrides = self.list_overrides()
        if overrides:
            lines.append(f"\n  ★ = overridden ({len(overrides)} active)")
        return "\n".join(lines)

    @staticmethod
    def _sync_to_env(overrides: dict[str, Any]) -> None:
        """Sync overrides to AGNT_FC_OVERRIDES env var."""
        if overrides:
            os.environ["AGNT_FC_OVERRIDES"] = json.dumps(overrides)
        elif "AGNT_FC_OVERRIDES" in os.environ:
            del os.environ["AGNT_FC_OVERRIDES"]

    def reload_flags(self) -> None:
        """Force the FeatureFlags singleton to reload from env."""
        try:
            from config.feature_flags import flags

            flags.reload()
        except ImportError:
            pass  # Feature flags module not available

    def get_change_log(self) -> list[ConfigChange]:
        """Return the in-memory audit trail of changes this session."""
        return list(self._change_log)
