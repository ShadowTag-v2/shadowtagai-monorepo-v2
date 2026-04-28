#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Google Drive Indexer

This script indexes the contents of a specific Google Drive folder and saves the
metadata to a JSON file. It uses the Google Drive API.

Usage:
    python scripts/drive_indexer.py

Requirements:
    pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
"""

import json
import logging
import os
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("drive_indexer")

# Constants
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
TARGET_FOLDERS = [
    "1kAidkMEUaPeNQ9q0wJpcHM7TD9mAs4HF",  # ShadowTag-v2_Phase_Docs
    "10oQU5IokLQP4KnmYk5sA9Zx5jEHBF33k",  # User Added Drive 1
    "1pJt--0WuGpezNtz_HS15e-HnGyg1fKTp",  # User Added Drive 2
]
OUTPUT_FILE = "pnkln_intelligence/knowledge_base/drive_index.json"
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


def get_credentials() -> Credentials:
    """Gets valid user credentials from storage or initiates OAuth flow."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"'{CREDENTIALS_FILE}' not found. Please download OAuth 2.0 Client IDs "
                    "from Google Cloud Console (APIs & Services > Credentials) and save it here.",
                )

            # Simple local server flow
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return creds


def list_files_in_folder(service, folder_id: str) -> list[dict[str, Any]]:
    """Recursively lists all files in a specific Google Drive folder."""
    files = []
    page_token = None
    query = f"'{folder_id}' in parents and trashed = false"

    while True:
        try:
            results = (
                service.files()
                .list(
                    q=query,
                    pageSize=1000,
                    fields="nextPageToken, files(id, name, mimeType, webViewLink, parents, createdTime, modifiedTime, size)",
                    pageToken=page_token,
                )
                .execute()
            )

            items = results.get("files", [])

            for item in items:
                # Add parent info for reconstruction of path if needed
                item["parent_id"] = folder_id
                files.append(item)

                # If it's a folder, recurse
                if item["mimeType"] == "application/vnd.google-apps.folder":
                    logger.info(f"Scanning subfolder: {item['name']}")
                    files.extend(list_files_in_folder(service, item["id"]))

            page_token = results.get("nextPageToken")
            if not page_token:
                break

        except Exception as e:
            logger.error(f"Error listing files in folder {folder_id}: {e}")
            break

    return files


def main():
    """Main execution function."""
    logger.info("Starting Google Drive Indexer...")

    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

        logger.info("Authenticating...")
        creds = get_credentials()
        service = build("drive", "v3", credentials=creds)

        all_files = []
        for folder_id in TARGET_FOLDERS:
            logger.info(f"Indexing folder ID: {folder_id}")
            folder_files = list_files_in_folder(service, folder_id)
            logger.info(f"Found {len(folder_files)} items in {folder_id}")
            all_files.extend(folder_files)

        logger.info(f"Total items found across {len(TARGET_FOLDERS)} drives: {len(all_files)}")

        # Save to JSON
        with open(OUTPUT_FILE, "w") as f:
            json.dump(
                {
                    "target_folder_ids": TARGET_FOLDERS,
                    "total_items": len(all_files),
                    "indexed_at_utc": os.popen('date -u +"%Y-%m-%dT%H:%M:%SZ"').read().strip(),
                    "files": all_files,
                },
                f,
                indent=2,
            )

        logger.info(f"Index saved to {OUTPUT_FILE}")

    except Exception as e:
        logger.error(f"Indexer failed: {e}")
        raise


if __name__ == "__main__":
    main()
