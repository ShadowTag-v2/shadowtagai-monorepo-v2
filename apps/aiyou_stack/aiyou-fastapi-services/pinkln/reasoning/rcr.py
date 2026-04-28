# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Reflect-Critique-Refine (RCR) reasoning framework.

RCR implements a self-improvement cycle where agents:
1. REFLECT on their own solutions
2. CRITIQUE peer solutions
3. REFINE their answers with novel steps

This is particularly powerful in multi-agent debate scenarios.

Usage:
    rcr = ReflectCritiqueRefine()
    result = await rcr.iterate(initial_solution, peers_solutions)
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ReflectionResult:
    """Result of reflection phase."""

    assumptions: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    confidence: float = 0.5
    self_assessment: str = ""


@dataclass
class CritiqueResult:
    """Result of critique phase."""

    target_id: str
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    bugs: list[str] = field(default_factory=list)
    inefficiencies: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    severity: str = "medium"  # low, medium, high, critical


@dataclass
class RefinementResult:
    """Result of refinement phase."""

    original_answer: Any
    refined_answer: Any
    novel_steps: list[str] = field(default_factory=list)
    changes_made: list[str] = field(default_factory=list)
    improvement_score: float = 0.0
    final_confidence: float = 0.5


class ReflectCritiqueRefine:
    """Reflect-Critique-Refine framework implementation.

    This framework enables:
    - Self-assessment and error detection
    - Peer review and collaborative improvement
    - Iterative refinement with novelty requirements
    """

    REFLECT_PROMPT = """
REFLECT on your solution deeply.

Your solution: {solution}

Consider:
1. What assumptions did you make?
2. Where might you have made errors?
3. What are the limitations of your approach?
4. How confident are you? (0-100%)

Reflection:
"""

    CRITIQUE_PROMPT = """
CRITIQUE this solution carefully.

Solution from {peer_name}: {solution}

Analyze:
1. Strengths: What works well?
2. Weaknesses: What could be improved?
3. Bugs: Any logical errors or mistakes?
4. Inefficiencies: Any wasteful or suboptimal approaches?
5. Suggestions: Concrete improvements

Be specific and constructive.

Critique:
"""

    REFINE_PROMPT = """
REFINE your solution based on reflection and critiques.

Your original solution: {original_solution}

Your reflection: {reflection}

Critiques received:
{critiques}

Requirements:
1. Address identified weaknesses
2. Fix any bugs or errors
3. Add at least one novel step or approach not in your original
4. Make the solution more elegant and robust

If your solution is correct and already excellent, defend it with examples.
If flawed, transform it with breakthrough thinking.
If another solution is superior, adapt and transcend it.

Refined solution:
"""

    def __init__(self):
        """Initialize RCR framework."""
        self.iteration_history: list[dict[str, Any]] = []

    async def iterate(
        self,
        own_solution: Any,
        peer_solutions: list[dict[str, Any]] | None = None,
        max_critiques: int = 2,
        context: dict[str, Any] | None = None,
    ) -> RefinementResult:
        """Perform one RCR iteration.

        Args:
            own_solution: The agent's own solution
            peer_solutions: Solutions from other agents
            max_critiques: Maximum number of peers to critique
            context: Optional context

        Returns:
            Refinement result

        """
        # Phase 1: REFLECT
        reflection = await self.reflect(own_solution, context)

        # Phase 2: CRITIQUE (up to max_critiques peers)
        critiques = []
        if peer_solutions:
            for peer in peer_solutions[:max_critiques]:
                critique = await self.critique(peer, context)
                critiques.append(critique)

        # Phase 3: REFINE
        refinement = await self.refine(own_solution, reflection, critiques, context)

        # Record iteration
        self.iteration_history.append(
            {
                "original": own_solution,
                "reflection": reflection,
                "critiques": critiques,
                "refinement": refinement,
            },
        )

        return refinement

    async def reflect(
        self,
        solution: Any,
        context: dict[str, Any] | None = None,
    ) -> ReflectionResult:
        """Reflect on own solution.

        Args:
            solution: Solution to reflect on
            context: Optional context

        Returns:
            Reflection result

        """
        # Placeholder - would use LLM in production
        return ReflectionResult(
            assumptions=["Assumption 1", "Assumption 2"],
            errors=[],
            limitations=["Limited scope"],
            confidence=0.7,
            self_assessment="Solution appears sound but could be more elegant",
        )

    async def critique(
        self,
        peer_solution: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> CritiqueResult:
        """Critique a peer's solution.

        Args:
            peer_solution: Peer's solution to critique
            context: Optional context

        Returns:
            Critique result

        """
        peer_id = peer_solution.get("id", "unknown")

        # Placeholder - would use LLM in production
        return CritiqueResult(
            target_id=peer_id,
            strengths=["Good structure"],
            weaknesses=["Could be simplified"],
            bugs=[],
            inefficiencies=["Redundant steps"],
            suggestions=["Combine steps 2 and 3"],
            severity="low",
        )

    async def refine(
        self,
        original: Any,
        reflection: ReflectionResult,
        critiques: list[CritiqueResult],
        context: dict[str, Any] | None = None,
    ) -> RefinementResult:
        """Refine solution based on reflection and critiques.

        Args:
            original: Original solution
            reflection: Reflection result
            critiques: List of critiques
            context: Optional context

        Returns:
            Refinement result

        """
        # Analyze critiques to extract improvements
        all_suggestions = []
        for critique in critiques:
            all_suggestions.extend(critique.suggestions)

        # Placeholder - would use LLM in production
        return RefinementResult(
            original_answer=original,
            refined_answer=f"Refined: {original}",
            novel_steps=["New approach using X"],
            changes_made=["Simplified step 2", "Added error handling"],
            improvement_score=0.2,
            final_confidence=0.85,
        )

    def get_iteration_history(self) -> list[dict[str, Any]]:
        """Get complete iteration history."""
        return self.iteration_history

    def clear_history(self):
        """Clear iteration history."""
        self.iteration_history = []


class RCRCodeAdapter(ReflectCritiqueRefine):
    """RCR adapted specifically for code review and improvement.

    This variant focuses on:
    - Identifying bugs and logical errors
    - Detecting inefficiencies
    - Improving code elegance
    - Handling edge cases
    """

    REFLECT_PROMPT = """
REFLECT on your code deeply.

Your code:
```
{solution}
```

Consider:
1. Are there any bugs or logical errors?
2. Are there inefficiencies or performance issues?
3. Are edge cases properly handled?
4. Is the code elegant and maintainable?
5. Does every function name "sing"?

Reflection:
"""

    CRITIQUE_PROMPT = """
CRITIQUE this code carefully.

Code from {peer_name}:
```
{solution}
```

Analyze:
1. Bugs: Any logical errors, off-by-one errors, null pointer issues?
2. Inefficiencies: Unnecessary loops, redundant operations, poor data structures?
3. Edge Cases: What edge cases are missed?
4. Security: Any vulnerabilities (injection, XSS, etc.)?
5. Elegance: How can this be more elegant?

Provide corrected code if bugs found.

Critique:
"""

    REFINE_PROMPT = """
REFINE your code based on reflection and critiques.

Original code:
```
{original_solution}
```

Your reflection: {reflection}

Critiques received:
{critiques}

Requirements:
1. Fix all identified bugs
2. Address inefficiencies
3. Handle all edge cases gracefully
4. Make every function name sing
5. Add at least one novel improvement

Refined code:
"""

    async def refine(
        self,
        original: Any,
        reflection: ReflectionResult,
        critiques: list[CritiqueResult],
        context: dict[str, Any] | None = None,
    ) -> RefinementResult:
        """Refine code based on reflection and critiques.

        Args:
            original: Original code
            reflection: Reflection result
            critiques: List of critiques
            context: Optional context

        Returns:
            Refinement result with corrected code

        """
        # Collect all bugs from critiques
        all_bugs = []
        all_inefficiencies = []
        for critique in critiques:
            all_bugs.extend(critique.bugs)
            all_inefficiencies.extend(critique.inefficiencies)

        # Placeholder refinement
        changes_made = []
        if all_bugs:
            changes_made.append(f"Fixed {len(all_bugs)} bugs")
        if all_inefficiencies:
            changes_made.append(f"Addressed {len(all_inefficiencies)} inefficiencies")
        if reflection.errors:
            changes_made.append(f"Corrected {len(reflection.errors)} self-identified errors")

        return RefinementResult(
            original_answer=original,
            refined_answer=f"# Refined code\n{original}",
            novel_steps=["Added input validation", "Extracted helper function"],
            changes_made=changes_made,
            improvement_score=0.3,
            final_confidence=0.9,
        )
