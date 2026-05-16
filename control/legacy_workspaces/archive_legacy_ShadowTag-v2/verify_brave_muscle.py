# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import sys
import logging
from libs.arsenal.jetski.browser import JetskiAgent, find_brave_path

# Configure logging
logging.basicConfig(level=logging.INFO)


def test_muscle():
  print(">>> 🦁 TESTING BRAVE MUSCLE...")

  # 1. Check Path Detection
  path = find_brave_path()
  if path:
    print(f"✅ BRAVE BINARY FOUND: {path}")
  else:
    print("⚠️  BRAVE NOT FOUND (Fallback to Chromium)")
    print("    (This is expected if running in a container without Brave installed)")

  # 2. Instantiate Agent
  try:
    agent = JetskiAgent()
    print("✅ JETSKI AGENT INSTANTIATED")
    print(f"   Model: {agent.model}")
    print(f"   Browser Path: {agent.brave_path}")
  except Exception as e:
    print(f"❌ AGENT ERROR: {e}")
    sys.exit(1)


if __name__ == "__main__":
  test_muscle()
