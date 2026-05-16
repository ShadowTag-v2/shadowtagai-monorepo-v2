# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
core/sovereign_mlx/kv_cache_slab.py
Sovereign MLX Protocol — Phase 1: Disaggregate Prefill on Apple Silicon.

Mapping:
  Aegaeon "VRAM Slab"   →  llama.cpp KV-cache .bin on Unified Memory
  GPU VRAM pooling       →  M1 Max Unified Memory (CPU / Metal / ANE share same pool)

Workflow:
  1. Collect .beads grounding library text (CLAUDE.md, rulesets, judge6 context)
  2. Run `llama-server --prompt-cache` to pre-evaluate KV tensors once
  3. Export slab to data/sovereign_mlx/kv_cache_slab.bin
  4. ANEBridge passes --prompt-cache path to every subsequent request (skip prefill)

Trigger:
  - Called by monorepo post-merge hook or launchd when .beads update
  - Also callable manually: python -m core.sovereign_mlx.kv_cache_slab --build
"""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import subprocess
import time
from pathlib import Path

logger = logging.getLogger("sovereign_mlx.kv_cache_slab")

REPO_ROOT = Path(__file__).parent.parent.parent
SLAB_DIR = REPO_ROOT / "data" / "sovereign_mlx"
SLAB_PATH = SLAB_DIR / "kv_cache_slab.bin"
SLAB_PROMPT_PATH = SLAB_DIR / "slab_prompt.txt"
SLAB_STATE_PATH = SLAB_DIR / "slab_state.json"

# llama.cpp server binary — override via env
LLAMA_SERVER = os.environ.get("LLAMA_SERVER_BIN", "llama-server")
MODEL_PATH = os.environ.get(
  "LOCAL_MODEL_PATH",
  str(Path.home() / "models" / "gemma-2-9b-it.Q4_K_M.gguf"),
)

_SLAB_SOURCES: list[Path] = [
  REPO_ROOT / "CLAUDE.md",
  REPO_ROOT / "operations" / "monorepo_manifest.yaml",
  REPO_ROOT / "scripts" / "judge6.sh",
  REPO_ROOT / "data" / "ane_beads",
]


class KVCacheSlab:
  """Builds and manages the llama.cpp KV-cache slab on M1 Max Unified Memory."""

  # ── Public API ──────────────────────────────────────────────────────────

  def get_slab_path(self) -> Path | None:
    """Return the slab path if it's built and current, else None."""
    if SLAB_PATH.exists() and self._is_current():
      return SLAB_PATH
    return None

  def build(self, force: bool = False) -> Path:
    """Build (or rebuild) the KV-cache slab. Returns path to .bin file."""
    if not force and SLAB_PATH.exists() and self._is_current():
      logger.info("Slab is current — skipping rebuild. Use force=True to override.")
      return SLAB_PATH

    if not shutil.which(LLAMA_SERVER):
      raise RuntimeError(
        f"llama-server not found at '{LLAMA_SERVER}'. Install llama.cpp with Metal: cmake -DLLAMA_METAL=on .."
      )
    if not Path(MODEL_PATH).exists():
      raise RuntimeError(
        f"Model not found: {MODEL_PATH}. Set LOCAL_MODEL_PATH env var or download a .gguf model."
      )

    SLAB_DIR.mkdir(parents=True, exist_ok=True)
    prompt_text = self._collect_slab_text()
    SLAB_PROMPT_PATH.write_text(prompt_text, encoding="utf-8")
    logger.info(
      "Building KV-cache slab: %.1f KB prompt → %s",
      len(prompt_text) / 1024,
      SLAB_PATH,
    )

    cmd = [
      LLAMA_SERVER,
      "-m",
      MODEL_PATH,
      "--prompt-cache",
      str(SLAB_PATH),
      "--prompt-cache-all",
      "-ngl",
      "99",  # offload all layers to Metal GPU
      "--no-mmap",  # keep weights resident in Unified Memory
      "-p",
      prompt_text[:32_000],  # llama-server prompt arg (truncated)
      "-n",
      "1",  # generate 1 token to trigger cache write
      "--log-disable",
    ]
    t0 = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    elapsed = time.time() - t0

    if result.returncode != 0:
      raise RuntimeError(f"llama-server slab build failed:\n{result.stderr[:2000]}")

    self._save_state(prompt_text)
    logger.info("KV-cache slab built in %.1fs → %s", elapsed, SLAB_PATH)
    return SLAB_PATH

  # ── Private ─────────────────────────────────────────────────────────────

  def _collect_slab_text(self, max_chars: int = 200_000) -> str:

    parts: list[str] = []
    total = 0
    for src in _SLAB_SOURCES:
      if src.is_dir():
        for f in sorted(src.rglob("*.txt"))[:300]:
          chunk = f.read_text(errors="ignore")[:6_000]
          parts.append(f"### {f.name}\n{chunk}")
          total += len(chunk)
          if total >= max_chars:
            break
      elif src.is_file():
        chunk = src.read_text(errors="ignore")[:50_000]
        parts.append(f"### {src.name}\n{chunk}")
        total += len(chunk)
      if total >= max_chars:
        break
    return "\n\n".join(parts)

  def _is_current(self) -> bool:
    import json as _json

    if not SLAB_STATE_PATH.exists():
      return False
    try:
      state = _json.loads(SLAB_STATE_PATH.read_text())
      return time.time() < state.get("expires_at", 0)
    except (ValueError, KeyError):
      return False

  def _save_state(self, prompt_text: str) -> None:
    import hashlib
    import json as _json

    state = {
      "prompt_hash": hashlib.sha256(prompt_text.encode()).hexdigest()[:12],
      "built_at": time.time(),
      "expires_at": time.time() + 86_400,  # 24-hour validity
      "model": Path(MODEL_PATH).name,
    }
    SLAB_STATE_PATH.write_text(_json.dumps(state, indent=2))


if __name__ == "__main__":
  logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
  )
  parser = argparse.ArgumentParser(description="Build the Sovereign MLX KV-cache slab")
  parser.add_argument("--build", action="store_true", help="Build/rebuild the slab")
  parser.add_argument(
    "--force", action="store_true", help="Force rebuild even if current"
  )
  args = parser.parse_args()
  if args.build or args.force:
    slab = KVCacheSlab()
    path = slab.build(force=args.force)
    print(f"Slab ready: {path}")
  else:
    parser.print_help()
