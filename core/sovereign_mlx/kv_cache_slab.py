# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""kv_cache_slab.py — Sovereign MLX KV Cache Slab Builder

Runs llama-server --prompt-cache-all once against the .beads corpus
to produce a persistent KV cache binary slab. Subsequent inference
requests use --prompt-cache-ro to skip prefill entirely.

Slab is valid for 24 hours (regenerate daily via COR.KAIROS daemon).

Usage:
    python -m core.sovereign_mlx.kv_cache_slab --build
    python -m core.sovereign_mlx.kv_cache_slab --status
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import os
import pathlib
import subprocess

logging.basicConfig(level=logging.INFO, format="%(asctime)s [MLX-SLAB] %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "data" / "sovereign_mlx"
SLAB_FILE = DATA_DIR / "kv_cache_slab.bin"
STATE_FILE = DATA_DIR / "slab_state.json"
BEADS_DIR = REPO_ROOT / ".beads"

# Default llama.cpp server binary path
DEFAULT_LLAMA_SERVER = os.environ.get("LLAMA_SERVER_PATH", "llama-server")
DEFAULT_MODEL_PATH = os.environ.get(
  "LOCAL_MODEL_PATH",
  os.path.expanduser("~/models/gemma-2-9b-it.Q4_K_M.gguf"),
)

# Slab validity (seconds)
SLAB_TTL = 86400  # 24 hours


def _collect_prompt_corpus() -> str:
  """Build the prompt corpus from .beads files for KV prefill."""
  parts: list[str] = []
  if BEADS_DIR.exists():
    for f in sorted(BEADS_DIR.glob("*.md")):
      content = f.read_text(errors="replace")
      parts.append(f"### {f.name}\n{content}\n")
      logger.info("  Added: %s (%d bytes)", f.name, len(content))

  # Include AGENTS.md and CLAUDE.md
  for name in ("AGENTS.md", "CLAUDE.md"):
    path = REPO_ROOT / name
    if path.exists():
      parts.append(path.read_text(errors="replace"))

  return "\n".join(parts)


def build_slab(
  model_path: str = DEFAULT_MODEL_PATH,
  llama_server: str = DEFAULT_LLAMA_SERVER,
) -> dict | None:
  """Build the KV cache slab by running llama-server with prompt-cache-all.

  Returns:
      Slab metadata dict, or None on failure.
  """
  DATA_DIR.mkdir(parents=True, exist_ok=True)

  if not pathlib.Path(model_path).exists():
    logger.error("Model not found: %s", model_path)
    return None

  corpus = _collect_prompt_corpus()
  if not corpus.strip():
    logger.error("No corpus content collected")
    return None

  # Write corpus to temp file for llama-server
  corpus_file = DATA_DIR / "slab_corpus.txt"
  corpus_file.write_text(corpus)

  logger.info(
    "Building KV slab (%d chars) from %s...",
    len(corpus),
    model_path,
  )

  # Run llama-server in prompt-cache-all mode (single pass)
  cmd = [
    llama_server,
    "-m",
    model_path,
    "--prompt-cache-all",
    "--prompt-cache",
    str(SLAB_FILE),
    "-ngl",
    "99",  # full GPU offload
    "-f",
    str(corpus_file),
    "--batch-size",
    "512",
    "-n",
    "1",  # generate 1 token then stop
  ]

  try:
    result = subprocess.run(
      cmd,
      capture_output=True,
      text=True,
      timeout=300,
    )

    if SLAB_FILE.exists():
      state = {
        "slab_path": str(SLAB_FILE),
        "model": model_path,
        "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "slab_bytes": SLAB_FILE.stat().st_size,
        "corpus_chars": len(corpus),
        "ttl_seconds": SLAB_TTL,
      }
      STATE_FILE.write_text(json.dumps(state, indent=2))
      logger.info("KV slab built: %s (%d bytes)", SLAB_FILE, state["slab_bytes"])
      return state

    logger.error("Slab file not created. stderr: %s", result.stderr[:500])
    return None

  except FileNotFoundError:
    logger.error("llama-server not found at: %s", llama_server)
    return None
  except subprocess.TimeoutExpired:
    logger.error("Slab build timed out (300s)")
    return None


def is_valid() -> bool:
  """Check if current slab is still within TTL."""
  if not STATE_FILE.exists():
    return False
  state = json.loads(STATE_FILE.read_text())
  created = datetime.datetime.fromisoformat(state["created_at"])
  age = (datetime.datetime.now(datetime.UTC) - created).total_seconds()
  return age < state.get("ttl_seconds", SLAB_TTL)


def get_status() -> dict | None:
  """Read current slab state from disk."""
  if not STATE_FILE.exists():
    logger.info("No slab state found at %s", STATE_FILE)
    return None
  state = json.loads(STATE_FILE.read_text())
  valid = is_valid()
  logger.info("Slab: %s", state.get("slab_path", "unknown"))
  logger.info("Model: %s", state.get("model", "unknown"))
  logger.info("Created: %s", state.get("created_at", "unknown"))
  logger.info("Size: %d bytes", state.get("slab_bytes", 0))
  logger.info("Valid: %s", "YES" if valid else "EXPIRED")
  return state


def main() -> None:
  parser = argparse.ArgumentParser(description="Sovereign MLX KV Cache Slab Manager")
  parser.add_argument("--build", action="store_true", help="Build a new KV cache slab")
  parser.add_argument("--status", action="store_true", help="Show current slab state")
  parser.add_argument("--model", default=DEFAULT_MODEL_PATH, help="Model path")
  args = parser.parse_args()

  if args.build:
    build_slab(model_path=args.model)
  elif args.status:
    get_status()
  else:
    parser.print_help()


if __name__ == "__main__":
  main()
