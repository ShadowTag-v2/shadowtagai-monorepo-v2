# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Copyright 2026 ShadowTagAI. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Function Registry — tracks approved functions with risk classification.

Every function that the AI model can call MUST be registered here first.
Unregistered functions are rejected by the bridge.
"""

from __future__ import annotations

import enum
import inspect
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


class RiskTier(enum.StrEnum):
    """Risk classification per tool_contracts/firebase.function_bridge.yaml."""

    LOW = "low"  # Read-only queries, search, calculations
    MEDIUM = "medium"  # State mutation, preference writes
    HIGH = "high"  # Payment, auth changes, PII access
    CRITICAL = "critical"  # Destructive ops, deployment, money movement

    @property
    def requires_confirmation(self) -> bool:
        """HIGH and CRITICAL require user confirmation before execution."""
        return self in (RiskTier.HIGH, RiskTier.CRITICAL)


# Actions that always require confirmation regardless of risk tier.
# Sourced from tool_contracts/firebase.function_bridge.yaml confirmation_required_for.
CONFIRMATION_ACTIONS: frozenset[str] = frozenset(
    {
        "purchase",
        "deployment",
        "data_delete",
        "data_write_sensitive",
        "github_push",
        "external_api_mutation",
        "money_movement",
        "user_notification_broadcast",
    }
)


@dataclass(frozen=True, slots=True)
class RegisteredFunction:
    """A function registered with the bridge."""

    name: str
    callable: Callable[..., Any]
    risk_tier: RiskTier
    description: str
    action_tags: frozenset[str] = field(default_factory=frozenset)

    @property
    def requires_confirmation(self) -> bool:
        """Check if this function requires user confirmation."""
        if self.risk_tier.requires_confirmation:
            return True
        return bool(self.action_tags & CONFIRMATION_ACTIONS)


class FunctionRegistry:
    """Thread-safe registry of approved functions.

    Usage:
        registry = FunctionRegistry()
        registry.register("get_weather", get_weather, RiskTier.LOW,
                          description="Fetch weather for a city.")
        fn = registry.get("get_weather")
    """

    def __init__(self, *, max_functions: int = 128) -> None:
        """Initialize the registry.

        Args:
            max_functions: Maximum number of registered functions.
                Firebase AI Logic supports up to 128 function declarations.
        """
        self._functions: dict[str, RegisteredFunction] = {}
        self._max_functions = max_functions

    def register(
        self,
        name: str,
        fn: Callable[..., Any],
        risk_tier: RiskTier,
        *,
        description: str = "",
        action_tags: frozenset[str] | None = None,
    ) -> RegisteredFunction:
        """Register a function for use by the AI model.

        Args:
            name: Unique function name matching the FunctionDeclaration name.
            fn: The Python callable to execute.
            risk_tier: Risk classification for this function.
            description: Human-readable description. If empty, extracted from docstring.
            action_tags: Optional set of action tags for confirmation gating.

        Returns:
            The registered function record.

        Raises:
            ValueError: If name is already registered or registry is full.
        """
        if name in self._functions:
            msg = f"Function '{name}' is already registered."
            raise ValueError(msg)
        if len(self._functions) >= self._max_functions:
            msg = f"Registry full ({self._max_functions} functions). Cannot register '{name}'."
            raise ValueError(msg)

        if not description:
            description = inspect.getdoc(fn) or f"Function: {name}"

        registered = RegisteredFunction(
            name=name,
            callable=fn,
            risk_tier=risk_tier,
            description=description,
            action_tags=action_tags or frozenset(),
        )
        self._functions[name] = registered
        logger.info("Registered function '%s' (risk=%s)", name, risk_tier.value)
        return registered

    def get(self, name: str) -> RegisteredFunction | None:
        """Look up a registered function by name."""
        return self._functions.get(name)

    def list_all(self) -> list[RegisteredFunction]:
        """Return all registered functions sorted by name."""
        return sorted(self._functions.values(), key=lambda f: f.name)

    def unregister(self, name: str) -> bool:
        """Remove a function from the registry.

        Returns:
            True if the function was found and removed, False otherwise.
        """
        if name in self._functions:
            del self._functions[name]
            logger.info("Unregistered function '%s'", name)
            return True
        return False

    @property
    def count(self) -> int:
        """Number of registered functions."""
        return len(self._functions)

    def __contains__(self, name: str) -> bool:
        return name in self._functions

    def __len__(self) -> int:
        return len(self._functions)
