# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Custom exception classes for accessible error handling.

All exceptions follow WCAG 2.1 principles with:
- Clear, user-friendly messages
- Machine-readable error codes
- Semantic HTTP status codes
- Structured error details
"""

from typing import Any


class APIException(Exception):
    """
    Base API exception with semantic structure.

    All API errors inherit from this class to ensure consistent error handling.
    """

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ):
        """
        Initialize API exception.

        Args:
            status_code: HTTP status code (e.g., 400, 404, 500)
            code: Machine-readable error code (e.g., "VALIDATION_ERROR")
            message: User-friendly error message in plain language
            details: Additional error details (field-specific errors, suggestions)
            headers: Optional HTTP headers to include in response
        """
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}
        self.headers = headers
        super().__init__(message)


class ValidationError(APIException):
    """
    400 Bad Request - Invalid input data.

    Used when client sends data that doesn't meet validation requirements.
    """

    def __init__(
        self,
        message: str = "Invalid input data provided",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            status_code=400,
            code="VALIDATION_ERROR",
            message=message,
            details=details,
        )


class UnauthorizedError(APIException):
    """
    401 Unauthorized - Authentication required.

    Used when client needs to authenticate before accessing resource.
    """

    def __init__(
        self,
        message: str = "Authentication is required to access this resource",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            status_code=401,
            code="UNAUTHORIZED",
            message=message,
            details=details,
        )


class ForbiddenError(APIException):
    """
    403 Forbidden - Insufficient permissions.

    Used when authenticated client lacks permission for requested action.
    """

    def __init__(
        self,
        message: str = "You do not have permission to access this resource",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            status_code=403,
            code="FORBIDDEN",
            message=message,
            details=details,
        )


class NotFoundError(APIException):
    """
    404 Not Found - Resource doesn't exist.

    Used when requested resource cannot be found.
    """

    def __init__(
        self,
        message: str = "The requested resource was not found",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            status_code=404,
            code="NOT_FOUND",
            message=message,
            details=details,
        )


class ConflictError(APIException):
    """
    409 Conflict - Resource conflict.

    Used when request conflicts with current state (e.g., duplicate email).
    """

    def __init__(
        self,
        message: str = "The request conflicts with existing data",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            status_code=409,
            code="CONFLICT",
            message=message,
            details=details,
        )


class InternalError(APIException):
    """
    500 Internal Server Error - Server fault.

    Used for unexpected server errors. Details should not expose sensitive info.
    """

    def __init__(
        self,
        message: str = "An unexpected error occurred. Please try again later",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            status_code=500,
            code="INTERNAL_ERROR",
            message=message,
            details=details,
        )
