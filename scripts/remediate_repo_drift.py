#!/usr/bin/env python3
import os
import re

ROOT = "/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
CANONICAL_WORKSPACE = "pnkln.code-workspace"

EXCLUDE_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "env",
    "venv",
    "__pycache__",
    ".next",
    ".cache",
    "dist",
    "build",
    "out",
    "coverage",
    ".idea",
}

EXCLUDE_EXTS = {
    ".min.js",
    ".map",
    ".pyc",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".svg",
    ".zip",
    ".tar",
    ".gz",
    ".sql",
    ".sqlite",
    ".sqlite3",
    ".log",
    ".lock",
    ".csv",
    ".pdf",
    ".mp4",
    ".mov",
    ".woff",
    ".woff2",
    ".ttf",
}


def is_excluded(path, name, is_dir):
    if is_dir and name in EXCLUDE_DIRS:
        return True
    if not is_dir:
        _, ext = os.path.splitext(name)
        if ext.lower() in EXCLUDE_EXTS:
            return True
    return False


def scrub_workspaces():
    print("[remediate] Starting workspace deletion protocol...")
    deleted = 0
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if not is_excluded(root, d, True)]
        for file in files:
            if file.endswith(".code-workspace"):
                if file == CANONICAL_WORKSPACE:
                    continue
                path = os.path.join(root, file)
                print(f"  - Deleting alternate root: {path}", flush=True)
                os.remove(path)
                deleted += 1
    print(
        f"[remediate] Deletion complete. Neutralized {deleted} alternate operator entrypoints.\n",
        flush=True,
    )


def scrub_content():
    print("[remediate] Starting aggressive string replacement protocol...", flush=True)

    # Precise replacements
    naming_replacements = {
        re.compile(r"pnkln-stack", re.IGNORECASE): "pnkln-stack",
        re.compile(r"pnkln stack", re.IGNORECASE): "pnkln stack",
        re.compile(r"pnkln", re.IGNORECASE): "pnkln",
        re.compile(r"pnkln", re.IGNORECASE): "pnkln",
    }

    # Model replacements (`gemini-3.1-family`, `gemini-3.1-family`, `gemini-3.1-family`, etc -> `gemini-3.1-family`)
    # Exception: we don't want to replace "gemini-3.1-family" itself if it's partially matched, so we look for older gemini tags
    model_regex = re.compile(r"gemini-(pro|1\.[0-9]+(-pro|-flash)?(-latest|-00[1-9])?)", re.IGNORECASE)

    mod_count = 0

    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if not is_excluded(root, d, True)]
        for file in files:
            if is_excluded(root, file, False):
                continue

            path = os.path.join(root, file)

            # Skip massive files (over 2MB)
            try:
                if os.path.getsize(path) > 2 * 1024 * 1024:
                    continue
            except OSError:
                continue

            # Try parsing as utf-8 strings
            try:
                with open(path, encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue  # Skip binary or unreadable files

            original_content = content

            # Apply naming fixes
            for pattern, repl in naming_replacements.items():
                content = pattern.sub(repl, content)

            # Apply model fixes
            content = model_regex.sub("gemini-3.1-family", content)

            if content != original_content:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                mod_count += 1

    print(
        f"[remediate] Replacement protocol complete. Reprogrammed {mod_count} files to canonical alignment.\n",
        flush=True,
    )


if __name__ == "__main__":
    scrub_workspaces()
    scrub_content()
    print("[remediate] Programmatic phase 3.5 sweep strictly enforced and finalized.", flush=True)
