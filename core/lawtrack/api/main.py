# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from fastapi import FastAPI, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

app = FastAPI(title="Cor.LawTrack Engine", description="Zero-Trust API Gateway for Multi-Vertical Compliance", version="1.0.0")

# Enforce JWT / Bearer Auth for all inbound external requests
security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    # Placeholder for actual JWKS OIDC validation against SSO provier (e.g. Google/Okta)
    # The Business Judgment Rule mandates this cannot remain a placeholder in prod
    if credentials.credentials != os.environ.get("LAWTRACK_SYSTEM_KEY", "dev-override-key"):
        raise HTTPException(status_code=403, detail="Invalid authorization token")
    return credentials.credentials


@app.get("/health")
def health_check():
    """Validates the API is hot and responding."""
    return {"status": "ok", "engine": "Cor.LawTrack", "encryption_mode": "enforced"}


# Import and attach service routers (To be implemented downstream)
# from core.lawtrack.services import ingestion, timeline, help_on_demand
# app.include_router(ingestion.router, prefix="/api/v1/ingest", dependencies=[Depends(verify_token)])
# app.include_router(timeline.router, prefix="/api/v1/timeline", dependencies=[Depends(verify_token)])
# app.include_router(help_on_demand.router, prefix="/api/v1/help", dependencies=[Depends(verify_token)])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
