"""API Routes - Cor.17 Architecture Endpoints"""
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Any, Optional

# Import route modules
from app.api.endpoints import orchestration, search, reasoning, safety, dataops

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    orchestration.router,
    prefix="/orchestration",
    tags=["orchestration"]
)

api_router.include_router(
    search.router,
    prefix="/search",
    tags=["search"]
)

api_router.include_router(
    reasoning.router,
    prefix="/reasoning",
    tags=["reasoning"]
)

api_router.include_router(
    safety.router,
    prefix="/safety",
    tags=["safety"]
)

api_router.include_router(
    dataops.router,
    prefix="/dataops",
    tags=["dataops"]
)
