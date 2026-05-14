# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
JR Engine with 4-Layer Failover Architecture

This module implements the failover cascade for Judge #6 (JR) decisions:
    Layer 1: Gemini (primary, 40% allocation)
    Layer 2: Claude (backup, +10% capacity)
    Layer 3: GPT-5 (emergency, +5% capacity)
    Layer 4: Local PyTorch + Rules (deterministic, always available)

Target: p99≤90ms latency even during multi-provider outages
"""

import time
import logging
from typing import Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


# Configure structured logging for failover events
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ProviderType(Enum):
    """LLM Provider Types"""

    GEMINI = "gemini"
    CLAUDE = "claude"
    GPT5 = "gpt5"
    LOCAL = "local"


class FailoverReason(Enum):
    """Reasons for failover to next layer"""

    TIMEOUT = "timeout"
    API_ERROR = "api_error"
    RATE_LIMIT = "rate_limit"
    QUALITY_CHECK_FAILED = "quality_check_failed"
    PROVIDER_UNAVAILABLE = "provider_unavailable"


@dataclass
class FailoverEvent:
    """Structured logging for failover events"""

    timestamp: datetime
    from_provider: ProviderType
    to_provider: ProviderType
    reason: FailoverReason
    latency_ms: float
    error_message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "from_provider": self.from_provider.value,
            "to_provider": self.to_provider.value,
            "reason": self.reason.value,
            "latency_ms": self.latency_ms,
            "error_message": self.error_message,
        }


@dataclass
class JudgeDecision:
    """Standardized decision format across all providers"""

    decision: str  # "approve", "reject", "escalate"
    confidence: float  # 0.0-1.0
    reasoning: str
    provider_used: ProviderType
    latency_ms: float
    fallback_chain: list[ProviderType]  # Providers attempted before success
    is_degraded_mode: bool = False  # True if local-only fallback used


class TimeoutError(Exception):
    """Raised when provider exceeds timeout threshold"""

    pass


class APIError(Exception):
    """Raised when provider API returns error"""

    pass


class JREngineWithFailover:
    """
    Judge #6 (JR) Engine with automatic 4-layer failover.

    This class ensures p99≤90ms SLA by cascading through multiple
    LLM providers and ultimately falling back to deterministic local
    inference when all commercial APIs fail.
    """

    def __init__(
        self,
        gemini_timeout_ms: int = 70,
        claude_timeout_ms: int = 75,
        gpt5_timeout_ms: int = 85,
        coordination_buffer_ms: int = 5,
        enable_metrics: bool = True,
    ):
        """
        Initialize JR Engine with failover configuration.

        Args:
            gemini_timeout_ms: Max latency for Gemini before failover (default: 70ms)
            claude_timeout_ms: Max latency for Claude before failover (default: 75ms)
            gpt5_timeout_ms: Max latency for GPT-5 before failover (default: 85ms)
            coordination_buffer_ms: Overhead for failover logic (default: 5ms)
            enable_metrics: Whether to emit Prometheus metrics (default: True)
        """
        self.gemini_timeout = gemini_timeout_ms / 1000  # Convert to seconds
        self.claude_timeout = claude_timeout_ms / 1000
        self.gpt5_timeout = gpt5_timeout_ms / 1000
        self.coordination_buffer = coordination_buffer_ms / 1000
        self.enable_metrics = enable_metrics

        self.failover_events: list[FailoverEvent] = []

        # TODO: Initialize actual API clients here
        # self.gemini_client = GeminiClient(api_key=os.getenv("GEMINI_API_KEY"))
        # self.claude_client = AnthropicClient(api_key=os.getenv("ANTHROPIC_API_KEY"))
        # self.gpt5_client = OpenAIClient(api_key=os.getenv("OPENAI_API_KEY"))
        # self.local_model = LocalPyTorchModel(model_path="models/judge6_local.pt")

        logger.info(
            f"JREngineWithFailover initialized: "
            f"Gemini={gemini_timeout_ms}ms, "
            f"Claude={claude_timeout_ms}ms, "
            f"GPT-5={gpt5_timeout_ms}ms, "
            f"Buffer={coordination_buffer_ms}ms"
        )

    def execute_decision(self, context: dict[str, Any]) -> JudgeDecision:
        """
        Execute Judge #6 decision with automatic failover.

        This is the main entry point. It attempts each layer in sequence:
        1. Gemini (primary)
        2. Claude (backup)
        3. GPT-5 (emergency)
        4. Local PyTorch (guaranteed success)

        Args:
            context: Decision context (user request, history, policies, etc.)

        Returns:
            JudgeDecision with provider used and latency metrics

        Raises:
            Never raises - always returns a decision (local fallback guarantees success)
        """
        start_time = time.time()
        fallback_chain: list[ProviderType] = []

        # LAYER 1: Gemini (target: <60ms p99)
        try:
            decision = self._gemini_judge(context, timeout=self.gemini_timeout)
            if self._check_time_budget(start_time, 0.085):  # 85ms buffer
                decision.fallback_chain = fallback_chain
                self._emit_metrics(decision)
                return decision
            else:
                # Gemini succeeded but too slow - try faster fallback
                fallback_chain.append(ProviderType.GEMINI)
                self._log_failover(
                    ProviderType.GEMINI,
                    ProviderType.CLAUDE,
                    FailoverReason.TIMEOUT,
                    (time.time() - start_time) * 1000,
                    "Gemini response exceeded time budget",
                )
        except (TimeoutError, APIError) as e:
            fallback_chain.append(ProviderType.GEMINI)
            self._log_failover(
                ProviderType.GEMINI,
                ProviderType.CLAUDE,
                FailoverReason.API_ERROR if isinstance(e, APIError) else FailoverReason.TIMEOUT,
                (time.time() - start_time) * 1000,
                str(e),
            )

        # LAYER 2: Claude (target: <70ms p99)
        try:
            decision = self._claude_judge(context, timeout=self.claude_timeout)
            if self._check_time_budget(start_time, 0.090):  # 90ms budget
                decision.fallback_chain = fallback_chain
                self._emit_metrics(decision)
                return decision
            else:
                fallback_chain.append(ProviderType.CLAUDE)
                self._log_failover(
                    ProviderType.CLAUDE,
                    ProviderType.GPT5,
                    FailoverReason.TIMEOUT,
                    (time.time() - start_time) * 1000,
                    "Claude response exceeded time budget",
                )
        except (TimeoutError, APIError) as e:
            fallback_chain.append(ProviderType.CLAUDE)
            self._log_failover(
                ProviderType.CLAUDE,
                ProviderType.GPT5,
                FailoverReason.API_ERROR if isinstance(e, APIError) else FailoverReason.TIMEOUT,
                (time.time() - start_time) * 1000,
                str(e),
            )

        # LAYER 3: GPT-5 (target: <80ms p99)
        try:
            decision = self._gpt5_judge(context, timeout=self.gpt5_timeout)
            if self._check_time_budget(start_time, 0.090):  # 90ms budget
                decision.fallback_chain = fallback_chain
                self._emit_metrics(decision)
                return decision
            else:
                fallback_chain.append(ProviderType.GPT5)
                self._log_failover(
                    ProviderType.GPT5,
                    ProviderType.LOCAL,
                    FailoverReason.TIMEOUT,
                    (time.time() - start_time) * 1000,
                    "GPT-5 response exceeded time budget",
                )
        except (TimeoutError, APIError) as e:
            fallback_chain.append(ProviderType.GPT5)
            self._log_failover(
                ProviderType.GPT5,
                ProviderType.LOCAL,
                FailoverReason.API_ERROR if isinstance(e, APIError) else FailoverReason.TIMEOUT,
                (time.time() - start_time) * 1000,
                str(e),
            )

        # LAYER 4: Local PyTorch + Rules (ALWAYS succeeds)
        # Target: <10ms p99 (no network calls)
        decision = self._local_judge(context)
        decision.fallback_chain = fallback_chain
        decision.is_degraded_mode = True
        self._emit_metrics(decision)

        logger.warning(
            f"All commercial APIs failed - using local fallback. "
            f"Total latency: {decision.latency_ms:.2f}ms. "
            f"Fallback chain: {[p.value for p in fallback_chain]}"
        )

        return decision

    def _gemini_judge(self, context: dict[str, Any], timeout: float) -> JudgeDecision:
        """
        Execute decision using Gemini API.

        Args:
            context: Decision context
            timeout: Max execution time in seconds

        Returns:
            JudgeDecision from Gemini

        Raises:
            TimeoutError: If execution exceeds timeout
            APIError: If Gemini API returns error
        """
        start = time.time()

        # TODO: Replace with actual Gemini API call
        # result = self.gemini_client.judge(
        #     prompt=self._format_judge_prompt(context),
        #     timeout=timeout
        # )

        # MOCK IMPLEMENTATION (replace with real API)
        time.sleep(0.055)  # Simulate 55ms API call
        if context.get("simulate_gemini_failure"):
            raise APIError("Gemini API returned 503 Service Unavailable")

        latency_ms = (time.time() - start) * 1000

        return JudgeDecision(
            decision="approve",
            confidence=0.92,
            reasoning="Request meets policy requirements (Gemini analysis)",
            provider_used=ProviderType.GEMINI,
            latency_ms=latency_ms,
            fallback_chain=[],
        )

    def _claude_judge(self, context: dict[str, Any], timeout: float) -> JudgeDecision:
        """Execute decision using Claude API (backup layer)"""
        start = time.time()

        # TODO: Replace with actual Claude API call
        # result = self.claude_client.judge(
        #     prompt=self._format_judge_prompt(context),
        #     timeout=timeout
        # )

        # MOCK IMPLEMENTATION
        time.sleep(0.060)  # Simulate 60ms API call
        if context.get("simulate_claude_failure"):
            raise APIError("Claude API timeout")

        latency_ms = (time.time() - start) * 1000

        return JudgeDecision(
            decision="approve",
            confidence=0.89,
            reasoning="Request meets policy requirements (Claude analysis)",
            provider_used=ProviderType.CLAUDE,
            latency_ms=latency_ms,
            fallback_chain=[],
        )

    def _gpt5_judge(self, context: dict[str, Any], timeout: float) -> JudgeDecision:
        """Execute decision using GPT-5 API (emergency layer)"""
        start = time.time()

        # TODO: Replace with actual GPT-5 API call
        # result = self.gpt5_client.judge(
        #     prompt=self._format_judge_prompt(context),
        #     timeout=timeout
        # )

        # MOCK IMPLEMENTATION
        time.sleep(0.065)  # Simulate 65ms API call
        if context.get("simulate_gpt5_failure"):
            raise APIError("GPT-5 API rate limit exceeded")

        latency_ms = (time.time() - start) * 1000

        return JudgeDecision(
            decision="approve",
            confidence=0.87,
            reasoning="Request meets policy requirements (GPT-5 analysis)",
            provider_used=ProviderType.GPT5,
            latency_ms=latency_ms,
            fallback_chain=[],
        )

    def _local_judge(self, context: dict[str, Any]) -> JudgeDecision:
        """
        Execute decision using local PyTorch model + rule engine.

        This is the deterministic fallback that ALWAYS succeeds.
        Target: <10ms p99 (no network calls).

        Args:
            context: Decision context

        Returns:
            JudgeDecision from local inference (never raises exception)
        """
        start = time.time()

        # TODO: Replace with actual PyTorch inference
        # embeddings = self.local_model.encode(context)
        # logits = self.local_model.forward(embeddings)
        # decision = self._apply_rules(logits, context)

        # MOCK IMPLEMENTATION (deterministic rules)
        time.sleep(0.005)  # Simulate 5ms local inference

        # Simple rule-based logic (replace with actual model)
        if "forbidden_keyword" in context.get("user_request", "").lower():
            decision = "reject"
            confidence = 0.95
            reasoning = "Request contains forbidden content (rule-based)"
        else:
            decision = "approve"
            confidence = 0.75  # Lower confidence for local fallback
            reasoning = "Request meets basic policy requirements (local inference)"

        latency_ms = (time.time() - start) * 1000

        return JudgeDecision(
            decision=decision,
            confidence=confidence,
            reasoning=reasoning + " [DEGRADED MODE: Commercial APIs unavailable]",
            provider_used=ProviderType.LOCAL,
            latency_ms=latency_ms,
            fallback_chain=[],
        )

    def _check_time_budget(self, start_time: float, budget_seconds: float) -> bool:
        """Check if we're still within time budget for SLA"""
        elapsed = time.time() - start_time
        return elapsed < budget_seconds

    def _log_failover(
        self, from_provider: ProviderType, to_provider: ProviderType, reason: FailoverReason, latency_ms: float, error_message: str | None = None
    ):
        """Log failover event for monitoring and SLA tracking"""
        event = FailoverEvent(
            timestamp=datetime.now(),
            from_provider=from_provider,
            to_provider=to_provider,
            reason=reason,
            latency_ms=latency_ms,
            error_message=error_message,
        )
        self.failover_events.append(event)

        logger.warning(f"FAILOVER: {from_provider.value} -> {to_provider.value} (reason: {reason.value}, latency: {latency_ms:.2f}ms)")

        # TODO: Emit to monitoring system (Datadog, Prometheus, etc.)
        # if self.enable_metrics:
        #     metrics.increment(
        #         "jr_engine.failover",
        #         tags={
        #             "from": from_provider.value,
        #             "to": to_provider.value,
        #             "reason": reason.value
        #         }
        #     )

    def _emit_metrics(self, decision: JudgeDecision):
        """Emit metrics for SLA monitoring"""
        if not self.enable_metrics:
            return

        # TODO: Emit to monitoring system
        # metrics.histogram(
        #     "jr_engine.latency_ms",
        #     decision.latency_ms,
        #     tags={
        #         "provider": decision.provider_used.value,
        #         "degraded": decision.is_degraded_mode
        #     }
        # )
        # metrics.increment(
        #     "jr_engine.decisions",
        #     tags={
        #         "provider": decision.provider_used.value,
        #         "decision": decision.decision
        #     }
        # )

        logger.info(
            f"DECISION: {decision.decision} "
            f"(provider: {decision.provider_used.value}, "
            f"latency: {decision.latency_ms:.2f}ms, "
            f"confidence: {decision.confidence:.2f}, "
            f"fallback_chain: {[p.value for p in decision.fallback_chain]})"
        )

    def get_failover_stats(self) -> dict[str, Any]:
        """Get statistics on failover events for SLA reporting"""
        if not self.failover_events:
            return {"total_failovers": 0, "failovers_by_provider": {}, "failovers_by_reason": {}}

        failovers_by_provider = {}
        failovers_by_reason = {}

        for event in self.failover_events:
            # Count by source provider
            provider = event.from_provider.value
            failovers_by_provider[provider] = failovers_by_provider.get(provider, 0) + 1

            # Count by reason
            reason = event.reason.value
            failovers_by_reason[reason] = failovers_by_reason.get(reason, 0) + 1

        return {
            "total_failovers": len(self.failover_events),
            "failovers_by_provider": failovers_by_provider,
            "failovers_by_reason": failovers_by_reason,
            "most_recent_failover": self.failover_events[-1].to_dict() if self.failover_events else None,
        }


