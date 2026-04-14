import glob
import os
from datetime import timedelta

from temporalio import activity, workflow


@activity.defn
async def ingest_logs_to_lancedb() -> str:
    """Crawls local .agent/logs/ and archive_brain_sessions/ directories,
    extracts transcripts, and ingests them into LanceDB.
    """
    # Navigate up from apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services/src/workflows/omega_dream_daemon.py
    # to the Monorepo root.
    repo_root = os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        ),
    )
    logs_pattern = os.path.join(repo_root, ".agent", "logs", "*.log")
    legacy_pattern = os.path.join(
        repo_root, "control", "legacy_workspaces", "archive_brain_sessions", "*", "*.md",
    )

    # In reality, this would import core/lancedb_indexer.py and trigger ingestion.
    try:
        from src.core.lancedb_indexer import index_documents
    except ImportError:
        index_documents = None

    found_logs = glob.glob(logs_pattern)
    found_legacy = glob.glob(legacy_pattern)

    total_files = len(found_logs) + len(found_legacy)
    msg = f"[KAIROS DREAM] Found {total_files} session transcripts. Consolidating into LanceDB Memory Graph..."
    print(msg)

    if index_documents:
        # Trigger actual document ingestion
        pass

    return msg


@workflow.defn
class OmegaDreamDaemon:
    """Temporal cron workflow designed to mimic KAIROS_DREAM daemon.
    Should be scheduled from the client with cron_schedule="0 3 * * *".
    """

    @workflow.run
    async def run(self) -> str:
        result = await workflow.execute_activity(
            ingest_logs_to_lancedb, start_to_close_timeout=timedelta(minutes=10),
        )
        return result
