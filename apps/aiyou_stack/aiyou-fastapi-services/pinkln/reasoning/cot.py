"""Chain of Thought (CoT) reasoning framework.

CoT is a linear, step-by-step reasoning approach that makes the thought process
transparent. It's effective for math, logic, and problems requiring sequential steps.

Usage:
    cot = ChainOfThought()
    result = await cot.reason("Solve: 4 + 9 * (13 - 10)")
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ThoughtStep:
    """A single step in the chain of thought."""

    step_number: int
    description: str
    reasoning: str
    intermediate_result: Any = None
    confidence: float = 1.0


class ChainOfThought:
    """Chain of Thought reasoning implementation.

    This framework breaks down complex problems into transparent, sequential steps,
    reducing hallucinations and improving accuracy.
    """

    PROMPT_TEMPLATE = """
Let's think through this step-by-step.

Problem: {problem}

Please solve this by:
1. Breaking down the problem into clear steps
2. Working through each step methodically
3. Showing your reasoning at each stage
4. Arriving at the final answer

Think step-by-step:
"""

    def __init__(self):
        """Initialize CoT framework."""
        self.thought_chain: list[ThoughtStep] = []

    async def reason(self, problem: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Apply chain of thought reasoning to a problem.

        Args:
            problem: Problem to solve
            context: Optional context

        Returns:
            Result with thought chain

        """
        self.thought_chain = []

        # Generate the prompt
        prompt = self.PROMPT_TEMPLATE.format(problem=problem)

        # In a real implementation, this would call an LLM
        # For now, return a structured response
        return {
            "problem": problem,
            "prompt": prompt,
            "thought_chain": [step.__dict__ for step in self.thought_chain],
            "final_answer": None,
            "metadata": {"method": "chain_of_thought", "steps_taken": len(self.thought_chain)},
        }

    def add_step(
        self,
        description: str,
        reasoning: str,
        result: Any = None,
        confidence: float = 1.0,
    ):
        """Add a step to the thought chain.

        Args:
            description: Step description
            reasoning: Reasoning for this step
            result: Intermediate result
            confidence: Confidence level (0-1)

        """
        step = ThoughtStep(
            step_number=len(self.thought_chain) + 1,
            description=description,
            reasoning=reasoning,
            intermediate_result=result,
            confidence=confidence,
        )
        self.thought_chain.append(step)

    def get_chain(self) -> list[ThoughtStep]:
        """Get the complete thought chain."""
        return self.thought_chain

    def get_last_step(self) -> ThoughtStep | None:
        """Get the last step in the chain."""
        return self.thought_chain[-1] if self.thought_chain else None

    def format_chain(self) -> str:
        """Format the thought chain as a readable string."""
        if not self.thought_chain:
            return "No thoughts in chain yet."

        formatted = ["Chain of Thought:\n"]
        for step in self.thought_chain:
            formatted.append(f"Step {step.step_number}: {step.description}")
            formatted.append(f"  Reasoning: {step.reasoning}")
            if step.intermediate_result is not None:
                formatted.append(f"  Result: {step.intermediate_result}")
            formatted.append(f"  Confidence: {step.confidence:.2%}\n")

        return "\n".join(formatted)

    def clear_chain(self):
        """Clear the thought chain."""
        self.thought_chain = []


# Specialized CoT variants


class SelfAskCoT(ChainOfThought):
    """Self-Ask variant of CoT.

    This variant explicitly asks and answers sub-questions before tackling
    the main problem.
    """

    PROMPT_TEMPLATE = """
Let's break this down by asking and answering sub-questions.

Main Question: {problem}

For each sub-question:
1. Ask: What do I need to know?
2. Answer: Provide the answer
3. Follow-up: What's next?

Sub-questions and answers:
"""


class PlanAndSolveCoT(ChainOfThought):
    """Plan-and-Solve variant of CoT.

    This variant first creates a plan, then executes it step-by-step.
    """

    PROMPT_TEMPLATE = """
Let's first make a plan, then solve step-by-step.

Problem: {problem}

Phase 1 - Planning:
1. Understand the problem
2. Identify required steps
3. Create execution plan

Phase 2 - Execution:
Execute each step of the plan

Let's begin:
"""

    async def reason(self, problem: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Apply plan-and-solve reasoning.

        Args:
            problem: Problem to solve
            context: Optional context

        Returns:
            Result with plan and execution

        """
        # Phase 1: Planning
        plan = await self._create_plan(problem, context)

        # Phase 2: Execution
        result = await self._execute_plan(plan, context)

        return {
            "problem": problem,
            "plan": plan,
            "execution": result,
            "metadata": {
                "method": "plan_and_solve",
                "plan_steps": len(plan.get("steps", [])),
                "execution_steps": len(self.thought_chain),
            },
        }

    async def _create_plan(self, problem: str, context: dict[str, Any] | None) -> dict[str, Any]:
        """Create an execution plan."""
        return {"steps": [], "dependencies": [], "estimated_complexity": 0.5}

    async def _execute_plan(
        self,
        plan: dict[str, Any],
        context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Execute the plan step-by-step."""
        return {"executed_steps": [], "final_result": None}
