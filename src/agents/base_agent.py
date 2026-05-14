# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Base agent implementation using Google ADK.

This module provides the foundation for building multi-agent systems
using Google's Agent Development Kit (ADK) with parent-child relationships.
"""

from typing import List, Optional, Dict, Any
from collections.abc import AsyncGenerator
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
import logging

logger = logging.getLogger(__name__)


class MultiAgent(BaseAgent):
    """
    Base multi-agent class that extends Google ADK's BaseAgent.

    This class demonstrates the core pattern for building multi-agent systems
    where agents can have sub-agents and coordinate their execution.

    Example:
        ```python
        # Create individual agents
        agent1 = MultiAgent(name="Agent1", model="gemini-2.5-flash")
        agent2 = MultiAgent(name="Agent2", model="gemini-2.5-flash")

        # Create coordinator with sub-agents
        coordinator = MultiAgent(
            name="Coordinator",
            model="gemini-2.5-flash",
            sub_agents=[agent1, agent2]
        )
        ```
    """

    def __init__(
        self,
        name: str,
        model: str = "gemini-2.5-flash",
        description: str | None = None,
        sub_agents: list[BaseAgent] | None = None,
        instructions: str | None = None,
        **kwargs,
    ):
        """
        Initialize a MultiAgent.

        Args:
            name: The name of the agent
            model: The model to use (default: gemini-2.5-flash)
            description: A description of the agent's purpose
            sub_agents: List of child agents to coordinate
            instructions: Specific instructions for the agent
            **kwargs: Additional arguments passed to BaseAgent
        """
        self.model = model
        self.instructions = instructions
        self._description = description

        # Initialize the base agent with sub_agents
        super().__init__(name=name, sub_agents=sub_agents or [], **kwargs)

    async def _run_async_impl(self, context: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        Implementation of the agent's execution logic.

        This method is called when the agent is invoked. Override this
        method in custom agents to implement specific behavior.

        Args:
            context: The invocation context containing request information

        Yields:
            Event: Events generated during agent execution
        """
        logger.info(f"Agent {self.name} starting execution")

        # Get the user's input from the context
        user_input = context.get("user_input", "")

        # If there are sub-agents, delegate to them
        if self.sub_agents:
            logger.info(f"Agent {self.name} delegating to {len(self.sub_agents)} sub-agents")
            for sub_agent in self.sub_agents:
                logger.info(f"Invoking sub-agent: {sub_agent.name}")
                # Invoke sub-agent and yield its events
                async for event in sub_agent._run_async_impl(context):
                    yield event
        else:
            # This is a leaf agent - perform actual work
            logger.info(f"Agent {self.name} performing work")

            # Create a simple response event
            # In a real implementation, this would call an LLM or perform tasks
            result = {
                "agent": self.name,
                "status": "completed",
                "message": f"Agent {self.name} processed: {user_input}",
                "description": self._description,
            }

            # Yield a completion event
            from google.adk.events import AgentEvent

            event = AgentEvent(agent_name=self.name, data=result)
            yield event

    def add_sub_agent(self, agent: BaseAgent) -> None:
        """
        Add a sub-agent to this agent's hierarchy.

        Args:
            agent: The sub-agent to add
        """
        if not self.sub_agents:
            self.sub_agents = []
        self.sub_agents.append(agent)
        logger.info(f"Added sub-agent {agent.name} to {self.name}")

    def remove_sub_agent(self, agent_name: str) -> bool:
        """
        Remove a sub-agent by name.

        Args:
            agent_name: The name of the sub-agent to remove

        Returns:
            bool: True if removed, False if not found
        """
        if not self.sub_agents:
            return False

        initial_count = len(self.sub_agents)
        self.sub_agents = [a for a in self.sub_agents if a.name != agent_name]

        removed = len(self.sub_agents) < initial_count
        if removed:
            logger.info(f"Removed sub-agent {agent_name} from {self.name}")
        return removed

    def get_hierarchy(self) -> dict[str, Any]:
        """
        Get the agent hierarchy as a dictionary.

        Returns:
            Dict: A dictionary representing the agent hierarchy
        """
        hierarchy = {"name": self.name, "description": self._description, "model": self.model, "sub_agents": []}

        if self.sub_agents:
            for sub_agent in self.sub_agents:
                if isinstance(sub_agent, MultiAgent):
                    hierarchy["sub_agents"].append(sub_agent.get_hierarchy())
                else:
                    hierarchy["sub_agents"].append({"name": sub_agent.name, "type": type(sub_agent).__name__})

        return hierarchy
