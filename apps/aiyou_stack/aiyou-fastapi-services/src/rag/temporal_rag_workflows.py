# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""
Temporal Workflows for LanceDB RAG Ingestion

Automates document ingestion into the LanceDB vector store via Temporal
durable workflows. Supports scheduled nightly ingestion, document-change
detection, and retry-with-backoff for embedding failures.

Usage:
    # Start a Temporal worker
    python -m temporal_rag_workflows

    # Or trigger from orchestrator
    from temporal_rag_workflows import ingest_documents_workflow
"""

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


# ── Activity Inputs ────────────────────────────────────────────


@dataclass
class IngestInput:
    """Input for document ingestion activity."""

    file_paths: list[str]
    table_name: str = "shadowtag_docs"
    chunk_size: int = 512
    chunk_overlap: int = 64


@dataclass
class IngestResult:
    """Result from document ingestion activity."""

    files_processed: int
    chunks_created: int
    vectors_stored: int
    errors: list[str]
    elapsed_seconds: float


@dataclass
class QueryInput:
    """Input for RAG query activity."""

    question: str
    top_k: int = 5
    table_name: str = "shadowtag_docs"


@dataclass
class QueryResult:
    """Result from RAG query activity."""

    answer: str
    sources: list[dict]
    num_sources: int


# ── Activities ─────────────────────────────────────────────────


async def ingest_documents_activity(input: IngestInput) -> IngestResult:
    """Activity: Ingest documents into LanceDB.

    This runs as a Temporal activity with automatic retry on failure.
    """
    import time

    # Import the pipeline lazily to avoid loading heavy ML models at module level
    from src.rag.lancedb_pipeline import Document, RAGPipeline

    start = time.time()
    errors = []

    pipeline = RAGPipeline(table_name=input.table_name)
    pipeline.chunker.chunk_size = input.chunk_size
    pipeline.chunker.overlap = input.chunk_overlap

    documents = []
    for filepath in input.file_paths:
        path = Path(filepath)
        try:
            if path.is_file():
                content = path.read_text(errors="replace")
                documents.append(Document(content=content, source=str(path)))
            elif path.is_dir():
                for f in path.rglob("*"):
                    if f.is_file() and f.suffix in {
                        ".py",
                        ".md",
                        ".txt",
                        ".yaml",
                        ".json",
                        ".html",
                    }:
                        content = f.read_text(errors="replace")
                        documents.append(Document(content=content, source=str(f)))
        except Exception as e:
            errors.append(f"{filepath}: {e}")
            logger.error("Failed to read %s: %s", filepath, e)

    chunks_created = 0
    if documents:
        chunks_created = pipeline.ingest(documents)

    elapsed = time.time() - start

    return IngestResult(
        files_processed=len(documents),
        chunks_created=chunks_created,
        vectors_stored=pipeline.store.count(),
        errors=errors,
        elapsed_seconds=round(elapsed, 2),
    )


async def query_rag_activity(input: QueryInput) -> QueryResult:
    """Activity: Query the RAG pipeline."""
    from src.rag.lancedb_pipeline import RAGPipeline

    pipeline = RAGPipeline(table_name=input.table_name)
    result = pipeline.query(input.question, top_k=input.top_k)

    return QueryResult(
        answer=result["answer"],
        sources=result["sources"],
        num_sources=result["num_sources"],
    )


async def scan_for_changes_activity(
    watch_dirs: list[str],
    since_hours: int = 24,
) -> list[str]:
    """Activity: Scan directories for recently modified files.

    Returns list of file paths modified in the last `since_hours`.
    """
    import os
    import time

    cutoff = time.time() - (since_hours * 3600)
    changed = []

    for dir_path in watch_dirs:
        path = Path(dir_path)
        if not path.exists():
            continue

        for f in path.rglob("*"):
            if (
                f.is_file()
                and f.suffix in {".py", ".md", ".txt", ".yaml", ".json", ".html"}
                and os.path.getmtime(f) > cutoff
            ):
                changed.append(str(f))

    logger.info("Found %d changed files in %d directories", len(changed), len(watch_dirs))
    return changed


# ── Workflows ──────────────────────────────────────────────────


async def ingest_documents_workflow(input: IngestInput) -> IngestResult:
    """Workflow: Ingest documents into the RAG pipeline.

    This is the top-level durable workflow that orchestrates ingestion
    with automatic retry, timeout, and error handling.

    In production, this would use @workflow.defn and @activity.defn
    decorators from the temporalio library. For now, this is a
    functional scaffold that can be wired to Temporal when ready.
    """
    logger.info(
        "Starting ingestion workflow: %d paths, table=%s",
        len(input.file_paths),
        input.table_name,
    )

    # Activity execution with retry policy
    # In production: workflow.execute_activity(
    #     ingest_documents_activity,
    #     input,
    #     start_to_close_timeout=timedelta(minutes=30),
    #     retry_policy=RetryPolicy(
    #         initial_interval=timedelta(seconds=5),
    #         maximum_interval=timedelta(minutes=2),
    #         maximum_attempts=3,
    #         backoff_coefficient=2.0,
    #     ),
    # )
    result = await ingest_documents_activity(input)

    if result.errors:
        logger.warning(
            "Ingestion completed with %d errors: %s",
            len(result.errors),
            result.errors[:5],
        )

    logger.info(
        "Ingestion workflow complete: %d files → %d chunks in %.1fs",
        result.files_processed,
        result.chunks_created,
        result.elapsed_seconds,
    )

    return result


async def nightly_ingestion_workflow(
    watch_dirs: list[str] | None = None,
    table_name: str = "shadowtag_docs",
) -> IngestResult | None:
    """Workflow: Nightly scheduled ingestion.

    Scans for changed files in the last 24 hours and ingests them.
    Designed to run on a Temporal cron schedule: "0 2 * * *" (2 AM daily).
    """
    if watch_dirs is None:
        watch_dirs = [
            "docs/",
            "apps/counselconduit/spec/",
            "apps/aiyou_stack/aiyou-fastapi-services/src/",
            "AGENTS.md",
            "BUSINESS_CONTEXT_LOCKED.md",
            "PRIVACY.md",
            "TERMS.md",
        ]

    # Step 1: Scan for changes
    changed_files = await scan_for_changes_activity(watch_dirs)

    if not changed_files:
        logger.info("No changed files found — skipping ingestion")
        return None

    # Step 2: Ingest changed files
    return await ingest_documents_workflow(
        IngestInput(file_paths=changed_files, table_name=table_name)
    )


# ── CLI / Worker ───────────────────────────────────────────────


async def main():
    """Run a manual ingestion workflow."""
    import argparse

    parser = argparse.ArgumentParser(description="Temporal RAG Workflows")
    sub = parser.add_subparsers(dest="command")

    ingest_cmd = sub.add_parser("ingest", help="Run ingestion workflow")
    ingest_cmd.add_argument("paths", nargs="+", help="Files/dirs to ingest")
    ingest_cmd.add_argument("--table", default="shadowtag_docs")

    nightly_cmd = sub.add_parser("nightly", help="Run nightly scan + ingest")
    nightly_cmd.add_argument("--table", default="shadowtag_docs")

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    if args.command == "ingest":
        result = await ingest_documents_workflow(
            IngestInput(file_paths=args.paths, table_name=args.table)
        )
        print(f"\n✅ Ingested {result.files_processed} files → {result.chunks_created} chunks")
        print(f"   Total vectors: {result.vectors_stored}")
        print(f"   Time: {result.elapsed_seconds}s")
        if result.errors:
            print(f"   ⚠️  Errors ({len(result.errors)}):")
            for e in result.errors[:5]:
                print(f"     • {e}")

    elif args.command == "nightly":
        result = await nightly_ingestion_workflow(table_name=args.table)
        if result:
            print(f"\n✅ Nightly: {result.files_processed} files → {result.chunks_created} chunks")
        else:
            print("\n✅ Nightly: No changes detected")

    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
