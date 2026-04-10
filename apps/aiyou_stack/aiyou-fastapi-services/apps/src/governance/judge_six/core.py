import hashlib
import time
import uuid
from enum import Enum, StrEnum

from pydantic import BaseModel


class RiskTier(StrEnum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    ORANGE = "ORANGE"
    RED = "RED"


class Decision(BaseModel):
    status: str
    authority: str
    proof_hash: str


class JudgeSixPayload(BaseModel):
    judge_id: str = "J6-VER-2.0"
    transaction_id: str
    timestamp: str
    context: dict[str, str]
    decision: Decision


class JudgeSixEngine:
    def __init__(self):
        self.name = "Justitia Kernel"

    def evaluate_transaction(self, context_str: str, prob: int, sev: int) -> str:
        # Simple Matrix Logic: Score = Prob + Sev
        score = prob + sev
        if score <= 3:
            tier = RiskTier.RED
        elif score <= 5:
            tier = RiskTier.ORANGE
        elif score <= 7:
            tier = RiskTier.YELLOW
        else:
            tier = RiskTier.GREEN

        status = "APPROVED" if tier != RiskTier.RED else "BLOCKED"
        authority = "AUTO" if tier == RiskTier.GREEN else "HUMAN_OVERRIDE"

        proof = (
            f"sha256:{hashlib.sha256(f'{context_str}:{status}:{time.time()}'.encode()).hexdigest()}"
        )

        receipt = JudgeSixPayload(
            transaction_id=str(uuid.uuid4()),
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            context={"mett_tc": context_str, "risk_tier": tier.value},
            decision=Decision(status=status, authority=authority, proof_hash=proof),
        )
        return receipt.model_dump_json(indent=2)
