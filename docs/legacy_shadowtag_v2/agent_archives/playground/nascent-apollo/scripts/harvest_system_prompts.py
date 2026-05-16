#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os
from pathlib import Path

# SHADOWTAG PROMPT HARVESTER
# Scans external_repos/agentic for "System Prompts" and aggregates them.

TARGET_DIR = Path("external_repos/agentic")
OUTPUT_FILE = Path("Docs/Strategic_Intelligence/SYSTEM_PROMPTS_COLLECTION.md")

KEYWORDS = ["system_prompt", "system-prompt", "prompts", "identity", "persona"]
EXTENSIONS = [".md", ".txt", ".json"]


def harvest():
    if not TARGET_DIR.exists():
        print(f"❌ Target directory {TARGET_DIR} not found. Run clone_universe.sh first.")
        return

    print("=== HARVESTING SYSTEM PROMPTS ===")
    collected_content = "# COLLECTED SYSTEM PROMPTS\n\n"

    for root, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            file_lower = file.lower()
            if any(ext in file_lower for ext in EXTENSIONS) and any(kw in file_lower for kw in KEYWORDS):
                path = Path(root) / file
                print(f"✅ Found potential prompt: {path}")
                try:
                    content = path.read_text(encoding="utf-8", errors="ignore")
                    repo_name = path.relative_to(TARGET_DIR).parts[0]
                    collected_content += f"## SOURCE: {repo_name} / {file}\n"
                    collected_content += "```text\n"
                    collected_content += content[:5000]  # Limit to 5k chars per file to avoid explosion
                    collected_content += "\n```\n\n"
                except Exception as e:
                    print(f"⚠️ Error reading {path}: {e}")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(collected_content, encoding="utf-8")
    print(f"💾 Saved collection to {OUTPUT_FILE}")


if __name__ == "__main__":
    harvest()
