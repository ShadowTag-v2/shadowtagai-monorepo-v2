"""Recursive Critique and Refinement (RCR) Skill

Iteratively improve responses through self-critique

Example:
  Initial: "The code works."

  Critique 1: "Too vague. Specify what 'works' means."
  Refine 1: "The code passes all unit tests."

  Critique 2: "Add performance metrics."
  Refine 2: "The code passes all unit tests and runs in O(n log n) time."

  Critique 3: "Mention edge cases."
  Final: "The code passes all unit tests, runs in O(n log n) time, and handles empty inputs gracefully."

Research: Self-Refine (https://arxiv.org/abs/2303.17651)

"""

import asyncio
import time
from typing import Any

from .base import Skill, SkillResult


class CritiqueResult:
    """Result of critiquing a response"""

    def __init__(self, issues: list[str], score: float, is_acceptable: bool):
        self.issues = issues  # List of identified issues
        self.score = score  # Quality score (0-1)
        self.is_acceptable = is_acceptable  # Good enough to stop?

    def __repr__(self) -> str:
        status = "✓ Acceptable" if self.is_acceptable else "✗ Needs work"
        return f"Critique[score={self.score:.2f}, {len(self.issues)} issues] {status}"


class RecursiveCritique(Skill):
    """Recursive Critique and Refinement skill

    1. Generate initial response
    2. Critique the response
    3. Refine based on critique
    4. Repeat until acceptable or max iterations
    """

    def __init__(
        self,
        name: str = "RecursiveCritique",
        description: str = "Iteratively improve responses through self-critique",
        initial_rating: float = 1650.0,  # Higher than ToT (more sophisticated)
        model: str = "gemini-2.0-flash-exp",
        max_iterations: int = 3,
        acceptance_threshold: float = 0.85,
    ):
        # CheatSheet for RCR
        cheatsheet = """
# Recursive Critique and Refinement CheatSheet

## Pattern
1. **Generate** initial response
2. **Critique** the response objectively
3. **Identify** specific issues
4. **Refine** to address issues
5. **Repeat** until acceptable

## Critique Criteria
- Accuracy: Is the information correct?
- Completeness: Are all aspects covered?
- Clarity: Is it easy to understand?
- Specificity: Is it concrete vs vague?
- Correctness: Are there logical errors?

## Template
Response V1: [Initial attempt]

Critique V1:
  - Issue 1: [Specific problem]
  - Issue 2: [Another problem]
  Score: 0.6/1.0

Response V2: [Improved version]

Critique V2:
  - Issue 1: Fixed ✓
  - Remaining: [If any]
  Score: 0.9/1.0 → ACCEPTED
"""

        super().__init__(
            name=name,
            description=description,
            initial_rating=initial_rating,
            cheatsheet=cheatsheet,
        )

        self.model = model
        self.max_iterations = max_iterations
        self.acceptance_threshold = acceptance_threshold

    async def execute(self, task: str, context: dict[str, Any] | None = None) -> SkillResult:
        """Execute Recursive Critique and Refinement

        Args:
            task: Problem to solve
            context: Optional context (max_iterations override, etc.)

        Returns:
            SkillResult with refinement trace

        """
        start_time = time.time()

        # Extract parameters
        max_iter = (
            context.get("max_iterations", self.max_iterations) if context else self.max_iterations
        )
        threshold = (
            context.get("acceptance_threshold", self.acceptance_threshold)
            if context
            else self.acceptance_threshold
        )

        # Iterative refinement
        current_response = await self._generate_initial(task)
        reasoning_trace = [f"V1 (initial): {current_response}"]
        iteration = 1

        while iteration <= max_iter:
            # Critique current response
            critique = await self._critique(task, current_response)
            reasoning_trace.append(
                f"Critique V{iteration}: Score {critique.score:.2f}, Issues: {', '.join(critique.issues) if critique.issues else 'None'}",
            )

            # Check if acceptable
            if critique.is_acceptable or critique.score >= threshold:
                break

            # Refine
            refined_response = await self._refine(task, current_response, critique)
            reasoning_trace.append(f"V{iteration + 1} (refined): {refined_response}")

            current_response = refined_response
            iteration += 1

        latency_ms = (time.time() - start_time) * 1000

        # Final critique for confidence
        final_critique = await self._critique(task, current_response)

        return SkillResult(
            output=current_response,
            reasoning_trace=reasoning_trace,
            confidence=final_critique.score,
            tokens_used=self._estimate_tokens(task, iteration),
            latency_ms=latency_ms,
            metadata={
                "skill": "RecursiveCritique",
                "iterations": iteration,
                "final_score": final_critique.score,
            },
        )

    async def _generate_initial(self, task: str) -> str:
        """Generate initial response

        In production, call Gemini API
        """
        # Mock implementation
        return "Initial response to the task (placeholder)"

    async def _critique(self, task: str, response: str) -> CritiqueResult:
        """Critique a response

        In production:
        ```python
        prompt = f\"\"\"
        Task: {task}

        Response: {response}

        Critique this response. Identify issues:
        1. Accuracy
        2. Completeness
        3. Clarity
        4. Specificity

        Score (0-1):
        Issues:
        \"\"\"

        critique_text = await gemini.generate(prompt)
        # Parse score and issues
        ```

        For now, mock based on iteration
        """
        # Mock: Improve score over iterations
        score = 0.6 + (len(response) / 500) * 0.3  # Longer = better (rough heuristic)
        score = min(score, 0.95)

        issues = []
        if score < 0.7:
            issues.append("Too vague, add specifics")
        if score < 0.8:
            issues.append("Missing edge cases")
        if score < 0.9:
            issues.append("Could be more concise")

        return CritiqueResult(
            issues=issues,
            score=score,
            is_acceptable=score >= self.acceptance_threshold,
        )

    async def _refine(self, task: str, current_response: str, critique: CritiqueResult) -> str:
        """Refine response based on critique

        In production:
        ```python
        prompt = f\"\"\"
        Task: {task}

        Current response: {current_response}

        Issues identified:
        {chr(10).join(f"- {issue}" for issue in critique.issues)}

        Provide an improved response that addresses these issues:
        \"\"\"

        refined = await gemini.generate(prompt)
        return refined
        ```
        """
        # Mock: Add more detail
        return f"{current_response} [Refined to address: {', '.join(critique.issues)}]"

    def _estimate_tokens(self, task: str, iterations: int) -> int:
        """Estimate total tokens used"""
        task_tokens = len(task) // 4
        # Each iteration: response (200) + critique (300) + refine (400)
        iteration_tokens = iterations * 900
        return task_tokens + iteration_tokens


# Example usage
async def example():
    """Example: RCR on a code review task"""
    rcr = RecursiveCritique(max_iterations=3, acceptance_threshold=0.85)

    result = await rcr.execute(
        "Review this Python function:\n\n"
        "def add(a, b):\n"
        "    return a + b\n\n"
        "Provide feedback on correctness, type safety, and documentation.",
    )

    print(f"Final response:\n{result.output}\n")
    print("Refinement trace:")
    for trace in result.reasoning_trace:
        print(f"  • {trace}")
    print(f"\nConfidence: {result.confidence:.1%}")
    print(f"Iterations: {result.metadata['iterations']}")
    print(f"Latency: {result.latency_ms:.0f}ms")


if __name__ == "__main__":
    asyncio.run(example())
