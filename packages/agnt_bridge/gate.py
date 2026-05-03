"""Safe Harbor bridge feature gating.

Ported from src/bridge/bridgeEnabled.ts. ALL GrowthBook remote calls
replaced with local-only AGNT_FC_OVERRIDES resolution. No network
egress permitted.
"""

from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from typing import Any

logger = logging.getLogger(__name__)

# ─── Local Feature Flag Resolution ────────────────────────────────────


def _load_overrides() -> dict[str, Any]:
    """Load feature flag overrides from AGNT_FC_OVERRIDES env var.

    Returns an empty dict if the env var is missing or malformed.
    Never contacts any remote service.
    """
    raw = os.environ.get("AGNT_FC_OVERRIDES", "")
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            logger.warning("AGNT_FC_OVERRIDES is not a JSON object, ignoring")
            return {}
        return parsed
    except (json.JSONDecodeError, TypeError):
        logger.warning("AGNT_FC_OVERRIDES contains invalid JSON, ignoring")
        return {}


def get_flag(flag_name: str, default: bool = False) -> bool:
    """Resolve a feature flag from local overrides only.

    Safe Harbor: NEVER contacts GrowthBook or any remote service.
    Resolution chain: AGNT_FC_OVERRIDES → default.
    """
    overrides = _load_overrides()
    value = overrides.get(flag_name)
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "on")
    return default


# ─── Bridge Feature Gates ─────────────────────────────────────────────


def is_bridge_enabled() -> bool:
    """Check if the local IPC bridge is enabled.

    Safe Harbor: No OAuth subscriber check. No remote GrowthBook gate.
    Enabled when AGNT_BRIDGE_ENABLED=true in AGNT_FC_OVERRIDES or
    when AGNT_BRIDGE_SECRET is set (implying intent to use the bridge).
    """
    if get_flag("agnt_bridge_enabled", default=False):
        return True
    # Presence of the shared secret implies bridge intent
    return bool(os.environ.get("AGNT_BRIDGE_SECRET"))


def is_bridge_enabled_blocking() -> bool:
    """Blocking entitlement check for the bridge.

    Safe Harbor: Synchronous — no async GrowthBook fetch needed when
    everything is local. Same result as is_bridge_enabled().
    """
    return is_bridge_enabled()


def get_bridge_disabled_reason() -> str | None:
    """Diagnostic message for why the bridge is unavailable.

    Returns None if the bridge is enabled.
    """
    if is_bridge_enabled():
        return None

    if not os.environ.get("AGNT_BRIDGE_SECRET"):
        return (
            "Local IPC bridge requires AGNT_BRIDGE_SECRET environment "
            "variable. Generate a secret with: "
            'python -c "import secrets; print(secrets.token_hex(32))"'
        )

    return "Local IPC bridge is not enabled. Set 'agnt_bridge_enabled': true in AGNT_FC_OVERRIDES."


def is_env_less_bridge_enabled() -> bool:
    """Check if the env-less bridge path is enabled.

    Safe Harbor: Resolves from AGNT_FC_OVERRIDES only.
    """
    return get_flag("agnt_bridge_env_less", default=False)


@lru_cache(maxsize=1)
def get_bridge_config_path() -> str:
    """Get the path to the bridge socket.

    Uses XDG_RUNTIME_DIR or falls back to /tmp.
    """
    runtime_dir = os.environ.get("XDG_RUNTIME_DIR", "/tmp")  # noqa: S108
    return os.path.join(runtime_dir, "agnt_bridge.sock")
