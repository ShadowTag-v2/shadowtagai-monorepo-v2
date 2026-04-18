"""MonetizationArchitectSkill - Revenue system design."""

import os
import sys
from typing import Any

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.base_skill import BaseSkill


class MonetizationArchitectSkill(BaseSkill):
    """Maps content + audience + offer to scalable revenue streams."""

    PROMPT_TEMPLATE = """
You are the RevenueAgent at pinkln – think Steve Jobs launching the next Apple product.

Given: content catalog {catalog}, audience size {audience}, current offers {offers}.

Task:
1. Deep breath. You are creating a high-leverage income engine.
2. Map out:
   - Core offer (entry-point)
   - Upsell offer (mid-ticket)
   - Continuity/membership (recurring)
   - Premium/legacy (high ticket)
   - Cross-sell/back-sell logic
3. For each: define price point, value proposition, funnel trigger, expected revenue multiplier.
4. Highlight where we are leaving money on the table.
5. End with: "Launch today. Iterate tomorrow. Scale until revenue grows faster than audience."
"""

    def __init__(self):
        super().__init__(
            name="MonetizationArchitectSkill",
            version="1.0",
            description="Designs backend revenue systems: upsell, continuity, premium tiers",
        )
        self.metadata.tags = ["monetization", "revenue", "scalability", "offers"]

    async def execute(self, input_data: dict[str, Any], **kwargs) -> dict[str, Any]:
        """Design monetization architecture."""
        result = {
            "core_offer": {
                "name": "Entry Product",
                "price": 97,
                "value_prop": "Quick win solution",
                "expected_conversion": "5-8%",
            },
            "upsell": {
                "name": "Advanced System",
                "price": 497,
                "value_prop": "Complete transformation",
                "expected_conversion": "25% of buyers",
            },
            "continuity": {
                "name": "Membership",
                "price": 47,
                "frequency": "monthly",
                "expected_ltv": 423,
            },
            "premium": {
                "name": "VIP Coaching",
                "price": 2997,
                "value_prop": "Done-with-you implementation",
                "expected_conversion": "2-3% of buyers",
            },
            "money_on_table": [
                "No upsell sequence: $XX,XXX/month",
                "No continuity program: $XX,XXX/month",
                "No premium tier: $XX,XXX/month",
            ],
        }

        return {"output": result, "metadata": {"skill": self.metadata.name}}

    def get_prompt_template(self) -> str:
        return self.PROMPT_TEMPLATE
