"""
Antigravity Wrapper for Firebase Genkit.
Aligns Genkit initialization with the Antigravity/ShadowTag-v4 architecture.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from genkit.ai import Genkit
from genkit.core.action import Action

logger = logging.getLogger(__name__)


class GenkitInterface:
    """
    Wrapper for Genkit initialization and flow management.
    Ensures standard configuration across the Antigravity ecosystem.
    """

    def __init__(self, plugins: list[Any] | None = None) -> None:
        """
        Initialize the Genkit interface.

        Args:
            plugins: List of Genkit plugins to initialize.
        """
        self.plugins = plugins or []
        self._ai: Genkit | None = None
        self._initialized = False

    def initialize(self) -> Genkit:
        """
        Lazy initialization of the Genkit instance.
        """
        if not self._initialized:
            logger.info("Initializing Genkit with plugins: %s", self.plugins)
            # In a real implementation, we would pass plugins to genkit.
            # For now, we assume standard global initialization or similar pattern
            # depending on the exact SDK version nuances (Alpha).
            # This follows the pattern: ai = genkit.Genkit(plugins=...)
            self._ai = Genkit(plugins=self.plugins)
            self._initialized = True

        if self._ai is None:
            raise RuntimeError("Genkit failed to initialize.")

        return self._ai

    @property
    def ai(self) -> Genkit:
        """Access the underlying Genkit instance."""
        return self.initialize()

    def register_flow(self, name: str, func: Callable[..., Any]) -> Action:
        """
        Register a flow with the Genkit instance.

        Args:
           name: The name of the flow.
           func: The function to register as a flow.
        """
        logger.info("Registering Genkit flow: %s", name)
        # Using the decorator pattern programmatically if possible,
        # or just returning the decorated function.
        # The SDK usage is typically @ai.flow(name="...").
        # Here we apply it manually.
        return self.ai.flow(name=name)(func)


# Global singleton or factory access
_global_genkit: GenkitInterface | None = None


def get_genkit(plugins: list[Any] | None = None) -> GenkitInterface:
    """Get or create the global Genkit interface."""
    global _global_genkit
    if _global_genkit is None:
        _global_genkit = GenkitInterface(plugins=plugins)
    return _global_genkit
