#!/usr/bin/env python3
"""
zero_cpu_router.py — Master Hardware Router for Antigravity Sovereign Stack
Latest version (May 2026): Properly calls the ANE Bridge (Pickle Rick's orchestrator)
with full leak-defusal, M1 Max L2 cache enforcement, and seamless Colab T4 fallback.

Usage:
    python zero_cpu_router.py <task_id> <code_file.py> [--estimate-bytes N]

This script is the single entry point for all compute dispatch in the monorepo.
It NEVER runs heavy workloads on the local CPU. All ML/tensor work is routed to:
  - Tier 3: Apple Neural Engine (ANE) via ane_bridge.py (if < 12.5 MB L2 SRAM)
  - Tier 2: Colab T4 (via Google Drive IPC) for larger workloads

The ANE Bridge handles:
  - 119-cycle compile limit defusal via exec() restart
  - Dynamic seq_len halving on L2 overflow
  - ctypes bridge to the compiled C library (third_party/ANE/bridge/libane_bridge.dylib)
"""

import os
import sys
import time
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# =============================================================================
# M1 MAX HARDWARE CONSTANTS (queried via sysctl hw on user's machine)
# =============================================================================
M1_MAX_L2_SRAM_BYTES = 12_582_912  # 12.5 MB — DO NOT EXCEED
M1_MAX_UNIFIED_RAM_GB = 64

# =============================================================================
# PATH CONFIGURATION (adjust for your monorepo layout)
# =============================================================================
# The ANE Bridge lives alongside this router in the FastAPI service dir
ANE_BRIDGE_PATH = (
  Path(__file__).parent / "ane_bridge.py"
)  # or absolute: /path/to/apps/aiyou_stack/aiyou-fastapi-services/ane_bridge.py
COLAB_IPC_DIR = Path.home() / "Google Drive" / "My Drive" / "Antigravity_IPC"


