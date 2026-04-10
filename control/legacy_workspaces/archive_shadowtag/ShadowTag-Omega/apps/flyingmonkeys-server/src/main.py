import sys, os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Imports
sys.path.append(os.path.abspath("../../../libs"))
from manager_routes import router as manager_router
from router_routes import api_router as router_dispatcher
from ui_routes import router as ui_router

app = FastAPI()

# Mount Routes
app.include_router(manager_router, prefix="/manager")
app.include_router(router_dispatcher, prefix="/api")
app.include_router(ui_router, prefix="/ui")

@app.get("/health")
def health_check():
    return {"status": "active", "server": "n-autoresearch/Kosmos/BioAgentss"}


# UI
if os.path.exists("../../apps/agent-manager-ui/dist"):
    app.mount("/", StaticFiles(directory="../../apps/agent-manager-ui/dist", html=True), name="ui")
else:
    print("UI directory not found, skipping mount.")

