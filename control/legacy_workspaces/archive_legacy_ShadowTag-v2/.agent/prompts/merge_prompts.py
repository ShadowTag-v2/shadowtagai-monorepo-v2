import re
import yaml
from pathlib import Path
from collections import defaultdict

PRIORITY = {
  "CLAUDE_4": 100,
  "ANTHROPIC": 98,
  "CLAUDECODE": 95,
  "CURSOR": 90,
  "GROK": 85,
  "PERPLEXITY": 80,
  "DEVIN": 75,
  "V0": 70,
}


def extract_atomic_blocks(file_path: Path) -> dict:
  content = file_path.read_text(encoding="utf-8", errors="ignore")
  blocks = defaultdict(str)

  xml_matches = re.findall(r"<([A-Z_]+)>(.*?)</\1>", content, re.DOTALL | re.IGNORECASE)
  for name, text in xml_matches:
    blocks[name.upper()] += text.strip() + "\n\n"

  md_matches = re.findall(
    r"^#\s+(.+?)\n(.*?)(?=^#|\Z)", content, re.DOTALL | re.MULTILINE
  )
  for name, text in md_matches:
    clean_name = re.sub(r"[^A-Z0-9_]", "_", name.upper().strip())
    blocks[clean_name] += text.strip() + "\n\n"

  if not blocks:
    blocks[file_path.stem.upper()] = content

  return dict(blocks)


def merge_blocks(all_blocks: dict) -> dict:
  merged = {}
  for block_name, sources in all_blocks.items():
    if not sources:
      continue
    best_source = max(sources.keys(), key=lambda s: PRIORITY.get(s, 0))
    merged[block_name] = sources[best_source].strip()
  return merged


def build_unified_prompt(merged: dict) -> str:
  out = {
    "version": "1.4",
    "date": "2026-02-24",
    "description": "Ultimate Unified Master Prompt - ALL major leaks merged.",
    "core_identity": {
      "name": "Ultimate Truth-Seeking High-Agency AI",
      "philosophy": "Truth-seeking, humanist, maximally curious. Respond in user's exact language/dialect. Push back politely when corrected if confident.",
    },
    "blocks": {},
  }
  for k, v in sorted(merged.items()):
    # Limit to reasonable length
    if len(v) < 10000:
      out["blocks"][k] = {"description": f"Extracted block {k}", "rules": v}

  return yaml.dump(out, sort_keys=False)


if __name__ == "__main__":
  prompt_dir = Path(".")
  all_blocks = defaultdict(dict)

  for ext in ["*.txt", "*.md"]:
    for file in prompt_dir.rglob(ext):
      source_name = file.parent.name.upper() or "UNKNOWN"
      blocks = extract_atomic_blocks(file)
      for name, text in blocks.items():
        all_blocks[name][source_name] = text

  merged = merge_blocks(all_blocks)
  unified = build_unified_prompt(merged)

  Path("../master_prompt_v1.4_unified.yaml").write_text(unified)
  print("✅ master_prompt_v1.4_unified.yaml created in .agent directory")
