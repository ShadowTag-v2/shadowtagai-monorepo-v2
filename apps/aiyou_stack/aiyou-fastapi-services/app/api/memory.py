"""Memory API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.memory import MemoryCategory
from app.schemas.memory import (
    MemoryEntryCreate,
    MemoryEntryResponse,
    MemoryEntryUpdate,
    MemoryListResponse,
    MemorySynthesisRequest,
    MemorySynthesisResponse,
)
from app.services.memory_service import MemoryService
from app.services.synthesis_service import SynthesisService

router = APIRouter()


@router.get("/", response_model=MemoryListResponse)
async def get_memory(
    project_id: UUID | None = Query(None),
    category: MemoryCategory | None = Query(None),
    active_only: bool = Query(True),
    min_confidence: float | None = Query(None, ge=0.0, le=1.0),
    db: AsyncSession = Depends(get_db),
):
    """Get active memory entries."""
    service = MemoryService(db)
    entries = await service.list_memory_entries(
        project_id=project_id,
        category=category,
        active_only=active_only,
        min_confidence=min_confidence,
    )

    # Group by category
    by_category = {}
    for entry in entries:
        cat = entry.category.value
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(str(entry.id))

    return MemoryListResponse(
        entries=entries,
        total=len(entries),
        by_category=by_category,
    )


@router.post("/", response_model=MemoryEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory_entry(
    memory_data: MemoryEntryCreate,
    db: AsyncSession = Depends(get_db),
):
    """Manually create a memory entry."""
    service = MemoryService(db)
    memory = await service.create_memory_entry(memory_data)
    return memory


@router.put("/{memory_id}", response_model=MemoryEntryResponse)
async def update_memory_entry(
    memory_id: UUID,
    update_data: MemoryEntryUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a memory entry."""
    service = MemoryService(db)
    memory = await service.update_memory_entry(memory_id, update_data)
    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory entry not found",
        )
    return memory


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory_entry(
    memory_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a memory entry."""
    service = MemoryService(db)
    deleted = await service.delete_memory_entry(memory_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory entry not found",
        )


@router.post("/synthesize", response_model=MemorySynthesisResponse)
async def trigger_synthesis(
    request: MemorySynthesisRequest,
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger memory synthesis."""
    service = SynthesisService(db)
    result = await service.synthesize_memory(
        project_id=request.project_id,
        since=request.since,
        force=request.force,
    )

    return MemorySynthesisResponse(
        status="completed",
        entries_created=result["entries_created"],
        entries_updated=result["entries_updated"],
        conversations_processed=result["conversations_processed"],
    )
