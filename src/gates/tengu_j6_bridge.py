# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tengu Gate J6 Bridge — Python-side gate enforcement for governance.

Integrates the Tengu gate registry with the J-6 CSRMC Policy Enforcement
Point. This module provides Python-callable gate checks that delegate to
the TypeScript gate evaluation layer (via IPC/shared config) for consistency,
while adding J-6 ZTA handoff enforcement for inter-agent data transfers.

For pure Python services (ML pipelines, KAIROS daemon, etc.), gates are
read from the disk cache written by GrowthBook's syncRemoteEvalToDisk.

References:
    - src/gates/tengu_registry.ts (canonical gate definitions)
    - src/governance/j6_csrmc_cato.py (ZTA enforcement)
    - src/services/analytics/growthbook.ts (disk cache source)
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from governance.j6_csrmc_cato import Cor_Claude_Code_6CSRMC, CSRMCBlockError

logger = logging.getLogger("tengu-gates")


class GateCategory(Enum):
    """Mirror of the TypeScript GateCategory enum."""

    SECURITY = "SECURITY"
    ENTITLEMENT = "ENTITLEMENT"
    FEATURE = "FEATURE"
    TELEMETRY = "TELEMETRY"
    INTERNAL = "INTERNAL"


@dataclass(frozen=True)
class GateDefinition:
    """Python-side gate definition (subset of TypeScript TenguGateDefinition)."""

    key: str
    description: str
    category: GateCategory
    default_value: Any
    ant_only: bool = False


# ─── Python-side Gate Registry (mirrors tengu_registry.ts) ──────────

PYTHON_GATES: dict[str, GateDefinition] = {
    "yolo_classifier_enabled": GateDefinition(
        key="tengu_yolo_security_classifier",
        description="BashSecurityClassifier 30-check pipeline",
        category=GateCategory.SECURITY,
        default_value=True,
    ),
    "xml_pipeline_enabled": GateDefinition(
        key="tengu_xml_2stage_pipeline",
        description="XML 2-stage classification pipeline",
        category=GateCategory.SECURITY,
        default_value=True,
    ),
    "zta_handoff_enforcement": GateDefinition(
        key="tengu_j6_zta_handoff",
        description="J6 Zero Trust handoff enforcement",
        category=GateCategory.SECURITY,
        default_value=True,
    ),
    "speculation_engine": GateDefinition(
        key="tengu_speculation_engine",
        description="Speculative prompt pre-execution",
        category=GateCategory.FEATURE,
        default_value=False,
    ),
    "context_compaction": GateDefinition(
        key="tengu_context_compaction_v2",
        description="4-layer context compaction pipeline",
        category=GateCategory.FEATURE,
        default_value=False,
    ),
    "ant_model_override": GateDefinition(
        key="tengu_ant_model_override",
        description="Internal model override",
        category=GateCategory.INTERNAL,
        default_value="",
        ant_only=True,
    ),
}


# ─── Disk Cache Reader ──────────────────────────────────────────────


def _find_config_path() -> Path | None:
    """Locate the GrowthBook disk cache (globalConfig.json).

    Searches in order:
    1. CLAUDE_CONFIG_DIR env var
    2. ~/.claude/ (default)
    3. XDG_CONFIG_HOME/claude/
    """
    config_dir = os.environ.get("CLAUDE_CONFIG_DIR")
    if config_dir:
        p = Path(config_dir) / "globalConfig.json"
        if p.exists():
            return p

    home = Path.home()
    default = home / ".claude" / "globalConfig.json"
    if default.exists():
        return default

    xdg = os.environ.get("XDG_CONFIG_HOME", str(home / ".config"))
    xdg_path = Path(xdg) / "claude" / "globalConfig.json"
    if xdg_path.exists():
        return xdg_path

    return None


def _read_cached_features() -> dict[str, Any]:
    """Read GrowthBook feature values from disk cache."""
    config_path = _find_config_path()
    if not config_path:
        logger.debug("No globalConfig.json found — using defaults")
        return {}

    try:
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)
        return config.get("cachedGrowthBookFeatures", {})
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Failed to read GrowthBook cache: %s", e)
        return {}


