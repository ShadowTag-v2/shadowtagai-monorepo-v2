#!/usr/bin/env python3
"""drive_ingest_runner.py — ANE-stack entrypoint for Drive ingest.

Execution order:
  1. Verify libane_bridge.dylib exists (run `make` only if missing)
  2. Probe zero_cpu_router import — confirms ANE stack is live
  3. Run drive_ingest_daemon.py as a live streaming subprocess (control plane)
  4. Report LanceDB row count (data/drive_ingest/lancedb)
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────

ROOT = Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball")
BRIDGE_DIR = ROOT / "third_party/ANE/bridge"
DYLIB = BRIDGE_DIR / "libane_bridge.dylib"
ANE_SVC = ROOT / "apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services"
VENV_PY = ROOT / ".venv/bin/python3"
DAEMON = ROOT / "scripts/drive_ingest_daemon.py"
LANCE_PATH = ROOT / "data/drive_ingest/lancedb"


# ── Step 1: Ensure dylib is present ───────────────────────────────────────────


def ensure_ane_bridge() -> None:
    if DYLIB.exists():
        return
    r = subprocess.run(["make"], cwd=BRIDGE_DIR, capture_output=True, text=True)
    if r.returncode != 0:
        msg = f"make failed:\n{r.stderr}"
        raise RuntimeError(msg)
    if not DYLIB.exists():
        msg = f"make succeeded but dylib still missing: {DYLIB}"
        raise FileNotFoundError(msg)


# ── Step 2: Probe ANE stack ────────────────────────────────────────────────────


def probe_ane_stack() -> None:
    sys.path.insert(0, str(ANE_SVC))
    try:
        from zero_cpu_router import dispatch_compute  # noqa: F401

    except Exception as e:
        msg = f"zero_cpu_router import failed: {e}"
        raise RuntimeError(msg) from e


# ── Step 3: Run daemon (streaming) ────────────────────────────────────────────


def run_daemon() -> None:
    env = {**os.environ, "PYTHONUNBUFFERED": "1"}
    proc = subprocess.run(
        [str(VENV_PY), str(DAEMON)],
        env=env,
        cwd=str(ROOT),
    )
    if proc.returncode != 0:
        msg = f"drive_ingest_daemon exited {proc.returncode}"
        raise RuntimeError(msg)


# ── Step 4: Report local output ────────────────────────────────────────────────


def report_local() -> None:
    ingest = ROOT / "data/drive_ingest"
    jsonl = ingest / "extractions.jsonl"
    docs = ingest / "docs"
    if jsonl.exists():
        sum(1 for _ in open(jsonl))
    if docs.exists():
        sum(1 for _ in docs.iterdir())


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        ensure_ane_bridge()
        probe_ane_stack()
        run_daemon()
        report_local()
    except Exception:
        sys.exit(1)
