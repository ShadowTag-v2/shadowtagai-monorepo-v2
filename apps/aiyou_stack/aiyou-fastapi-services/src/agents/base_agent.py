# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Base agent class for all AI agents"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any


class BaseAgent(ABC):
    """Base class for all AI agents in the system"""

    def __init__(self, name: str, system_prompt: str, config: dict[str, Any] | None = None):
        """Initialize base agent

        Args:
            name: Agent name
            system_prompt: System prompt for the agent
            config: Agent configuration dictionary

        """
        self.name = name
        self.system_prompt = system_prompt
        self.config = config or {}

    @abstractmethod
    async def process(
        self,
        prompt: str,
        context: dict[str, Any] | None = None,
        stream: bool = False,
    ) -> AsyncIterator[str] | dict[str, Any]:
        """Process user request through the agent

        Args:
            prompt: User input/request
            context: Additional context for the request
            stream: Whether to stream the response

        Returns:
            Agent response (streamed or complete)

        """

    def get_info(self) -> dict[str, Any]:
        """Get agent information"""
        return {"name": self.name, "config": self.config, "capabilities": self.get_capabilities()}

    @abstractmethod
    def get_capabilities(self) -> list[str]:
        """Get list of agent capabilities"""

    def validate_input(self, prompt: str, context: dict | None = None) -> bool:
        """Validate input before processing

        Args:
            prompt: User prompt
            context: Request context

        Returns:
            True if valid, False otherwise

        """
        return not (not prompt or not prompt.strip())
