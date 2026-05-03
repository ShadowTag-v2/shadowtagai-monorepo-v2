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

This module provides:
  - ServiceRegistry: Central registry for lazy service initialization
  - ServiceStatus: Health check dataclass
  - get_service_status(): Quick diagnostics for all registered services
"""

from __future__ import annotations

import importlib
import logging
from dataclasses import dataclass, field
from enum import StrEnum

logger = logging.getLogger(__name__)


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


# Map of service_name → package import path for lazy loading
_SERVICE_REGISTRY: dict[str, str] = {
    "speculation_engine": "speculation_engine",
    "auto_dream": "auto_dream",
    "context_compactor": "context_compactor",
    "telemetry": "telemetry",
    "token_estimation": "token_estimation",
    "vcr": "vcr",
    "terminal_notifier": "terminal_notifier",
    "magic_docs": "magic_docs",
    "plugin_manager": "plugin_manager",
    "session_recovery": "session_recovery",
    "prevent_sleep": "prevent_sleep",
    "sanitization": "sanitization",
    "feature_flags": "feature_flags",
    "tool_gateway": "tool_gateway",
    "tool_discovery": "tool_discovery",
    "plan_mode": "plan_mode",
    "resilient_retry": "resilient_retry",
    "circuit_breaker": "circuit_breaker",
    # V14.1 additions — remaining ported services
    "thinking_config": "thinking_config",
    "xml_tags": "xml_tags",
    "code_reasoning": "code_reasoning",
    "undercover": "undercover",
    "prompt_assembler": "prompt_assembler",
    "prompt_sections": "prompt_sections",
    "token_budget": "token_budget",
    "tool_limits": "tool_limits",
    "vcr_fixtures": "vcr_fixtures",
    # V15 expansion — unported src/services/ modules (stubs for tracking)
    "agent_summary": "agent_summary",
    "session_memory": "session_memory",
    "extract_memories": "extract_memories",
    "policy_limits": "policy_limits",
    "analytics": "analytics",
    "oauth_flow": "oauth_flow",
    "voice_modality": "voice_modality",
    "watchdog": "watchdog",
    # V2.2.0 foundation modules — ported from src/utils/
    "forked_agent": "forked_agent",
    "cron_scheduler": "cron_scheduler",
    "conversation_recovery": "conversation_recovery",
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
