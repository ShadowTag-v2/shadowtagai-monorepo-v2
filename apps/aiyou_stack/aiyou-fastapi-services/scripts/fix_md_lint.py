# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import re
from pathlib import Path


def fix_markdown(file_path):
    if not file_path.is_file():
        return

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # MD022: Headings should be surrounded by blank lines
    # Fix before heading
    content = re.sub(r"([^\n])\n(#+\s)", r"\1\n\n\2", content)
    # Fix after heading (needs careful handling to not break next block if it's tight)
    # But usually headers should have blank after
    content = re.sub(r"^(#+.*)\n([^\n#])", r"\1\n\n\2", content, flags=re.MULTILINE)

    # MD032: Lists should be surrounded by blank lines
    # Fix before list (unordered)
    content = re.sub(r"([^\n])\n(\s*[-*+]\s)", r"\1\n\n\2", content)
    # Fix before list (ordered)
    content = re.sub(r"([^\n])\n(\s*\d+\.\s)", r"\1\n\n\2", content)

    # MD031: Fenced code blocks should be surrounded by blank lines
    # Fix before fence
    content = re.sub(r"([^\n])\n(```)", r"\1\n\n\2", content)
    # Fix after fence
    content = re.sub(r"(```)\n([^\n])", r"\1\n\n\2", content)

    # MD030: Spaces after list markers (reduce 2+ spaces to 1)
    # Use careful regex to only target list items
    content = re.sub(r"^(\s*[-*+])\s{2,}(?=\S)", r"\1 ", content, flags=re.MULTILINE)
    content = re.sub(r"^(\s*\d+\.)\s{2,}(?=\S)", r"\1 ", content, flags=re.MULTILINE)

    if content != original_content:
        print(f"Fixing {file_path}")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)


def main():
    root_dir = Path("/Users/Deleted Users/pikeymickey/shadowtag_v4-fastapi-services")
    for path in root_dir.rglob("*.md"):
        if ".git" in path.parts or "node_modules" in path.parts:
            continue
        fix_markdown(path)


if __name__ == "__main__":
    main()
