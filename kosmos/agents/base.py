# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Base Agent: Abstract base class for specialized Kosmos agents.

Each agent specializes in a specific aspect of autonomous research:
- Literature search and citation
- Data analysis and code generation
- Hypothesis generation
- Synthesis and report writing
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from collections.abc import Callable
from dataclasses import dataclass

from kosmos.core.orchestrator import ReActOrchestrator, ReActResult
from kosmos.core.world_model import KosmosWorldModel
from kosmos.core.vertex_client import VertexAIClient, GeminiModel


@dataclass
class AgentConfig:
    """Configuration for a specialized agent."""

    name: str
    model: GeminiModel
    instruction: str  # System instruction / agent role
    tools: list[str]  # Tool names this agent can use
    temperature: float = 0.7
    max_iterations: int = 20


class BaseAgent(ABC):
    """
    Abstract base class for specialized Kosmos agents.

    Each agent:
    1. Has a specific role/instruction
    2. Uses a tailored set of tools
    3. Operates via ReAct loop
    4. Updates the shared world model
    """

    def __init__(
        self,
        config: AgentConfig,
        vertex_client: VertexAIClient,
        world_model: KosmosWorldModel,
        tool_registry: dict[str, Callable],
    ):
        """
        Initialize base agent.

        Args:
            config: Agent configuration
            vertex_client: Vertex AI client for LLM calls
            world_model: Shared world model for state tracking
            tool_registry: Global registry of available tools
        """
        self.config = config
        self.vertex_client = vertex_client
        self.world_model = world_model

        # Extract tools for this agent from registry
        self.tools = {name: tool_registry[name] for name in config.tools if name in tool_registry}

        # Create ReAct orchestrator for this agent
        llm_client = vertex_client.get_model(config.model)
        self.orchestrator = ReActOrchestrator(
            llm_client=llm_client,
            tools=self.tools,
            world_model=world_model,
            max_iterations=config.max_iterations,
            temperature=config.temperature,
        )

    @abstractmethod
    def execute_task(self, task: str, context: dict[str, Any] | None = None) -> ReActResult:
        """
        Execute agent's specialized task.

        Args:
            task: Task description
            context: Optional context/parameters

        Returns:
            ReActResult with execution trace
        """
        pass

    def _build_goal_with_instruction(self, task: str) -> str:
        """
        Build goal prompt combining agent instruction with specific task.

        Args:
            task: Specific task to execute

        Returns:
            Formatted goal string for ReAct loop
        """
        return f"""
{self.config.instruction}

Specific task: {task}

Use your tools systematically and reason through each step.
"""

    def get_name(self) -> str:
        """Get agent name."""
        return self.config.name

    def get_capabilities(self) -> list[str]:
        """Get list of agent capabilities (tool names)."""
        return self.config.tools

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.config.name}, model={self.config.model.value}, tools={self.config.tools})"
