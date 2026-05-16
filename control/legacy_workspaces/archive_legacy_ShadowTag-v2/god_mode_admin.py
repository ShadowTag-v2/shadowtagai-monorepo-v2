# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os
import sys

# Add the project root to sys.path so we can import libs
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from libs.steel.sdk import VelocityEngine


def main():
  print(">>> 🏛️  JUDGE 6: GOD MODE ACTIVATED")

  # 1. Initialize the Sovereign Suit
  try:
    suit = VelocityEngine(agent_name="Admin_GodMode", auto_apply=True)
  except Exception as e:
    print(f">>> ❌ CRITICAL: Failed to initialize Velocity Engine. {e}")
    sys.exit(1)

  # 2. SYNC FIRST (The Update)
  print(">>> 📡 Contacting Mothership (Git Pull)...")
  if not suit.pull_updates():
    print(">>> ⚠️ WARNING: Sync failed. Proceeding with potentially stale code.")
  else:
    print(">>> ✅ SYNC COMPLETE: Context is fresh.")

  # 3. The Mission Loop (Placeholder for future autonomous logic)
  print(">>> 🦾 READY. Waiting for Directives...")
  # Here allows manual interaction or starts a specific strategy
  # e.g. suit.run_strategy("clean_architecture")

  # For now, just keep alive or exit
  print(">>> 🏁 God Mode Initialization Complete.")


if __name__ == "__main__":
  main()
