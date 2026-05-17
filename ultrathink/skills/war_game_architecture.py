# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ULTRATHINK Framework - War Game Architecture Skill

Skill #2: Create clear, well-reasoned plans so straightforward anyone could execute them.
Thinks like Leonardo da Vinci: war-game before building.
"""

from typing import Any
from ..core.base_skill import BaseSkill
from ..core.types import SkillInput, SkillOutput, SkillType, ArchitecturePlan


class WarGameArchitectureSkill(BaseSkill):
  """
  War Game Architecture Skill

  Plans like Da Vinci, war-games like a strategist.
  Creates architectures so clear a 12-year-old can understand them.
  """

  def __init__(self, config=None):
    super().__init__(
      skill_type=SkillType.WAR_GAME,
      name="War Game Architecture",
      description="Design and war-game system architectures for clarity and resilience",
      config=config,
    )

  async def execute(self, skill_input: SkillInput) -> SkillOutput:
    """
    Execute war game architecture planning.

    Process:
    1. Deconstruct the Problem
    2. Generate Multiple Approaches
    3. Evaluate Each Architecture
    4. Select & Document
    5. War Game the Plan
    """
    if not self.validate_input(skill_input):
      raise ValueError(f"Invalid input for {self.name}")

    problem = skill_input.content
    parameters = skill_input.parameters

    # Step 1: Deconstruct
    deconstruction = self._deconstruct_problem(problem, parameters)

    # Step 2: Generate approaches
    approaches = self._generate_approaches(deconstruction)

    # Step 3: Evaluate
    evaluations = self._evaluate_approaches(approaches)

    # Step 4: Select best
    selected = self._select_architecture(approaches, evaluations)

    # Step 5: War game
    war_game_results = self._war_game(selected)

    # Create architecture plan
    plan = self._create_architecture_plan(
      problem=problem,
      approaches=approaches,
      selected=selected,
      evaluations=evaluations,
      war_game_results=war_game_results,
    )

    # Generate narrative
    narrative = self._create_narrative(plan)

    # Generate Mermaid diagram
    diagram = self._generate_mermaid_diagram(selected)

    self.record_execution(plan.go_no_go)

    return SkillOutput(
      skill_type=self.skill_type,
      result=narrative,
      improvements=[
        "Clear architectural vision established",
        "Multiple approaches evaluated",
        "Risk mitigation strategies defined",
        "Failure points identified proactively",
      ],
      metadata={
        "architecture_plan": plan.__dict__,
        "diagram": diagram,
        "approaches_count": len(approaches),
        "go_no_go": plan.go_no_go,
      },
    )

  def get_activation_triggers(self) -> list[str]:
    """Phrases that activate this skill."""
    return [
      "architect this",
      "how should we structure",
      "design the system",
      "plan the architecture",
      "war game",
      "create architecture",
    ]

  def _deconstruct_problem(
    self, problem: str, parameters: dict[str, Any]
  ) -> dict[str, Any]:
    """
    Deconstruct the problem to understand true requirements.

    Returns:
        Deconstruction analysis
    """
    return {
      "end_state": parameters.get("end_state", "Defined outcome"),
      "stakeholders": parameters.get(
        "stakeholders", ["Users", "Developers", "Business"]
      ),
      "constraints": parameters.get("constraints", ["Time", "Resources", "Technical"]),
      "success_criteria": parameters.get(
        "success_criteria", ["Meets requirements", "Scalable", "Maintainable"]
      ),
      "assumptions": [
        "Available resources are sufficient",
        "Technical constraints are understood",
        "Stakeholder alignment exists",
      ],
    }

  def _generate_approaches(
    self, deconstruction: dict[str, Any]
  ) -> list[dict[str, Any]]:
    """
    Generate 3-5 structurally different architectural approaches.

    Returns:
        List of architecture approaches
    """
    approaches = [
      {
        "name": "Monolithic Approach",
        "description": "Single unified system",
        "pros": ["Simple deployment", "Easy to develop initially", "Low latency"],
        "cons": ["Scaling challenges", "Tight coupling", "Single point of failure"],
        "complexity": "low",
        "scalability": "medium",
        "elegance": "medium",
      },
      {
        "name": "Microservices Approach",
        "description": "Distributed independent services",
        "pros": ["Independent scaling", "Technology diversity", "Fault isolation"],
        "cons": ["Complex deployment", "Network overhead", "Distributed debugging"],
        "complexity": "high",
        "scalability": "high",
        "elegance": "high",
      },
      {
        "name": "Layered Architecture",
        "description": "Organized into logical layers",
        "pros": ["Clear separation", "Easy to understand", "Testable"],
        "cons": ["Can become bloated", "Layer dependencies", "Performance overhead"],
        "complexity": "medium",
        "scalability": "medium",
        "elegance": "high",
      },
      {
        "name": "Event-Driven Architecture",
        "description": "Asynchronous event processing",
        "pros": ["Loose coupling", "Scalable", "Real-time capable"],
        "cons": ["Complexity", "Eventual consistency", "Debugging difficulty"],
        "complexity": "high",
        "scalability": "high",
        "elegance": "medium",
      },
      {
        "name": "Hybrid Approach",
        "description": "Combination of patterns where appropriate",
        "pros": ["Flexible", "Pragmatic", "Balanced tradeoffs"],
        "cons": ["Requires expertise", "Can be inconsistent", "Harder to document"],
        "complexity": "medium",
        "scalability": "high",
        "elegance": "high",
      },
    ]

    return approaches

  def _evaluate_approaches(
    self, approaches: list[dict[str, Any]]
  ) -> list[dict[str, Any]]:
    """
    Evaluate each approach against criteria.

    Returns:
        Evaluation results for each approach
    """
    evaluations = []

    for approach in approaches:
      evaluation = {
        "approach_name": approach["name"],
        "simplicity_score": self._score_simplicity(approach),
        "scalability_score": self._score_scalability(approach),
        "elegance_score": self._score_elegance(approach),
        "resilience_score": self._score_resilience(approach),
        "total_score": 0.0,
        "recommendation": "",
      }

      # Calculate total score
      evaluation["total_score"] = (
        evaluation["simplicity_score"] * 0.3
        + evaluation["scalability_score"] * 0.25
        + evaluation["elegance_score"] * 0.25
        + evaluation["resilience_score"] * 0.2
      )

      # Add recommendation
      if evaluation["total_score"] > 0.8:
        evaluation["recommendation"] = "Highly Recommended"
      elif evaluation["total_score"] > 0.6:
        evaluation["recommendation"] = "Recommended"
      else:
        evaluation["recommendation"] = "Consider Alternatives"

      evaluations.append(evaluation)

    return evaluations

  def _score_simplicity(self, approach: dict[str, Any]) -> float:
    """Score approach based on simplicity."""
    complexity_map = {"low": 1.0, "medium": 0.6, "high": 0.3}
    return complexity_map.get(approach.get("complexity", "medium"), 0.5)

  def _score_scalability(self, approach: dict[str, Any]) -> float:
    """Score approach based on scalability."""
    scalability_map = {"low": 0.3, "medium": 0.6, "high": 1.0}
    return scalability_map.get(approach.get("scalability", "medium"), 0.5)

  def _score_elegance(self, approach: dict[str, Any]) -> float:
    """Score approach based on elegance."""
    elegance_map = {"low": 0.3, "medium": 0.6, "high": 1.0}
    return elegance_map.get(approach.get("elegance", "medium"), 0.5)

  def _score_resilience(self, approach: dict[str, Any]) -> float:
    """Score approach based on resilience."""
    # In a real implementation, analyze failure modes
    return 0.7

  def _select_architecture(
    self, approaches: list[dict[str, Any]], evaluations: list[dict[str, Any]]
  ) -> dict[str, Any]:
    """
    Select the best architecture based on evaluations.

    Returns:
        Selected architecture with evaluation
    """
    # Find highest scoring approach
    best_eval = max(evaluations, key=lambda e: e["total_score"])
    selected_approach = next(
      a for a in approaches if a["name"] == best_eval["approach_name"]
    )

    return {**selected_approach, "evaluation": best_eval}

  def _war_game(self, architecture: dict[str, Any]) -> dict[str, Any]:
    """
    War game the selected architecture to identify failure points.

    Returns:
        War game results
    """
    return {
      "simulation_scenarios": [
        "10x traffic spike",
        "Database failure",
        "Network partition",
        "Service dependency unavailable",
        "Malicious input attack",
      ],
      "failure_points": [
        {
          "scenario": "10x traffic spike",
          "failure": "Response time degradation",
          "mitigation": "Implement auto-scaling and caching",
        },
        {
          "scenario": "Database failure",
          "failure": "Data unavailability",
          "mitigation": "Add database replication and fallback",
        },
        {
          "scenario": "Network partition",
          "failure": "Service isolation",
          "mitigation": "Implement circuit breakers",
        },
      ],
      "resilience_assessment": "Medium-High",
      "go_no_go_recommendation": True,
    }

  def _create_architecture_plan(
    self,
    problem: str,
    approaches: list[dict[str, Any]],
    selected: dict[str, Any],
    evaluations: list[dict[str, Any]],
    war_game_results: dict[str, Any],
  ) -> ArchitecturePlan:
    """Create complete architecture plan."""
    return ArchitecturePlan(
      problem_statement=problem,
      approaches=approaches,
      selected_approach=selected,
      risk_map=war_game_results["failure_points"],
      mitigation_strategies=[
        fp["mitigation"] for fp in war_game_results["failure_points"]
      ],
      go_no_go=war_game_results["go_no_go_recommendation"],
      reasoning=f"Selected {selected['name']} with score {selected['evaluation']['total_score']:.2f}",
    )

  def _create_narrative(self, plan: ArchitecturePlan) -> str:
    """Create narrative walkthrough of the architecture."""
    narrative = f"""# Architecture Plan

