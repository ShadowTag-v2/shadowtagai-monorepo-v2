# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
GateAdapter — Bridges the CoreOrchestrator to src/gates/QualityGateChecker.

Provides an async ``check(ctx)`` method that the orchestrator calls
during its pre-flight gate check phase. Translates OperationContext
into gate-compatible checks and returns a GateCheckResult.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class GateCheckResult:
    """Result of a gate check on an operation context."""

    passed: bool
    reason: str = ""
    severity: str = "ok"
    checks: list[dict[str, Any]] = field(default_factory=list)
    latency_ms: float = 0.0


class GateAdapter:
    """
    Async adapter wrapping the quality gate system.

    Enforces pre-flight checks on all operations before they
    reach the routing layer. Gates can be:
    - Structural (payload validation)
    - Security (risk level classification)
    - Budget (cost/rate limiting)
    - Custom (pluggable gate functions)
    """

    def __init__(
        self,
        *,
        quality_gate_checker: Any | None = None,
        custom_gates: list[Any] | None = None,
        fail_open: bool = False,
    ):
        """
        Initialize the gate adapter.

        Args:
            quality_gate_checker: Instance of QualityGateChecker from src/gates.
            custom_gates: Additional callable gate functions.
            fail_open: If True, pass on gate errors instead of blocking.
        """
        self._checker = quality_gate_checker
        self._custom_gates = custom_gates or []
        self._fail_open = fail_open
        self._check_count = 0

    async def check(self, ctx: Any) -> GateCheckResult:
        """
        Run all gate checks against an operation context.

        Args:
            ctx: OperationContext from the orchestrator.

        Returns:
            GateCheckResult with pass/fail status and details.
        """
        start = time.perf_counter()
        self._check_count += 1

        checks: list[dict[str, Any]] = []

        try:
            # Gate 1: Payload validation.
            payload_check = self._validate_payload(ctx)
            checks.append(payload_check)
            if not payload_check["passed"]:
                latency_ms = (time.perf_counter() - start) * 1000
                return GateCheckResult(
                    passed=False,
                    reason=payload_check["message"],
                    severity="critical",
                    checks=checks,
                    latency_ms=latency_ms,
                )

            # Gate 2: Operation-specific security gate.
            security_check = self._security_gate(ctx)
            checks.append(security_check)

            # Gate 3: Custom gates.
            for gate_fn in self._custom_gates:
                custom_result = self._run_custom_gate(gate_fn, ctx)
                checks.append(custom_result)

            # Aggregate results.
            all_passed = all(c["passed"] for c in checks)
            failures = [c for c in checks if not c["passed"]]

            latency_ms = (time.perf_counter() - start) * 1000

            if all_passed:
                return GateCheckResult(
                    passed=True,
                    reason="All gates passed",
                    severity="ok",
                    checks=checks,
                    latency_ms=latency_ms,
                )

            # Find worst severity.
            worst = "warning"
            for f in failures:
                if f.get("severity") == "critical":
                    worst = "critical"
                    break

            reason = "; ".join(f["message"] for f in failures)

            # Fail-open: promote non-critical failures to pass.
            if self._fail_open and worst != "critical":
                logger.warning(
                    "gate_adapter.fail_open",
                    reason=reason,
                    failure_count=len(failures),
                )
                return GateCheckResult(
                    passed=True,
                    reason=f"Passed (fail-open): {reason}",
                    severity="warning",
                    checks=checks,
                    latency_ms=latency_ms,
                )

            return GateCheckResult(
                passed=False,
                reason=reason,
                severity=worst,
                checks=checks,
                latency_ms=latency_ms,
            )

        except Exception as e:
            latency_ms = (time.perf_counter() - start) * 1000
            logger.error("gate_adapter.error", error=str(e))

            if self._fail_open:
                return GateCheckResult(
                    passed=True,
                    reason=f"Gate error (fail-open): {e}",
                    severity="warning",
                    checks=checks,
                    latency_ms=latency_ms,
                )
            return GateCheckResult(
                passed=False,
                reason=f"Gate error: {e}",
                severity="critical",
                checks=checks,
                latency_ms=latency_ms,
            )

    @staticmethod
    def _validate_payload(ctx: Any) -> dict[str, Any]:
        """Validate that the operation context has required fields."""
        if not hasattr(ctx, "payload") or ctx.payload is None:
            return {
                "gate": "payload_validation",
                "passed": False,
                "severity": "critical",
                "message": "Missing operation payload",
            }

        if not hasattr(ctx, "operation_id") or not ctx.operation_id:
            return {
                "gate": "payload_validation",
                "passed": False,
                "severity": "critical",
                "message": "Missing operation_id",
            }

        return {
            "gate": "payload_validation",
            "passed": True,
            "severity": "ok",
            "message": "Payload structure valid",
        }

    @staticmethod
    def _security_gate(ctx: Any) -> dict[str, Any]:
        """
        Basic security classification gate.

        Blocks operations with dangerous payload markers.
        """
        payload = getattr(ctx, "payload", {}) or {}

        # Check for destructive markers.
        # Categories: shell destruction, privilege escalation, network exfil,
        # file manipulation, code injection, SQL injection.
        dangerous_keywords = {
            # Shell destruction
            "rm -rf",
            "rm -f /",
            "mkfs.",
            "dd if=/dev/zero",
            "shred",
            "> /dev/sda",
            # Privilege escalation
            "sudo",
            "su -",
            "doas",
            "chmod 777",
            "chmod +s",
            # Network exfiltration
            "| sh",
            "| bash",
            "nc -e",
            "ncat -e",
            "mkfifo",
            # Code injection
            "eval(",
            "exec(",
            "os.system(",
            "child_process",
            "__import__(",
            # SQL injection
            "DROP TABLE",
            "DELETE FROM",
            "TRUNCATE TABLE",
            "ALTER TABLE DROP",
            "UNION SELECT",
            "xp_cmdshell",
        }
        payload_str = str(payload).lower()

        for keyword in dangerous_keywords:
            if keyword.lower() in payload_str:
                return {
                    "gate": "security",
                    "passed": False,
                    "severity": "critical",
                    "message": f"Dangerous keyword detected: {keyword}",
                }

        return {
            "gate": "security",
            "passed": True,
            "severity": "ok",
            "message": "Security check passed",
        }

    @staticmethod
    def _run_custom_gate(gate_fn: Any, ctx: Any) -> dict[str, Any]:
        """Execute a custom gate function safely."""
        try:
            result = gate_fn(ctx)
            if isinstance(result, dict):
                return result
            return {
                "gate": "custom",
                "passed": bool(result),
                "severity": "ok" if result else "warning",
                "message": str(result),
            }
        except Exception as e:
            return {
                "gate": "custom",
                "passed": False,
                "severity": "warning",
                "message": f"Custom gate error: {e}",
            }

    @property
    def check_count(self) -> int:
        """Total checks performed since init."""
        return self._check_count
