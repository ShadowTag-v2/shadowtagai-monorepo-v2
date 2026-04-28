# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""API v1 Router - Aggregates all v1 endpoints"""

from fastapi import APIRouter

from app.api.v1.endpoints import compliance

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(compliance.router)

# Add more routers as needed
# api_router.include_router(users.router)
# api_router.include_router(analytics.router)
