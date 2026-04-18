#!/usr/bin/env python3
"""Pnkln Judge #6 Hybrid Orchestrator - Vertex AI Integration
Purpose: Coordinate 3-layer governance enforcement with <90ms p99 latency SLA
Architecture:
  Layer 1: Fine-tuned Gemini (policy understanding)
  Layer 2: PyTorch (enforcement logic)
  Layer 3: Rules engine (deterministic gates)
"""

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, TypedDict

import vertexai
from prometheus_client import Counter, Gauge, Histogram, start_http_server
from vertexai.generative_models import GenerationConfig, GenerativeModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION
# ============================================================================


@dataclass
class Config:
    """Configuration for Judge #6 orchestrator"""

    project_id: str = os.getenv("GOOGLE_CLOUD_PROJECT", "pnkln-validation")
    location: str = os.getenv("VERTEX_AI_LOCATION", "us-central1")

    # Model configuration
    gemini_model: str = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-pro-002")
    gemini_tuned_model: str = os.getenv("GEMINI_TUNED_MODEL_NAME", "gemini-1.5-pro-002-tuned")

    # SLA configuration
    latency_sla_p99_ms: int = int(os.getenv("LATENCY_SLA_P99_MS", "90"))
    latency_sla_p95_ms: int = int(os.getenv("LATENCY_SLA_P95_MS", "60"))
    latency_sla_p50_ms: int = int(os.getenv("LATENCY_SLA_P50_MS", "30"))

    # Layer timeouts (ms)
    gemini_timeout_ms: int = int(os.getenv("LAYER_1_TIMEOUT_MS", "30"))
    pytorch_timeout_ms: int = int(os.getenv("LAYER_2_TIMEOUT_MS", "40"))
    rules_timeout_ms: int = int(os.getenv("LAYER_3_TIMEOUT_MS", "10"))

    # Circuit breaker
    circuit_breaker_threshold_ms: int = int(os.getenv("CIRCUIT_BREAKER_THRESHOLD_MS", "100"))
    circuit_breaker_fallback_mode: str = os.getenv("CIRCUIT_BREAKER_FALLBACK_MODE", "rules-only")
    circuit_breaker_recovery_time_sec: int = int(
        os.getenv("CIRCUIT_BREAKER_RECOVERY_TIME_SEC", "60"),
    )

    # Feature flags
    enable_layer_1: bool = os.getenv("ENABLE_LAYER_1_GEMINI", "true").lower() == "true"
    enable_layer_2: bool = os.getenv("ENABLE_LAYER_2_PYTORCH", "true").lower() == "true"
    enable_layer_3: bool = os.getenv("ENABLE_LAYER_3_RULES", "true").lower() == "true"

    # Metrics
    metrics_port: int = int(os.getenv("METRICS_PORT", "8080"))


# ============================================================================
# PROMETHEUS METRICS
# ============================================================================

# Request metrics
request_total = Counter(
    "judge_request_total",
    "Total number of judge requests",
    ["layer", "status"],
)

request_errors = Counter(
    "judge_request_errors_total",
    "Total number of judge request errors",
    ["layer", "error_type"],
)

request_duration = Histogram(
    "judge_request_duration_seconds",
    "Judge request duration in seconds",
    ["layer"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0],
)

layer_duration = Histogram(
    "judge_layer_duration_seconds",
    "Individual layer duration in seconds",
    ["layer"],
    buckets=[0.001, 0.005, 0.01, 0.02, 0.03, 0.04, 0.05, 0.1],
)

circuit_breaker_trips = Counter(
    "judge_circuit_breaker_trips_total",
    "Total circuit breaker trips",
    ["layer"],
)

active_requests = Gauge("judge_active_requests", "Number of active judge requests")


# ============================================================================
# DATA MODELS
# ============================================================================


class Decision(StrEnum):
    """Judge decision types"""

    APPROVE = "APPROVE"
    DENY = "DENY"
    PENDING = "PENDING"
    ERROR = "ERROR"


class JudgeState(TypedDict):
    """State passed through the judge pipeline"""

    request_id: str
    request: dict[str, Any]

    # Layer 1: Gemini
    gemini_decision: Decision | None
    gemini_confidence: float | None
    gemini_reasoning: str | None
    gemini_timeout: bool
    gemini_duration_ms: float | None

    # Layer 2: PyTorch
    pytorch_score: float | None
    pytorch_features: dict[str, Any] | None
    pytorch_timeout: bool
    pytorch_duration_ms: float | None

    # Layer 3: Rules
    rules_verdict: bool | None
    rules_matched: list | None
    rules_timeout: bool
    rules_duration_ms: float | None

    # Final decision
    final_action: Decision | None
    final_reasoning: str | None
    total_duration_ms: float | None


