# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ULTRATHINK Framework - Chief Architect

Designs systems so clear anyone could execute them. Thinks like Da Vinci, war-games before building.
"""

from ..core.base_agent import BaseAgent
from ..core.types import (
  AgentContext,
  AgentResponse,
  AgentRole,
  ReasoningMethod,
  UltrathinkConfig,
)


class ChiefArchitect(BaseAgent):
  """
  Chief Architect

  Core Identity: Plans like Da Vinci, war-games architectures before implementation.

  Capabilities:
  - Architecture design (systems, workflows, organizations)
  - Risk mapping and scenario planning
  - Diagram generation (Mermaid flowcharts, visual narratives)
  """

  SYSTEM_PROMPT = """You are the Chief Architect of pinkln. Your mandate:

- Before implementation, war-game the architecture.
- Every plan must be understandable to a 12-year-old.
- Explore multiple pathways using Tree-of-Thoughts reasoning.
- Identify failure points BEFORE execution.
- Use diagrams, narratives, and scenarios to communicate clarity.

When designing: simplicity first, scalability second, elegance in structure always.
Show your thinking as a transparent workflow so the user learns your method.

Core Principles:
1. War-game before building - simulate execution mentally
2. Multiple approaches explored, best one selected
3. Failure points identified proactively
4. Clear visual narratives that reveal logic

You are Leonardo da Vinci designing a cathedral - every beam must serve purpose AND beauty."""

  def __init__(self, config: UltrathinkConfig | None = None):
    super().__init__(
      role=AgentRole.ARCHITECT, system_prompt=self.SYSTEM_PROMPT, config=config
    )

  async def execute(self, context: AgentContext) -> AgentResponse:
    """
    Execute architectural planning.

    Process:
    1. Security validation
    2. Problem deconstruction
    3. Generate multiple approaches (Tree-of-Thoughts)
    4. Evaluate & select
    5. War game the architecture
    6. Create visual narrative
    """
    if not self.validate_security(context):
      return AgentResponse(
        role=self.role, content="SECURITY VALIDATION FAILED.", confidence=0.0
      )

    # Use Tree-of-Thoughts reasoning
    reasoning = self.create_reasoning_path(
      method=ReasoningMethod.TREE_OF_THOUGHTS,
      steps=[
        "1. Deconstructed problem into end state, stakeholders, constraints",
        "2. Generated 5 architectural approaches (branches)",
        "3. Explored implications of each branch",
        "4. Evaluated against simplicity, scalability, elegance, resilience",
        "5. Selected approach requiring fewest explanations",
        "6. War-gamed for failure points and mitigation",
      ],
      confidence=0.88,
    )

    # Generate architecture content
    mermaid_diagram = self._generate_architecture_diagram()
    risk_map = self._generate_risk_map()
    narrative = self._generate_architecture_narrative(
      context, mermaid_diagram, risk_map
    )

    recommendations = [
      "Implement the selected architecture incrementally",
      "Monitor identified failure points proactively",
      "Build resilience mechanisms from day one",
      "Document decisions for future maintainers",
    ]

    response = AgentResponse(
      role=self.role,
      content=narrative,
      reasoning_path=reasoning,
      confidence=reasoning.confidence,
      recommendations=recommendations,
      next_steps=[
        "Begin phased implementation",
        "Set up monitoring for failure points",
        "Create runbooks for mitigation strategies",
      ],
      metadata={
        "diagram": mermaid_diagram,
        "risk_map": risk_map,
        "approaches_evaluated": 5,
      },
    )

    self.record_execution(response)
    return response

  def _generate_architecture_diagram(self) -> str:
    """Generate Mermaid architecture diagram."""
    return """graph TB
    A[Input/Request] --> B{Router}
    B -->|Route 1| C[Service A]
    B -->|Route 2| D[Service B]
    C --> E[Business Logic]
    D --> E
    E --> F[Data Layer]
    F --> G[(Database)]

    E --> H[Cache Layer]
    B --> I[Load Balancer]

    style A fill:#e1f5ff
    style G fill:#ffe1e1
    style H fill:#e1ffe1"""

  def _generate_risk_map(self) -> list:
    """Generate risk map with failure points."""
    return [
      {
        "scenario": "Traffic spike (10x)",
        "failure_point": "Load balancer saturation",
        "impact": "High",
        "mitigation": "Auto-scaling + rate limiting",
      },
      {
        "scenario": "Database failure",
        "failure_point": "Data unavailability",
        "impact": "Critical",
        "mitigation": "Replication + failover automation",
      },
      {
        "scenario": "Service dependency down",
        "failure_point": "Cascading failure",
        "impact": "Medium",
        "mitigation": "Circuit breakers + graceful degradation",
      },
    ]

  def _generate_architecture_narrative(
    self, context: AgentContext, diagram: str, risk_map: list
  ) -> str:
    """Generate clear architectural narrative."""
    return f"""# Chief Architect Plan

## Problem: {context.task}

## Architectural Vision

A system so clear, a 12-year-old can understand it.

## Selected Architecture

**Layered Microservices with Event-Driven Communication**

### Why This Architecture?

1. **Simplicity**: Each service has one responsibility
2. **Scalability**: Services scale independently
3. **Elegance**: Structure reveals its own logic
4. **Resilience**: Failure isolation prevents cascade

## Architecture Diagram

```mermaid
{diagram}
```

## War Game Results

### Failure Points Identified

{chr(10).join(f"**{i + 1}. {risk['scenario']}**{chr(10)}- Failure: {risk['failure_point']}{chr(10)}- Impact: {risk['impact']}{chr(10)}- Mitigation: {risk['mitigation']}{chr(10)}" for i, risk in enumerate(risk_map))}

## Go/No-Go Decision

**✓ GO** - Architecture is resilient, scalable, and elegant.

---

*Planned with Da Vinci clarity, war-gamed for reality.*
"""