# =============================================================================
# UTILITY: M1 MAX L2 CACHE ENFORCER
# =============================================================================
def enforce_m1_max_constraints(seq_len: int, dim: int, num_qkv: int = 3) -> int:
  """
  Prevents the Apple Neural Engine from overflowing its 12.5 MB L2 SRAM cache.
  Formula used by Pickle Rick's orchestrator:
      estimated_bytes = seq_len * dim * 4 (fp32) * num_qkv (Q/K/V)
  If overflow → dynamically halve seq_len and warn.
  """
  estimated_bytes = seq_len * dim * 4 * num_qkv
  if estimated_bytes > M1_MAX_L2_SRAM_BYTES:
    new_seq = max(1, seq_len // 2)
    print(f"🔴 [M1 MAX] PANIC AVOIDED: {estimated_bytes} bytes > 12.5 MB L2 cache.")
    print(f"   Auto-halving seq_len {seq_len} → {new_seq} to survive.")
    return new_seq
  return seq_len


# =============================================================================
# CORE DISPATCH — THE SOVEREIGN ROUTER
# =============================================================================
def dispatch_compute(
  task_id: str,
  python_code: str,
  estimated_bytes: Optional[int] = None,
  force_colab: bool = False,
) -> Dict[str, Any]:
  """
  Master dispatch function. Call this from any Antigravity agent (Claurst, Jules, GCA, etc.).

  Decision tree:
      1. If estimated_bytes <= 12.5 MB AND no heavy torch/tf → ANE (Tier 3)
      2. Else → Colab T4 via Google Drive IPC (Tier 2)
      3. Never falls back to local CPU.

  Returns dict with keys: status, source, data (or error)
  """
  if estimated_bytes is None:
    # Heuristic: rough byte estimate for tensor work (over-estimate to be safe)
    estimated_bytes = len(python_code.encode("utf-8")) * 128

  print(
    f"\n🚀 [zero_cpu_router] Dispatching task '{task_id}' ({estimated_bytes} bytes estimated)"
  )

  # ------------------------------------------------------------------
  # TIER 3 — APPLE NEURAL ENGINE (Bare-Metal Edge)
  # ------------------------------------------------------------------
  if (
    not force_colab
    and estimated_bytes <= M1_MAX_L2_SRAM_BYTES
    and "import torch" not in python_code
    and "import tensorflow" not in python_code
    and "import jax" not in python_code
  ):
    print("⚡ Routing to Apple Neural Engine (Tier 3 — M1 Max Bare-Metal)")

    # Write payload for the bridge
    payload_path = Path(f"/tmp/{task_id}_ane_payload.py")
    payload_path.write_text(python_code)

    # Call the ANE Bridge properly (Pickle Rick's full orchestrator)
    # The bridge handles: 119-cycle leak defusal, dynamic constraints, ctypes to .dylib
    try:
      cmd = [
        sys.executable,
        str(ANE_BRIDGE_PATH),
        "--run",
        str(payload_path),
        "--task-id",
        task_id,
      ]
      result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300,  # 5 min max for ANE tasks
      )

      if result.returncode == 0:
        return {
          "status": "success",
          "source": "ANE_EDGE",
          "task_id": task_id,
          "data": result.stdout.strip(),
          "stderr": result.stderr.strip() or None,
        }
      else:
        return {
          "status": "error",
          "source": "ANE_EDGE",
          "task_id": task_id,
          "error": result.stderr or result.stdout,
          "returncode": result.returncode,
        }

    except subprocess.TimeoutExpired:
      return {
        "status": "error",
        "source": "ANE_EDGE",
        "error": "ANE task timed out after 300s",
      }
    except Exception as e:
      return {"status": "error", "source": "ANE_EDGE", "error": str(e)}

  # ------------------------------------------------------------------
  # TIER 2 — COLAB T4 (Cloud GPU Fallback via Google Drive IPC)
  # ------------------------------------------------------------------
  else:
    reason = "forced" if force_colab else "exceeds L2 cache or heavy ML libs"
    print(f"☁️  Routing to Colab T4 ({reason}) — Tier 2 Sovereign Cloud")

    os.makedirs(COLAB_IPC_DIR / "inbox", exist_ok=True)
    os.makedirs(COLAB_IPC_DIR / "outbox", exist_ok=True)

    inbox_path = COLAB_IPC_DIR / "inbox" / f"{task_id}.py"
    outbox_path = COLAB_IPC_DIR / "outbox" / f"{task_id}.json"

    inbox_path.write_text(python_code)

    # Wait for Colab worker (started via harbor up llamacpp ... or manual)
    print("   Waiting for Colab worker to execute and return result...")
    timeout = 600  # 10 min
    start = time.time()
    while not outbox_path.exists():
      if time.time() - start > timeout:
        return {
          "status": "error",
          "source": "COLAB_CLOUD",
          "error": "Timeout waiting for Colab result",
        }
      time.sleep(0.5)

    try:
      result = json.loads(outbox_path.read_text())
      outbox_path.unlink(missing_ok=True)
      result["source"] = "COLAB_CLOUD"
      result["task_id"] = task_id
      return result
    except Exception as e:
      return {
        "status": "error",
        "source": "COLAB_CLOUD",
        "error": f"Failed to parse Colab result: {e}",
      }


# =============================================================================
# CLI ENTRY POINT (used by Jules/GCA swarm, Claurst hooks, etc.)
# =============================================================================
def main():
  parser = argparse.ArgumentParser(description="Antigravity Zero-CPU Compute Router")
  parser.add_argument("task_id", help="Unique task identifier")
  parser.add_argument(
    "code_file", help="Path to Python file containing the compute payload"
  )
  parser.add_argument(
    "--estimate-bytes", type=int, default=None, help="Override byte estimate"
  )
  parser.add_argument(
    "--force-colab", action="store_true", help="Force Tier 2 Colab even if small"
  )
  args = parser.parse_args()

  code = Path(args.code_file).read_text()
  result = dispatch_compute(
    task_id=args.task_id,
    python_code=code,
    estimated_bytes=args.estimate_bytes,
    force_colab=args.force_colab,
  )
  print(json.dumps(result, indent=2))


if __name__ == "__main__":
  main()
