"""
RISE: Role-Input-Steps-Expectation

The most detailed framework. For complex, multi-step processes.
When you need precision and step-by-step execution.

Philosophy: Leave nothing to chance. Explicit > implicit.
"""

from ultrathink.core.prompts.base import BasePrompt


class RISE(BasePrompt):
    """
    Role-Input-Steps-Expectation prompting.

    Usage:
        >>> rise = RISE(
        ...     role="Senior DevOps engineer with Kubernetes expertise",
        ...     input_data="Prod cluster metrics showing memory leak",
        ...     steps=[
        ...         "1. Identify pods with abnormal memory growth",
        ...         "2. Analyze heap dumps and GC patterns",
        ...         "3. Trace to application code or library bug",
        ...         "4. Propose fix with rollback plan"
        ...     ],
        ...     expectation="Root cause analysis + fix implementation + tests"
        ... )
        >>> result = rise.execute("Metrics: [...]")

    Why it works:
        - Role: Expertise/persona context
        - Input: Structured data the model receives
        - Steps: Exact process to follow (prevents shortcuts)
        - Expectation: Output quality/completeness bar
    """

    def __init__(
        self,
        role: str,
        input_data: str,
        steps: list[str] | str,
        expectation: str,
        output_format: str | None = None,
    ) -> None:
        """
        Initialize RISE prompt.

        Args:
            role: Expertise or persona
            input_data: What data/context the model receives
            steps: Sequential process to follow
            expectation: What the output should achieve
            output_format: Optional format specification
        """
        super().__init__(
            role=role,
            input_data=input_data,
            steps=steps,
            expectation=expectation,
            output_format=output_format,
        )
        self.role = role
        self.input_data = input_data
        self.steps = steps
        self.expectation = expectation
        self.output_format = output_format

    def format(self, user_input: str) -> str:
        """Generate RISE-structured prompt."""
        prompt = f"""ROLE:
You are a {self.role}.

INPUT DATA:
{self.input_data}

STEPS TO FOLLOW:"""

        if isinstance(self.steps, list):
            prompt += "\n" + "\n".join(self.steps)
        else:
            prompt += f"\n{self.steps}"

        prompt += f"""

EXPECTATION:
{self.expectation}"""

        if self.output_format:
            prompt += f"\n\nOUTPUT FORMAT:\n{self.output_format}"

        prompt += f"""

User Input:
{user_input}

Please proceed with the analysis following the steps above."""

        return prompt.strip()
