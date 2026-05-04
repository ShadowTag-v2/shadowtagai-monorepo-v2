# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AGNT Services — Core service registry and lifecycle management.

Ported from src/services/ (Claude Code v2.1.91, 130 files).

This package aggregates the already-ported service modules that live in
dedicated packages:

  - speculation_engine/   → Proactive suggestion generation
  - auto_dream/           → Dream consolidation + memory extraction
  - context_compactor/    → 4-layer context compaction pipeline
  - telemetry/            → Diagnostic tracking + event logging
  - token_estimation/     → Model-aware token counting
  - vcr/                  → VCR record/replay cassette management
  - terminal_notifier/    → Multi-terminal notification routing
  - magic_docs/           → Auto-maintained documentation via subagents
  - plugin_manager/       → Background plugin marketplace reconciliation
  - session_recovery/     → Crash recovery + session state persistence
  - prevent_sleep/        → macOS caffeinate integration
  - sanitization/         → Content sanitization pipeline
  - diagnostic_tracking/  → IDE diagnostic baseline/diff tracking
  - notifier/             → Multi-terminal notification dispatch
  - away_summary/         → Session recap generation
  - rate_limit_messages/  → Rate limit message generation

This module provides:
  - ServiceRegistry: Central registry for lazy service initialization
  - ServiceStatus: Health check dataclass
  - get_service_status(): Quick diagnostics for all registered services
