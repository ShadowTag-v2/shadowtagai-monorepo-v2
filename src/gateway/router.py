# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Governance Request Router

The heart of hybrid architecture: routes requests to fast or slow path.
Every routing decision justified. Every path optimized.

"Elegance is not when there's nothing left to add,
 but when there's nothing left to remove."
"""

import time
import uuid
from datetime import datetime, timezone

from .models import (
    GovernanceRequest,
    GovernanceResponse,
    RoutingDecision,
    DecisionPath,
    DecisionOutcome,
    RiskAssessment,
)
from .risk_classifier import ATP519RiskClassifier


class GovernanceRouter:
    """
    Routes governance requests to optimal decision path.

    Fast Path (OPA): <10ms, deterministic, 98% of requests
    Slow Path (Agent): 2-5s, contextual, 2% of requests
    """

    def __init__(
        self,
        opa_client: Any | None = None,
        agent_client: Any | None = None,
    ):
        """
        Initialize router with decision engines.

        Args:
            opa_client: OPA rule engine client (fast path)
            agent_client: Agent governance client (slow path)
        """
        self.opa_client = opa_client
        self.agent_client = agent_client
        self.classifier = ATP519RiskClassifier()

    async def route_request(self, request: GovernanceRequest) -> tuple[RoutingDecision, GovernanceResponse]:
        """
        Route request and return decision.

        This is the primary entry point for all governance decisions.

        Returns:
            (routing_decision, governance_response) tuple
        """
        start_time = time.time()

        # Step 1: Assess risk using ATP 5-19
        risk_assessment = self.classifier.assess_risk(request)

        # Step 2: Determine routing path
        path = self.classifier.determine_path(risk_assessment)
        estimated_latency = self.classifier.estimate_latency(path)

        routing_decision = RoutingDecision(
            path=path,
            risk_assessment=risk_assessment,
            reason=self._explain_routing(risk_assessment, path),
            estimated_latency_ms=estimated_latency,
        )

        # Step 3: Execute decision on chosen path
        if path == DecisionPath.FAST_PATH:
            response = await self._execute_fast_path(request, risk_assessment)
        else:
            response = await self._execute_slow_path(request, risk_assessment)

        # Step 4: Record actual latency
        actual_latency = int((time.time() - start_time) * 1000)
        response.latency_ms = actual_latency

        return routing_decision, response

    async def _execute_fast_path(self, request: GovernanceRequest, risk: RiskAssessment) -> GovernanceResponse:
        """
        Execute OPA fast path (<10ms deterministic decisions).

        For EH/H risk: immediate blocking of dangerous actions.
        """
        if self.opa_client is None:
            # Fallback to conservative denial if OPA unavailable
            return self._create_fallback_response(request, "OPA client unavailable - defaulting to DENY")

        try:
            # Call OPA with request context
            opa_result = await self._call_opa(request)

            return GovernanceResponse(
                request_id=request.request_id,
                outcome=(DecisionOutcome.APPROVED if opa_result["allow"] else DecisionOutcome.DENIED),
                confidence=1.0,  # Deterministic rules = 100% confidence
                reasoning=opa_result.get("reasons", ["OPA rule evaluation"]),
                policy_citations=opa_result.get("policies", []),
                path_taken=DecisionPath.FAST_PATH,
                latency_ms=0,  # Will be set by router
                model_used=None,  # OPA, not LLM
                trust_score=1.0,  # OPA is fully trusted
                hallucination_check=True,  # N/A for deterministic
                timestamp=datetime.now(timezone.utc),
                audit_id=f"audit_{uuid.uuid4().hex[:16]}",
            )

        except Exception as e:
            # OPA failure -> conservative fallback
            return self._create_fallback_response(request, f"OPA execution error: {str(e)}")

    async def _execute_slow_path(self, request: GovernanceRequest, risk: RiskAssessment) -> GovernanceResponse:
        """
        Execute agent slow path (2-5s contextual reasoning).

        For M/L risk: nuanced evaluation with policy interpretation.
        """
        if self.agent_client is None:
            # If agents unavailable, escalate to human review
            return GovernanceResponse(
                request_id=request.request_id,
                outcome=DecisionOutcome.ESCALATED,
                confidence=0.0,
                reasoning=["Agent client unavailable - human review required"],
                policy_citations=[],
                path_taken=DecisionPath.SLOW_PATH,
                latency_ms=0,
                model_used=None,
                trust_score=0.0,
                hallucination_check=False,
                timestamp=datetime.now(timezone.utc),
                audit_id=f"audit_{uuid.uuid4().hex[:16]}",
                escalation_required=True,
                escalation_reason="Agent system unavailable",
            )

        try:
            # Call agent governance layer
            agent_result = await self._call_agent(request, risk)

            # Validate agent response
            if agent_result["confidence"] < 0.6:
                # Low confidence -> escalate
                return GovernanceResponse(
                    request_id=request.request_id,
                    outcome=DecisionOutcome.ESCALATED,
                    confidence=agent_result["confidence"],
                    reasoning=agent_result["reasoning"],
                    policy_citations=agent_result.get("citations", []),
                    path_taken=DecisionPath.SLOW_PATH,
                    latency_ms=0,
                    model_used=agent_result.get("model", "gemini-2.5-flash"),
                    trust_score=agent_result.get("trust_score", 0.5),
                    hallucination_check=agent_result.get("hallucination_check", True),
                    timestamp=datetime.now(timezone.utc),
                    audit_id=f"audit_{uuid.uuid4().hex[:16]}",
                    escalation_required=True,
                    escalation_reason="Confidence below threshold (60%)",
                )

            return GovernanceResponse(
                request_id=request.request_id,
                outcome=(DecisionOutcome.APPROVED if agent_result["decision"] == "approve" else DecisionOutcome.DENIED),
                confidence=agent_result["confidence"],
                reasoning=agent_result["reasoning"],
                policy_citations=agent_result.get("citations", []),
                path_taken=DecisionPath.SLOW_PATH,
                latency_ms=0,
                model_used=agent_result.get("model", "gemini-2.5-flash"),
                trust_score=agent_result.get("trust_score", 0.8),
                hallucination_check=agent_result.get("hallucination_check", True),
                timestamp=datetime.now(timezone.utc),
                audit_id=f"audit_{uuid.uuid4().hex[:16]}",
            )

        except Exception as e:
            # Agent failure -> escalate
            return GovernanceResponse(
                request_id=request.request_id,
                outcome=DecisionOutcome.ESCALATED,
                confidence=0.0,
                reasoning=[f"Agent execution error: {str(e)}"],
                policy_citations=[],
                path_taken=DecisionPath.SLOW_PATH,
                latency_ms=0,
                model_used=None,
                trust_score=0.0,
                hallucination_check=False,
                timestamp=datetime.now(timezone.utc),
                audit_id=f"audit_{uuid.uuid4().hex[:16]}",
                escalation_required=True,
                escalation_reason=f"Agent system error: {str(e)}",
            )

    async def _call_opa(self, request: GovernanceRequest) -> dict:
        """
        Call OPA policy engine.

        Placeholder for actual OPA integration.
        """
        # TODO: Implement actual OPA client call
        # For now, return mock response
        return {
            "allow": request.financial_value is None or request.financial_value < 10_000,
            "reasons": [
                "Amount within delegated authority",
                "Resource type permitted for user role",
            ],
            "policies": ["POL-FIN-001", "POL-AUTH-003"],
        }

    async def _call_agent(self, request: GovernanceRequest, risk: RiskAssessment) -> dict:
        """
        Call agent governance layer.

        Placeholder for actual agent integration.
        """
        # TODO: Implement actual agent client call
        # For now, return mock response
        return {
            "decision": "approve" if risk.risk_level.value in ["low", "medium"] else "deny",
            "confidence": 0.87,
            "reasoning": [
                f"Risk assessment: {risk.risk_level.value}",
                f"Identified hazards: {', '.join(risk.hazards)}",
                f"Recommended controls: {', '.join(risk.controls)}",
                "All controls can be implemented",
            ],
            "citations": ["POL-RISK-001 §2.3", "ATP-5-19 Risk Matrix"],
            "model": "gemini-2.5-flash-002",
            "trust_score": 0.85,
            "hallucination_check": True,
        }

    def _explain_routing(self, risk: RiskAssessment, path: DecisionPath) -> str:
        """
        Generate human-readable routing explanation.

        Transparency is security. Every decision explained.
        """
        if path == DecisionPath.FAST_PATH:
            return f"{risk.risk_level.value.upper()} risk requires immediate deterministic control via OPA rule engine"
        else:
            return f"{risk.risk_level.value.upper()} risk benefits from contextual agent evaluation with policy interpretation"

    def _create_fallback_response(self, request: GovernanceRequest, reason: str) -> GovernanceResponse:
        """
        Create conservative fallback response when systems fail.

        Fail secure: when in doubt, deny and escalate.
        """
        return GovernanceResponse(
            request_id=request.request_id,
            outcome=DecisionOutcome.DENIED,
            confidence=1.0,  # Certain denial
            reasoning=[reason, "Failing secure per security policy"],
            policy_citations=["POL-SEC-001: Fail Secure Principle"],
            path_taken=DecisionPath.FAST_PATH,
            latency_ms=0,
            model_used=None,
            trust_score=1.0,  # Failsafe is trusted
            hallucination_check=True,
            timestamp=datetime.now(timezone.utc),
            audit_id=f"audit_{uuid.uuid4().hex[:16]}",
            escalation_required=True,
            escalation_reason="System failure - manual review required",
        )
