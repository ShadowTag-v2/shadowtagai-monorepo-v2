"""Tree-of-Thoughts (ToT) Reasoning

Multi-path exploration with backtracking.
When there are multiple solution paths, explore them systematically.

Philosophy: Don't commit to the first path. War-game alternatives.
"""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class ThoughtState(StrEnum):
    """State of a thought node in the tree."""

    EXPLORING = "exploring"
    PROMISING = "promising"
    DEAD_END = "dead_end"
    SOLUTION = "solution"


class ThoughtNode(BaseModel):
    """Single node in tree-of-thoughts."""

    id: str
    thought: str
    parent_id: str | None = None
    state: ThoughtState
    value: float = Field(ge=0.0, le=1.0, description="Estimated value/promise (0-1)")
    depth: int = 0


class ToTResult(BaseModel):
    """Result of tree-of-thoughts reasoning."""

    tree: list[ThoughtNode]
    best_path: list[ThoughtNode]
    final_answer: str
    explored_branches: int
    metadata: dict = Field(default_factory=dict)


class ToT:
    """Tree-of-Thoughts reasoning engine.

    Usage:
        >>> tot = ToT(branches=3, max_depth=5, search="bfs")
        >>> result = tot.reason(
        ...     "Design a pricing strategy for a new SaaS tool"
        ... )
        >>> print(f"Explored {result.explored_branches} paths")

    Why it works:
        - Explores multiple solution paths (not just first idea)
        - Backtracks from dead ends
        - Finds non-obvious solutions
        - Critical for problems with multiple valid approaches
        - ~2-5x better than CoT on planning/strategy tasks
    """

    def __init__(
        self,
        branches: int = 3,
        max_depth: int = 5,
        search: Literal["bfs", "dfs", "beam"] = "bfs",
        prune_threshold: float = 0.3,
    ) -> None:
        """Initialize ToT reasoner.

        Args:
            branches: How many alternative paths to explore per node
            max_depth: Maximum tree depth
            search: Search strategy (BFS=breadth-first, DFS=depth-first, beam=best-first)
            prune_threshold: Value below which to prune branches (0-1)

        """
        self.branches = branches
        self.max_depth = max_depth
        self.search = search
        self.prune_threshold = prune_threshold

    def format_prompt(self, problem: str, current_path: list[str]) -> str:
        """Generate ToT exploration prompt."""
        path_context = (
            "\n".join(f"{i + 1}. {step}" for i, step in enumerate(current_path))
            if current_path
            else "Starting fresh"
        )

        prompt = f"""Explore multiple solution paths for this problem using tree-of-thoughts.

Problem:
{problem}

Current path:
{path_context}

Generate {self.branches} alternative next steps.
For each, evaluate its promise (0-1) and explain why.

Format:
Option 1: [thought] (value: X.XX) - [reasoning]
Option 2: ...
"""

        return prompt.strip()

    def reason(
        self,
        problem: str,
        model: any | None = None,
        temperature: float = 0.7,
    ) -> ToTResult:
        """Execute tree-of-thoughts reasoning.

        Args:
            problem: The problem to solve
            model: Optional model instance
            temperature: Higher = more exploration

        Returns:
            ToTResult with tree and best path

        """
        # Placeholder implementation
        # In production, this would:
        # 1. Explore branches using the search strategy
        # 2. Evaluate each node
        # 3. Prune low-value paths
        # 4. Backtrack and explore alternatives
        # 5. Return best path

        result = ToTResult(
            tree=[
                ThoughtNode(
                    id="root",
                    thought=problem,
                    state=ThoughtState.EXPLORING,
                    value=1.0,
                    depth=0,
                ),
            ],
            best_path=[],
            final_answer="Placeholder - would be computed via tree search",
            explored_branches=0,
            metadata={
                "technique": "ToT",
                "branches": self.branches,
                "max_depth": self.max_depth,
                "search_strategy": self.search,
            },
        )

        return result

    def __repr__(self) -> str:
        return f"ToT(branches={self.branches}, max_depth={self.max_depth}, search={self.search!r})"
