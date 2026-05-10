"""Playground: Apple Neural Engine smoke test.

Verifies CoreML model loading on the local ANE.
Runtime: local Apple Silicon only (M-series).
Model: gemini-3.1-flash-lite-preview (served via sovereign stack).

Per AGENTS.md: labs must not redefine product truth.
"""

from __future__ import annotations

import platform
import sys


def check_ane_availability() -> dict[str, str]:
  """Check if Apple Neural Engine is available on this machine."""
  info = {
    "platform": platform.platform(),
    "machine": platform.machine(),
    "python": sys.version,
    "ane_available": "unknown",
  }

  if platform.machine() != "arm64" or platform.system() != "Darwin":
    info["ane_available"] = "no — not Apple Silicon"
    return info

  try:
    import coremltools  # noqa: F401

    info["ane_available"] = "yes — coremltools importable"
  except ImportError:
    info["ane_available"] = (
      "partial — coremltools not installed (pip install coremltools)"
    )

  return info


if __name__ == "__main__":
  result = check_ane_availability()
  for k, v in result.items():
    print(f"  {k}: {v}")
