"""
Google Drive Connector: Scan Drive for watermarked content.

Implements OAuth2 authentication and recursive file scanning
with support for docs, sheets, images, PDFs, and videos.
"""

from __future__ import annotations

import io
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# OAuth2 scopes for Drive access
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
]


@dataclass
class DriveFile:
    """Represents a file from Google Drive."""

    id: str
    name: str
    mime_type: str
    size: int
    created_time: datetime
    modified_time: datetime
    parents: list[str]
    web_view_link: str | None = None
    md5_checksum: str | None = None
    content: bytes | None = None

    @property
    def is_image(self) -> bool:
        return self.mime_type.startswith("image/")

    @property
    def is_video(self) -> bool:
        return self.mime_type.startswith("video/")

    @property
    def is_document(self) -> bool:
        return self.mime_type in [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.google-apps.document",
            "text/plain",
        ]

    @property
    def is_spreadsheet(self) -> bool:
        return self.mime_type in [
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.google-apps.spreadsheet",
        ]


class GoogleDriveConnector:
    """
    Connector for scanning Google Drive content.

    Supports:
    - OAuth2 authentication
    - Recursive folder scanning
    - File content download
    - Metadata extraction
    """

    def __init__(
        self,
        credentials_path: str = "credentials.json",
        token_path: str = "token.json",
    ):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self._service = None
        self._creds = None

    def authenticate(self) -> None:
        """Authenticate with Google Drive API."""
        creds = None

        # Load existing token
        try:
            import os

            if os.path.exists(self.token_path):
                creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        except Exception:
            pass

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save token for future use
            with open(self.token_path, "w") as token:
                token.write(creds.to_json())

        self._creds = creds
        self._service = build("drive", "v3", credentials=creds)

    @property
    def service(self):
        """Get authenticated Drive service."""
        if self._service is None:
            self.authenticate()
        return self._service

    async def list_files(
        self,
        folder_id: str = "root",
        recursive: bool = True,
        mime_types: list[str] | None = None,
        max_results: int = 1000,
    ) -> AsyncIterator[DriveFile]:
        """
        List files in Drive folder.

        Args:
            folder_id: Folder ID to scan (default: root)
            recursive: Scan subfolders
            mime_types: Filter by MIME types
            max_results: Maximum files to return
        """
        query_parts = [f"'{folder_id}' in parents", "trashed = false"]

        if mime_types:
            mime_filter = " or ".join(f"mimeType = '{mt}'" for mt in mime_types)
            query_parts.append(f"({mime_filter})")

        query = " and ".join(query_parts)

        page_token = None
        count = 0

        while count < max_results:
            results = (
                self.service.files()
                .list(
                    q=query,
                    pageSize=min(100, max_results - count),
                    pageToken=page_token,
                    fields="nextPageToken, files(id, name, mimeType, size, "
                    "createdTime, modifiedTime, parents, webViewLink, md5Checksum)",
                )
                .execute()
            )

            files = results.get("files", [])

            for file_data in files:
                drive_file = DriveFile(
                    id=file_data["id"],
                    name=file_data["name"],
                    mime_type=file_data.get("mimeType", ""),
                    size=int(file_data.get("size", 0)),
                    created_time=datetime.fromisoformat(
                        file_data.get("createdTime", "").replace("Z", "+00:00")
                    )
                    if file_data.get("createdTime")
                    else datetime.utcnow(),
                    modified_time=datetime.fromisoformat(
                        file_data.get("modifiedTime", "").replace("Z", "+00:00")
                    )
                    if file_data.get("modifiedTime")
                    else datetime.utcnow(),
                    parents=file_data.get("parents", []),
                    web_view_link=file_data.get("webViewLink"),
                    md5_checksum=file_data.get("md5Checksum"),
                )

                yield drive_file
                count += 1

                if count >= max_results:
                    break

                # Recurse into folders
                if recursive and drive_file.mime_type == "application/vnd.google-apps.folder":
                    async for sub_file in self.list_files(
                        folder_id=drive_file.id,
                        recursive=True,
                        mime_types=mime_types,
                        max_results=max_results - count,
                    ):
                        yield sub_file
                        count += 1
                        if count >= max_results:
                            break

            page_token = results.get("nextPageToken")
            if not page_token:
                break

    async def download_file(self, file_id: str) -> bytes:
        """Download file content."""
        request = self.service.files().get_media(fileId=file_id)

        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        return buffer.getvalue()

    async def get_file_with_content(self, file_id: str) -> DriveFile:
        """Get file metadata and content."""
        # Get metadata
        file_data = (
            self.service.files()
            .get(
                fileId=file_id,
                fields="id, name, mimeType, size, createdTime, modifiedTime, "
                "parents, webViewLink, md5Checksum",
            )
            .execute()
        )

        drive_file = DriveFile(
            id=file_data["id"],
            name=file_data["name"],
            mime_type=file_data.get("mimeType", ""),
            size=int(file_data.get("size", 0)),
            created_time=datetime.fromisoformat(
                file_data.get("createdTime", "").replace("Z", "+00:00")
            )
            if file_data.get("createdTime")
            else datetime.utcnow(),
            modified_time=datetime.fromisoformat(
                file_data.get("modifiedTime", "").replace("Z", "+00:00")
            )
            if file_data.get("modifiedTime")
            else datetime.utcnow(),
            parents=file_data.get("parents", []),
            web_view_link=file_data.get("webViewLink"),
            md5_checksum=file_data.get("md5Checksum"),
        )

        # Download content if not a Google native format
        if not drive_file.mime_type.startswith("application/vnd.google-apps"):
            drive_file.content = await self.download_file(file_id)

        return drive_file

    async def scan_for_watermarks(
        self,
        folder_id: str = "root",
        file_types: list[str] | None = None,
    ) -> AsyncIterator[DriveFile]:
        """
        Scan Drive for files that may contain watermarks.

        Default file types: images, PDFs, videos, documents
        """
        if file_types is None:
            file_types = [
                # Images
                "image/jpeg",
                "image/png",
                "image/gif",
                "image/webp",
                "image/tiff",
                # Videos
                "video/mp4",
                "video/quicktime",
                "video/webm",
                # Documents
                "application/pdf",
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                # Google native
                "application/vnd.google-apps.document",
                "application/vnd.google-apps.spreadsheet",
            ]

        async for file in self.list_files(
            folder_id=folder_id,
            recursive=True,
            mime_types=file_types,
        ):
            yield file

    def get_file_metadata(self, file_id: str) -> dict[str, Any]:
        """Get detailed metadata for a file."""
        return (
            self.service.files()
            .get(
                fileId=file_id,
                fields="*",
            )
            .execute()
        )
