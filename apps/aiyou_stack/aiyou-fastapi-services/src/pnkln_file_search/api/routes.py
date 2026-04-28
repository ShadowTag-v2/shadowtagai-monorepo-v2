# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""API routes for file search service"""

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request

from pnkln_file_search.api.models import (
    CorpusCreateRequest,
    CorpusInfo,
    FileImportRequest,
    HealthResponse,
    QueryRequest,
    QueryResponse,
    VerticalInfo,
)
from pnkln_file_search.config.verticals import VERTICALS, get_vertical_config
from pnkln_file_search.corpus.manager import CorpusManager
from pnkln_file_search.monitoring.kill_switch import KillSwitch
from pnkln_file_search.orchestrator.query_handler import QueryHandler

logger = structlog.get_logger(__name__)

router = APIRouter()


def get_corpus_manager(request: Request) -> CorpusManager:
    """Dependency to get corpus manager"""
    return request.app.state.corpus_manager


def get_kill_switch(request: Request) -> KillSwitch:
    """Dependency to get kill switch"""
    return request.app.state.kill_switch


@router.post("/query", response_model=QueryResponse)
async def process_query(
    query_req: QueryRequest,
    corpus_manager: CorpusManager = Depends(get_corpus_manager),  # noqa: B008
    kill_switch: KillSwitch = Depends(get_kill_switch),  # noqa: B008
):
    """Process a query with file search and Judge 6 enforcement

    This endpoint orchestrates:
    1. File search for policy context (async)
    2. Judge 6 Layer 1 assessment (async, parallel with file search)
    3. Judge 6 Layers 2+3 enforcement (sequential)
    """
    try:
        # Check if file search is enabled
        if not kill_switch.is_enabled():
            raise HTTPException(
                status_code=503,
                detail="File search is currently disabled due to health issues",
            )

        # Create query handler
        handler = QueryHandler(corpus_manager)
        await handler.initialize()

        # Process query
        result = await handler.process_query_with_context(
            user_query=query_req.query,
            vertical=query_req.vertical,
            corpus_name=query_req.corpus_name,
        )

        logger.info(
            "query_processed",
            vertical=query_req.vertical,
            allowed=result["enforcement"]["allowed"],
            total_ms=result["timing"]["total_ms"],
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error("query_processing_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Query processing failed: {e!s}") from e


@router.get("/corpus", response_model=list[CorpusInfo])
async def list_corpora(
    corpus_manager: CorpusManager = Depends(get_corpus_manager),  # noqa: B008
):
    """List all corpora"""
    try:
        corpora = await corpus_manager.list_corpora()
        return corpora
    except Exception as e:
        logger.error("corpus_list_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list corpora: {e!s}") from e


@router.post("/corpus", response_model=dict[str, str])
async def create_corpus(
    create_req: CorpusCreateRequest,
    corpus_manager: CorpusManager = Depends(get_corpus_manager),  # noqa: B008
):
    """Create a new corpus for a vertical"""
    try:
        vertical_config = get_vertical_config(create_req.vertical)
        corpus_name = await corpus_manager.create_corpus(
            vertical_config,
            force_recreate=create_req.force_recreate,
        )

        return {
            "corpus_name": corpus_name,
            "vertical": create_req.vertical,
            "status": "created",
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error("corpus_creation_error", error=str(e), vertical=create_req.vertical)
        raise HTTPException(status_code=500, detail=f"Failed to create corpus: {e!s}") from e


@router.post("/corpus/import")
async def import_files(
    import_req: FileImportRequest,
    corpus_manager: CorpusManager = Depends(get_corpus_manager),  # noqa: B008
):
    """Import files into a corpus"""
    try:
        await corpus_manager.import_files(
            corpus_name=import_req.corpus_name,
            file_paths=import_req.file_paths,
            chunk_size=import_req.chunk_size,
            chunk_overlap=import_req.chunk_overlap,
        )

        return {
            "corpus_name": import_req.corpus_name,
            "files_imported": len(import_req.file_paths),
            "status": "success",
        }

    except Exception as e:
        logger.error(
            "file_import_error",
            error=str(e),
            corpus=import_req.corpus_name,
        )
        raise HTTPException(status_code=500, detail=f"Failed to import files: {e!s}") from e


@router.delete("/corpus/{corpus_name}")
async def delete_corpus(
    corpus_name: str,
    corpus_manager: CorpusManager = Depends(get_corpus_manager),  # noqa: B008
):
    """Delete a corpus"""
    try:
        await corpus_manager.delete_corpus(corpus_name)

        return {
            "corpus_name": corpus_name,
            "status": "deleted",
        }

    except Exception as e:
        logger.error("corpus_deletion_error", error=str(e), corpus=corpus_name)
        raise HTTPException(status_code=500, detail=f"Failed to delete corpus: {e!s}") from e


@router.get("/verticals", response_model=list[VerticalInfo])
async def list_verticals():
    """List all available verticals"""
    return [
        VerticalInfo(
            name=v.name,
            display_name=v.display_name,
            regulations=v.regulations,
            description=v.description,
        )
        for v in VERTICALS
    ]


@router.get("/verticals/{vertical_name}", response_model=VerticalInfo)
async def get_vertical(vertical_name: str):
    """Get information about a specific vertical"""
    try:
        vertical = get_vertical_config(vertical_name)
        return VerticalInfo(
            name=vertical.name,
            display_name=vertical.display_name,
            regulations=vertical.regulations,
            description=vertical.description,
        )
    except ValueError:
        raise HTTPException(
            status_code=404, detail=f"Vertical not found: {vertical_name}"
        ) from None


@router.get("/monitoring/health", response_model=HealthResponse)
async def get_health(
    kill_switch: KillSwitch = Depends(get_kill_switch),  # noqa: B008
):
    """Get detailed health status"""
    health_check = kill_switch.check_health()
    return health_check


@router.post("/monitoring/kill-switch/enable")
async def enable_kill_switch(
    kill_switch: KillSwitch = Depends(get_kill_switch),  # noqa: B008
):
    """Manually enable file search"""
    kill_switch.force_enable()
    return {"status": "enabled", "state": kill_switch.get_state()}


@router.post("/monitoring/kill-switch/disable")
async def disable_kill_switch(
    kill_switch: KillSwitch = Depends(get_kill_switch),  # noqa: B008
):
    """Manually disable file search"""
    kill_switch.force_disable()
    return {"status": "disabled", "state": kill_switch.get_state()}
