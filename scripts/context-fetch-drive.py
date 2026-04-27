#!/usr/bin/env python3
"""context-fetch-drive.py — Fetch context documents from Google Drive.

Uses the Google Drive API via Application Default Credentials to pull
documents into the local .memory/ or docs/ directory for agent consumption.

Usage:
    python3 scripts/context-fetch-drive.py --folder-id <FOLDER_ID> [--output-dir docs/research]
    python3 scripts/context-fetch-drive.py --file-id <FILE_ID> [--output-dir .memory/atoms/facts]
    python3 scripts/context-fetch-drive.py --query "name contains 'TACSOP'" [--output-dir docs/]

Environment:
    GOOGLE_APPLICATION_CREDENTIALS — Path to service account JSON (ADC fallback).
    DRIVE_FOLDER_ID — Default folder ID if --folder-id not specified.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, UTC
from pathlib import Path

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
except ImportError:
    print("ERROR: google-api-python-client and google-auth are required.")
    print("  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    sys.exit(1)

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
MIME_EXPORT_MAP = {
    "application/vnd.google-apps.document": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".docx",
    ),
    "application/vnd.google-apps.spreadsheet": (
        "text/csv",
        ".csv",
    ),
    "application/vnd.google-apps.presentation": (
        "application/pdf",
        ".pdf",
    ),
}


def get_drive_service():
    """Build the Drive v3 service using ADC or SA key."""
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if creds_path and Path(creds_path).exists():
        creds = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    else:
        # Fallback to ADC
        try:
            import google.auth

            creds, _ = google.auth.default(scopes=SCOPES)
        except Exception as exc:
            print(f"ERROR: No credentials found. Set GOOGLE_APPLICATION_CREDENTIALS. ({exc})")
            sys.exit(1)
    return build("drive", "v3", credentials=creds)


def list_files_in_folder(service, folder_id: str, query: str | None = None):
    """List files in a Drive folder."""
    q_parts = [f"'{folder_id}' in parents", "trashed = false"]
    if query:
        q_parts.append(query)
    q = " and ".join(q_parts)
    results = []
    page_token = None
    while True:
        resp = (
            service.files()
            .list(
                q=q,
                spaces="drive",
                fields="nextPageToken, files(id, name, mimeType, modifiedTime, size)",
                pageToken=page_token,
                pageSize=100,
            )
            .execute()
        )
        results.extend(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return results


def download_file(service, file_meta: dict, output_dir: Path):
    """Download or export a single file."""
    file_id = file_meta["id"]
    name = file_meta["name"]
    mime = file_meta["mimeType"]

    if mime in MIME_EXPORT_MAP:
        export_mime, ext = MIME_EXPORT_MAP[mime]
        safe_name = name.replace("/", "_") + ext
        dest = output_dir / safe_name
        request = service.files().export_media(fileId=file_id, mimeType=export_mime)
    else:
        safe_name = name.replace("/", "_")
        dest = output_dir / safe_name
        request = service.files().get_media(fileId=file_id)

    import io

    fh = io.FileIO(str(dest), "wb")
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _status, done = downloader.next_chunk()
    fh.close()
    print(f"  ✅ {safe_name} ({mime})")
    return str(dest)


def main():
    parser = argparse.ArgumentParser(description="Fetch context from Google Drive")
    parser.add_argument("--folder-id", default=os.environ.get("DRIVE_FOLDER_ID"))
    parser.add_argument("--file-id", help="Download a single file by ID")
    parser.add_argument("--query", help="Additional Drive query filter")
    parser.add_argument("--output-dir", default="docs/research", help="Local output directory")
    parser.add_argument("--manifest", action="store_true", help="Write fetch manifest JSON")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    service = get_drive_service()
    fetched = []

    if args.file_id:
        meta = service.files().get(fileId=args.file_id, fields="id,name,mimeType,modifiedTime").execute()
        path = download_file(service, meta, output_dir)
        fetched.append({"id": meta["id"], "name": meta["name"], "local": path})

    elif args.folder_id:
        files = list_files_in_folder(service, args.folder_id, args.query)
        print(f"Found {len(files)} files in folder {args.folder_id}")
        for f in files:
            path = download_file(service, f, output_dir)
            fetched.append({"id": f["id"], "name": f["name"], "local": path})

    else:
        print("ERROR: Provide --folder-id or --file-id")
        sys.exit(1)

    if args.manifest:
        manifest = {
            "fetched_at": datetime.now(UTC).isoformat(),
            "count": len(fetched),
            "files": fetched,
        }
        manifest_path = output_dir / "fetch_manifest.json"
        with open(manifest_path, "w") as fh:
            json.dump(manifest, fh, indent=2)
        print(f"📋 Manifest → {manifest_path}")

    print(f"\n✅ Fetched {len(fetched)} files → {output_dir}/")


if __name__ == "__main__":
    main()
