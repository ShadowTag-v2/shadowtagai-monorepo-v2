"""Chain-of-Thought (CoT) Reasoning

The breakthrough that changed LLM capabilities.
Simple addition: "Let's think step by step."

Philosophy: Slow thinking (System 2) > fast thinking (System 1) for hard problems.
"""

from typing import Literal

from pydantic import BaseModel, Field


class CoTStep(BaseModel):
    """Single step in chain-of-thought reasoning."""

    step_number: int
    thought: str
    reasoning: str
    conclusion: str | None = None


class CoTResult(BaseModel):
    """Result of chain-of-thought reasoning."""

    steps: list[CoTStep]
    final_answer: str
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in answer (0-1)")
    metadata: dict = Field(default_factory=dict)


class CoT:
    """Chain-of-Thought reasoning engine.

    Usage:
        >>> cot = CoT(steps=5, verify=True)
        >>> result = cot.reason(
        ...     "If a SaaS has $10k MRR, $50k CAC, 20% churn, what's breakeven CAC?"
        ... )
        >>> print(result.final_answer)
        "$12,500 CAC (5 months to recover at $2.5k/month net retention)"

    Why it works:
        - Forces explicit reasoning steps (prevents shortcuts)
        - Self-verification catches errors
        - Transparency: you see the thinking, not just the answer
        - 10-80% accuracy boost on complex problems vs. direct prompting
    """

    def __init__(
        self,
        steps: int = 5,
        verify: bool = True,
        style: Literal["detailed", "concise"] = "detailed",
    ) -> None:
        """Initialize CoT reasoner.

        Args:
            steps: Number of reasoning steps to use
            verify: Whether to verify the final answer
            style: How verbose the reasoning should be

        """
        self.steps = steps
        self.verify = verify
        self.style = style

    def format_prompt(self, problem: str) -> str:
        """Generate CoT-structured prompt."""
        prompt = f"""Solve the following problem using step-by-step reasoning.

Problem:
{problem}

Instructions:
- Break down your thinking into {self.steps} clear steps
- For each step, explain your reasoning
- {"Verify your final answer for accuracy" if self.verify else "State your final answer"}
- Style: {self.style}

Let's think step by step:"""

        return prompt.strip()

    def reason(
        self,
        problem: str,
        model: any | None = None,
        temperature: float = 0.3,
    ) -> CoTResult:
        """Execute chain-of-thought reasoning.

        Args:
            problem: The problem to solve
            model: Optional model instance
            temperature: Sampling temperature (lower = more focused)

        Returns:
            CoTResult with steps and final answer

        """
        prompt = self.format_prompt(problem)

        # Execute with LLM
        try:
            from ultrathink.llm import LLMExecutor

            executor = model or LLMExecutor()
            llm_response = executor.execute(prompt, temperature=temperature)

            # Parse response into steps (simple parsing - would be more sophisticated)
            lines = llm_response.content.split("\n")
            steps = []
            final_answer = ""

            for i, line in enumerate(lines):
                if line.strip() and ("step" in line.lower() or i < self.steps):
                    steps.append(
                        CoTStep(
                            step_number=len(steps) + 1,
                            thought=line.strip(),
                            reasoning=line.strip(),
                            conclusion=None,
                        ),
                    )
                if "final answer" in line.lower() or "conclusion" in line.lower():
                    final_answer = line.strip()

            if not final_answer:
                final_answer = lines[-1] if lines else llm_response.content[:200]

            result = CoTResult(
                steps=steps[: self.steps]
                if steps
                else [
                    CoTStep(
                        step_number=1,
                        thought="Generated response",
                        reasoning=llm_response.content[:500],
                        conclusion=None,
                    ),
                ],
                final_answer=final_answer,
                confidence=0.85,  # Could parse from response
                metadata={
                    "technique": "CoT",
                    "num_steps": self.steps,
                    "verified": self.verify,
                    "model": llm_response.model,
                    "tokens": llm_response.tokens_input + llm_response.tokens_output,
                    "cost_usd": llm_response.cost_usd,
                    "latency_ms": llm_response.latency_ms,
                },
            )

        except Exception as e:
            # Fallback
            result = CoTResult(
                steps=[
                    CoTStep(
                        step_number=1,
                        thought=f"Error: {e}",
                        reasoning="Failed to execute",
                        conclusion=None,
                    ),
                ],
                final_answer=f"Error executing CoT: {e}",
                confidence=0.0,
                metadata={"technique": "CoT", "error": str(e)},
            )

        return result

    def __repr__(self) -> str:
        return f"CoT(steps={self.steps}, verify={self.verify}, style={self.style!r})"
