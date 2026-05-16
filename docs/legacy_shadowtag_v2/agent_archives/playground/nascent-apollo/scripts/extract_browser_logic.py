#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os
from pathlib import Path

# BROWSER-USE LOGIC EXTRACTOR
# Scans external_repos/agentic/browser-use for useful snippets.

TARGET_DIR = Path("external_repos/agentic/browser-use")
OUTPUT_FILE = Path("Docs/Strategic_Intelligence/BROWSER_USE_INSIGHTS.md")


def extract():
    if not TARGET_DIR.exists():
        print(f"⏳ {TARGET_DIR} not found yet.")
        return

    print("=== ANALYZING BROWSER-USE ===")
    insights = "# BROWSER-USE INSIGHTS\n\n"

    # Look for specific files of interest
    interesting_files = ["agent.py", "browser.py", "controller.py"]

    for root, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            if file in interesting_files:
                path = Path(root) / file
                print(f"🔍 Analyzing {path}...")
                try:
                    content = path.read_text(encoding="utf-8", errors="ignore")
                    insights += f"## SOURCE: {path.relative_to(TARGET_DIR)}\n"
                    insights += "```python\n"
                    # Grab first 50 lines as a sample
                    insights += "\n".join(content.splitlines()[:50])
                    insights += "\n...\n```\n\n"
                except Exception as e:
                    print(f"⚠️ Error reading {path}: {e}")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(insights, encoding="utf-8")
    print(f"💾 Saved insights to {OUTPUT_FILE}")


if __name__ == "__main__":
    extract()
