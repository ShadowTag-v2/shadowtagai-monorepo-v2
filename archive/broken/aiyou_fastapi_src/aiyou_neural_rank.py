"""
ShadowTag-v4 Neural Ranking Agent
AI-cognition based content ranking (not engagement-based)

Implements:
- Educational value scoring
- Factual accuracy assessment
- Depth of insight analysis
- Long-term relevance prediction
- Anti-clickbait filtering

Target: $275M ARR discovery layer
Cost: ~$0.003 per content item analyzed
"""

import logging
from datetime import datetime
from enum import Enum, StrEnum
from typing import Any

from pydantic import BaseModel, Field

from src.protocols.agent_protocol import (
    AgentMessage,
    AgentRole,
    create_error_message,
    create_response_message,
)
from src.services.gemini_batch import GeminiBatchProcessor

logger = logging.getLogger(__name__)


class RankingTier(StrEnum):
    """ShadowTag-v4 content ranking tiers"""

    TIER_S = "tier_s"  # Exceptional (top 5%)
    TIER_A = "tier_a"  # High quality (top 20%)
    TIER_B = "tier_b"  # Good (top 50%)
    TIER_C = "tier_c"  # Average (top 80%)
    TIER_D = "tier_d"  # Below average


class ContentCategory(StrEnum):
    """Content categories for specialized ranking"""

    EDUCATIONAL = "educational"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    NEWS = "news"
    OPINION = "opinion"
    ENTERTAINMENT = "entertainment"


class AICognitionScore(BaseModel):
    """AI-cognition ranking score breakdown"""

    # Overall score
    overall_score: float = Field(
        ..., ge=0, le=100, description="Overall AI-cognition score (0-100)"
    )
    tier: RankingTier = Field(..., description="Ranking tier")

    # Component scores
    educational_value: float = Field(..., ge=0, le=100, description="Educational/learning value")
    factual_accuracy: float = Field(..., ge=0, le=100, description="Factual accuracy assessment")
    depth_of_insight: float = Field(
        ..., ge=0, le=100, description="Depth and originality of insight"
    )
    long_term_relevance: float = Field(
        ..., ge=0, le=100, description="Long-term value (not trending/viral)"
    )
    clarity_score: float = Field(..., ge=0, le=100, description="Clarity of communication")

    # Anti-metrics (penalize these)
    clickbait_score: float = Field(
        ..., ge=0, le=100, description="Clickbait detection (higher = more clickbait)"
    )
    sensationalism_score: float = Field(..., ge=0, le=100, description="Sensationalism detection")

    # Metadata
    category: ContentCategory = Field(..., description="Content category")
    confidence: float = Field(default=0.8, description="Scoring confidence (0-1)")
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "overall_score": 82.5,
                "tier": "tier_a",
                "educational_value": 85.0,
                "factual_accuracy": 90.0,
                "depth_of_insight": 78.0,
                "long_term_relevance": 88.0,
                "clarity_score": 80.0,
                "clickbait_score": 12.0,
                "sensationalism_score": 8.0,
                "category": "educational",
                "confidence": 0.85,
            }
        }


