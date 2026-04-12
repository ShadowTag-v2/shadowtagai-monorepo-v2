"""Custom exceptions for the application"""

from typing import Any


class AppException(Exception):
    """Base exception for application errors"""

    def __init__(self, message: str, status_code: int = 500, details: dict[str, Any] | None = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AgentException(AppException):
    """Exception raised when Claude Agent SDK encounters an error"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message, status_code=500, details=details)


class ValidationException(AppException):
    """Exception raised for validation errors"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message, status_code=400, details=details)


class RateLimitException(AppException):
    """Exception raised when rate limit is exceeded"""

    def __init__(self, message: str = "Rate limit exceeded", details: dict[str, Any] | None = None):
        super().__init__(message, status_code=429, details=details)
