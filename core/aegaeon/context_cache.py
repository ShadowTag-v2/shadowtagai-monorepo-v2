# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
core/aegaeon/context_cache.py
Gemini Context Cache "Slab" — maps Aegaeon's VRAM slab to Gemini's caching API.

Economics:
  Standard input tokens: $X
  Cached input tokens:   $X * 0.25  (75% discount)
  Combined with flash-lite baseline → net ~84% reduction vs stateless usage.

Usage:
  cache = AegaeonContextCache()
  cache_name = cache.build()           # one-time upload
  cache_name = cache.get_or_build()    # idempotent — reuses live cache
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path

logger = logging.getLogger("aegaeon.context_cache")

REPO_ROOT = Path(__file__).parent.parent.parent
CACHE_STATE_PATH = REPO_ROOT / "data" / "aegaeon" / "cache_state.json"
MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite-preview")
CACHE_TTL_SECONDS = int(os.environ.get("AEGAEON_CACHE_TTL", "3600"))

# Sources loaded into the Master Memory Slab (in priority order)
_SLAB_SOURCES: list[Path] = [
    REPO_ROOT / "CLAUDE.md",
    REPO_ROOT / "operations" / "monorepo_manifest.yaml",
    REPO_ROOT / "scripts" / "judge6.sh",
    REPO_ROOT / "data" / "ane_beads",  # directory — all .txt files under it
]


def _load_slab_text(max_chars: int = 900_000) -> str:
    parts: list[str] = []
    total = 0
    for src in _SLAB_SOURCES:
        if src.is_dir():
            files = sorted(src.rglob("*.txt"))[:200]
            for f in files:
                chunk = f.read_text(errors="ignore")[:8_000]
                parts.append(f"# {f.name}\n{chunk}")
                total += len(chunk)
                if total >= max_chars:
                    break
        elif src.is_file():
            chunk = src.read_text(errors="ignore")[:40_000]
            parts.append(f"# {src.name}\n{chunk}")
            total += len(chunk)
        if total >= max_chars:
            break
    return "\n\n".join(parts)


class AegaeonContextCache:
    """Manages the Gemini Context Cache slab lifecycle."""

    def __init__(self) -> None:
        try:
            from google import genai

            self._client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
            self._genai = genai
        except ImportError as exc:
            raise RuntimeError("Install google-genai: pip install google-genai") from exc

    # ── Public API ──────────────────────────────────────────────────────────

    def get_or_build(self) -> str:
        """Return existing cache name if still valid, else build a new one."""
        existing = self._load_state()
        if existing and self._is_alive(existing):
            logger.info("Reusing live context cache: %s", existing)
            return existing
        logger.info("Cache missing or expired — building new slab...")
        return self.build()

    def build(self) -> str:
        """Upload a fresh context slab and persist the cache name."""
        from google.genai import types

        slab_text = _load_slab_text()
        logger.info("Uploading %.1f KB to Gemini Context Cache...", len(slab_text) / 1024)

        cache = self._client.caches.create(
            model=MODEL,
            config=types.CreateCachedContentConfig(
                contents=[
                    types.Content(
                        role="user",
                        parts=[types.Part(text=slab_text)],
                    )
                ],
                system_instruction=(
                    "You are Cor, the Antigravity Principal AI Coding Architect. "
                    "Apply the Sovereign Doctrine, Judge 6 rulesets, and Zero Trust "
                    "security protocols from the slab above to every response."
                ),
                ttl=f"{CACHE_TTL_SECONDS}s",
            ),
        )
        cache_name: str = cache.name
        self._save_state(cache_name)
        logger.info("Context cache created: %s (TTL %ds)", cache_name, CACHE_TTL_SECONDS)
        return cache_name

    def invalidate(self) -> None:
        """Force-expire the cached slab (triggers rebuild on next get_or_build)."""
        if CACHE_STATE_PATH.exists():
            CACHE_STATE_PATH.unlink()
            logger.info("Cache state invalidated.")

    # ── Private helpers ─────────────────────────────────────────────────────

    def _load_state(self) -> str | None:
        if not CACHE_STATE_PATH.exists():
            return None
        try:
            state = json.loads(CACHE_STATE_PATH.read_text())
            if time.time() < state.get("expires_at", 0):
                return state["name"]
        except (json.JSONDecodeError, KeyError):
            pass
        return None

    def _save_state(self, name: str) -> None:
        CACHE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        state = {"name": name, "expires_at": time.time() + CACHE_TTL_SECONDS - 60}
        CACHE_STATE_PATH.write_text(json.dumps(state, indent=2))

    def _is_alive(self, name: str) -> bool:
        try:
            self._client.caches.get(name=name)
            return True
        except Exception:
            return False
