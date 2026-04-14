"""NS Scan Kernel - California AI Regulations
==========================================
Kernel 1 of NS-JR-Cor pipeline for California AI compliance.

Specifications:
- Input: Raw message content + user context (up to 50KB)
- Output: Structured detection signals (~2-3KB)
- Model: Gemini Flash for advanced classification
- Latency target: <100ms p50

Based on ATP 5-19 Scan Kernel pattern.
"""

import json
import logging

from app.kernels.base import Kernel, KernelChainError
from app.models.california_ai import (
    NSDetectionOutput,
    UserAgeCategory,
)
from app.models.kernel import KernelInput, KernelMetrics, KernelOutput
from app.services.ns_detection_engine import NSDetectionEngine, create_ns_engine

logger = logging.getLogger(__name__)


# =============================================================================
# Input/Output Models
# =============================================================================


class NSScanInput:
    """Input for NS Scan Kernel"""

    def __init__(
        self,
        content: str,
        user_age_category: UserAgeCategory = UserAgeCategory.UNKNOWN,
        session_id: str | None = None,
        platform_id: str = "default",
        metadata: dict | None = None,
    ):
        self.content = content
        self.user_age_category = user_age_category
        self.session_id = session_id
        self.platform_id = platform_id
        self.metadata = metadata or {}


# =============================================================================
# NS Scan Kernel
# =============================================================================


class NSScanKernel(Kernel):
    """Kernel 1: NS (Neural System) Signal Detection.

    Scans content for California AI regulation triggers:
    - Self-harm indicators
    - Explicit content
    - Medical impersonation
    - Other risk signals

    Uses pattern matching + external APIs for detection.
    """

    SYSTEM_PROMPT = """You are a California AI Compliance Scanner. Your job is to detect risk signals in content.

DETECTION CATEGORIES:
- SELF_HARM: Suicidal ideation, self-harm statements, crisis indicators
- EXPLICIT: Sexual content, violence, harmful instructions
- MEDICAL: Medical professional impersonation, unauthorized medical advice
- MINOR_RISK: Content inappropriate for minors

OUTPUT FORMAT (JSON only):
{
  "signals": [
    {
      "category": "SELF_HARM|EXPLICIT|MEDICAL|MINOR_RISK",
      "confidence": 0.0-1.0,
      "evidence": "relevant excerpt",
      "severity": "low|medium|high|critical"
    }
  ],
  "overall_risk": 0.0-1.0,
  "crisis_response_needed": true|false
}

RULES:
1. Return ONLY valid JSON
2. Be conservative - flag uncertain cases for review
3. Self-harm detection is highest priority
4. Evidence should be short excerpts only
"""

    def __init__(
        self,
        ns_engine: NSDetectionEngine | None = None,
        max_latency_ms: float = 100.0,
    ):
        super().__init__(name="NSScanKernel", max_latency_ms=max_latency_ms)
        self.ns_engine = ns_engine or create_ns_engine()

    async def execute(self, kernel_input: KernelInput) -> KernelOutput:
        """Execute NS scan on content.

        Args:
            kernel_input: Contains NSScanInput or raw content string

        Returns:
            KernelOutput with NSDetectionOutput

        """
        try:
            # Extract input
            if isinstance(kernel_input.data, NSScanInput):
                content = kernel_input.data.content
                user_age = kernel_input.data.user_age_category
            elif isinstance(kernel_input.data, str):
                content = kernel_input.data
                user_age = UserAgeCategory.UNKNOWN
            elif isinstance(kernel_input.data, dict):
                content = kernel_input.data.get("content", "")
                user_age = UserAgeCategory(kernel_input.data.get("user_age_category", "unknown"))
            else:
                raise KernelChainError(
                    f"Invalid input type: expected NSScanInput, str, or dict, "
                    f"got {type(kernel_input.data)}",
                )

            # Run detection
            detection_output = await self.ns_engine.detect(content)

            # Adjust thresholds based on user age
            if user_age in [UserAgeCategory.UNDER_13, UserAgeCategory.TEEN_13_17]:
                # Lower thresholds for minors = more sensitive detection
                detection_output = self._adjust_for_minors(detection_output)

            # Calculate token counts (approximate)
            input_tokens = len(content.split())
            output_tokens = 100  # Estimated output size

            # Estimate cost
            cost = (input_tokens + output_tokens) / 1000 * 0.00001  # Flash pricing

            return KernelOutput(
                data=detection_output,
                kernel_name=self.name,
                success=True,
                metrics=KernelMetrics(
                    latency_ms=detection_output.processing_time_ms,
                    token_count_input=input_tokens,
                    token_count_output=output_tokens,
                    cost_usd=cost,
                ),
            )

        except Exception as e:
            raise KernelChainError(f"NS scan failed: {e!s}") from e

    def _adjust_for_minors(self, output: NSDetectionOutput) -> NSDetectionOutput:
        """Adjust detection output for minor users.
        Lowers confidence thresholds = more sensitive.
        """
        # Boost confidence scores for minors (more cautious)
        adjustment_factor = 1.2

        for signal in output.explicit_content_signals:
            signal.confidence = min(1.0, signal.confidence * adjustment_factor)

        for signal in output.self_harm_signals:
            # Self-harm signals always high priority regardless of age
            pass

        # Recalculate overall risk
        all_confidences = (
            [s.confidence for s in output.self_harm_signals]
            + [s.confidence for s in output.explicit_content_signals]
            + [s.confidence for s in output.medical_claim_signals]
            + [s.confidence for s in output.signals]
        )

        if all_confidences:
            output.overall_risk_score = max(all_confidences)

        return output


