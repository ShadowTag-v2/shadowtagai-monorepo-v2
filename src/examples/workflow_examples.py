# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Workflow agent examples demonstrating Sequential, Parallel, Loop, and Conditional patterns.
"""

import asyncio
import logging

from google.adk.agents.invocation_context import InvocationContext

from src.agents import AnalysisAgent, TaskAgent, ValidationAgent
from src.workflows import (
  ConditionalWorkflowAgent,
  LoopWorkflowAgent,
  ParallelWorkflowAgent,
  SequentialWorkflowAgent,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def sequential_workflow_example():
  """
  Demonstrates sequential workflow where agents execute one after another.
  """
  logger.info("=" * 60)
  logger.info("Sequential Workflow Example")
  logger.info("=" * 60)

  # Create a data processing pipeline
  step1 = TaskAgent(name="DataFetcher", task_description="Fetch raw data")
  step2 = TaskAgent(name="DataProcessor", task_description="Process fetched data")
  step3 = AnalysisAgent(name="DataAnalyzer")
  step4 = ValidationAgent(name="ResultValidator")

  # Create sequential workflow
  pipeline = SequentialWorkflowAgent(
    name="DataProcessingPipeline",
    sub_agents=[step1, step2, step3, step4],
    description="Sequential data processing pipeline",
  )

  # Execute
  context = InvocationContext(
    {"user_input": "Process customer data and generate insights"}
  )

  logger.info("\nExecuting sequential pipeline...")
  logger.info("-" * 60)

  async for event in pipeline._run_async_impl(context):
    status = event.data.get("status", "N/A")
    step = event.data.get("step", "")
    agent = event.data.get("agent", event.agent_name)
    logger.info(f"[{agent}] {status} {f'(Step {step})' if step else ''}")

  logger.info("-" * 60)
  logger.info("Sequential workflow completed!")
  logger.info("=" * 60 + "\n")


async def parallel_workflow_example():
  """
  Demonstrates parallel workflow where agents execute concurrently.
  """
  logger.info("=" * 60)
  logger.info("Parallel Workflow Example")
  logger.info("=" * 60)

  # Create independent data gathering tasks
  news_fetcher = TaskAgent(name="NewsFetcher", task_description="Fetch news")
  weather_fetcher = TaskAgent(name="WeatherFetcher", task_description="Fetch weather")
  stock_fetcher = TaskAgent(name="StockFetcher", task_description="Fetch stock data")
  social_fetcher = TaskAgent(
    name="SocialFetcher", task_description="Fetch social media"
  )

  # Create parallel workflow
  parallel_gatherer = ParallelWorkflowAgent(
    name="DataGatherer",
    sub_agents=[news_fetcher, weather_fetcher, stock_fetcher, social_fetcher],
    description="Parallel data gathering",
    max_concurrent=2,  # Limit to 2 concurrent tasks
  )

  # Execute
  context = InvocationContext({"user_input": "Gather all data sources"})

  logger.info("\nExecuting parallel workflow...")
  logger.info("-" * 60)

  async for event in parallel_gatherer._run_async_impl(context):
    status = event.data.get("status", "N/A")
    logger.info(f"[{event.agent_name}] {status}")

  logger.info("-" * 60)
  logger.info("Parallel workflow completed!")
  logger.info("=" * 60 + "\n")


async def loop_workflow_example():
  """
  Demonstrates loop workflow for iterative processing.
  """
  logger.info("=" * 60)
  logger.info("Loop Workflow Example")
  logger.info("=" * 60)

  # Create an iterative refinement agent
  refiner = TaskAgent(name="DataRefiner", task_description="Refine data iteratively")

  # Create loop workflow with max iterations
  loop_processor = LoopWorkflowAgent(
    name="RefinementLoop",
    sub_agents=[refiner],
    max_iterations=5,
    description="Iterative data refinement",
  )

  # Execute
  context = InvocationContext({"user_input": "Refine data until quality threshold met"})

  logger.info("\nExecuting loop workflow...")
  logger.info("-" * 60)

  async for event in loop_processor._run_async_impl(context):
    status = event.data.get("status", "N/A")
    iteration = event.data.get("iteration", "")
    logger.info(
      f"[{event.agent_name}] {status} {f'(Iteration {iteration})' if iteration else ''}"
    )

  logger.info("-" * 60)
  logger.info("Loop workflow completed!")
  logger.info("=" * 60 + "\n")


async def conditional_workflow_example():
  """
  Demonstrates conditional workflow based on runtime conditions.
  """
  logger.info("=" * 60)
  logger.info("Conditional Workflow Example")
  logger.info("=" * 60)

  # Create different processing routes
  high_priority = TaskAgent(
    name="HighPriorityHandler", task_description="Handle high priority"
  )
  medium_priority = TaskAgent(
    name="MediumPriorityHandler", task_description="Handle medium priority"
  )
  low_priority = TaskAgent(
    name="LowPriorityHandler", task_description="Handle low priority"
  )
  default_handler = TaskAgent(
    name="DefaultHandler", task_description="Default handling"
  )

  # Create conditional workflow
  router = ConditionalWorkflowAgent(
    name="PriorityRouter",
    conditions=[
      (lambda ctx: ctx.get("priority", 0) >= 8, [high_priority]),
      (lambda ctx: ctx.get("priority", 0) >= 5, [medium_priority]),
      (lambda ctx: ctx.get("priority", 0) >= 2, [low_priority]),
    ],
    default_agents=[default_handler],
    description="Route based on priority level",
  )

  # Test with different priorities
  priorities = [9, 6, 3, 1]

  for priority in priorities:
    logger.info(f"\n--- Testing with priority: {priority} ---")

    context = InvocationContext(
      {"user_input": f"Process request with priority {priority}", "priority": priority}
    )

    async for event in router._run_async_impl(context):
      status = event.data.get("status", "N/A")
      logger.info(f"[{event.agent_name}] {status}")

  logger.info("-" * 60)
  logger.info("Conditional workflow completed!")
  logger.info("=" * 60 + "\n")


async def combined_workflow_example():
  """
  Demonstrates combining multiple workflow patterns.
  """
  logger.info("=" * 60)
  logger.info("Combined Workflow Example")
  logger.info("=" * 60)

  # Stage 1: Parallel data gathering
  fetcher1 = TaskAgent(name="Fetcher1")
  fetcher2 = TaskAgent(name="Fetcher2")
  parallel_stage = ParallelWorkflowAgent(
    name="GatherStage", sub_agents=[fetcher1, fetcher2]
  )

  # Stage 2: Sequential processing
  processor = TaskAgent(name="Processor")
  analyzer = AnalysisAgent(name="Analyzer")

  # Combine into a sequential pipeline
  combined_pipeline = SequentialWorkflowAgent(
    name="CombinedPipeline",
    sub_agents=[parallel_stage, processor, analyzer],
    description="Combined parallel and sequential workflow",
  )

  # Execute
  context = InvocationContext({"user_input": "Execute combined workflow pattern"})

  logger.info("\nExecuting combined workflow...")
  logger.info("-" * 60)

  async for event in combined_pipeline._run_async_impl(context):
    status = event.data.get("status", "N/A")
    logger.info(f"[{event.agent_name}] {status}")

  logger.info("-" * 60)
  logger.info("Combined workflow completed!")
  logger.info("=" * 60 + "\n")


async def main():
  """Run all workflow examples."""
  logger.info("\n" + "=" * 60)
  logger.info("WORKFLOW AGENT EXAMPLES")
  logger.info("=" * 60 + "\n")

  await sequential_workflow_example()
  await asyncio.sleep(0.5)

  await parallel_workflow_example()
  await asyncio.sleep(0.5)

  await loop_workflow_example()
  await asyncio.sleep(0.5)

  await conditional_workflow_example()
  await asyncio.sleep(0.5)

  await combined_workflow_example()

  logger.info("\n" + "=" * 60)
  logger.info("ALL WORKFLOW EXAMPLES COMPLETED")
  logger.info("=" * 60 + "\n")


if __name__ == "__main__":
  asyncio.run(main())
