# apps/counselconduit/api/provider_health.py
"""Item 6: Per-provider health endpoint.

Exposes /health/providers with per-model-provider latency and status.
Used by monitoring dashboards and canary analysis.
"""

from __future__ import annotations

import asyncio
import os
import time

import structlog
from fastapi import APIRouter

logger = structlog.get_logger("counselconduit.provider_health")

router = APIRouter(tags=["Health"])

# Provider endpoints to probe
_PROVIDERS: dict[str, dict[str, str]] = {
    "gemini": {
        "name": "Google Gemini",
        "probe": "https://generativelanguage.googleapis.com/",
        "expected": "models",
    },
    "anthropic": {
        "name": "Anthropic Claude",
        "probe": "https://api.anthropic.com/v1/messages",
        "expected": "authentication",
    },
    "openai": {
        "name": "OpenAI GPT",
        "probe": "https://api.openai.com/v1/models",
        "expected": "authentication",
    },
}


async def _probe_provider(name: str, url: str) -> dict[str, str | float | bool]:
    """Probe a single provider endpoint."""
    try:
        import httpx

        start = time.monotonic()
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
            latency_ms = round((time.monotonic() - start) * 1000, 1)
            return {
                "provider": name,
                "status": "reachable",
                "http_code": resp.status_code,
                "latency_ms": latency_ms,
                "healthy": resp.status_code < 500,
            }
    except Exception as e:
        return {
            "provider": name,
            "status": "unreachable",
            "error": type(e).__name__,
            "latency_ms": -1,
            "healthy": False,
        }


@router.get("/health/providers")
async def provider_health():
    """Per-provider health check with latency metrics.

    Returns status for each LLM provider (Gemini, Claude, OpenAI).
    Does NOT send authenticated requests — only probes endpoint reachability.
    """
    tasks = [
        _probe_provider(info["name"], info["probe"])
        for info in _PROVIDERS.values()
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    providers = []
    all_healthy = True
    for result in results:
        if isinstance(result, Exception):
            providers.append({"provider": "unknown", "status": "error", "error": str(result)})
            all_healthy = False
        else:
            providers.append(result)
            if not result.get("healthy"):
                all_healthy = False

    return {
        "status": "healthy" if all_healthy else "degraded",
        "timestamp": time.time(),
        "providers": providers,
        "model_routing": os.getenv("DEFAULT_MODEL", "gemini-2.0-flash"),
    }
