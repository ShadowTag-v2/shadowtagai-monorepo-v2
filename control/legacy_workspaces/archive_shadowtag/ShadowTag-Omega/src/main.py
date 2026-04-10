from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.agents.manager import agent
from src.governance.api import judge

app = FastAPI()
app.mount("/", StaticFiles(directory="apps/web/public", html=True), name="ui")

@app.get("/api/agent")
def interact(q: str):
    # 1. Governance Check
    verdict = judge.evaluate(q)
    if verdict["status"] == "BLOCKED":
        return {"root_id": "error", "components": [{"id": "error", "type": "Text", "props": {"text": "BLOCKED BY JUDGE 6"}}]}

    # 2. Agent Execution
    return agent.generate(q)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
