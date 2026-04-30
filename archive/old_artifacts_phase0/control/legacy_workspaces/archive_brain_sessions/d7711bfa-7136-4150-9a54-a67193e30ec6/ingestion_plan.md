# IMPL PLAN: INGESTION PIPELINE (PHASE 10)

## 1. Goal
Create a robust `POST /api/v1/ingest` endpoint in `judge-sentinel` that:
1.  Receives raw files (PDFs, Images, Text).
2.  Uploads them to GCS (`shadowtag-raw-intake`).
3.  Triggers Gemini 1.5 Pro to extract structured Pitch Deck data.
4.  Saves the result to Firestore (`/projects/{id}`).

## 2. Infrastructure
*   **Service:** `judge-sentinel` (FastAPI).
*   **Storage:** Google Cloud Storage (Bucket: `shadowtag-raw-intake`).
*   **Database:** Firestore (Collection: `projects`).
*   **AI:** Vertex AI `gemini-1.5-pro-preview-0409`.

## 3. Code Structure (`apps/judge-sentinel`)
*   `routers/ingest.py`: The API Handler.
*   `services/storage.py`: GCS Wrapper.
*   `services/extractor.py`: Gemini Logic.

## 4. Verification
*   **Test:** Curl command with a sample PDF.
*   **Success:** JSON response with `{ "project_id": "...", "status": "processing" }` and data visible in Firestore.
