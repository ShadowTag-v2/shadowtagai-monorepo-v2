#!/usr/bin/env python3
"""
Google Drive Document Reader
Reads all Google Docs and PDFs from your Drive, extracts text content.
"""

import io
import json
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/documents.readonly'
]

CLIENT_SECRET_PATH = "/Users/pikeymickey/Downloads/client_secret_215390634092-soouingb3826ubu3m7bseu24c6lu04h4.apps.googleusercontent.com.json"
TOKEN_PATH = Path(__file__).parent / "gdrive_token.json"
OUTPUT_DIR = Path(__file__).parent.parent / "gdrive_content"


def get_credentials():
    """Get or refresh OAuth2 credentials."""
    creds = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    return creds


def list_all_files(service, mime_type: str = None):
    """List all files of a given mime type."""
    files = []
    page_token = None

    query = f"mimeType='{mime_type}'" if mime_type else None

    while True:
        results = service.files().list(
            q=query,
            pageSize=100,
            fields="nextPageToken, files(id, name, mimeType, modifiedTime)",
            pageToken=page_token
        ).execute()

        files.extend(results.get('files', []))
        page_token = results.get('nextPageToken')

        if not page_token:
            break

    return files


def export_google_doc(service, file_id: str, file_name: str) -> str:
    """Export a Google Doc as plain text."""
    try:
        request = service.files().export_media(
            fileId=file_id,
            mimeType='text/plain'
        )
        content = request.execute()
        return content.decode('utf-8')
    except Exception as e:
        print(f"  Error exporting {file_name}: {e}")
        return ""


def download_pdf(service, file_id: str, file_name: str) -> bytes:
    """Download a PDF file."""
    try:
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        return fh.getvalue()
    except Exception as e:
        print(f"  Error downloading {file_name}: {e}")
        return b""


def extract_pdf_text(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes using PyMuPDF."""
    if not HAS_PYMUPDF:
        return "[PyMuPDF not installed - cannot extract PDF text]"

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        return f"[Error extracting PDF: {e}]"


def sanitize_filename(name: str) -> str:
    """Sanitize filename for filesystem."""
    return "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name)


def main():
    print("///▞ GDRIVE READER :: Initializing")

    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Authenticate
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)

    print("///▞ GDRIVE READER :: Authenticated")

    # Get all Google Docs
    print("\n=== Google Docs ===")
    docs = list_all_files(service, 'application/vnd.google-apps.document')
    print(f"Found {len(docs)} Google Docs")

    for doc in docs:
        print(f"  Processing: {doc['name']}")
        content = export_google_doc(service, doc['id'], doc['name'])

        if content:
            filename = sanitize_filename(doc['name']) + ".txt"
            filepath = OUTPUT_DIR / filename
            filepath.write_text(content)
            print(f"    Saved: {filepath}")

    # Get all PDFs
    print("\n=== PDFs ===")
    pdfs = list_all_files(service, 'application/pdf')
    print(f"Found {len(pdfs)} PDFs")

    for pdf in pdfs:
        print(f"  Processing: {pdf['name']}")
        pdf_bytes = download_pdf(service, pdf['id'], pdf['name'])

        if pdf_bytes:
            # Save raw PDF
            pdf_filename = sanitize_filename(pdf['name']) + ".pdf"
            pdf_filepath = OUTPUT_DIR / pdf_filename
            pdf_filepath.write_bytes(pdf_bytes)

            # Extract and save text
            text = extract_pdf_text(pdf_bytes)
            if text and not text.startswith("["):
                txt_filename = sanitize_filename(pdf['name']) + "_extracted.txt"
                txt_filepath = OUTPUT_DIR / txt_filename
                txt_filepath.write_text(text)
                print(f"    Saved: {txt_filepath}")
            else:
                print(f"    Saved PDF only (no text extraction): {pdf_filepath}")

    # Summary
    print("\n///▞ GDRIVE READER :: Complete")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Total docs processed: {len(docs)}")
    print(f"Total PDFs processed: {len(pdfs)}")

    # Create manifest
    manifest = {
        "docs": [{"id": d['id'], "name": d['name']} for d in docs],
        "pdfs": [{"id": p['id'], "name": p['name']} for p in pdfs]
    }
    manifest_path = OUTPUT_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"Manifest saved: {manifest_path}")


if __name__ == "__main__":
    main()
