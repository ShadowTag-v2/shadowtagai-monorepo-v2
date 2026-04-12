PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS documents (
  doc_id TEXT PRIMARY KEY,
  repo_id TEXT NOT NULL,
  rel_path TEXT NOT NULL,
  abs_path TEXT NOT NULL,
  kind TEXT NOT NULL,
  language TEXT,
  size_bytes INTEGER,
  sha256 TEXT NOT NULL,
  mtime_ns INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS document_content_fts USING fts5(
  doc_id UNINDEXED,
  rel_path,
  title,
  body,
  tokenize = 'unicode61'
);

CREATE TABLE IF NOT EXISTS symbols (
  symbol_id TEXT PRIMARY KEY,
  doc_id TEXT NOT NULL,
  symbol_name TEXT NOT NULL,
  symbol_kind TEXT NOT NULL,
  signature TEXT,
  line_start INTEGER,
  line_end INTEGER,
  parent_symbol TEXT
);

CREATE TABLE IF NOT EXISTS chunk_manifest (
  chunk_id TEXT PRIMARY KEY,
  doc_id TEXT NOT NULL,
  rel_path TEXT NOT NULL,
  chunk_type TEXT NOT NULL,
  section_path TEXT,
  start_line INTEGER,
  end_line INTEGER,
  sha256 TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
