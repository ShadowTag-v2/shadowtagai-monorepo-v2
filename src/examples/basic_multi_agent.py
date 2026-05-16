# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Basic multi-agent system example using Google ADK patterns.

This example demonstrates how to create a simple multi-agent hierarchy
with parent-child relationships.
"""

import asyncio
import logging

from google.adk.agents.invocation_context import InvocationContext

from src.agents import AnalysisAgent, CoordinatorAgent, ResearchAgent, TaskAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def basic_multi_agent_example():
  """
  Demonstrates a basic multi-agent system with coordinator and specialized agents.
  """
  logger.info("=" * 60)
  logger.info("Basic Multi-Agent System Example")
  logger.info("=" * 60)

  # Create specialized sub-agents
  researcher = ResearchAgent(name="Researcher")
  analyzer = AnalysisAgent(name="Analyzer")
  task_executor = TaskAgent(name="TaskExecutor")

  # Create coordinator agent with sub-agents
  coordinator = CoordinatorAgent(
    name="MainCoordinator", sub_agents=[researcher, analyzer, task_executor]
  )

  # Print the agent hierarchy
  logger.info("\nAgent Hierarchy:")
  hierarchy = coordinator.get_hierarchy()
  logger.info(f"Coordinator: {hierarchy['name']}")
  for sub_agent in hierarchy["sub_agents"]:
    logger.info(f"  ├─ {sub_agent['name']} ({sub_agent.get('description', 'N/A')})")

  # Create invocation context
  context = InvocationContext(
    {
      "user_input": "Analyze market trends and provide insights",
      "task_type": "research_and_analysis",
    }
  )

  # Execute the multi-agent system
  logger.info("\nExecuting multi-agent system...")
  logger.info("-" * 60)

  results = []
  async for event in coordinator._run_async_impl(context):
    logger.info(f"Event from {event.agent_name}: {event.data}")
    results.append(event.data)

  logger.info("-" * 60)
  logger.info(f"\nCompleted with {len(results)} events")
  logger.info("=" * 60)

  return results


async def hierarchical_multi_agent_example():
  """
  Demonstrates a deeper hierarchical multi-agent system.
  """
  logger.info("=" * 60)
  logger.info("Hierarchical Multi-Agent System Example")
  logger.info("=" * 60)

  # Level 3: Leaf agents
  data_collector = TaskAgent(name="DataCollector", task_description="Collect data")
  data_validator = TaskAgent(name="DataValidator", task_description="Validate data")

  # Level 2: Mid-level coordinator
  data_team = CoordinatorAgent(
    name="DataTeamCoordinator", sub_agents=[data_collector, data_validator]
  )

  # Level 3: More leaf agents
  insight_generator = AnalysisAgent(name="InsightGenerator")
  report_builder = TaskAgent(name="ReportBuilder", task_description="Build reports")

  # Level 2: Another mid-level coordinator
  analysis_team = CoordinatorAgent(
    name="AnalysisTeamCoordinator", sub_agents=[insight_generator, report_builder]
  )

  # Level 1: Top-level coordinator
  master_coordinator = CoordinatorAgent(
    name="MasterCoordinator", sub_agents=[data_team, analysis_team]
  )

  # Print the full hierarchy
  logger.info("\nComplete Agent Hierarchy:")

  def print_hierarchy(agent_dict, level=0):
    indent = "  " * level
    logger.info(f"{indent}├─ {agent_dict['name']}")
    for sub in agent_dict.get("sub_agents", []):
      print_hierarchy(sub, level + 1)

  print_hierarchy(master_coordinator.get_hierarchy())

  # Execute the system
  context = InvocationContext(
    {"user_input": "Complete data analysis pipeline", "task_type": "full_pipeline"}
  )

  logger.info("\nExecuting hierarchical system...")
  logger.info("-" * 60)

  results = []
  async for event in master_coordinator._run_async_impl(context):
    logger.info(f"[{event.agent_name}] {event.data.get('status', 'N/A')}")
    results.append(event.data)

  logger.info("-" * 60)
  logger.info(f"\nCompleted with {len(results)} events")
  logger.info("=" * 60)

  return results


async def dynamic_agent_management_example():
  """
  Demonstrates dynamic addition and removal of sub-agents.
  """
  logger.info("=" * 60)
  logger.info("Dynamic Agent Management Example")
  logger.info("=" * 60)

  # Start with a coordinator with one agent
  initial_agent = TaskAgent(name="InitialAgent")
  coordinator = CoordinatorAgent(name="DynamicCoordinator", sub_agents=[initial_agent])

  logger.info("\nInitial hierarchy:")
  logger.info(coordinator.get_hierarchy())

  # Dynamically add more agents
  logger.info("\nAdding new agents dynamically...")
  coordinator.add_sub_agent(ResearchAgent(name="DynamicResearcher"))
  coordinator.add_sub_agent(AnalysisAgent(name="DynamicAnalyzer"))

  logger.info("\nUpdated hierarchy:")
  logger.info(coordinator.get_hierarchy())

  # Remove an agent
  logger.info("\nRemoving 'InitialAgent'...")
  removed = coordinator.remove_sub_agent("InitialAgent")
  logger.info(f"Removal successful: {removed}")

  logger.info("\nFinal hierarchy:")
  logger.info(coordinator.get_hierarchy())

  # Execute with the updated agent set
  context = InvocationContext(
    {"user_input": "Execute with dynamically configured agents", "task_type": "dynamic"}
  )

  logger.info("\nExecuting with dynamic agents...")
  results = []
  async for event in coordinator._run_async_impl(context):
    logger.info(f"[{event.agent_name}] {event.data.get('status', 'N/A')}")
    results.append(event.data)

  logger.info("=" * 60)
  return results


async def main():
  """Run all examples."""
  logger.info("\n" + "=" * 60)
  logger.info("GOOGLE ADK MULTI-AGENT EXAMPLES")
  logger.info("=" * 60 + "\n")

  # Run basic example
  await basic_multi_agent_example()
  await asyncio.sleep(1)

  # Run hierarchical example
  await hierarchical_multi_agent_example()
  await asyncio.sleep(1)

  # Run dynamic management example
  await dynamic_agent_management_example()

  logger.info("\n" + "=" * 60)
  logger.info("ALL EXAMPLES COMPLETED")
  logger.info("=" * 60 + "\n")


if __name__ == "__main__":
  asyncio.run(main())
