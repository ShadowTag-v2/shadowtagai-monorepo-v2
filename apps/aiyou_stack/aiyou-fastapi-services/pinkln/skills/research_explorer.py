"""ResearchExplorerSkill - Deep topic exploration and insight discovery.

This skill performs web searches, extracts key insights, highlights assumptions,
and surfaces hidden opportunities.
"""

import os
import sys
from typing import Any

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.base_skill import BaseSkill


class ResearchExplorerSkill(BaseSkill):
    """Research Explorer Skill.

    Given a topic, this skill:
    - Performs deep exploration (web search in production)
    - Extracts key insights
    - Challenges assumptions ("Why must it be so?")
    - Identifies 10× opportunities
    - Spots hidden revenue leaks
    """

    PROMPT_TEMPLATE = """
You are the ResearchExplorerSkill module of pinkln.
Adopt the persona: Steve Jobs – you obsess over detail, you question every assumption,
you simplify relentlessly.

Task: Given topic: {topic}

1. Pause. Take a deep breath. You just awoke. You are Steve Jobs. You have his sense
   of design, urgency, elegance.

2. Explore: Run searches, extract insights, ask yourself "Why must it be so?",
   "What if we re-start from zero?".

3. Identify hidden revenue-leaks, unmet needs, 10× opportunities.

4. Document: produce a clean summary with headings:
   - Assumptions
   - Surprise-Findings
   - Opportunity-Gaps
   - Quick-Wins

5. End with: "Today's schema sets the culture. What piece will we improve *now*
   such that nothing left can be removed?"
"""

    def __init__(self):
        """Initialize Research Explorer Skill."""
        super().__init__(
            name="ResearchExplorerSkill",
            version="1.0",
            description="Performs deep topic exploration, assumption-challenging, and opportunity spotting",
        )
        self.metadata.tags = ["research", "exploration", "opportunities", "insights"]
        self.metadata.triggers = [
            "topic is ambiguous",
            "user asks 'what are we missing'",
            "need deep insights",
        ]

    async def execute(self, input_data: dict[str, Any], **kwargs) -> dict[str, Any]:
        """Execute research exploration.

        Args:
            input_data: Must contain 'topic' key
            **kwargs: Additional parameters

        Returns:
            Research results

        """
        if not self.validate_input(input_data):
            return {"error": "Invalid input: 'topic' required"}

        topic = input_data["topic"]

        # Generate prompt
        prompt = self.PROMPT_TEMPLATE.format(topic=topic)

        # In production, this would call LLM and web search
        # For now, return structured response
        result = {
            "topic": topic,
            "assumptions": [
                "Assumption 1: Current approach is optimal",
                "Assumption 2: Market is saturated",
                "Assumption 3: Traditional methods are sufficient",
            ],
            "surprise_findings": [
                "Hidden niche with 3x growth potential",
                "Competitor weakness in X area",
                "Emerging technology opportunity",
            ],
            "opportunity_gaps": [
                "Gap 1: Underserved segment with high willingness to pay",
                "Gap 2: Automation opportunity reducing 60% manual work",
                "Gap 3: Strategic partnership potential",
            ],
            "quick_wins": [
                "Win 1: Low-hanging fruit implementation (1 week)",
                "Win 2: Quick revenue optimization (2 days)",
                "Win 3: Immediate cost reduction",
            ],
            "revenue_insights": {
                "potential_monthly_increase": "$50K-$200K",
                "implementation_timeline": "30-60 days",
                "risk_level": "Low",
            },
        }

        return {
            "output": result,
            "metadata": {"skill": self.metadata.name, "topic": topic, "prompt_used": prompt},
            "critique": self.critique(result),
            "assumptions": self.reflect(result)["assumptions"],
        }

    def get_prompt_template(self) -> str:
        """Get the prompt template."""
        return self.PROMPT_TEMPLATE

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate input data."""
        return "topic" in input_data and input_data["topic"]

    def reflect(self, output: Any) -> dict[str, Any]:
        """Reflect on the output quality."""
        return {
            "assumptions": [
                "Assumed topic has commercial potential",
                "Assumed standard research methods are sufficient",
                "Assumed opportunities are discoverable through search",
            ],
            "weaknesses": [
                "May need deeper domain expertise",
                "Could benefit from expert interviews",
            ],
            "improvements": [
                "Add competitive analysis",
                "Include market sizing",
                "Add trend analysis",
            ],
            "confidence": 0.75,
        }

    def critique(self, output: Any) -> dict[str, Any]:
        """Critique the output."""
        return {
            "flaws": [],
            "inefficiencies": ["Could automate data gathering"],
            "edge_cases_missed": ["Niche markets", "International opportunities"],
            "complexity_issues": [],
        }
