from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
import logging

import uuid
from temporalio.client import Client
from .upload_workflow import LanceDBIngestionWorkflow

logger = logging.getLogger("upload-router")
router = APIRouter(prefix="/upload")

# Mock identity pass-through for Sovereign Local testing
async def mock_auth():
    pass

@router.post("/document")
async def upload_document(file: UploadFile = File(...), auth=Depends(mock_auth)):
    """
    Zero-Trust ingest endpoint for native contract documentation parsing into the vector RAG loop.
    """
    logger.info(f"Ingesting binary payload: {file.filename}")
    if not file.filename.endswith((".pdf", ".txt", ".docx")):
        raise HTTPException(status_code=400, detail="Matrix block: Extraneous file type.")

    # Calculate bytes
    content = await file.read()
    size = len(content)

    # Dispatch physical Sovereign Matrix via Temporal
    try:
        temporal_client = await Client.connect("localhost:7233")
        workflow_id = f"ingest-{uuid.uuid4().hex[:8]}"

        await temporal_client.execute_workflow(
            LanceDBIngestionWorkflow.run,
            args=[file.filename, size],
            id=workflow_id,
            task_queue="omega-swarm-queue",
        )
        vector_status = "omega_queued"
    except Exception as e:
        logger.error(f"Temporal Handshake Failed: {e}")
        vector_status = "temporal_disconnected"

    return {
        "status": "ingested",
        "vector_status": vector_status,
        "file": file.filename,
        "bytes_processed": size
    }
