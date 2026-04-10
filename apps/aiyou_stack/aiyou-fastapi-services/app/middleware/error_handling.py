"""Error handling middleware and exception handlers"""

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException
from app.utils.logger import logger


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Handle custom application exceptions

    Args:
        request: FastAPI request
        exc: Application exception

    Returns:
        JSON response with error details
    """
    logger.error(f"AppException: {exc.message}", extra={"details": exc.details})

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "details": exc.details,
                "type": exc.__class__.__name__,
            }
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handle request validation errors

    Args:
        request: FastAPI request
        exc: Validation error

    Returns:
        JSON response with validation error details
    """
    logger.warning(f"Validation error: {exc.errors()}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "message": "Validation error",
                "details": exc.errors(),
                "type": "ValidationError",
            }
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle general uncaught exceptions

    Args:
        request: FastAPI request
        exc: Exception

    Returns:
        JSON response with error details
    """
    logger.exception(f"Unhandled exception: {str(exc)}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "Internal server error",
                "details": str(exc) if logger.level == 10 else {},  # Show details in DEBUG mode
                "type": "InternalServerError",
            }
        },
    )
