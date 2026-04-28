#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""grok_extraction.py

Utility script to help you export Grok (xAI) conversation data.
It does **not** perform the actual export (that requires user interaction or an API key),
but it prints clear step‑by‑step instructions and a placeholder for a future API integration.

Usage:
    python3 scripts/grok_extraction.py

The script will:
1. Explain the two main ways to obtain Grok data (official export or browser extension).
2. Show the command you can run to move the exported JSON into the project's `extractions/` folder.
3. Optionally, if you set an environment variable `GROK_API_KEY`, it will demonstrate a stub HTTP request.
"""

import json
import os
import sys


def print_instructions() -> None:
    instructions = """
=== Grok Conversation Extraction Guide ===

1️⃣ **Official Data Export**
   • Open https://grok.x.ai and go to Settings → Data & Privacy → Export data.
   • Request the export; you’ll receive an email with a download link.
   • Download the ZIP and extract the JSON file (e.g., `grok_conversations.json`).

2️⃣ **Browser Extension / Userscript**
   • Install *Grok Exporter* (Chrome Web Store) or the *enhanced‑grok‑export* userscript from GitHub.
   • Open a conversation, click the “Export” button, and save as JSON.

3️⃣ **Move the JSON into the project**
   Run the following command (replace `<path>` with the actual location of the JSON file):

   ```bash
   mv <path>/grok_conversations.json \
      $(pwd)/erik-hancock-llm-memory/extractions/
   ```

4️⃣ **Re‑run the merge script** to include Grok data:

   ```bash
   python3 scripts/merge_web_extractions.py \
       --input-dir erik-hancock-llm-memory/extractions \
       --output-file erik-hancock-llm-memory/extractions/merged_extractions.json
   ```

---
If you have a Grok API key (currently in beta), you can use the stub below to fetch recent chats.
Set the environment variable `GROK_API_KEY` and run the script with `--fetch`.
---
"""
    print(instructions)


def fetch_placeholder() -> None:
    api_key = os.getenv("GROK_API_KEY")
    if not api_key:
        print("[INFO] No GROK_API_KEY found – skipping API fetch.")
        return
    # This is a stub; real implementation would use the xAI API (OpenAI‑compatible).
    print("[INFO] Detected GROK_API_KEY – would perform an API request here.")
    # Example payload (not executed):
    example = {
        "model": "grok-beta",
        "messages": [{"role": "system", "content": "list conversations"}],
    }
    print(json.dumps(example, indent=2))


if __name__ == "__main__":
    if "--fetch" in sys.argv:
        fetch_placeholder()
    else:
        print_instructions()
