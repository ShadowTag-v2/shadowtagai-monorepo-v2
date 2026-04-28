# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import argparse
from google.auth import default
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import io
from googleapiclient.http import MediaIoBaseDownload


def fetch_drive_doc(file_id, output_path=None):
    """
    Fetches a Google Drive document using Application Default Credentials (ADC).
    If it's a Google Doc, it exports to plain text.
    Otherwise, it downloads the raw file.
    """
    try:
        # Obtain Application Default Credentials
        # The SCOPES are required if the ADC does not have the necessary permissions natively.
        credentials, project = default(scopes=["https://www.googleapis.com/auth/drive.readonly"])

        service = build("drive", "v3", credentials=credentials)

        # Get file metadata to check mimeType
        file_metadata = service.files().get(fileId=file_id, fields="name, mimeType").execute()
        mime_type = file_metadata.get("mimeType")
        file_name = file_metadata.get("name")

        print(f">>> [DRIVE FETCHER] Found file: {file_name} ({mime_type})")

        # If it's a Google Workspace document, we must export it.
        if "application/vnd.google-apps" in mime_type:
            if mime_type == "application/vnd.google-apps.document":
                request = service.files().export_media(fileId=file_id, mimeType="text/plain")
            else:
                print(f"⚠️ Cannot export this Google Workspace type natively to text: {mime_type}")
                return
        else:
            # For standard binary/text files
            request = service.files().get_media(fileId=file_id)

        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f">>> [DRIVE FETCHER] Download {int(status.progress() * 100)}%.")

        content = fh.getvalue()

        if output_path:
            with open(output_path, "wb") as f:
                f.write(content)
            print(f">>> [DRIVE FETCHER] Successfully saved to {output_path}")
        else:
            # If no path, just print it out for the AI agent to read in context
            print(content.decode("utf-8", errors="replace"))

    except HttpError as error:
        print(f"❌ An error occurred: {error}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch a file from Google Drive via ADC")
    parser.add_argument("file_id", type=str, help="The Google Drive File ID")
    parser.add_argument("--output", type=str, help="Optional output file path", default=None)

    args = parser.parse_args()
    fetch_drive_doc(args.file_id, args.output)
