# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""RTF: Role-Task-Format

The simplest, most elegant prompting pattern.
Perfect for 80% of use cases.

Philosophy: Clarity beats cleverness. Tell the model WHO it is,
WHAT to do, and HOW to respond.
"""

from typing import Literal

from ultrathink.core.prompts.base import BasePrompt


class RTF(BasePrompt):
    """Role-Task-Format prompting.

    Usage:
        >>> rtf = RTF(
        ...     role="expert financial analyst",
        ...     task="analyze Q3 revenue trends",
        ...     format="JSON with insights and recommendations"
        ... )
        >>> result = rtf.execute("Revenue data: [...]")

    Why it works:
        - Role: Activates relevant knowledge/persona in the model
        - Task: Explicit objective prevents drift
        - Format: Ensures parseable, consistent output
    """

    def __init__(
        self,
        role: str,
        task: str,
        format: str = "clear, structured response",
        tone: Literal["professional", "casual", "technical", "creative"] = "professional",
    ) -> None:
        """Initialize RTF prompt.

        Args:
            role: Who the model should be (e.g., "senior Python developer")
            task: What to accomplish (e.g., "review code for security issues")
            format: Output format (e.g., "JSON", "bullet points", "markdown")
            tone: Communication style

        """
        super().__init__(role=role, task=task, format=format, tone=tone)
        self.role = role
        self.task = task
        self.format = format
        self.tone = tone

    def format(self, user_input: str) -> str:
        """Generate RTF-structured prompt."""
        prompt = f"""You are a {self.role}.

Your task: {self.task}

Input:
{user_input}

Please provide a {self.format}.
Tone: {self.tone}"""

        return prompt.strip()
