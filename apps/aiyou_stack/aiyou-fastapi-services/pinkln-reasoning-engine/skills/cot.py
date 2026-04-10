"""
Chain of Thought (CoT) Skill

Step-by-step reasoning with explicit intermediate steps

Example:
  Q: What is 15% of 80?
  CoT:
    1. Convert 15% to decimal: 15/100 = 0.15
    2. Multiply by 80: 0.15 × 80
    3. Calculate: 12
  A: 12

Research: https://arxiv.org/abs/2201.11903
"""

import re
import time
from typing import Any

from .base import Skill, SkillResult


class ChainOfThought(Skill):
    """
    Chain of Thought reasoning skill

    Generates explicit step-by-step reasoning before final answer
    """

    def __init__(
        self,
        name: str = "ChainOfThought",
        description: str = "Step-by-step reasoning with explicit intermediate steps",
        initial_rating: float = 1500.0,
        model: str = "gemini-2.0-flash-exp",
    ):
        # CheatSheet for CoT
        cheatsheet = """
# Chain of Thought CheatSheet

## Pattern
1. **Break down** the problem into steps
2. **Show work** for each step explicitly
3. **Build** towards the final answer incrementally

## Template
Let's solve this step by step:

Step 1: [First component/calculation]
Step 2: [Next component, using Step 1]
Step 3: [Continue building]
...
Therefore: [Final answer]

## Examples
✅ Good CoT: "Step 1: Convert units. Step 2: Apply formula. Step 3: Simplify."
❌ Bad CoT: "The answer is X." (no intermediate steps)
"""

        super().__init__(
            name=name, description=description, initial_rating=initial_rating, cheatsheet=cheatsheet
        )

        self.model = model

    async def execute(self, task: str, context: dict[str, Any] | None = None) -> SkillResult:
        """
        Execute Chain of Thought reasoning

        Args:
            task: Problem to solve
            context: Optional context (model override, etc.)

        Returns:
            SkillResult with step-by-step reasoning trace
        """
        start_time = time.time()

        # Build prompt with CheatSheet
        prompt = self._build_prompt(task)

        # Generate with Gemini (mock for now, replace with actual API)
        response = await self._generate(prompt, context)

        # Parse steps
        reasoning_trace = self._extract_steps(response)

        # Extract final answer
        answer = self._extract_answer(response)

        latency_ms = (time.time() - start_time) * 1000

        return SkillResult(
            output=answer,
            reasoning_trace=reasoning_trace,
            confidence=self._estimate_confidence(reasoning_trace),
            tokens_used=self._count_tokens(prompt + response),
            latency_ms=latency_ms,
            metadata={"skill": "ChainOfThought", "steps": len(reasoning_trace)},
        )

    def _build_prompt(self, task: str) -> str:
        """Build CoT prompt with CheatSheet"""
        return f"""{self.cheatsheet}

Now solve this problem using Chain of Thought reasoning:

**Problem:** {task}

**Solution (show your work step-by-step):**
"""

    async def _generate(self, prompt: str, context: dict[str, Any] | None) -> str:
        """
        Generate response (mock implementation)

        Replace with actual Gemini API call:
        ```python
        import google.generativeai as genai
        response = await genai.generate_text_async(
            model=context.get("model", self.model) if context else self.model,
            prompt=prompt
        )
        return response.text
        ```
        """
        # Mock response for now
        return """Let's solve this step by step:

Step 1: Understand the problem
We need to find 15% of 80.

Step 2: Convert percentage to decimal
15% = 15/100 = 0.15

Step 3: Multiply by the number
0.15 × 80 = 12

Therefore: The answer is 12.
"""

    def _extract_steps(self, response: str) -> list[str]:
        """Extract individual reasoning steps"""
        # Match "Step N: ..." patterns
        step_pattern = r"Step \d+:([^\n]+)"
        steps = re.findall(step_pattern, response)
        return [step.strip() for step in steps]

    def _extract_answer(self, response: str) -> str:
        """Extract final answer"""
        # Look for "Therefore:" or "Answer:" or last line
        if "Therefore:" in response:
            return response.split("Therefore:")[-1].strip()
        elif "Answer:" in response:
            return response.split("Answer:")[-1].strip()
        else:
            # Last non-empty line
            lines = [line.strip() for line in response.split("\n") if line.strip()]
            return lines[-1] if lines else ""

    def _estimate_confidence(self, reasoning_trace: list[str]) -> float:
        """
        Estimate confidence based on reasoning quality

        More steps + clear logic = higher confidence
        """
        if not reasoning_trace:
            return 0.3  # Low confidence without steps

        # Confidence increases with step count (plateaus at 5 steps)
        step_confidence = min(len(reasoning_trace) / 5.0, 1.0)

        # Confidence increases if steps build on each other
        building_confidence = 0.8 if len(reasoning_trace) >= 3 else 0.5

        return (step_confidence + building_confidence) / 2

    def _count_tokens(self, text: str) -> int:
        """Rough token count (1 token ≈ 4 characters)"""
        return len(text) // 4


# Example usage
async def example():
    """Example: Chain of Thought on a math problem"""
    cot = ChainOfThought()

    result = await cot.execute("What is 23 × 17?")

    print(f"Answer: {result.output}")
    print("\nReasoning:")
    for i, step in enumerate(result.reasoning_trace, 1):
        print(f"  {i}. {step}")
    print(f"\nConfidence: {result.confidence:.1%}")
    print(f"Latency: {result.latency_ms:.0f}ms")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example())
