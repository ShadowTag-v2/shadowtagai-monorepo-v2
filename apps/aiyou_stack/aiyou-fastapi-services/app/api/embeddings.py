"""Embeddings API endpoints for vector operations and semantic search.
"""

import structlog
from fastapi import APIRouter, HTTPException

from app.schemas.chat import (
    DocumentAddRequest,
    EmbeddingRequest,
    EmbeddingResponse,
    SearchRequest,
    SearchResponse,
)
from app.services.embeddings import EmbeddingsService

logger = structlog.get_logger()
router = APIRouter(prefix="/embeddings", tags=["embeddings"])

# Global embeddings service instance
embeddings_service = None


def get_embeddings_service() -> EmbeddingsService:
    """Get or create embeddings service instance."""
    global embeddings_service
    if embeddings_service is None:
        embeddings_service = EmbeddingsService()
    return embeddings_service


@router.post("/generate", response_model=EmbeddingResponse)
async def generate_embeddings(request: EmbeddingRequest):
    """Generate embeddings for text(s).

    Supports both single text and batch processing.
    """
    try:
        service = get_embeddings_service()

        if request.text and request.texts:
            raise HTTPException(
                status_code=400, detail="Provide either 'text' or 'texts', not both",
            )

        if request.text:
            embedding = await service.generate_embedding(request.text)
            return EmbeddingResponse(
                embedding=embedding, dimension=len(embedding), model=request.model or service.model,
            )
        if request.texts:
            embeddings = await service.generate_embeddings(request.texts)
            return EmbeddingResponse(
                embeddings=embeddings,
                dimension=len(embeddings[0]) if embeddings else 0,
                model=request.model or service.model,
            )
        raise HTTPException(status_code=400, detail="Either 'text' or 'texts' must be provided")

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Embedding generation failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/collections/{collection_name}/documents")
async def add_documents(collection_name: str, request: DocumentAddRequest):
    """Add documents to a vector collection.

    Creates embeddings and stores them with the documents.
    """
    try:
        service = get_embeddings_service()

        await service.add_documents(
            collection_name=collection_name,
            documents=request.documents,
            metadata=request.metadata,
            ids=request.ids,
        )

        return {
            "message": "Documents added successfully",
            "collection_name": collection_name,
            "count": len(request.documents),
        }

    except Exception as e:
        logger.error("Adding documents failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """Search for similar documents using semantic search.

    Uses vector similarity to find relevant documents.
    """
    try:
        service = get_embeddings_service()

        results = await service.search(
            collection_name=request.collection_name,
            query=request.query,
            n_results=request.n_results,
            where=request.where,
        )

        return SearchResponse(
            documents=results["documents"][0] if results["documents"] else [],
            distances=results["distances"][0] if results["distances"] else [],
            metadata=results["metadatas"][0] if results["metadatas"] else [],
            ids=results["ids"][0] if results["ids"] else [],
        )

    except Exception as e:
        logger.error("Search failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/collections")
async def list_collections():
    """List all vector collections.
    """
    try:
        service = get_embeddings_service()
        collections = service.list_collections()

        return {"collections": collections, "count": len(collections)}

    except Exception as e:
        logger.error("List collections failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/collections/{collection_name}")
async def delete_collection(collection_name: str):
    """Delete a vector collection.
    """
    try:
        service = get_embeddings_service()
        service.delete_collection(collection_name)

        return {"message": "Collection deleted successfully", "collection_name": collection_name}

    except Exception as e:
        logger.error("Delete collection failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/collections/{collection_name}")
async def create_collection(collection_name: str, metadata: dict = None):
    """Create a new vector collection.
    """
    try:
        service = get_embeddings_service()
        collection = service.create_collection(collection_name=collection_name, metadata=metadata)

        return {"message": "Collection created successfully", "collection_name": collection_name}

    except Exception as e:
        logger.error("Create collection failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