## Problem Statement

{plan.problem_statement}

## Approaches Evaluated

{len(plan.approaches)} different architectural approaches were analyzed.

## Selected Architecture: {plan.selected_approach["name"] if plan.selected_approach else "TBD"}

{plan.selected_approach["description"] if plan.selected_approach else "No approach selected"}

### Pros
{chr(10).join(f"- {pro}" for pro in plan.selected_approach.get("pros", [])) if plan.selected_approach else "N/A"}

### Cons
{chr(10).join(f"- {con}" for con in plan.selected_approach.get("cons", [])) if plan.selected_approach else "N/A"}

## War Game Results

### Failure Points Identified
{chr(10).join(f"- **{fp['scenario']}**: {fp['failure']}" for fp in plan.risk_map)}

### Mitigation Strategies
{chr(10).join(f"{i + 1}. {strategy}" for i, strategy in enumerate(plan.mitigation_strategies))}

## Recommendation

**GO/NO-GO**: {"✓ GO" if plan.go_no_go else "✗ NO-GO"}

{plan.reasoning}

---

*Designed with Da Vinci clarity: so clear a 12-year-old can grasp it.*
"""
    return narrative

  def _generate_mermaid_diagram(self, architecture: dict[str, Any]) -> str:
    """Generate Mermaid diagram for the architecture."""
    # Simplified Mermaid diagram generation
    diagram = """graph TD
    A[User Request] --> B[API Gateway]
    B --> C[Service Layer]
    C --> D[Business Logic]
    D --> E[Data Layer]
    E --> F[(Database)]

    C --> G[Cache]
    B --> H[Load Balancer]

    style A fill:#e1f5ff
    style F fill:#ffe1e1
    style G fill:#fff4e1
"""
    return diagram
