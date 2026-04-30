import re
from datetime import UTC, datetime
from pathlib import Path

from ..utils.db import sqlite_conn
from ..utils.hash import sha256_file, sha256_text

TEXT_EXTS = {
    ".md",
    ".txt",
    ".py",
    ".m",
    ".h",
    ".c",
    ".cc",
    ".cpp",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
}
CODE_EXTS = {".py", ".m", ".h", ".c", ".cc", ".cpp"}


def classify_kind(path: Path):
    ext = path.suffix.lower()
    if ext in CODE_EXTS:
        return "code", ext.lstrip(".")
    if ext in TEXT_EXTS or path.name.lower() == "makefile":
        return "doc", ext.lstrip(".") or "make"
    return "other", ext.lstrip(".")


def scan_repo(sqlite_db: str, repo_id: str, repo_root: str):
    root = Path(repo_root)
    now = datetime.now(UTC).isoformat()
    count = 0
    with sqlite_conn(sqlite_db) as conn:
        cur = conn.cursor()
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in {".git", "build", "dist", "__pycache__", ".venv"} for part in path.parts):
                continue
            kind, language = classify_kind(path)
            if kind == "other":
                continue
            rel_path = str(path.relative_to(root))
            doc_id = sha256_text(f"{repo_id}:{rel_path}")
            sha = sha256_file(path)
            size_bytes = path.stat().st_size
            mtime_ns = int(path.stat().st_mtime_ns)
            cur.execute(
                "INSERT OR REPLACE INTO documents (doc_id, repo_id, rel_path, abs_path, kind, language, size_bytes, sha256, mtime_ns, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    doc_id,
                    repo_id,
                    rel_path,
                    str(path),
                    kind,
                    language,
                    size_bytes,
                    sha,
                    mtime_ns,
                    now,
                    now,
                ),
            )
            try:
                body = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                body = ""
            cur.execute("DELETE FROM document_content_fts WHERE doc_id = ?", (doc_id,))
            cur.execute(
                "INSERT INTO document_content_fts (doc_id, rel_path, title, body) VALUES (?, ?, ?, ?)",
                (doc_id, rel_path, path.name, body[:500000]),
            )
            count += 1
    return {"indexed_documents": count}


def extract_symbols(text: str):
    patterns = [
        (r"^\s*[-+]\s*\([^)]*\)\s*([A-Za-z_][A-Za-z0-9_]*)", "objc_method"),
        (r"^\s*(?:def|class)\s+([A-Za-z_][A-Za-z0-9_]*)", "python"),
        (
            r"^\s*(?:static\s+)?(?:inline\s+)?[A-Za-z_][\w\s\*]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(",
            "c_func",
        ),
    ]
    out = []
    for i, line in enumerate(text.splitlines(), start=1):
        for pat, kind in patterns:
            m = re.search(pat, line)
            if m:
                out.append((m.group(1), kind, i, i))
    return out


def refresh_symbols(sqlite_db: str):
    inserted = 0
    with sqlite_conn(sqlite_db) as conn:
        cur = conn.cursor()
        rows = cur.execute("SELECT doc_id, abs_path FROM documents").fetchall()
        for doc_id, abs_path in rows:
            cur.execute("DELETE FROM symbols WHERE doc_id = ?", (doc_id,))
            try:
                text = Path(abs_path).read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for name, kind, start, end in extract_symbols(text):
                sid = sha256_text(f"{doc_id}:{name}:{start}:{kind}")
                cur.execute(
                    "INSERT OR REPLACE INTO symbols (symbol_id, doc_id, symbol_name, symbol_kind, signature, line_start, line_end, parent_symbol) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (sid, doc_id, name, kind, None, start, end, None),
                )
                inserted += 1
    return {"symbols_inserted": inserted}


def chunk_text(sqlite_db: str):
    chunks = []
    with sqlite_conn(sqlite_db) as conn:
        cur = conn.cursor()
        rows = cur.execute("SELECT doc_id, rel_path, abs_path, kind, language, sha256 FROM documents").fetchall()
        for doc_id, rel_path, abs_path, kind, language, sha in rows:
            try:
                text = Path(abs_path).read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            lines = text.splitlines()
            step = 80 if kind == "doc" else 120
            for start in range(0, len(lines), step):
                end = min(start + step, len(lines))
                content = "\n".join(lines[start:end]).strip()
                if not content:
                    continue
                chunk_id = sha256_text(f"{doc_id}:{start}:{end}")
                section_path = f"{rel_path}:{start + 1}-{end}"
                chunks.append(
                    {
                        "chunk_id": chunk_id,
                        "doc_id": doc_id,
                        "repo_id": "ane",
                        "rel_path": rel_path,
                        "chunk_type": kind,
                        "language": language or "",
                        "title": Path(rel_path).name,
                        "content": content,
                        "section_path": section_path,
                        "start_line": start + 1,
                        "end_line": end,
                        "importance": 0.5,
                        "sha256": sha,
                        "metadata_json": "{}",
                    }
                )
                cur.execute(
                    "INSERT OR REPLACE INTO chunk_manifest (chunk_id, doc_id, rel_path, chunk_type, section_path, start_line, end_line, sha256, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))",
                    (chunk_id, doc_id, rel_path, kind, section_path, start + 1, end, sha),
                )
    return chunks


def exact_search(sqlite_db: str, query: str, limit: int = 8):
    with sqlite_conn(sqlite_db) as conn:
        conn.row_factory = lambda cur, row: {
            "doc_id": row[0],
            "rel_path": row[1],
            "title": row[2],
            "body": row[3],
        }
        cur = conn.cursor()
        try:
            return cur.execute(
                "SELECT doc_id, rel_path, title, snippet(document_content_fts, 3, '[', ']', ' … ', 16) FROM document_content_fts WHERE document_content_fts MATCH ? LIMIT ?",
                (query, limit),
            ).fetchall()
        except Exception:
            return []
