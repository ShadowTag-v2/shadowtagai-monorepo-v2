# ADK Multi-Agent Patterns Reference

**Source:** [Google ADK Docs](https://google.github.io/adk-docs/)
**Date:** 2026-01-18

This document contains the core Multi-Agent Patterns extracted from the ADK documentation, ready for implementation in `ShadowTag-v2`.

## 1. Sequential Pipeline (The Assembly Line)

_Linear, deterministic execution._

```python
from google.adk.agents import SequentialAgent, LlmAgent

# Agent 1: Researches a topic
research_agent = LlmAgent(
    name="Researcher",
    instruction="Research the given topic and provide a detailed summary.",
    output_key="research_summary"
)

# Agent 2: Writes an article based on the research
writer_agent = LlmAgent(
    name="Writer",
    instruction="Write a blog post based on the research summary provided in the state.",
    output_key="blog_post"
)

# Sequential Workflow
pipeline = SequentialAgent(
    name="ContentPipeline",
    sub_agents=[research_agent, writer_agent]
)
```

## 2. Parallel Fan-Out/Gather (The Swarm)

_Concurrent execution for independent tasks._

```python
from google.adk.agents import ParallelAgent, LlmAgent

# These agents run in parallel
fetch_weather = LlmAgent(name="WeatherFetcher", output_key="weather")
fetch_news = LlmAgent(name="NewsFetcher", output_key="news")

# Parallel Workflow
gatherer = ParallelAgent(
    name="InfoGatherer",
    sub_agents=[fetch_weather, fetch_news]
)
```

## 3. Coordinator/Dispatcher (The Concierge)

_LLM-driven dynamic routing._

```python
from google.adk.agents import LlmAgent

booking_agent = LlmAgent(
    name="Booker",
    description="Handles flight and hotel bookings."
)
info_agent = LlmAgent(
    name="Info",
    description="Provides general information and answers questions."
)

coordinator = LlmAgent(
    name="Coordinator",
    model="gemini-3.1-flash",
    instruction="You are an assistant. Delegate booking tasks to Booker and info requests to Info.",
    description="Main coordinator.",
    sub_agents=[booking_agent, info_agent]
)
```

## 4. Loop Agent (The Sculptor / Generator-Critic)

_Iterative refinement until a condition is met._

```python
from google.adk.agents import LoopAgent, LlmAgent

# Generator / Improver
improver = LlmAgent(name="Improver", output_key="draft")
# Critic
critic = LlmAgent(name="Critic", output_key="critique")

# Loop Workflow (Refinement)
refinement_loop = LoopAgent(
    name="IterativeRefiner",
    sub_agents=[improver, critic],
    max_iterations=3
)
```

## Implementation Notes

- **State Management:** Use `output_key` to write to the shared session state.
- **Routing:** Use `description` fields in Sub-Agents to guide the Coordinator's routing logic.
- **Library:** These patterns rely on `google.adk.agents`. Ensure this package is available or implement the equivalent classes in `libs/pnkln-stack`.
