"""CARE: Context-Action-Result-Example

For when you need context-rich, example-driven outputs.
Perfect for creative work, content generation, marketing.

Philosophy: Show, don't just tell. Examples ground the model's understanding.
"""

from typing import Any

from ultrathink.core.prompts.base import BasePrompt


class CARE(BasePrompt):
    """Context-Action-Result-Example prompting.

    Usage:
        >>> care = CARE(
        ...     context="Launching eco-friendly clothing brand targeting Gen Z",
        ...     action="Create Instagram campaign for product launch",
        ...     result="Viral content that drives 10k pre-orders in 30 days",
        ...     example={
        ...         "brand": "Patagonia",
        ...         "campaign": "Don't Buy This Jacket",
        ...         "outcome": "Increased sales 30% via reverse psychology"
        ...     }
        ... )
        >>> result = care.execute("Product: recycled ocean plastic hoodies")

    Why it works:
        - Context: Rich background prevents hallucinations
        - Action: Clear directive
        - Result: Expected outcome quality bar
        - Example: Concrete reference point (critical for subjective tasks)
    """

    def __init__(
        self,
        context: str,
        action: str,
        result: str,
        example: dict[str, Any] | str | None = None,
    ) -> None:
        """Initialize CARE prompt.

        Args:
            context: Background, audience, domain knowledge
            action: What to create/analyze/generate
            result: Expected output characteristics
            example: Reference example(s) to emulate

        """
        super().__init__(context=context, action=action, result=result, example=example)
        self.context = context
        self.action = action
        self.result = result
        self.example = example

    def format(self, user_input: str) -> str:
        """Generate CARE-structured prompt."""
        prompt = f"""CONTEXT:
{self.context}

ACTION:
{self.action}

EXPECTED RESULT:
{self.result}"""

        if self.example:
            if isinstance(self.example, dict):
                example_str = "\n".join(f"- {k}: {v}" for k, v in self.example.items())
            else:
                example_str = self.example

            prompt += f"\n\nEXAMPLE TO EMULATE:\n{example_str}"

        prompt += f"\n\nInput:\n{user_input}"

        return prompt.strip()