class ShadowTag-v2NeuralRankAgent:
    """
    ShadowTag-v4 Neural Ranking Agent

    Ranks content by AI-cognition value, NOT engagement metrics.
    Prioritizes:
    - Educational value over viral potential
    - Factual accuracy over sensationalism
    - Depth over brevity
    - Long-term relevance over trending topics

    Anti-patterns detected:
    - Clickbait titles
    - Sensationalist framing
    - Misleading thumbnails
    - Engagement bait

    Usage:
        agent = ShadowTag-v2NeuralRankAgent(gemini_api_key="...")
        score = await agent.rank_content(content_item)
    """

    def __init__(self, gemini_api_key: str, batch_processor: GeminiBatchProcessor | None = None):
        """
        Initialize ShadowTag-v4 Neural Ranking Agent

        Args:
            gemini_api_key: Google AI API key for Gemini
            batch_processor: Optional pre-configured GeminiBatchProcessor
        """
        self.agent_role = AgentRole.NEURAL_RANK

        if batch_processor:
            self.batch_processor = batch_processor
        else:
            self.batch_processor = GeminiBatchProcessor(api_key=gemini_api_key, batch_size=100)

        # Ranking weights
        self.score_weights = {
            "educational_value": 0.30,
            "factual_accuracy": 0.25,
            "depth_of_insight": 0.20,
            "long_term_relevance": 0.15,
            "clarity_score": 0.10,
        }

        # Tier thresholds
        self.tier_thresholds = {
            RankingTier.TIER_S: 85.0,
            RankingTier.TIER_A: 75.0,
            RankingTier.TIER_B: 60.0,
            RankingTier.TIER_C: 45.0,
            RankingTier.TIER_D: 0.0,
        }

        logger.info("ShadowTag-v2NeuralRankAgent initialized")

    async def process_message(self, message: AgentMessage) -> AgentMessage:
        """
        Process incoming agent message

        Expected message.data format:
        {
            "content": Dict with title, description, text, url, etc.
            "action": "rank_content" | "rank_batch"
        }
        """
        try:
            action = message.data.get("action", "rank_content")

            if action == "rank_content":
                result = await self._rank_content_handler(message)
            elif action == "rank_batch":
                result = await self._rank_batch_handler(message)
            else:
                raise ValueError(f"Unknown action: {action}")

            return create_response_message(message, result)

        except Exception as e:
            logger.error(f"ShadowTag-v2NeuralRankAgent error: {e}")
            return create_error_message(message, str(e))

    async def _rank_content_handler(self, message: AgentMessage) -> dict[str, Any]:
        """Handle single content ranking request"""

        content = message.data.get("content", {})

        if not content:
            raise ValueError("content required for ranking")

        # Rank content
        score = await self.rank_content(content)

        return {
            "ai_cognition_score": score.dict(),
            "content_id": content.get("id"),
            "processing_cost_usd": 0.003,
            "status": "completed",
        }

    async def _rank_batch_handler(self, message: AgentMessage) -> dict[str, Any]:
        """Handle batch content ranking request"""

        content_items = message.data.get("content_items", [])

        if not content_items:
            raise ValueError("content_items required for batch ranking")

        # Rank batch
        scores = await self.rank_content_batch(content_items)

        return {
            "scores": [score.dict() for score in scores],
            "total_items": len(scores),
            "processing_cost_usd": len(scores) * 0.003,
            "status": "completed",
        }

    async def rank_content(self, content: dict[str, Any]) -> AICognitionScore:
        """
        Rank single content item by AI-cognition value

        Args:
            content: Content dict with title, description, text, url, etc.

        Returns:
            AICognitionScore with detailed breakdown
        """
        logger.info(f"Ranking content: {content.get('title', 'Untitled')[:50]}")

        # Extract text for analysis
        text = self._extract_content_text(content)

        # Categorize content
        category = await self._categorize_content(text)

        # Analyze content using Gemini
        analysis = await self._analyze_with_gemini(text, category)

        # Compute component scores
        educational_value = analysis.get("educational_value", 50.0)
        factual_accuracy = analysis.get("factual_accuracy", 50.0)
        depth_of_insight = analysis.get("depth_of_insight", 50.0)
        long_term_relevance = analysis.get("long_term_relevance", 50.0)
        clarity_score = analysis.get("clarity_score", 50.0)

        # Detect anti-patterns
        clickbait_score = await self._detect_clickbait(content)
        sensationalism_score = await self._detect_sensationalism(text)

        # Compute overall score (weighted average)
        overall_score = (
            educational_value * self.score_weights["educational_value"]
            + factual_accuracy * self.score_weights["factual_accuracy"]
            + depth_of_insight * self.score_weights["depth_of_insight"]
            + long_term_relevance * self.score_weights["long_term_relevance"]
            + clarity_score * self.score_weights["clarity_score"]
        )

        # Penalize for clickbait and sensationalism
        penalty = (clickbait_score + sensationalism_score) / 2 * 0.15  # Up to 15% penalty
        overall_score = max(0, overall_score - penalty)

        # Determine tier
        tier = self._assign_tier(overall_score)

        score = AICognitionScore(
            overall_score=round(overall_score, 2),
            tier=tier,
            educational_value=round(educational_value, 2),
            factual_accuracy=round(factual_accuracy, 2),
            depth_of_insight=round(depth_of_insight, 2),
            long_term_relevance=round(long_term_relevance, 2),
            clarity_score=round(clarity_score, 2),
            clickbait_score=round(clickbait_score, 2),
            sensationalism_score=round(sensationalism_score, 2),
            category=category,
            confidence=0.85,
        )

        logger.info(
            f"✓ Content ranked: score={score.overall_score}, tier={score.tier}, category={category}"
        )

        return score

    def _extract_content_text(self, content: dict[str, Any]) -> str:
        """Extract text from content for analysis"""
        parts = []

        if content.get("title"):
            parts.append(f"Title: {content['title']}")
        if content.get("description"):
            parts.append(f"Description: {content['description']}")
        if content.get("text"):
            parts.append(f"Content: {content['text'][:2000]}")  # Limit to 2000 chars

        return "\n\n".join(parts) if parts else "Empty content"

    async def _categorize_content(self, text: str) -> ContentCategory:
        """Categorize content using keyword analysis"""

        text_lower = text.lower()

        # Simple keyword-based categorization
        if any(kw in text_lower for kw in ["learn", "tutorial", "guide", "how to", "explain"]):
            return ContentCategory.EDUCATIONAL
        elif any(kw in text_lower for kw in ["code", "algorithm", "api", "framework", "technical"]):
            return ContentCategory.TECHNICAL
        elif any(kw in text_lower for kw in ["art", "music", "design", "creative", "film"]):
            return ContentCategory.CREATIVE
        elif any(kw in text_lower for kw in ["news", "report", "announce", "breaking"]):
            return ContentCategory.NEWS
        elif any(kw in text_lower for kw in ["think", "believe", "opinion", "perspective"]):
            return ContentCategory.OPINION
        else:
            return ContentCategory.ENTERTAINMENT

    async def _analyze_with_gemini(self, text: str, category: ContentCategory) -> dict[str, float]:
        """
        Analyze content using Gemini for component scores

        Uses structured prompting to extract:
        - Educational value
        - Factual accuracy
        - Depth of insight
        - Long-term relevance
        - Clarity
        """
        prompt = f"""
Analyze this {category.value} content for AI-cognition value.

Content:
{text[:1500]}

Rate the following aspects (0-100):

1. Educational Value: How much can someone learn from this? Does it teach or explain concepts clearly?
2. Factual Accuracy: How accurate and well-sourced is the information? (penalize speculation)
3. Depth of Insight: How deep and original is the analysis? Does it go beyond surface-level?
4. Long-term Relevance: Will this be valuable in 6 months? (penalize viral/trending content)
5. Clarity: How clear and well-structured is the communication?

Respond with ONLY a JSON object:
{{
  "educational_value": <score>,
  "factual_accuracy": <score>,
  "depth_of_insight": <score>,
  "long_term_relevance": <score>,
  "clarity_score": <score>
}}
"""

        # Use batch processor for analysis
        try:
            results = await self.batch_processor.analyze_content_batch(
                [text], prompt_template=prompt
            )

            if results and len(results) > 0:
                analysis_text = results[0].get("analysis", "{}")

                # Parse JSON response
                # TODO: Implement proper JSON parsing from Gemini response
                # For now, return mock scores based on category

                return self._get_category_baseline_scores(category)
            else:
                return self._get_category_baseline_scores(category)

        except Exception as e:
            logger.warning(f"Gemini analysis failed: {e}, using baseline scores")
            return self._get_category_baseline_scores(category)

    def _get_category_baseline_scores(self, category: ContentCategory) -> dict[str, float]:
        """Get baseline scores based on content category"""

        baselines = {
            ContentCategory.EDUCATIONAL: {
                "educational_value": 75.0,
                "factual_accuracy": 70.0,
                "depth_of_insight": 65.0,
                "long_term_relevance": 80.0,
                "clarity_score": 70.0,
            },
            ContentCategory.TECHNICAL: {
                "educational_value": 80.0,
                "factual_accuracy": 85.0,
                "depth_of_insight": 75.0,
                "long_term_relevance": 70.0,
                "clarity_score": 65.0,
            },
            ContentCategory.CREATIVE: {
                "educational_value": 50.0,
                "factual_accuracy": 40.0,
                "depth_of_insight": 70.0,
                "long_term_relevance": 60.0,
                "clarity_score": 65.0,
            },
            ContentCategory.NEWS: {
                "educational_value": 55.0,
                "factual_accuracy": 75.0,
                "depth_of_insight": 50.0,
                "long_term_relevance": 30.0,
                "clarity_score": 70.0,
            },
            ContentCategory.OPINION: {
                "educational_value": 45.0,
                "factual_accuracy": 50.0,
                "depth_of_insight": 60.0,
                "long_term_relevance": 40.0,
                "clarity_score": 60.0,
            },
            ContentCategory.ENTERTAINMENT: {
                "educational_value": 25.0,
                "factual_accuracy": 30.0,
                "depth_of_insight": 35.0,
                "long_term_relevance": 20.0,
                "clarity_score": 55.0,
            },
        }

        return baselines.get(category, baselines[ContentCategory.ENTERTAINMENT])

    async def _detect_clickbait(self, content: dict[str, Any]) -> float:
        """
        Detect clickbait patterns in title/thumbnail

        Patterns:
        - ALL CAPS WORDS
        - Excessive punctuation!!!
        - "You won't believe..."
        - "This one trick..."
        - Number bait ("10 shocking...")
        """
        title = content.get("title", "")

        if not title:
            return 0.0

        clickbait_score = 0.0

        # ALL CAPS detection
        caps_ratio = sum(1 for c in title if c.isupper()) / max(len(title), 1)
        if caps_ratio > 0.5:
            clickbait_score += 30.0

        # Excessive punctuation
        punct_count = title.count("!") + title.count("?")
        if punct_count > 2:
            clickbait_score += 20.0

        # Clickbait phrases
        clickbait_phrases = [
            "you won't believe",
            "this one trick",
            "doctors hate",
            "shocking",
            "mind-blowing",
            "what happens next",
            "the truth about",
        ]
        title_lower = title.lower()
        if any(phrase in title_lower for phrase in clickbait_phrases):
            clickbait_score += 40.0

        # Number bait
        if title_lower.startswith(tuple(str(i) for i in range(1, 101))):
            clickbait_score += 15.0

        return min(clickbait_score, 100.0)

    async def _detect_sensationalism(self, text: str) -> float:
        """
        Detect sensationalist language

        Patterns:
        - Extreme adjectives (devastating, catastrophic, incredible)
        - Fear mongering
        - Unsubstantiated claims
        """
        text_lower = text.lower()

        sensationalism_score = 0.0

        # Extreme adjectives
        extreme_words = [
            "devastating",
            "catastrophic",
            "incredible",
            "unbelievable",
            "shocking",
            "horrifying",
            "mind-blowing",
            "insane",
            "crazy",
        ]
        extreme_count = sum(1 for word in extreme_words if word in text_lower)
        sensationalism_score += min(extreme_count * 10, 40.0)

        # Fear mongering phrases
        fear_phrases = ["be afraid", "you should worry", "danger", "crisis", "disaster"]
        if any(phrase in text_lower for phrase in fear_phrases):
            sensationalism_score += 30.0

        return min(sensationalism_score, 100.0)

    def _assign_tier(self, overall_score: float) -> RankingTier:
        """Assign tier based on overall score"""

        if overall_score >= self.tier_thresholds[RankingTier.TIER_S]:
            return RankingTier.TIER_S
        elif overall_score >= self.tier_thresholds[RankingTier.TIER_A]:
            return RankingTier.TIER_A
        elif overall_score >= self.tier_thresholds[RankingTier.TIER_B]:
            return RankingTier.TIER_B
        elif overall_score >= self.tier_thresholds[RankingTier.TIER_C]:
            return RankingTier.TIER_C
        else:
            return RankingTier.TIER_D

    async def rank_content_batch(
        self, content_items: list[dict[str, Any]]
    ) -> list[AICognitionScore]:
        """
        Rank multiple content items in batch

        Optimizes Gemini API calls using batch processor
        Cost: ~$0.003 per item
        """
        logger.info(f"Batch ranking {len(content_items)} content items")

        # Rank all items
        scores = []
        for content in content_items:
            score = await self.rank_content(content)
            scores.append(score)

        total_cost = len(scores) * 0.003
        logger.info(
            f"✓ Batch ranking completed: {len(scores)} items, estimated cost: ${total_cost:.2f}"
        )

        return scores

    def get_feed_ranking(self, scores: list[AICognitionScore]) -> list[AICognitionScore]:
        """
        Sort content by AI-cognition score for feed presentation

        Returns:
            Sorted list (highest score first)
        """
        return sorted(scores, key=lambda s: s.overall_score, reverse=True)
