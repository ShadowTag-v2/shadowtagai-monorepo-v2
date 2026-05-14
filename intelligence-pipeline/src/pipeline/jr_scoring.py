# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
PNKLN Intelligence Pipeline - JR Engine Scoring

JR (Junior) Engine provides initial scoring and reasoning for intelligence items.
Uses Claude API (Haiku for cost efficiency) to analyze relevance and impact.

Scoring Criteria:
- Business relevance (0-1): Direct impact on PNKLN operations
- Regulatory impact (0-1): Compliance requirements
- Competitive intelligence (0-1): Market positioning insights
- Timing urgency (0-1): How soon action is needed
- Strategic value (0-1): Long-term business value

Final score: Weighted average (0-1 scale)
"""

import anthropic
import os
import json
import logging
from typing import List
from datetime import datetime

from ..models.intelligence_item import IntelligenceItem, JRScore

logger = logging.getLogger(__name__)


class JRScoringEngine:
    """
    JR Engine for scoring intelligence items using Claude API
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize JR scoring engine

        Args:
            api_key: Anthropic API key (defaults to env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        logger.info("JRScoringEngine initialized")

    async def score_items(self, items: list[IntelligenceItem]) -> list[IntelligenceItem]:
        """
        Score all intelligence items

        Args:
            items: List of intelligence items to score

        Returns:
            Same list with jr_score and jr_reasoning populated
        """
        logger.info(f"=== JR Engine Scoring {len(items)} items ===")
        start_time = datetime.now()

        for i, item in enumerate(items):
            try:
                jr_score = await self.score_item(item)
                item.jr_score = jr_score.score
                item.jr_reasoning = jr_score.reasoning

                logger.info(f"[{i + 1}/{len(items)}] {item.title[:50]}... → Score: {jr_score.score:.2f}")

            except Exception as e:
                logger.error(f"Error scoring item {item.id}: {e}")
                item.jr_score = 0.0
                item.jr_reasoning = f"Scoring failed: {str(e)}"

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"✓ JR Scoring complete in {duration:.1f}s")

        return items

    async def score_item(self, item: IntelligenceItem) -> JRScore:
        """
        Score a single intelligence item using Claude

        Args:
            item: Intelligence item to score

        Returns:
            JRScore with score and reasoning
        """
        prompt = self._build_scoring_prompt(item)

        try:
            message = self.client.messages.create(
                model="claude-3-5-haiku-20241022",  # Cost-efficient model
                max_tokens=1024,
                temperature=0.3,  # Low temp for consistent scoring
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text

            # Parse JSON response
            score_data = json.loads(response_text)

            return JRScore(
                score=score_data["final_score"],
                reasoning=score_data["reasoning"],
                confidence=score_data["confidence"],
                key_factors=score_data["key_factors"],
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JR response: {e}")
            # Fallback: extract score from text
            return JRScore(score=0.5, reasoning="Failed to parse structured response", confidence=0.3, key_factors=[])

    def _build_scoring_prompt(self, item: IntelligenceItem) -> str:
        """
        Build scoring prompt for Claude

        Args:
            item: Intelligence item

        Returns:
            Prompt string
        """
        return f"""You are JR, the Junior Intelligence Analyst for PNKLN, an AI governance platform startup.

Your task is to score this intelligence item on a 0.0 to 1.0 scale based on business relevance.

INTELLIGENCE ITEM:
- Source: {item.source.value}
- Title: {item.title}
- URL: {item.url}
- Published: {item.published_date.strftime("%Y-%m-%d")}
- Content: {item.content[:1000]}  # First 1000 chars

PNKLN BUSINESS CONTEXT:
- Product: AI governance & compliance platform
- Target: Enterprise customers (healthcare, finance, government)
- Stage: Pre-seed, building toward $750K ARR (Gate A)
- Focus: Regulatory compliance, risk management, audit trails
- Competitors: Palantir, Scale AI, DataRobot

SCORING CRITERIA (each 0-1):
1. Business Relevance: Direct impact on PNKLN product/operations
2. Regulatory Impact: New compliance requirements or regulations
3. Competitive Intelligence: Insights on market positioning
4. Timing Urgency: How soon does this require action?
5. Strategic Value: Long-term business value

RESPONSE FORMAT (JSON):
{{
  "business_relevance": 0.0-1.0,
  "regulatory_impact": 0.0-1.0,
  "competitive_intelligence": 0.0-1.0,
  "timing_urgency": 0.0-1.0,
  "strategic_value": 0.0-1.0,
  "final_score": 0.0-1.0,  // Weighted average
  "confidence": 0.0-1.0,
  "reasoning": "Brief explanation (2-3 sentences)",
  "key_factors": ["factor1", "factor2", "factor3"]
}}

Provide ONLY the JSON response, no other text.
"""


async def main():
    """
    Main JR scoring entry point
    """
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Load items from ingestion
    input_file = "/tmp/intelligence_items.json"
    with open(input_file) as f:
        items_data = json.load(f)

    items = [IntelligenceItem.from_dict(item_data) for item_data in items_data]

    # Score items
    engine = JRScoringEngine()
    scored_items = await engine.score_items(items)

    # Save scored items
    output_file = "/tmp/intelligence_items_scored.json"
    with open(output_file, "w") as f:
        json.dump([item.to_dict() for item in scored_items], f, indent=2, default=str)

    print(f"✓ Scored {len(scored_items)} items")
    print(f"✓ Saved to {output_file}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
