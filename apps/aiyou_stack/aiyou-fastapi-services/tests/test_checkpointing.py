"""Tests for checkpointing functionality."""

import os
import tempfile
from datetime import datetime, timedelta

import pytest

from src.models.checkpoint import CheckpointCreate, CheckpointRestore, CheckpointType
from src.services.checkpointing_service import CheckpointingService


class TestCheckpointingService:
    """Test checkpointing service."""

    @pytest.mark.asyncio
    async def test_create_checkpoint(self, test_db, test_storage, test_file):
        """Test creating a checkpoint."""
        service = CheckpointingService(db=test_db, store=test_storage)

        checkpoint_data = CheckpointCreate(
            session_id="test_session_1",
            user_message="Test checkpoint",
            checkpoint_type=CheckpointType.AUTO,
            file_paths=[test_file],
        )

        checkpoint = await service.create_checkpoint(checkpoint_data)

        assert checkpoint is not None
        assert checkpoint.session_id == "test_session_1"
        assert checkpoint.user_message == "Test checkpoint"
        assert checkpoint.file_count == 1
        assert checkpoint.total_size_bytes > 0

    @pytest.mark.asyncio
    async def test_restore_checkpoint(self, test_db, test_storage, test_file):
        """Test restoring a checkpoint."""
        service = CheckpointingService(db=test_db, store=test_storage)

        # Create checkpoint
        checkpoint_data = CheckpointCreate(
            session_id="test_session_1",
            user_message="Test checkpoint",
            checkpoint_type=CheckpointType.AUTO,
            file_paths=[test_file],
        )

        checkpoint = await service.create_checkpoint(checkpoint_data)

        # Modify original file
        with open(test_file, "w") as f:
            f.write("Modified content")

        # Restore checkpoint
        restore_data = CheckpointRestore(restore_code=True)
        restored = await service.restore_checkpoint(checkpoint.id, restore_data)

        assert restored is not None
        assert restored.id == checkpoint.id

        # Verify file was restored
        with open(test_file) as f:
            content = f.read()
            assert content == "Test file content"

    def test_get_checkpoint(self, test_db, test_storage):
        """Test getting a checkpoint by ID."""
        service = CheckpointingService(db=test_db, store=test_storage)

        # Create a checkpoint manually
        from src.models.checkpoint import Checkpoint

        checkpoint = Checkpoint(
            id="test_checkpoint_1",
            session_id="test_session_1",
            user_message="Test",
        )

        test_db.add(checkpoint)
        test_db.commit()

        # Get checkpoint
        retrieved = service.get_checkpoint("test_checkpoint_1")

        assert retrieved is not None
        assert retrieved.id == "test_checkpoint_1"

    def test_list_checkpoints(self, test_db, test_storage):
        """Test listing checkpoints for a session."""
        service = CheckpointingService(db=test_db, store=test_storage)

        # Create multiple checkpoints
        from src.models.checkpoint import Checkpoint

        for i in range(5):
            checkpoint = Checkpoint(
                id=f"test_checkpoint_{i}",
                session_id="test_session_1",
                user_message=f"Test {i}",
            )
            test_db.add(checkpoint)

        test_db.commit()

        # List checkpoints
        checkpoints, total = service.list_checkpoints("test_session_1")

        assert total == 5
        assert len(checkpoints) == 5

    def test_delete_checkpoint(self, test_db, test_storage):
        """Test deleting a checkpoint."""
        service = CheckpointingService(db=test_db, store=test_storage)

        # Create a checkpoint
        from src.models.checkpoint import Checkpoint

        checkpoint = Checkpoint(
            id="test_checkpoint_1",
            session_id="test_session_1",
            user_message="Test",
        )

        test_db.add(checkpoint)
        test_db.commit()

        # Delete checkpoint
        deleted = service.delete_checkpoint("test_checkpoint_1")

        assert deleted is True

        # Verify it's marked as deleted
        retrieved = test_db.query(Checkpoint).filter(Checkpoint.id == "test_checkpoint_1").first()

        assert retrieved.is_deleted is True

    def test_cleanup_expired_checkpoints(self, test_db, test_storage):
        """Test cleaning up expired checkpoints."""
        service = CheckpointingService(db=test_db, store=test_storage)

        # Create expired checkpoint
        from src.models.checkpoint import Checkpoint

        expired_checkpoint = Checkpoint(
            id="expired_checkpoint",
            session_id="test_session_1",
            user_message="Expired",
            expires_at=datetime.utcnow() - timedelta(days=1),
        )

        test_db.add(expired_checkpoint)

        # Create active checkpoint
        active_checkpoint = Checkpoint(
            id="active_checkpoint",
            session_id="test_session_1",
            user_message="Active",
            expires_at=datetime.utcnow() + timedelta(days=30),
        )

        test_db.add(active_checkpoint)
        test_db.commit()

        # Clean up
        cleanup_count = service.cleanup_expired_checkpoints()

        assert cleanup_count == 1

    def test_get_session_stats(self, test_db, test_storage):
        """Test getting session statistics."""
        service = CheckpointingService(db=test_db, store=test_storage)

        # Create checkpoints with different statuses
        from src.models.checkpoint import Checkpoint, CheckpointStatus

        checkpoint1 = Checkpoint(
            id="checkpoint_1",
            session_id="test_session_1",
            user_message="Test 1",
            status=CheckpointStatus.ACTIVE.value,
            file_count=2,
            total_size_bytes=1000,
        )

        checkpoint2 = Checkpoint(
            id="checkpoint_2",
            session_id="test_session_1",
            user_message="Test 2",
            status=CheckpointStatus.RESTORED.value,
            file_count=3,
            total_size_bytes=2000,
        )

        test_db.add(checkpoint1)
        test_db.add(checkpoint2)
        test_db.commit()

        # Get stats
        stats = service.get_session_stats("test_session_1")

        assert stats["session_id"] == "test_session_1"
        assert stats["checkpoint_count"] == 2
        assert stats["total_files"] == 5
        assert stats["total_size_bytes"] == 3000
        assert stats["active_checkpoints"] == 1
        assert stats["restored_checkpoints"] == 1


class TestCheckpointStore:
    """Test checkpoint storage."""

    @pytest.mark.asyncio
    async def test_save_file(self, test_storage, test_file):
        """Test saving a file to storage."""
        content_hash, size_bytes, storage_path = await test_storage.save_file(
            checkpoint_id="test_checkpoint", file_path=test_file, snapshot_id="test_snapshot",
        )

        assert content_hash is not None
        assert size_bytes > 0
        assert os.path.exists(storage_path)

    @pytest.mark.asyncio
    async def test_restore_file(self, test_storage, test_file):
        """Test restoring a file from storage."""
        # Save file
        content_hash, size_bytes, storage_path = await test_storage.save_file(
            checkpoint_id="test_checkpoint", file_path=test_file, snapshot_id="test_snapshot",
        )

        # Create a new target path
        with tempfile.NamedTemporaryFile(delete=False) as f:
            target_path = f.name

        try:
            # Restore file
            await test_storage.restore_file(storage_path, target_path)

            # Verify content
            with open(target_path) as f:
                content = f.read()
                assert content == "Test file content"

        finally:
            if os.path.exists(target_path):
                os.unlink(target_path)

    def test_get_storage_stats(self, test_storage):
        """Test getting storage statistics."""
        stats = test_storage.get_storage_stats()

        assert "total_size_bytes" in stats
        assert "checkpoint_count" in stats
        assert "file_count" in stats
        assert "storage_path" in stats
