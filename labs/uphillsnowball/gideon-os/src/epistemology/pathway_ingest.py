# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# src/epistemology/pathway_ingest.py
# ============================================================================
# Pathway LLM-App — Real-Time Ingestion Sync
# ============================================================================
# Block 5 of the Ex Toto Omni-Compile (Gideon OS Architecture)
# Keeps NotebookLM sources synchronized with live data drop folders.
# ============================================================================
import logging
import subprocess

logger = logging.getLogger("Pathway-Sync")


def sync_to_notebooklm(file_path: str) -> str:
    """Push new data to NotebookLM Master Brain."""
    logger.info(f"🔄 [PATHWAY] New data detected at {file_path}. Pushing to NotebookLM Master Brain.")
    subprocess.run(
        [
            "notebooklm",
            "source",
            "add",
            file_path,
            "--notebook-id",
            "MASTER_BRAIN_ID",
        ],
        check=False,
    )
    return file_path


class PathwaySyncEngine:
    """Real-time filesystem watcher that syncs to NotebookLM."""

    def run_pipeline(self):
        import pathway as pw

        data = pw.io.fs.read(
            "./live_research_drop/",
            format="binary",
            mode="streaming",
            with_metadata=True,
        )
        _processed = data.select(synced_path=pw.apply(sync_to_notebooklm, pw.this.metadata.path))
        pw.run()


if __name__ == "__main__":
    PathwaySyncEngine().run_pipeline()
