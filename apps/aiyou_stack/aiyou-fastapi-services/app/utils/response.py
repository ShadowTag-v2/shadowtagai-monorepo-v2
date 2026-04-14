"""Response formatting utilities.
Makes it easy to return consistent API responses.
"""

from typing import Any, TypeVar

from app.models.response import APIResponse, ErrorResponse, PaginatedResponse, PaginationMeta

T = TypeVar("T")


def success_response(data: T | None = None, message: str | None = None) -> APIResponse[T]:
    """Create a successful API response.

    Args:
        data: Response data
        message: Optional success message

    Returns:
        APIResponse object

    """
    return APIResponse(success=True, message=message, data=data)


def error_response(
    error: str, message: str, details: Any | None = None, path: str | None = None,
) -> ErrorResponse:
    """Create an error response.

    Args:
        error: Error type or code
        message: Error message
        details: Additional error details
        path: Request path

    Returns:
        ErrorResponse object

    """
    return ErrorResponse(success=False, error=error, message=message, details=details, path=path)


def paginated_response(
    data: list[T], pagination: PaginationMeta, message: str | None = None,
) -> PaginatedResponse[T]:
    """Create a paginated API response.

    Args:
        data: List of items
        pagination: Pagination metadata
        message: Optional message

    Returns:
        PaginatedResponse object

    """
    return PaginatedResponse(success=True, message=message, data=data, pagination=pagination)
