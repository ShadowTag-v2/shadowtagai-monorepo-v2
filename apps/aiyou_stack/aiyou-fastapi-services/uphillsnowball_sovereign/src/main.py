import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.governance.judge_six.sentinel import JudgeSixSentinel

app = FastAPI(title="UphillSnowball Sovereign OS")
judge = JudgeSixSentinel()


class MissionRequest(BaseModel):
    query: str
    context: str = "general"


@app.post("/mission")
async def launch_mission(req: MissionRequest):
    """
    The Single Entrypoint.
    Guarded by Judge #6 and the 650-Unit Army.
    """
    # 1. Governance Gate
    verdict = judge.evaluate(req.query, req.context)

    if verdict["status"] == "BLOCKED":
        raise HTTPException(status_code=403, detail=verdict)

    # 2. Execution (Placeholder for Agent Logic)
    return {
        "status": "MISSION_GO",
        "governance_receipt": verdict,
        "payload": f"Executing: {req.query}",
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
