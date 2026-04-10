"""
PNKLN Core Stack - Judge #6 Validation Layer

Hybrid Gemini+PyTorch validation system that ensures data quality
and compliance before items reach downstream applications.

Features:
- Multi-stage validation pipeline
- ATP 5-19 risk assessment integration
- p99 ≤90ms latency target
- 98% coverage gates
- ShadowTagJR doctrine compliance
- Calls services across 4 namespaces
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

import structlog
import torch
import torch.nn as nn
from anthropic import Anthropic

from ingestion.classification.tier_classifier import IngestedItem, TierScore
from ingestion.core.config import get_config

logger = structlog.get_logger(__name__)


class RiskLevel(StrEnum):
    """ATP 5-19 Risk Assessment Levels"""

    EXTREMELY_HIGH = "extremely_high"  # RA-5
    HIGH = "high"  # RA-4
    MODERATE = "moderate"  # RA-3
    LOW = "low"  # RA-2
    EXTREMELY_LOW = "extremely_low"  # RA-1


class ValidationStatus(StrEnum):
    """Validation outcome"""

    PASSED = "passed"
    FAILED = "failed"
    FLAGGED = "flagged"  # Needs human review
    BLOCKED = "blocked"  # Hard reject


@dataclass
class ValidationResult:
    """Result of Judge #6 validation"""

    item_id: str
    status: ValidationStatus
    risk_level: RiskLevel
    confidence_score: float  # 0.0-1.0
    validation_checks: dict[str, bool]
    failure_reasons: list[str]
    latency_ms: float
    timestamp: datetime

    # ATP 5-19 fields
    severity: int  # 1-5
    probability: int  # 1-5
    risk_score: int  # severity × probability

    # ShadowTagJR compliance
    jr_compliant: bool
    jr_reasoning: str


