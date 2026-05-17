# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
API v1 Router
"""

from fastapi import APIRouter
from app.api.v1 import governance, adtech, content, accessibility, recommender, kpi

api_router = APIRouter()

# Include all sub-routers
api_router.include_router(governance.router, prefix="/governance", tags=["Governance"])
api_router.include_router(adtech.router, prefix="/adtech", tags=["Adtech Compliance"])
api_router.include_router(
  content.router, prefix="/content", tags=["Content Provenance"]
)
api_router.include_router(
  accessibility.router, prefix="/accessibility", tags=["Accessibility"]
)
api_router.include_router(
  recommender.router, prefix="/recommender", tags=["Recommender"]
)
api_router.include_router(kpi.router, prefix="/kpi", tags=["KPI Tracking"])
