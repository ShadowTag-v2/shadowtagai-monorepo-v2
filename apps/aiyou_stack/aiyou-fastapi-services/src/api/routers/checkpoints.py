"""Checkpoint API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.models.checkpoint import (
    CheckpointCreate,
    CheckpointListResponse,
    CheckpointResponse,
    CheckpointRestore,
    FileSnapshotResponse,
)
from src.models.database import get_db
from src.services.checkpointing_service import CheckpointingService

router = APIRouter(prefix="/checkpoints", tags=["checkpoints"])


def get_checkpoint_service(db: Session = Depends(get_db)) -> CheckpointingService:
    """Get checkpoint service instance."""
    return CheckpointingService(db=db)


@router.post("", response_model=CheckpointResponse, status_code=status.HTTP_201_CREATED)
async def create_checkpoint(
    checkpoint_data: CheckpointCreate,
    service: CheckpointingService = Depends(get_checkpoint_service),
):
    """Create a new checkpoint.

    Creates a checkpoint that captures the state of specified files.
    Checkpoints are automatically created before edits and can be used
    to restore previous states.

    Args:
        checkpoint_data: Checkpoint creation data including session ID and file paths
        service: Checkpoint service instance

    Returns:
        Created checkpoint details

    """
    try:
        checkpoint = await service.create_checkpoint(checkpoint_data)
        return checkpoint
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkpoint: {e!s}",
        ) from e


@router.get("/{checkpoint_id}", response_model=CheckpointResponse)
async def get_checkpoint(
    checkpoint_id: str,
    service: CheckpointingService = Depends(get_checkpoint_service),
):
    """Get checkpoint details by ID.

    Args:
        checkpoint_id: Checkpoint identifier
        service: Checkpoint service instance

    Returns:
        Checkpoint details

    Raises:
        HTTPException: If checkpoint not found

    """
    checkpoint = service.get_checkpoint(checkpoint_id)

    if not checkpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Checkpoint {checkpoint_id} not found",
        )

    return checkpoint


@router.get("/sessions/{session_id}", response_model=CheckpointListResponse)
async def list_checkpoints(
    session_id: str,
    limit: int = 100,
    offset: int = 0,
    service: CheckpointingService = Depends(get_checkpoint_service),
):
    """List all checkpoints for a session.

    Args:
        session_id: Session identifier
        limit: Maximum number of checkpoints to return (default: 100)
        offset: Number of checkpoints to skip (default: 0)
        service: Checkpoint service instance

    Returns:
        List of checkpoints and total count

    """
    checkpoints, total = service.list_checkpoints(session_id=session_id, limit=limit, offset=offset)

    return CheckpointListResponse(checkpoints=checkpoints, total=total, session_id=session_id)


@router.post("/{checkpoint_id}/restore", response_model=CheckpointResponse)
async def restore_checkpoint(
    checkpoint_id: str,
    restore_data: CheckpointRestore,
    service: CheckpointingService = Depends(get_checkpoint_service),
):
    """Restore a checkpoint.

    Restores files to their state at the time of checkpoint creation.
    Can optionally restore conversation state as well.

    Args:
        checkpoint_id: Checkpoint identifier
        restore_data: Restore options (code, conversation, or both)
        service: Checkpoint service instance

    Returns:
        Restored checkpoint details

    Raises:
        HTTPException: If checkpoint not found or restore fails

    """
    try:
        checkpoint = await service.restore_checkpoint(checkpoint_id, restore_data)
        return checkpoint
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to restore checkpoint: {e!s}",
        ) from e


@router.get("/{checkpoint_id}/files", response_model=list[FileSnapshotResponse])
async def get_checkpoint_files(
    checkpoint_id: str,
    service: CheckpointingService = Depends(get_checkpoint_service),
):
    """Get all file snapshots for a checkpoint.

    Args:
        checkpoint_id: Checkpoint identifier
        service: Checkpoint service instance

    Returns:
        List of file snapshots

    Raises:
        HTTPException: If checkpoint not found

    """
    # Verify checkpoint exists
    checkpoint = service.get_checkpoint(checkpoint_id)
    if not checkpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Checkpoint {checkpoint_id} not found",
        )

    # Get file snapshots
    snapshots = service.get_file_snapshots(checkpoint_id)
    return snapshots


@router.delete("/{checkpoint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_checkpoint(
    checkpoint_id: str,
    service: CheckpointingService = Depends(get_checkpoint_service),
):
    """Delete a checkpoint.

    Removes checkpoint metadata and deletes associated files from storage.

    Args:
        checkpoint_id: Checkpoint identifier
        service: Checkpoint service instance

    Raises:
        HTTPException: If checkpoint not found

    """
    deleted = service.delete_checkpoint(checkpoint_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Checkpoint {checkpoint_id} not found",
        )


@router.get("/sessions/{session_id}/stats")
async def get_session_stats(
    session_id: str,
    service: CheckpointingService = Depends(get_checkpoint_service),
):
    """Get checkpoint statistics for a session.

    Args:
        session_id: Session identifier
        service: Checkpoint service instance

    Returns:
        Session statistics including checkpoint count and storage usage

    """
    return service.get_session_stats(session_id)


@router.post("/cleanup", status_code=status.HTTP_200_OK)
async def cleanup_expired_checkpoints(
    service: CheckpointingService = Depends(get_checkpoint_service),
):
    """Clean up expired checkpoints.

    Removes checkpoints that have exceeded the retention period.
    This is typically run as a scheduled task.

    Args:
        service: Checkpoint service instance

    Returns:
        Number of checkpoints cleaned up

    """
    cleanup_count = service.cleanup_expired_checkpoints()

    return {"message": f"Cleaned up {cleanup_count} expired checkpoints", "count": cleanup_count}
