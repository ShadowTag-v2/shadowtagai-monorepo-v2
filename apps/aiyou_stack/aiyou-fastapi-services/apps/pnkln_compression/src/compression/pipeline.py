import time
from dataclasses import asdict, dataclass

from .atp_519_scan import atp_519_scan
from .decision_packet import Decision, DecisionPacket, RiskLevel
from .llmlingua_stage import get_compressor


@dataclass
class CompressionMetrics:
    total_latency_ms: float
    stage_latencies: dict[str, float]
    sla_met: bool
    input_size: int
    output_size: int


class PnklnCompressionPipeline:
    SLA_MS = 90

    def __init__(self):
        # Lazy load compressor
        self.compressor = get_compressor()

    def process(
        self,
        context: str,
        session_id: str,
        domain: str = "general",
    ) -> tuple[DecisionPacket, CompressionMetrics]:
        start_total = time.perf_counter()
        latencies = {}
        input_size = len(context.encode("utf-8"))

        # --- Stage 1: ATP Scan ---
        t1 = time.perf_counter()
        atp = atp_519_scan(context, domain=domain)
        latencies["atp"] = (time.perf_counter() - t1) * 1000

        # --- Stage 2: Compression ---
        t2 = time.perf_counter()
        # Pre-truncate to protect Stage 2 from massive inputs
        if len(atp.compressed_context) > 2000:
            atp.compressed_context = atp.compressed_context[:2000]

        compressed = self.compressor.compress_for_judge6(asdict(atp))
        latencies["llm"] = (time.perf_counter() - t2) * 1000

        # --- Stage 3: Judge #6 Logic ---
        t3 = time.perf_counter()
        decision_data = self._judge6_decide(atp)
        latencies["judge"] = (time.perf_counter() - t3) * 1000

        # --- Stage 4: Packetize ---
        t4 = time.perf_counter()
        packet = DecisionPacket.create(
            decision=decision_data["decision"],
            risk_level=decision_data["risk_level"],
            confidence_pct=decision_data["confidence"],
            policies=atp.policy_refs,
            reason=decision_data["reason"],
            audit_context=compressed.get("compressed_text", "")[:163],
            session_id=session_id,
        )
        latencies["pack"] = (time.perf_counter() - t4) * 1000

        total_ms = (time.perf_counter() - start_total) * 1000
        metrics = CompressionMetrics(
            total_latency_ms=total_ms,
            stage_latencies=latencies,
            sla_met=total_ms <= self.SLA_MS,
            input_size=input_size,
            output_size=DecisionPacket.TOTAL_SIZE,
        )

        return packet, metrics

    def _judge6_decide(self, atp):
        """Deterministic Governance Logic"""
        # Hard Stop: Known Violations
        if atp.violations:
            return {
                "decision": Decision.DENY,
                "risk_level": RiskLevel.HIGH,
                "confidence": 0.99,
                "reason": f"Violations detected: {','.join(atp.violations)}",
            }

        # Hard Stop: Extreme Risk
        if atp.risk_level == "EH":
            return {
                "decision": Decision.ESCALATE,
                "risk_level": RiskLevel.EXTREMELY_HIGH,
                "confidence": 0.95,
                "reason": f"EH Risk ({atp.risk_probability}/{atp.risk_severity})",
            }

        # Default Logic
        risk_map = {"L": RiskLevel.LOW, "M": RiskLevel.MEDIUM, "H": RiskLevel.HIGH}
        mapped_risk = risk_map.get(atp.risk_level, RiskLevel.MEDIUM)

        return {
            "decision": Decision.ALLOW,
            "risk_level": mapped_risk,
            "confidence": 0.85,
            "reason": f"Standard access: {atp.action_requested} {atp.entity_type}",
        }
