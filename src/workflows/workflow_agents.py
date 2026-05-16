# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Workflow agent implementations based on Google ADK patterns.

This module provides specialized workflow agents that orchestrate
the execution of sub-agents in different patterns:
- Sequential: Execute sub-agents one after another
- Parallel: Execute sub-agents concurrently
- Loop: Execute sub-agents iteratively
- Conditional: Execute sub-agents based on conditions
"""

import asyncio
import logging
from collections.abc import AsyncGenerator, Callable
from typing import Any

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import AgentEvent, Event

logger = logging.getLogger(__name__)


class SequentialWorkflowAgent(BaseAgent):
  """
  Sequential workflow agent that executes sub-agents one after another.

  This agent runs sub-agents in sequence, where each agent's output
  can be passed to the next agent in the pipeline.

  Example:
      ```python
      from google.adk.agents import LlmAgent

      step1 = LlmAgent(name="DataFetch", output_key="raw_data")
      step2 = LlmAgent(name="DataProcess", instruction="Process {raw_data}")
      step3 = LlmAgent(name="DataAnalyze", instruction="Analyze processed data")

      pipeline = SequentialWorkflowAgent(
          name="DataPipeline",
          sub_agents=[step1, step2, step3]
      )
      ```
  """

  def __init__(
    self,
    name: str,
    sub_agents: list[BaseAgent],
    description: str | None = None,
    **kwargs,
  ):
    """
    Initialize a SequentialWorkflowAgent.

    Args:
        name: The name of the workflow
        sub_agents: List of agents to execute sequentially
        description: Description of the workflow
        **kwargs: Additional arguments
    """
    super().__init__(name=name, sub_agents=sub_agents, **kwargs)
    self._description = description or "Sequential workflow execution"
    self.results: list[dict[str, Any]] = []

  async def _run_async_impl(self, context: InvocationContext) -> AsyncGenerator[Event]:
    """
    Execute sub-agents sequentially.

    Each sub-agent runs after the previous one completes.
    Results are accumulated and can be passed between agents.
    """
    logger.info(
      f"SequentialWorkflowAgent {self.name} starting with {len(self.sub_agents)} agents"
    )

    yield AgentEvent(
      agent_name=self.name,
      data={
        "status": "started",
        "workflow_type": "sequential",
        "total_agents": len(self.sub_agents),
      },
    )

    self.results = []

    for idx, sub_agent in enumerate(self.sub_agents, 1):
      logger.info(f"Executing step {idx}/{len(self.sub_agents)}: {sub_agent.name}")

      # Create context for this step, including previous results
      step_context = context.copy()
      step_context["step_number"] = idx
      step_context["previous_results"] = self.results

      yield AgentEvent(
        agent_name=self.name,
        data={"status": "executing_step", "step": idx, "agent": sub_agent.name},
      )

      # Execute the sub-agent and collect events
      step_results = []
      async for event in sub_agent._run_async_impl(step_context):
        # Pass through the event
        yield event

        # Collect results if it's an AgentEvent
        if isinstance(event, AgentEvent):
          step_results.append(event.data)

      # Store results for next steps
      self.results.append(
        {"step": idx, "agent": sub_agent.name, "results": step_results}
      )

      yield AgentEvent(
        agent_name=self.name,
        data={"status": "step_completed", "step": idx, "agent": sub_agent.name},
      )

    yield AgentEvent(
      agent_name=self.name,
      data={
        "status": "completed",
        "workflow_type": "sequential",
        "total_steps": len(self.sub_agents),
        "results": self.results,
      },
    )


class ParallelWorkflowAgent(BaseAgent):
  """
  Parallel workflow agent that executes sub-agents concurrently.

  This agent runs all sub-agents in parallel, useful for independent
  tasks that can be executed simultaneously.

  Example:
      ```python
      from google.adk.agents import LlmAgent

      task1 = LlmAgent(name="FetchNews")
      task2 = LlmAgent(name="FetchWeather")
      task3 = LlmAgent(name="FetchStocks")

      parallel = ParallelWorkflowAgent(
          name="DataGatherer",
          sub_agents=[task1, task2, task3]
      )
      ```
  """

  def __init__(
    self,
    name: str,
    sub_agents: list[BaseAgent],
    description: str | None = None,
    max_concurrent: int | None = None,
    **kwargs,
  ):
    """
    Initialize a ParallelWorkflowAgent.

    Args:
        name: The name of the workflow
        sub_agents: List of agents to execute in parallel
        description: Description of the workflow
        max_concurrent: Maximum number of concurrent executions (None = unlimited)
        **kwargs: Additional arguments
    """
    super().__init__(name=name, sub_agents=sub_agents, **kwargs)
    self._description = description or "Parallel workflow execution"
    self.max_concurrent = max_concurrent
    self.results: list[dict[str, Any]] = []

  async def _run_async_impl(self, context: InvocationContext) -> AsyncGenerator[Event]:
    """
    Execute sub-agents in parallel.

    All sub-agents run concurrently, with optional concurrency limits.
    """
    logger.info(
      f"ParallelWorkflowAgent {self.name} starting with {len(self.sub_agents)} agents"
    )

    yield AgentEvent(
      agent_name=self.name,
      data={
        "status": "started",
        "workflow_type": "parallel",
        "total_agents": len(self.sub_agents),
        "max_concurrent": self.max_concurrent,
      },
    )

    self.results = []

    async def execute_agent(agent: BaseAgent, idx: int):
      """Execute a single agent and collect results."""
      logger.info(f"Executing parallel task {idx}: {agent.name}")

      agent_context = context.copy()
      agent_context["parallel_index"] = idx

      events = []
      async for event in agent._run_async_impl(agent_context):
        events.append(event)

      return {"index": idx, "agent": agent.name, "events": events}

    # Create tasks for all sub-agents
    tasks = [execute_agent(agent, idx) for idx, agent in enumerate(self.sub_agents)]

    # Execute with optional concurrency limit
    if self.max_concurrent:
      # Execute in batches
      for i in range(0, len(tasks), self.max_concurrent):
        batch = tasks[i : i + self.max_concurrent]
        batch_results = await asyncio.gather(*batch)
        self.results.extend(batch_results)

        yield AgentEvent(
          agent_name=self.name,
          data={
            "status": "batch_completed",
            "batch_number": i // self.max_concurrent + 1,
            "completed_count": min(i + self.max_concurrent, len(tasks)),
          },
        )
    else:
      # Execute all at once
      self.results = await asyncio.gather(*tasks)

    # Emit all collected events
    for result in self.results:
      for event in result.get("events", []):
        yield event

    yield AgentEvent(
      agent_name=self.name,
      data={
        "status": "completed",
        "workflow_type": "parallel",
        "total_agents": len(self.sub_agents),
        "results_count": len(self.results),
      },
    )


class LoopWorkflowAgent(BaseAgent):
  """
  Loop workflow agent that executes sub-agents iteratively.

  This agent runs sub-agents in a loop until a condition is met
  or a maximum iteration count is reached.

  Example:
      ```python
      from google.adk.agents import LlmAgent

      processor = LlmAgent(name="DataProcessor")

      loop = LoopWorkflowAgent(
          name="ProcessLoop",
          sub_agents=[processor],
          max_iterations=10,
          condition=lambda ctx: ctx.get("is_complete", False)
      )
      ```
  """

  def __init__(
    self,
    name: str,
    sub_agents: list[BaseAgent],
    max_iterations: int = 10,
    condition: Callable[[InvocationContext], bool] | None = None,
    description: str | None = None,
    **kwargs,
  ):
    """
    Initialize a LoopWorkflowAgent.

    Args:
        name: The name of the workflow
        sub_agents: List of agents to execute in loop
        max_iterations: Maximum number of iterations
        condition: Optional function to determine when to stop (returns True to stop)
        description: Description of the workflow
        **kwargs: Additional arguments
    """
    super().__init__(name=name, sub_agents=sub_agents, **kwargs)
    self._description = description or "Loop workflow execution"
    self.max_iterations = max_iterations
    self.condition = condition
    self.iteration_results: list[dict[str, Any]] = []

  async def _run_async_impl(self, context: InvocationContext) -> AsyncGenerator[Event]:
    """
    Execute sub-agents in a loop.

    Continues until condition is met or max iterations reached.
    """
    logger.info(
      f"LoopWorkflowAgent {self.name} starting with max {self.max_iterations} iterations"
    )

    yield AgentEvent(
      agent_name=self.name,
      data={
        "status": "started",
        "workflow_type": "loop",
        "max_iterations": self.max_iterations,
      },
    )

    self.iteration_results = []

    for iteration in range(1, self.max_iterations + 1):
      logger.info(f"Loop iteration {iteration}/{self.max_iterations}")

      # Check condition
      if self.condition and self.condition(context):
        logger.info(f"Loop condition met at iteration {iteration}")
        yield AgentEvent(
          agent_name=self.name, data={"status": "condition_met", "iteration": iteration}
        )
        break

      yield AgentEvent(
        agent_name=self.name,
        data={"status": "iteration_started", "iteration": iteration},
      )

      iteration_events = []

      # Execute all sub-agents in this iteration
      for sub_agent in self.sub_agents:
        loop_context = context.copy()
        loop_context["iteration"] = iteration
        loop_context["previous_iterations"] = self.iteration_results

        async for event in sub_agent._run_async_impl(loop_context):
          yield event
          if isinstance(event, AgentEvent):
            iteration_events.append(event.data)

      # Store iteration results
      self.iteration_results.append(
        {"iteration": iteration, "events": iteration_events}
      )

      yield AgentEvent(
        agent_name=self.name,
        data={"status": "iteration_completed", "iteration": iteration},
      )

    yield AgentEvent(
      agent_name=self.name,
      data={
        "status": "completed",
        "workflow_type": "loop",
        "total_iterations": len(self.iteration_results),
        "results": self.iteration_results,
      },
    )


class ConditionalWorkflowAgent(BaseAgent):
  """
  Conditional workflow agent that executes sub-agents based on conditions.

  This agent evaluates conditions and routes execution to different
  sub-agents accordingly (similar to if-else logic).

  Example:
      ```python
      from google.adk.agents import LlmAgent

      route_a = LlmAgent(name="RouteA")
      route_b = LlmAgent(name="RouteB")
      default_route = LlmAgent(name="Default")

      conditional = ConditionalWorkflowAgent(
          name="Router",
          conditions=[
              (lambda ctx: ctx.get("score", 0) > 0.8, [route_a]),
              (lambda ctx: ctx.get("score", 0) > 0.5, [route_b]),
          ],
          default_agents=[default_route]
      )
      ```
  """

  def __init__(
    self,
    name: str,
    conditions: list[tuple[Callable[[InvocationContext], bool], list[BaseAgent]]],
    default_agents: list[BaseAgent] | None = None,
    description: str | None = None,
    **kwargs,
  ):
    """
    Initialize a ConditionalWorkflowAgent.

    Args:
        name: The name of the workflow
        conditions: List of (condition_function, agents) tuples
        default_agents: Agents to execute if no condition matches
        description: Description of the workflow
        **kwargs: Additional arguments
    """
    # Collect all possible sub-agents
    all_agents = []
    for _, agents in conditions:
      all_agents.extend(agents)
    if default_agents:
      all_agents.extend(default_agents)

    super().__init__(name=name, sub_agents=all_agents, **kwargs)
    self._description = description or "Conditional workflow execution"
    self.conditions = conditions
    self.default_agents = default_agents or []

  async def _run_async_impl(self, context: InvocationContext) -> AsyncGenerator[Event]:
    """
    Execute sub-agents based on conditions.

    Evaluates conditions in order and executes corresponding agents.
    """
    logger.info(f"ConditionalWorkflowAgent {self.name} evaluating conditions")

    yield AgentEvent(
      agent_name=self.name,
      data={
        "status": "started",
        "workflow_type": "conditional",
        "conditions_count": len(self.conditions),
      },
    )

    # Evaluate conditions
    matched = False
    for idx, (condition, agents) in enumerate(self.conditions):
      try:
        if condition(context):
          logger.info(f"Condition {idx} matched, executing {len(agents)} agents")

          yield AgentEvent(
            agent_name=self.name,
            data={
              "status": "condition_matched",
              "condition_index": idx,
              "agents_count": len(agents),
            },
          )

          # Execute matched agents
          for agent in agents:
            async for event in agent._run_async_impl(context):
              yield event

          matched = True
          break
      except Exception as e:
        logger.error(f"Error evaluating condition {idx}: {e}")
        yield AgentEvent(
          agent_name=self.name,
          data={"status": "condition_error", "condition_index": idx, "error": str(e)},
        )

    # Execute default agents if no condition matched
    if not matched and self.default_agents:
      logger.info(
        f"No conditions matched, executing {len(self.default_agents)} default agents"
      )

      yield AgentEvent(
        agent_name=self.name,
        data={"status": "executing_default", "agents_count": len(self.default_agents)},
      )

      for agent in self.default_agents:
        async for event in agent._run_async_impl(context):
          yield event

    yield AgentEvent(
      agent_name=self.name,
      data={"status": "completed", "workflow_type": "conditional", "matched": matched},
    )
