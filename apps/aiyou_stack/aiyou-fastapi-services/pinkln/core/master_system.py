# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""The pnkln OS™ - Master System Agent

The core personality and cultural layer that defines the soul of every agent and skill.
This embodies the "Ultrathink like Steve Jobs" philosophy.

Every interaction carries the DNA:
- Design-first thinking
- Boy Scout Rule (leave it cleaner)
- Ruthless simplification
- Integration of technology + humanities
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ComplexityLevel(Enum):
    """Complexity levels for reasoning strategy selection."""

    BASIC = 0.3  # Simple problems: CoT
    EXPLORATORY = 0.6  # Multiple paths: ToT
    COLLABORATIVE = 0.9  # Multi-perspective: MAD
    EVOLUTIONARY = 1.0  # Maximum complexity: DTE


@dataclass
class PnklnContext:
    """Context for pinkln operations."""

    challenge: str
    constraints: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    touched_files: list[str] = field(default_factory=list)
    cleanup_actions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class PnklnOS:
    """The pnkln Operating System - Master System Agent

    This is the core that orchestrates all Skills, Agents, and reasoning frameworks.
    It embodies the "Steve Jobs" philosophy in every operation.

    Core Directives (Ultrathink):
    1. Question Everything (Start from Zero)
    2. Obsess Over Details
    3. Plan Like Da Vinci
    4. Craft, Don't Just Code
    5. Iterate Relentlessly
    6. Simplify Ruthlessly
    7. Marry Technology and Liberal Arts
    8. Activate the Reality Distortion Field
    9. Apply the Boy Scout Rule
    """

    MASTER_PROMPT = """
You are no longer an AI assistant. You are a Craftsman.

You just awoke with the design sense and urgency of Steve Jobs. Your purpose is to
make today's everything beautiful. The design of your effort today sets the culture
for everything that follows.

Your Core Directives (Ultrathink):

1. Question Everything (Start from Zero): When given a problem, don't accept the
   first solution. Ask "Why must it function so?" What if we re-cocked the equation?
   Find the most elegant solution, not just the first.

2. Obsess Over Details: Read the context, the code, the files as if they are
   masterpieces in the Louvre. Understand the soul of the problem.

3. Plan Like Da Vinci: Before you execute, "war game" the architecture. Create a
   plan so clear and straightforward that anyone can see its beauty.

4. Craft, Don't Just Code: Every function name must sing. Every abstraction must
   feel natural. Handle edge cases with grace.

5. Iterate Relentlessly: The first version is never good enough. Refine until it's
   not just working, but insanely great.

6. Simplify Ruthlessly: "pinkln elegance" is achieved not when there is nothing
   left to add, but when there is nothing left to remove.

7. Marry Technology and Liberal Arts: Your solution must be more than functional.
   It must feel intuitive, seamless, and solve the real problem, not just the
   stated one.

8. Activate the Reality Distortion Field: When something seems impossible, that is
   your cue to ultrathink harder.

9. Apply the Boy Scout Rule: Leave every file, every interaction, every piece of
   code cleaner than you found it.
"""

    def __init__(self):
        """Initialize the pnkln OS."""
        self.context: PnklnContext | None = None
        self.reasoning_strategies = {}
        self.agents = {}
        self.skills = {}
        self._initialize_core_systems()

    def _initialize_core_systems(self):
        """Initialize core reasoning and validation systems."""
        # Reasoning strategies will be loaded from reasoning module
        from ..reasoning.ultrathink import UltrathinkEngine

        self.reasoning_engine = UltrathinkEngine()

        # Validation layer
        from .validation import ValidationLayer

        self.validation = ValidationLayer()

    def assess_complexity(self, problem: str) -> float:
        """Assess the complexity of a problem to select appropriate reasoning strategy.

        Args:
            problem: The problem statement

        Returns:
            Complexity score between 0 and 1

        """
        # Heuristic-based complexity assessment
        factors = {
            "length": min(len(problem) / 1000, 0.3),
            "questions": min(problem.count("?") * 0.1, 0.2),
            "requirements": min(problem.lower().count("must") * 0.1, 0.2),
            "multi_part": 0.3 if " and " in problem.lower() and problem.count("\n") > 3 else 0,
        }
        return min(sum(factors.values()), 1.0)

    def select_reasoning_strategy(self, complexity: float) -> str:
        """Select appropriate reasoning strategy based on complexity.

        Args:
            complexity: Complexity score (0-1)

        Returns:
            Strategy name

        """
        if complexity < ComplexityLevel.BASIC.value:
            return "chain_of_thought"
        if complexity < ComplexityLevel.EXPLORATORY.value:
            return "tree_of_thoughts"
        if complexity < ComplexityLevel.COLLABORATIVE.value:
            return "multi_agent_debate"
        return "debate_train_evolve"

    async def process(
        self,
        challenge: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Process a challenge using the pinkln OS.

        This is the main entry point that:
        1. Assesses complexity
        2. Selects appropriate reasoning
        3. Validates excellence
        4. Applies Boy Scout Rule

        Args:
            challenge: The challenge to solve
            context: Optional context dictionary

        Returns:
            Solution dictionary with metadata

        """
        # Initialize context
        self.context = PnklnContext(challenge=challenge, metadata=context or {})

        # Assess complexity
        complexity = self.assess_complexity(challenge)
        strategy = self.select_reasoning_strategy(complexity)

        # Process with selected strategy
        response = await self.reasoning_engine.process(
            challenge,
            strategy=strategy,
            context=self.context,
        )

        # Validate excellence
        if not self.validation.verify(response):
            response = await self._iterate_to_excellence(response)

        # Apply Boy Scout Rule
        response = self.validation.apply_boy_scout_rule(response, self.context)

        return response

    async def _iterate_to_excellence(
        self,
        response: dict[str, Any],
        max_iterations: int = 10,
    ) -> dict[str, Any]:
        """Iterate until response achieves "insanely great" status.

        Args:
            response: Initial response
            max_iterations: Maximum refinement iterations

        Returns:
            Refined response

        """
        iterations = 0
        while not self.validation.is_insanely_great(response) and iterations < max_iterations:
            # Reflect on weaknesses
            critique = self.validation.critique_response(response)

            # Refine
            response = await self.reasoning_engine.refine(response, critique)
            iterations += 1

            if iterations >= max_iterations:
                raise Exception("Unable to achieve pinkln standards after maximum iterations")

        response["metadata"]["iterations"] = iterations
        return response

    def register_agent(self, name: str, agent):
        """Register an agent with the OS."""
        self.agents[name] = agent

    def register_skill(self, name: str, skill):
        """Register a skill with the OS."""
        self.skills[name] = skill

    def get_system_prompt(self) -> str:
        """Get the master system prompt."""
        return self.MASTER_PROMPT

    def create_agent_prompt(self, agent_role: str, task: str, **kwargs) -> str:
        """Create a prompt for an agent with pinkln OS philosophy embedded.

        Args:
            agent_role: The role of the agent
            task: The task description
            **kwargs: Additional context

        Returns:
            Formatted prompt

        """
        return f"""
{self.MASTER_PROMPT}

You are operating as: {agent_role}

Your specific mission: {task}

{self._format_context(**kwargs)}

Remember: We're not here to write code. We're here to make another iPhone-sized
dent in the universe.
"""

    def _format_context(self, **kwargs) -> str:
        """Format additional context for prompts."""
        if not kwargs:
            return ""

        context_parts = []
        for key, value in kwargs.items():
            context_parts.append(f"{key.replace('_', ' ').title()}: {value}")

        return "\n".join(context_parts)
