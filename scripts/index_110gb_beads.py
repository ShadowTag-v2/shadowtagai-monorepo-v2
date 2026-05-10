import json

import os

import sqlite3

import subprocess

import sys

from datetime import datetime

# Try to load the ANE Router
sys.path.append(
  os.path.abspath("apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services")
)
try:
  from zero_cpu_router import dispatch_compute

  ANE_ENABLED = True
except ImportError:
  ANE_ENABLED = False

import pathlib


ROOT_DIR = str(pathlib.Path(__file__).parent.parent.absolute())
BEADS_DIR = os.path.join(ROOT_DIR, ".beads")
INDEX_DB = os.path.join(BEADS_DIR, "beads_index.sqlite")


def init_db():
  os.makedirs(os.path.dirname(INDEX_DB), exist_ok=True)
  conn = sqlite3.connect(INDEX_DB)
  c = conn.cursor()
  c.execute(
    """CREATE TABLE IF NOT EXISTS beads_registry
                 (filepath TEXT UNIQUE, size_bytes INT, biome_status TEXT, ane_semantic_class TEXT, last_indexed TIMESTAMP)""",
  )
  conn.commit()
  return conn


def biome_check(filepath: str) -> str:
  """COMMON SENSE FALLBACK: Use local CPU and Biome to instantly validate JSON/JSONL structure."""
  if not filepath.endswith((".json", ".jsonl")):
    return "N/A"

  # Run Biome natively for extreme speed
  try:
    result = subprocess.run(
      ["npx", "@biomejs/biome", "check", filepath], capture_output=True, text=True
    )
    return "PASS" if result.returncode == 0 else "FAIL_SYNTAX"
  except Exception as e:
    return f"ERROR: {e!s}"


def ane_semantic_scan(filepath: str, filename: str) -> str:
  """Heavy Lift: Route to Apple Neural Engine via Pickle Rick Bypass."""
  if not ANE_ENABLED:
    return "CPU_HEURISTIC_GUESS"

  # Fast heuristic block
  if "ast_fossil_record" in filename:
    return "ARCHITECTURAL_AST_DUMP"
  if "history.jsonl" in filename:
    return "AGENT_CONVERSATION_HISTORY"
  if "doctrinal_manuals" in filepath:
    return "PINKLN_DOCTRINE"

  ane_code = f"""
import json
import logging

filename = "{filename}"
if "master" in filename.lower() or "doctrine" in filename.lower():
    cat = "CORE_SYSTEM_RULES"
elif "architecture" in filename.lower():
    cat = "SYSTEM_TOPOLOGY"
else:
    cat = "UNCATEGORIZED_INTELLIGENCE"
logging.info(json.dumps({{"category": cat}}))
"""
  result = dispatch_compute(
    text=ane_code,
    prompt_description=f"bead_{filename[:10]}",
    examples=[],
    file_name=filename,
  )
  if isinstance(result, list) and len(result) > 0:
    result_dict = result[0]
    if result_dict.get("attrs", {}).get("compute_target") == "ANE-NPU":
      try:
        return json.loads(result_dict.get("text")).get("category", "UNKNOWN")
      except Exception:
        return "ANE_DECODE_ERROR"
  return "UNKNOWN"


def index_library() -> None:
  conn = init_db()
  c = conn.cursor()

  for root, _dirs, files in os.walk(BEADS_DIR):
    for file in files:
      # Skip massive WAL files or internal DB locks to prevent blocking
      if file.endswith((".db-wal", ".db-shm", ".lock", ".sock", ".pid")):
        continue

      filepath = os.path.join(root, file)
      size = os.path.getsize(filepath)

      biome_status = biome_check(filepath)
      ane_class = ane_semantic_scan(filepath, file)

      c.execute(
        """INSERT OR REPLACE INTO beads_registry
                         (filepath, size_bytes, biome_status, ane_semantic_class, last_indexed)
                         VALUES (?, ?, ?, ?, ?)""",
        (filepath, size, biome_status, ane_class, datetime.now()),
      )
      conn.commit()

      if biome_status == "FAIL_SYNTAX":
        pass

  conn.close()


if __name__ == "__main__":
  index_library()
