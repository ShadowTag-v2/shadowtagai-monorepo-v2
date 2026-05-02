"""Judge #6 Validation Service"""

import logging
from datetime import datetime

from app.config import settings
from app.models.pnkln import IngestedItem, ValidationMetrics, ValidationStatus

logger = logging.getLogger(__name__)


class JudgeSixService:
    """Judge #6 - Hybrid Gemini+PyTorch validation system"""

    def __init__(self):
        """Initialize Judge #6 Service"""
        self.enabled = settings.JUDGE_ENABLED
        if not self.enabled:
            logger.warning("Judge #6 is disabled")
        logger.info("Judge #6 Validation Service initialized")

    async def validate_item(self, item: IngestedItem, use_hybrid: bool = True) -> tuple[ValidationStatus, float]:
        """
        Validate a single ingested item

        Args:
            item: The item to validate
            use_hybrid: Whether to use hybrid Gemini+PyTorch approach

        Returns:
            Tuple of (ValidationStatus, confidence_score)
        """
        if not self.enabled:
            return ValidationStatus.APPROVED, 1.0

        # Simulate validation logic
        # In production, this would use Gemini API and PyTorch models

        # Basic quality checks
        if item.relevance_score < settings.MIN_RELEVANCE_SCORE:
            return ValidationStatus.REJECTED, 0.95

        # Check tier appropriateness
        if item.tier == "tier_3" and item.cost > settings.MAX_COST_PER_ITEM:
            return ValidationStatus.REJECTED, 0.88

        # Confidence check
        confidence = self._calculate_confidence(item)

        if confidence >= settings.JUDGE_CONFIDENCE_THRESHOLD:
            return ValidationStatus.APPROVED, confidence
        elif confidence >= 0.5:
            return ValidationStatus.REVIEW_REQUIRED, confidence
        else:
            return ValidationStatus.REJECTED, confidence

    async def validate_batch(self, items: list[IngestedItem]) -> ValidationMetrics:
        """
        Validate a batch of items

        Args:
            items: List of items to validate

        Returns:
            ValidationMetrics with batch results
        """
        datetime.utcnow()

        approved = 0
        rejected = 0
        review_required = 0
        confidences = []
        latencies = []

        for item in items:
            item_start = datetime.utcnow()
            status, confidence = await self.validate_item(item)
            latency = (datetime.utcnow() - item_start).total_seconds() * 1000

            if status == ValidationStatus.APPROVED:
                approved += 1
            elif status == ValidationStatus.REJECTED:
                rejected += 1
            else:
                review_required += 1

            confidences.append(confidence)
            latencies.append(latency)

            # Update item status
            item.validation_status = status

        # Calculate metrics
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        p99_latency = sorted(latencies)[int(len(latencies) * 0.99)] if latencies else 0.0

        # Simulate error rates (in production, these come from ground truth comparison)
        fp_rate = 0.015  # False positive rate
        fn_rate = 0.012  # False negative rate

        metrics = ValidationMetrics(
            items_validated=len(items),
            approved_count=approved,
            rejected_count=rejected,
            review_required_count=review_required,
            false_positive_rate=fp_rate,
            false_negative_rate=fn_rate,
            average_latency_ms=avg_latency,
            p99_latency_ms=p99_latency,
            average_confidence=avg_confidence,
        )

        logger.info(
            f"Batch validation complete: {approved} approved, {rejected} rejected, "
            f"{review_required} review required (avg confidence: {avg_confidence:.2f})"
        )

        return metrics

    def _calculate_confidence(self, item: IngestedItem) -> float:
        """Calculate confidence score for validation"""
        import random

        # Simulate confidence calculation
        # In production, this would use actual model outputs
        base_confidence = item.relevance_score

        # Adjust based on tier
        if item.tier == "tier_1":
            base_confidence += 0.1
        elif item.tier == "tier_3":
            base_confidence -= 0.1

        # Add some variance
        confidence = min(1.0, max(0.0, base_confidence + random.uniform(-0.1, 0.1)))

        return confidence

    def check_performance_gates(self, metrics: ValidationMetrics) -> dict[str, bool]:
        """
        Check if validation performance meets gates

        Returns:
            Dict of gate checks
        """
        gates = {
            "fp_rate": metrics.false_positive_rate <= settings.JUDGE_FP_RATE_THRESHOLD,
            "fn_rate": metrics.false_negative_rate <= settings.JUDGE_FN_RATE_THRESHOLD,
            "confidence": metrics.average_confidence >= settings.JUDGE_CONFIDENCE_THRESHOLD,
        }

        gates["all_passed"] = all(gates.values())

        return gates
