#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""The Squasher: Drive Content Extractor
Downloads and extracts text from Google Drive assets into a single JSONL file.
"""

import io
import json
import logging
import os
from datetime import datetime
from typing import Any

import docx
import ebooklib

# Extractor libs
import pypdf
from bs4 import BeautifulSoup
from ebooklib import epub
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("squasher")

# Configuration
INDEX_FILE = "pnkln_intelligence/knowledge_base/drive_index.json"
OUTPUT_FILE = "pnkln_intelligence/knowledge_base/gucci_content_lake.jsonl"
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]  # Note: Needs full readonly to download

# Mime Types
MIME_PDF = "application/pdf"
MIME_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
MIME_GOOGLE_DOC = "application/vnd.google-apps.document"
MIME_GOOGLE_SHEET = "application/vnd.google-apps.spreadsheet"
MIME_EPUB = "application/epub+zip"
MIME_FOLDER = "application/vnd.google-apps.folder"


def get_credentials() -> Credentials:
    """Gets valid user credentials."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError("Credentials file not found")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return creds


def extract_text_pdf(file_stream) -> str:
    try:
        reader = pypdf.PdfReader(file_stream)
        text = []
        for page in reader.pages:
            text.append(page.extract_text() or "")
        return "\n".join(text)
    except Exception as e:
        logger.error(f"PDF Extract Error: {e}")
        return ""


def extract_text_docx(file_stream) -> str:
    try:
        doc = docx.Document(file_stream)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        logger.error(f"DOCX Extract Error: {e}")
        return ""


def extract_text_epub(file_path_or_stream) -> str:
    # Ebooklib requires a file path usually, writing to temp
    try:
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False, suffix=".epub") as tmp:
            tmp.write(file_path_or_stream.getvalue())
            tmp_path = tmp.name

        book = epub.read_epub(tmp_path)
        text = []
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), "html.parser")
                text.append(soup.get_text())

        os.unlink(tmp_path)
        return "\n".join(text)
    except Exception as e:
        logger.error(f"EPUB Extract Error: {e}")
        return ""


def process_file(service, file_item: dict[str, Any]) -> dict[str, Any]:
    file_id = file_item["id"]
    name = file_item["name"]
    mime = file_item["mimeType"]

    logger.info(f"Processing: {name} ({mime})")

    file_content = io.BytesIO()
    request = None

    # Generate Request
    if mime == MIME_GOOGLE_DOC:
        request = service.files().export_media(fileId=file_id, mimeType="text/plain")
    elif mime == MIME_GOOGLE_SHEET:
        # Skip sheets for now or export as csv? Skip to keep simple text lake.
        logger.info("Skipping Google Sheet (structured data)")
        return None
    elif mime == MIME_FOLDER:
        return None
    else:
        # Binary download
        request = service.files().get_media(fileId=file_id)

    # Download
    try:
        downloader = MediaIoBaseDownload(file_content, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()

        file_content.seek(0)
    except Exception as e:
        logger.error(f"Download failed for {name}: {e}")
        return None

    # Extract
    text = ""
    if mime == MIME_PDF:
        text = extract_text_pdf(file_content)
    elif mime in (
        MIME_DOCX,
        MIME_GOOGLE_DOC,
    ):  # Google Doc exported as text/plain is handled below?
        if mime == MIME_DOCX:
            text = extract_text_docx(file_content)
        else:
            # It's plain text from Google Doc export
            text = file_content.getvalue().decode("utf-8", errors="ignore")
    elif mime == MIME_EPUB:
        text = extract_text_epub(file_content)
    elif "text/" in mime or name.endswith(".md") or name.endswith(".py") or name.endswith(".txt"):
        text = file_content.getvalue().decode("utf-8", errors="ignore")
    else:
        logger.warning(f"Unsupported mime for text extraction: {mime}")
        return None

    if not text.strip():
        logger.warning(f"No text extracted from {name}")
        return None

    return {
        "id": file_id,
        "title": name,
        "mimeType": mime,
        "content": text,
        "timestamp": datetime.now().isoformat(),
        "webViewLink": file_item.get("webViewLink", ""),
        "parent_id": file_item.get("parents", [""])[0] if file_item.get("parents") else None,
    }


def main():
    if not os.path.exists(INDEX_FILE):
        logger.error(f"Index file {INDEX_FILE} not found!")
        return

    logger.info("Loading drive index...")
    with open(INDEX_FILE) as f:
        data = json.load(f)

    files = data.get("files", [])
    logger.info(f"Loaded {len(files)} files from index.")

    # Authenticate
    creds = get_credentials()
    service = build("drive", "v3", credentials=creds)

    # Output file
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    processed_count = 0
    with open(OUTPUT_FILE, "a") as out_f:  # Append mode to support resume or chunking
        for file_item in files:
            # Filter logic could go here (e.g., skip Images/Videos)
            if "video/" in file_item["mimeType"] or "image/" in file_item["mimeType"]:
                continue

            try:
                doc = process_file(service, file_item)
                if doc:
                    out_f.write(json.dumps(doc) + "\n")
                    out_f.flush()
                    processed_count += 1
            except Exception as e:
                logger.error(f"Failed to process {file_item['name']}: {e}")

    logger.info(f"Squashing Complete. Extracted {processed_count} documents to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
