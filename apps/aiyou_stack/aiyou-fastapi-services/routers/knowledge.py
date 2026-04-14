"""Knowledge ingestion route.

POST /api/v1/workspaces/{workspace_id}/knowledge
    — uploads a plain-text or markdown file, chunks it, embeds with
      Vertex AI text-embedding-004, and stores in LanceDB.
"""

import traceback
import uuid

from fastapi import APIRouter, File, HTTPException, Path, UploadFile
from pydantic import BaseModel

from vector_db import get_gemini_embedding, vector_db_manager

knowledge_router = APIRouter(prefix="/api/v1/workspaces", tags=["knowledge"])


class IngestionResponse(BaseModel):
    status: str
    chunks_ingested: int
    source: str


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if len(chunk) >= 50:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


@knowledge_router.post("/{workspace_id}/knowledge", response_model=IngestionResponse)
async def ingest_document(workspace_id: str = Path(...), file: UploadFile = File(...)):
    try:
        content = await file.read()
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            text = content.decode("latin-1", errors="replace")

        chunks = chunk_text(text)

        documents = []
        for chunk in chunks:
            if not chunk.strip():
                continue
            emb_vector = get_gemini_embedding(chunk)
            documents.append(
                {
                    "id": str(uuid.uuid4()),
                    "workspace_id": workspace_id,
                    "source": file.filename or "",
                    "text": chunk,
                    "vector": emb_vector,
                },
            )

        if documents:
            vector_db_manager.add_documents(documents)

        return IngestionResponse(
            status="success",
            chunks_ingested=len(documents),
            source=file.filename or "",
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
