"""Tier Classification Implementation

Uses Gemini 2.5 Flash-Lite for cost-effective content classification.
Pricing: $0.10 input / $0.40 output per million tokens

Classification criteria:
- Tier 1: Verified sources, high authority, factual accuracy
- Tier 2: Credible sources, moderate authority, generally reliable
- Tier 3: Unverified sources, low authority, needs fact-checking
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

# Note: In production, use google-cloud-aiplatform or google-generativeai
# For now, we'll create the structure


class TierLevel(StrEnum):
    """Data quality tier levels"""

    TIER_1 = "tier_1"
    TIER_2 = "tier_2"
    TIER_3 = "tier_3"


@dataclass
class ClassificationResult:
    """Result from tier classification"""

    tier: TierLevel
    confidence: float  # 0.0 to 1.0
    reasoning: str
    metadata: dict[str, Any]
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

    def meets_threshold(self, threshold: float = 0.60) -> bool:
        """Check if confidence meets minimum threshold"""
        return self.confidence >= threshold


class TierClassifier:
    """Tier classification using Gemini 2.5 Flash-Lite.

    Evaluates content across multiple dimensions:
    - Source credibility and authority
    - Content accuracy and factual basis
    - Timeliness and relevance
    - Completeness of information
    """

    def __init__(
        self,
        model: str = "gemini-3.1-flash-lite-preview-lite",
        confidence_threshold: float = 0.60,
        temperature: float = 0.3,
        max_tokens: int = 8192,
    ):
        """Initialize tier classifier.

        Args:
            model: Gemini model to use
            confidence_threshold: Minimum confidence for classification (60% for pre-prod)
            temperature: Model temperature (lower = more deterministic)
            max_tokens: Maximum tokens for response

        """
        self.model = model
        self.confidence_threshold = confidence_threshold
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Statistics
        self.stats = {
            "total_classifications": 0,
            "tier_1_count": 0,
            "tier_2_count": 0,
            "tier_3_count": 0,
            "below_threshold": 0,
            "total_tokens_used": 0,
            "total_cost_usd": 0.0,
        }

        # Known high-quality domains (Tier 1)
        self.tier_1_domains = {
            "reuters.com",
            "apnews.com",
            "bbc.com",
            "bloomberg.com",
            "nature.com",
            "science.org",
            "arxiv.org",
        }

        # Known moderate domains (Tier 2)
        self.tier_2_domains = {
            "techcrunch.com",
            "wired.com",
            "theverge.com",
            "arstechnica.com",
        }

    def _get_classification_prompt(self, content: dict[str, Any]) -> str:
        """Generate classification prompt for Gemini.

        Args:
            content: Content metadata to classify

        Returns:
            Formatted prompt for Gemini

        """
        source = content.get("source", "unknown")
        domain = content.get("domain", "unknown")
        title = content.get("title", "")
        text = content.get("text", "")[:1000]  # First 1000 chars
        author = content.get("author", "unknown")

        prompt = f"""Classify this content into one of three quality tiers for an intelligence ingestion pipeline:

**Content to Classify:**
- Source: {source}
- Domain: {domain}
- Author: {author}
- Title: {title}
- Text Preview: {text}

**Classification Criteria:**

**TIER 1** (High-Value, Verified):
- Established news organizations (Reuters, AP, BBC, Bloomberg)
- Peer-reviewed academic sources (Nature, Science, ArXiv)
- Official government or institutional sources
- Verified expert authors with credentials
- Factual, well-sourced content
- High editorial standards

**TIER 2** (Medium-Value, Credible):
- Reputable tech publications (TechCrunch, Wired, Ars Technica)
- Industry blogs with good track record
- Known subject matter experts
- Generally reliable but may lack peer review
- Reasonable editorial oversight

**TIER 3** (Low-Value, Unverified):
- Social media posts without verification
- Unknown or new sources
- Opinion pieces without factual basis
- User-generated content platforms
- Sources with questionable credibility
- Lacks editorial oversight

**Required Output Format (JSON):**
{{
    "tier": "tier_1" | "tier_2" | "tier_3",
    "confidence": 0.0 to 1.0,
    "reasoning": "Brief explanation of classification",
    "red_flags": ["list", "of", "concerns"],
    "quality_indicators": ["list", "of", "positive", "signals"]
}}

