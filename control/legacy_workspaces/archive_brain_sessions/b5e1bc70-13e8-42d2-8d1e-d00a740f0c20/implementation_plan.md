# Ingestion Plan: LangExtract

## Goal
Ingest 18 PDF documents from Google Drive using the `langextract` library.

## Configuration
- **Library**: `langextract` (v1.1.1) + `pypdf` (for text extraction).
- **Model**: `gemini-2.0-flash` (Fast, efficient).
- **API Key**: Loaded from `.env` (`GEMINI_API_KEY`).

## Prompt Strategy
We instruct the model to extract the following attributes as entities (Source Grounding enabled):
- `'title'`: Document title.
- `'author'`: Author names.
- `'summary'`: Concise summary.
- `'key_concept'`: Core concepts.

## Script Logic (`scripts/ingest_langextract.py`)
1.  **Iterate**: Glob `*.pdf` in Source Dir.
2.  **Extract Text**: Convert PDF -> Text.
3.  **LangExtract**:
    *   Call `lx.extract()` with `prompt_description` and generic `examples` (required).
    *   Buffer increased to `30000` chars.
4.  **Save**: Write structured JSONL (grounded) to `artifacts/sovereign_knowledge.jsonl`.
