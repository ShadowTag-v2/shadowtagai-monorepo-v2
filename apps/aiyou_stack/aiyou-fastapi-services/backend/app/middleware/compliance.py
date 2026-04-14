"""Compliance Middleware - Enforce compliance policies
"""

import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.config import settings

logger = logging.getLogger(__name__)


class ComplianceMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce compliance policies"""

    async def dispatch(self, request: Request, call_next):
        """Process request and enforce compliance"""
        # Get user location from headers or GeoIP
        user_location = request.headers.get("cf-ipcountry")  # Cloudflare header
        if not user_location:
            user_location = request.headers.get("x-country-code")

        # Check if GDPR applies
        gdpr_countries = [
            "AT",
            "BE",
            "BG",
            "HR",
            "CY",
            "CZ",
            "DK",
            "EE",
            "FI",
            "FR",
            "DE",
            "GR",
            "HU",
            "IE",
            "IT",
            "LV",
            "LT",
            "LU",
            "MT",
            "NL",
            "PL",
            "PT",
            "RO",
            "SK",
            "SI",
            "ES",
            "SE",
            "GB",
        ]

        gdpr_applies = user_location in gdpr_countries if user_location else False
        ccpa_applies = user_location == "US"  # Simplified - should check state

        # Store in request state for use in endpoints
        request.state.gdpr_applies = gdpr_applies
        request.state.ccpa_applies = ccpa_applies
        request.state.user_location = user_location

        # Check cookie consent for GDPR users
        if settings.COOKIE_CONSENT_REQUIRED and gdpr_applies:
            cookie_consent = request.cookies.get("cookie_consent")

            # Allow certain paths without consent
            allowed_paths = ["/health", "/api/docs", "/api/v1/compliance/consent"]

            if not cookie_consent and request.url.path not in allowed_paths:
                logger.warning(
                    f"Request without cookie consent from GDPR region: {request.url.path}",
                )
                # In production, you might want to enforce this more strictly
                # For now, we just log it

        # Process request
        response = await call_next(request)

        # Add compliance headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Add privacy headers
        if gdpr_applies:
            response.headers["X-GDPR-Applies"] = "true"
        if ccpa_applies:
            response.headers["X-CCPA-Applies"] = "true"

        return response
