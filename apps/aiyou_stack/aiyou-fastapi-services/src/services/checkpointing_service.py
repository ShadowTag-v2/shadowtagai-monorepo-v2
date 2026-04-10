"""Checkpointing service implementation."""

import os
import uuid
from datetime import datetime, timedelta

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.core.config import settings
from src.models.checkpoint import (
    Checkpoint,
    CheckpointCreate,
    CheckpointRestore,
    CheckpointStatus,
    FileSnapshot,
)
from src.storage.checkpoint_store import CheckpointStore


class CheckpointingService:
    """Service for managing checkpoints."""

    def __init__(self, db: Session, store: CheckpointStore | None = None):
        """Initialize checkpointing service.

        Args:
            db: Database session
            store: Checkpoint storage instance
        """
        self.db = db
        self.store = store or CheckpointStore()

    async def create_checkpoint(self, checkpoint_data: CheckpointCreate) -> Checkpoint:
        """Create a new checkpoint.

        Args:
            checkpoint_data: Checkpoint creation data

        Returns:
            Created checkpoint
        """
        # Generate checkpoint ID
        checkpoint_id = str(uuid.uuid4())

        # Calculate expiry date
        expires_at = datetime.utcnow() + timedelta(days=settings.checkpoint_retention_days)

        # Create checkpoint record
        checkpoint = Checkpoint(
            id=checkpoint_id,
            session_id=checkpoint_data.session_id,
            user_message=checkpoint_data.user_message,
            checkpoint_type=checkpoint_data.checkpoint_type.value,
            status=CheckpointStatus.ACTIVE.value,
            expires_at=expires_at,
            metadata=checkpoint_data.metadata,
        )

        # Save files and create snapshots
        total_size = 0
        file_count = 0

        for file_path in checkpoint_data.file_paths:
            # Check if file exists
            if not os.path.exists(file_path):
                continue

            # Generate snapshot ID
            snapshot_id = str(uuid.uuid4())

            try:
                # Save file to storage
                content_hash, size_bytes, storage_path = await self.store.save_file(
                    checkpoint_id=checkpoint_id, file_path=file_path, snapshot_id=snapshot_id
                )

                # Create file snapshot record
                file_snapshot = FileSnapshot(
                    id=snapshot_id,
                    checkpoint_id=checkpoint_id,
                    file_path=file_path,
                    content_hash=content_hash,
                    size_bytes=size_bytes,
                    storage_path=storage_path,
                )

                self.db.add(file_snapshot)
                total_size += size_bytes
                file_count += 1

            except Exception as e:
                # Log error but continue with other files
                print(f"Error saving file {file_path}: {e}")
                continue

        # Update checkpoint statistics
        checkpoint.file_count = file_count
        checkpoint.total_size_bytes = total_size

        # Save checkpoint
        self.db.add(checkpoint)
        self.db.commit()
        self.db.refresh(checkpoint)

        return checkpoint

    async def restore_checkpoint(
        self, checkpoint_id: str, restore_data: CheckpointRestore
    ) -> Checkpoint:
        """Restore a checkpoint.

        Args:
            checkpoint_id: Checkpoint identifier
            restore_data: Restore options

        Returns:
            Restored checkpoint

        Raises:
            ValueError: If checkpoint not found or invalid
        """
        # Get checkpoint
        checkpoint = self.db.query(Checkpoint).filter(Checkpoint.id == checkpoint_id).first()

        if not checkpoint:
            raise ValueError(f"Checkpoint {checkpoint_id} not found")

        if checkpoint.status == CheckpointStatus.EXPIRED.value:
            raise ValueError(f"Checkpoint {checkpoint_id} has expired")

        # Restore code if requested
        if restore_data.restore_code:
            # Get all file snapshots for this checkpoint
            snapshots = (
                self.db.query(FileSnapshot)
                .filter(FileSnapshot.checkpoint_id == checkpoint_id)
                .all()
            )

            for snapshot in snapshots:
                try:
                    # Restore file from storage
                    await self.store.restore_file(
                        storage_path=snapshot.storage_path, target_path=snapshot.file_path
                    )
                except Exception as e:
                    print(f"Error restoring file {snapshot.file_path}: {e}")
                    continue

        # Update checkpoint status
        checkpoint.status = CheckpointStatus.RESTORED.value
        checkpoint.restored_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(checkpoint)

        return checkpoint

    def get_checkpoint(self, checkpoint_id: str) -> Checkpoint | None:
        """Get a checkpoint by ID.

        Args:
            checkpoint_id: Checkpoint identifier

        Returns:
            Checkpoint or None if not found
        """
        return (
            self.db.query(Checkpoint)
            .filter(Checkpoint.id == checkpoint_id, not Checkpoint.is_deleted)
            .first()
        )

    def list_checkpoints(
        self, session_id: str, limit: int = 100, offset: int = 0
    ) -> tuple[list[Checkpoint], int]:
        """List checkpoints for a session.

        Args:
            session_id: Session identifier
            limit: Maximum number of checkpoints to return
            offset: Number of checkpoints to skip

        Returns:
            Tuple of (checkpoints, total_count)
        """
        query = (
            self.db.query(Checkpoint)
            .filter(Checkpoint.session_id == session_id, not Checkpoint.is_deleted)
            .order_by(Checkpoint.created_at.desc())
        )

        total = query.count()
        checkpoints = query.limit(limit).offset(offset).all()

        return checkpoints, total

    def get_file_snapshots(self, checkpoint_id: str) -> list[FileSnapshot]:
        """Get all file snapshots for a checkpoint.

        Args:
            checkpoint_id: Checkpoint identifier

        Returns:
            List of file snapshots
        """
        return self.db.query(FileSnapshot).filter(FileSnapshot.checkpoint_id == checkpoint_id).all()

    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a checkpoint.

        Args:
            checkpoint_id: Checkpoint identifier

        Returns:
            True if deleted, False if not found
        """
        checkpoint = self.get_checkpoint(checkpoint_id)

        if not checkpoint:
            return False

        # Mark as deleted (soft delete)
        checkpoint.is_deleted = True
        self.db.commit()

        # Delete files from storage
        try:
            self.store.delete_checkpoint(checkpoint_id)
        except Exception as e:
            print(f"Error deleting checkpoint files: {e}")

        return True

    def cleanup_expired_checkpoints(self) -> int:
        """Clean up expired checkpoints.

        Returns:
            Number of checkpoints cleaned up
        """
        now = datetime.utcnow()

        # Find expired checkpoints
        expired_checkpoints = (
            self.db.query(Checkpoint)
            .filter(and_(Checkpoint.expires_at < now, not Checkpoint.is_deleted))
            .all()
        )

        cleanup_count = 0

        for checkpoint in expired_checkpoints:
            # Mark as expired and deleted
            checkpoint.status = CheckpointStatus.EXPIRED.value
            checkpoint.is_deleted = True

            # Delete from storage
            try:
                self.store.delete_checkpoint(checkpoint.id)
                cleanup_count += 1
            except Exception as e:
                print(f"Error cleaning up checkpoint {checkpoint.id}: {e}")

        self.db.commit()

        return cleanup_count

    def get_session_stats(self, session_id: str) -> dict:
        """Get checkpoint statistics for a session.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with session statistics
        """
        checkpoints = (
            self.db.query(Checkpoint)
            .filter(Checkpoint.session_id == session_id, not Checkpoint.is_deleted)
            .all()
        )

        total_size = sum(cp.total_size_bytes for cp in checkpoints)
        total_files = sum(cp.file_count for cp in checkpoints)

        return {
            "session_id": session_id,
            "checkpoint_count": len(checkpoints),
            "total_files": total_files,
            "total_size_bytes": total_size,
            "active_checkpoints": len(
                [cp for cp in checkpoints if cp.status == CheckpointStatus.ACTIVE.value]
            ),
            "restored_checkpoints": len(
                [cp for cp in checkpoints if cp.status == CheckpointStatus.RESTORED.value]
            ),
        }