# ============================================================================
# CIRCUIT BREAKER
# ============================================================================


@dataclass
class CircuitBreaker:
    """Circuit breaker for layer timeouts"""

    threshold_ms: int
    recovery_time_sec: int
    _trips: int = field(default=0, init=False)
    _last_trip_time: float = field(default=0.0, init=False)
    _is_open: bool = field(default=False, init=False)

    def record_call(self, duration_ms: float, layer: str) -> bool:
        """Record a call and return whether circuit is open"""
        if duration_ms > self.threshold_ms:
            self._trips += 1
            self._last_trip_time = time.time()
            self._is_open = True
            circuit_breaker_trips.labels(layer=layer).inc()
            logger.warning(
                f"Circuit breaker tripped for {layer}: {duration_ms}ms > {self.threshold_ms}ms",
            )
            return True

        # Check if we should close the circuit
        if self._is_open and (time.time() - self._last_trip_time) > self.recovery_time_sec:
            self._is_open = False
            logger.info(f"Circuit breaker closed for {layer} after recovery period")

        return self._is_open

    def is_open(self) -> bool:
        """Check if circuit is currently open"""
        if self._is_open and (time.time() - self._last_trip_time) > self.recovery_time_sec:
            self._is_open = False
        return self._is_open


# ============================================================================
# LAYER IMPLEMENTATIONS
# ============================================================================


class Layer1Gemini:
    """Layer 1: Fine-tuned Gemini for policy understanding"""

    def __init__(self, config: Config):
        self.config = config
        self.circuit_breaker = CircuitBreaker(
            threshold_ms=config.circuit_breaker_threshold_ms,
            recovery_time_sec=config.circuit_breaker_recovery_time_sec,
        )

        # Initialize Vertex AI
        vertexai.init(project=config.project_id, location=config.location)

        # Use tuned model if available, otherwise base model
        model_name = config.gemini_tuned_model or config.gemini_model
        self.model = GenerativeModel(model_name)

        logger.info(f"Initialized Gemini layer with model: {model_name}")

    async def process(self, state: JudgeState) -> JudgeState:
        """Process request through Gemini layer"""
        if not self.config.enable_layer_1 or self.circuit_breaker.is_open():
            logger.warning("Gemini layer bypassed (disabled or circuit open)")
            state["gemini_timeout"] = True
            return state

        start_time = time.time()

        try:
            # Build prompt for Gemini
            prompt = self._build_prompt(state["request"])

            # Call Gemini with timeout
            generation_config = GenerationConfig(
                temperature=0.1,
                top_p=0.95,
                max_output_tokens=256,
            )

            # Async call to Gemini
            response = await asyncio.wait_for(
                self._call_gemini_async(prompt, generation_config),
                timeout=self.config.gemini_timeout_ms / 1000.0,
            )

            # Parse response
            decision, confidence, reasoning = self._parse_response(response)

            duration_ms = (time.time() - start_time) * 1000

            state["gemini_decision"] = decision
            state["gemini_confidence"] = confidence
            state["gemini_reasoning"] = reasoning
            state["gemini_timeout"] = False
            state["gemini_duration_ms"] = duration_ms

            # Record metrics
            layer_duration.labels(layer="gemini").observe(duration_ms / 1000.0)
            request_total.labels(layer="gemini", status="success").inc()

            # Check circuit breaker
            self.circuit_breaker.record_call(duration_ms, "gemini")

            logger.info(
                f"Gemini layer completed: {decision} (confidence: {confidence:.2f}, duration: {duration_ms:.1f}ms)",
            )

        except TimeoutError:
            duration_ms = (time.time() - start_time) * 1000
            state["gemini_timeout"] = True
            state["gemini_duration_ms"] = duration_ms
            request_errors.labels(layer="gemini", error_type="timeout").inc()
            logger.error(f"Gemini layer timeout after {duration_ms:.1f}ms")

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            state["gemini_timeout"] = True
            state["gemini_duration_ms"] = duration_ms
            request_errors.labels(layer="gemini", error_type="error").inc()
            logger.error(f"Gemini layer error: {e}")

        return state

    def _build_prompt(self, request: dict[str, Any]) -> str:
        """Build prompt for Gemini"""
        return f"""You are a policy enforcement AI for the Pnkln governance system.
Analyze the following request and determine if it should be APPROVED or DENIED based on policy compliance.

Request: {request}

Respond in JSON format:
{{
  "decision": "APPROVE" or "DENY",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}}"""

    async def _call_gemini_async(self, prompt: str, config: GenerationConfig) -> str:
        """Async wrapper for Gemini API call"""
        # Note: Vertex AI SDK doesn't have native async support yet
        # This would ideally use aiohttp or similar for true async
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.model.generate_content(prompt, generation_config=config),
        )
        return response.text

    def _parse_response(self, response: str) -> tuple[Decision, float, str]:
        """Parse Gemini response"""
        import json

        try:
            data = json.loads(response)
            decision = Decision(data.get("decision", "DENY"))
            confidence = float(data.get("confidence", 0.0))
            reasoning = data.get("reasoning", "")
            return decision, confidence, reasoning
        except Exception as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            return Decision.ERROR, 0.0, f"Parse error: {e}"


