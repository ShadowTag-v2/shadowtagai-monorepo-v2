"""Memory Scanner: Scan local file system for watermarked content.

Implements file system walking with filters for watermark detection.
"""

from __future__ import annotations

import hashlib
import mimetypes
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class LocalFile:
    """Represents a local file."""

    path: Path
    name: str
    mime_type: str
    size: int
    created_time: datetime
    modified_time: datetime
    md5_hash: str | None = None
    content: bytes | None = None

    @property
    def is_image(self) -> bool:
        return self.mime_type.startswith("image/") if self.mime_type else False

    @property
    def is_video(self) -> bool:
        return self.mime_type.startswith("video/") if self.mime_type else False

    @property
    def is_document(self) -> bool:
        doc_types = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
        ]
        return self.mime_type in doc_types if self.mime_type else False


class MemoryScanner:
    """Scanner for local file system content.

    Supports:
    - Recursive directory scanning
    - File type filtering
    - Content loading
    - Hash calculation
    """

    def __init__(
        self,
        base_path: str = ".",
        exclude_patterns: list[str] | None = None,
    ):
        self.base_path = Path(base_path).resolve()
        self.exclude_patterns = exclude_patterns or [
            ".git",
            "__pycache__",
            "node_modules",
            ".venv",
            "venv",
            ".env",
        ]

    def _should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded."""
        return any(pattern in path.parts for pattern in self.exclude_patterns)

    def _get_mime_type(self, path: Path) -> str:
        """Get MIME type for file."""
        mime_type, _ = mimetypes.guess_type(str(path))
        return mime_type or "application/octet-stream"

    def _calculate_md5(self, path: Path) -> str:
        """Calculate MD5 hash of file."""
        hash_md5 = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    async def scan_directory(
        self,
        path: str | None = None,
        recursive: bool = True,
        extensions: list[str] | None = None,
        max_size_mb: float = 100,
        calculate_hash: bool = False,
    ) -> AsyncIterator[LocalFile]:
        """Scan directory for files.

        Args:
            path: Directory to scan (default: base_path)
            recursive: Scan subdirectories
            extensions: Filter by extensions (e.g., [".jpg", ".pdf"])
            max_size_mb: Skip files larger than this
            calculate_hash: Calculate MD5 hash

        """
        scan_path = Path(path) if path else self.base_path

        if not scan_path.exists():
            return

        if not scan_path.is_dir():
            # Single file
            if scan_path.is_file():
                local_file = await self._create_local_file(scan_path, calculate_hash)
                if local_file:
                    yield local_file
            return

        # Directory scan
        iterator = scan_path.rglob("*") if recursive else scan_path.glob("*")

        for file_path in iterator:
            if not file_path.is_file():
                continue

            if self._should_exclude(file_path):
                continue

            # Filter by extension
            if extensions and file_path.suffix.lower() not in extensions:
                continue

            # Check size
            try:
                size = file_path.stat().st_size
                if size > max_size_mb * 1024 * 1024:
                    continue
            except OSError:
                continue

            local_file = await self._create_local_file(file_path, calculate_hash)
            if local_file:
                yield local_file

    async def _create_local_file(
        self,
        path: Path,
        calculate_hash: bool = False,
    ) -> LocalFile | None:
        """Create LocalFile from path."""
        try:
            stat = path.stat()

            local_file = LocalFile(
                path=path,
                name=path.name,
                mime_type=self._get_mime_type(path),
                size=stat.st_size,
                created_time=datetime.fromtimestamp(stat.st_ctime),
                modified_time=datetime.fromtimestamp(stat.st_mtime),
            )

            if calculate_hash:
                local_file.md5_hash = self._calculate_md5(path)

            return local_file

        except (OSError, PermissionError):
            return None

    async def load_content(self, file: LocalFile) -> bytes:
        """Load file content into memory."""
        content = file.path.read_bytes()
        file.content = content
        return content

    async def scan_for_watermarks(
        self,
        path: str | None = None,
    ) -> AsyncIterator[LocalFile]:
        """Scan for files that may contain watermarks.

        Targets: images, PDFs, videos, documents
        """
        extensions = [
            # Images
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".webp",
            ".tiff",
            ".bmp",
            # Videos
            ".mp4",
            ".mov",
            ".avi",
            ".webm",
            ".mkv",
            # Documents
            ".pdf",
            ".doc",
            ".docx",
            ".txt",
        ]

        async for file in self.scan_directory(
            path=path,
            recursive=True,
            extensions=extensions,
            calculate_hash=True,
        ):
            yield file

    def get_file_info(self, path: str) -> dict[str, Any]:
        """Get detailed info about a file."""
        file_path = Path(path)

        if not file_path.exists():
            return {"error": "File not found"}

        stat = file_path.stat()

        return {
            "path": str(file_path.absolute()),
            "name": file_path.name,
            "extension": file_path.suffix,
            "mime_type": self._get_mime_type(file_path),
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
            "md5": self._calculate_md5(file_path),
            "permissions": oct(stat.st_mode)[-3:],
        }

    async def find_duplicates(
        self,
        path: str | None = None,
    ) -> dict[str, list[str]]:
        """Find duplicate files by MD5 hash."""
        hash_to_files: dict[str, list[str]] = {}

        async for file in self.scan_directory(
            path=path,
            calculate_hash=True,
        ):
            if file.md5_hash:
                if file.md5_hash not in hash_to_files:
                    hash_to_files[file.md5_hash] = []
                hash_to_files[file.md5_hash].append(str(file.path))

        # Return only duplicates
        return {h: files for h, files in hash_to_files.items() if len(files) > 1}