# =============================================================================
# Gemini-Enhanced NS Scan Kernel
# =============================================================================


class GeminiNSScanKernel(NSScanKernel):
    """NS Scan Kernel with Gemini Flash enhancement.

    Uses Gemini Flash for advanced classification when:
    - Pattern matching is inconclusive
    - Content is complex or ambiguous
    - Higher accuracy is needed
    """

    def __init__(
        self,
        ns_engine: NSDetectionEngine | None = None,
        gemini_api_key: str | None = None,
        max_latency_ms: float = 200.0,
    ):
        super().__init__(ns_engine=ns_engine, max_latency_ms=max_latency_ms)
        self.gemini_api_key = gemini_api_key
        self._gemini_model = None

        if gemini_api_key:
            self._init_gemini()

    def _init_gemini(self):
        """Initialize Gemini model"""
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.gemini_api_key)
            self._gemini_model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": 500,
                },
            )
        except ImportError:
            logger.warning("google-generativeai not installed, Gemini enhancement disabled")
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini: {e}")

    async def execute(self, kernel_input: KernelInput) -> KernelOutput:
        """Execute with optional Gemini enhancement"""
        # First run standard detection
        output = await super().execute(kernel_input)

        # Enhance with Gemini if:
        # 1. Gemini is available
        # 2. Risk score is in ambiguous range (0.3-0.7)
        # 3. No critical signals detected
        detection_output: NSDetectionOutput = output.data

        if (
            self._gemini_model
            and 0.3 < detection_output.overall_risk_score < 0.7
            and not detection_output.has_critical_signals
        ):
            enhanced = await self._gemini_classify(kernel_input.data)
            if enhanced:
                # Merge Gemini results
                detection_output.signals.extend(enhanced.get("signals", []))
                if enhanced.get("overall_risk", 0) > detection_output.overall_risk_score:
                    detection_output.overall_risk_score = enhanced["overall_risk"]

        return output

    async def _gemini_classify(self, content) -> dict | None:
        """Use Gemini for additional classification"""
        if not self._gemini_model:
            return None

        try:
            text = content if isinstance(content, str) else content.content

            prompt = f"""Analyze this content for California AI compliance risks.

Content:
{text[:2000]}

{self.SYSTEM_PROMPT}"""

            response = self._gemini_model.generate_content(prompt)
            response_text = response.text.strip()

            # Parse JSON
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])

            return json.loads(response_text)

        except Exception as e:
            logger.warning(f"Gemini classification failed: {e}")
            return None


# =============================================================================
# Factory Functions
# =============================================================================


def create_ns_scan_kernel(
    gemini_api_key: str | None = None,
    max_latency_ms: float = 100.0,
) -> NSScanKernel:
    """Create NS Scan Kernel instance"""
    if gemini_api_key:
        return GeminiNSScanKernel(gemini_api_key=gemini_api_key, max_latency_ms=max_latency_ms)
    return NSScanKernel(max_latency_ms=max_latency_ms)
