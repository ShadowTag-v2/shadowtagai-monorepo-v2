# apps/counselconduit/api/app_error.py
"""Centralized Error Handling — Cor.30 "Opaque Errors" Rule.

RFC 9457 (Problem Details) structured error responses.
Never expose stack traces, SQL, or system internals to clients.
"""

from __future__ import annotations

import logging
import os
import traceback
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("counselconduit.errors")

_IS_PRODUCTION = os.getenv("APP_ENV") != "development"


class AppError(Exception):
    """Application error with structured RFC 9457 response.

    Usage:
        raise AppError(401, "UNAUTHORIZED", "Session expired.")
        raise AppError(400, "VALIDATION_ERROR", "Invalid email", details={"email": "required"})
    """

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Any = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)

    def to_response(self) -> dict[str, Any]:
        """Convert to RFC 9457 Problem Details JSON."""
        body: dict[str, Any] = {
            "status": self.status_code,
            "code": self.code,
            "message": self.message,
        }
        if self.details is not None:
            body["details"] = self.details
        return body


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """FastAPI exception handler for AppError."""
    logger.warning(
        "AppError: code=%s status=%d path=%s",
        exc.code,
        exc.status_code,
        request.url.path,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_response(),
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unhandled exceptions — never expose internals.

    In development: include traceback for debugging.
    In production: generic message only. Stack trace goes to Cloud Logging.
    """
    logger.error(
        "Unhandled error: %s path=%s",
        str(exc),
        request.url.path,
        exc_info=True,
    )

    if _IS_PRODUCTION:
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "code": "INTERNAL_ERROR",
                "message": "An internal error occurred. Please try again.",
            },
        )

    # Development only — include traceback
    return JSONResponse(
        status_code=500,
        content={
            "status": 500,
            "code": "INTERNAL_ERROR",
            "message": str(exc),
            "traceback": traceback.format_exc(),
        },
    )
