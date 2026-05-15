# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import re

files_to_check = [
  "docs/architecture/claude_code_6_block_allow_spec.md",
  "walkthrough.md",
  "Claude_Code_6/main.go",
  "docs/prompts/gemini-ingestion-layer-prompt-design.md",
  "docs/architecture/memory_pointer_index_spec.md",
  "docs/architecture/agnt_comparison.md",
  "docs/daily-notes/2026-04-18.md",
]


def replace_in_file(filepath):
  if not os.path.exists(filepath):
    return False

  with open(filepath, encoding="utf-8") as f:
    content = f.read()

  original = content

  # Replace specifically in the context of BLOCK/ALLOW
  content = re.sub(
    r"Judge\s*#?6\s*[—\-]\s*BLOCK/ALLOW",
    "Claude_Code_6 — BLOCK/ALLOW",
    content,
    flags=re.IGNORECASE,
  )
  content = re.sub(
    r"Judge\s*#?6\s*BLOCK/ALLOW",
    "Claude_Code_6 BLOCK/ALLOW",
    content,
    flags=re.IGNORECASE,
  )
  content = re.sub(
    r"Judge\s*#?6\s*Gate", "Claude_Code_6 Gate", content, flags=re.IGNORECASE
  )

  # In the specific spec files, replace all Judge 6 if it doesn't mention atp 5-19
  if "claude_code_6_block_allow_spec.md" in filepath or "walkthrough.md" in filepath:
    if "atp 5-19" not in content.lower():
      content = re.sub(r"Judge\s*#?6", "Claude_Code_6", content, flags=re.IGNORECASE)

  if content != original:
    with open(filepath, "w", encoding="utf-8") as f:
      f.write(content)
    print(f"Updated {filepath}")
    return True
  return False


for f in files_to_check:
  replace_in_file(f)
