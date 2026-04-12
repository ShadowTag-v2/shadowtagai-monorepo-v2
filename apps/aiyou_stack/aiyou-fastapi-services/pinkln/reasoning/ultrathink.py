"""
Ultrathink Engine - Unified Reasoning Orchestrator

The Ultrathink engine automatically selects and orchestrates the appropriate
reasoning strategy based on problem complexity:

Level 1 (< 0.3): Chain of Thought (CoT) - Linear reasoning
Level 2 (< 0.6): Tree of Thoughts (ToT) - Exploratory reasoning
Level 3 (< 0.9): Multi-Agent Debate (MAD) - Collaborative reasoning
Level 4 (1.0):   Debate-Train-Evolve (DTE) - Evolutionary reasoning

This is the "deep agent skill" that can be called by any agent when faced
with complex problems.
"""

from enum import Enum
from typing import Any

from .cot import ChainOfThought, PlanAndSolveCoT
from .mad import MultiAgentDebate, PanelGPT
from .rcr import ReflectCritiqueRefine
from .tot import SearchStrategy, TreeOfThoughts


class ReasoningLevel(Enum):
    """Reasoning complexity levels."""

    BASIC = ("basic", 0.3, "Chain of Thought")
    EXPLORATORY = ("exploratory", 0.6, "Tree of Thoughts")
    COLLABORATIVE = ("collaborative", 0.9, "Multi-Agent Debate")
    EVOLUTIONARY = ("evolutionary", 1.0, "Debate-Train-Evolve")

    def __init__(self, key: str, threshold: float, description: str):
        self.key = key
        self.threshold = threshold
        self.description = description


class UltrathinkEngine:
    """
    The Ultrathink Reasoning Engine.

    This engine embodies the "Ultrathink like Steve Jobs" philosophy by:
    1. Assessing problem complexity
    2. Selecting optimal reasoning strategy
    3. Executing with elegance and depth
    4. Iterating until "insanely great"
    """

    def __init__(self):
        """Initialize Ultrathink engine."""
        self.strategies = {
            "chain_of_thought": ChainOfThought(),
            "plan_and_solve": PlanAndSolveCoT(),
            "tree_of_thoughts": TreeOfThoughts(),
            "multi_agent_debate": MultiAgentDebate(),
            "panel_gpt": PanelGPT(),
            "rcr": ReflectCritiqueRefine(),
        }
        self.execution_history: list = []

    async def process(
        self, problem: str, strategy: str | None = None, context: Any | None = None, **kwargs
    ) -> dict[str, Any]:
        """
        Process a problem using Ultrathink.

        Args:
            problem: Problem to solve
            strategy: Optional strategy override
            context: Optional context
            **kwargs: Additional arguments for strategies

        Returns:
            Solution with metadata
        """
        # If strategy not specified, auto-select
        if not strategy:
            complexity = self._assess_complexity(problem)
            strategy = self._select_strategy(complexity)

        # Execute with selected strategy
        result = await self._execute_strategy(strategy, problem, context, **kwargs)

        # Record execution
        self.execution_history.append({"problem": problem, "strategy": strategy, "result": result})

        return result

    async def refine(self, response: dict[str, Any], critique: dict[str, Any]) -> dict[str, Any]:
        """
        Refine a response based on critique.

        Args:
            response: Original response
            critique: Critique to address

        Returns:
            Refined response
        """
        # Use RCR for refinement
        rcr = self.strategies["rcr"]

        refinement = await rcr.refine(
            original=response.get("output"),
            reflection=critique,
            critiques=[],
            context=response.get("metadata"),
        )

        # Update response
        response["output"] = refinement.refined_answer
        response["metadata"]["refined"] = True
        response["metadata"]["refinement_score"] = refinement.improvement_score

        return response

    def _assess_complexity(self, problem: str) -> float:
        """
        Assess problem complexity.

        Args:
            problem: Problem to assess

        Returns:
            Complexity score (0-1)
        """
        factors = {
            "length": min(len(problem) / 1000, 0.25),
            "questions": min(problem.count("?") * 0.1, 0.2),
            "requirements": min(problem.lower().count("must") * 0.1, 0.15),
            "multi_part": 0.3 if " and " in problem.lower() and problem.count("\n") > 3 else 0,
            "technical": 0.2
            if any(term in problem.lower() for term in ["algorithm", "optimize", "architecture"])
            else 0,
        }
        return min(sum(factors.values()), 1.0)

    def _select_strategy(self, complexity: float) -> str:
        """
        Select reasoning strategy based on complexity.

        Args:
            complexity: Complexity score (0-1)

        Returns:
            Strategy name
        """
        if complexity < ReasoningLevel.BASIC.threshold:
            return "chain_of_thought"
        elif complexity < ReasoningLevel.EXPLORATORY.threshold:
            return "tree_of_thoughts"
        elif complexity < ReasoningLevel.COLLABORATIVE.threshold:
            return "multi_agent_debate"
        else:
            # For maximum complexity, use multi-agent debate with RCR
            return "panel_gpt"

    async def _execute_strategy(
        self, strategy: str, problem: str, context: Any | None, **kwargs
    ) -> dict[str, Any]:
        """
        Execute specific reasoning strategy.

        Args:
            strategy: Strategy name
            problem: Problem to solve
            context: Optional context
            **kwargs: Additional arguments

        Returns:
            Strategy result
        """
        if strategy not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy}")

        strategy_obj = self.strategies[strategy]

        # Execute based on strategy type
        if strategy == "chain_of_thought" or strategy == "plan_and_solve":
            return await strategy_obj.reason(problem, context)

        elif strategy == "tree_of_thoughts":
            search_strategy = kwargs.get("search_strategy", SearchStrategy.BFS)
            return await strategy_obj.explore(problem, search_strategy, context)

        elif strategy in ["multi_agent_debate", "panel_gpt"]:
            num_agents = kwargs.get("num_agents", 3)
            personas = kwargs.get("personas")
            strategy_obj.num_agents = num_agents
            return await strategy_obj.debate(problem, personas, context)

        else:
            # Default: treat as CoT
            return await self.strategies["chain_of_thought"].reason(problem, context)

    def get_execution_history(self) -> list:
        """Get execution history."""
        return self.execution_history

    def clear_history(self):
        """Clear execution history."""
        self.execution_history = []


