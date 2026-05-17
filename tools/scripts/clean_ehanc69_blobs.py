#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import logging
import os
import shutil
from pathlib import Path

# Setup logging
logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s - [%(levelname)s] - %(message)s",
  handlers=[logging.StreamHandler()],  # Ensure logs go to stdout/stderr
)

TARGET_DIR = Path("apps/aiyou_stack")

# The exact folder names that must be annihilated on sight
DIRECTORIES_TO_NUKE = {
  "node_modules",
  ".git",  # Breaks monorepo indexing
  ".venv",
  "venv",
  "env",
  "__pycache__",
  ".next",  # NextJS build output
  "dist",
  "build",
  "coverage",
  ".cursor",  # Cursor IDE extensions which was the 50MB+ culprit
  ".vscode",  # IDE configs mapping to old paths
}

# The exact file extensions that must be annihilated
EXTENSIONS_TO_NUKE = {
  ".tar.gz",
  ".zip",
  ".mp4",
  ".mov",
  ".log",
  ".sqlite3",
  ".db",
  ".ttf",  # Fonts (can be huge)
  ".woff2",
}

# Files over this size in bytes will be deleted
MAX_FILE_SIZE = 25 * 1024 * 1024


def get_dir_size(path: Path) -> int:
  """
  Calculates the total size of a directory using os.walk for robustness.
  Ignores errors from broken symlinks or permission issues.
  """
  total_size = 0
  try:
    for dirpath, _, filenames in os.walk(path):
      for f in filenames:
        fp = Path(dirpath) / f
        try:
          # Check if it's a file and not a symlink to avoid double counting
          # or errors with broken links.
          if fp.is_file():
            total_size += fp.stat().st_size
        except (OSError, FileNotFoundError) as e:
          logging.warning(f"Could not get size of file {fp}: {e}")
  except Exception as e:
    logging.error(f"Could not walk directory {path} to get size: {e}")
  return total_size


def analyze_and_destroy(root_path: Path):
  """
  Recursively walks the directory tree and executes the purge using an efficient
  top-down approach. Prunes entire directories from the walk once they are deleted.
  """
  bytes_saved = 0
  items_deleted = 0

  if not root_path.exists() or not root_path.is_dir():
    logging.error(f"Target path '{root_path}' does not exist or is not a directory.")
    return

  logging.info(f"Targeting orbital strike on: {root_path.resolve()}")

  # Use os.walk with topdown=True to allow pruning directories.
  # onerror is a good addition for robustness.
  for root, dirs, files in os.walk(
    str(root_path), topdown=True, onerror=logging.warning
  ):
    current_dir = Path(root)

    # 1. Annihilate entire directories and prune them from the walk.
    # Iterate over a copy of `dirs` because we modify it in-place.
    for dir_name in list(dirs):
      if dir_name in DIRECTORIES_TO_NUKE:
        dir_path = current_dir / dir_name
        try:
          size = get_dir_size(dir_path)
          shutil.rmtree(dir_path)
          bytes_saved += size
          items_deleted += 1
          logging.info(
            f"Nuked directory and its contents: {dir_path.relative_to(root_path)}"
          )
          # This is the key optimization: prevent os.walk from descending further.
          dirs.remove(dir_name)
        except Exception as e:
          logging.warning(f"Failed to delete directory {dir_path}: {e}")

    # 2. Annihilate individual bloated files in the current directory.
    for filename in files:
      file_path = current_dir / filename

      # Use try/except for stat to handle broken symlinks gracefully.
      try:
        # Ensure it's a file, not a symlink to a directory or a broken link
        if not file_path.is_file():
          continue
        file_size = file_path.stat().st_size
      except (FileNotFoundError, OSError) as e:
        logging.debug(
          f"Could not stat file (likely broken symlink): {file_path}. Error: {e}"
        )
        continue

      # Decide whether to delete the file
      do_delete = False
      reason = ""
      if file_path.suffix.lower() in EXTENSIONS_TO_NUKE:
        do_delete = True
        reason = f"extension ({file_path.suffix.lower()})"
      elif file_size > MAX_FILE_SIZE:
        do_delete = True
        reason = f"size (> {MAX_FILE_SIZE // 1024 // 1024}MB)"

      if do_delete:
        try:
          file_path.unlink()
          bytes_saved += file_size
          items_deleted += 1
          # Use relative path for cleaner logs
          logging.info(f"Nuked file: ./{file_path.relative_to(root_path)} ({reason})")
        except Exception as e:
          logging.warning(f"Failed to delete file {file_path}: {e}")

  gb_saved = bytes_saved / (1024 * 1024 * 1024)
  logging.info("ORBITAL STRIKE COMPLETE.")
  logging.info(f"Total items vaporized: {items_deleted}")
  logging.info(f"Total disk space reclaimed: {gb_saved:.4f} GB")


if __name__ == "__main__":
  if not TARGET_DIR.exists():
    logging.error(f"The target directory '{TARGET_DIR}' does not exist. Aborting.")
  else:
    analyze_and_destroy(TARGET_DIR)
