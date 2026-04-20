"""swarm_router.py — Aegaeon 7-Instance Gemini Swarm Router

Routes inference requests through a shared Gemini Context Cache.
Two tiers:
  - Fast Path (Semaphore 5): extraction, PR formatting, simple Q&A
  - Heavy Lift (Semaphore 2): architectural anomaly detection, escalation

All instances share one cached_content=cache_name for ~90% cost reduction (Gemini 2.5+ pricing).

Usage:
    from core.aegaeon.swarm_router import SwarmRouter
    router = SwarmRouter()
    result = await router.route("fast", "Summarize the judge6 pipeline")
"""

from __future__ import annotations

import asyncio
import logging
import os

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [SWARM] %(message)s")
logger = logging.getLogger(__name__)

# Concurrency limits
FAST_PATH_CONCURRENCY = 5
HEAVY_LIFT_CONCURRENCY = 2


class SwarmRouter:
    """Async Gemini swarm router with shared context cache.

    Args:
        cache_name: Gemini cached content resource name.
        model: Model ID for generation.
    """

    def __init__(
        self,
        cache_name: str | None = None,
        model: str = "models/gemini-3.1-flash-lite-preview",
    ):
        self._cache_name = cache_name
        self._model = model
        self._fast_sem = asyncio.Semaphore(FAST_PATH_CONCURRENCY)
        self._heavy_sem = asyncio.Semaphore(HEAVY_LIFT_CONCURRENCY)
        self._client = None

    def _get_client(self):
        """Lazy-load Gemini client."""
        if self._client is None:
            from google import genai

            api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                raise RuntimeError("No GEMINI_API_KEY or GOOGLE_API_KEY in environment")
            self._client = genai.Client(api_key=api_key)
        return self._client

    async def route(self, tier: str, prompt: str) -> str:
        """Route a prompt through the appropriate tier.

        Args:
            tier: "fast" or "heavy"
            prompt: User prompt text.

        Returns:
            Generated response text.
        """
        sem = self._fast_sem if tier == "fast" else self._heavy_sem
        tier_label = "FAST" if tier == "fast" else "HEAVY"

        async with sem:
            logger.info("[%s] Processing: %s...", tier_label, prompt[:60])
            return await asyncio.to_thread(self._generate, prompt)

    def _generate(self, prompt: str) -> str:
        """Synchronous generation call (run in thread)."""
        client = self._get_client()

        generate_kwargs: dict = {
            "model": self._model,
            "contents": prompt,
        }

        # Attach cached context if available
        if self._cache_name:
            generate_kwargs["config"] = {"cached_content": self._cache_name}

        try:
            response = client.models.generate_content(**generate_kwargs)
            return response.text
        except Exception as e:
            logger.error("Generation failed: %s", e)
            return f"[ERROR] {e}"

    async def batch_fast(self, prompts: list[str]) -> list[str]:
        """Run multiple prompts through the fast path concurrently."""
        tasks = [self.route("fast", p) for p in prompts]
        return await asyncio.gather(*tasks)

    async def batch_heavy(self, prompts: list[str]) -> list[str]:
        """Run multiple prompts through the heavy lift path."""
        tasks = [self.route("heavy", p) for p in prompts]
        return await asyncio.gather(*tasks)
