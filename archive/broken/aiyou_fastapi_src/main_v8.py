# main.py — Pure Cloud Run entrypoint
import os

from fastapi import FastAPI

from src.libs.ShadowTag-v2.governance.architect_valuation import simulate_valuation
from src.libs.ShadowTag-v2.governance.judge_six_premium import JudgeSixPremium
from src.libs.ShadowTag-v2.governance.scout_intel import scout_threads

app = FastAPI()
judge = JudgeSixPremium()


@app.get("/health")
def health():
    return {
        "status": "SOVEREIGN",
        "stack": "Gemini + Cloud Run",
        "tier": "PREMIUM_EMPIRE",
    }


@app.post("/execute")
async def execute(action: str, payload: dict):
    # 1. Premium Governance Gate (Biz Judgment)
    verdict = judge.evaluate_biz_judgment(payload)
    if verdict.get("verdict") == "FAILED":
        return {"status": "DENIED", "reason": verdict}

    # 2. Routing
    if action == "valuation_sim":
        result = simulate_valuation(payload.get("scenario", "base"))
        return {"status": "EXECUTED", "result": result}

    elif action == "scout":
        result = scout_threads(payload.get("query", ""))
        return {"status": "EXECUTED", "result": result}

    else:
        # Default Gemini Action
        return {"status": "EXECUTED", "result": "Gemini processed generic action"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
