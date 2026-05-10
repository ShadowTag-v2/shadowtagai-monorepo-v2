"""Checkpoint storage implementation."""

import hashlib
import shutil
from datetime import datetime
from pathlib import Path

import aiofiles

from src.core.config import settings


class CheckpointStore:
    """Manages storage of checkpoint files."""

    def __init__(self, storage_path: str | None = None):
        """Initialize checkpoint store.

        Args:
            storage_path: Base path for storing checkpoint files

        """
        self.storage_path = Path(storage_path or settings.checkpoint_storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _get_checkpoint_dir(self, checkpoint_id: str) -> Path:
        """Get directory path for a checkpoint.

        Args:
            checkpoint_id: Checkpoint identifier

        Returns:
            Path to checkpoint directory

        """
        checkpoint_dir = self.storage_path / checkpoint_id
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        return checkpoint_dir

    def _compute_hash(self, content: bytes) -> str:
        """Compute SHA-256 hash of content.

        Args:
            content: File content as bytes

        Returns:
            Hexadecimal hash string

        """
        return hashlib.sha256(content).hexdigest()

    async def save_file(
        self,
        checkpoint_id: str,
        file_path: str,
        snapshot_id: str,
    ) -> tuple[str, int, str]:
        """Save a file to checkpoint storage.

        Args:
            checkpoint_id: Checkpoint identifier
            file_path: Original file path
            snapshot_id: Snapshot identifier

        Returns:
            Tuple of (content_hash, size_bytes, storage_path)

        """
        # Read file content
        async with aiofiles.open(file_path, "rb") as f:
            content = await f.read()

        # Compute hash and size
        content_hash = self._compute_hash(content)
        size_bytes = len(content)

        # Determine storage path
        checkpoint_dir = self._get_checkpoint_dir(checkpoint_id)
        storage_file_path = checkpoint_dir / f"{snapshot_id}.snapshot"

        # Save file
        async with aiofiles.open(storage_file_path, "wb") as f:
            await f.write(content)

        return content_hash, size_bytes, str(storage_file_path)

    async def restore_file(self, storage_path: str, target_path: str) -> None:
        """Restore a file from checkpoint storage.

        Args:
            storage_path: Path to stored snapshot file
            target_path: Target path to restore file to

        """
        # Create target directory if needed
        target_dir = Path(target_path).parent
        target_dir.mkdir(parents=True, exist_ok=True)

        # Copy file from storage to target
        async with aiofiles.open(storage_path, "rb") as src:
            content = await src.read()
            async with aiofiles.open(target_path, "wb") as dst:
                await dst.write(content)

    async def get_file_content(self, storage_path: str) -> bytes:
        """Get file content from storage.

        Args:
            storage_path: Path to stored snapshot file

        Returns:
            File content as bytes

        """
        async with aiofiles.open(storage_path, "rb") as f:
            return await f.read()

    def delete_checkpoint(self, checkpoint_id: str) -> None:
        """Delete all files for a checkpoint.

        Args:
            checkpoint_id: Checkpoint identifier

        """
        checkpoint_dir = self._get_checkpoint_dir(checkpoint_id)
        if checkpoint_dir.exists():
            shutil.rmtree(checkpoint_dir)

    def cleanup_expired(self, expiry_date: datetime) -> int:
        """Clean up checkpoints older than expiry date.

        Args:
            expiry_date: Checkpoints older than this will be deleted

        Returns:
            Number of checkpoints deleted

        """
        deleted_count = 0

        for checkpoint_dir in self.storage_path.iterdir():
            if not checkpoint_dir.is_dir():
                continue

            # Check modification time
            mtime = datetime.fromtimestamp(checkpoint_dir.stat().st_mtime)
            if mtime < expiry_date:
                shutil.rmtree(checkpoint_dir)
                deleted_count += 1

        return deleted_count

    def get_storage_stats(self) -> dict:
        """Get storage statistics.

        Returns:
            Dictionary with storage statistics

        """
        total_size = 0
        checkpoint_count = 0
        file_count = 0

        for checkpoint_dir in self.storage_path.iterdir():
            if not checkpoint_dir.is_dir():
                continue

            checkpoint_count += 1

            for file_path in checkpoint_dir.iterdir():
                if file_path.is_file():
                    total_size += file_path.stat().st_size
                    file_count += 1

        return {
            "total_size_bytes": total_size,
            "checkpoint_count": checkpoint_count,
            "file_count": file_count,
            "storage_path": str(self.storage_path),
        }
