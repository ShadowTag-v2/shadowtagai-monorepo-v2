import os

ROOT = "/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
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

renamed_dirs = 0
renamed_files = 0


def merge_directories(src, dst) -> None:
    if not os.path.exists(dst):
        os.rename(src, dst)
        return
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            merge_directories(s, d)
        elif not os.path.exists(d):
            os.rename(s, d)
        else:
            os.unlink(d)  # overwrite
            os.rename(s, d)
    os.rmdir(src)


for root, dirs, files in os.walk(ROOT, topdown=False):
    # Rename files
    for name in files:
        if "pnkln" in name.lower() or "pnkln" in name.lower():
            new_name = name.replace("pnkln", "pnkln").replace("pnkln", "pnkln").replace("pnkln", "pnkln").replace("pnkln", "pnkln")
            old_path = os.path.join(root, name)
            new_path = os.path.join(root, new_name)
            if old_path != new_path and not os.path.exists(new_path):
                os.rename(old_path, new_path)
                renamed_files += 1

    # Rename dirs
    for name in dirs:
        if name in EXCLUDE_DIRS:
            continue
        if "pnkln" in name.lower() or "pnkln" in name.lower():
            new_name = name.replace("pnkln", "pnkln").replace("pnkln", "pnkln").replace("pnkln", "pnkln").replace("pnkln", "pnkln")
            old_path = os.path.join(root, name)
            new_path = os.path.join(root, new_name)
            if old_path != new_path:
                merge_directories(old_path, new_path)
                renamed_dirs += 1