class UltrathinkSkill:
    """
    Ultrathink as a callable skill.

    This wraps the Ultrathink engine as a skill that can be used by agents.
    """

    PROMPT_TEMPLATE = """
Activate Ultrathink mode for this problem.

Problem: {problem}

Complexity Assessment:
{complexity_analysis}

Selected Strategy: {strategy}

Reasoning Process:
{reasoning_output}

Validation:
- Assumptions: {assumptions}
- Confidence: {confidence}
- Simplification Opportunities: {simplifications}

Final Answer:
{final_answer}
"""

    def __init__(self):
        """Initialize Ultrathink skill."""
        self.engine = UltrathinkEngine()

    async def execute(self, problem: str, strategy: str | None = None, **kwargs) -> dict[str, Any]:
        """
        Execute Ultrathink skill.

        Args:
            problem: Problem to solve
            strategy: Optional strategy override
            **kwargs: Additional arguments

        Returns:
            Ultrathink result
        """
        # Get complexity assessment
        complexity = self.engine._assess_complexity(problem)

        # Process with Ultrathink
        result = await self.engine.process(problem, strategy, **kwargs)

        # Format output
        formatted = self.PROMPT_TEMPLATE.format(
            problem=problem,
            complexity_analysis=f"Complexity Score: {complexity:.2f}",
            strategy=result.get("metadata", {}).get("method", "unknown"),
            reasoning_output=self._format_reasoning(result),
            assumptions="[To be analyzed]",
            confidence="[To be calculated]",
            simplifications="[To be identified]",
            final_answer=result.get("final_answer", "See reasoning output"),
        )

        return {
            "output": formatted,
            "raw_result": result,
            "complexity": complexity,
            "strategy_used": result.get("metadata", {}).get("method"),
            "metadata": result.get("metadata", {}),
        }

    def _format_reasoning(self, result: dict[str, Any]) -> str:
        """Format reasoning output for display."""
        method = result.get("metadata", {}).get("method", "unknown")

        if method == "chain_of_thought":
            chain = result.get("thought_chain", [])
            return "\n".join(f"Step {i + 1}: {step}" for i, step in enumerate(chain))

        elif method == "tree_of_thoughts":
            return f"Explored {result.get('tree_size', 0)} nodes\nBest path found"

        elif method in ["multi_agent_debate", "panel_gpt"]:
            return f"Debate completed in {result.get('num_rounds', 0)} rounds"

        else:
            return str(result.get("output", ""))