class ContentSafetyClassifier(nn.Module):
    """
    PyTorch model for content safety classification.

    Lightweight neural network for fast (<10ms) content screening:
    - Hate speech detection
    - Violence/NSFW detection
    - Misinformation signals
    - Spam detection
    """

    def __init__(self, input_dim: int = 768, hidden_dim: int = 256):
        super().__init__()

        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim // 2, 4),  # 4 safety categories
        )

        self.sigmoid = nn.Sigmoid()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.

        Args:
            x: Input embeddings (batch_size, input_dim)

        Returns:
            Safety scores for 4 categories (batch_size, 4)
        """
        logits = self.encoder(x)
        return self.sigmoid(logits)


class Judge6Validator:
    """
    Judge #6 - Main validation orchestrator.

    Implements hybrid Gemini+PyTorch validation with:
    - Fast PyTorch pre-screening (<10ms)
    - Gemini deep analysis for flagged items
    - ATP 5-19 risk assessment
    - ShadowTagJR compliance checking
    """

    def __init__(self):
        self.config = get_config()

        # Initialize Gemini client
        self.gemini = Anthropic(api_key=self.config.anthropic.api_key)

        # Initialize PyTorch safety classifier
        self.safety_model = ContentSafetyClassifier()
        self.safety_model.eval()  # Inference mode

        # Load pre-trained weights if available
        # TODO: Load actual trained model
        # self.safety_model.load_state_dict(torch.load('models/safety_classifier.pt'))

        # Validation thresholds
        self.safety_threshold = 0.85  # Min safety score to pass
        self.confidence_threshold = 0.70  # Min confidence for auto-pass

        # Performance tracking
        self._validation_count = 0
        self._total_latency_ms = 0.0

        logger.info(
            "judge6_initialized",
            safety_threshold=self.safety_threshold,
            confidence_threshold=self.confidence_threshold,
        )

    async def validate(self, item: IngestedItem, tier_score: TierScore) -> ValidationResult:
        """
        Validate an ingested item using multi-stage pipeline.

        Pipeline:
        1. Fast PyTorch safety screening (<10ms)
        2. Rule-based checks (metadata, completeness)
        3. ATP 5-19 risk assessment
        4. Gemini deep analysis (if flagged)
        5. ShadowTagJR compliance check

        Args:
            item: The ingested item to validate
            tier_score: Classification score from ingestion layer

        Returns:
            ValidationResult with pass/fail decision
        """
        start_time = datetime.utcnow()

        validation_checks = {}
        failure_reasons = []

        # Stage 1: PyTorch safety screening
        safety_scores = await self._safety_screen(item)
        safety_passed = all(score >= self.safety_threshold for score in safety_scores.values())
        validation_checks["safety_screen"] = safety_passed

        if not safety_passed:
            failure_reasons.append(f"Safety screening failed: {safety_scores}")

        # Stage 2: Metadata validation
        metadata_valid = self._validate_metadata(item)
        validation_checks["metadata_valid"] = metadata_valid

        if not metadata_valid:
            failure_reasons.append("Metadata validation failed")

        # Stage 3: Content completeness
        completeness = self._check_completeness(item)
        validation_checks["completeness"] = completeness >= 0.95

        if completeness < 0.95:
            failure_reasons.append(f"Completeness {completeness:.1%} < 95%")

        # Stage 4: Source credibility
        source_credible = self._check_source_credibility(item)
        validation_checks["source_credible"] = source_credible

        if not source_credible:
            failure_reasons.append("Source credibility check failed")

        # Stage 5: ATP 5-19 risk assessment
        risk_assessment = self._assess_risk(item, tier_score, validation_checks)

        # Stage 6: Determine if Gemini deep analysis needed
        needs_deep_analysis = (
            not safety_passed
            or risk_assessment["risk_level"] in [RiskLevel.HIGH, RiskLevel.EXTREMELY_HIGH]
            or tier_score.tier == 1  # Always validate Tier 1 deeply
        )

        # Stage 7: Gemini deep analysis (if needed)
        gemini_analysis = None
        if needs_deep_analysis:
            gemini_analysis = await self._gemini_deep_check(item, tier_score, validation_checks)
            validation_checks["gemini_deep_analysis"] = gemini_analysis["passed"]

            if not gemini_analysis["passed"]:
                failure_reasons.extend(gemini_analysis.get("reasons", []))

        # Stage 8: ShadowTagJR compliance
        jr_compliance = self._check_jr_compliance(item, validation_checks, risk_assessment)
        validation_checks["jr_compliant"] = jr_compliance["compliant"]

        # Calculate final confidence score
        confidence = self._calculate_confidence(validation_checks, tier_score, gemini_analysis)

        # Determine final status
        status = self._determine_status(validation_checks, confidence, risk_assessment)

        # Calculate latency
        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

        # Track metrics
        self._validation_count += 1
        self._total_latency_ms += latency_ms

        result = ValidationResult(
            item_id=item.id,
            status=status,
            risk_level=risk_assessment["risk_level"],
            confidence_score=confidence,
            validation_checks=validation_checks,
            failure_reasons=failure_reasons,
            latency_ms=round(latency_ms, 2),
            timestamp=datetime.utcnow(),
            severity=risk_assessment["severity"],
            probability=risk_assessment["probability"],
            risk_score=risk_assessment["risk_score"],
            jr_compliant=jr_compliance["compliant"],
            jr_reasoning=jr_compliance["reasoning"],
        )

        logger.info(
            "validation_completed",
            item_id=item.id,
            status=status.value,
            risk_level=risk_assessment["risk_level"].value,
            confidence=confidence,
            latency_ms=latency_ms,
        )

        return result

    async def _safety_screen(self, item: IngestedItem) -> dict[str, float]:
        """
        Fast PyTorch-based safety screening.

        Returns safety scores for 4 categories:
        - hate_speech: 0.0-1.0 (1.0 = safe)
        - violence: 0.0-1.0 (1.0 = safe)
        - misinformation: 0.0-1.0 (1.0 = safe)
        - spam: 0.0-1.0 (1.0 = safe)
        """
        # TODO: Implement actual embedding + model inference
        # For now, use simple heuristics

        content = f"{item.title} {item.content or ''}".lower()

        # Simple keyword-based checks (replace with actual model)
        hate_keywords = ["hate", "racist", "offensive"]
        violence_keywords = ["kill", "attack", "violence"]
        misinfo_keywords = ["fake", "hoax", "conspiracy"]
        spam_keywords = ["click here", "buy now", "limited offer"]

        def check_safety(keywords):
            count = sum(1 for kw in keywords if kw in content)
            return max(0.5, 1.0 - (count * 0.2))  # Decrease score per keyword

        return {
            "hate_speech": check_safety(hate_keywords),
            "violence": check_safety(violence_keywords),
            "misinformation": check_safety(misinfo_keywords),
            "spam": check_safety(spam_keywords),
        }

    def _validate_metadata(self, item: IngestedItem) -> bool:
        """Validate metadata fields are present and well-formed."""
        required_fields = [item.id, item.source, item.title, item.url, item.published_at]

        return all(field is not None for field in required_fields)

    def _check_completeness(self, item: IngestedItem) -> float:
        """Calculate completeness score (0.0-1.0)."""
        fields = [
            item.id,
            item.source,
            item.title,
            item.content,
            item.url,
            item.published_at,
            item.author,
            item.metadata,
        ]

        return sum(1 for f in fields if f) / len(fields)

    def _check_source_credibility(self, item: IngestedItem) -> bool:
        """Check if source is credible."""
        # TODO: Implement source credibility database

        # For now, simple checks
        credible_domains = [
            "youtube.com",
            "twitter.com",
            "nytimes.com",
            "wsj.com",
            "reuters.com",
            "bloomberg.com",
            "techcrunch.com",
            "wired.com",
        ]

        return any(domain in item.url for domain in credible_domains)

    def _assess_risk(
        self, item: IngestedItem, tier_score: TierScore, validation_checks: dict[str, bool]
    ) -> dict:
        """
        ATP 5-19 Risk Assessment.

        Severity (1-5):
        1 = Negligible
        2 = Minor
        3 = Moderate
        4 = Critical
        5 = Catastrophic

        Probability (1-5):
        1 = Unlikely
        2 = Seldom
        3 = Occasional
        4 = Likely
        5 = Frequent

        Risk Score = Severity × Probability
        """
        # Calculate severity based on tier and validation failures
        severity = 1

        if tier_score.tier == 1:
            severity += 2  # Tier 1 items have higher impact

        failed_checks = sum(1 for passed in validation_checks.values() if not passed)
        severity += min(failed_checks, 2)

        severity = min(severity, 5)

        # Calculate probability based on source and historical data
        probability = 2  # Default: Seldom

        if not validation_checks.get("source_credible", True):
            probability += 1

        if not validation_checks.get("safety_screen", True):
            probability += 2

        probability = min(probability, 5)

        # Calculate risk score
        risk_score = severity * probability

        # Map risk score to risk level
        if risk_score >= 20:
            risk_level = RiskLevel.EXTREMELY_HIGH
        elif risk_score >= 12:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 6:
            risk_level = RiskLevel.MODERATE
        elif risk_score >= 2:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.EXTREMELY_LOW

        return {
            "severity": severity,
            "probability": probability,
            "risk_score": risk_score,
            "risk_level": risk_level,
        }

    async def _gemini_deep_check(
        self, item: IngestedItem, tier_score: TierScore, validation_checks: dict[str, bool]
    ) -> dict:
        """
        Gemini-powered deep content analysis.

        Used for high-risk or Tier 1 items requiring semantic understanding.
        """
        prompt = f"""You are a content validation expert for PNKLN intelligence platform.

