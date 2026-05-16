# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""JudgeSixClassifyKernel — kernel wrapper for the Judge 6 pipeline.

Kernel 2 in the 3-kernel chain: ATP519Scan → JudgeSixClassify → AuditCompress.
Receives ViolationsScanOutput, produces JudgeSixClassification.
"""

from __future__ import annotations


from app.kernels.base import Kernel, KernelChainError
from app.models.decision import (
    JudgeSixClassification,
    RiskTier,
    ViolationsScanOutput,
)
from app.models.kernel import KernelInput, KernelMetrics, KernelOutput


class JudgeSixClassifyKernel(Kernel):
    """Kernel that wraps Judge 6 classification for chain orchestration.

    Input:  KernelInput.data = ViolationsScanOutput
    Output: KernelOutput.data = JudgeSixClassification
    """

    def __init__(self):
        super().__init__(name="judge_six_classify")

    async def execute(self, kernel_input: KernelInput) -> KernelOutput:
        """Execute Judge 6 classification on violations scan output.

        Args:
            kernel_input: KernelInput whose .data is ViolationsScanOutput.

        Returns:
            KernelOutput with JudgeSixClassification.

        Raises:
            KernelChainError: If input is not a ViolationsScanOutput.
        """
        if not isinstance(kernel_input.data, ViolationsScanOutput):
            raise KernelChainError(
                f"Invalid input type: expected ViolationsScanOutput, "
                f"got {type(kernel_input.data).__name__}",
            )

        scan_output: ViolationsScanOutput = kernel_input.data
        violations = scan_output.violations

        # ── Feature extraction ──────────────────────────────────────────
        _features = self._extract_features(scan_output)

        # ── Classification logic ────────────────────────────────────────
        if not violations:
            decision = True
            confidence = 0.95
            risk_tier = RiskTier.TIER_1_MINIMAL
            reasoning = "No ATP 5-19 violations detected. Decision approved."
        else:
            decision = False
            severity_counts = _count_severities(violations)
            has_critical = severity_counts.get("critical", 0) > 0
            has_major = severity_counts.get("major", 0) > 0

            if has_critical:
                risk_tier = RiskTier.TIER_5_CRITICAL
                confidence = 0.90
            elif has_major:
                risk_tier = RiskTier.TIER_4_HIGH
                confidence = 0.85
            else:
                risk_tier = RiskTier.TIER_3_MODERATE
                confidence = 0.80

            n = len(violations)
            parts = [f"{n} violation{'s' if n != 1 else ''} detected"]
            for sev in ("critical", "major", "moderate", "minor"):
                cnt = severity_counts.get(sev, 0)
                if cnt:
                    parts.append(f"{cnt} {sev}")
            reasoning = ". ".join(parts) + "."

        classification = JudgeSixClassification(
            decision=decision,
            confidence=confidence,
            risk_tier=risk_tier,
            reasoning=reasoning,
        )

        return KernelOutput(
            data=classification,
            kernel_name=self.name,
            success=True,
            metrics=KernelMetrics(
                latency_ms=0,  # Overwritten by base class __call__
                token_count_input=0,
                token_count_output=0,
                cost_usd=0.0,  # Local deterministic — no API cost
            ),
        )

    # ── Helpers ──────────────────────────────────────────────────────────

    def _extract_features(self, scan_output: ViolationsScanOutput) -> list[float]:
        """Extract a 10-element feature vector from violations for ML scoring.

        Feature vector layout (all normalised to [0, 1]):
            [0] total_violations / 10  (capped)
            [1] minor_count / 5
            [2] moderate_count / 5
            [3] major_count / 5
            [4] critical_count / 5
            [5] unique_rules / 10
            [6] has_major   (0 or 1)
            [7] has_critical (0 or 1)
            [8] avg_severity_score / 4
            [9] reserved (0.0)
        """
        violations = scan_output.violations
        if not violations:
            return [0.0] * 10

        sev_map = {"minor": 1, "moderate": 2, "major": 3, "critical": 4}
        severity_counts = _count_severities(violations)
        total = len(violations)
        unique_rules = len({v.rule_id for v in violations})
        avg_sev = sum(sev_map.get(v.severity, 0) for v in violations) / total

        return [
            min(total / 10.0, 1.0),
            min(severity_counts.get("minor", 0) / 5.0, 1.0),
            min(severity_counts.get("moderate", 0) / 5.0, 1.0),
            min(severity_counts.get("major", 0) / 5.0, 1.0),
            min(severity_counts.get("critical", 0) / 5.0, 1.0),
            min(unique_rules / 10.0, 1.0),
            1.0 if severity_counts.get("major", 0) > 0 else 0.0,
            1.0 if severity_counts.get("critical", 0) > 0 else 0.0,
            min(avg_sev / 4.0, 1.0),
            0.0,
        ]


def _count_severities(violations: list) -> dict[str, int]:
    """Count violations by severity level."""
    counts: dict[str, int] = {}
    for v in violations:
        sev = v.severity.lower() if hasattr(v, "severity") else "unknown"
        counts[sev] = counts.get(sev, 0) + 1
    return counts


__all__ = ["JudgeSixClassifyKernel"]
