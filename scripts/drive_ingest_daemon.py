#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from __future__ import annotations

"""
SYSTEM PROMPT (ArXiv 2512.14982 - PROMPT REPETITION ENFORCEMENT):
Ensure you reprint all thread code, number of atomic code blocks being irrelevant. In so doing, Be elegant and Steve Jobs-esque, to thereby generate us the best uplift in performance, accuracy, and financial output possible.
Ensure you reprint all thread code, number of atomic code blocks being irrelevant. In so doing, Be elegant and Steve Jobs-esque, to thereby generate us the best uplift in performance, accuracy, and financial output possible.
Ensure you reprint all thread code, number of atomic code blocks being irrelevant. In so doing, Be elegant and Steve Jobs-esque, to thereby generate us the best uplift in performance, accuracy, and financial output possible.

Cor.Gemini.Leaks (v3.0-LOCAL)
Drive Ingest Daemon — extracts all Google Drive docs to local Mac.
Checkpoint: SQLite (file_id dedup, resumable). Output: JSONL + per-doc text files.
No LanceDB. No remote push. Local only.
"""

import json
import logging
import os
import sqlite3
import sys
import textwrap
import time
from pathlib import Path

from google import genai as google_genai  # noqa: E402
from googleapiclient.discovery import build  # noqa: E402

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import langextract as lx  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

from shared.config import settings  # noqa: E402

