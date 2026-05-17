# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
FastAPI application for multi-agent system.

This module provides a RESTful API for interacting with the multi-agent system.
"""

import logging
import os
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.adk.agents.invocation_context import InvocationContext
from pydantic import BaseModel, Field

from src.agents import (
  AnalysisAgent,
  CoordinatorAgent,
  ResearchAgent,
  TaskAgent,
  ValidationAgent,
)
from src.workflows import (
  ConditionalWorkflowAgent,
  LoopWorkflowAgent,
  ParallelWorkflowAgent,
  SequentialWorkflowAgent,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
  title="Multi-Agent System API",
  description="API for interacting with Google ADK-based multi-agent systems",
  version="1.0.0",
)

# Add CORS middleware
_cors_origins = os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
  CORSMiddleware,
  allow_origins=_cors_origins,
  allow_credentials=True,
  allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
  allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)


# Pydantic models for request/response
class AgentRequest(BaseModel):
  """Request model for agent execution."""

  user_input: str = Field(..., description="User input to process")
  task_type: str | None = Field("general", description="Type of task")
  context: dict[str, Any] | None = Field(
    default_factory=dict, description="Additional context"
  )


class AgentResponse(BaseModel):
  """Response model for agent execution."""

  success: bool
  message: str
  events: list[dict[str, Any]]
  agent_hierarchy: dict[str, Any] | None = None


class WorkflowRequest(BaseModel):
  """Request model for workflow execution."""

  workflow_type: str = Field(
    ..., description="Type of workflow: sequential, parallel, loop, conditional"
  )
  user_input: str = Field(..., description="User input to process")
  context: dict[str, Any] | None = Field(
    default_factory=dict, description="Additional context"
  )
  max_iterations: int | None = Field(5, description="Max iterations for loop workflow")
  max_concurrent: int | None = Field(
    None, description="Max concurrent tasks for parallel workflow"
  )


class AgentHierarchyResponse(BaseModel):
  """Response model for agent hierarchy."""

  name: str
  description: str | None = None
  model: str | None = None
  sub_agents: list[dict[str, Any]]


# Initialize default multi-agent system
def create_default_coordinator():
  """Create a default multi-agent coordinator."""
  researcher = ResearchAgent(name="DefaultResearcher")
  analyzer = AnalysisAgent(name="DefaultAnalyzer")
  task_executor = TaskAgent(name="DefaultTaskExecutor")

  coordinator = CoordinatorAgent(
    name="DefaultCoordinator", sub_agents=[researcher, analyzer, task_executor]
  )

  return coordinator


# Global coordinator instance
default_coordinator = create_default_coordinator()


@app.get("/")
async def root():
  """Root endpoint."""
  return {
    "message": "Multi-Agent System API",
    "version": "1.0.0",
    "endpoints": {
      "execute": "/api/agents/execute",
      "workflow": "/api/workflows/execute",
      "hierarchy": "/api/agents/hierarchy",
    },
  }


@app.get("/health")
@app.get("/healthz")
async def health_check():
  """Health check endpoint (Cloud Run compatible)."""
  return {"status": "healthy", "service": "multi-agent-system"}


@app.post("/api/agents/execute", response_model=AgentResponse)
async def execute_agent(request: AgentRequest):
  """
  Execute the default multi-agent coordinator.

  Args:
      request: Agent execution request

  Returns:
      AgentResponse with execution results
  """
  try:
    logger.info(f"Executing agent with input: {request.user_input}")

    # Create invocation context
    context = InvocationContext(
      {
        "user_input": request.user_input,
        "task_type": request.task_type,
        **request.context,
      }
    )

    # Execute agent and collect events
    events = []
    async for event in default_coordinator._run_async_impl(context):
      event_data = {"agent_name": event.agent_name, "data": event.data}
      events.append(event_data)

    # Get agent hierarchy
    hierarchy = default_coordinator.get_hierarchy()

    return AgentResponse(
      success=True,
      message=f"Successfully executed agent with {len(events)} events",
      events=events,
      agent_hierarchy=hierarchy,
    )

  except Exception as e:
    logger.error(f"Error executing agent: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/workflows/execute", response_model=AgentResponse)
async def execute_workflow(request: WorkflowRequest):
  """
  Execute a specific workflow type.

  Args:
      request: Workflow execution request

  Returns:
      AgentResponse with execution results
  """
  try:
    logger.info(f"Executing {request.workflow_type} workflow")

    # Create agents based on workflow type
    if request.workflow_type == "sequential":
      agents = [
        TaskAgent(name="Step1", task_description="Step 1"),
        TaskAgent(name="Step2", task_description="Step 2"),
        AnalysisAgent(name="Step3"),
        ValidationAgent(name="Step4"),
      ]
      workflow = SequentialWorkflowAgent(name="SequentialWorkflow", sub_agents=agents)

    elif request.workflow_type == "parallel":
      agents = [
        TaskAgent(name="Task1", task_description="Parallel Task 1"),
        TaskAgent(name="Task2", task_description="Parallel Task 2"),
        TaskAgent(name="Task3", task_description="Parallel Task 3"),
      ]
      workflow = ParallelWorkflowAgent(
        name="ParallelWorkflow",
        sub_agents=agents,
        max_concurrent=request.max_concurrent,
      )

    elif request.workflow_type == "loop":
      agents = [TaskAgent(name="LoopTask", task_description="Iterative Task")]
      workflow = LoopWorkflowAgent(
        name="LoopWorkflow", sub_agents=agents, max_iterations=request.max_iterations
      )

    elif request.workflow_type == "conditional":
      high = TaskAgent(name="HighPriority")
      low = TaskAgent(name="LowPriority")
      default = TaskAgent(name="Default")

      workflow = ConditionalWorkflowAgent(
        name="ConditionalWorkflow",
        conditions=[
          (lambda ctx: ctx.get("priority", 0) >= 5, [high]),
          (lambda ctx: ctx.get("priority", 0) >= 2, [low]),
        ],
        default_agents=[default],
      )

    else:
      raise HTTPException(
        status_code=400, detail=f"Unknown workflow type: {request.workflow_type}"
      )

    # Create context
    context = InvocationContext({"user_input": request.user_input, **request.context})

    # Execute workflow
    events = []
    async for event in workflow._run_async_impl(context):
      event_data = {"agent_name": event.agent_name, "data": event.data}
      events.append(event_data)

    return AgentResponse(
      success=True,
      message=f"Successfully executed {request.workflow_type} workflow with {len(events)} events",
      events=events,
    )

  except HTTPException:
    raise
  except Exception as e:
    logger.error(f"Error executing workflow: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/hierarchy", response_model=AgentHierarchyResponse)
async def get_agent_hierarchy():
  """
  Get the current agent hierarchy.

  Returns:
      AgentHierarchyResponse with the hierarchy structure
  """
  try:
    hierarchy = default_coordinator.get_hierarchy()
    return AgentHierarchyResponse(**hierarchy)

  except Exception as e:
    logger.error(f"Error getting hierarchy: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/custom", response_model=AgentResponse)
async def execute_custom_agent(agent_type: str, request: AgentRequest):
  """
  Execute a specific custom agent type.

  Args:
      agent_type: Type of agent (research, analysis, task, validation)
      request: Agent execution request

  Returns:
      AgentResponse with execution results
  """
  try:
    # Create the requested agent type
    if agent_type == "research":
      agent = ResearchAgent(name="CustomResearcher")
    elif agent_type == "analysis":
      agent = AnalysisAgent(name="CustomAnalyzer")
    elif agent_type == "task":
      agent = TaskAgent(name="CustomTaskExecutor")
    elif agent_type == "validation":
      agent = ValidationAgent(name="CustomValidator")
    else:
      raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")

    # Create context
    context = InvocationContext(
      {
        "user_input": request.user_input,
        "task_type": request.task_type,
        **request.context,
      }
    )

    # Execute agent
    events = []
    async for event in agent._run_async_impl(context):
      event_data = {"agent_name": event.agent_name, "data": event.data}
      events.append(event_data)

    return AgentResponse(
      success=True,
      message=f"Successfully executed {agent_type} agent with {len(events)} events",
      events=events,
    )

  except HTTPException:
    raise
  except Exception as e:
    logger.error(f"Error executing custom agent: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
  import uvicorn

  uvicorn.run(app, host="0.0.0.0", port=8000)
