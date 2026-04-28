# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""PNKLN Intelligence Pipeline - Tier Classification

Classifies scored intelligence items into three tiers:
- Tier 1 (Score ≥ 0.7): CEO briefing - critical/strategic
- Tier 2 (0.4 ≤ Score < 0.7): Auto-action - medium priority
- Tier 3 (Score < 0.4): Archive only - low priority

Uses Claude API for nuanced classification and action recommendations
"""

import json
import logging
import os
from datetime import datetime

import anthropic

from ..models.intelligence_item import IntelligenceItem, IntelligenceTier, TierClassification

logger = logging.getLogger(__name__)


class TierClassificationEngine:
    """Tier classification engine using Claude API"""

    # Score thresholds
    TIER_1_THRESHOLD = 0.7
    TIER_2_THRESHOLD = 0.4

    def __init__(self, api_key: str | None = None):
        """Initialize tier classification engine

        Args:
            api_key: Anthropic API key (defaults to env var)

        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        logger.info("TierClassificationEngine initialized")

    async def classify_items(self, items: list[IntelligenceItem]) -> list[IntelligenceItem]:
        """Classify all intelligence items into tiers

        Args:
            items: List of scored intelligence items

        Returns:
            Same list with tier and tier_reasoning populated

        """
        logger.info(f"=== Tier Classification for {len(items)} items ===")
        start_time = datetime.now()

        tier_counts = {
            IntelligenceTier.TIER_1: 0,
            IntelligenceTier.TIER_2: 0,
            IntelligenceTier.TIER_3: 0,
        }

        for i, item in enumerate(items):
            try:
                classification = await self.classify_item(item)
                item.tier = classification.tier
                item.tier_reasoning = classification.reasoning

                tier_counts[classification.tier] += 1

                logger.info(
                    f"[{i + 1}/{len(items)}] {item.title[:50]}... "
                    f"→ {classification.tier.value.upper()} (score: {item.jr_score:.2f})",
                )

            except Exception as e:
                logger.error(f"Error classifying item {item.id}: {e}")
                # Default to Tier 3 on error
                item.tier = IntelligenceTier.TIER_3
                item.tier_reasoning = f"Classification failed: {e!s}"
                tier_counts[IntelligenceTier.TIER_3] += 1

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"✓ Classification complete in {duration:.1f}s\n"
            f"  Tier 1: {tier_counts[IntelligenceTier.TIER_1]} items\n"
            f"  Tier 2: {tier_counts[IntelligenceTier.TIER_2]} items\n"
            f"  Tier 3: {tier_counts[IntelligenceTier.TIER_3]} items",
        )

        return items

    async def classify_item(self, item: IntelligenceItem) -> TierClassification:
        """Classify a single intelligence item

        Args:
            item: Scored intelligence item

        Returns:
            TierClassification with tier and reasoning

        """
        # Initial classification based on score thresholds
        if item.jr_score >= self.TIER_1_THRESHOLD:
            initial_tier = IntelligenceTier.TIER_1
        elif item.jr_score >= self.TIER_2_THRESHOLD:
            initial_tier = IntelligenceTier.TIER_2
        else:
            initial_tier = IntelligenceTier.TIER_3

        # Use Claude for nuanced classification and action recommendations
        prompt = self._build_classification_prompt(item, initial_tier)

        try:
            message = self.client.messages.create(
                model="claude-3-5-haiku-20241022",  # Cost-efficient
                max_tokens=512,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text
            classification_data = json.loads(response_text)

            # Use Claude's tier recommendation or fall back to score-based
            tier_str = classification_data.get("tier", initial_tier.value)
            tier = IntelligenceTier(tier_str)

            return TierClassification(
                tier=tier,
                reasoning=classification_data["reasoning"],
                confidence=classification_data["confidence"],
                action_recommendation=classification_data["action_recommendation"],
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to parse classification response, using score-based: {e}")
            return TierClassification(
                tier=initial_tier,
                reasoning=f"Score-based classification: {item.jr_reasoning}",
                confidence=0.6,
                action_recommendation="Review manually",
            )

    def _build_classification_prompt(
        self,
        item: IntelligenceItem,
        initial_tier: IntelligenceTier,
    ) -> str:
        """Build classification prompt for Claude

        Args:
            item: Intelligence item
            initial_tier: Initial score-based tier

        Returns:
            Prompt string

        """
        return f"""You are a tier classification specialist for PNKLN's intelligence pipeline.

INTELLIGENCE ITEM:
- Title: {item.title}
- Source: {item.source.value}
- JR Score: {item.jr_score:.2f}
- JR Reasoning: {item.jr_reasoning}
- Initial Tier: {initial_tier.value}

TIER DEFINITIONS:
- tier_1: CEO briefing required (critical regulatory changes, major competitive moves, strategic opportunities)
- tier_2: Auto-action (update documentation, monitor development, prepare response)
- tier_3: Archive only (informational, low business impact)

TASK:
1. Review the JR score and reasoning
2. Confirm or adjust the tier classification
3. Provide brief reasoning
4. Recommend specific action

RESPONSE FORMAT (JSON):
{{
  "tier": "tier_1" | "tier_2" | "tier_3",
  "reasoning": "Brief explanation (1-2 sentences)",
  "confidence": 0.0-1.0,
  "action_recommendation": "Specific action to take"
}}

Provide ONLY the JSON response, no other text.
"""


async def main():
    """Main tier classification entry point"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Load scored items
    input_file = "/tmp/intelligence_items_scored.json"
    with open(input_file) as f:
        items_data = json.load(f)

    items = [IntelligenceItem.from_dict(item_data) for item_data in items_data]

    # Classify items
    engine = TierClassificationEngine()
    classified_items = await engine.classify_items(items)

    # Save classified items
    output_file = "/tmp/intelligence_items_classified.json"
    with open(output_file, "w") as f:
        json.dump([item.to_dict() for item in classified_items], f, indent=2, default=str)

    print(f"✓ Classified {len(classified_items)} items")
    print(f"✓ Saved to {output_file}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