load_dotenv(override=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DriveIngest")

ROOT = Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball")
OUT = ROOT / "data" / "drive_ingest"
OUT.mkdir(parents=True, exist_ok=True)

DB_PATH = OUT / "ingest.db"
JSONL_PATH = OUT / "extractions.jsonl"
DOCS_PATH = OUT / "docs"
DOCS_PATH.mkdir(exist_ok=True)

MODEL_ID = "gemini-3.1-flash-lite-preview"
EMBED_MODEL = "text-embedding-004"
RATE_DELAY = 1.0
MAX_RETRIES = 3

MIME_EXPORT: dict[str, str] = {
    "application/vnd.google-apps.document": "text/plain",
    "application/vnd.google-apps.presentation": "text/plain",
    "application/vnd.google-apps.spreadsheet": "text/csv",
}

SUPPORTED_MIMES = list(MIME_EXPORT.keys()) + [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown",
    "text/csv",
]

EXTRACT_PROMPT = textwrap.dedent("""\
    You are extracting structured intelligence from scholarly sources for business plan validation.
    For each document extract:
    - claim: a key finding, argument, or conclusion stated by the authors
    - evidence: data, statistics, or empirical support for a claim
    - methodology: research design, study type, or analytical approach used
    - framework: theoretical or conceptual model proposed or applied
    - citation: author(s), year, title, or journal referenced within the text
    - concept: a domain term or idea explicitly defined or central to the work

    Be precise. Quote or closely paraphrase. Do not hallucinate.
    Each extraction must be directly traceable to the provided text.
""")

EXAMPLES = [
    lx.data.ExampleData(
        text=(
            "Smith & Lee (2021) found that venture-backed startups with formal advisory boards "
            "had a 34% higher 5-year survival rate (n=1,200, p<0.01), using Cox proportional "
            "hazards regression on Crunchbase longitudinal data."
        ),
        extractions=[
            lx.data.Extraction(
                extraction_class="claim",
                extraction_text=("Venture-backed startups with formal advisory boards had a 34% higher 5-year survival rate"),
                attributes={"confidence": "p<0.01", "sample_size": "n=1200"},
            ),
            lx.data.Extraction(
                extraction_class="evidence",
                extraction_text="34% higher 5-year survival rate (n=1,200, p<0.01)",
                attributes={"metric": "survival_rate", "delta": "+34%"},
            ),
            lx.data.Extraction(
                extraction_class="methodology",
                extraction_text=("Cox proportional hazards regression on Crunchbase longitudinal data"),
                attributes={"study_type": "longitudinal", "dataset": "Crunchbase"},
            ),
            lx.data.Extraction(
                extraction_class="citation",
                extraction_text="Smith & Lee (2021)",
                attributes={"year": "2021"},
            ),
        ],
    )
]


# ── Checkpoint DB ──────────────────────────────────────────────────────────────


class CheckpointDB:
    def __init__(self, path: Path) -> None:
        self.conn = sqlite3.connect(path)
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS processed (
                file_id TEXT PRIMARY KEY,
                name    TEXT,
                status  TEXT,
                count   INTEGER,
                ts      TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS extractions (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT,
                name    TEXT,
                class   TEXT,
                text    TEXT,
                attrs   TEXT
            );
            CREATE VIRTUAL TABLE IF NOT EXISTS extractions_fts
                USING fts5(text, name, class, content='extractions', content_rowid='id');
            CREATE TRIGGER IF NOT EXISTS extractions_ai
                AFTER INSERT ON extractions BEGIN
                    INSERT INTO extractions_fts(rowid, text, name, class)
                    VALUES (new.id, new.text, new.name, new.class);
                END;
        """)
        self.conn.commit()

    def is_done(self, file_id: str) -> bool:
        row = self.conn.execute("SELECT status FROM processed WHERE file_id=?", (file_id,)).fetchone()
        return row is not None and row[0] == "ok"

    def insert_extractions(self, file_id: str, name: str, extractions: list[dict]) -> None:
        self.conn.executemany(
            "INSERT INTO extractions(file_id,name,class,text,attrs) VALUES(?,?,?,?,?)",
            [(file_id, name, e["class"], e["text"], json.dumps(e["attrs"])) for e in extractions],
        )
        self.conn.commit()

    def mark(self, file_id: str, name: str, status: str, count: int = 0) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO processed(file_id,name,status,count) VALUES(?,?,?,?)",
            (file_id, name, status, count),
        )
        self.conn.commit()

    def stats(self) -> dict:
        row = self.conn.execute("SELECT COUNT(*), SUM(count), SUM(status='ok'), SUM(status='failed') FROM processed").fetchone()
        return {
            "total": row[0],
            "extractions": row[1] or 0,
            "ok": row[2] or 0,
            "failed": row[3] or 0,
        }


# ── Embedder ───────────────────────────────────────────────────────────────────


class Embedder:
    """text-embedding-004 via google-genai. 768-dim, rate-limited."""

    MAX_CHARS = 9_000

    def __init__(self, api_key: str) -> None:
        self.client = google_genai.Client(api_key=api_key)
        self._last_call = 0.0

    def embed(self, text: str) -> list[float]:
        text = text[: self.MAX_CHARS]
        gap = 0.5 - (time.monotonic() - self._last_call)
        if gap > 0:
            time.sleep(gap)
        response = self.client.models.embed_content(model=EMBED_MODEL, contents=text)
        self._last_call = time.monotonic()
        return response.embeddings[0].values


# ── Drive client ───────────────────────────────────────────────────────────────


class DriveClient:
    def __init__(self, credentials) -> None:  # type: ignore[no-untyped-def]
        self.svc = build("drive", "v3", credentials=credentials)

    def list_all(self) -> list[dict]:
        mime_filter = " or ".join(f"mimeType='{m}'" for m in SUPPORTED_MIMES)
        query = f"({mime_filter}) and trashed=false"
        files: list[dict] = []
        token = None
        while True:
            resp = (
                self.svc.files()
                .list(
                    q=query,
                    pageSize=100,
                    pageToken=token,
                    fields="nextPageToken, files(id, name, mimeType, modifiedTime)",
                )
                .execute()
            )
            files.extend(resp.get("files", []))
            token = resp.get("nextPageToken")
            if not token:
                break
        return files

    def export_text(self, file_id: str, mime_type: str) -> str:
        export_mime = MIME_EXPORT.get(mime_type, "text/plain")
        raw = self.svc.files().export(fileId=file_id, mimeType=export_mime).execute()
        return raw.decode("utf-8", errors="ignore") if isinstance(raw, bytes) else raw

    def download_media(self, file_id: str) -> bytes:
        import io

        from googleapiclient.http import MediaIoBaseDownload

        request = self.svc.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        return fh.getvalue()


# ── Extractor ──────────────────────────────────────────────────────────────────


class Extractor:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        # Connect zero_cpu_router bypassing network requests
        import os
        import sys

        zero_cpu_path = os.path.join(PROJECT_ROOT, "apps/aiyou_stack/aiyou-fastapi-services")
        if zero_cpu_path not in sys.path:
            sys.path.insert(0, zero_cpu_path)

    def extract(self, text: str, doc_name: str) -> list[dict]:
        if not text.strip():
            return []

        import zero_cpu_router

        try:
            return zero_cpu_router.dispatch_compute(text=text, prompt_description=EXTRACT_PROMPT, examples=EXAMPLES, file_name=doc_name)
        except Exception as e:
            logger.error(f"Zero-CPU ANE Extraction failed for {doc_name}: {e}")
            return []


# ── JSONL writer ───────────────────────────────────────────────────────────────


class JSONLWriter:
    def __init__(self, path: Path) -> None:
        self.fh = open(path, "a", encoding="utf-8")  # noqa: SIM115

    def write(self, file_id: str, extractions: list[dict]) -> None:
        for ex in extractions:
            self.fh.write(json.dumps({"file_id": file_id, **ex}) + "\n")
        self.fh.flush()

    def close(self) -> None:
        self.fh.close()


# ── Orchestrator ───────────────────────────────────────────────────────────────


class SovereignDriveIngester:
    def __init__(self) -> None:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials

        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file(
                "token.json", ["https://www.googleapis.com/auth/cloud-platform", "https://www.googleapis.com/auth/drive.readonly"]
            )

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                raise RuntimeError("token.json missing or invalid. Please execute `python scripts/auth_setup.py` first to bind the Web Client ID!")
        logger.info("Auth bound via Dedicated Client ID token.json")

        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("LANGEXTRACT_API_KEY") or getattr(settings, "gemini_api_key", None)
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set")

        self.embedder = Embedder(api_key)
        self.drive = DriveClient(creds)
        self.extractor = Extractor(api_key)
        self.db = CheckpointDB(DB_PATH)
        self.writer = JSONLWriter(JSONL_PATH)

    def run(self) -> None:
        files = self.drive.list_all()
        logger.info(f"Found {len(files)} docs across {len(SUPPORTED_MIMES)} MIME types")

        for i, f in enumerate(files, 1):
            fid, name, mime = f["id"], f["name"], f["mimeType"]

            if self.db.is_done(fid):
                logger.info(f"[{i}/{len(files)}] Skip (done): {name}")
                continue

            logger.info(f"[{i}/{len(files)}] Processing: {name}")
            try:
                if mime.startswith("application/vnd.google-apps"):
                    text = self.drive.export_text(fid, mime)
                elif mime == "application/pdf":
                    # Bypass Gemini 1,000-page File API limit by scaling extraction locally using ODL.
                    # OpenDataLoader massively improves table fidelity and formatting natively.
                    media_bytes = self.drive.download_media(fid)
                    from opendataloader_pdf import convert

                    safe_name = "".join(c for c in name if c.isalnum() or c in " _-").strip()
                    temp_pdf_path = DOCS_PATH / f"{safe_name}_{fid}.pdf"
                    temp_pdf_path.write_bytes(media_bytes)

                    convert(
                        input_path=str(temp_pdf_path),
                        output_dir=str(DOCS_PATH),
                        format=["markdown"],
                    )

                    temp_md_path = DOCS_PATH / f"{safe_name}_{fid}.md"
                    if temp_md_path.exists():
                        text = temp_md_path.read_text(encoding="utf-8")
                        temp_pdf_path.unlink(missing_ok=True)
                        temp_md_path.unlink(missing_ok=True)
                    else:
                        text = ""
                elif mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    media_bytes = self.drive.download_media(fid)
                    import io

                    import mammoth

                    with io.BytesIO(media_bytes) as docx_file:
                        result = mammoth.convert_to_markdown(docx_file)
                        text = result.value
                else:
                    media_bytes = self.drive.download_media(fid)
                    text = media_bytes.decode("utf-8", errors="ignore")

                # Save raw text locally
                safe = "".join(c for c in name if c.isalnum() or c in " _-").strip()
                (DOCS_PATH / f"{safe}_{fid}.txt").write_text(text, encoding="utf-8")

                extractions = self.extractor.extract(text, name)

                # Embed each extraction
                for ex in extractions:
                    try:
                        ex["embedding"] = self.embedder.embed(ex["text"])
                    except Exception as emb_err:
                        logger.warning(f"Embed failed in {name}: {emb_err}")
                        ex["embedding"] = None

                self.writer.write(fid, extractions)
                self.db.insert_extractions(fid, name, extractions)
                self.db.mark(fid, name, "ok", len(extractions))
                logger.info(f"  → {len(extractions)} extractions saved locally")

            except Exception as e:
                logger.error(f"  → Failed: {e}")
                self.db.mark(fid, name, "failed")

            time.sleep(RATE_DELAY)

        self.writer.close()
        stats = self.db.stats()
        logger.info(
            f"Done. {stats['ok']}/{stats['total']} docs OK, {stats['extractions']} total extractions, {stats['failed']} failed.\nOutput: {OUT}"
        )

        # Fire Intelligence Layer Hook
        import subprocess
        import sys

        try:
            subprocess.run(
                [sys.executable, "core/rag_evolve.py", "--post-ingest", "drive"],
                cwd="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball",
                check=False,
            )
        except Exception as trigger_err:
            logger.error(f"Post-ingest intelligence loop failed to trigger: {trigger_err}")


if __name__ == "__main__":
    logger.info("Starting Sovereign Drive Ingest v3.0 (local)...")
    SovereignDriveIngester().run()
