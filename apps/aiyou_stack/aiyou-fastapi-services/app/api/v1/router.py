# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Main API v1 router"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, integrations, webhooks

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

api_router.include_router(integrations.router, prefix="/integrations", tags=["Integrations"])

api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
