# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from fastapi import FastAPI

from .calendar import google_sync
from .ceo_track import prodding_engine
from .config import settings
from .ingestion import webhooks
from .parsing import gemini_parser
from .rules import rules_engine

app = FastAPI(title="LegalTrack + CEOTrack", version="1.0.0")

# --- Ingestion Webhooks (PubSub / Direct) ---
app.include_router(webhooks.router, prefix="/api/v1/ingestion", tags=["Ingestion"])

# --- Parsing via Vertex AI (Gemini) ---
app.include_router(gemini_parser.router, prefix="/api/v1/parse", tags=["Parsing"])

# --- Rules Engine ---
app.include_router(rules_engine.router, prefix="/api/v1/rules", tags=["Rules"])

# --- Calendar Sync ---
app.include_router(google_sync.router, prefix="/api/v1/calendar", tags=["Calendar"])

# --- CEOTrack Orchestrator ---
app.include_router(prodding_engine.router, prefix="/api/v1/ceotrack", tags=["CEOTrack"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT, "systems_active": 12}
