# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""CopyConverterSkill - High-converting copy generation."""

import os
import sys
from typing import Any

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.base_skill import BaseSkill


class CopyConverterSkill(BaseSkill):
    """Generates high-converting copy, funnel assets, messaging."""

    PROMPT_TEMPLATE = """
You are the CopyAgent at pinkln – Steve Jobs in voice.

Given: audience profile {audience}, offer description {offer}, core insight {insight}.

Task:
1. Deep breath. You just awoke as Steve Jobs. This copy must be elegant, intuitive, inevitable.
2. Question assumptions: What does the audience *truly* want? What's the deeper emotional trigger?
3. Write:
   - Headline (25 characters max) that stops scroll
   - Sub-headline expanding promise
   - Core body copy (approx 300 words) with tension → solution → transformation
   - CTA with high leverage
4. Ensure: clarity, simplicity, power. Remove any word that doesn't pull its weight.
5. End with: "If we couldn't read this in 2 seconds, we failed. Simplify more."
"""

    def __init__(self):
        super().__init__(
            name="CopyConverterSkill",
            version="1.0",
            description="Generates high-converting copy, funnel scripts, positioning",
        )
        self.metadata.tags = ["copy", "conversion", "funnel", "messaging"]

    async def execute(self, input_data: dict[str, Any], **kwargs) -> dict[str, Any]:
        """Generate converting copy."""
        result = {
            "headline": "Transform Your [X] in 30 Days",
            "subheadline": "The proven system used by 10,000+ [target audience]",
            "body_copy": "Elegant, compelling copy here...",
            "cta": "Start Your Transformation Now",
        }

        return {"output": result, "metadata": {"skill": self.metadata.name}}

    def get_prompt_template(self) -> str:
        return self.PROMPT_TEMPLATE
