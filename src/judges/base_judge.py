# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Base Judge Class
Abstract base class for all Judge verticals with shared enforcement logic
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any
import time

from src.judges.models import JudgeRequest, JudgeResponse, JudgeDecision, ApprovalGate, JudgeType, AuditTrail
from src.risk_matrix import RiskAssessment, Probability, Severity, assess_risk
from src.utils.semantic_compression import compress_audit_trail, generate_trail_id, validate_semantic_trail


class BaseJudge(ABC):
    """
    Base Judge class implementing common enforcement logic

    All judge verticals inherit from this class and implement:
    - evaluate_action(): Vertical-specific evaluation logic
    - extract_risk_factors(): Extract probability and severity
    """

    def __init__(self, judge_type: JudgeType):
        """
        Initialize base judge

        Args:
            judge_type: The specific judge vertical type
        """
        self.judge_type = judge_type
        self.decision_count = 0
        self.latencies = []

    @abstractmethod
    def evaluate_action(self, request: JudgeRequest) -> dict[str, Any]:
        """
        Evaluate the action (vertical-specific logic)

        Must return dict with:
        - decision: JudgeDecision
        - reasoning: str
        - metadata: Dict[str, Any]

        Args:
            request: Judge request to evaluate

        Returns:
            Evaluation result dictionary
        """
        pass

    @abstractmethod
    def extract_risk_factors(self, request: JudgeRequest, evaluation: dict[str, Any]) -> tuple[Probability, Severity, str, list[str]]:
        """
        Extract ATP 5-19 risk factors from request and evaluation

        Must return:
        - probability: Probability enum
        - severity: Severity enum
        - rationale: str
        - mitigations: list[str]

        Args:
            request: Original judge request
            evaluation: Result from evaluate_action()

        Returns:
            Tuple of (probability, severity, rationale, mitigations)
        """
        pass

    def judge(self, request: JudgeRequest) -> JudgeResponse:
        """
        Main judge enforcement flow (binary ALLOW/BLOCK decision)

        Flow:
        1. Start latency timer
        2. Evaluate action (vertical-specific)
        3. Extract risk factors
        4. Perform ATP 5-19 risk assessment
        5. Determine approval gate
        6. Generate semantic audit trail
        7. Return decision with <90ms latency

        Args:
            request: Judge request to evaluate

        Returns:
            Judge response with binary decision
        """
        start_time = time.perf_counter()

        # Step 1: Evaluate action (vertical-specific)
        evaluation = self.evaluate_action(request)

        # Step 2: Extract risk factors
        probability, severity, rationale, mitigations = self.extract_risk_factors(request, evaluation)

        # Step 3: ATP 5-19 risk assessment
        amount_usd = request.context.get("amount_usd", 0)
        risk_assessment = assess_risk(probability=probability, severity=severity, rationale=rationale, mitigations=mitigations, amount_usd=amount_usd)

        # Step 4: Determine approval gate
        approval_gate = self._map_approval_gate(risk_assessment.approval_authority)

        # Step 5: Final decision (BLOCK if approval required, otherwise ALLOW)
        # Note: ALLOW doesn't mean executed - it means can proceed (possibly to approval)
        final_decision = evaluation["decision"]
        if risk_assessment.requires_approval and final_decision == JudgeDecision.ALLOW:
            # ALLOW but requires approval - route to approval gate
            pass
        elif final_decision == JudgeDecision.BLOCK:
            # Hard BLOCK - do not proceed
            approval_gate = ApprovalGate.ESCALATE

        # Step 6: Generate semantic audit trail
        semantic_trail = compress_audit_trail(
            action_type=request.action_type,
            context=request.context,
            decision=final_decision.value,
            risk_level=risk_assessment.risk_level.value,
            approval_required=risk_assessment.requires_approval,
            approval_authority=risk_assessment.approval_authority,
        )

        # Validate trail
        if not validate_semantic_trail(semantic_trail):
            # Fallback to simple trail
            semantic_trail = f"{request.action_type}→{risk_assessment.risk_level.value}→{final_decision.value}"

        # Step 7: Determine next steps
        next_steps = self._generate_next_steps(final_decision, risk_assessment, approval_gate, request)

        # Calculate latency
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000

        # Track metrics
        self.decision_count += 1
        self.latencies.append(latency_ms)

        # Step 8: Build response
        response = JudgeResponse(
            request_id=request.request_id,
            decision=final_decision,
            risk_assessment=risk_assessment,
            approval_gate=approval_gate,
            reasoning=evaluation["reasoning"],
            semantic_trail=semantic_trail,
            latency_ms=latency_ms,
            judge_type=self.judge_type,
            metadata=evaluation.get("metadata", {}),
            next_steps=next_steps,
            timestamp=datetime.now(timezone.utc),
        )

        return response

    def _map_approval_gate(self, authority: str) -> ApprovalGate:
        """Map approval authority to approval gate"""
        mapping = {
            "Automated": ApprovalGate.AUTO,
            "Department Head": ApprovalGate.DEPT_HEAD,
            "Finance Director": ApprovalGate.FINANCE_DIR,
            "CFO": ApprovalGate.CFO,
            "Senior Executive": ApprovalGate.SENIOR_EXEC,
            "C-Suite + Board": ApprovalGate.BOARD,
        }
        return mapping.get(authority, ApprovalGate.ESCALATE)

    def _generate_next_steps(
        self, decision: JudgeDecision, risk_assessment: RiskAssessment, approval_gate: ApprovalGate, request: JudgeRequest
    ) -> list[str]:
        """Generate actionable next steps"""
        steps = []

        if decision == JudgeDecision.BLOCK:
            steps.append("Action BLOCKED - do not proceed")
            steps.append(f"Escalate to {approval_gate.value} for review")
            steps.append("Document blocking rationale")
        else:  # ALLOW
            if risk_assessment.requires_approval:
                steps.append(f"Route to {approval_gate.value} approval queue")
                steps.append("Hold action pending approval")

                # Add mitigation steps
                for mitigation in risk_assessment.mitigations:
                    steps.append(f"Execute mitigation: {mitigation}")
            else:
                steps.append("Action ALLOWED - may proceed")
                steps.append("Log action in audit trail")

        return steps

    def create_audit_trail(self, response: JudgeResponse, request: JudgeRequest) -> AuditTrail:
        """
        Create immutable audit trail record

        Args:
            response: Judge response
            request: Original request

        Returns:
            Audit trail record
        """
        trail_id = generate_trail_id(self.judge_type.value, request.request_id, response.timestamp)

        return AuditTrail(
            trail_id=trail_id,
            request_id=request.request_id,
            judge_type=self.judge_type,
            decision=response.decision,
            risk_level=response.risk_assessment.risk_level,
            semantic_summary=response.semantic_trail,
            full_context={
                "request": request.model_dump(),
                "response": response.model_dump(),
                # In production: encrypt this
                "encrypted": False,
            },
            approval_chain=[],
            timestamp=response.timestamp,
            retention_days=2555,  # 7 years
        )

    def get_metrics(self) -> dict[str, Any]:
        """Get judge performance metrics"""
        if not self.latencies:
            return {"decision_count": 0, "avg_latency_ms": 0, "p50_latency_ms": 0, "p99_latency_ms": 0}

        sorted_latencies = sorted(self.latencies)
        p50_idx = int(len(sorted_latencies) * 0.50)
        p99_idx = int(len(sorted_latencies) * 0.99)

        return {
            "decision_count": self.decision_count,
            "avg_latency_ms": sum(self.latencies) / len(self.latencies),
            "p50_latency_ms": sorted_latencies[p50_idx],
            "p99_latency_ms": sorted_latencies[p99_idx],
            "max_latency_ms": max(self.latencies),
            "min_latency_ms": min(self.latencies),
        }


__all__ = ["BaseJudge"]
