# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# apps/counselconduit/api/middleware_ant.py
"""Ant Gate Middleware for CounselConduit.

Injects `USER_TYPE='ant'` into request state for internal Cloud Run requests.
This mimics the Claude Code architectural pattern where internal users get
differentiated observability, feature flags, and mock environments.

Flow:
    1. Middleware intercepts request.
    2. Checks for ant authentication headers or internal service accounts.
    3. Sets `request.state.user_type = 'ant'` or `'external'`.
    4. Routes can inject `request` and check `request.state.user_type`.
"""

import logging
import os
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("counselconduit.ant_gate")


class AntGateMiddleware(BaseHTTPMiddleware):
    """Middleware to inject USER_TYPE into request state."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Default to external
        request.state.user_type = "external"

        # Only process Ant Gate headers if the feature flag is enabled
        enable_ant_gate = os.getenv("ENABLE_ANT_GATE", "false").lower() in ("true", "1", "t", "y", "yes")
        if enable_ant_gate:
            # Check for Ant Gate Headers (for internal engineering tools)
            ant_header = request.headers.get("X-ShadowTag-Ant-Gate")
            if ant_header and ant_header.lower() == "true":
                request.state.user_type = "ant"
                logger.debug("Ant Gate triggered via X-ShadowTag-Ant-Gate header.")

        # Check internal service accounts or authenticated email (if decoded early)
        # Note: If auth happens in dependencies, this middleware might run before claims are verified.
        # But for Cloud Run internal M2M auth (OIDC tokens), we can check OIDC claims here if needed.
        # For now, rely on X-ShadowTag-Ant-Gate (which should ideally be validated or stripped by the load balancer for external requests).

        response = await call_next(request)

        # Optionally, we can append research blocks or hook timing blocks to the response
        # if the user is an 'ant'.
        if request.state.user_type == "ant":
            response.headers["X-Ant-Gate-Active"] = "true"

        return response
