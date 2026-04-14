"""PNKLN Core Stack - Tier Classification Engine

Classifies ingested items into tiers using Gemini 2.0 Pro:
- Tier 1: High-value, time-sensitive intelligence (target 20%)
- Tier 2: Medium-value, contextual information (target 50%)
- Tier 3: Archive/reference material (target 30%)

Scoring dimensions:
- Relevance: How relevant to PNKLN's intelligence focus
- Timeliness: How time-sensitive the information is
- Completeness: Quality and completeness of metadata
- Source Authority: Credibility of the source
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

import structlog
from anthropic import Anthropic

from ingestion.core.config import get_config

logger = structlog.get_logger(__name__)


@dataclass
class TierScore:
    """Classification score breakdown."""

    relevance: float  # 0.0-1.0
    timeliness: float  # 0.0-1.0
    completeness: float  # 0.0-1.0
    source_authority: float  # 0.0-1.0
    overall: float  # weighted average
    tier: Literal[1, 2, 3]
    reasoning: str  # Gemini's explanation


@dataclass
class IngestedItem:
    """Represents an item from any source."""

    id: str
    source: Literal["youtube", "twitter", "news", "rss"]
    title: str
    content: str | None
    url: str
    published_at: datetime
    author: str | None
    metadata: dict

    @property
    def age_hours(self) -> float:
        """Calculate item age in hours."""
        return (datetime.utcnow() - self.published_at).total_seconds() / 3600


class TierClassifier:
    """Classifies ingested items into tiers using Gemini 2.0 Pro.

    Uses structured prompts to evaluate items across multiple dimensions
    and assign tier classifications with reasoning.
    """

    CLASSIFICATION_PROMPT = """You are a intelligence analyst for PNKLN, a strategic information platform. Classify the following item into one of three tiers based on its intelligence value.

**Item Details:**
- Source: {source}
- Title: {title}
- Content Preview: {content_preview}
- Published: {published_at} ({age_hours:.1f} hours ago)
- Author: {author}
- URL: {url}

**Classification Criteria:**

**Tier 1 (High-Value, Time-Sensitive)**:
- Breaking news or emerging trends in AI, technology, geopolitics
- Original research or primary sources
- High-authority sources (major news orgs, verified experts)
- Time-sensitive information requiring immediate attention
- Strategic intelligence with actionable insights

**Tier 2 (Medium-Value, Contextual)**:
- Analysis or commentary on known events
- Secondary sources or aggregated content
- Moderately credible sources
- Useful context but not urgently time-sensitive
- Background information supporting strategic decisions

**Tier 3 (Archive/Reference)**:
- Historical information or evergreen content
- Low-urgency updates or routine announcements
- Unverified or low-authority sources
- Redundant information already covered
- General interest but low strategic value

