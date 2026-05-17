#!/usr/bin/env python3
"""
Google Drive Knowledge Extractor

Extracts and indexes content from Google Drive including:
- Documents (PDF, DOCX, TXT, MD)
- Ebooks (PDF, EPUB, MOBI)
- Archives (ZIP, TAR.GZ)
- Code files (PY, JS, TS, etc.)
- Spreadsheets, Presentations

USAGE:
    python scripts/extract_google_drive.py

SETUP:
    1. Enable Google Drive API: https://console.cloud.google.com/apis/library/drive.googleapis.com
    2. Create OAuth credentials: https://console.cloud.google.com/apis/credentials
    3. Download credentials.json to this directory
    4. Run script - browser will open for auth
    5. Credentials saved to token.json for future use

OUTPUT:
    - drive_knowledge/
        ├── documents/        # Extracted text from all files
        ├── metadata/         # File metadata (title, author, created)
        ├── embeddings/       # Gemini embeddings for search
        └── index.json        # Master index
"""

import hashlib
import io
import json
import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path

import docx
import ebooklib

# Google AI
import google.generativeai as genai

# Document processing
import PyPDF2
from bs4 import BeautifulSoup
from ebooklib import epub

# Google API
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Configuration
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
CREDENTIALS_FILE = Path(__file__).parent / "credentials.json"
TOKEN_FILE = Path(__file__).parent / "token.json"
DRIVE_KNOWLEDGE_DIR = Path(__file__).parent.parent / "drive_knowledge"

# Supported file types
SUPPORTED_TYPES = {
  # Documents
  "application/pdf": "pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
  "text/plain": "txt",
  "text/markdown": "md",
  # Ebooks
  "application/epub+zip": "epub",
  "application/x-mobipocket-ebook": "mobi",
  # Archives
  "application/zip": "zip",
  "application/x-zip-compressed": "zip",
  "application/gzip": "gzip",
  "application/x-tar": "tar",
  # Google Workspace
  "application/vnd.google-apps.document": "gdoc",
  "application/vnd.google-apps.spreadsheet": "gsheet",
  "application/vnd.google-apps.presentation": "gslides",
  # Code files
  "text/x-python": "py",
  "application/javascript": "js",
  "text/javascript": "js",
  "application/typescript": "ts",
}


def authenticate_drive():
  """Authenticate with Google Drive API."""
  print("🔐 Authenticating with Google Drive...")

  creds = None

  # Check for existing token
  if TOKEN_FILE.exists():
    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

  # If no valid credentials, get new ones
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      if not CREDENTIALS_FILE.exists():
        print("❌ ERROR: credentials.json not found!")
        print("\nSetup instructions:")
        print("1. Go to https://console.cloud.google.com/apis/credentials")
        print("2. Create OAuth 2.0 Client ID")
        print("3. Download JSON and save as credentials.json")
        print(f"4. Place in: {CREDENTIALS_FILE.parent}")
        sys.exit(1)

      flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
      creds = flow.run_local_server(port=0)

    # Save credentials for next run
    with open(TOKEN_FILE, "w") as token:
      token.write(creds.to_json())

  print("   ✓ Authenticated successfully")
  return build("drive", "v3", credentials=creds)


def list_all_files(service, max_files: int = 1000) -> list[dict]:
  """List all files from Google Drive."""
  print(f"\n📂 Scanning Google Drive (max {max_files} files)...")

  files = []
  page_token = None

  while len(files) < max_files:
    try:
      results = (
        service.files()
        .list(
          pageSize=min(100, max_files - len(files)),
          pageToken=page_token,
          fields="nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime, owners, parents, webViewLink)",
          orderBy="modifiedTime desc",
        )
        .execute()
      )

      items = results.get("files", [])
      files.extend(items)

      print(f"   Found {len(files)} files so far...", end="\r")

      page_token = results.get("nextPageToken")
      if not page_token:
        break

    except Exception as e:
      print(f"\n   ✗ Error listing files: {e}")
      break

  print(f"\n   ✓ Found {len(files)} total files")
  return files


def download_file(service, file_id: str, mime_type: str) -> bytes | None:
  """Download file content from Google Drive."""
  try:
    # Google Workspace files need export
    if mime_type.startswith("application/vnd.google-apps"):
      export_mime = {
        "application/vnd.google-apps.document": "text/plain",
        "application/vnd.google-apps.spreadsheet": "text/csv",
        "application/vnd.google-apps.presentation": "text/plain",
      }.get(mime_type, "text/plain")

      request = service.files().export_media(fileId=file_id, mimeType=export_mime)
    else:
      request = service.files().get_media(fileId=file_id)

    file_content = io.BytesIO()
    downloader = MediaIoBaseDownload(file_content, request)

    done = False
    while not done:
      status, done = downloader.next_chunk()

    return file_content.getvalue()

  except Exception as e:
    print(f"      ✗ Download error: {e}")
    return None