# Example usage
if __name__ == "__main__":
    # Initialize engine
    engine = JREngineWithFailover()

    # Example 1: Normal operation (Gemini succeeds)
    print("\n=== Example 1: Normal Operation ===")
    context = {"user_request": "Deploy new feature to production", "user_id": "user_123", "policies": ["require_approval", "security_scan"]}
    decision = engine.execute_decision(context)
    print(f"Decision: {decision.decision}")
    print(f"Provider: {decision.provider_used.value}")
    print(f"Latency: {decision.latency_ms:.2f}ms")
    print(f"Confidence: {decision.confidence:.2f}")

    # Example 2: Gemini fails, Claude succeeds
    print("\n=== Example 2: Gemini Fails, Claude Succeeds ===")
    context = {"user_request": "Deploy new feature to production", "simulate_gemini_failure": True}
    decision = engine.execute_decision(context)
    print(f"Decision: {decision.decision}")
    print(f"Provider: {decision.provider_used.value}")
    print(f"Latency: {decision.latency_ms:.2f}ms")
    print(f"Fallback chain: {[p.value for p in decision.fallback_chain]}")

    # Example 3: All commercial APIs fail, local fallback
    print("\n=== Example 3: All APIs Fail, Local Fallback ===")
    context = {
        "user_request": "Deploy new feature to production",
        "simulate_gemini_failure": True,
        "simulate_claude_failure": True,
        "simulate_gpt5_failure": True,
    }
    decision = engine.execute_decision(context)
    print(f"Decision: {decision.decision}")
    print(f"Provider: {decision.provider_used.value}")
    print(f"Latency: {decision.latency_ms:.2f}ms")
    print(f"Degraded mode: {decision.is_degraded_mode}")
    print(f"Fallback chain: {[p.value for p in decision.fallback_chain]}")

    # Show failover statistics
    print("\n=== Failover Statistics ===")
    stats = engine.get_failover_stats()
    print(f"Total failovers: {stats['total_failovers']}")
    print(f"By provider: {stats['failovers_by_provider']}")
    print(f"By reason: {stats['failovers_by_reason']}")
