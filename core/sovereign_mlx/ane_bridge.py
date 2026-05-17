# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
core/sovereign_mlx/ane_bridge.py
Sovereign MLX Protocol — Phase 2: Token-level dispatch on Apple Silicon.

Mapping:
  Aegaeon Multi-Model Pool     →  single llama.cpp instance, Unified Memory
  Decode disaggregation        →  async concurrent completions, shared KV-cache pointer
  Fast Path (instances 1-5)    →  FAST tier: extraction, lint, PR format
  Heavy Lift (instances 6-7)   →  HEAVY tier: arch anomaly, security, escalation

The model weights are loaded ONCE into Unified Memory.
Every request passes --prompt-cache pointing to the pre-built KV-cache slab,
so Metal skips the expensive prefill phase and computes only the delta.

Usage:
  bridge = ANEBridge()
  results = await bridge.dispatch([
      ANETask("lint_check", "diff: ...", tier=ANETier.FAST),
      ANETask("security_audit", "module: ...", tier=ANETier.HEAVY),
  ])
"""

from __future__ import annotations

import asyncio
import logging
import os
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from .kv_cache_slab import KVCacheSlab

logger = logging.getLogger("sovereign_mlx.ane_bridge")

LLAMA_CLI = os.environ.get("LLAMA_CLI_BIN", "llama-cli")
MODEL_PATH = os.environ.get(
  "LOCAL_MODEL_PATH",
  str(__import__("pathlib").Path.home() / "models" / "gemma-2-9b-it.Q4_K_M.gguf"),
)
FAST_CONCURRENCY = 5
HEAVY_CONCURRENCY = 2


class ANETier(str, Enum):
  FAST = "fast"
  HEAVY = "heavy"


@dataclass
class ANETask:
  name: str
  prompt: str
  tier: ANETier = ANETier.FAST
  max_tokens: int = 512
  metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ANEResult:
  task_name: str
  tier: ANETier
  text: str
  latency_ms: float = 0.0
  error: str | None = None


class ANEBridge:
  """
  Async token-level dispatcher for local llama.cpp inference on M1 Max.
  Loads model weights once; routes all requests through shared KV-cache slab.
  """

  def __init__(self, slab: KVCacheSlab | None = None) -> None:
    self._slab = slab or KVCacheSlab()
    self._fast_sem = asyncio.Semaphore(FAST_CONCURRENCY)
    self._heavy_sem = asyncio.Semaphore(HEAVY_CONCURRENCY)

  # ── Public API ──────────────────────────────────────────────────────────

  async def dispatch(self, tasks: list[ANETask]) -> list[ANEResult]:
    """Dispatch all tasks concurrently, all sharing the same slab."""
    slab_path = self._slab.get_slab_path()
    if slab_path is None:
      logger.info("Slab not found — building now (first-run, takes ~60s)...")
      slab_path = self._slab.build()

    logger.info(
      "ANE dispatch: %d tasks (fast=%d heavy=%d), slab=%s",
      len(tasks),
      sum(1 for t in tasks if t.tier == ANETier.FAST),
      sum(1 for t in tasks if t.tier == ANETier.HEAVY),
      slab_path.name,
    )
    coros = [self._run_task(t, slab_path) for t in tasks]
    return list(await asyncio.gather(*coros))

  async def run_one(self, task: ANETask) -> ANEResult:
    slab_path = self._slab.get_slab_path() or self._slab.build()
    return await self._run_task(task, slab_path)

  # ── Private ─────────────────────────────────────────────────────────────

  async def _run_task(self, task: ANETask, slab_path: Path) -> ANEResult:
    sem = self._fast_sem if task.tier == ANETier.FAST else self._heavy_sem
    async with sem:
      return await asyncio.to_thread(self._infer, task, slab_path)

  def _infer(self, task: ANETask, slab_path: Path) -> ANEResult:
    if not shutil.which(LLAMA_CLI):
      return ANEResult(
        task_name=task.name,
        tier=task.tier,
        text="",
        error=(
          f"llama-cli not found at '{LLAMA_CLI}'. Install llama.cpp: cmake -DLLAMA_METAL=on .."
        ),
      )

    cmd = [
      LLAMA_CLI,
      "-m",
      MODEL_PATH,
      "--prompt-cache",
      str(slab_path),
      "--prompt-cache-ro",  # read-only — slab shared across all tasks
      "-ngl",
      "99",  # offload all layers to Metal
      "--no-mmap",
      "-n",
      str(task.max_tokens),
      "-p",
      task.prompt[:8_000],
      "--log-disable",
      "--simple-io",
    ]

    t0 = time.time()
    try:
      result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
      )
      latency_ms = (time.time() - t0) * 1000

      if result.returncode != 0:
        return ANEResult(
          task_name=task.name,
          tier=task.tier,
          text="",
          latency_ms=latency_ms,
          error=result.stderr[:1000],
        )

      output = result.stdout.strip()
      logger.debug(
        "[%s/%s] %.0fms → %d chars", task.tier, task.name, latency_ms, len(output)
      )
      return ANEResult(
        task_name=task.name,
        tier=task.tier,
        text=output,
        latency_ms=latency_ms,
      )
    except subprocess.TimeoutExpired:
      return ANEResult(
        task_name=task.name,
        tier=task.tier,
        text="",
        latency_ms=(time.time() - t0) * 1000,
        error="llama-cli timed out after 120s",
      )
