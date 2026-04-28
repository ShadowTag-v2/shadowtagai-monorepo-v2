# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""API v1 Router

Aggregates all v1 endpoints
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, health, subscriptions, users

api_router = APIRouter()

# Health checks (no prefix, no auth)
api_router.include_router(health.router, tags=["health"])

# Authentication (no auth required)
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Users (auth required)
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Subscriptions (auth required)
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
