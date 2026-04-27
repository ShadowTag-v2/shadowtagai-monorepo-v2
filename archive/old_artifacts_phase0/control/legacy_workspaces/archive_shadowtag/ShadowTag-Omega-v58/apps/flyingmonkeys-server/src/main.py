from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from libs.ShadowTag-v2.agents.a2ui_agent import A2UIGenerator

app = FastAPI()
app.mount("/", StaticFiles(directory="../../apps/agent-manager-ui/public", html=True), name="ui")
generator = A2UIGenerator()


@app.get("/api/ui")
def get_ui(intent: str):
    return generator.generate(intent)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