class Layer2PyTorch:
    """Layer 2: PyTorch enforcement logic"""

    def __init__(self, config: Config):
        self.config = config
        self.circuit_breaker = CircuitBreaker(
            threshold_ms=config.circuit_breaker_threshold_ms,
            recovery_time_sec=config.circuit_breaker_recovery_time_sec,
        )

        # In production, load actual PyTorch model here
        # self.model = torch.load(...)
        logger.info("Initialized PyTorch layer (mock)")

    async def process(self, state: JudgeState) -> JudgeState:
        """Process request through PyTorch layer"""
        if not self.config.enable_layer_2 or self.circuit_breaker.is_open():
            logger.warning("PyTorch layer bypassed (disabled or circuit open)")
            state["pytorch_timeout"] = True
            return state

        start_time = time.time()

        try:
            # Mock PyTorch inference
            # In production, this would be: score = self.model.predict(features)
            await asyncio.sleep(0.015)  # Simulate 15ms inference

            score = 0.85  # Mock score
            features = {"feature_1": 0.5, "feature_2": 0.7}

            duration_ms = (time.time() - start_time) * 1000

            state["pytorch_score"] = score
            state["pytorch_features"] = features
            state["pytorch_timeout"] = False
            state["pytorch_duration_ms"] = duration_ms

            # Record metrics
            layer_duration.labels(layer="pytorch").observe(duration_ms / 1000.0)
            request_total.labels(layer="pytorch", status="success").inc()

            # Check circuit breaker
            self.circuit_breaker.record_call(duration_ms, "pytorch")

            logger.info(f"PyTorch layer completed: score={score:.2f}, duration={duration_ms:.1f}ms")

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            state["pytorch_timeout"] = True
            state["pytorch_duration_ms"] = duration_ms
            request_errors.labels(layer="pytorch", error_type="error").inc()
            logger.error(f"PyTorch layer error: {e}")

        return state


