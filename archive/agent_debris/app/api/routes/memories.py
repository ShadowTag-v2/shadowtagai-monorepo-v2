"""Memory API routes."""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.schemas.memory import (
    MemoryCreate,
    MemoryUpdate,
    MemoryResponse,
    MemorySynthesisResponse,
)
from app.services import memory_service

router = APIRouter(prefix="/memories", tags=["memories"])


# Mock user dependency (replace with real auth)
async def get_current_user_id() -> int:
    """Get current user ID from auth token."""
    return 1  # TODO: Implement real authentication


@router.post("/", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(memory_data: MemoryCreate, db: AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    """Create a new memory."""
    memory = await memory_service.create_memory(db, user_id, memory_data)
    return memory


@router.get("/", response_model=list[MemoryResponse])
async def get_memories(
    project_id: int | None = None,
    memory_type: str | None = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Get user memories with optional filtering."""
    memories = await memory_service.get_memories(db, user_id, project_id, memory_type, limit, offset)
    return memories


@router.get("/synthesis", response_model=MemorySynthesisResponse)
async def get_memory_synthesis(project_id: int | None = None, db: AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    """Get a synthesis of all user memories."""
    synthesis = await memory_service.synthesize_user_memories(db, user_id, project_id)
    return synthesis


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(memory_id: int, db: AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    """Get a specific memory by ID."""
    from sqlalchemy import select, and_
    from app.models import Memory

    stmt = select(Memory).where(and_(Memory.id == memory_id, Memory.user_id == user_id))
    result = await db.execute(stmt)
    memory = result.scalar_one_or_none()

    if not memory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found")

    return memory


@router.patch("/{memory_id}", response_model=MemoryResponse)
async def update_memory(memory_id: int, memory_data: MemoryUpdate, db: AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    """Update a memory."""
    memory = await memory_service.update_memory(db, memory_id, user_id, memory_data)

    if not memory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found")

    return memory


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(memory_id: int, db: AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    """Delete a memory."""
    success = await memory_service.delete_memory(db, memory_id, user_id)

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found")


@router.post("/extract/{conversation_id}", response_model=list[MemoryResponse])
async def extract_memories_from_conversation(
    conversation_id: int, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user_id)
):
    """Extract memories from a conversation."""
    memories = await memory_service.auto_extract_memories_from_conversation(db, conversation_id, user_id)

    return memories
