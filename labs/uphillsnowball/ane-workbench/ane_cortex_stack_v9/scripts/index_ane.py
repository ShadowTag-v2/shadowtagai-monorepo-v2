from service.app.config import load_settings
from service.app.retrieval.sqlite_index import scan_repo, refresh_symbols, chunk_text
from service.app.retrieval.lancedb_store import upsert_chunks
from service.app.jobs.sync_postgres import sync_doc_registry

s = load_settings()
print(scan_repo(s.sqlite_db, s.repo_id, s.repo_root))
print(refresh_symbols(s.sqlite_db))
chunks = chunk_text(s.sqlite_db)
print({"chunked": len(chunks)})
print(upsert_chunks(s.lancedb_root, chunks))
print(sync_doc_registry(s.sqlite_db, s.postgres_dsn, s.repo_id))
