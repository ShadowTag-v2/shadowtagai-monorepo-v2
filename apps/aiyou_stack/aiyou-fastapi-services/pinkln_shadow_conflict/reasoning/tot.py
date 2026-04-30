"""Tree of Thoughts (ToT) reasoning framework.

ToT enables exploration of multiple reasoning paths through a tree structure,
allowing for lookahead, backtracking, and evaluation of different approaches.

Usage:
    tot = TreeOfThoughts()
    result = await tot.explore("Propose next steps for: 4 9 10 13 to make 24")
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SearchStrategy(Enum):
    """Search strategies for tree exploration."""

    BFS = "breadth_first"  # Explore all nodes at current depth before going deeper
    DFS = "depth_first"  # Explore one path fully before backtracking


class ThoughtViability(Enum):
    """Viability ratings for thoughts."""

    SURE = "sure"  # Definitely viable
    LIKELY = "likely"  # Probably viable
    MAYBE = "maybe"  # Possibly viable
    UNLIKELY = "unlikely"  # Probably not viable
    IMPOSSIBLE = "impossible"  # Definitely not viable


@dataclass
class ThoughtNode:
    """A node in the tree of thoughts."""

    id: int
    content: str
    depth: int
    parent_id: int | None = None
    children_ids: list[int] = field(default_factory=list)
    viability: ThoughtViability = ThoughtViability.MAYBE
    value_score: float = 0.5  # 0-1, higher is better
    visited: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


class TreeOfThoughts:
    """Tree of Thoughts reasoning implementation.

    This framework:
    1. Decomposes problems into steps
    2. Generates multiple thoughts per step
    3. Evaluates viability of each thought
    4. Prunes unpromising branches
    5. Explores promising paths
    """

    DECOMPOSE_PROMPT = """
Break down this problem into 3-5 smaller steps:

Problem: {problem}

Steps:
"""

    GENERATE_PROMPT = """
For this step, generate {num_thoughts} different potential approaches or thoughts:

Step: {step}
Context: {context}

Thoughts:
"""

    EVALUATE_PROMPT = """
Evaluate the viability of this thought for solving the problem:

Problem: {problem}
Current thought: {thought}

