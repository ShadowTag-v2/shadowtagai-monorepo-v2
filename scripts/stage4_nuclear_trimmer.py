# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os
import re
import shutil
from pathlib import Path


def run_nuclear_trim(root_path: Path):
    print("=============================================")
    print(" INIT: STAGE 4 NUCLEAR TRIM & BLOAT ERADICATION")
    print("=============================================")

    # 1. Eradicate all .git folders and hooks (Strips forks and hooks and history natively)
    git_folders_deleted = 0
    for git_dir in root_path.rglob(".git"):
        if git_dir.is_dir():
            try:
                shutil.rmtree(git_dir, ignore_errors=True)
                git_folders_deleted += 1
            except Exception:
                pass
    print(f"[X] Obliterated {git_folders_deleted} embedded .git tracking folders and hooks.")

    # 2. Eradicate binaries, huge third-party databases, and dense artifacts
    binary_extensions = {
        ".exe",
        ".dll",
        ".so",
        ".dylib",
        ".bin",
        ".pth",
        ".safetensors",
        ".gguf",
        ".sqlite",
        ".sqlite3",
        ".db",
        ".idx",
        ".pack",
    }

    deleted_binaries = 0
    massive_files = 0

    for root, dirs, files in os.walk(root_path):
        # Skip specific critical paths if necessary, but user said "any"
        for name in files:
            file_path = Path(root) / name
            if file_path.is_symlink():
                continue

            # Delete if known binary extension
            if file_path.suffix.lower() in binary_extensions:
                try:
                    file_path.unlink(missing_ok=True)
                    deleted_binaries += 1
                    continue
                except:
                    pass

            # Delete if file is larger than 25MB (massive non-our databases/blobs)
            try:
                if file_path.exists() and file_path.stat().st_size > 25 * 1024 * 1024:
                    file_path.unlink()
                    massive_files += 1
            except OSError:
                pass

    print(f"[X] Stripped {deleted_binaries} binaries/databases and {massive_files} massive >25MB artifacts.")

    # 3. Replace 'https://github.com/karpathy/autoresearch' with 'https://github.com/karpathy/autoresearch'
    flying_monkey_pattern = re.compile(r"https://github.com/karpathy/autoresearch", re.IGNORECASE)
    replaced_monkeys = 0

    # We will only scan text-like files to avoid corruption
    text_extensions = {
        ".py",
        ".md",
        ".json",
        ".yaml",
        ".yml",
        ".ts",
        ".tsx",
        ".js",
        ".jsx",
        ".html",
        ".css",
        ".sh",
        ".txt",
        ".csv",
    }

    for filepath in root_path.rglob("*"):
        if filepath.is_file() and not filepath.is_symlink():
            if filepath.suffix.lower() in text_extensions or filepath.suffix == "":
                try:
                    content = filepath.read_text(encoding="utf-8")
                    if flying_monkey_pattern.search(content):
                        new_content = flying_monkey_pattern.sub("https://github.com/karpathy/autoresearch", content)
                        filepath.write_text(new_content, encoding="utf-8")
                        replaced_monkeys += 1
                except (UnicodeDecodeError, PermissionError):
                    pass

    print(f"[X] Re-routed {replaced_monkeys} 'https://github.com/karpathy/autoresearch' literals to 'karpathy/autoresearch'.")
    print("=============================================")
    print(" CRITICAL PAYLOAD TRIM COMPLETE.")
    print("=============================================")


if __name__ == "__main__":
    monorepo_root = Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball")
    run_nuclear_trim(monorepo_root)
