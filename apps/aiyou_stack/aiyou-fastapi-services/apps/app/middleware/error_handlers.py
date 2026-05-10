"""Error handling middleware for consistent, accessible error responses.

All errors are transformed into a standard format following WCAG 2.1 principles:
- Clear, user-friendly messages
- Machine-readable error codes
- Consistent structure
- Request tracing
"""

import logging
from datetime import datetime

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from app.utils.errors import APIException

logger = logging.getLogger(__name__)


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Handle custom API exceptions.

    Args:
        request: Incoming request
        exc: APIException instance

    Returns:
        JSONResponse with standardized error format

    """
    request_id = getattr(request.state, "request_id", "unknown")

    error_response = {
        "status": "error",
        "code": exc.code,
        "message": exc.message,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "request_id": request_id,
        "details": exc.details,
    }

    logger.warning(
        f"API Exception | {request_id} | {exc.code} | {exc.message}",
        extra={
            "request_id": request_id,
            "error_code": exc.code,
            "status_code": exc.status_code,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response,
        headers=exc.headers,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError | PydanticValidationError,
) -> JSONResponse:
    """Handle Pydantic validation errors with user-friendly messages.

    Args:
        request: Incoming request
        exc: Validation error from Pydantic

    Returns:
        JSONResponse with standardized error format

    """
    request_id = getattr(request.state, "request_id", "unknown")

    # Transform Pydantic errors into user-friendly format
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append(
            {
                "field": field,
                "message": error["msg"],
                "type": error["type"],
            },
        )

    error_response = {
        "status": "error",
        "code": "VALIDATION_ERROR",
        "message": "Invalid input data. Please check the errors below and try again.",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "request_id": request_id,
        "details": {
            "errors": errors,
            "error_count": len(errors),
        },
    }

    logger.warning(
        f"Validation Error | {request_id} | {len(errors)} field(s)",
        extra={"request_id": request_id, "error_count": len(errors)},
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response,
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions.

    Args:
        request: Incoming request
        exc: Any unhandled exception

    Returns:
        JSONResponse with standardized error format (no sensitive details)

    """
    request_id = getattr(request.state, "request_id", "unknown")

    # Log the full exception for debugging (but don't expose to client)
    logger.error(
        f"Unhandled Exception | {request_id} | {exc!s}",
        extra={"request_id": request_id},
        exc_info=True,
    )

    error_response = {
        "status": "error",
        "code": "INTERNAL_ERROR",
        "message": "An unexpected error occurred. Please try again later.",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "request_id": request_id,
        "details": {"support_message": f"Please contact support with request ID: {request_id}"},
    }

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response,
    )
