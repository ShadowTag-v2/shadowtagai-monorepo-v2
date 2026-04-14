import os

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Judge#6 Governance Engine", version="2025.3")


class RiskCheck(BaseModel):
    operation: str
    confidence: float
    vertical: str


@app.get("/")
def health_check():
    return {"status": "operational", "doctrine": "Tier 30: The Child"}


@app.post("/validate")
def validate_operation(check: RiskCheck):
    """Judge#6 Brakes Logic:
    If Confidence < 0.75 -> FREEZE
    """
    if check.confidence < 0.75:
        return {"verdict": "FREEZE", "reason": "Confidence too low (<0.75)"}

    return {"verdict": "PROCEED", "reason": "Risk acceptable"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
