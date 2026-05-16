# Expected performance

- SQLite scan + FTS ingest: under 1 minute for ANE-sized repo
- symbol extraction: seconds to low minutes
- chunking: seconds
- LanceDB upsert: fast locally; embedding generation dominates when using real providers
- /api/search exact hits: near-instant to ~50ms
- semantic search: tens to low hundreds of ms
- /api/context assembly: usually <1s before model generation

## Indexless JSON memory
- writes: extremely cheap append-only
- reads: linear scan
- good for hundreds to low thousands of memories
- not ideal as the only retrieval store once memory volume grows

ANE is configured first for blocking/correctness-sensitive paths in this bundle.
Keep validation + fallback enabled.
