"""Purpose Validator - JR Engine Component 1

Validates the PURPOSE of an action:
- What is this action trying to accomplish?
- Does it align with business objectives?
- Is there a clear mission statement?
- What is the value proposition?
"""

from ..models import Action, PurposeVerdict, VerdictStatus


class PurposeValidator:
    """Validates the PURPOSE dimension of an action"""

    def validate(self, action: Action) -> PurposeVerdict:
        # Heuristic validation for prototype
        mission_keywords = ["revenue", "sovereign", "intelligence", "hardening", "deployment"]
        payload_str = str(action.payload).lower()

        matches = [k for k in mission_keywords if k in payload_str]
        alignment_score = min(10.0, len(matches) * 2.5) if matches else 2.0

        status = VerdictStatus.APPROVED
        explanation = f"Purpose aligns with {len(matches)} mission keywords."
        if alignment_score < 4.0:
            status = VerdictStatus.FLAGGED
            explanation = "Weak purpose alignment."

        prohibited = ["bypass", "exploit", "leak"]
        if any(p in payload_str for p in prohibited):
            status = VerdictStatus.REJECTED
            explanation = "Prohibited purpose detected."
            alignment_score = 0.0

        return PurposeVerdict(
            score=alignment_score,
            status=status,
            alignment_score=alignment_score,
            clarity_score=8.0,  # Placeholder
            mission_fit=alignment_score >= 5.0,
            explanation=explanation,
        )
