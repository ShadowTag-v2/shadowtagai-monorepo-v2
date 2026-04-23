"""FastAPI routes for notes management."""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models.storage import (
    AppendToNoteRequest,
    AppendToNoteResponse,
    CreateNoteRequest,
    CreateNoteResponse,
    GetNoteResponse,
    ListNotesResponse,
)
from app.services.storage_service import StorageService

router = APIRouter(prefix="/api/notes", tags=["notes"])


# Dependency to get storage service
def get_storage_service() -> StorageService:
    """Get the storage service instance."""
    # This will be overridden by dependency injection in main.py
    return None


@router.post("/", response_model=CreateNoteResponse)
async def create_note(
    request: CreateNoteRequest,
    storage: StorageService = Depends(get_storage_service),
):
    """Create a new note."""
    try:
        note_id = storage.create_note(
            folder=request.folder,
            title=request.title,
            content=request.content,
        )
        return CreateNoteResponse(note_id=note_id, message="Note created successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create note: {e!s}") from e


@router.post("/append", response_model=AppendToNoteResponse)
async def append_to_note(
    request: AppendToNoteRequest,
    storage: StorageService = Depends(get_storage_service),
):
    """Append content to an existing note."""
    try:
        note_id = storage.append_to_note(title=request.title, content=request.content)
        return AppendToNoteResponse(note_id=note_id, message="Content appended successfully")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to append to note: {e!s}") from e


@router.get("/by-title/{title}", response_model=GetNoteResponse)
async def get_note_by_title(title: str, storage: StorageService = Depends(get_storage_service)):
    """Get a note by its title."""
    note = storage.get_note_by_title(title)
    if not note:
        raise HTTPException(status_code=404, detail=f"Note with title '{title}' not found")

    return GetNoteResponse(note=note)


@router.get("/{note_id}", response_model=GetNoteResponse)
async def get_note_by_id(note_id: str, storage: StorageService = Depends(get_storage_service)):
    """Get a note by its ID."""
    note = storage.get_note_by_id(note_id)
    if not note:
        raise HTTPException(status_code=404, detail=f"Note with ID '{note_id}' not found")

    return GetNoteResponse(note=note)


@router.get("/", response_model=ListNotesResponse)
async def list_notes(
    folder: str | None = Query(None, description="Filter by folder"),
    storage: StorageService = Depends(get_storage_service),
):
    """List all notes, optionally filtered by folder."""
    notes = storage.list_notes(folder=folder)
    return ListNotesResponse(notes=notes, count=len(notes))


@router.delete("/{note_id}")
async def delete_note(note_id: str, storage: StorageService = Depends(get_storage_service)):
    """Delete a note."""
    success = storage.delete_note(note_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Note with ID '{note_id}' not found")

    return {"message": "Note deleted successfully"}