Provide your classification:"""

        return prompt

    async def classify(self, content: dict[str, Any]) -> ClassificationResult:
        """Classify content into tier.

        Args:
            content: Content metadata dictionary with keys:
                - source: Source name
                - domain: Domain name
                - title: Content title
                - text: Content text
                - author: Author name (optional)
                - url: Source URL (optional)

        Returns:
            ClassificationResult with tier and confidence

        """
        self.stats["total_classifications"] += 1

        # Quick domain-based classification for known sources
        domain = content.get("domain", "").lower()

        if domain in self.tier_1_domains:
            result = ClassificationResult(
                tier=TierLevel.TIER_1,
                confidence=0.95,
                reasoning=f"Known Tier 1 domain: {domain}",
                metadata={"method": "domain_whitelist"},
            )
            self.stats["tier_1_count"] += 1
            return result

        if domain in self.tier_2_domains:
            result = ClassificationResult(
                tier=TierLevel.TIER_2,
                confidence=0.85,
                reasoning=f"Known Tier 2 domain: {domain}",
                metadata={"method": "domain_whitelist"},
            )
            self.stats["tier_2_count"] += 1
            return result

        # For unknown domains, use Gemini classification
        # NOTE: In production, replace with actual Gemini API call
        result = await self._classify_with_gemini(content)

        # Update statistics
        if result.tier == TierLevel.TIER_1:
            self.stats["tier_1_count"] += 1
        elif result.tier == TierLevel.TIER_2:
            self.stats["tier_2_count"] += 1
        else:
            self.stats["tier_3_count"] += 1

        if not result.meets_threshold(self.confidence_threshold):
            self.stats["below_threshold"] += 1

        return result

    async def _classify_with_gemini(self, content: dict[str, Any]) -> ClassificationResult:
        """Classify using Gemini API.

        NOTE: This is a placeholder. In production, implement actual Gemini API call:

        ```python
        import google.generativeai as genai

        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel(self.model)

        prompt = self._get_classification_prompt(content)
        response = await model.generate_content_async(
            prompt,
            generation_config={
                "temperature": self.temperature,
                "max_output_tokens": self.max_tokens
            }
        )

        # Parse JSON response
        result_data = json.loads(response.text)
        ```

        Args:
            content: Content to classify

        Returns:
            ClassificationResult

        """
        # Placeholder implementation
        # In production, use actual Gemini API

        # Heuristic classification based on source
        source = content.get("source", "").lower()
        domain = content.get("domain", "").lower()

        # Simple heuristics
        if "youtube" in source or "reddit" in source or "twitter" in source:
            tier = TierLevel.TIER_3
            confidence = 0.70
            reasoning = "Social media source - requires verification"
        elif "news" in source:
            tier = TierLevel.TIER_2
            confidence = 0.75
            reasoning = "News aggregator - credible but unverified"
        else:
            tier = TierLevel.TIER_3
            confidence = 0.65
            reasoning = "Unknown source - default to Tier 3"

        # Estimate token usage and cost
        # Input: ~500 tokens (prompt + content)
        # Output: ~150 tokens (JSON response)
        input_tokens = 500
        output_tokens = 150
        cost = (input_tokens / 1_000_000 * 0.10) + (output_tokens / 1_000_000 * 0.40)

        self.stats["total_tokens_used"] += input_tokens + output_tokens
        self.stats["total_cost_usd"] += cost

        return ClassificationResult(
            tier=tier,
            confidence=confidence,
            reasoning=reasoning,
            metadata={
                "method": "gemini_api",
                "model": self.model,
                "tokens_used": input_tokens + output_tokens,
                "cost_usd": round(cost, 6),
                "source": source,
                "domain": domain,
            },
        )

    async def classify_batch(self, contents: list[dict[str, Any]]) -> list[ClassificationResult]:
        """Classify multiple items.

        Args:
            contents: List of content dictionaries

        Returns:
            List of ClassificationResults

        """
        import asyncio

        tasks = [self.classify(content) for content in contents]
        return await asyncio.gather(*tasks)

    def get_stats(self) -> dict[str, Any]:
        """Get classification statistics"""
        total = self.stats["total_classifications"]

        if total == 0:
            return self.stats

        return {
            **self.stats,
            "tier_1_percentage": round(self.stats["tier_1_count"] / total * 100, 2),
            "tier_2_percentage": round(self.stats["tier_2_count"] / total * 100, 2),
            "tier_3_percentage": round(self.stats["tier_3_count"] / total * 100, 2),
            "below_threshold_percentage": round(self.stats["below_threshold"] / total * 100, 2),
            "average_cost_per_item": round(self.stats["total_cost_usd"] / total, 6)
            if total > 0
            else 0.0,
        }

    def check_tier_distribution(self) -> dict[str, Any]:
        """Check if tier distribution meets targets.

        Targets:
        - Tier 1: 30%
        - Tier 2: 50%
        - Tier 3: ≤20%

        Returns:
            Distribution analysis with pass/fail status

        """
        stats = self.get_stats()
        total = self.stats["total_classifications"]

        if total == 0:
            return {"status": "no_data", "message": "No classifications yet"}

        tier_1_pct = stats["tier_1_percentage"]
        tier_2_pct = stats["tier_2_percentage"]
        tier_3_pct = stats["tier_3_percentage"]

        # Check targets (with 5% tolerance)
        tier_1_ok = tier_1_pct >= 25  # 30% target, 25% min
        tier_2_ok = tier_2_pct >= 45  # 50% target, 45% min
        tier_3_ok = tier_3_pct <= 25  # 20% max, 25% tolerance

        all_ok = tier_1_ok and tier_2_ok and tier_3_ok

        return {
            "status": "pass" if all_ok else "fail",
            "tier_1": {
                "actual": tier_1_pct,
                "target": 30.0,
                "status": "pass" if tier_1_ok else "fail",
            },
            "tier_2": {
                "actual": tier_2_pct,
                "target": 50.0,
                "status": "pass" if tier_2_ok else "fail",
            },
            "tier_3": {
                "actual": tier_3_pct,
                "target": 20.0,
                "max": 25.0,
                "status": "pass" if tier_3_ok else "fail",
            },
            "total_classifications": total,
        }
