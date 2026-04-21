#!/usr/bin/env python3
import os

ROOT = "/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
REF_DIR = os.path.join(ROOT, "reference")
SKILLS_DIR = "/Users/pikeymickey/.gemini/antigravity/skills"

output_path = os.path.join(ROOT, "docs", "REFERENCE_INDEX.md")
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w") as f:
    f.write("# Reference and Skills Index\n\n")

    f.write("## Antigravity Skills Inventory\n")
    if os.path.exists(SKILLS_DIR):
        for item in sorted(os.listdir(SKILLS_DIR)):
            path = os.path.join(SKILLS_DIR, item)
            if os.path.isdir(path):
                f.write(f"- `{item}` (External Skill)\n")
    else:
        f.write("*No skills directory found.*\n")

    f.write("\n## Offline Reference Modules\n")
    if os.path.exists(REF_DIR):
        for item in sorted(os.listdir(REF_DIR)):
            path = os.path.join(REF_DIR, item)
            if os.path.isdir(path):
                f.write(f"- `{item}/`\n")
            elif os.path.isfile(path) and not item.startswith("."):
                f.write(f"- `{item}`\n")
    else:
        f.write("*No reference directory found.*\n")
