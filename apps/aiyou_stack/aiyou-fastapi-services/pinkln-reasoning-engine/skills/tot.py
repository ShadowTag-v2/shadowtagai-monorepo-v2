"""Tree of Thoughts (ToT) Skill

Explores multiple reasoning paths, evaluates them, and selects the best

Example:
  Q: Use 4 numbers and basic arithmetic to get 24
     Numbers: 4, 6, 8, 10

  ToT explores paths:
    Path 1: (4 + 6) × (10 - 8) = 10 × 2 = 20 ❌
    Path 2: (10 - 4) × (8 - 6) = 6 × 2 = 12 ❌
    Path 3: 6 × (10 - 4) ÷ 8 = 6 × 6 ÷ 8 = 4.5 ❌
    Path 4: (8 - 4) × 6 = 4 × 6 = 24 ✅ (BEST)

Research: https://arxiv.org/abs/2305.10601

"""

import asyncio
import time
from typing import Any

from .base import Skill, SkillResult


class ReasoningPath:
    """A single reasoning path in the tree"""

    def __init__(self, steps: list[str], score: float, leaf: bool = False):
        self.steps = steps  # Reasoning steps
        self.score = score  # Evaluation score (0-1)
        self.leaf = leaf  # Is this a terminal path?

    def __repr__(self) -> str:
        status = "✓" if self.leaf and self.score > 0.8 else "..."
        return f"Path[{len(self.steps)} steps, score={self.score:.2f}] {status}"


