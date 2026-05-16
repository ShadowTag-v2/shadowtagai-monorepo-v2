# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Tools and utilities for managing agents in multi-agent systems.
"""

import logging

from google.adk.agents import BaseAgent

logger = logging.getLogger(__name__)


class AgentRegistry:
  """
  Registry for managing and discovering agents.

  This class provides a centralized registry for agent types,
  allowing for dynamic agent creation and management.
  """

  def __init__(self):
    """Initialize the agent registry."""
    self._agents: dict[str, type[BaseAgent]] = {}
    self._instances: dict[str, BaseAgent] = {}

  def register(self, name: str, agent_class: type[BaseAgent]) -> None:
    """
    Register an agent class.

    Args:
        name: The name to register the agent under
        agent_class: The agent class to register
    """
    self._agents[name] = agent_class
    logger.info(f"Registered agent type: {name}")

  def unregister(self, name: str) -> bool:
    """
    Unregister an agent class.

    Args:
        name: The name of the agent to unregister

    Returns:
        bool: True if unregistered, False if not found
    """
    if name in self._agents:
      del self._agents[name]
      logger.info(f"Unregistered agent type: {name}")
      return True
    return False

  def get_agent_class(self, name: str) -> type[BaseAgent] | None:
    """
    Get a registered agent class.

    Args:
        name: The name of the agent class

    Returns:
        Optional[Type[BaseAgent]]: The agent class or None if not found
    """
    return self._agents.get(name)

  def create_agent(self, name: str, instance_name: str, **kwargs) -> BaseAgent | None:
    """
    Create an agent instance from a registered class.

    Args:
        name: The name of the registered agent class
        instance_name: The name for the agent instance
        **kwargs: Additional arguments for agent initialization

    Returns:
        Optional[BaseAgent]: The created agent instance or None if not found
    """
    agent_class = self._agents.get(name)
    if agent_class:
      instance = agent_class(name=instance_name, **kwargs)
      self._instances[instance_name] = instance
      logger.info(f"Created agent instance: {instance_name} of type {name}")
      return instance
    return None

  def get_instance(self, instance_name: str) -> BaseAgent | None:
    """
    Get a created agent instance.

    Args:
        instance_name: The name of the agent instance

    Returns:
        Optional[BaseAgent]: The agent instance or None if not found
    """
    return self._instances.get(instance_name)

  def list_registered(self) -> list[str]:
    """
    List all registered agent types.

    Returns:
        List[str]: List of registered agent type names
    """
    return list(self._agents.keys())

  def list_instances(self) -> list[str]:
    """
    List all created agent instances.

    Returns:
        List[str]: List of agent instance names
    """
    return list(self._instances.keys())


class AgentManager:
  """
  Manager for orchestrating and monitoring agents.

  This class provides high-level management capabilities for
  multi-agent systems, including lifecycle management and monitoring.
  """

  def __init__(self):
    """Initialize the agent manager."""
    self._active_agents: dict[str, BaseAgent] = {}
    self._agent_stats: dict[str, dict] = {}

  def add_agent(self, agent: BaseAgent) -> None:
    """
    Add an agent to management.

    Args:
        agent: The agent to add
    """
    self._active_agents[agent.name] = agent
    self._agent_stats[agent.name] = {
      "executions": 0,
      "errors": 0,
      "last_execution": None,
    }
    logger.info(f"Added agent to manager: {agent.name}")

  def remove_agent(self, agent_name: str) -> bool:
    """
    Remove an agent from management.

    Args:
        agent_name: The name of the agent to remove

    Returns:
        bool: True if removed, False if not found
    """
    if agent_name in self._active_agents:
      del self._active_agents[agent_name]
      if agent_name in self._agent_stats:
        del self._agent_stats[agent_name]
      logger.info(f"Removed agent from manager: {agent_name}")
      return True
    return False

  def get_agent(self, agent_name: str) -> BaseAgent | None:
    """
    Get a managed agent.

    Args:
        agent_name: The name of the agent

    Returns:
        Optional[BaseAgent]: The agent or None if not found
    """
    return self._active_agents.get(agent_name)

  def list_agents(self) -> list[str]:
    """
    List all managed agents.

    Returns:
        List[str]: List of managed agent names
    """
    return list(self._active_agents.keys())

  def get_stats(self, agent_name: str) -> dict | None:
    """
    Get statistics for an agent.

    Args:
        agent_name: The name of the agent

    Returns:
        Optional[Dict]: Agent statistics or None if not found
    """
    return self._agent_stats.get(agent_name)

  def record_execution(self, agent_name: str, success: bool = True) -> None:
    """
    Record an agent execution.

    Args:
        agent_name: The name of the agent
        success: Whether the execution was successful
    """
    if agent_name in self._agent_stats:
      stats = self._agent_stats[agent_name]
      stats["executions"] += 1
      if not success:
        stats["errors"] += 1
      stats["last_execution"] = "now"  # In real implementation, use datetime

  def get_all_stats(self) -> dict[str, dict]:
    """
    Get statistics for all managed agents.

    Returns:
        Dict[str, Dict]: Dictionary of agent statistics
    """
    return self._agent_stats.copy()


# Global registry and manager instances
global_registry = AgentRegistry()
global_manager = AgentManager()
