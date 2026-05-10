"""
intent_sync.py — Human-to-Machine Bridge (Workspace → Epistemic Engine)

Autonomously polls Google Drive for PRDs, reads them, and permanently
writes them to the multi-modal Gemini File Search vector space.

The human writes intent in Google Docs. The agent reads it, embeds it,
and executes it. No prompt engineering required.

Requirements:
    pip install google-api-python-client google-auth google-genai
"""

import os
import sys
import json
import time
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="[intent_sync] %(message)s")
log = logging.getLogger(__name__)


def fetch_and_embed_business_intent(
  drive_folder_id: str | None = None,
  store_name: str | None = None,
) -> dict:
  """
  Autonomously reads human PRDs from Drive and embeds them into Sovereign Memory.

  Args:
      drive_folder_id: Google Drive folder ID containing PRD_ documents.
      store_name: Gemini FileSearchStore name to upload into.

  Returns:
      dict with status and embedded file URIs.
  """
  try:
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    from google import genai
  except ImportError as e:
    return {
      "error": f"Missing dependency: {e}. Run: pip install google-api-python-client google-auth google-genai"
    }

  # --- Auth ---
  sa_path = os.environ.get(
    "GOOGLE_APPLICATION_CREDENTIALS",
    str(Path(__file__).parent.parent.parent / "secrets" / "workspace-sa.json"),
  )
  if not Path(sa_path).exists():
    # Fall back to ADC
    from google.auth import default

    creds, _ = default(scopes=["https://www.googleapis.com/auth/drive.readonly"])
  else:
    creds = service_account.Credentials.from_service_account_file(
      sa_path,
      scopes=["https://www.googleapis.com/auth/drive.readonly"],
    )

  drive_service = build("drive", "v3", credentials=creds)

  api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
  if not api_key:
    return {"error": "GEMINI_API_KEY not set"}

  client = genai.Client(api_key=api_key)

  # --- 1. Poll for PRD documents ---
  query = "name contains 'PRD_' and mimeType='application/vnd.google-apps.document'"
  if drive_folder_id:
    query += f" and '{drive_folder_id}' in parents"

  results = (
    drive_service.files()
    .list(
      q=query,
      fields="files(id, name, modifiedTime)",
      orderBy="modifiedTime desc",
      pageSize=10,
    )
    .execute()
  )

  files = results.get("files", [])
  if not files:
    return {
      "status": "idle",
      "message": "No PRD_ documents found. Awaiting business intent.",
    }

  log.info(f"Found {len(files)} PRD documents")

  embedded = []
  for file_info in files:
    file_id = file_info["id"]
    file_name = file_info["name"]

    # --- 2. Export Google Doc to plain text ---
    request = drive_service.files().export_media(fileId=file_id, mimeType="text/plain")
    content = request.execute()

    tmp_path = Path(f"/tmp/{file_name}.txt")
    tmp_path.write_bytes(content)

    # --- 3. Upload to Epistemic Engine with metadata ---
    if store_name:
      operation = client.file_search_stores.upload_to_file_search_store(
        file=str(tmp_path),
        file_search_store_name=store_name,
        config={
          "displayName": file_name,
          "customMetadata": [
            {"key": "domain", "stringValue": "general"},
            {"key": "source", "stringValue": "design_doc"},
            {"key": "status", "stringValue": "active"},
            {
              "key": "last_modified",
              "stringValue": file_info.get("modifiedTime", "")[:10],
            },
            {"key": "component", "stringValue": "agent"},
          ],
        },
      )

      # Poll for completion
      attempts = 0
      while not operation.done and attempts < 60:
        time.sleep(2)
        operation = client.operations.get(operation)
        attempts += 1

      embedded.append(
        {
          "name": file_name,
          "store": store_name,
          "indexed": operation.done,
        }
      )
      log.info(f"Embedded: {file_name} → {store_name} (done={operation.done})")
    else:
      log.info(f"Skipping embed (no store_name): {file_name}")

    tmp_path.unlink(missing_ok=True)

  return {
    "status": "synced",
    "documents_found": len(files),
    "documents_embedded": len(embedded),
    "details": embedded,
  }


if __name__ == "__main__":
  folder_id = os.environ.get("DRIVE_WATCH_FOLDER_ID")
  store = sys.argv[1] if len(sys.argv) > 1 else None
  result = fetch_and_embed_business_intent(folder_id, store)
  print(json.dumps(result, indent=2))
