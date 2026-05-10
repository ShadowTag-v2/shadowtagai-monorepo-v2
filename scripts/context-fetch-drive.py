#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import argparse
import io
import sys
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError


def fetch_drive_doc(file_id, output_path=None):
  try:
    # Uses Application Default Credentials (ADC)
    creds, _ = google.auth.default()
    service = build("drive", "v3", credentials=creds)

    # Check if it's a native Google Workspace doc (Docs, Sheets, etc.)
    file_metadata = service.files().get(fileId=file_id).execute()
    mime_type = file_metadata.get("mimeType", "")

    if "application/vnd.google-apps" in mime_type:
      print(">>> [DRIVE FETCHER] Exporting Google Document...")
      request = service.files().export_media(fileId=file_id, mimeType="text/plain")
    else:
      print(">>> [DRIVE FETCHER] Downloading standard file...")
      request = service.files().get_media(fileId=file_id)

    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
      status, done = downloader.next_chunk()
      if status:
        print(f">>> [DRIVE FETCHER] Download {int(status.progress() * 100)}%.")

    content = fh.getvalue()

    if output_path:
      with open(output_path, "wb") as f:
        f.write(content)
      print(f">>> [DRIVE FETCHER] Successfully saved to {output_path}")
    else:
      print(content.decode("utf-8", errors="replace"))

  except HttpError as error:
    print(f"❌ An error occurred: {error}", file=sys.stderr)
    sys.exit(1)
  except google.auth.exceptions.DefaultCredentialsError:
    print("❌ ADC missing. Run: gcloud auth application-default login", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Fetch a file from Google Drive via ADC")
  parser.add_argument("file_id", type=str, help="The Google Drive File ID")
  parser.add_argument(
    "--output", type=str, help="Optional output file path", default=None
  )

  args = parser.parse_args()
  fetch_drive_doc(args.file_id, args.output)
