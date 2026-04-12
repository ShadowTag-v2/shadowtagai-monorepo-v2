from datetime import datetime

from pydantic import BaseModel, Field

# Ultrathink Integration
from src.ultrathink.agents.roster import AgentProfile, StandardRoster
from src.ultrathink.skills.patterns import ChainOfThought


class JudgeRequest(BaseModel):
    request_id: str
    intent_nl: str
    metrics: dict[str, float] = Field(default_factory=dict)
    context: dict[str, str] = Field(default_factory=dict)


class JudgeRuling(BaseModel):
    ruling_id: str
    timestamp: datetime
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    confidence: float
    decision_memo: str
    controls_required: list[str]
    audit_trail: list[str]


class PureJudgeEngine:
    """
    FinJudge Pure Judge (v0.2) powered by Ultrathink.
    Uses 'CRITIC' agent and CoT reasoning to classify risk.
    """

    def __init__(self):
        # Load the Persona
        self.judge_persona: AgentProfile = StandardRoster.get_critic()

        # Load Skills
        self.cot = ChainOfThought(trigger_phrase="Analyze the financial risk step by step.")

    async def evaluate(self, request: JudgeRequest) -> JudgeRuling:
        # 1. Expand Intent with CoT
        reasoning_prompt = self.cot.apply(
            f"Intent: {request.intent_nl}\nMetrics: {request.metrics}\nContext: {request.context}"
        )

        # 2. Mock Agent Reasoning (Simulating LLM Call)
        # In a real system, we'd pass `reasoning_prompt` to Gemini using `self.judge_persona`.
        # For v0.2 integration, we simulate the output logic based on metrics.

        # Simple deterministic logic for demo purposes:
        # If 'burn_rate' or 'risk' metric is high, trigger higher risk levels.
        risk_score = request.metrics.get("risk_score", 0.0)
        burn_rate = request.metrics.get("burn_rate", 0.0)

        audit_log = [f"Agent {self.judge_persona.name} activation"]
        audit_log.append(f"Applied CoT: {reasoning_prompt[:50]}...")

        if risk_score > 0.8 or burn_rate > 500000:
            risk_level = "CRITICAL"
            controls = ["Board Approval Required", "CFO Sign-off"]
            memo = (
                f"CRITICAL RISK DETECTED. {self.judge_persona.name} flags high burn/risk metrics."
            )
        elif risk_score > 0.5:
            risk_level = "HIGH"
            controls = ["CFO Sign-off"]
            memo = "High risk detected. Proceed with caution."
        elif risk_score > 0.2:
            risk_level = "MEDIUM"
            controls = ["Manager Approval"]
            memo = "Moderate risk. Standard controls apply."
        else:
            risk_level = "LOW"
            controls = []
            memo = "Low risk. Approved for execution."

        return JudgeRuling(
            ruling_id=request.request_id,
            timestamp=datetime.now(),
            risk_level=risk_level,
            confidence=0.95,
            decision_memo=memo,
            controls_required=controls,
            audit_trail=audit_log,
        )
