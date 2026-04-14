"""Judge Six Sentinel — Governance Gate for UphillSnowball Sovereign OS.

Production-ready version: self-contained, no external deps.
"""

import logging

logger = logging.getLogger(__name__)


class MemoryBank:
    """Simple in-memory governance history."""

    def __init__(self):
        self._history: list[dict] = []

    def consult(self, query: str, context: str = "general") -> str:
        """Check if query is in the known-safe patterns."""
        safe_patterns = ["health", "status", "ping", "rag", "query"]
        if any(p in query.lower() for p in safe_patterns):
            return "ALLOW"
        return "EVALUATE"


class JudgeSixSentinel:
    """Core governance gate.

    Enforces hazard pattern detection and basic risk scoring
    before allowing mission execution.
    """

    def __init__(self):
        self.memory = MemoryBank()
        self.forbidden = [
            "sk-",          # API key leak
            "rm -rf",       # destructive cmd
            "0.0.0.0/0",   # open CIDR
            "DROP TABLE",   # SQL injection
            "sudo ",        # privilege escalation
        ]

    def evaluate(self, query: str, context: str = "general") -> dict:
        """Evaluate a mission request through the governance pipeline.

        Returns:
            dict with 'status' (SUCCESS/BLOCKED) and 'reason'.
        """
        # 1. Hazard Pattern Check
        for bad in self.forbidden:
            if bad.lower() in query.lower():
                logger.warning("BLOCKED: hazard pattern '%s' in query", bad)
                return {
                    "status": "BLOCKED",
                    "reason": f"Hazard Pattern Detected: '{bad}'",
                    "gate": 1,
                }

        # 2. Memory Override (known-safe patterns)
        if self.memory.consult(query, context) == "ALLOW":
            return {
                "status": "SUCCESS",
                "reason": "Memory Override — known safe pattern",
                "gate": 2,
            }

        # 3. Risk Scoring (simplified for v1)
        high_risk_signals = ["delete", "drop", "truncate", "exec", "eval"]
        risk_score = sum(1 for s in high_risk_signals if s in query.lower())

        if risk_score >= 2:
            logger.warning("BLOCKED: high risk score %d for query", risk_score)
            return {
                "status": "BLOCKED",
                "reason": f"High Risk Score: {risk_score}/5",
                "gate": 3,
            }

        return {
            "status": "SUCCESS",
            "reason": f"Approved (risk={risk_score}/5)",
            "gate": 3,
        }
