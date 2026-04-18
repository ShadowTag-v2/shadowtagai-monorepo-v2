"""Brakes Validator - JR Engine Component 3

Validates the BRAKES (risks) of an action:
- What could go wrong?
- Are there security threats?
- Are there compliance violations?
- Are there performance/ethical concerns?
"""

from ..models import Action, BrakesVerdict, Severity, VerdictStatus


class BrakesValidator:
    """Validates the BRAKES dimension of an action (risk detection)"""

    def validate(self, action: Action) -> BrakesVerdict:
        payload_str = str(action.payload).lower()
        threats = []

        # Simple heuristics for prototype
        if "sql" in payload_str and ("union" in payload_str or "select" in payload_str):
            threats.append("Possible SQL Injection")
        if "<script>" in payload_str:
            threats.append("Possible XSS")
        if "../" in payload_str:
            threats.append("Path Traversal")

        status = VerdictStatus.APPROVED
        risk_level = Severity.LOW
        score = 0.0  # Low risk
        explanation = "No blocking risks detected."

        if threats:
            status = VerdictStatus.REJECTED
            risk_level = Severity.CRITICAL
            score = 10.0
            explanation = f"Critical threats detected: {', '.join(threats)}"

        return BrakesVerdict(
            score=score,
            status=status,
            threats_detected=threats,
            compliance_violations=[],
            risk_level=risk_level,
            explanation=explanation,
        )
