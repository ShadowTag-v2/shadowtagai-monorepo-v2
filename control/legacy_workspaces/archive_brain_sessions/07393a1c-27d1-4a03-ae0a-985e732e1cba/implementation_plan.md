# LangExtract Ingestion Plan

**Goal:** Ingest documents from specified Google Drive paths using `LangExtract` to create a structured knowledge base.

## User Review Required
> [!NOTE]
> No specific extraction schema was provided. I will use a **General Knowledge Extraction** prompt:
> "Extract key topics, entities, definitions, and relationships found in the text."

## Proposed Changes

### [Scripts] `scripts/ingest_drive_docs.py`
#### [NEW] `scripts/ingest_drive_docs.py`
- **Input:** List of 8 paths provided by user.
- **Processing:**
    - Recursive walk.
    - Filter for `.txt`, `.md`, `.pdf` (if supported), `.epub`.
    - Extract text content.
    - Run `lx.extract`.
- **Output:** `.beads/knowledge_base/extraction_results.jsonl`

### [Configuration]
- Ensure `LANGEXTRACT_API_KEY` or Google Cloud credentials are active. (Using Gemini 3 Flash by default).

## Verification Plan
- Run script on a small subset first (dry run or limit=1).
- Verify JSONL output structure.
