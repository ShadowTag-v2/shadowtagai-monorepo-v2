# TEST_INDEX (PNKLN)

## RAG
- Build from 3 items → returns success and non-empty answer for query "deadlines?"
- Cosine scores monotonic across similar query variants

## OCR
- Summarize empty list → returns string
- Summarize sample image → no exception, non-empty or empty string allowed

## GCS Publish
- publish_manifest(bucket) returns gs:// URL string

## Prompts
- Each prompt template round-trips without Studio validation errors
