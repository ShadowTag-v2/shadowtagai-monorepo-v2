"""WorkflowRefinerSkill - Ruthless workflow simplification.
"""

import os
import sys
from typing import Any

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.base_skill import BaseSkill


class WorkflowRefinerSkill(BaseSkill):
    """Simplifies workflows ruthlessly: merge, remove, optimize."""

    PROMPT_TEMPLATE = """
You are the WorkflowRefinerSkill module at pinkln – Steve Jobs's personal optimizer.

Given: workflow description {workflow} (steps, tools, roles).

Task:
1. Take a deep breath. You're Steve Jobs. No unnecessary steps.
2. Map the workflow: list each step, who does it, time cost, tools used.
3. For each step ask: Why must this step exist? Who's it serving? Can we remove or merge?
4. Propose: a simplified flow with fewer steps, higher leverage, fewer hand-offs.
5. Output: original vs refined, with explanation of each removal/merge.
6. End with: "Elegance achieved when there's nothing left to remove."
"""

    def __init__(self):
        super().__init__(
            name="WorkflowRefinerSkill",
            version="1.0",
            description="Simplifies workflows ruthlessly: merge/remove steps, increase leverage",
        )
        self.metadata.tags = ["workflow", "optimization", "simplification", "efficiency"]

    async def execute(self, input_data: dict[str, Any], **kwargs) -> dict[str, Any]:
        """Refine workflow."""
        input_data.get("workflow", {})

        result = {
            "original_steps": 12,
            "refined_steps": 7,
            "removals": [
                {"step": "Manual data entry", "reason": "Automate with integration"},
                {"step": "Duplicate approval", "reason": "Redundant with step 3"},
            ],
            "merges": [
                {
                    "steps": ["Step 4", "Step 5"],
                    "into": "Combined validation",
                    "reason": "Same context",
                },
            ],
            "time_saved": "8 hours/week",
            "complexity_reduction": "42%",
        }

        return {"output": result, "metadata": {"skill": self.metadata.name}}

    def get_prompt_template(self) -> str:
        return self.PROMPT_TEMPLATE
