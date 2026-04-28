# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os

import google.auth.transport.requests
import google.oauth2.id_token
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="SeatJudge BFF", version="0.1.0")

# CONFIGURATION
# The protected Core API URL
CORE_API_URL = os.environ.get("CORE_API_URL", "https://seatjudge-api-poaakxhkkq-uc.a.run.app")


async def get_id_token(audience: str) -> str:
    """Generates a Google OIDC ID Token for the target audience
    using the metadata server (when running on Cloud Run).
    """
    try:
        auth_req = google.auth.transport.requests.Request()
        token = google.oauth2.id_token.fetch_id_token(auth_req, audience)
        return token
    except Exception as e:
        print(f"⚠️ Failed to get ID Token: {e}")
        # Fallback for local testing if needed, or re-raise
        return "mock-token-for-local"


@app.get("/")
async def serve_dashboard():
    return FileResponse("static/index.html")


@app.get("/bff/map/{venue_id}")
async def proxy_get_map(venue_id: str):
    """Proxies the GET /map/{venue_id} call to the Core API.
    Injects the OIDC Authorization header.
    """
    token = await get_id_token(CORE_API_URL)
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{CORE_API_URL}/map/{venue_id}", headers=headers)
            # Pass through the status code and JSON or error
            return JSONResponse(status_code=resp.status_code, content=resp.json())
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/bff/assess")
async def proxy_assess(request: Request):
    """Proxies the POST /assess call to the Core API.
    Injects the OIDC Authorization header.
    """
    token = await get_id_token(CORE_API_URL)
    headers = {"Authorization": f"Bearer {token}"}

    try:
        body = await request.json()
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{CORE_API_URL}/assess", json=body, headers=headers)
            return JSONResponse(status_code=resp.status_code, content=resp.json())
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# Mount static files (optional, if we have assets)
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
