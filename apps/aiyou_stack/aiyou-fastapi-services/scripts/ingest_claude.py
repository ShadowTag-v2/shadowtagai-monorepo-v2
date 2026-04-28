# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import glob
import json
import os

# TARGETS: The "Lost Treasury", Active Configs, and External Repos
PATHS_TO_SCAN = [
    "/Users/Deleted Users/pikeymickey/.claude",
    os.path.expanduser("~/.claude"),
    "/Users/pikeymickey/shadowtag_v4-stack/ShadowTag-v2/external_repos",  # Captured from symlinks
]


KEYWORDS = [
    "Plan",
    "Revenue",
    "Architecture",
    "Strategy",
    "Valuation",
    "Cor.",
    "p99",
    "tier",
    "Idea",
    "Concept",
]
Output_File = "claude_intelligence_manifest.md"


def parse_jsonl_file(filepath, out_handle, source_label):
    """Helper to parse a single JSONL file."""
    print(f"📄 Parsing {source_label}: {os.path.basename(filepath)}")
    try:
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    content = ""
                    # Handle various message formats
                    if "text" in entry:
                        content = entry["text"]
                    elif "content" in entry:
                        content = str(entry["content"])
                    elif "chat_messages" in entry:  # history.jsonl format sometimes differs
                        # Extract user/assistant text from chat_messages list
                        msgs = entry.get("chat_messages", [])
                        content = " ".join([m.get("text", "") for m in msgs])

                    if content and any(k in content for k in KEYWORDS):
                        # Extract a snippet - slightly longer for history
                        snippet = content[:500].replace("\n", " ")
                        out_handle.write(f"- **{source_label} Insight**: {snippet}...\n")
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"⚠️ Error reading {filepath}: {e}")


def ingest_claude_projects():
    print("🕵️‍♀️ SCANNING CLAUDE INTELLIGENCE...")

    with open(Output_File, "w") as out:
        out.write("# CLAUDE INTELLIGENCE MANIFEST (RECOVERY MODE)\n\n")

        for base_path in PATHS_TO_SCAN:
            if not os.path.exists(base_path):
                continue

            print(f"📂 Scanning Base: {base_path}")

            # 1. Main Global History (The "Scattered" chats)
            history_file = os.path.join(base_path, "history.jsonl")
            if os.path.exists(history_file):
                out.write(f"## 📜 Global History ({base_path})\n")
                parse_jsonl_file(history_file, out, "Global History")
                out.write("\n")

            # 2. Project Specific History
            projects_dir = os.path.join(base_path, "projects")
            if os.path.exists(projects_dir):
                project_folders = [f.path for f in os.scandir(projects_dir) if f.is_dir()]
                for folder in project_folders:
                    project_name = os.path.basename(folder)
                    out.write(f"## 📂 Project: {project_name}\n")

                    jsonl_files = glob.glob(os.path.join(folder, "*.jsonl"))
                    for log_file in jsonl_files:
                        parse_jsonl_file(log_file, out, f"Project {project_name}")
                    out.write("\n")


if __name__ == "__main__":
    ingest_claude_projects()
    print(f"\n✅ Intelligence Manifest saved to {Output_File}")
