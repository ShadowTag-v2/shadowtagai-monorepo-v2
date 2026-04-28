# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import io
from pathlib import Path

import PyPDF2
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Configuration
TOKEN_FILE = Path("token.json")
OUTPUT_FILE = Path("biz_plan_raw.txt")

# Folder IDs
FOLDERS = {
    "Business Plan Source": "1pJt--0WuGpezNtz_HS15e-HnGyg1fKTp",
    "Valuation and Stats": "10oQU5IokLQP4KnmYk5sA9Zx5jEHBF33k",
}

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def get_credentials():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("No valid token found and cannot authenticate interactively.")
            return None
    return creds


def list_files_in_folder(service, folder_id):
    results = (
        service.files()
        .list(
            q=f"'{folder_id}' in parents and trashed = false",
            pageSize=100,
            fields="nextPageToken, files(id, name, mimeType)",
        )
        .execute()
    )
    return results.get("files", [])


def download_file_content(service, file_id, mime_type):
    try:
        if mime_type.startswith("application/vnd.google-apps"):
            if "document" in mime_type:
                request = service.files().export_media(fileId=file_id, mimeType="text/plain")
            elif "spreadsheet" in mime_type:
                request = service.files().export_media(fileId=file_id, mimeType="text/csv")
            else:
                return None, "Unsupported Google App Type"
        else:
            request = service.files().get_media(fileId=file_id)

        file_content = io.BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        return file_content.getvalue(), None
    except Exception as e:
        return None, str(e)


def extract_text(content, mime_type):
    if mime_type == "application/pdf":
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            return "\n".join(page.extract_text() for page in pdf_reader.pages)
        except Exception as e:
            return f"[PDF Extraction Error: {e}]"
    else:
        return content.decode("utf-8", errors="ignore")


def main():
    creds = get_credentials()
    if not creds:
        return

    service = build("drive", "v3", credentials=creds)

    # ensure file is empty first
    with open(OUTPUT_FILE, "w") as f:
        f.write("=== BUSINESS PLAN EXTRACTION START ===\n")

    for label, folder_id in FOLDERS.items():
        print(f"--- Processing {label} ({folder_id}) ---")
        try:
            files = list_files_in_folder(service, folder_id)
        except Exception as e:
            print(f"Failed to list folder {label}: {e}")
            continue

        for file in files:
            name = file["name"]
            mime = file["mimeType"]

            # Skip likely binaries or large archives
            if any(
                name.lower().endswith(ext)
                for ext in [
                    ".tar.gz",
                    ".zip",
                    ".dmg",
                    ".iso",
                    ".bin",
                    ".exe",
                    ".avif",
                    ".png",
                    ".jpg",
                ]
            ):
                print(f"  Skipping binary/archive: {name}")
                continue

            print(f"  Fetching: {name}")
            content, error = download_file_content(service, file["id"], mime)

            if error:
                print(f"    Error: {error}")
                continue

            if content:
                # Check size (rough)
                if len(content) > 5 * 1024 * 1024:  # 5MB limit
                    print("    Skipping large file > 5MB")
                    continue

                text = extract_text(content, mime)

                # Write immediately
                try:
                    with open(OUTPUT_FILE, "a") as f:
                        f.write(f"\n\n=== SOURCE: {label} / {name} ===\n\n{text}")
                    print(f"    Extracted {len(text)} chars (saved)")
                except Exception as e:
                    print(f"    Error writing to file: {e}")


if __name__ == "__main__":
    main()
