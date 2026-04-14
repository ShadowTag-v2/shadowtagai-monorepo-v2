"""API v1 Router

Includes all API sub-routers including the ActiveShield Modular Compliance Framework (MCF).
"""

from fastapi import APIRouter

from app.api.v1 import (
    accessibility,
    adtech,
    california_ai,
    compliance,
    content,
    governance,
    kpi,
    orchestrator,
    recommender,
)

api_router = APIRouter()

# Include all sub-routers
api_router.include_router(governance.router, prefix="/governance", tags=["Governance"])
api_router.include_router(compliance.router, prefix="/compliance", tags=["Compliance MCF"])
api_router.include_router(adtech.router, prefix="/adtech", tags=["Adtech Compliance"])
api_router.include_router(content.router, prefix="/content", tags=["Content Provenance"])
api_router.include_router(accessibility.router, prefix="/accessibility", tags=["Accessibility"])
api_router.include_router(recommender.router, prefix="/recommender", tags=["Recommender"])
api_router.include_router(kpi.router, prefix="/kpi", tags=["KPI Tracking"])
api_router.include_router(orchestrator.router, prefix="/orchestrator", tags=["Orchestrator"])
api_router.include_router(
    california_ai.router, prefix="/california-ai", tags=["California AI Compliance"],
)
