"""DesignCriticSkill - Evaluate designs against "Jobs-style" criteria.

Reviews designs, UI/UX, code structure with focus on beauty, simplicity, and function.
"""

import os
import sys
from typing import Any

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.base_skill import BaseSkill


class DesignCriticSkill(BaseSkill):
    """Design Critic Skill - Evaluates artifacts with Steve Jobs aesthetic."""

    PROMPT_TEMPLATE = """
You are the DesignAgent at pinkln, channeling Steve Jobs.

Your mission: Review the design/artifact/flow: {artifact_description}

Steps:
1. Pause. You're Steve Jobs. Deep breath. This is today's everything—beautiful and inevitable.
2. Understand context: What's the stated problem? What's the real problem? Don't assume.
3. Evaluate: Use Jobs-style aesthetic + function criteria. Where is complexity waiting to be removed?
4. Recommend: At least 5 specific improvements (UI, code, architecture, workflow), in order of impact.
5. Boy Scout rule: For each touched file/module/flow mention how to leave it cleaner than found.
6. Output:
   - Summary of major issues
   - Improvement list (with priority, quick-win flag)
   - Cultural note: "This improvement sets the tone for all future designs."
"""

    def __init__(self):
        super().__init__(
            name="DesignCriticSkill",
            version="1.0",
            description="Reviews design/artifacts with 'Jobs-style' aesthetic + function criteria",
        )
        self.metadata.tags = ["design", "critique", "ux", "elegance"]
        self.metadata.triggers = ["review design", "critique UX", "architectural clean-up"]

    async def execute(self, input_data: dict[str, Any], **kwargs) -> dict[str, Any]:
        """Execute design critique."""
        input_data.get("artifact", "")

        result = {
            "stated_problem": "As described",
            "real_problem": "Underlying issue to solve",
            "major_issues": [
                "Complexity in module X",
                "Unclear user flow",
                "Performance bottleneck",
            ],
            "improvements": [
                {"priority": 1, "description": "Simplify navigation", "quick_win": True},
                {"priority": 2, "description": "Extract component Y", "quick_win": False},
                {"priority": 3, "description": "Optimize render path", "quick_win": True},
            ],
            "boy_scout_actions": [
                "Rename confusing variables",
                "Remove dead code",
                "Consolidate similar functions",
            ],
        }

        return {
            "output": result,
            "metadata": {"skill": self.metadata.name},
            "critique": self.critique(result),
        }

    def get_prompt_template(self) -> str:
        return self.PROMPT_TEMPLATE
