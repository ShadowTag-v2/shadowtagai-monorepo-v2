# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Pagination utilities for list endpoints."""

from math import ceil
from typing import TypeVar

from app.models.response import PaginationMeta

T = TypeVar("T")


def paginate(items: list[T], page: int = 1, page_size: int = 10) -> tuple[list[T], PaginationMeta]:
    """Paginate a list of items.

    Args:
        items: List of items to paginate
        page: Current page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple of (paginated_items, pagination_meta)

    """
    total_items = len(items)
    ceil(total_items / page_size) if page_size > 0 else 0

    # Calculate slice indices
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    # Get paginated items
    paginated_items = items[start_idx:end_idx]

    # Create pagination metadata
    pagination_meta = create_pagination_meta(
        page=page,
        page_size=page_size,
        total_items=total_items,
    )

    return paginated_items, pagination_meta


def create_pagination_meta(page: int, page_size: int, total_items: int) -> PaginationMeta:
    """Create pagination metadata.

    Args:
        page: Current page number
        page_size: Items per page
        total_items: Total number of items

    Returns:
        PaginationMeta object

    """
    total_pages = ceil(total_items / page_size) if page_size > 0 else 0

    return PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
    )
