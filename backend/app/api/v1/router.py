# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
API v1 router combining all endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import releases, feature_flags

api_router = APIRouter(prefix="/v1")

# Include all endpoint routers
api_router.include_router(releases.router)
api_router.include_router(feature_flags.router)
