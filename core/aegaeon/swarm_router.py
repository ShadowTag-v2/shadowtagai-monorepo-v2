# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
core/aegaeon/swarm_router.py
7-instance Gemini Swarm Router — token-level auto-scaling (Aegaeon decode disaggregation).

Architecture:
  Instances 1-5  (Fast Path)  — extraction, PR formatting, lint checks
  Instances 6-7  (Heavy Lift) — architectural anomaly detection, escalation

All instances share a single Context Cache ID → zero redundant prefill cost.
Only the unique delta (diff / query, typically <1 000 tokens) is billed at full rate.

Usage:
  router = SwarmRouter()
  results = await router.dispatch([
      SwarmTask("format_pr", "diff: ...", tier=SwarmTier.FAST),
      SwarmTask("arch_review", "module: ...", tier=SwarmTier.HEAVY),
  ])
"""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .context_cache import AegaeonContextCache

logger = logging.getLogger("aegaeon.swarm_router")

MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite-preview")
FAST_PATH_SLOTS = 5
HEAVY_LIFT_SLOTS = 2
TOTAL_SLOTS = FAST_PATH_SLOTS + HEAVY_LIFT_SLOTS


class SwarmTier(str, Enum):
    FAST = "fast"  # instances 1-5: high-speed extraction / PR formatting
    HEAVY = "heavy"  # instances 6-7: deep architectural / security analysis


@dataclass
class SwarmTask:
    name: str
    prompt: str
    tier: SwarmTier = SwarmTier.FAST
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SwarmResult:
    task_name: str
    tier: SwarmTier
    text: str
    error: str | None = None


class SwarmRouter:
    """Routes tasks to a pooled set of gemini-3.1-flash-lite-preview instances."""

    def __init__(self, cache: AegaeonContextCache | None = None) -> None:
        try:
            from google import genai

            self._client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        except ImportError as exc:
            raise RuntimeError("Install google-genai: pip install google-genai") from exc

        self._cache = cache or AegaeonContextCache()
        self._fast_sem = asyncio.Semaphore(FAST_PATH_SLOTS)
        self._heavy_sem = asyncio.Semaphore(HEAVY_LIFT_SLOTS)

    # ── Public API ──────────────────────────────────────────────────────────

    async def dispatch(self, tasks: list[SwarmTask]) -> list[SwarmResult]:
        """Dispatch all tasks concurrently against the shared context slab."""
        cache_name = self._cache.get_or_build()
        logger.info(
            "Dispatching %d tasks (cache=%s) — %d fast / %d heavy",
            len(tasks),
            cache_name,
            sum(1 for t in tasks if t.tier == SwarmTier.FAST),
            sum(1 for t in tasks if t.tier == SwarmTier.HEAVY),
        )
        coros = [self._run_task(t, cache_name) for t in tasks]
        return list(await asyncio.gather(*coros))

    async def run_one(self, task: SwarmTask) -> SwarmResult:
        cache_name = self._cache.get_or_build()
        return await self._run_task(task, cache_name)

    # ── Private ─────────────────────────────────────────────────────────────

    async def _run_task(self, task: SwarmTask, cache_name: str) -> SwarmResult:
        sem = self._fast_sem if task.tier == SwarmTier.FAST else self._heavy_sem
        async with sem:
            return await asyncio.to_thread(self._generate, task, cache_name)

    def _generate(self, task: SwarmTask, cache_name: str) -> SwarmResult:
        try:
            from google.genai import types

            response = self._client.models.generate_content(
                model=MODEL,
                contents=task.prompt,
                config=types.GenerateContentConfig(
                    cached_content=cache_name,
                    temperature=0.2 if task.tier == SwarmTier.FAST else 0.4,
                    max_output_tokens=2048 if task.tier == SwarmTier.FAST else 4096,
                ),
            )
            text = response.text or ""
            logger.debug("[%s/%s] → %d chars", task.tier, task.name, len(text))
            return SwarmResult(task_name=task.name, tier=task.tier, text=text)
        except Exception as exc:
            logger.error("[%s/%s] failed: %s", task.tier, task.name, exc)
            return SwarmResult(task_name=task.name, tier=task.tier, text="", error=str(exc))
