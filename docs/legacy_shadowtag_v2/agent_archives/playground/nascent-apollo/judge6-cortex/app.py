# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from fastapi import FastAPI
from logic.reasoning import evaluate_verdict

app = FastAPI(title="CLAUDE_CODE_6_CORTEX", version="1.0.0")


@app.get("/")
def health_check():
    return {"status": "SOVEREIGN_ONLINE", "metabolism": "NOMINAL"}


@app.post("/judge")
def judge_command(command: dict):
    """
    The Main Entry Point for the HUD.
    """
    result = evaluate_verdict(command.get("input", ""))
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
