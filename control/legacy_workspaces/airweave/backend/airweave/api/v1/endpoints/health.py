# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Health check endpoints."""

from airweave.api.router import TrailingSlashRouter

router = TrailingSlashRouter()


@router.get("")
async def health_check() -> dict[str, str]:
    """Check if the API is healthy.

    Returns:
    --------
        dict: A dictionary containing the status of the API.
    """
    return {"status": "healthy"}