Rate as: sure / likely / maybe / unlikely / impossible
Provide reasoning for your rating.
"""

    def __init__(self, max_depth: int = 5, thoughts_per_step: int = 3):
        """Initialize ToT framework.

        Args:
            max_depth: Maximum tree depth
            thoughts_per_step: Number of thoughts to generate per step

        """
        self.max_depth = max_depth
        self.thoughts_per_step = thoughts_per_step
        self.nodes: dict[int, ThoughtNode] = {}
        self.next_id = 0
        self.root_id: int | None = None

    async def explore(
        self,
        problem: str,
        strategy: SearchStrategy = SearchStrategy.BFS,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Explore the problem using tree of thoughts.

        Args:
            problem: Problem to explore
            strategy: Search strategy to use
            context: Optional context

        Returns:
            Exploration results with best path

        """
        # Step 1: Decompose into steps
        steps = await self._decompose(problem)

        # Step 2: Create root node
        root = self._create_node(problem, depth=0)
        self.root_id = root.id

        # Step 3: Explore tree
        if strategy == SearchStrategy.BFS:
            await self._explore_bfs(root, steps, context)
        else:
            await self._explore_dfs(root, steps, context)

        # Step 4: Find best path
        best_path = self._find_best_path()

        return {
            "problem": problem,
            "steps": steps,
            "tree_size": len(self.nodes),
            "best_path": best_path,
            "metadata": {
                "method": "tree_of_thoughts",
                "strategy": strategy.value,
                "max_depth": self.max_depth,
            },
        }

    async def _decompose(self, problem: str) -> list[str]:
        """Decompose problem into steps.

        Args:
            problem: Problem to decompose

        Returns:
            List of steps

        """
        # Placeholder - would use LLM in production
        return ["Step 1", "Step 2", "Step 3"]

    async def _generate_thoughts(
        self,
        step: str,
        context: dict[str, Any] | None = None,
    ) -> list[str]:
        """Generate multiple thoughts for a step.

        Args:
            step: Step to generate thoughts for
            context: Optional context

        Returns:
            List of thought strings

        """
        # Placeholder - would use LLM in production
        return [f"Thought {i + 1} for {step}" for i in range(self.thoughts_per_step)]

    async def _evaluate_thought(self, problem: str, thought: str) -> tuple[ThoughtViability, float]:
        """Evaluate viability of a thought.

        Args:
            problem: Original problem
            thought: Thought to evaluate

        Returns:
            (viability rating, value score)

        """
        # Placeholder - would use LLM in production
        return (ThoughtViability.LIKELY, 0.7)

    async def _explore_bfs(
        self,
        root: ThoughtNode,
        steps: list[str],
        context: dict[str, Any] | None,
    ):
        """Explore tree using breadth-first search.

        Args:
            root: Root node
            steps: Problem steps
            context: Optional context

        """
        queue = [root]

        while queue and root.depth < self.max_depth:
            current = queue.pop(0)

            if current.visited:
                continue

            current.visited = True

            # Generate thoughts for this node
            thoughts = await self._generate_thoughts(current.content, context)

            # Create child nodes
            for thought in thoughts:
                # Evaluate thought
                viability, value = await self._evaluate_thought(root.content, thought)

                # Prune if impossible or unlikely
                if viability in [ThoughtViability.IMPOSSIBLE, ThoughtViability.UNLIKELY]:
                    continue

                # Create child node
                child = self._create_node(thought, depth=current.depth + 1, parent_id=current.id)
                child.viability = viability
                child.value_score = value

                # Link to parent
                current.children_ids.append(child.id)

                # Add to queue
                queue.append(child)

    async def _explore_dfs(
        self,
        root: ThoughtNode,
        steps: list[str],
        context: dict[str, Any] | None,
    ):
        """Explore tree using depth-first search.

        Args:
            root: Root node
            steps: Problem steps
            context: Optional context

        """
        stack = [root]

        while stack:
            current = stack.pop()

            if current.visited or current.depth >= self.max_depth:
                continue

            current.visited = True

            # Generate thoughts
            thoughts = await self._generate_thoughts(current.content, context)

            # Create and evaluate children
            for thought in thoughts:
                viability, value = await self._evaluate_thought(root.content, thought)

                if viability in [ThoughtViability.IMPOSSIBLE, ThoughtViability.UNLIKELY]:
                    continue

                child = self._create_node(thought, depth=current.depth + 1, parent_id=current.id)
                child.viability = viability
                child.value_score = value

                current.children_ids.append(child.id)
                stack.append(child)

    def _create_node(self, content: str, depth: int, parent_id: int | None = None) -> ThoughtNode:
        """Create a new thought node.

        Args:
            content: Node content
            depth: Tree depth
            parent_id: Parent node ID

        Returns:
            Created node

        """
        node = ThoughtNode(id=self.next_id, content=content, depth=depth, parent_id=parent_id)
        self.nodes[node.id] = node
        self.next_id += 1
        return node

    def _find_best_path(self) -> list[dict[str, Any]]:
        """Find the best path through the tree.

        Returns:
            List of nodes representing best path

        """
        if not self.nodes:
            return []

        # Find leaf nodes (nodes with no children)
        leaves = [node for node in self.nodes.values() if not node.children_ids]

        if not leaves:
            return []

        # Find leaf with highest value
        best_leaf = max(leaves, key=lambda n: n.value_score)

        # Trace back to root
        path = []
        current_id = best_leaf.id

        while current_id is not None:
            node = self.nodes[current_id]
            path.insert(
                0,
                {
                    "content": node.content,
                    "viability": node.viability.value,
                    "value_score": node.value_score,
                },
            )
            current_id = node.parent_id

        return path

    def get_tree_stats(self) -> dict[str, Any]:
        """Get statistics about the tree."""
        return {
            "total_nodes": len(self.nodes),
            "max_depth_reached": max((n.depth for n in self.nodes.values()), default=0),
            "viable_nodes": len(
                [
                    n
                    for n in self.nodes.values()
                    if n.viability in [ThoughtViability.SURE, ThoughtViability.LIKELY]
                ],
            ),
            "pruned_nodes": len(
                [
                    n
                    for n in self.nodes.values()
                    if n.viability in [ThoughtViability.IMPOSSIBLE, ThoughtViability.UNLIKELY]
                ],
            ),
        }

    def visualize_tree(self) -> str:
        """Create a text visualization of the tree."""
        if not self.root_id:
            return "Empty tree"

        lines = []
        self._visualize_node(self.root_id, lines, prefix="", is_last=True)
        return "\n".join(lines)

    def _visualize_node(
        self,
        node_id: int,
        lines: list[str],
        prefix: str = "",
        is_last: bool = True,
    ):
        """Recursively visualize tree nodes."""
        node = self.nodes[node_id]

        # Add current node
        connector = "└── " if is_last else "├── "
        lines.append(
            f"{prefix}{connector}{node.content[:50]} ({node.viability.value}, {node.value_score:.2f})",
        )

        # Add children
        extension = "    " if is_last else "│   "
        for i, child_id in enumerate(node.children_ids):
            is_last_child = i == len(node.children_ids) - 1
            self._visualize_node(child_id, lines, prefix + extension, is_last_child)
