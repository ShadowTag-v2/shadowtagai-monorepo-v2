#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
omega-loopin.py
Legacy wrapper/alias for the Omega Loop. Redirects to canonical finish_changes.py.
"""

import subprocess
from pathlib import Path


def run_loop():
  print("Delegating to canonical /omega-loop handler: finish_changes.py")
  script_path = Path(__file__).parent / "finish_changes.py"
  if script_path.exists():
    subprocess.run(["python3", str(script_path)])
  else:
    print("Error: finish_changes.py not found in the scripts/ folder.")


if __name__ == "__main__":
  run_loop()
