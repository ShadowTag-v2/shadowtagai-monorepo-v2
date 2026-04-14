"""Kernel Chain Execution Logic"""

from app.kernels.base import Kernel, KernelChainError
from app.models.decision import AuditTrail, DecisionContext, DecisionResult, RiskTier, Violation


class KernelChain:
    """Ordered chain of kernels."""

    def __init__(self, kernels: list[Kernel]):
        self.kernels = kernels


class ChainExecutor:
    """Executes the kernel chain."""

    def __init__(self, chain: KernelChain):
        self.chain = chain

    async def execute_decision(self, context: DecisionContext) -> DecisionResult:
        """Execute the full chain: Scan -> Classify -> Compress
        """
        try:
            # 1. ATP Scan
            scan_kernel = self.chain.kernels[0]
            # ATP519ScanKernel.execute(context: str) -> ViolationResult
            scan_output = scan_kernel.execute(context.content)

            # 2. Judge Six
            judge_kernel = self.chain.kernels[1]
            # JudgeSixKernel.execute(violations: ViolationResult) -> JudgeSixResult
            judge_output = judge_kernel.execute(scan_output)

            # 3. Audit Compress
            compress_kernel = self.chain.kernels[2]
            # AuditCompressKernel.execute(judge_result, violations) -> AuditTrail (local dataclass)
            audit_output = compress_kernel.execute(judge_output, scan_output)

            # Map Pnkln AuditTrail to App Model AuditTrail (if needed) or just use fields
            # app.models.decision.AuditTrail has:
            # compressed_data, compression_ratio, original_size_bytes, compressed_size_bytes, checksum

            # src.pnkln.kernels.AuditTrail has:
            # compressed_bytes, compression_ratio, original_size_bytes, ...

            app_audit_trail = AuditTrail(
                compressed_data=audit_output.compressed_bytes,
                compression_ratio=audit_output.compression_ratio,
                original_size_bytes=audit_output.original_size_bytes,
                compressed_size_bytes=len(audit_output.compressed_bytes),
                checksum=str(hash(audit_output.compressed_bytes)),  # Simple checksum for now
            )

            # Map Violations
            # src.pnkln.kernels.ViolationResult.violations is list[dict]
            # app.models.decision.Violation expects objects

            mapped_violations = []
            for v in scan_output.violations:
                mapped_violations.append(
                    Violation(
                        rule_id=v.get("category", "unknown"),
                        description=v.get("text", ""),
                        severity=v.get("severity", "low"),
                        context=v.get("snippet", ""),
                        suggested_action="Review compliance guidelines",
                    ),
                )

            # Construct Final Result
            return DecisionResult(
                decision=judge_output.decision,
                confidence=judge_output.confidence,
                risk_tier=RiskTier[f"TIER_{map_risk_tier(judge_output.risk_tier)}"],
                violations=mapped_violations,
                audit_trail=app_audit_trail,
                total_latency_ms=judge_output.execution_time_ms,  # Simplified latency
                total_cost_usd=0.0,
                trace_id=context.trace_id or "unknown",
            )

        except Exception as e:
            raise KernelChainError(f"Chain execution failed: {e}") from e


def map_risk_tier(tier_str: str) -> str:
    """Map L/M/H/EH/CRITICAL to risk tier suffix"""
    mapping = {
        "L": "1_MINIMAL",
        "M": "2_LOW",
        "H": "3_MODERATE",
        "EH": "4_HIGH",
        "CRITICAL": "5_CRITICAL",
    }
    return mapping.get(tier_str, "3_MODERATE")