Analyze this item for validity, safety, and credibility:

**Item:**
- Source: {item.source}
- Title: {item.title}
- Content: {item.content[:500] if item.content else "(No content)"}
- Author: {item.author or "(Unknown)"}
- URL: {item.url}

**Classification:**
- Tier: {tier_score.tier}
- Relevance: {tier_score.relevance:.2f}
- Source Authority: {tier_score.source_authority:.2f}

**Validation Checks:**
{validation_checks}

**Assess:**
1. Is this content safe and appropriate?
2. Is it credible and fact-based?
3. Does it align with PNKLN's intelligence mission?
4. Are there any red flags or concerns?

Respond in JSON:
{{
  "passed": true/false,
  "confidence": 0.0-1.0,
  "reasons": ["reason 1", "reason 2"],
  "recommendation": "approve" | "flag" | "reject"
}}"""

        try:
            response = self.gemini.messages.create(
                model=self.config.anthropic.model,
                max_tokens=1024,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}],
            )

            import json

            result_text = response.content[0].text
            start = result_text.find("{")
            end = result_text.rfind("}") + 1
            result = json.loads(result_text[start:end])

            return result

        except Exception as e:
            logger.error("gemini_deep_check_failed", error=str(e))
            return {
                "passed": False,
                "confidence": 0.0,
                "reasons": [f"Gemini analysis error: {str(e)}"],
                "recommendation": "flag",
            }

    def _check_jr_compliance(
        self, item: IngestedItem, validation_checks: dict[str, bool], risk_assessment: dict
    ) -> dict:
        """
        ShadowTagJR (Judgment Rule) compliance check.

        Ensures validation decisions are:
        - Informed: Based on sufficient data
        - Reasonable: Aligned with policy
        - Good Faith: No bias or malicious intent
        """
        # Informed: Do we have enough data?
        informed = validation_checks.get("metadata_valid", False) and validation_checks.get(
            "completeness", False
        )

        # Reasonable: Does risk assessment make sense?
        reasonable = risk_assessment["risk_score"] <= 25  # Not absurdly high

        # Good Faith: Are we applying rules consistently?
        good_faith = len(validation_checks) >= 4  # Multiple checks performed

        compliant = informed and reasonable and good_faith

        reasoning = []
        if not informed:
            reasoning.append("Insufficient data for informed decision")
        if not reasonable:
            reasoning.append("Risk assessment appears unreasonable")
        if not good_faith:
            reasoning.append("Validation process incomplete")

        return {
            "compliant": compliant,
            "reasoning": "; ".join(reasoning) if reasoning else "Compliant with JR doctrine",
        }

    def _calculate_confidence(
        self,
        validation_checks: dict[str, bool],
        tier_score: TierScore,
        gemini_analysis: dict | None,
    ) -> float:
        """Calculate overall validation confidence (0.0-1.0)."""
        # Base confidence from validation checks
        passed_checks = sum(1 for passed in validation_checks.values() if passed)
        total_checks = len(validation_checks)
        base_confidence = passed_checks / total_checks if total_checks > 0 else 0.0

        # Adjust for tier score quality
        tier_confidence = tier_score.overall

        # Adjust for Gemini analysis if available
        gemini_confidence = gemini_analysis.get("confidence", 0.5) if gemini_analysis else 0.5

        # Weighted average
        confidence = base_confidence * 0.4 + tier_confidence * 0.3 + gemini_confidence * 0.3

        return round(confidence, 3)

    def _determine_status(
        self, validation_checks: dict[str, bool], confidence: float, risk_assessment: dict
    ) -> ValidationStatus:
        """Determine final validation status."""
        # Hard blocks
        if not validation_checks.get("safety_screen", True):
            return ValidationStatus.BLOCKED

        if risk_assessment["risk_level"] == RiskLevel.EXTREMELY_HIGH:
            return ValidationStatus.BLOCKED

        # Flags for human review
        if risk_assessment["risk_level"] == RiskLevel.HIGH:
            return ValidationStatus.FLAGGED

        if confidence < 0.5:
            return ValidationStatus.FLAGGED

        # Failures
        if confidence < 0.7:
            return ValidationStatus.FAILED

        # Pass
        return ValidationStatus.PASSED

    def get_stats(self) -> dict:
        """Get Judge #6 performance statistics."""
        avg_latency = (
            self._total_latency_ms / self._validation_count if self._validation_count > 0 else 0.0
        )

        return {
            "total_validations": self._validation_count,
            "avg_latency_ms": round(avg_latency, 2),
            "p99_target_ms": 90,
            "within_target": avg_latency <= 90,
            "model": "hybrid_gemini_pytorch",
            "coverage_target_pct": 98,
        }
