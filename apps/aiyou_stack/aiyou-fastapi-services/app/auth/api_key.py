"""
API Key authentication.
Simple and efficient authentication using API keys in headers.
"""

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import settings

# API Key header scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str | None = Security(api_key_header)) -> str:
    """
    Verify the API key from request headers.

    Args:
        api_key: The API key from X-API-Key header

    Returns:
        The validated API key

    Raises:
        HTTPException: If API key is missing or invalid
    """
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if api_key not in settings.api_keys:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key")

    return api_key


async def get_api_key(api_key: str | None = Security(api_key_header)) -> str | None:
    """
    Get the API key from request headers (optional).

    Args:
        api_key: The API key from X-API-Key header

    Returns:
        The API key if present and valid, None otherwise
    """
    if api_key is None:
        return None

    if api_key in settings.api_keys:
        return api_key

    return None
