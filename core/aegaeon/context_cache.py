# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""context_cache.py — Aegaeon Protocol: Gemini Context Cache Slab Builder

Builds a persistent Gemini Context Cache ("Master Memory Slab") from
CLAUDE.md, .beads/, Claude_Code_6 config, and monorepo manifest. Cached tokens
cost ~90% less on subsequent requests (Gemini 2.5+ pricing).

State persists to data/aegaeon/cache_state.json.

Usage:
    python -m core.aegaeon.context_cache --build
    python -m core.aegaeon.context_cache --status
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import os
import pathlib

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [AEGAEON] %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "data" / "aegaeon"
STATE_FILE = DATA_DIR / "cache_state.json"

# Files composing the Master Memory Slab (order matters)
SLAB_SOURCES = [
    REPO_ROOT / "CLAUDE.md",
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "monorepo_manifest.yaml",
    REPO_ROOT / ".beads" / "active_session_invariants.md",
    REPO_ROOT / "apps" / "aiyou_stack" / "aiyou-fastapi-services" / "src" / "Claude_Code_6" / "orchestrator.py",
]

# Default model for caching
DEFAULT_MODEL = "models/gemini-3.1-flash-lite-preview"
DEFAULT_TTL_HOURS = 24


def _collect_slab_content() -> str:
    """Concatenate all slab source files into a single context string."""
    parts: list[str] = []
    for path in SLAB_SOURCES:
        if path.exists():
            content = path.read_text(errors="replace")
            parts.append(f"--- {path.relative_to(REPO_ROOT)} ---\n{content}\n")
            logger.info("  Loaded: %s (%d bytes)", path.name, len(content))
        else:
            logger.warning("  Missing: %s", path)
    return "\n".join(parts)


def build_cache(model: str = DEFAULT_MODEL, ttl_hours: int = DEFAULT_TTL_HOURS) -> dict | None:
    """Create a new Gemini Context Cache from slab sources.

    Returns:
        Cache metadata dict, or None on failure.
    """
    try:
        from google import genai
    except ImportError:
        logger.error("google-genai not installed. Run: pip install google-genai")
        return None

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        logger.error("No GEMINI_API_KEY or GOOGLE_API_KEY in environment")
        return None

    client = genai.Client(api_key=api_key)
    slab_content = _collect_slab_content()

    if not slab_content.strip():
        logger.error("No content collected for slab")
        return None

    logger.info("Building cache slab (%d chars) for model %s...", len(slab_content), model)

    try:
        cache = client.caches.create(
            model=model,
            config={
                "contents": [{"role": "user", "parts": [{"text": slab_content}]}],
                "display_name": "aegaeon-master-slab",
                "ttl": f"{ttl_hours * 3600}s",
                "system_instruction": (
                    "You are an expert assistant for the ShadowTag monorepo. "
                    "Use the cached context to answer questions about the codebase, "
                    "architecture, and operational state."
                ),
            },
        )

        state = {
            "cache_name": cache.name,
            "model": model,
            "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
            "ttl_hours": ttl_hours,
            "slab_chars": len(slab_content),
            "source_count": len([p for p in SLAB_SOURCES if p.exists()]),
        }

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=2))
        logger.info("Cache created: %s", cache.name)
        logger.info("State saved to: %s", STATE_FILE)
        return state

    except Exception as e:
        logger.error("Cache creation failed: %s", e)
        return None


def get_status() -> dict | None:
    """Read current cache state from disk."""
    if not STATE_FILE.exists():
        logger.info("No cache state found at %s", STATE_FILE)
        return None
    state = json.loads(STATE_FILE.read_text())
    logger.info("Cache: %s", state.get("cache_name", "unknown"))
    logger.info("Created: %s", state.get("created_at", "unknown"))
    logger.info("Model: %s", state.get("model", "unknown"))
    logger.info("TTL: %dh", state.get("ttl_hours", 0))
    return state


def main() -> None:
    parser = argparse.ArgumentParser(description="Aegaeon Context Cache Manager")
    parser.add_argument("--build", action="store_true", help="Build a new cache slab")
    parser.add_argument("--status", action="store_true", help="Show current cache state")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Gemini model ID")
    parser.add_argument("--ttl", type=int, default=DEFAULT_TTL_HOURS, help="Cache TTL in hours")
    args = parser.parse_args()

    if args.build:
        build_cache(model=args.model, ttl_hours=args.ttl)
    elif args.status:
        get_status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
