# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Google Cloud Docs MCP Integration
Enables AI agents to read/write Google Docs for:
- Cor state management
- Documentation updates
- Meeting notes synthesis
"""

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ImportError:
    service_account = None
    build = None
    logger.warning(
        "Google API client not installed. Run: pip install google-api-python-client google-auth",
    )


class GoogleDocsMCP:
    """MCP-compatible Google Docs integration for ShadowTag agents."""

    def __init__(self, project_id: str | None = None):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v2")
        self.folder_id = os.getenv("GOOGLE_DOCS_FOLDER_ID")
        self._docs_service = None
        self._drive_service = None

    def _get_credentials(self):
        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not creds_path:
            raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS not set")
        return service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=[
                "https://www.googleapis.com/auth/documents",
                "https://www.googleapis.com/auth/drive",
            ],
        )

    @property
    def docs_service(self):
        if self._docs_service is None and build is not None:
            creds = self._get_credentials()
            self._docs_service = build("docs", "v1", credentials=creds)
        return self._docs_service

    @property
    def drive_service(self):
        if self._drive_service is None and build is not None:
            creds = self._get_credentials()
            self._drive_service = build("drive", "v3", credentials=creds)
        return self._drive_service

    def read_document(self, doc_id: str) -> str:
        """Read content from a Google Doc."""
        doc = self.docs_service.documents().get(documentId=doc_id).execute()
        content = doc.get("body", {}).get("content", [])

        text_parts = []
        for element in content:
            paragraph = element.get("paragraph")
            if paragraph:
                for run in paragraph.get("elements", []):
                    text = run.get("textRun", {}).get("content", "")
                    text_parts.append(text)

        return "".join(text_parts)

    def update_document(self, doc_id: str, content: str) -> bool:
        """Append content to a Google Doc."""
        requests = [{"insertText": {"location": {"index": 1}, "text": content}}]
        self.docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": requests},
        ).execute()
        return True

    def create_cor_snapshot(self, cor_data: dict[str, Any]) -> str:
        """Create a Cor state snapshot as a new Google Doc."""
        title = f"Cor Snapshot - {cor_data.get('cor_id', 'unknown')}"
        body = {"title": title}
        doc = self.docs_service.documents().create(body=body).execute()
        doc_id = doc["documentId"]

        snapshot_text = json.dumps(cor_data, indent=2)
        self.update_document(doc_id, snapshot_text)

        # Move to target folder if configured
        if self.folder_id:
            self.drive_service.files().update(
                fileId=doc_id,
                addParents=self.folder_id,
                fields="id, parents",
            ).execute()

        logger.info(f"Created Cor snapshot: {doc_id}")
        return doc_id

    def list_documents(self, query: str | None = None) -> list[dict[str, str]]:
        """List documents in the configured folder."""
        q = f"'{self.folder_id}' in parents and mimeType='application/vnd.google-apps.document'"
        if query:
            q += f" and name contains '{query}'"

        results = (
            self.drive_service.files()
            .list(
                q=q,
                fields="files(id, name, modifiedTime)",
                orderBy="modifiedTime desc",
                pageSize=20,
            )
            .execute()
        )

        return results.get("files", [])
