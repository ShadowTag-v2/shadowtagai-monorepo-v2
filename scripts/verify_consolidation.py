# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os
import time

MONOREPO_ROOT = "/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
SOURCE_DIRS = [
  "/Users/pikeymickey/aiyou-stack/ShadowTag-v2",
  "/Users/pikeymickey/.gemini",
  "/Users/Deleted Users/pikeymickey",
]

IGNORE_DIRS = {
  ".git",
  "node_modules",
  ".venv",
  "__pycache__",
  "build",
  "dist",
  ".next",
  ".chroma_db",
  ".beads",
}


def get_file_metadata(root_dir):
  """Recursively sweep a directory and return a dict of {filename: set(sizes)}."""
  metadata = {}
  if not os.path.exists(root_dir):
    print(f"⚠️ Source not found/accessible: {root_dir}")
    return metadata

  for root, dirs, files in os.walk(root_dir):
    # Mutating dirs in place skips ignored directories completely
    dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

    for file in files:
      # Skip massive invisible index files or lock files
      if file.endswith((".lock", ".pyc", ".sock", ".pid")) or file == ".DS_Store":
        continue

      filepath = os.path.join(root, file)
      try:
        size = os.path.getsize(filepath)
        if file not in metadata:
          metadata[file] = set()
        metadata[file].add(size)
      except OSError:
        continue  # Skip symlinks or permission denied files
  return metadata


def verify():
  print("🔍 [PHASE 1] Indexing Monorepo Target...")
  start_time = time.time()
  monorepo_files = get_file_metadata(MONOREPO_ROOT)
  print(f"✅ Monorepo Indexed: {len(monorepo_files)} unique file names found.")
  print(f"⏱️ Time taken: {time.time() - start_time:.2f}s\n")

  for source_dir in SOURCE_DIRS:
    print(f"🔍 [PHASE 2] Auditing Source Directory: {source_dir}")
    start_time = time.time()
    source_files = get_file_metadata(source_dir)

    if not source_files:
      continue

    found_count = 0
    missing_count = 0
    missing_files_sample = []

    for filename, sizes in source_files.items():
      # A match is when the filename exists in the repo
      # For stricter checking, we could check if AT LEAST ONE size matches, but since
      # linters ran (formatting changes size), filename presence is a better heuristic.
      if filename in monorepo_files:
        found_count += 1
      else:
        missing_count += 1
        if len(missing_files_sample) < 10:
          missing_files_sample.append(filename)

    total_files = found_count + missing_count
    match_rate = (found_count / total_files * 100) if total_files > 0 else 0

    print(f"📊 Results for {source_dir}:")
    print(f"   - Total Relevant Files Scanned: {total_files}")
    print(f"   - Migrated/Existing in Repo:    {found_count}")
    print(f"   - Left Behind (Missing):        {missing_count}")
    print(f"   - Match Confidence Rate:        {match_rate:.2f}%")

    if missing_count > 0:
      print("   - Sample of Missing Files:")
      for m_file in missing_files_sample:
        print(f"       ❌ {m_file}")

    print(f"⏱️ Time taken: {time.time() - start_time:.2f}s\n")


if __name__ == "__main__":
  verify()
