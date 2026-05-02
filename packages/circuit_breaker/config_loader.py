# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Circuit Breaker — YAML-based service profile loader.

Reads ``service_profiles.yaml`` and pre-registers all service breakers
in a CircuitBreakerRegistry. This decouples service configuration from
application code — add/tune services without touching Python.

Usage::

    from circuit_breaker.config_loader import load_profiles

    registry = load_profiles()  # Uses default_registry + service_profiles.yaml
    breaker = registry.get("firestore")
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from circuit_breaker.registry import CircuitBreakerRegistry
from circuit_breaker.telemetry_bridge import default_registry

logger = logging.getLogger(__name__)

_DEFAULT_PROFILES_PATH = Path(__file__).parent / "service_profiles.yaml"


def load_profiles(
    *,
    profiles_path: Path | None = None,
    registry: CircuitBreakerRegistry | None = None,
) -> CircuitBreakerRegistry:
    """Load service profiles from YAML and register breakers.

    Args:
        profiles_path: Path to the YAML config. Defaults to
            ``packages/circuit_breaker/service_profiles.yaml``.
        registry: Registry to populate. Defaults to the global
            telemetry-wired ``default_registry``.

    Returns:
        The populated CircuitBreakerRegistry.
    """
    target_registry = registry if registry is not None else default_registry
    config_path = profiles_path or _DEFAULT_PROFILES_PATH

    if not config_path.exists():
        logger.warning("Service profiles not found at %s — no breakers pre-registered", config_path)
        return target_registry

    try:
        import yaml  # type: ignore[import-untyped]

        raw = yaml.safe_load(config_path.read_text())
    except ImportError:
        logger.debug("PyYAML not installed — falling back to manual registration")
        return target_registry
    except Exception as exc:
        logger.error("Failed to parse service profiles: %s", exc)
        return target_registry

    services: dict[str, dict[str, Any]] = raw.get("services", {})

    for service_name, profile in services.items():
        target_registry.register(
            service_name=service_name,
            failure_threshold=profile.get("failure_threshold", 3),
            reset_timeout_s=float(profile.get("reset_timeout_s", 60.0)),
            half_open_max_probes=profile.get("half_open_max_probes", 1),
        )

    logger.info(
        "Loaded %d circuit breaker profiles from %s",
        len(services),
        config_path.name,
    )
    return target_registry
