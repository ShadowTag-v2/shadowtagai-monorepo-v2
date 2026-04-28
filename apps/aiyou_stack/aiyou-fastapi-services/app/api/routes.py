# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""API Routes - Cor.17 Architecture Endpoints"""

from fastapi import APIRouter

# Import route modules
from app.api.endpoints import dataops, orchestration, reasoning, safety, search

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(orchestration.router, prefix="/orchestration", tags=["orchestration"])

api_router.include_router(search.router, prefix="/search", tags=["search"])

api_router.include_router(reasoning.router, prefix="/reasoning", tags=["reasoning"])

api_router.include_router(safety.router, prefix="/safety", tags=["safety"])

api_router.include_router(dataops.router, prefix="/dataops", tags=["dataops"])