def extract_text_from_pdf(content: bytes) -> str:
  """Extract text from PDF."""
  try:
    pdf_file = io.BytesIO(content)
    pdf_reader = PyPDF2.PdfReader(pdf_file)

    text = []
    for page in pdf_reader.pages:
      text.append(page.extract_text())

    return "\n\n".join(text)
  except Exception as e:
    print(f"      ✗ PDF extraction error: {e}")
    return ""


def extract_text_from_epub(content: bytes) -> str:
  """Extract text from EPUB."""
  try:
    epub_file = io.BytesIO(content)
    book = epub.read_epub(epub_file)

    text = []
    for item in book.get_items():
      if item.get_type() == ebooklib.ITEM_DOCUMENT:
        soup = BeautifulSoup(item.get_content(), "html.parser")
        text.append(soup.get_text())

    return "\n\n".join(text)
  except Exception as e:
    print(f"      ✗ EPUB extraction error: {e}")
    return ""


def extract_text_from_docx(content: bytes) -> str:
  """Extract text from DOCX."""
  try:
    docx_file = io.BytesIO(content)
    doc = docx.Document(docx_file)

    text = []
    for paragraph in doc.paragraphs:
      text.append(paragraph.text)

    return "\n\n".join(text)
  except Exception as e:
    print(f"      ✗ DOCX extraction error: {e}")
    return ""


def extract_text_from_zip(content: bytes, max_files: int = 50) -> dict[str, str]:
  """Extract text from files inside ZIP archive."""
  try:
    zip_file = io.BytesIO(content)
    extracted = {}

    with zipfile.ZipFile(zip_file, "r") as zf:
      file_list = zf.namelist()[:max_files]  # Limit files processed

      for filename in file_list:
        if filename.endswith("/"):  # Skip directories
          continue

        try:
          file_content = zf.read(filename)

          # Try to decode as text
          if filename.endswith(
            (".txt", ".md", ".py", ".js", ".ts", ".json", ".yaml", ".yml")
          ):
            extracted[filename] = file_content.decode("utf-8", errors="ignore")

          # Try to extract from PDF inside ZIP
          elif filename.endswith(".pdf"):
            extracted[filename] = extract_text_from_pdf(file_content)

          # Try to extract from EPUB inside ZIP
          elif filename.endswith(".epub"):
            extracted[filename] = extract_text_from_epub(file_content)

        except Exception as e:
          print(f"      ✗ Error extracting {filename}: {e}")

    return extracted

  except Exception as e:
    print(f"      ✗ ZIP extraction error: {e}")
    return {}


def extract_text(content: bytes, mime_type: str, filename: str) -> str:
  """Extract text based on file type."""
  file_type = SUPPORTED_TYPES.get(mime_type, "unknown")

  # Handle archives specially - return dict of files
  if file_type == "zip":
    extracted = extract_text_from_zip(content)
    # Combine all extracted files
    return "\n\n---FILE SEPARATOR---\n\n".join(
      [f"FILE: {name}\n\n{text}" for name, text in extracted.items()]
    )

  # Regular file types
  if file_type == "pdf":
    return extract_text_from_pdf(content)
  elif file_type == "epub":
    return extract_text_from_epub(content)
  elif file_type == "docx":
    return extract_text_from_docx(content)
  elif file_type in ["txt", "md", "py", "js", "ts", "gdoc"]:
    return content.decode("utf-8", errors="ignore")
  else:
    # Try to decode as text
    try:
      return content.decode("utf-8", errors="ignore")
    except:
      return ""


def generate_embedding(text: str, api_key: str) -> list[float] | None:
  """Generate Gemini embedding for text."""
  try:
    genai.configure(api_key=api_key)
    result = genai.embed_content(
      model="models/embedding-001",
      content=text[:20000],  # Limit to first 20k chars
      task_type="retrieval_document",
    )
    return result["embedding"]
  except Exception as e:
    print(f"      ✗ Embedding error: {e}")
    return None


