# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
JR Engine: Purpose-Reasons-Brakes validation framework.

Validates each kernel against three criteria:
- Purpose: Does this kernel advance revenue/security?
- Reasons: Can I defend this kernel's necessity?
- Brakes: What's p99 failure mode? Cost blowup scenario?
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel


class ValidationStatus(str, Enum):
    """Validation status for each criterion."""

    PASS = "✓"
    FAIL = "✗"
    WARNING = "⚠"


class KernelValidation(BaseModel):
    """Validation result for a single kernel."""

    kernel_name: str
    purpose_status: ValidationStatus
    purpose_notes: str
    reasons_status: ValidationStatus
    reasons_notes: str
    brakes_status: ValidationStatus
    brakes_notes: str
    verdict: str  # "APPROVED" or "REJECTED"
    overall_notes: str | None = None


class ValidationResult(BaseModel):
    """Overall validation result for kernel chain."""

    passed: bool
    total_kernels: int
    approved_kernels: int
    rejected_kernels: int
    validations: list[KernelValidation]
    recommendations: list[str] = []


class JREngine:
    """
    JR Engine validator for kernel chain architecture.

    Example usage:
        engine = JREngine()
        result = engine.validate_kernel_chain([
            ("ATP519ScanKernel", kernel_1_config),
            ("JudgeSixClassifyKernel", kernel_2_config),
            ("AuditCompressKernel", kernel_3_config),
        ])
    """

    # Predefined validations for SHADOWTAGAI kernels
    KERNEL_VALIDATIONS: dict[str, KernelValidation] = {
        "ATP519ScanKernel": KernelValidation(
            kernel_name="ATP519ScanKernel",
            purpose_status=ValidationStatus.PASS,
            purpose_notes=("Advances security: Extracts ATP 5-19 violations, enabling compliance enforcement. Direct impact on go/no-go decision."),
            reasons_status=ValidationStatus.PASS,
            reasons_notes=(
                "Must-have: Without violation extraction, no downstream "
                "classification possible. 95% token reduction (50KB → 2.5KB) "
                "justifies cost/complexity."
            ),
            brakes_status=ValidationStatus.PASS,
            brakes_notes=(
                "p99 failure: Gemini API timeout (40ms SLA). "
                "Cost blowup: Max $0.0003/decision (50KB context). "
                "Mitigation: Fail fast on timeout, enforce token limits."
            ),
            verdict="APPROVED",
            overall_notes=("Critical kernel. Single responsibility (extract violations only). Meets all JR Engine criteria."),
        ),
        "JudgeSixClassifyKernel": KernelValidation(
            kernel_name="JudgeSixClassifyKernel",
            purpose_status=ValidationStatus.PASS,
            purpose_notes=("Advances revenue: Binary decision reduces manual review by 80%. Enables automated governance at scale."),
            reasons_status=ValidationStatus.PASS,
            reasons_notes=(
                "Must-have: Core decision engine (Judge #6 compliant). "
                "Zero cost (local PyTorch), <12ms p99. Risk tier classification "
                "required for audit compliance."
            ),
            brakes_status=ValidationStatus.PASS,
            brakes_notes=(
                "p99 failure: Model inference timeout (12ms SLA). "
                "Cost blowup: N/A (local inference, zero marginal cost). "
                "Mitigation: CPU-only inference, no GPU dependency."
            ),
            verdict="APPROVED",
            overall_notes=("Core decision kernel. Local inference = zero cost + low latency. Confidence threshold (0.85) provides quality gate."),
        ),
        "AuditCompressKernel": KernelValidation(
            kernel_name="AuditCompressKernel",
            purpose_status=ValidationStatus.PASS,
            purpose_notes=(
                "Advances security: Immutable audit trail required for compliance. 10:1 compression enables long-term storage (487 bytes/decision)."
            ),
            reasons_status=ValidationStatus.PASS,
            reasons_notes=(
                "Must-have: Regulatory requirement for decision auditability. "
                "Deterministic compression (zstd) = reproducible trails. "
                "Checksum ensures integrity."
            ),
            brakes_status=ValidationStatus.PASS,
            brakes_notes=(
                "p99 failure: Compression library error (rare, deterministic). "
                "Cost blowup: N/A (rules-based, zero cost). "
                "Mitigation: Graceful degradation (store uncompressed if needed)."
            ),
            verdict="APPROVED",
            overall_notes=("Compliance-critical kernel. Deterministic + zero cost. Compression ratio monitored (target: 10:1)."),
        ),
    }

    # Example of a REJECTED kernel (per architecture doc)
    REJECTED_EXAMPLE = KernelValidation(
        kernel_name="SentimentAnalysisKernel",
        purpose_status=ValidationStatus.FAIL,
        purpose_notes=("Does NOT advance revenue/security: Sentiment analysis is informational only, doesn't affect go/no-go decision."),
        reasons_status=ValidationStatus.FAIL,
        reasons_notes=("Nice-to-have, NOT must-have: Decision can be made without sentiment. Adds latency/cost without improving accuracy."),
        brakes_status=ValidationStatus.PASS,
        brakes_notes="Fails gracefully if removed (no downstream dependency).",
        verdict="REJECTED",
        overall_notes=("Kill this kernel. 3-kernel chain sufficient. Violates Purpose + Reasons criteria."),
    )

    def validate_kernel_chain(self, kernel_names: list[str]) -> ValidationResult:
        """
        Validate a proposed kernel chain.

        Args:
            kernel_names: List of kernel names to validate

        Returns:
            ValidationResult with per-kernel validations and overall verdict
        """
        validations = []
        approved_count = 0
        rejected_count = 0
        recommendations = []

        for name in kernel_names:
            validation = self.KERNEL_VALIDATIONS.get(name)

            if not validation:
                # Unknown kernel - create warning validation
                validation = KernelValidation(
                    kernel_name=name,
                    purpose_status=ValidationStatus.WARNING,
                    purpose_notes="Unknown kernel - manual JR Engine validation required",
                    reasons_status=ValidationStatus.WARNING,
                    reasons_notes="Unknown kernel - manual JR Engine validation required",
                    brakes_status=ValidationStatus.WARNING,
                    brakes_notes="Unknown kernel - manual JR Engine validation required",
                    verdict="NEEDS_REVIEW",
                    overall_notes="Kernel not in predefined validation set",
                )
                recommendations.append(f"Manual review required for {name}: Apply JR Engine criteria")

            validations.append(validation)

            if validation.verdict == "APPROVED":
                approved_count += 1
            elif validation.verdict == "REJECTED":
                rejected_count += 1
                recommendations.append(f"Remove {name} from chain: Failed JR Engine validation")

        # Overall pass: all kernels approved, none rejected
        passed = rejected_count == 0 and approved_count == len(kernel_names)

        # Additional recommendations based on chain composition
        if len(kernel_names) > 5:
            recommendations.append(f"Chain has {len(kernel_names)} kernels. Consider reducing for lower latency/complexity.")

        return ValidationResult(
            passed=passed,
            total_kernels=len(kernel_names),
            approved_kernels=approved_count,
            rejected_kernels=rejected_count,
            validations=validations,
            recommendations=recommendations,
        )

    def validate_kernel(self, kernel_name: str) -> KernelValidation:
        """
        Validate a single kernel.

        Args:
            kernel_name: Name of kernel to validate

        Returns:
            KernelValidation for this kernel
        """
        return self.KERNEL_VALIDATIONS.get(
            kernel_name,
            KernelValidation(
                kernel_name=kernel_name,
                purpose_status=ValidationStatus.WARNING,
                purpose_notes="Unknown kernel",
                reasons_status=ValidationStatus.WARNING,
                reasons_notes="Unknown kernel",
                brakes_status=ValidationStatus.WARNING,
                brakes_notes="Unknown kernel",
                verdict="NEEDS_REVIEW",
            ),
        )


class YRMClient:
    """Client for YouAi Risk Engine (YRM) integration."""

    def report_hazard(self, category: str, severity: str, description: str, details: dict[str, Any]):
        """
        Report a hazard to the YRM.

        Args:
            category: Hazard category (e.g., "code_quality")
            severity: Risk level (EH, H, M, L)
            description: Short description
            details: Additional context
        """
        print(f"🚨 [YRM] Hazard Reported: [{severity}] {description}")
        print(f"   Category: {category}")
        print(f"   Details: {details}")
        # In a real implementation, this would send data to the YRM service