"""

from __future__ import annotations

import importlib
import logging
import sys
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

logger = logging.getLogger(__name__)

# ── sys.path fix ──────────────────────────────────────────────────
# Packages under packages/ use bare internal imports (e.g. `from telemetry.catalog
# import ...`).  Adding `packages/` to sys.path lets those bare names resolve
# without converting every __init__.py to relative imports.
_PACKAGES_DIR = str(Path(__file__).resolve().parent.parent)
if _PACKAGES_DIR not in sys.path:
    sys.path.insert(0, _PACKAGES_DIR)


class ServiceState(StrEnum):
    """Service lifecycle state."""

    UNLOADED = "unloaded"
    LOADING = "loading"
    READY = "ready"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass(frozen=True, slots=True)
class ServiceStatus:
    """Health check result for a single service."""

    name: str
    state: ServiceState
    error: str | None = None
    module_path: str | None = None


# Map of service_name → package import path for lazy loading.
# Bare names resolve via the packages/ sys.path entry above.
# f"{_PKG}.*" entries are intra-package modules in packages/agnt_services/*.py.
_PKG = "packages.agnt_services"

_SERVICE_REGISTRY: dict[str, str] = {
    # ── External packages (packages/<name>/) ──────────────────────
    "speculation_engine": "speculation_engine",
    "auto_dream": "auto_dream",
    "context_compactor": "agnt_context_compactor",
    "telemetry": "telemetry",
    "token_estimation": "token_estimation",
    "vcr": "agnt_vcr",
    "terminal_notifier": "terminal_notifier",
    "magic_docs": "magic_docs",
    "plugin_manager": "plugin_manager",
    "session_recovery": "session_recovery",
    "sanitization": "sanitization",
    "feature_flags": "feature_flags",
    "tool_gateway": "tool_gateway",
    "tool_discovery": "tool_discovery",
    "plan_mode": "plan_mode",
    # ── Intra-package modules (packages/agnt_services/*.py) ───────
    "prevent_sleep": f"{_PKG}.prevent_sleep",
    "resilient_retry": f"{_PKG}.resilient_retry",
    "circuit_breaker": f"{_PKG}.circuit_breaker",
    "xml_tags": f"{_PKG}.xml_tags",
    "agent_summary": f"{_PKG}.agent_summary",
    "session_memory": f"{_PKG}.session_memory",
    "extract_memories": f"{_PKG}.extract_memories",
    "watchdog": f"{_PKG}.watchdog",
    "forked_agent": f"{_PKG}.forked_agent",
    "cron_scheduler": f"{_PKG}.cron_scheduler",
    "conversation_recovery": f"{_PKG}.conversation_recovery",
    "git_ops": f"{_PKG}.git_ops",
    "telemetry_events": f"{_PKG}.telemetry_events",
    "diagnostic_tracking": f"{_PKG}.diagnostic_tracking",
    "notifier": f"{_PKG}.notifier",
    "away_summary": f"{_PKG}.away_summary",
    "rate_limit_messages": f"{_PKG}.rate_limit_messages",
    # ── Batch 4 ported services ───────────────────────────────────
    "thinking_config": "thinking_config",
    "code_reasoning": "code_reasoning",
    "undercover": "undercover",
    "prompt_assembler": "prompt_assembler",
    "prompt_sections": "prompt_sections",
    "token_budget": "token_budget",
    "tool_limits": "tool_limits",
    "vcr_fixtures": "vcr_fixtures",
    "policy_limits": "tool_gateway.policy_limits",
    # ── Batch 5 ported services ───────────────────────────────────
    "agnt_classifier": "agnt_classifier",
    "agnt_bash_classifier": "agnt_bash_classifier",
    "agnt_tools": "agnt_tools",
    "agnt_compact": "agnt_compact",
    "agnt_context": "agnt_context",
    "deep_research": "deep_research",
    "mcp_tools": "mcp_tools",
    "repo_oracle": "repo_oracle",
    "collapse_read_search": "collapse_read_search",
    "evaluation_bridge": "evaluation_bridge",
    # ── Batch 6 ported services ───────────────────────────────────
    "tool_use_summary": f"{_PKG}.tool_use_summary",
    "tip_registry": f"{_PKG}.tip_registry",
    "settings_sync": f"{_PKG}.settings_sync",
    "team_memory_sync": f"{_PKG}.team_memory_sync",
    "mock_rate_limits": f"{_PKG}.mock_rate_limits",
    "internal_logging": f"{_PKG}.internal_logging",
    # ── Batch 7 ported services ───────────────────────────────────
    "oauth_service": f"{_PKG}.oauth_service",
    "remote_managed_settings": f"{_PKG}.remote_managed_settings",
    "lsp_client": f"{_PKG}.lsp_client",
    "voice_service": f"{_PKG}.voice_service",
    "tool_orchestration": f"{_PKG}.tool_orchestration",
    # ── Batch 8 ported services ───────────────────────────────────
    "mcp_channel": f"{_PKG}.mcp_channel_service",
    "session_memory_svc": f"{_PKG}.session_memory_service",
    "extract_memories_svc": f"{_PKG}.extract_memories_service",
    "token_estimation_svc": f"{_PKG}.token_estimation_service",
    "team_memory_sync_svc": f"{_PKG}.team_memory_sync_service",
}


@dataclass
class ServiceRegistry:
    """Central registry for lazy service initialization.

    Services are loaded on first access and cached for the process lifetime.
    Failed imports are recorded but do not crash the runtime.
    """

    _loaded: dict[str, object] = field(default_factory=dict)
    _errors: dict[str, str] = field(default_factory=dict)

    def get(self, name: str) -> object | None:
        """Get a loaded service module by name. Returns None if not available."""
        if name in self._loaded:
            return self._loaded[name]
        if name in self._errors:
            return None  # Already failed
        if name not in _SERVICE_REGISTRY:
            logger.warning("Unknown service: %s", name)
            return None

        module_path = _SERVICE_REGISTRY[name]
        try:
            mod = importlib.import_module(module_path)
            self._loaded[name] = mod
            return mod
        except ImportError as e:
            self._errors[name] = str(e)
            logger.debug("Service %s not available: %s", name, e)
            return None

    def status(self, name: str) -> ServiceStatus:
        """Get the current status of a named service."""
        if name in self._loaded:
            return ServiceStatus(
                name=name,
                state=ServiceState.READY,
                module_path=_SERVICE_REGISTRY.get(name),
            )
        if name in self._errors:
            return ServiceStatus(
                name=name,
                state=ServiceState.ERROR,
                error=self._errors[name],
                module_path=_SERVICE_REGISTRY.get(name),
            )
        return ServiceStatus(
            name=name,
            state=ServiceState.UNLOADED,
            module_path=_SERVICE_REGISTRY.get(name),
        )

    def all_statuses(self) -> list[ServiceStatus]:
        """Get status for all registered services."""
        return [self.status(name) for name in sorted(_SERVICE_REGISTRY)]


# Module-level singleton
_registry = ServiceRegistry()


def get_service(name: str) -> object | None:
    """Get a service by name from the global registry."""
    return _registry.get(name)


def get_service_status() -> list[ServiceStatus]:
    """Get health status for all registered services."""
    return _registry.all_statuses()


def health_check() -> dict[str, str | int]:
    """Run a health check across all registered services.

    Returns a dict with:
      - total: number of registered services
      - ready: number successfully imported
      - failed: number that failed to import
      - details: dict of service_name → 'ready' | error_message
    """
    details: dict[str, str] = {}
    ready = 0
    failed = 0
    for name in sorted(_SERVICE_REGISTRY):
        status = _registry.status(name)
        if status.state == ServiceState.READY:
            details[name] = "ready"
            ready += 1
        elif status.state == ServiceState.ERROR:
            details[name] = f"error: {status.error}"
            failed += 1
        else:
            # Force a load attempt
            svc = _registry.get(name)
            if svc is not None:
                details[name] = "ready"
                ready += 1
            else:
                details[name] = f"error: {_registry._errors.get(name, 'unknown')}"
                failed += 1

    return {
        "total": len(_SERVICE_REGISTRY),
        "ready": ready,
        "failed": failed,
        "details": details,
    }


__all__ = [
    "ServiceRegistry",
    "ServiceState",
    "ServiceStatus",
    "get_service",
    "get_service_status",
    "health_check",
]