**Respond in JSON format:**
{{
  "relevance_score": 0.0-1.0,
  "timeliness_score": 0.0-1.0,
  "completeness_score": 0.0-1.0,
  "source_authority_score": 0.0-1.0,
  "overall_score": 0.0-1.0,
  "tier": 1 | 2 | 3,
  "reasoning": "2-3 sentence explanation of tier assignment"
}}"""

    def __init__(self):
        self.config = get_config()
        self.client = Anthropic(api_key=self.config.anthropic.api_key)
        self._classification_count = 0
        self._cost_tracking = 0.0
        logger.info("tier_classifier_initialized", model=self.config.anthropic.model)

    def _format_prompt(self, item: IngestedItem) -> str:
        """Format the classification prompt for a specific item."""
        content_preview = (item.content[:500] + "...") if item.content else "(No content available)"

        return self.CLASSIFICATION_PROMPT.format(
            source=item.source,
            title=item.title,
            content_preview=content_preview,
            published_at=item.published_at.isoformat(),
            age_hours=item.age_hours,
            author=item.author or "(Unknown)",
            url=item.url,
        )

    def _parse_gemini_response(self, response_text: str) -> dict:
        """Parse JSON response from Gemini."""
        import json

        try:
            # Extract JSON from response (Gemini sometimes wraps it)
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            json_str = response_text[start:end]
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error("json_parse_error", error=str(e), response=response_text)
            raise ValueError(f"Failed to parse Gemini response: {e}")

    def _calculate_overall_score(
        self, relevance: float, timeliness: float, completeness: float, source_authority: float,
    ) -> float:
        """Calculate weighted overall score.

        Weights:
        - Relevance: 40%
        - Timeliness: 30%
        - Source Authority: 20%
        - Completeness: 10%
        """
        return relevance * 0.40 + timeliness * 0.30 + source_authority * 0.20 + completeness * 0.10

    def _assign_tier(self, overall_score: float) -> Literal[1, 2, 3]:
        """Assign tier based on overall score and thresholds."""
        if overall_score >= self.config.classification.tier_1_score_threshold:
            return 1
        if overall_score >= self.config.classification.tier_2_score_threshold:
            return 2
        return 3

    async def classify(self, item: IngestedItem) -> TierScore:
        """Classify a single ingested item using Gemini.

        Args:
            item: The ingested item to classify

        Returns:
            TierScore with classification results

        Raises:
            ValueError: If Gemini response is invalid

        """
        prompt = self._format_prompt(item)

        try:
            # Call Gemini API
            response = self.client.messages.create(
                model=self.config.anthropic.model,
                max_tokens=self.config.anthropic.max_tokens,
                temperature=self.config.anthropic.temperature,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse response
            response_text = response.content[0].text
            parsed = self._parse_gemini_response(response_text)

            # Calculate overall score (override Gemini's if needed)
            calculated_overall = self._calculate_overall_score(
                parsed["relevance_score"],
                parsed["timeliness_score"],
                parsed["completeness_score"],
                parsed["source_authority_score"],
            )

            # Assign tier
            tier = self._assign_tier(calculated_overall)

            # Track costs
            self._classification_count += 1
            self._cost_tracking += self.config.ingestion.cost_per_gemini_classification

            score = TierScore(
                relevance=parsed["relevance_score"],
                timeliness=parsed["timeliness_score"],
                completeness=parsed["completeness_score"],
                source_authority=parsed["source_authority_score"],
                overall=calculated_overall,
                tier=tier,
                reasoning=parsed["reasoning"],
            )

            logger.info(
                "item_classified",
                item_id=item.id,
                source=item.source,
                tier=tier,
                overall_score=calculated_overall,
                age_hours=item.age_hours,
            )

            return score

        except Exception as e:
            logger.error("classification_error", item_id=item.id, error=str(e))
            raise

    async def classify_batch(
        self, items: list[IngestedItem], max_concurrent: int = 10,
    ) -> dict[str, TierScore]:
        """Classify multiple items concurrently.

        Args:
            items: List of items to classify
            max_concurrent: Maximum concurrent Gemini API calls

        Returns:
            Dictionary mapping item IDs to TierScores

        """
        import asyncio

        semaphore = asyncio.Semaphore(max_concurrent)

        async def classify_with_semaphore(item: IngestedItem) -> tuple[str, TierScore]:
            async with semaphore:
                score = await self.classify(item)
                return item.id, score

        results = await asyncio.gather(
            *[classify_with_semaphore(item) for item in items], return_exceptions=True,
        )

        # Filter out exceptions
        successful = {}
        failed = []

        for result in results:
            if isinstance(result, Exception):
                failed.append(result)
            else:
                item_id, score = result
                successful[item_id] = score

        if failed:
            logger.warning(
                "batch_classification_partial_failure",
                total=len(items),
                successful=len(successful),
                failed=len(failed),
            )

        return successful

    def get_tier_distribution(self, scores: dict[str, TierScore]) -> dict[str, dict]:
        """Calculate tier distribution statistics.

        Args:
            scores: Dictionary of item scores

        Returns:
            Distribution stats with counts and percentages

        """
        total = len(scores)
        if total == 0:
            return {
                "tier_1": {"count": 0, "percentage": 0.0},
                "tier_2": {"count": 0, "percentage": 0.0},
                "tier_3": {"count": 0, "percentage": 0.0},
                "total": 0,
            }

        tier_counts = {1: 0, 2: 0, 3: 0}
        for score in scores.values():
            tier_counts[score.tier] += 1

        return {
            "tier_1": {
                "count": tier_counts[1],
                "percentage": round(tier_counts[1] / total * 100, 1),
            },
            "tier_2": {
                "count": tier_counts[2],
                "percentage": round(tier_counts[2] / total * 100, 1),
            },
            "tier_3": {
                "count": tier_counts[3],
                "percentage": round(tier_counts[3] / total * 100, 1),
            },
            "total": total,
            "target_distribution": {"tier_1": "20%", "tier_2": "50%", "tier_3": "30%"},
        }

    def get_quality_metrics(self, scores: dict[str, TierScore]) -> dict[str, float]:
        """Calculate aggregate quality metrics."""
        if not scores:
            return {
                "avg_relevance": 0.0,
                "avg_timeliness": 0.0,
                "avg_completeness": 0.0,
                "avg_source_authority": 0.0,
                "avg_overall": 0.0,
            }

        values = list(scores.values())
        n = len(values)

        return {
            "avg_relevance": sum(s.relevance for s in values) / n,
            "avg_timeliness": sum(s.timeliness for s in values) / n,
            "avg_completeness": sum(s.completeness for s in values) / n,
            "avg_source_authority": sum(s.source_authority for s in values) / n,
            "avg_overall": sum(s.overall for s in values) / n,
        }

    def get_stats(self) -> dict:
        """Get classifier statistics."""
        return {
            "total_classifications": self._classification_count,
            "estimated_cost_usd": round(self._cost_tracking, 2),
            "model": self.config.anthropic.model,
            "thresholds": {
                "tier_1": self.config.classification.tier_1_score_threshold,
                "tier_2": self.config.classification.tier_2_score_threshold,
            },
        }
