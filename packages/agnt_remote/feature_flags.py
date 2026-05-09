"""Local-only feature flag resolution.

Resolves EXCLUSIVELY from AGNT_FC_OVERRIDES env var.
Never contacts GrowthBook, Statsig, LaunchDarkly, or any remote
feature flag service. This is the canonical flag resolver for all
Safe Harbor modules.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class LocalFeatureFlags:
    """Feature flag resolver backed by AGNT_FC_OVERRIDES JSON env var.

    Usage:
        export AGNT_FC_OVERRIDES='{"my_flag": true, "rollout_pct": 50}'
        flags = LocalFeatureFlags()
        flags.get_bool("my_flag")  # True
        flags.get_int("rollout_pct", 0)  # 50
    """

    __slots__ = ("_overrides",)

    def __init__(self) -> None:
        self._overrides = self._load()

    @staticmethod
    def _load() -> dict[str, Any]:
        raw = os.environ.get("AGNT_FC_OVERRIDES", "")
        if not raw:
            return {}
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return parsed
            logger.warning("AGNT_FC_OVERRIDES is not a dict, ignoring")
        except json.JSONDecodeError, TypeError:
            logger.warning("AGNT_FC_OVERRIDES invalid JSON, ignoring")
        return {}

    def reload(self) -> None:
        """Reload overrides from the environment."""
        self._overrides = self._load()

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get a boolean flag value."""
        val = self._overrides.get(key)
        if val is None:
            return default
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            return val.lower() in ("true", "1", "yes", "on")
        return default

    def get_int(self, key: str, default: int = 0) -> int:
        """Get an integer flag value."""
        val = self._overrides.get(key)
        if val is None:
            return default
        try:
            return int(val)
        except TypeError, ValueError:
            return default

    def get_str(self, key: str, default: str = "") -> str:
        """Get a string flag value."""
        val = self._overrides.get(key)
        if val is None:
            return default
        return str(val)

    def check_gate(self, gate: str) -> bool:
        """Check a feature gate (alias for get_bool)."""
        return self.get_bool(gate)
