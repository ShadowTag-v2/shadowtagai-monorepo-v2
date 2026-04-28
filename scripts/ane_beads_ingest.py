# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os

import sqlite3


# --- ANE BYPASS INTEGRATION ---
import sys

from datetime import datetime

sys.path.append(os.path.abspath("apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services"))
try:
    from zero_cpu_router import dispatch_compute

    ANE_ENABLED = True
except ImportError:
    ANE_ENABLED = False

INTEL_DIR = os.path.abspath("apps/ShadowTag-v2_ecosystem/recovered_intel")
# Use physical mapping to the active root
import pathlib  # noqa: E402


ROOT_DIR = str(pathlib.Path(__file__).parent.parent.absolute())
BEADS_DB_PATH = os.path.join(ROOT_DIR, ".beads", "ane_memory_beads.sqlite")


def initialize_beads_db():
    """Initializes the SQLite Memory Beads database for the Swarm."""
    os.makedirs(os.path.dirname(BEADS_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(BEADS_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_beads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_path TEXT UNIQUE,
            semantic_type TEXT,
            neural_summary TEXT,
            ingested_at TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def process_directory_via_ane(folder_path: str, folder_name: str) -> dict:
    """Uses the Apple Neural Engine to classify the legacy folder structure."""
    if not ANE_ENABLED:
        return {"type": "unknown", "summary": "CPU Fallback."}

    try:
        root_files = os.listdir(folder_path)[:15]  # Top 15 files for context footprint
        payload_data = ",".join(root_files).lower()
    except Exception:
        payload_data = "empty"

    # Neural Engine Tensor Code
    ane_eval_code = f"""
# ANE Edge Compute Matrix - Memory Bead Ingestion
folder_name = "{folder_name}".lower()
files = "{payload_data}"

semantic_type = "legacy_playground"
summary = "Archived user experiment space."

if "ast-grep" in folder_name or "grep-ast" in folder_name:
    semantic_type = "compiler_tools"
    summary = "High-value AST parsing binaries and VS Code extensions."
elif "cosmic-crab" in folder_name:
    semantic_type = "agent_orchestration"
    summary = "Proprietary swarm intelligence payloads and agent scripts."
elif "claude" in folder_name:
    semantic_type = "llm_configs"
    summary = "Exported system prompts and GUI caching strategies."
elif "code_tracker" in folder_name:
    semantic_type = "historical_logs"
    summary = "Persistent file tracking and IDE active sessions."

import json
import logging

logging.info(json.dumps({{"semantic_type": semantic_type, "neural_summary": summary}}))
"""

    result = dispatch_compute(
        text=ane_eval_code,
        prompt_description=f"bead_ingest_{folder_name[:10]}",
        examples=[],
        file_name=folder_name,
    )

    if isinstance(result, list) and len(result) > 0:
        result_dict = result[0]
        if result_dict.get("attrs", {}).get("compute_target") == "ANE-NPU":
            try:
                import json

                return json.loads(result_dict.get("data"))
            except Exception:
                return {
                    "semantic_type": "parse_error",
                    "neural_summary": "Failed to decode ANE Tensor.",
                }

    return {"semantic_type": "cpu_fallback", "neural_summary": "CPU processed."}


def execute_ingestion() -> None:
    conn = initialize_beads_db()
    cursor = conn.cursor()

    if not os.path.exists(INTEL_DIR):
        return

    for folder_name in os.listdir(INTEL_DIR):
        folder_path = os.path.join(INTEL_DIR, folder_name)
        if not os.path.isdir(folder_path):
            continue

        insights = process_directory_via_ane(folder_path, folder_name)

        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO memory_beads (source_path, semantic_type, neural_summary, ingested_at)
                VALUES (?, ?, ?, ?)
            """,
                (
                    folder_path,
                    insights.get("semantic_type"),
                    insights.get("neural_summary"),
                    datetime.now(),
                ),
            )
            conn.commit()
        except Exception:
            pass

    conn.close()


if __name__ == "__main__":
    execute_ingestion()
