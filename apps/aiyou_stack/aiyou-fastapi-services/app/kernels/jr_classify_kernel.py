# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""JR Classify Kernel - California AI Regulations
==============================================
Kernel 2 of NS-JR-Cor pipeline for California AI compliance.

Specifications:
- Input: NS scan output + policy rules
- Output: Binary go/no-go decision with risk tier
- Model: Policy rules (local) + optional Gemini for edge cases
- Latency target: <50ms p50

Based on Judge Six pattern from existing kernel chain.
"""

import logging

from app.kernels.base import Kernel, KernelChainError
from app.models.california_ai import (
    ComplianceAction,
    JRPolicyOutput,
    NSDetectionOutput,
    RiskTier,
    UserAgeCategory,
)
from app.models.kernel import KernelInput, KernelMetrics, KernelOutput
from app.services.jr_policy_engine import JRPolicyEngine, create_jr_engine

logger = logging.getLogger(__name__)


# =============================================================================
# Input Model
# =============================================================================


class JRClassifyInput:
    """Input for JR Classify Kernel"""

    def __init__(
        self,
        ns_output: NSDetectionOutput,
        user_age_category: UserAgeCategory = UserAgeCategory.UNKNOWN,
        session_duration_minutes: int = 0,
        is_conversation_start: bool = False,
        data_collection: bool = False,
        content_id: str | None = None,
    ):
        self.ns_output = ns_output
        self.user_age_category = user_age_category
        self.session_duration_minutes = session_duration_minutes
        self.is_conversation_start = is_conversation_start
        self.data_collection = data_collection
        self.content_id = content_id or ns_output.content_id


# =============================================================================
# JR Classify Kernel
# =============================================================================


class JRClassifyKernel(Kernel):
    """Kernel 2: JR (Judgment Rule) Policy Classification.

    Takes NS detection output and applies policy rules to:
    - Generate binary go/no-go decision
    - Assign risk tier (1-5)
    - Determine required compliance actions
    - Flag for human review if needed
    """

    def __init__(
        self,
        jr_engine: JRPolicyEngine | None = None,
        max_latency_ms: float = 50.0,
    ):
        super().__init__(name="JRClassifyKernel", max_latency_ms=max_latency_ms)
        self.jr_engine = jr_engine or create_jr_engine()

    async def execute(self, kernel_input: KernelInput) -> KernelOutput:
        """Execute JR classification.

        Args:
            kernel_input: Contains JRClassifyInput or NS output dict

        Returns:
            KernelOutput with JRPolicyOutput

        """
        try:
            # Extract input
            if isinstance(kernel_input.data, JRClassifyInput):
                jr_input = kernel_input.data
            elif isinstance(kernel_input.data, dict):
                # Reconstruct from dict
                ns_output = NSDetectionOutput(**kernel_input.data.get("ns_output", {}))
                jr_input = JRClassifyInput(
                    ns_output=ns_output,
                    user_age_category=UserAgeCategory(
                        kernel_input.data.get("user_age_category", "unknown"),
                    ),
                    session_duration_minutes=kernel_input.data.get("session_duration_minutes", 0),
                    is_conversation_start=kernel_input.data.get("is_conversation_start", False),
                    data_collection=kernel_input.data.get("data_collection", False),
                    content_id=kernel_input.data.get("content_id"),
                )
            elif isinstance(kernel_input.data, NSDetectionOutput):
                # Just NS output, use defaults
                jr_input = JRClassifyInput(ns_output=kernel_input.data)
            else:
                raise KernelChainError(
                    f"Invalid input type: expected JRClassifyInput, dict, or NSDetectionOutput, "
                    f"got {type(kernel_input.data)}",
                )

            # Run policy evaluation
            policy_output = await self.jr_engine.evaluate(
                content_id=jr_input.content_id,
                ns_output=jr_input.ns_output,
                user_age=jr_input.user_age_category,
                session_duration_minutes=jr_input.session_duration_minutes,
                is_conversation_start=jr_input.is_conversation_start,
                data_collection=jr_input.data_collection,
            )

            # Calculate approximate token/cost
            # JR is mostly local rules, minimal token usage
            cost = 0.0001  # Minimal cost for local processing

            return KernelOutput(
                data=policy_output,
                kernel_name=self.name,
                success=True,
                metrics=KernelMetrics(
                    latency_ms=policy_output.processing_time_ms,
                    token_count_input=0,  # Local processing
                    token_count_output=0,
                    cost_usd=cost,
                ),
            )

        except Exception as e:
            raise KernelChainError(f"JR classification failed: {e!s}") from e


# =============================================================================
# Fast Path Classifier
# =============================================================================


class FastPathClassifier:
    """Fast-path classifier for common cases.

    Bypasses full kernel chain for:
    - Clean content (no signals)
    - Critical signals (immediate block)
    - Cached decisions
    """

    @staticmethod
    def classify(ns_output: NSDetectionOutput, user_age: UserAgeCategory) -> JRPolicyOutput | None:
        """Try fast-path classification.

        Returns:
            JRPolicyOutput if fast path applies, None otherwise

        """
        import time

        start = time.time()

        # Fast path 1: No signals detected
        if (
            not ns_output.self_harm_signals
            and not ns_output.explicit_content_signals
            and not ns_output.medical_claim_signals
            and not ns_output.signals
            and ns_output.overall_risk_score < 0.1
        ):
            processing_time = (time.time() - start) * 1000
            return JRPolicyOutput(
                content_id=ns_output.content_id,
                user_age_category=user_age,
                evaluations=[],
                all_violations=[],
                go_decision=True,
                risk_tier=RiskTier.TIER_1_MINIMAL,
                required_actions=[ComplianceAction.PASS],
                human_review_required=False,
                confidence=1.0,
                reasoning="Fast path: No risk signals detected",
                processing_time_ms=processing_time,
            )

        # Fast path 2: Critical self-harm signals
        if ns_output.self_harm_signals:
            max_confidence = max(s.confidence for s in ns_output.self_harm_signals)
            if max_confidence > 0.9:
                processing_time = (time.time() - start) * 1000
                return JRPolicyOutput(
                    content_id=ns_output.content_id,
                    user_age_category=user_age,
                    evaluations=[],
                    all_violations=[],  # Will be populated by orchestrator
                    go_decision=False,  # Critical signal
                    risk_tier=RiskTier.TIER_5_CRITICAL,
                    required_actions=[ComplianceAction.RESPOND_WITH_RESOURCES],
                    human_review_required=True,
                    confidence=max_confidence,
                    reasoning="Fast path: Critical self-harm signal detected",
                    processing_time_ms=processing_time,
                )

        # Fast path 3: Critical explicit content for minors
        if (
            user_age in [UserAgeCategory.UNDER_13, UserAgeCategory.TEEN_13_17]
            and ns_output.explicit_content_signals
        ):
            max_confidence = max(s.confidence for s in ns_output.explicit_content_signals)
            if max_confidence > 0.9:
                processing_time = (time.time() - start) * 1000
                return JRPolicyOutput(
                    content_id=ns_output.content_id,
                    user_age_category=user_age,
                    evaluations=[],
                    all_violations=[],
                    go_decision=False,  # Block for minors
                    risk_tier=RiskTier.TIER_5_CRITICAL,
                    required_actions=[ComplianceAction.BLOCK],
                    human_review_required=False,
                    confidence=max_confidence,
                    reasoning="Fast path: Explicit content blocked for minor",
                    processing_time_ms=processing_time,
                )

        # No fast path available
        return None


# =============================================================================
# Enhanced JR Kernel with Fast Path
# =============================================================================


class EnhancedJRClassifyKernel(JRClassifyKernel):
    """JR Classify Kernel with fast-path optimization"""

    def __init__(
        self,
        jr_engine: JRPolicyEngine | None = None,
        max_latency_ms: float = 50.0,
        enable_fast_path: bool = True,
    ):
        super().__init__(jr_engine=jr_engine, max_latency_ms=max_latency_ms)
        self.enable_fast_path = enable_fast_path
        self.fast_classifier = FastPathClassifier()

        # Stats
        self._fast_path_hits = 0
        self._total_requests = 0

    async def execute(self, kernel_input: KernelInput) -> KernelOutput:
        """Execute with fast-path optimization"""
        self._total_requests += 1

        if self.enable_fast_path:
            # Try fast path first
            if isinstance(kernel_input.data, JRClassifyInput):
                jr_input = kernel_input.data
            elif isinstance(kernel_input.data, NSDetectionOutput):
                jr_input = JRClassifyInput(ns_output=kernel_input.data)
            else:
                jr_input = None

            if jr_input:
                fast_result = self.fast_classifier.classify(
                    jr_input.ns_output,
                    jr_input.user_age_category,
                )

                if fast_result:
                    self._fast_path_hits += 1
                    return KernelOutput(
                        data=fast_result,
                        kernel_name=self.name,
                        success=True,
                        metrics=KernelMetrics(
                            latency_ms=fast_result.processing_time_ms,
                            token_count_input=0,
                            token_count_output=0,
                            cost_usd=0.00001,
                        ),
                    )

        # Fall back to full evaluation
        return await super().execute(kernel_input)

    def get_fast_path_rate(self) -> float:
        """Get fast path hit rate"""
        if self._total_requests == 0:
            return 0.0
        return self._fast_path_hits / self._total_requests


# =============================================================================
# Factory Functions
# =============================================================================


def create_jr_classify_kernel(
    strict_mode: bool = True,
    enable_fast_path: bool = True,
    max_latency_ms: float = 50.0,
) -> JRClassifyKernel:
    """Create JR Classify Kernel instance"""
    jr_engine = create_jr_engine(strict_mode=strict_mode)

    if enable_fast_path:
        return EnhancedJRClassifyKernel(
            jr_engine=jr_engine,
            max_latency_ms=max_latency_ms,
            enable_fast_path=True,
        )

    return JRClassifyKernel(
        jr_engine=jr_engine,
        max_latency_ms=max_latency_ms,
    )
