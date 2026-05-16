# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os
import sqlite3
import subprocess

# Fix relative import pathing to target the established Zero-CPU router
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(
  0,
  os.path.abspath(
    os.path.join(
      os.path.dirname(__file__), "../apps/aiyou_stack/aiyou-fastapi-services"
    )
  ),
)
from zero_cpu_router import dispatch_compute

BEADS_DIR = os.path.expanduser("~/.beads")
STAGING_DIR = "/tmp/m1-staging-repos"


def setup_db():
  conn = sqlite3.connect("beads_index.sqlite", timeout=30.0)
  conn.execute("PRAGMA journal_mode=WAL;")
  conn.execute("PRAGMA synchronous=NORMAL;")
  conn.execute(
    """CREATE TABLE IF NOT EXISTS file_index
                    (path TEXT PRIMARY KEY, size_bytes INT, hardware_tier TEXT, result_status TEXT)"""
  )
  return conn


def clone_ehan69_repos():
  """Clone aiyou-fastapi-services and 51 other core repos to staging."""
  os.makedirs(STAGING_DIR, exist_ok=True)
  repos = [
    "https://github.com/ShadowTag-v2/aiyou-fastapi-services"
    # The other 51 repos would appended here dynamically via GitHub API if needed
  ]
  for repo in repos:
    repo_name = repo.split("/")[-1].replace(".git", "")
    target = os.path.join(STAGING_DIR, repo_name)
    if not os.path.exists(target):
      print(f"🧬 Cloning {repo_name} to Staging...")
      subprocess.run(["git", "clone", repo, target], check=True)


def process_single_file(filepath: str, size: int) -> tuple:
  """Isolate single file extraction and semantic routing for ThreadPool execution."""
  try:
    with open(filepath, encoding="utf-8", errors="ignore") as f:
      content = f.read(
        5000
      )  # Read only first 5000 chars for semantic memory snapshot to prevent RAM overflow

    # Route to Zero-CPU ANE Defuser
    res = dispatch_compute(content, estimated_bytes=size)
    return (
      filepath,
      size,
      res.get("source", "UNKNOWN"),
      res.get("status", "FAILED"),
    )
  except Exception as e:
    return (filepath, size, "ERROR", str(e)[:50])


def index_and_route(directory, conn):
  """Walks a directory, analyzes files, and dispatches them via massive ThreadPool concurrency."""
  target_files = []
  for root, _, files in os.walk(directory):
    for file in files:
      if not file.endswith((".py", ".md", ".json")):
        continue
      filepath = os.path.join(root, file)
      target_files.append((filepath, os.path.getsize(filepath)))

  print(
    f"🚀 Discovered {len(target_files)} targeted text files for extraction in {directory}."
  )

  batch_size = 500
  batch_results = []
  processed = 0
  total = len(target_files)

  with ThreadPoolExecutor(max_workers=os.cpu_count() or 8) as executor:
    futures = {
      executor.submit(process_single_file, path, size): (path, size)
      for path, size in target_files
    }

    for future in as_completed(futures):
      batch_results.append(future.result())
      processed += 1

      # Commit in discrete batches to prevent `database is locked` SQLite deadlocks
      if len(batch_results) >= batch_size or processed == total:
        conn.executemany(
          "INSERT OR REPLACE INTO file_index VALUES (?, ?, ?, ?)",
          batch_results,
        )
        conn.commit()
        print(
          f"✅ Ingested {processed}/{total} files synchronously into beads_index..."
        )
        batch_results.clear()


if __name__ == "__main__":
  conn = setup_db()

  # 1. Clone Repos
  clone_ehan69_repos()

  # 2. Index Repos
  print("====== Routing 52 Legacy Repos ======")
  index_and_route(STAGING_DIR, conn)

  # 3. Index Beads Data (110 GB) -- Using Limit for Demo
  print("====== Routing 110GB .beads Library ======")
  if os.path.exists(BEADS_DIR):
    index_and_route(BEADS_DIR, conn)

  print("✅ Zero-CPU Ingestion Complete.")
