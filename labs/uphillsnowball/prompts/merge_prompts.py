#!/usr/bin/env python3
import os
import re
import subprocess
from collections import defaultdict
from pathlib import Path

# Priority order: higher = preferred when merging same block
PRIORITY = {
  "Claude4.6": 100,
  "ClaudeCode": 95,
  "Cursor2.0": 90,
  "Cursor3.0": 88,
  "Grok4.20": 85,
  "Grok4.30": 84,
  "Perplexity": 80,
  "Devin": 75,
  "v0": 70,
}

REPOS = [
  "https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools.git",
  "https://github.com/elder-plinius/CL4R1T4S.git",
]


def extract_atomic_blocks(file_path: Path) -> dict:
  """Extract <BLOCK> or # Heading blocks from any prompt file."""
  try:
    content = file_path.read_text(encoding="utf-8", errors="ignore")
  except Exception:
    return {}

  blocks = defaultdict(str)

  # XML-style <BLOCK_NAME> ... </BLOCK_NAME>
  xml_matches = re.findall(r"<([A-Z_]+)>(.*?)</\1>", content, re.DOTALL | re.IGNORECASE)
  for name, text in xml_matches:
    blocks[name.upper()] += text.strip() + "\n\n"

  # Markdown # Heading style
  md_matches = re.findall(
    r"^#\s+(.+?)\n(.*?)(?=^#|\Z)", content, re.DOTALL | re.MULTILINE
  )
  for name, text in md_matches:
    clean_name = re.sub(r"[^A-Z0-9_]", "_", name.upper().strip())
    blocks[clean_name] += text.strip() + "\n\n"

  # Fallback: whole file as SINGLE_BLOCK if nothing tagged
  if not blocks:
    blocks["FULL_PROMPT"] = content

  return dict(blocks)


def merge_blocks(all_blocks: dict) -> dict:
  """Merge by block name, preferring highest priority source."""
  merged = {}
  for block_name, sources in all_blocks.items():
    if not sources:
      continue
    best_source = max(sources.keys(), key=lambda s: PRIORITY.get(s, 0))
    merged[block_name] = f"<!-- [{best_source}] -->\n{sources[best_source]}"
  return merged


def build_unified_prompt(merged: dict) -> str:
  header = """# ULTIMATE UNIFIED MASTER PROMPT v1.4
# Built from ALL major leaks (Pliny + x1xhlol + Grok 4.30)
# Copy-paste as system prompt. Edit blocks like code.

You are the ultimate truth-seeking, high-agency AI. Apply every block below on every response.

"""
  body = "\n".join(f"<{k}>\n{v}\n</{k}>\n" for k, v in sorted(merged.items()))
  return header + body


def update_and_merge():
  os.makedirs("leaks", exist_ok=True)
  all_blocks = defaultdict(dict)

  for repo in REPOS:
    name = repo.split("/")[-1].replace(".git", "")
    path = Path("leaks") / name
    if path.exists():
      print(f"[*] Updating {name}...")
      subprocess.run(["git", "-C", str(path), "pull"], capture_output=True)
    else:
      print(f"[*] Cloning {name}...")
      subprocess.run(["git", "clone", repo, str(path)], capture_output=True)

  # Parse extracted leaks
  prompt_dir = Path("leaks")
  for file in list(prompt_dir.rglob("*.txt")) + list(prompt_dir.rglob("*.md")):
    source_name = file.parent.name.upper() or "UNKNOWN"
    if any(
      x in source_name for x in ["CLAUDE", "CURSOR", "GROK", "DEVIN", "PERPLEXITY"]
    ):
      blocks = extract_atomic_blocks(file)
      for name, text in blocks.items():
        all_blocks[name][source_name] = text

  merged = merge_blocks(all_blocks)
  unified = build_unified_prompt(merged)

  Path("unified_master.md").write_text(unified)
  print("✅ unified_master.md auto-generated from latest leaks.")


if __name__ == "__main__":
  update_and_merge()
