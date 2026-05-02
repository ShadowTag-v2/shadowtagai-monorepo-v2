import os
import sys

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure libs path is discoverable for swarm integration later
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from routers import agents
from routers.auth import verify_activeshield_jwt

app = FastAPI(title="ShadowTag AI Arbiter", version="4.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:3000,https://counselconduit-767252945109.us-central1.run.app,https://shadowtagai.com",
    ).split(","),
    allow_credentials=True,
    allow_methods=os.environ.get("CORS_METHODS", "GET,POST,PUT,DELETE,OPTIONS,PATCH").split(","),
    allow_headers=os.environ.get("CORS_HEADERS", "Content-Type,Authorization,X-Requested-With").split(","),
)


app.include_router(
    agents.router,
    prefix="/api/v1/agents",
    dependencies=[Depends(verify_activeshield_jwt)],
)


@app.get("/health")
async def health_check():
    return {"status": "alive", "engine": "FastAPI arbiter online"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
