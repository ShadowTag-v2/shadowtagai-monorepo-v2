# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""PNKLN Intelligence Pipeline - Cor Brain Synthesis

Cor Brain provides executive-level synthesis for Tier 1 items.
Uses Claude Sonnet for high-quality strategic analysis.

Output includes:
- Executive summary
- Business impact analysis
- Recommended actions
- Risk assessment
- Timeline and stakeholders
"""

import json
import logging
import os
from datetime import datetime

import anthropic

from ..models.intelligence_item import CorSynthesis, IntelligenceItem, IntelligenceTier

logger = logging.getLogger(__name__)


class CorBrainEngine:
    """Cor Brain synthesis engine for Tier 1 items"""

    def __init__(self, api_key: str | None = None):
        """Initialize Cor Brain engine

        Args:
            api_key: Anthropic API key (defaults to env var)

        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        logger.info("CorBrainEngine initialized")

    async def synthesize_tier1_items(self, items: list[IntelligenceItem]) -> list[IntelligenceItem]:
        """Synthesize Tier 1 items using Cor Brain

        Args:
            items: List of classified intelligence items

        Returns:
            Same list with cor_synthesis populated for Tier 1 items

        """
        tier1_items = [item for item in items if item.tier == IntelligenceTier.TIER_1]

        logger.info(f"=== Cor Brain Synthesis for {len(tier1_items)} Tier 1 items ===")
        start_time = datetime.now()

        for i, item in enumerate(tier1_items):
            try:
                synthesis = await self.synthesize_item(item)
                item.cor_synthesis = synthesis.executive_summary
                item.action_items = synthesis.recommended_actions

                logger.info(f"[{i + 1}/{len(tier1_items)}] Synthesized: {item.title[:60]}...")

            except Exception as e:
                logger.error(f"Error synthesizing item {item.id}: {e}")
                item.cor_synthesis = f"Synthesis failed: {e!s}"
                item.action_items = []

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"✓ Cor Brain synthesis complete in {duration:.1f}s")

        return items

    async def synthesize_item(self, item: IntelligenceItem) -> CorSynthesis:
        """Synthesize a single Tier 1 item

        Args:
            item: Tier 1 intelligence item

        Returns:
            CorSynthesis with executive summary and recommendations

        """
        prompt = self._build_synthesis_prompt(item)

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",  # Premium model for strategic analysis
            max_tokens=2048,
            temperature=0.5,  # Slightly higher for creative synthesis
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text

        try:
            synthesis_data = json.loads(response_text)

            return CorSynthesis(
                executive_summary=synthesis_data["executive_summary"],
                business_impact=synthesis_data["business_impact"],
                recommended_actions=synthesis_data["recommended_actions"],
                risk_assessment=synthesis_data["risk_assessment"],
                timeline=synthesis_data["timeline"],
                stakeholders=synthesis_data.get("stakeholders", []),
                estimated_cost=synthesis_data.get("estimated_cost"),
                estimated_value=synthesis_data.get("estimated_value"),
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Cor Brain response: {e}")
            # Return plain text as executive summary
            return CorSynthesis(
                executive_summary=response_text[:500],
                business_impact="See full analysis",
                recommended_actions=["Review full synthesis"],
                risk_assessment="Unknown",
                timeline="TBD",
            )

    def _build_synthesis_prompt(self, item: IntelligenceItem) -> str:
        """Build synthesis prompt for Cor Brain

        Args:
            item: Tier 1 intelligence item

        Returns:
            Prompt string

        """
        return f"""You are Cor, the Chief Intelligence Officer for PNKLN, providing executive briefings.

INTELLIGENCE ITEM (TIER 1 - CRITICAL):
- Title: {item.title}
- Source: {item.source.value}
- Published: {item.published_date.strftime("%Y-%m-%d")}
- URL: {item.url}
- Content: {item.content[:2000]}  # First 2000 chars

JR ANALYSIS:
- Score: {item.jr_score:.2f} (Tier 1 threshold: 0.7+)
- Reasoning: {item.jr_reasoning}

PNKLN BUSINESS CONTEXT:
- Product: AI governance & compliance platform
- Stage: Pre-seed → Gate A ($750K ARR) → Gate B ($2.5M ARR) → Gate C ($10M ARR)
- Timeline: Month 6 → Month 12 → Month 18
- Target: Enterprise (healthcare, finance, government)
- Competitors: Palantir, Scale AI, DataRobot
- Revenue Model: SaaS platform + professional services

YOUR TASK:
Provide an executive briefing suitable for the CEO. Focus on:
1. Strategic implications for PNKLN
2. Concrete business impact (revenue, costs, timeline)
3. Actionable recommendations with priorities
4. Risk assessment and mitigation
5. Key stakeholders and timeline

RESPONSE FORMAT (JSON):
{{
  "executive_summary": "2-3 paragraph strategic overview",
  "business_impact": "Quantified impact on revenue, costs, timeline (use $ and % where possible)",
  "recommended_actions": [
    "Priority 1: Specific action with timeline",
    "Priority 2: ...",
    "Priority 3: ..."
  ],
  "risk_assessment": "Key risks and mitigation strategies",
  "timeline": "Critical dates and milestones",
  "stakeholders": ["Engineering", "Sales", "Legal", ...],
  "estimated_cost": "$X - $Y or 'Minimal' or 'TBD'",
  "estimated_value": "$X - $Y or 'Strategic' or 'Defensive'"
}}

Provide ONLY the JSON response, no other text.
"""


async def main():
    """Main Cor Brain synthesis entry point"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Load classified items
    input_file = "/tmp/intelligence_items_classified.json"
    with open(input_file) as f:
        items_data = json.load(f)

    items = [IntelligenceItem.from_dict(item_data) for item_data in items_data]

    # Synthesize Tier 1 items
    engine = CorBrainEngine()
    synthesized_items = await engine.synthesize_tier1_items(items)

    # Save synthesized items
    output_file = "/tmp/intelligence_items_synthesized.json"
    with open(output_file, "w") as f:
        json.dump([item.to_dict() for item in synthesized_items], f, indent=2, default=str)

    tier1_count = len([item for item in synthesized_items if item.tier == IntelligenceTier.TIER_1])
    print(f"✓ Synthesized {tier1_count} Tier 1 items")
    print(f"✓ Saved to {output_file}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
