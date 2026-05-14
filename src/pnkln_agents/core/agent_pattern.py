# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Pnkln Agent Pattern: Enforcement-First Agent Architecture

Pattern:
    task = parse_user_intent()
    jr_decision = jr_engine.validate(task)  # Purpose/Reasons/Brakes
    if jr_decision.brake_triggered:
        return escalate_to_human(jr_decision.audit)
    result = execute(task, guardrails=jr_decision.constraints)
    if not judge_six.verify(result, sla_p99=90):
        return rollback_and_log(result)
    return result + shadowtag_v2.watermark()
"""

from dataclasses import dataclass
from typing import Any
from collections.abc import Callable
from enum import Enum
import time
import json
from datetime import datetime, timezone

from .jr_engine import JREngine, Purpose, Reason, JRDecision
from .judge_six_lite import JudgeSixLite, VerificationResult


class AgentStatus(Enum):
    """Agent execution status"""

    PENDING = "pending"
    VALIDATING = "validating"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"
    ROLLED_BACK = "rolled_back"


@dataclass
class AgentTask:
    """Represents a task for the agent to execute"""

    intent: str
    customer_id: str
    context: dict[str, Any]
    cost_estimate_usd: float = 0.0
    business_value: str = ""
    expected_outcome: str = ""


@dataclass
class AgentResult:
    """Result of agent execution"""

    status: AgentStatus
    output: Any
    jr_decision: JRDecision | None = None
    verification_result: VerificationResult | None = None
    audit_trail: dict[str, Any] = None
    execution_time_ms: float = 0.0
    metadata: dict[str, Any] = None


class PnklnAgent:
    """
    Base class for Pnkln enforcement-first agents

    All agents follow the pattern:
    1. Parse user intent → AgentTask
    2. JR Engine validates (Purpose/Reasons/Brakes) → JRDecision
    3. If brake triggered → escalate to human
    4. Execute task with guardrails → raw result
    5. Judge #6 verifies result → VerificationResult
    6. If verification fails → rollback and log
    7. Return result with watermark
    """

    def __init__(self, jr_engine: JREngine | None = None, judge_six: JudgeSixLite | None = None, config: dict[str, Any] | None = None):
        self.jr_engine = jr_engine or JREngine()
        self.judge_six = judge_six or JudgeSixLite()
        self.config = config or {}
        self.execution_history: list[AgentResult] = []

    def execute(self, task: AgentTask) -> AgentResult:
        """
        Execute agent task with enforcement-first pattern

        Args:
            task: AgentTask with intent, customer_id, and context

        Returns:
            AgentResult with status, output, and audit trail
        """
        start_time = time.perf_counter()
        audit_trail = {
            "start_time": datetime.now(timezone.utc).isoformat(),
            "task": {
                "intent": task.intent,
                "customer_id": task.customer_id,
                "cost_estimate_usd": task.cost_estimate_usd,
            },
        }

        try:
            # Step 1: Validate with JR Engine
            jr_decision = self._validate_with_jr_engine(task)
            audit_trail["jr_validation"] = jr_decision.audit_trail

            # Step 2: Check for brakes
            if not jr_decision.approved:
                return self._escalate_to_human(task, jr_decision, audit_trail, start_time)

            # Step 3: Execute task with guardrails
            raw_result = self._execute_task(task, jr_decision.constraints)
            audit_trail["execution"] = {
                "completed": True,
                "constraints_applied": jr_decision.constraints,
            }

            # Step 4: Verify with Judge #6
            verification_result = self._verify_with_judge_six(raw_result, task.context)
            audit_trail["verification"] = verification_result.audit_report

            # Step 5: Check verification
            if not verification_result.passed:
                return self._rollback_and_log(task, raw_result, verification_result, audit_trail, start_time)

            # Step 6: Apply watermark and return
            final_result = self._apply_watermark(raw_result)

            execution_time_ms = (time.perf_counter() - start_time) * 1000
            audit_trail["end_time"] = datetime.now(timezone.utc).isoformat()
            audit_trail["execution_time_ms"] = execution_time_ms

            result = AgentResult(
                status=AgentStatus.COMPLETED,
                output=final_result,
                jr_decision=jr_decision,
                verification_result=verification_result,
                audit_trail=audit_trail,
                execution_time_ms=execution_time_ms,
                metadata={
                    "watermarked": True,
                },
            )

            self.execution_history.append(result)
            return result

        except Exception as e:
            execution_time_ms = (time.perf_counter() - start_time) * 1000
            audit_trail["error"] = str(e)
            audit_trail["end_time"] = datetime.now(timezone.utc).isoformat()

            result = AgentResult(
                status=AgentStatus.FAILED, output=None, audit_trail=audit_trail, execution_time_ms=execution_time_ms, metadata={"error": str(e)}
            )

            self.execution_history.append(result)
            return result

    def _validate_with_jr_engine(self, task: AgentTask) -> JRDecision:
        """Validate task with JR Engine"""
        purpose = Purpose(
            intent=task.intent,
            business_value=task.business_value or "Automated agent execution",
            customer_id=task.customer_id,
            cost_estimate_usd=task.cost_estimate_usd,
            expected_outcome=task.expected_outcome or "Task completion",
        )

        # Build reasons based on task context
        reasons = self._build_reasons(task)

        return self.jr_engine.validate(purpose, reasons, task.context)

    def _build_reasons(self, task: AgentTask) -> list[Reason]:
        """Build reasons for JR Engine validation (override in subclasses)"""
        return [
            Reason(
                justification="Automated agent task execution",
                risk_probability=0.1,
                risk_severity=0.2,
                mitigation_strategy="Automated verification with Judge #6",
            )
        ]

    def _execute_task(self, task: AgentTask, constraints: dict[str, Any]) -> Any:
        """
        Execute the actual task (must be implemented by subclasses)

        Args:
            task: AgentTask to execute
            constraints: Constraints from JR Engine

        Returns:
            Raw result of task execution
        """
        raise NotImplementedError("Subclasses must implement _execute_task")

    def _verify_with_judge_six(self, result: Any, context: dict[str, Any]) -> VerificationResult:
        """Verify result with Judge #6"""
        return self.judge_six.verify(result, context)

    def _escalate_to_human(self, task: AgentTask, jr_decision: JRDecision, audit_trail: dict[str, Any], start_time: float) -> AgentResult:
        """Escalate to human when brakes are triggered"""
        execution_time_ms = (time.perf_counter() - start_time) * 1000
        audit_trail["escalation"] = {
            "reason": "JR Engine brake triggered",
            "brakes": [
                {
                    "type": brake.brake_type.value,
                    "reason": brake.reason,
                    "required_action": brake.required_action,
                }
                for brake in jr_decision.brakes
            ],
        }
        audit_trail["end_time"] = datetime.now(timezone.utc).isoformat()

        result = AgentResult(
            status=AgentStatus.ESCALATED,
            output=None,
            jr_decision=jr_decision,
            audit_trail=audit_trail,
            execution_time_ms=execution_time_ms,
            metadata={
                "escalation_reason": jr_decision.brakes[0].reason if jr_decision.brakes else "Unknown",
            },
        )

        self.execution_history.append(result)
        return result

    def _rollback_and_log(
        self, task: AgentTask, result: Any, verification_result: VerificationResult, audit_trail: dict[str, Any], start_time: float
    ) -> AgentResult:
        """Rollback and log when verification fails"""
        execution_time_ms = (time.perf_counter() - start_time) * 1000
        audit_trail["rollback"] = {
            "reason": "Judge #6 verification failed",
            "violations": [
                {
                    "type": v.violation_type.value,
                    "severity": v.severity.value,
                    "description": v.description,
                }
                for v in verification_result.violations
            ],
        }
        audit_trail["end_time"] = datetime.now(timezone.utc).isoformat()

        # Perform rollback (override in subclasses if needed)
        self._perform_rollback(task, result)

        result_obj = AgentResult(
            status=AgentStatus.ROLLED_BACK,
            output=None,
            verification_result=verification_result,
            audit_trail=audit_trail,
            execution_time_ms=execution_time_ms,
            metadata={
                "rollback_reason": "Verification failed",
                "violation_count": len(verification_result.violations),
            },
        )

        self.execution_history.append(result_obj)
        return result_obj

    def _perform_rollback(self, task: AgentTask, result: Any):
        """Perform rollback (override in subclasses for specific rollback logic)"""
        pass

    def _apply_watermark(self, result: Any) -> Any:
        """Apply ShadowTag v2 watermark (placeholder)"""
        # TODO: Implement actual watermarking logic
        if isinstance(result, dict):
            result["_pnkln_watermark"] = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "version": "shadowtag_v2",
                "agent": self.__class__.__name__,
            }
        return result

    def get_audit_trail(self, result_index: int = -1) -> dict[str, Any]:
        """Get audit trail for a specific execution (default: most recent)"""
        if not self.execution_history:
            return {}
        return self.execution_history[result_index].audit_trail

    def export_audit_report(self, result_index: int = -1, format: str = "json") -> bytes:
        """Export audit report in specified format"""
        audit_trail = self.get_audit_trail(result_index)

        if format == "json":
            return json.dumps(audit_trail, indent=2).encode("utf-8")
        elif format == "pdf":
            # TODO: Implement PDF export
            return json.dumps(audit_trail, indent=2).encode("utf-8")
        else:
            raise ValueError(f"Unsupported format: {format}")


class SimpleAgent(PnklnAgent):
    """
    Simple example agent that demonstrates the enforcement-first pattern
    """

    def __init__(self, executor: Callable[[AgentTask, dict[str, Any]], Any], **kwargs):
        super().__init__(**kwargs)
        self.executor = executor

    def _execute_task(self, task: AgentTask, constraints: dict[str, Any]) -> Any:
        """Execute task using provided executor function"""
        return self.executor(task, constraints)