# ─── Gate Evaluation ────────────────────────────────────────────────


def evaluate_gate(gate_name: str) -> Any:
    """Evaluate a gate by name, reading from disk cache.

    For security gates, returns the default value (fail-closed) if cache
    is unavailable. For feature gates, returns the default (fail-open).

    Args:
        gate_name: Key into PYTHON_GATES dict.

    Returns:
        The gate value (type depends on the gate definition).

    Raises:
        KeyError: If gate_name is not registered.
    """
    if gate_name not in PYTHON_GATES:
        raise KeyError(
            f"Unregistered gate: {gate_name}. "
            f"Available: {sorted(PYTHON_GATES.keys())}"
        )

    defn = PYTHON_GATES[gate_name]

    # Ant-only enforcement
    if defn.ant_only and os.environ.get("USER_TYPE") != "ant":
        logger.debug("Gate %s is ant-only, returning default", defn.key)
        return defn.default_value

    # Read from disk cache
    cached = _read_cached_features()
    value = cached.get(defn.key)

    if value is not None:
        logger.debug("Gate %s = %s (from cache)", defn.key, value)
        return value

    logger.debug("Gate %s = %s (default, not in cache)", defn.key, defn.default_value)
    return defn.default_value


def is_security_gate_active(gate_name: str) -> bool:
    """Check if a security gate is active. Returns bool.

    Fail-closed: returns True (enforcement ON) if cache read fails.
    """
    try:
        value = evaluate_gate(gate_name)
        return bool(value)
    except Exception:
        logger.warning(
            "Security gate %s evaluation failed — FAIL-CLOSED (active)", gate_name
        )
        return True


# ─── J6 ZTA Integration ────────────────────────────────────────────


@dataclass
class HandoffRequest:
    """Inter-agent handoff request for J6 ZTA inspection."""

    source_agent: str
    destination_agent: str
    payload_type: str
    risk_severity: str = "MARGINAL"
    metadata: dict[str, Any] = field(default_factory=dict)


def enforce_zta_handoff(request: HandoffRequest) -> bool:
    """Enforce J6 ZTA gate on an inter-agent handoff.

    1. Check if ZTA enforcement gate is active
    2. If active, delegate to J6 CSRMC PEP
    3. If inactive, log warning and allow (degraded mode)

    Args:
        request: The handoff request to inspect.

    Returns:
        True if handoff is authorized.

    Raises:
        CSRMCBlockError: If the handoff is blocked by CSRMC policy.
    """
    if not is_security_gate_active("zta_handoff_enforcement"):
        logger.warning(
            "⚠️ ZTA enforcement gate is INACTIVE — allowing handoff %s → %s (degraded mode)",
            request.source_agent,
            request.destination_agent,
        )
        return True

    logger.info(
        "🔐 Tengu ZTA Gate: Inspecting %s → %s (type=%s, severity=%s)",
        request.source_agent,
        request.destination_agent,
        request.payload_type,
        request.risk_severity,
    )

    payload = {
        "type": request.payload_type,
        "risk_sev": request.risk_severity,
        **request.metadata,
    }

    # Delegate to J6 CSRMC PEP — may raise CSRMCBlockError
    return Cor_Claude_Code_6CSRMC.enforce_zero_trust_handoff(
        source=request.source_agent,
        destination=request.destination_agent,
        payload=payload,
    )


# ─── Diagnostics ────────────────────────────────────────────────────


def get_gate_diagnostics() -> dict[str, Any]:
    """Return a diagnostic snapshot of all Python-side gates."""
    cached = _read_cached_features()
    diagnostics: dict[str, Any] = {}

    for name, defn in PYTHON_GATES.items():
        cached_value = cached.get(defn.key)
        diagnostics[name] = {
            "key": defn.key,
            "category": defn.category.value,
            "cached_value": cached_value,
            "default_value": defn.default_value,
            "effective_value": cached_value if cached_value is not None else defn.default_value,
            "ant_only": defn.ant_only,
        }

    return diagnostics