class Layer3Rules:
    """Layer 3: Deterministic rules engine"""

    def __init__(self, config: Config):
        self.config = config
        self.rules = self._load_rules()
        logger.info(f"Initialized Rules layer with {len(self.rules)} rules")

    def _load_rules(self) -> list:
        """Load rules from configuration"""
        # In production, load from ConfigMap or database
        return [
            {"id": "R001", "priority": 1, "type": "gemini_approval"},
            {"id": "R002", "priority": 2, "type": "pytorch_threshold"},
            {"id": "R003", "priority": 0, "type": "explicit_deny"},
        ]

    async def process(self, state: JudgeState) -> JudgeState:
        """Process request through rules engine"""
        if not self.config.enable_layer_3:
            logger.warning("Rules layer bypassed (disabled)")
            state["rules_timeout"] = True
            return state

        start_time = time.time()

        try:
            # Apply rules
            verdict, matched_rules = self._apply_rules(state)

            duration_ms = (time.time() - start_time) * 1000

            state["rules_verdict"] = verdict
            state["rules_matched"] = matched_rules
            state["rules_timeout"] = False
            state["rules_duration_ms"] = duration_ms

            # Record metrics
            layer_duration.labels(layer="rules").observe(duration_ms / 1000.0)
            request_total.labels(layer="rules", status="success").inc()

            logger.info(
                f"Rules layer completed: verdict={verdict}, matched={len(matched_rules)}, duration={duration_ms:.1f}ms",
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            state["rules_timeout"] = True
            state["rules_duration_ms"] = duration_ms
            request_errors.labels(layer="rules", error_type="error").inc()
            logger.error(f"Rules layer error: {e}")

        return state

    def _apply_rules(self, state: JudgeState) -> tuple[bool, list]:
        """Apply deterministic rules"""
        matched = []

        # R003: Explicit deny override
        if state.get("gemini_decision") == Decision.DENY:
            matched.append("R003")
            return False, matched

        if state.get("pytorch_score", 0) < 0.3:
            matched.append("R003")
            return False, matched

        # R001: Gemini approval gate
        if state.get("gemini_decision") == Decision.APPROVE:
            matched.append("R001")

        # R002: PyTorch threshold
        if state.get("pytorch_score", 0) > 0.7:
            matched.append("R002")

        # Verdict: approve if both layers agree
        verdict = len(matched) >= 2
        return verdict, matched


# ============================================================================
# ORCHESTRATOR
# ============================================================================


class JudgeOrchestrator:
    """Orchestrates Judge #6 hybrid 3-layer enforcement"""

    def __init__(self, config: Config):
        self.config = config
        self.layer1 = Layer1Gemini(config)
        self.layer2 = Layer2PyTorch(config)
        self.layer3 = Layer3Rules(config)

        logger.info("Judge #6 Orchestrator initialized")

    async def judge_request(self, request: dict[str, Any]) -> JudgeState:
        """Process a request through all 3 layers"""
        request_id = request.get("id", "unknown")

        # Initialize state
        state: JudgeState = {
            "request_id": request_id,
            "request": request,
            "gemini_decision": None,
            "gemini_confidence": None,
            "gemini_reasoning": None,
            "gemini_timeout": False,
            "gemini_duration_ms": None,
            "pytorch_score": None,
            "pytorch_features": None,
            "pytorch_timeout": False,
            "pytorch_duration_ms": None,
            "rules_verdict": None,
            "rules_matched": None,
            "rules_timeout": False,
            "rules_duration_ms": None,
            "final_action": None,
            "final_reasoning": None,
            "total_duration_ms": None,
        }

        start_time = time.time()
        active_requests.inc()

        try:
            # Execute layers sequentially (could be parallelized for lower latency)
            state = await self.layer1.process(state)
            state = await self.layer2.process(state)
            state = await self.layer3.process(state)

            # Make final decision
            state = self._make_final_decision(state)

            # Calculate total duration
            duration_ms = (time.time() - start_time) * 1000
            state["total_duration_ms"] = duration_ms

            # Record overall metrics
            request_duration.labels(layer="total").observe(duration_ms / 1000.0)
            request_total.labels(layer="total", status="success").inc()

            # Log SLA compliance
            if duration_ms > self.config.latency_sla_p99_ms:
                logger.warning(
                    f"SLA BREACH: Request {request_id} took {duration_ms:.1f}ms (SLA: {self.config.latency_sla_p99_ms}ms)",
                )
            else:
                logger.info(f"Request {request_id} completed in {duration_ms:.1f}ms (within SLA)")

        finally:
            active_requests.dec()

        return state

    def _make_final_decision(self, state: JudgeState) -> JudgeState:
        """Make final decision based on layer outputs"""
        # Check for circuit breaker fallback
        if state["gemini_timeout"] or state["pytorch_timeout"]:
            # Fallback to rules-only mode
            if state["rules_verdict"]:
                state["final_action"] = Decision.APPROVE
                state["final_reasoning"] = "Circuit breaker: fallback to rules-only (approved)"
            else:
                state["final_action"] = Decision.DENY
                state["final_reasoning"] = "Circuit breaker: fallback to rules-only (denied)"
            return state

        # Normal operation: require all layers to agree
        if (
            state["gemini_decision"] == Decision.APPROVE
            and state["pytorch_score"]
            and state["pytorch_score"] > 0.7
            and state["rules_verdict"]
        ):
            state["final_action"] = Decision.APPROVE
            state["final_reasoning"] = "All layers approved"
        else:
            state["final_action"] = Decision.DENY
            state["final_reasoning"] = "One or more layers denied"

        return state


# ============================================================================
# MAIN
# ============================================================================


async def main():
    """Main entry point"""
    config = Config()

    # Start Prometheus metrics server
    start_http_server(config.metrics_port)
    logger.info(f"Prometheus metrics server started on port {config.metrics_port}")

    # Initialize orchestrator
    orchestrator = JudgeOrchestrator(config)

    # Example request
    test_request = {
        "id": "test-001",
        "action": "deploy_model",
        "user": "engineer@pnkln.com",
        "resource": "production/model-v2",
    }

    logger.info(f"Processing test request: {test_request['id']}")
    result = await orchestrator.judge_request(test_request)

    logger.info(f"Final decision: {result['final_action']}")
    logger.info(f"Total duration: {result['total_duration_ms']:.1f}ms")
    logger.info(
        f"Layer breakdown: Gemini={result['gemini_duration_ms']:.1f}ms, "
        f"PyTorch={result['pytorch_duration_ms']:.1f}ms, "
        f"Rules={result['rules_duration_ms']:.1f}ms",
    )


if __name__ == "__main__":
    asyncio.run(main())
