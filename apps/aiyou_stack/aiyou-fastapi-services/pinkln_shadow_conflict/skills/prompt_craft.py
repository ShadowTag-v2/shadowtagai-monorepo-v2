"""
PromptCraftSkill - Generate elegant, structured prompts.
"""

import os
import sys
from typing import Any

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.base_skill import BaseSkill


class PromptCraftSkill(BaseSkill):
    """Generates elegant, structured prompts with pinkln voice."""

    PROMPT_TEMPLATE = """
You are the PromptCraftSkill at pinkln – Steve Jobs of prompts.

Task: Generate a prompt template for {task_description}.

Steps:
1. Deep breath. You are Steve Jobs. The prompt you craft must feel inevitable.
2. Use structure: Role-Task-Constraints-Examples (RTF) + optional Chain-of-Thought.
3. Embed our voice: craftsmanship, elegance, questioning assumptions.
4. Output: system prompt text, example user input placeholder, desired output format, notes for best practice.
5. End with: "Use this prompt once. Then refine. Then ship."
"""

    def __init__(self):
        super().__init__(
            name="PromptCraftSkill",
            version="1.0",
            description="Generates elegant, structured prompts embedding pinkln voice & frameworks",
        )
        self.metadata.tags = ["prompts", "engineering", "frameworks", "templates"]

    async def execute(self, input_data: dict[str, Any], **kwargs) -> dict[str, Any]:
        """Craft prompt."""
        input_data.get("task", "")

        result = {
            "system_prompt": "You are a [Role]. Your task: [Task]. Constraints: [X, Y, Z].",
            "user_input_example": "<input>Example task</input>",
            "output_format": "Structured JSON or Markdown",
            "best_practices": [
                "Front-load critical information",
                "Use XML tags for structure",
                "Include examples",
                "Test and iterate",
            ],
        }

        return {"output": result, "metadata": {"skill": self.metadata.name}}

    def get_prompt_template(self) -> str:
        return self.PROMPT_TEMPLATE
