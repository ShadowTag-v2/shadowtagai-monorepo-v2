# Storing memories as indexless JSON

Use append-only JSONL.

Example line:
{"id":"...","type":"decision","subject":"ANE fallback policy","summary":"ANE first, Metal fallback on validation mismatch","body":"Longer note here","tags":["ane","fallback"],"repo_id":"ane","created_at":"2026-03-17T00:00:00Z"}

## Why JSONL
- append-only
- git-friendly
- human-readable
- simple export/import
- excellent as a journal and audit trail

## Best pattern
Use JSONL as the journal.
Use Postgres/LanceDB as the retrieval layer.

## When it works well
- hundreds to low thousands of memories
- local single-user flow
- startup hydration
- audit/replay
