# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Core checkpointing manager."""

from src.models.checkpoint import CheckpointCreate, CheckpointType
from src.models.database import SessionLocal
from src.services.checkpointing_service import CheckpointingService


class CheckpointManager:
    """High-level checkpoint manager for easy integration."""

    def __init__(self):
        """Initialize checkpoint manager."""
        self.current_session_id: str | None = None

    def set_session(self, session_id: str) -> None:
        """Set the current session ID.

        Args:
            session_id: Session identifier

        """
        self.current_session_id = session_id

    async def auto_checkpoint(self, file_paths: list[str], user_message: str | None = None) -> str:
        """Create an automatic checkpoint before edits.

        Args:
            file_paths: List of file paths to checkpoint
            user_message: Optional user message associated with checkpoint

        Returns:
            Checkpoint ID

        Raises:
            ValueError: If session not set

        """
        if not self.current_session_id:
            raise ValueError("Session ID not set. Call set_session() first.")

        db = SessionLocal()
        try:
            service = CheckpointingService(db=db)

            checkpoint_data = CheckpointCreate(
                session_id=self.current_session_id,
                user_message=user_message,
                checkpoint_type=CheckpointType.AUTO,
                file_paths=file_paths,
            )

            checkpoint = await service.create_checkpoint(checkpoint_data)
            return checkpoint.id

        finally:
            db.close()

    async def manual_checkpoint(
        self,
        file_paths: list[str],
        user_message: str | None = None,
    ) -> str:
        """Create a manual checkpoint.

        Args:
            file_paths: List of file paths to checkpoint
            user_message: Optional user message associated with checkpoint

        Returns:
            Checkpoint ID

        Raises:
            ValueError: If session not set

        """
        if not self.current_session_id:
            raise ValueError("Session ID not set. Call set_session() first.")

        db = SessionLocal()
        try:
            service = CheckpointingService(db=db)

            checkpoint_data = CheckpointCreate(
                session_id=self.current_session_id,
                user_message=user_message,
                checkpoint_type=CheckpointType.MANUAL,
                file_paths=file_paths,
            )

            checkpoint = await service.create_checkpoint(checkpoint_data)
            return checkpoint.id

        finally:
            db.close()

    async def rewind(
        self,
        checkpoint_id: str,
        restore_code: bool = True,
        restore_conversation: bool = False,
    ) -> bool:
        """Rewind to a specific checkpoint.

        Args:
            checkpoint_id: Checkpoint identifier
            restore_code: Whether to restore code changes
            restore_conversation: Whether to restore conversation state

        Returns:
            True if successful

        Raises:
            ValueError: If checkpoint not found or restore fails

        """
        from src.models.checkpoint import CheckpointRestore

        db = SessionLocal()
        try:
            service = CheckpointingService(db=db)

            restore_data = CheckpointRestore(
                restore_code=restore_code,
                restore_conversation=restore_conversation,
            )

            await service.restore_checkpoint(checkpoint_id, restore_data)
            return True

        finally:
            db.close()

    def get_session_checkpoints(self) -> list[dict]:
        """Get all checkpoints for current session.

        Returns:
            List of checkpoint dictionaries

        Raises:
            ValueError: If session not set

        """
        if not self.current_session_id:
            raise ValueError("Session ID not set. Call set_session() first.")

        db = SessionLocal()
        try:
            service = CheckpointingService(db=db)

            checkpoints, _ = service.list_checkpoints(session_id=self.current_session_id)

            return [
                {
                    "id": cp.id,
                    "user_message": cp.user_message,
                    "checkpoint_type": cp.checkpoint_type,
                    "status": cp.status,
                    "created_at": cp.created_at,
                    "file_count": cp.file_count,
                    "total_size_bytes": cp.total_size_bytes,
                }
                for cp in checkpoints
            ]

        finally:
            db.close()


# Global checkpoint manager instance
checkpoint_manager = CheckpointManager()
