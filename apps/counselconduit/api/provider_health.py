# apps/counselconduit/api/provider_health.py
"""Item 6: Per-provider health endpoint.

Exposes /health/providers with per-model-provider latency and status.
Used by monitoring dashboards and canary analysis.
"""

from __future__ import annotations

import asyncio
import collections
import os
import statistics
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

# In-memory latency history (circular buffer, last 100 samples per provider)
_LATENCY_HISTORY: dict[str, collections.deque] = {
    name: collections.deque(maxlen=100) for name in _PROVIDERS
}


def _calculate_percentiles(values: list[float]) -> dict[str, float | None]:
    """Calculate p50, p95, p99 from a list of latency values."""
    if not values:
        return {"p50": None, "p95": None, "p99": None, "samples": 0}
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    return {
        "p50": round(sorted_vals[int(n * 0.50)], 1),
        "p95": round(sorted_vals[int(min(n * 0.95, n - 1))], 1),
        "p99": round(sorted_vals[int(min(n * 0.99, n - 1))], 1),
        "mean": round(statistics.mean(sorted_vals), 1),
        "samples": n,
    }


async def _probe_provider(key: str, name: str, url: str) -> dict[str, str | float | bool]:
    """Probe a single provider endpoint."""
    try:
        import httpx

        start = time.monotonic()
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
            latency_ms = round((time.monotonic() - start) * 1000, 1)
            # Record latency for histogram
            _LATENCY_HISTORY[key].append(latency_ms)
            return {
                "provider": name,
                "status": "reachable",
                "http_code": resp.status_code,
                "latency_ms": latency_ms,
                "healthy": resp.status_code < 500,
                "histogram": _calculate_percentiles(list(_LATENCY_HISTORY[key])),
            }
    except Exception as e:
        return {
            "provider": name,
            "status": "unreachable",
            "error": type(e).__name__,
            "latency_ms": -1,
            "healthy": False,
            "histogram": _calculate_percentiles(list(_LATENCY_HISTORY[key])),
        }


@router.get("/health/providers")
async def provider_health():
    """Per-provider health check with latency metrics and histogram.

    Returns status for each LLM provider (Gemini, Claude, OpenAI).
    Includes p50/p95/p99 latency percentiles from recent probes.
    Does NOT send authenticated requests — only probes endpoint reachability.
    """
    tasks = [
        _probe_provider(key, info["name"], info["probe"])
        for key, info in _PROVIDERS.items()
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

