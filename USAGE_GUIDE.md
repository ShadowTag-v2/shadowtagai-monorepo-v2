# Multi-Agent System Usage Guide

This guide provides detailed instructions and advanced patterns for using the multi-agent system.

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [Agent Creation](#agent-creation)
3. [Workflow Patterns](#workflow-patterns)
4. [API Usage](#api-usage)
5. [Advanced Patterns](#advanced-patterns)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Core Concepts

### Multi-Agent Hierarchy

The foundation of Google ADK's multi-agent system is the parent-child relationship defined in `BaseAgent`. Agents can have sub-agents, creating a tree structure:

```python
# Single level
parent = MultiAgent(
    name="Parent",
    sub_agents=[child1, child2]
)

# Multi-level hierarchy
grandchild = MultiAgent(name="GrandChild")
child = MultiAgent(name="Child", sub_agents=[grandchild])
parent = MultiAgent(name="Parent", sub_agents=[child])
```

### Invocation Context

The `InvocationContext` carries information through the agent hierarchy:

```python
from google.adk.agents.invocation_context import InvocationContext

context = InvocationContext({
    "user_input": "Task description",
    "task_type": "research",
    "priority": 8,
    "custom_data": {"key": "value"}
})
```

### Event Streaming

Agents communicate through event streaming using `AsyncGenerator`:

```python
async for event in agent._run_async_impl(context):
    print(f"Agent: {event.agent_name}")
    print(f"Data: {event.data}")
```

## Agent Creation

### Creating Custom Agents

Extend `MultiAgent` for custom behavior:

```python
from src.agents.base_agent import MultiAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import AgentEvent
from typing import AsyncGenerator

class MyCustomAgent(MultiAgent):
    def __init__(self, name: str, **kwargs):
        super().__init__(
            name=name,
            model="gemini-2.5-flash",
            description="My custom agent",
            **kwargs
        )

    async def _run_async_impl(
        self,
        context: InvocationContext
    ) -> AsyncGenerator[AgentEvent, None]:
        # Your custom logic here
        user_input = context.get("user_input", "")

        # Yield events
        yield AgentEvent(
            agent_name=self.name,
            data={"status": "processing", "input": user_input}
        )

        # Do work...
        result = self.process(user_input)

        yield AgentEvent(
            agent_name=self.name,
            data={"status": "completed", "result": result}
        )

    def process(self, input_data):
        # Your processing logic
        return f"Processed: {input_data}"
```

### Using Pre-built Agents

```python
from src.agents import (
    CoordinatorAgent,
    ResearchAgent,
    AnalysisAgent,
    TaskAgent,
    ValidationAgent
)

# Research agent
researcher = ResearchAgent(name="MyResearcher")

# Analysis agent
analyzer = AnalysisAgent(name="MyAnalyzer")

# Task execution agent
executor = TaskAgent(
    name="MyExecutor",
    task_description="Execute specific tasks"
)

# Validation agent with criteria
validator = ValidationAgent(
    name="MyValidator",
    validation_criteria={
        "accuracy": 0.95,
        "completeness": True
    }
)

# Coordinator with sub-agents
coordinator = CoordinatorAgent(
    name="MainCoordinator",
    sub_agents=[researcher, analyzer, executor, validator]
)
```

## Workflow Patterns

### 1. Sequential Workflow

Best for: Data pipelines, step-by-step processing

```python
from src.workflows import SequentialWorkflowAgent
from src.agents import TaskAgent, AnalysisAgent, ValidationAgent

# Create pipeline steps
fetch = TaskAgent(name="DataFetcher", task_description="Fetch data")
clean = TaskAgent(name="DataCleaner", task_description="Clean data")
analyze = AnalysisAgent(name="DataAnalyzer")
validate = ValidationAgent(name="ResultValidator")

# Create sequential workflow
pipeline = SequentialWorkflowAgent(
    name="DataPipeline",
    sub_agents=[fetch, clean, analyze, validate],
    description="End-to-end data processing pipeline"
)

# Execute
context = InvocationContext({"user_input": "Process customer data"})
results = []
async for event in pipeline._run_async_impl(context):
    results.append(event.data)
    print(f"Step {event.data.get('step', '?')}: {event.agent_name}")

# Access results from pipeline
final_results = pipeline.results
```

### 2. Parallel Workflow

Best for: Independent tasks, data gathering, concurrent processing

```python
from src.workflows import ParallelWorkflowAgent
from src.agents import TaskAgent

# Create independent tasks
task1 = TaskAgent(name="FetchAPI1", task_description="Fetch from API 1")
task2 = TaskAgent(name="FetchAPI2", task_description="Fetch from API 2")
task3 = TaskAgent(name="FetchAPI3", task_description="Fetch from API 3")
task4 = TaskAgent(name="FetchAPI4", task_description="Fetch from API 4")

# Parallel with concurrency limit
parallel = ParallelWorkflowAgent(
    name="APIGatherer",
    sub_agents=[task1, task2, task3, task4],
    max_concurrent=2  # Only 2 at a time
)

# Execute
context = InvocationContext({"user_input": "Gather all data"})
async for event in parallel._run_async_impl(context):
    print(f"Task: {event.agent_name} - {event.data.get('status')}")

# Check results
print(f"Total results: {len(parallel.results)}")
```

### 3. Loop Workflow

Best for: Iterative refinement, retry logic, batch processing

```python
from src.workflows import LoopWorkflowAgent
from src.agents import TaskAgent

# Create iterative task
refiner = TaskAgent(name="DataRefiner", task_description="Refine data")

# Loop with condition
def is_quality_met(context):
    # Check if quality threshold is met
    quality = context.get("quality_score", 0)
    return quality >= 0.95

loop = LoopWorkflowAgent(
    name="RefinementLoop",
    sub_agents=[refiner],
    max_iterations=10,
    condition=is_quality_met
)

# Execute
context = InvocationContext({
    "user_input": "Refine until quality >= 0.95",
    "quality_score": 0.5
})

async for event in loop._run_async_impl(context):
    iteration = event.data.get('iteration', 0)
    status = event.data.get('status')
    print(f"Iteration {iteration}: {status}")

    # Update quality score based on progress (example)
    if status == "iteration_completed":
        context["quality_score"] = min(0.95, context["quality_score"] + 0.1)
```

### 4. Conditional Workflow

Best for: Routing logic, priority handling, dynamic execution paths

```python
from src.workflows import ConditionalWorkflowAgent
from src.agents import TaskAgent

# Create route handlers
urgent = TaskAgent(name="UrgentHandler", task_description="Handle urgent")
normal = TaskAgent(name="NormalHandler", task_description="Handle normal")
low = TaskAgent(name="LowHandler", task_description="Handle low priority")
default = TaskAgent(name="DefaultHandler", task_description="Default handler")

# Define conditions
router = ConditionalWorkflowAgent(
    name="PriorityRouter",
    conditions=[
        # (condition_function, [agents_to_execute])
        (lambda ctx: ctx.get("priority") == "urgent", [urgent]),
        (lambda ctx: ctx.get("priority") == "normal", [normal]),
        (lambda ctx: ctx.get("priority") == "low", [low])
    ],
    default_agents=[default]
)

# Test different priorities
for priority in ["urgent", "normal", "low", "unknown"]:
    print(f"\n--- Priority: {priority} ---")
    context = InvocationContext({
        "user_input": f"Task with {priority} priority",
        "priority": priority
    })

    async for event in router._run_async_impl(context):
        print(f"{event.agent_name}: {event.data.get('status')}")
```

## API Usage

### Starting the Server

```bash
# Development mode
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
python -m src.api.main
```

### Using the REST API

#### 1. Execute Multi-Agent System

```bash
curl -X POST "http://localhost:8000/api/agents/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Analyze market trends for Q1 2025",
    "task_type": "analysis",
    "context": {
      "priority": 8,
      "department": "research"
    }
  }'
```

#### 2. Execute Specific Workflow

```bash
# Sequential workflow
curl -X POST "http://localhost:8000/api/workflows/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_type": "sequential",
    "user_input": "Process customer data pipeline"
  }'

# Parallel workflow
curl -X POST "http://localhost:8000/api/workflows/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_type": "parallel",
    "user_input": "Gather data from multiple sources",
    "max_concurrent": 3
  }'

# Loop workflow
curl -X POST "http://localhost:8000/api/workflows/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_type": "loop",
    "user_input": "Refine results iteratively",
    "max_iterations": 5
  }'

# Conditional workflow
curl -X POST "http://localhost:8000/api/workflows/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_type": "conditional",
    "user_input": "Route based on priority",
    "context": {"priority": 7}
  }'
```

#### 3. Get Agent Hierarchy

```bash
curl -X GET "http://localhost:8000/api/agents/hierarchy"
```

#### 4. Execute Custom Agent

```bash
# Research agent
curl -X POST "http://localhost:8000/api/agents/custom?agent_type=research" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Research AI trends in 2025"
  }'

# Analysis agent
curl -X POST "http://localhost:8000/api/agents/custom?agent_type=analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Analyze sales data"
  }'
```

### Using Python Client

```python
import httpx
import asyncio

async def call_api():
    async with httpx.AsyncClient() as client:
        # Execute agent
        response = await client.post(
            "http://localhost:8000/api/agents/execute",
            json={
                "user_input": "Analyze market trends",
                "task_type": "analysis"
            }
        )
        result = response.json()
        print(f"Success: {result['success']}")
        print(f"Events: {len(result['events'])}")

        # Get hierarchy
        hierarchy = await client.get(
            "http://localhost:8000/api/agents/hierarchy"
        )
        print(f"Hierarchy: {hierarchy.json()}")

asyncio.run(call_api())
```

## Advanced Patterns

### 1. Nested Workflows

Combine different workflow types:

```python
from src.workflows import SequentialWorkflowAgent, ParallelWorkflowAgent
from src.agents import TaskAgent, AnalysisAgent

# Stage 1: Parallel data gathering
gather1 = TaskAgent(name="Gather1")
gather2 = TaskAgent(name="Gather2")
parallel_stage = ParallelWorkflowAgent(
    name="GatherStage",
    sub_agents=[gather1, gather2]
)

# Stage 2: Sequential processing
process = TaskAgent(name="Process")
analyze = AnalysisAgent(name="Analyze")

# Combine into sequential pipeline
combined = SequentialWorkflowAgent(
    name="CombinedPipeline",
    sub_agents=[parallel_stage, process, analyze]
)
```

### 2. Dynamic Agent Configuration

```python
from src.agents import CoordinatorAgent, TaskAgent

# Start with basic setup
coordinator = CoordinatorAgent(name="DynamicCoordinator")

# Add agents based on runtime conditions
if need_research:
    coordinator.add_sub_agent(ResearchAgent(name="Researcher"))

if need_analysis:
    coordinator.add_sub_agent(AnalysisAgent(name="Analyzer"))

# Execute with current configuration
context = InvocationContext({"user_input": "Execute"})
async for event in coordinator._run_async_impl(context):
    process_event(event)
```

### 3. Agent Registry Pattern

```python
from src.tools import global_registry, global_manager
from src.agents import ResearchAgent, AnalysisAgent

# Register agent types
global_registry.register("research", ResearchAgent)
global_registry.register("analysis", AnalysisAgent)

# Create instances dynamically
agent1 = global_registry.create_agent("research", "MyResearcher")
agent2 = global_registry.create_agent("analysis", "MyAnalyzer")

# Manage agents
global_manager.add_agent(agent1)
global_manager.add_agent(agent2)

# Get statistics
stats = global_manager.get_all_stats()
print(stats)
```

## Best Practices

### 1. Agent Naming

```python
# Good - descriptive, hierarchical
coordinator = CoordinatorAgent(name="MainCoordinator")
research_team = CoordinatorAgent(name="ResearchTeam")
researcher_1 = ResearchAgent(name="Researcher_Market")
researcher_2 = ResearchAgent(name="Researcher_Competitor")

# Avoid - vague, numbered without context
agent1 = MultiAgent(name="Agent1")
a = MultiAgent(name="A")
```

### 2. Context Management

```python
# Good - structured context
context = InvocationContext({
    "user_input": "Clear task description",
    "task_type": "research",
    "priority": 8,
    "metadata": {
        "department": "marketing",
        "deadline": "2025-12-31"
    }
})

# Avoid - unstructured data
context = InvocationContext({
    "data": "some random data"
})
```

### 3. Error Handling

```python
try:
    async for event in agent._run_async_impl(context):
        process_event(event)
except Exception as e:
    logger.error(f"Agent execution failed: {e}")
    # Handle error appropriately
```

### 4. Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MyAgent(MultiAgent):
    async def _run_async_impl(self, context):
        logger.info(f"Agent {self.name} starting")
        # ... execution ...
        logger.info(f"Agent {self.name} completed")
```

## Troubleshooting

### Issue: Agent not executing sub-agents

**Solution**: Ensure sub-agents are passed during initialization:

```python
# Correct
coordinator = CoordinatorAgent(
    name="Coordinator",
    sub_agents=[agent1, agent2]  # Pass during init
)

# Incorrect
coordinator = CoordinatorAgent(name="Coordinator")
coordinator.sub_agents = [agent1, agent2]  # Don't set directly
```

### Issue: Events not streaming

**Solution**: Use `async for` to consume events:

```python
# Correct
async for event in agent._run_async_impl(context):
    print(event)

# Incorrect
events = agent._run_async_impl(context)  # Returns generator, doesn't execute
```

### Issue: Context not updating between agents

**Solution**: Modify context in sub-agent execution:

```python
async def _run_async_impl(self, context):
    # Create modified context for sub-agents
    sub_context = context.copy()
    sub_context["additional_data"] = "value"

    for sub_agent in self.sub_agents:
        async for event in sub_agent._run_async_impl(sub_context):
            yield event
```

### Issue: API server not starting

**Solution**: Check port availability and dependencies:

```bash
# Check if port 8000 is in use
lsof -i :8000

# Install all dependencies
pip install -r requirements.txt

# Try different port
uvicorn src.api.main:app --port 8001
```

## Next Steps

- Review the [examples](src/examples/) for more patterns
- Consult [Google ADK documentation](https://google.github.io/adk-docs/) for advanced features
- Explore the [API documentation](http://localhost:8000/docs) when server is running
- Build custom agents for your specific use cases

---

For more information, see [README.md](README.md)