class TreeOfThoughts(Skill):
    """Tree of Thoughts reasoning skill

    1. Generate N candidate next steps
    2. Evaluate each step
    3. Select top K paths
    4. Recurse until solution or max depth
    """

    def __init__(
        self,
        name: str = "TreeOfThoughts",
        description: str = "Explore multiple reasoning paths and select the best",
        initial_rating: float = 1600.0,  # Higher than CoT (more sophisticated)
        model: str = "gemini-2.0-flash-exp",
        breadth: int = 3,  # Candidate steps per node
        depth: int = 4,  # Max depth
        top_k: int = 2,  # Keep top-K paths
    ):
        # CheatSheet for ToT
        cheatsheet = """
# Tree of Thoughts CheatSheet

## Pattern
1. **Generate** multiple next steps (breadth)
2. **Evaluate** each step's promise
3. **Prune** low-scoring paths
4. **Recurse** on top paths (depth)
5. **Select** best final path

## Evaluation Criteria
- Correctness: Does this step move towards the goal?
- Feasibility: Is this step valid/executable?
- Novelty: Does this explore new territory?

## Template
Exploring paths:
  Path A: [Step 1A] → [Step 2A] → ... (score: 0.8)
  Path B: [Step 1B] → [Step 2B] → ... (score: 0.6)
  Path C: [Step 1C] → ... (score: 0.4, pruned)

Best path: A
"""

        super().__init__(
            name=name,
            description=description,
            initial_rating=initial_rating,
            cheatsheet=cheatsheet,
        )

        self.model = model
        self.breadth = breadth
        self.depth = depth
        self.top_k = top_k

    async def execute(self, task: str, context: dict[str, Any] | None = None) -> SkillResult:
        """Execute Tree of Thoughts reasoning

        Args:
            task: Problem to solve
            context: Optional context (breadth/depth overrides, etc.)

        Returns:
            SkillResult with best path as reasoning trace

        """
        start_time = time.time()

        # Extract parameters from context
        breadth = context.get("breadth", self.breadth) if context else self.breadth
        depth = context.get("depth", self.depth) if context else self.depth
        top_k = context.get("top_k", self.top_k) if context else self.top_k

        # Build tree
        best_path = await self._build_tree(task, breadth=breadth, depth=depth, top_k=top_k)

        latency_ms = (time.time() - start_time) * 1000

        return SkillResult(
            output=best_path.steps[-1] if best_path.steps else "No solution found",
            reasoning_trace=best_path.steps,
            confidence=best_path.score,
            tokens_used=self._estimate_tokens(task, breadth, depth),
            latency_ms=latency_ms,
            metadata={
                "skill": "TreeOfThoughts",
                "breadth": breadth,
                "depth": depth,
                "paths_explored": breadth**depth,
            },
        )

    async def _build_tree(self, task: str, breadth: int, depth: int, top_k: int) -> ReasoningPath:
        """Build reasoning tree and return best path

        Args:
            task: Problem to solve
            breadth: Candidate steps per node
            depth: Max depth
            top_k: Keep top-K paths at each level

        Returns:
            Best reasoning path

        """
        # Start with root
        current_paths = [ReasoningPath(steps=[], score=1.0)]

        # Expand tree depth-first
        for _level in range(depth):
            next_paths = []

            for path in current_paths:
                # Generate candidate next steps
                candidates = await self._generate_candidates(task, path, breadth)

                # Evaluate each candidate
                for candidate in candidates:
                    new_steps = path.steps + [candidate]
                    score = await self._evaluate_path(task, new_steps)
                    is_leaf = await self._is_solution(task, new_steps)

                    next_paths.append(ReasoningPath(steps=new_steps, score=score, leaf=is_leaf))

                    # Early exit if perfect solution found
                    if is_leaf and score > 0.95:
                        return ReasoningPath(steps=new_steps, score=score, leaf=True)

            # Prune: Keep only top-K paths
            next_paths.sort(key=lambda p: p.score, reverse=True)
            current_paths = next_paths[:top_k]

            # Stop if all paths are leaves
            if all(p.leaf for p in current_paths):
                break

        # Return best path
        return current_paths[0] if current_paths else ReasoningPath(steps=[], score=0.0)

    async def _generate_candidates(
        self,
        task: str,
        current_path: ReasoningPath,
        breadth: int,
    ) -> list[str]:
        """Generate candidate next steps

        In production, this would call Gemini API multiple times
        For now, mock implementation
        """
        # Mock: Generate simple candidates
        current_depth = len(current_path.steps)
        return [
            f"Approach {current_depth}.{i + 1}: Try method {chr(65 + i)}" for i in range(breadth)
        ]

    async def _evaluate_path(self, task: str, steps: list[str]) -> float:
        """Evaluate how promising a path is (0-1)

        In production:
        - Use Gemini to score: "On a scale 0-1, how likely is this path to succeed?"
        - Consider: correctness, feasibility, novelty

        For now, mock based on step count
        """
        # Mock: Prefer paths with 3-4 steps
        if len(steps) == 0:
            return 1.0
        if len(steps) <= 3:
            return 0.8
        if len(steps) == 4:
            return 0.9  # Sweet spot
        return 0.6  # Too long

    async def _is_solution(self, task: str, steps: list[str]) -> bool:
        """Check if path is a complete solution

        In production:
        - Use Gemini to check: "Does this solve the problem? YES/NO"
        - Verify against ground truth if available

        For now, mock based on step count
        """
        # Mock: Consider 4 steps a complete solution
        return len(steps) >= 4

    def _estimate_tokens(self, task: str, breadth: int, depth: int) -> int:
        """Estimate total tokens used in tree exploration"""
        # Rough estimate: task + (breadth^depth × avg_response_tokens)
        task_tokens = len(task) // 4
        tree_tokens = (breadth**depth) * 200  # 200 tokens per node
        return task_tokens + tree_tokens


# Example usage
async def example():
    """Example: Tree of Thoughts on a planning problem"""
    tot = TreeOfThoughts(breadth=3, depth=3, top_k=2)

    result = await tot.execute(
        "Plan a 3-day trip to Tokyo with $1000 budget. Must include: transportation, "
        "accommodation, food, and one cultural experience per day.",
    )

    print(f"Best plan:\n{result.output}\n")
    print("Reasoning tree:")
    for i, step in enumerate(result.reasoning_trace, 1):
        print(f"  Level {i}: {step}")
    print(f"\nConfidence: {result.confidence:.1%}")
    print(f"Paths explored: {result.metadata['paths_explored']}")
    print(f"Latency: {result.latency_ms:.0f}ms")


if __name__ == "__main__":
    asyncio.run(example())
