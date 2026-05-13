# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tengu Gate Infrastructure — Feature-gating and security enforcement.

This package provides a centralized, category-aware gate system for managing
security controls, entitlements, feature rollouts, and telemetry configuration
across the ShadowTag monorepo.

Modules:
    tengu_registry: Single source of truth for all gate definitions.
    tengu_evaluator: Unified evaluation engine with category-aware routing.
    tengu_security: Hardened enforcement layer for security-critical gates.
    tengu_entitlements: Subscription and feature access control.
    tengu_telemetry: Non-blocking analytics configuration.
    tengu_j6_bridge: Python-side gate enforcement for J6 governance.
"""

from gates.tengu_j6_bridge import (
  GateCategory,
  GateDefinition,
  HandoffRequest,
  enforce_zta_handoff,
  evaluate_gate,
  get_gate_diagnostics,
  is_security_gate_active,
)

__all__ = [
  "GateCategory",
  "GateDefinition",
  "HandoffRequest",
  "enforce_zta_handoff",
  "evaluate_gate",
  "get_gate_diagnostics",
  "is_security_gate_active",
]
