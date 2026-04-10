"""
Standard API response models for consistent formatting.
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """
    Standard API response wrapper.
    Provides consistent response format across all endpoints.
    """

    success: bool = Field(default=True, description="Indicates if the request was successful")
    message: str | None = Field(default=None, description="Optional message about the response")
    data: T | None = Field(default=None, description="Response data")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {"id": 1, "name": "Example"},
            }
        }


class ErrorResponse(BaseModel):
    """
    Standard error response.
    Provides detailed error information.
    """

    success: bool = Field(default=False, description="Always false for errors")
    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Human-readable error message")
    details: Any | None = Field(default=None, description="Additional error details")
    path: str | None = Field(default=None, description="Request path where error occurred")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "ValidationError",
                "message": "Invalid input data",
                "details": {"field": "email", "issue": "Invalid email format"},
                "path": "/api/v1/users",
            }
        }


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    page: int = Field(..., description="Current page number", ge=1)
    page_size: int = Field(..., description="Items per page", ge=1, le=100)
    total_items: int = Field(..., description="Total number of items", ge=0)
    total_pages: int = Field(..., description="Total number of pages", ge=0)
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Paginated API response.
    Used for endpoints that return lists of items.
    """

    success: bool = Field(default=True, description="Indicates if the request was successful")
    message: str | None = Field(default=None, description="Optional message about the response")
    data: list[T] = Field(..., description="List of items")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Users retrieved successfully",
                "data": [{"id": 1, "name": "User 1"}, {"id": 2, "name": "User 2"}],
                "pagination": {
                    "page": 1,
                    "page_size": 10,
                    "total_items": 50,
                    "total_pages": 5,
                    "has_next": True,
                    "has_previous": False,
                },
            }
        }
