"""Shared HTTP utilities for Monke test steps."""

import os
from typing import Any

import httpx


def get_headers() -> dict[str, str]:
    """Get standard HTTP headers for Airweave API requests."""
    headers = {"Content-Type": "application/json"}
    api_key = os.getenv("AIRWEAVE_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key
    return headers


def get_base_url() -> str:
    """Get the Airweave API base URL."""
    return os.getenv("AIRWEAVE_API_URL", "http://localhost:8001").rstrip("/")


def http_get(path: str, timeout: float = 30.0) -> Any:
    """Perform HTTP GET request to Airweave API."""
    resp = httpx.get(f"{get_base_url()}{path}", headers=get_headers(), timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def http_post(
    path: str,
    json: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    timeout: float = 30.0,
) -> Any:
    """Perform HTTP POST request to Airweave API."""
    resp = httpx.post(
        f"{get_base_url()}{path}",
        headers=get_headers(),
        json=json,
        params=params,
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()


def http_delete(path: str, timeout: float = 30.0) -> httpx.Response:
    """Perform HTTP DELETE request to Airweave API."""
    return httpx.delete(
        f"{get_base_url()}{path}",
        headers=get_headers(),
        timeout=timeout,
    )