def process_files(service, files: list[dict], api_key: str | None = None):
  """Process all files and extract content."""
  print(f"\n📝 Processing {len(files)} files...")

  # Create output directories
  docs_dir = DRIVE_KNOWLEDGE_DIR / "documents"
  metadata_dir = DRIVE_KNOWLEDGE_DIR / "metadata"
  embeddings_dir = DRIVE_KNOWLEDGE_DIR / "embeddings"

  for dir in [docs_dir, metadata_dir, embeddings_dir]:
    dir.mkdir(parents=True, exist_ok=True)

  index = {
    "extracted_at": datetime.now().isoformat(),
    "total_files": len(files),
    "processed": 0,
    "skipped": 0,
    "files": [],
  }

  for i, file in enumerate(files):
    file_id = file["id"]
    name = file["name"]
    mime_type = file["mimeType"]

    print(f"\n   [{i + 1}/{len(files)}] {name}")
    print(f"      Type: {mime_type}")

    # Skip unsupported types
    if mime_type not in SUPPORTED_TYPES:
      print("      ⊘ Skipping unsupported type")
      index["skipped"] += 1
      continue

    # Download file
    print("      ⬇ Downloading...")
    content = download_file(service, file_id, mime_type)
    if not content:
      index["skipped"] += 1
      continue

    # Extract text
    print("      📄 Extracting text...")
    text = extract_text(content, mime_type, name)
    if not text:
      print("      ⊘ No text extracted")
      index["skipped"] += 1
      continue

    # Generate file hash for deduplication
    file_hash = hashlib.md5(content).hexdigest()

    # Save extracted text
    doc_file = docs_dir / f"{file_hash}.txt"
    with open(doc_file, "w") as f:
      f.write(text)

    # Save metadata
    metadata = {
      "id": file_id,
      "name": name,
      "mime_type": mime_type,
      "file_type": SUPPORTED_TYPES.get(mime_type),
      "size": file.get("size", 0),
      "created": file.get("createdTime"),
      "modified": file.get("modifiedTime"),
      "owners": file.get("owners", []),
      "web_link": file.get("webViewLink"),
      "hash": file_hash,
      "text_length": len(text),
      "word_count": len(text.split()),
    }

    metadata_file = metadata_dir / f"{file_hash}.json"
    with open(metadata_file, "w") as f:
      json.dump(metadata, f, indent=2)

    # Generate embedding (if API key provided)
    embedding = None
    if api_key and len(text) > 100:
      print("      🧠 Generating embedding...")
      embedding = generate_embedding(text, api_key)

      if embedding:
        embedding_file = embeddings_dir / f"{file_hash}.json"
        with open(embedding_file, "w") as f:
          json.dump({"embedding": embedding}, f)

    # Add to index
    index["files"].append(
      {
        "hash": file_hash,
        "name": name,
        "type": SUPPORTED_TYPES.get(mime_type),
        "size": file.get("size", 0),
        "word_count": len(text.split()),
        "has_embedding": embedding is not None,
      }
    )

    index["processed"] += 1
    print(f"      ✓ Processed ({len(text)} chars, {len(text.split())} words)")

  # Save index
  index_file = DRIVE_KNOWLEDGE_DIR / "index.json"
  with open(index_file, "w") as f:
    json.dump(index, f, indent=2)

  print(f"\n{'=' * 60}")
  print("✅ Processing Complete!")
  print(f"{'=' * 60}")
  print(f"   Processed: {index['processed']}")
  print(f"   Skipped: {index['skipped']}")
  print(f"   Total words: {sum(f['word_count'] for f in index['files']):,}")
  print(f"\n📂 Output: {DRIVE_KNOWLEDGE_DIR}")
  print("   documents/   - Extracted text files")
  print("   metadata/    - File metadata JSON")
  print("   embeddings/  - Gemini embeddings (if generated)")
  print("   index.json   - Master index")


def main():
  """Main execution flow."""
  print("=" * 60)
  print("Google Drive Knowledge Extractor v1.0")
  print("=" * 60)

  # Check for Google API key (optional, for embeddings)
  api_key = os.environ.get("GOOGLE_API_KEY")
  if api_key:
    print("✓ Google API key found - will generate embeddings")
  else:
    print("⚠ No GOOGLE_API_KEY - skipping embeddings")
    print("  (Set GOOGLE_API_KEY to generate embeddings for search)")

  # Authenticate
  service = authenticate_drive()

  # List files
  files = list_all_files(service)

  # Filter to supported types
  supported_files = [f for f in files if f["mimeType"] in SUPPORTED_TYPES]

  print("\n📊 File type breakdown:")
  type_counts = {}
  for f in supported_files:
    file_type = SUPPORTED_TYPES[f["mimeType"]]
    type_counts[file_type] = type_counts.get(file_type, 0) + 1

  for file_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"   {file_type}: {count}")

  print(f"\n   Total supported: {len(supported_files)} / {len(files)}")

  # Confirm before processing
  response = input(f"\n⚡ Process {len(supported_files)} files? (y/n): ")
  if response.lower() != "y":
    print("Aborted.")
    return

  # Process files
  process_files(service, supported_files, api_key)

  print("\n💡 Next steps:")
  print(f"   1. Review extracted content in {DRIVE_KNOWLEDGE_DIR}")
  print("   2. Run merge script to add to memory system")
  print("   3. Deploy to Claude Code for context-aware assistance")


if __name__ == "__main__":
  main()
