# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import subprocess


def enforce_immutable_prepared_state():
  print("💎 Initializing Omega Prepare (Format & Snapshot) Phase...")

  # 1. Format & Lint (The Quality Bar)
  print("   -> Enforcing Biome & Ruff Formats...")
  subprocess.run(["npx", "@biomejs/biome", "format", "--write", "apps"], check=False)
  subprocess.run(["python3", "-m", "ruff", "format", "apps"], check=False)

  # 2. Beads Memory Injection
  print("   -> Saving Temporal Bead State...")
  subprocess.run(
    [
      "python3",
      "tools/beads_manager.py",
      "add",
      "--id",
      "auto-egress-sync",
      "--type",
      "task",
      "--title",
      "Omega Prepare",
      "--content",
      "Snapshot locked.",
    ],
    check=False,
  )
  print("✅ Matrix format and temporal beads prepared.")


if __name__ == "__main__":
  enforce_immutable_prepared_state()
