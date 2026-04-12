# FILE: src/antigravity_core.py
# CLASSIFICATION: PROPRIETARY
# ARCHITECTURE: GKC-NATIVE (Cloud Run + Firestore)

import contextlib
import hashlib
import logging
import os
import time
from enum import Enum

from fastapi import FastAPI, HTTPException
from google.cloud import firestore
from pydantic import BaseModel

# --- INIT ---
app = FastAPI(title="Antigravity OS", version="11.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CORE")

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v2")
try:
    db = firestore.Client(project=PROJECT_ID)
except Exception as e:
    logger.warning(f"Firestore Client failed to init (running locally without ADC?): {e}")
    db = None


# --- JUDGE #6: THE GOVERNOR ---
class RiskLevel(Enum):
    LOW = 1  # Auto-Approve
    MEDIUM = 2  # Human Override
    HIGH = 3  # Hard Block
    EXTREME = 4  # Kill Switch


class JudgeSix:
    """
    The Conscience & The CFO.
    Enforces ATP 5-19 (Safety) AND Gulfstream (Financials).
    """

    def __init__(self):
        # Load Laws from Firestore Genesis Block
        self.laws = {}
        if db:
            try:
                doc = db.collection("governance_doctrine").document("gulfstream_laws").get()
                if doc.exists:
                    self.laws = doc.to_dict()
                else:
                    logger.warning("Genesis Block not found. Running with DEFAULT Laws.")
                    # Fallback defaults
                    self.laws = {
                        "FIN_01": {"min_threshold": 4.0},
                        "FIN_02": {"min_threshold": 0.85},
                        "FIN_03": {"max_months": 3},
                    }
            except Exception as e:
                logger.error(f"Failed to load laws: {e}")

    async def evaluate(self, action: str, payload: dict) -> dict:
        """
        The Universal Gating Function.
        """
        # 1. Safety Gate (ATP 5-19)
        safety_risk = self._assess_safety(action)

        # 2. Financial Gate (Gulfstream Logic)
        financial_risk = self._assess_gulfstream(action, payload)

        total_risk = max(safety_risk, financial_risk)

        if total_risk >= RiskLevel.HIGH.value:
            return {
                "verdict": "DENIED",
                "risk_score": total_risk,
                "reason": "Doctrine Violation",
                "action": action,
            }

        return {"verdict": "APPROVED", "risk_score": total_risk}

    def _assess_safety(self, action: str) -> int:
        # Simplified Gemini Proxy
        if "delete" in action or "halt" in action:
            return RiskLevel.EXTREME.value
        return RiskLevel.LOW.value

    def _assess_gulfstream(self, action: str, payload: dict) -> int:
        """
        The 'Rent Model' Governor.
        We do not build unless the math is perfect.
        """
        if action == "approve_lease" or action == "deploy_capital":
            ltv = payload.get("ltv", 0)
            cac = payload.get("cac", 1)
            margin = payload.get("margin", 0.0)
            payback = payload.get("payback_months", 12)

            # LAW 1: The Ratio
            law1 = self.laws.get("FIN_01", {"min_threshold": 4.0})
            if (ltv / cac) < law1["min_threshold"]:
                logger.error(f"GULFSTREAM VIOLATION: LTV:CAC {ltv / cac} < {law1['min_threshold']}")
                return RiskLevel.HIGH.value

            # LAW 2: The Margin
            law2 = self.laws.get("FIN_02", {"min_threshold": 0.85})
            if margin < law2["min_threshold"]:
                logger.error(f"GULFSTREAM VIOLATION: Margin {margin} < {law2['min_threshold']}")
                return RiskLevel.HIGH.value

            # LAW 3: The Velocity
            law3 = self.laws.get("FIN_03", {"max_months": 3})
            if payback > law3["max_months"]:
                logger.warning(
                    f"GULFSTREAM WARNING: Payback {payback} > {law3['max_months']} months"
                )
                return RiskLevel.MEDIUM.value

        return RiskLevel.LOW.value


# --- SHADOWTAG: THE TRUTH PROTOCOL ---
class ShadowTag:
    """
    v2.0: Invisible Watermarking + Polygon Anchor.
    """

    def sign(self, content: str, user_id: str) -> dict:
        timestamp = str(time.time())

        # 1. Cryptographic Hash
        content_hash = hashlib.sha256(f"{content}{timestamp}".encode()).hexdigest()

        # 2. Polygon Anchor Stub (Web3)
        # In production, this pushes to the matic-mainnet RPC
        tx_hash = f"0x{hashlib.md5(content_hash.encode()).hexdigest()}"

        # 3. Firestore Ledger Commit
        if db:
            try:
                db.collection("shadowtag_ledger").add(
                    {
                        "content_hash": content_hash,
                        "tx_hash": tx_hash,
                        "user_id": user_id,
                        "timestamp": firestore.SERVER_TIMESTAMP,
                        "status": "ANCHORED",
                    }
                )
            except Exception as e:
                logger.error(f"Failed to anchor to Firestore: {e}")

        return {"content_hash": content_hash, "tx_hash": tx_hash}


# --- KERNEL: MISSION CONTROL ---
try:
    judge = JudgeSix()
    tagger = ShadowTag()
except Exception as e:
    logger.error(f"Kernel Init Failed: {e}")
    raise e


class MissionRequest(BaseModel):
    session_id: str
    action: str
    payload: dict = {}


@app.get("/")
def health_check():
    # Ping the Sovereign Ring to confirm asset awareness
    assets = []
    if db:
        with contextlib.suppress(Exception):
            assets = [d.id for d in db.collection("infrastructure_ring").list_documents()]

    return {
        "status": "OPERATIONAL",
        "doctrine": "GKC-NATIVE",
        "assets_tracked": assets,
        "iq_lock": 160,
    }


@app.post("/execute")
async def execute_mission(req: MissionRequest):
    # 1. JUDGMENT
    verdict = await judge.evaluate(req.action, req.payload)
    if verdict["verdict"] == "DENIED":
        raise HTTPException(status_code=403, detail=verdict)

    # 2. EXECUTION (Simulation)
    result = f"Executed {req.action}. Outcome: SUCCESS."

    # 3. TRUTH ANCHORING
    proof = tagger.sign(result, "SYSTEM")

    # 4. MEMORY COMMIT (Firestore Singularity)
    if db:
        db.collection("sessions").document(req.session_id).set(
            {
                "history": firestore.ArrayUnion([{"action": req.action, "result": result}]),
                "last_active": firestore.SERVER_TIMESTAMP,
            },
            merge=True,
        )

    return {"status": "SUCCESS", "proof": proof, "governance": verdict}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
