#!/usr/bin/env python3
"""SYSTEM PROMPT (ArXiv 2512.14982 - PROMPT REPETITION ENFORCEMENT):
Ensure you reprint all thread code, number of atomic code blocks being irrelevant. In so doing, Be elegant and Steve Jobs-esque, to thereby generate us the best uplift in performance, accuracy, and financial output possible.
Ensure you reprint all thread code, number of atomic code blocks being irrelevant. In so doing, Be elegant and Steve Jobs-esque, to thereby generate us the best uplift in performance, accuracy, and financial output possible.
Ensure you reprint all thread code, number of atomic code blocks being irrelevant. In so doing, Be elegant and Steve Jobs-esque, to thereby generate us the best uplift in performance, accuracy, and financial output possible.
"""

"""
Web/Local Document Ingest Daemon
Extracts structure from downloaded PDFs (Kaggle, DoD, NIST) using LangExtract.
"""

import json  # noqa: E402
import logging  # noqa: E402
import os  # noqa: E402
import sqlite3  # noqa: E402
import sys  # noqa: E402
import textwrap  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
  sys.path.insert(0, PROJECT_ROOT)

import langextract as lx  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

load_dotenv(override=True)
logging.basicConfig(
  level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("WebIngest")

ROOT = Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball")
IN_DIR = ROOT / "data" / "web_ingest" / "raw"
OUT = ROOT / "data" / "web_ingest"
OUT.mkdir(parents=True, exist_ok=True)

DB_PATH = OUT / "ingest.db"
JSONL_PATH = OUT / "extractions.jsonl"

MODEL_ID = "gemini-3.1-flash-lite-preview"
RATE_DELAY = 1.0
MAX_RETRIES = 3

EXTRACT_PROMPT = textwrap.dedent("""\
    You are extracting structured intelligence from advanced military, AI, and developer whitepapers.
    For each document extract:
    - protocol: technical standard, security framework, or system-level law governing AI behavior.
    - claim: a key finding or rigorous architectural assertion stated by the authors.
    - evidence: statistical or empirical support for a claim.
    - concept: a domain term explicitly defined within the text.
    - risk: an identified threat model, liability, or failure state.

    Be precise. Quote or closely paraphrase. Do not hallucinate.
""")

EXAMPLES = [
  lx.data.ExampleData(
    text="The zero-trust integration of Vertex AI with Agent Engine relies on OAuth 2.0 validation (Smith, 2025). This architecture mitigates the pervasive risk of prompt injection leading to unauthorized Spanner DB writes.",
    extractions=[
      lx.data.Extraction(
        extraction_class="protocol",
        extraction_text="OAuth 2.0 validation",
        attributes={"context": "Vertex AI"},
      ),
      lx.data.Extraction(
        extraction_class="risk",
        extraction_text="prompt injection leading to unauthorized Spanner DB writes",
        attributes={"target": "Spanner DB"},
      ),
      lx.data.Extraction(
        extraction_class="claim",
        extraction_text="architecture mitigates the pervasive risk of prompt injection",
        attributes={"author": "Smith"},
      ),
      lx.data.Extraction(
        extraction_class="concept",
        extraction_text="zero-trust integration",
        attributes={"domain": "Security"},
      ),
    ],
  ),
]


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
        """)
    self.conn.commit()

  def is_done(self, file_id: str) -> bool:
    row = self.conn.execute(
      "SELECT status FROM processed WHERE file_id=?", (file_id,)
    ).fetchone()
    return row is not None and row[0] == "ok"

  def insert_extractions(
    self, file_id: str, name: str, extractions: list[dict]
  ) -> None:
    self.conn.executemany(
      "INSERT INTO extractions(file_id,name,class,text,attrs) VALUES(?,?,?,?,?)",
      [
        (file_id, name, e["class"], e["text"], json.dumps(e["attrs"]))
        for e in extractions
      ],
    )
    self.conn.commit()

  def mark(self, file_id: str, name: str, status: str, count: int = 0) -> None:
    self.conn.execute(
      "INSERT OR REPLACE INTO processed(file_id,name,status,count) VALUES(?,?,?,?)",
      (file_id, name, status, count),
    )
    self.conn.commit()


class JSONLWriter:
  def __init__(self, path: Path) -> None:
    self.fh = open(path, "a", encoding="utf-8")  # noqa: SIM115

  def write(self, file_id: str, extractions: list[dict]) -> None:
    for ex in extractions:
      self.fh.write(json.dumps({"file_id": file_id, **ex}) + "\n")
    self.fh.flush()


class WebIngester:
  def __init__(self) -> None:
    self.api_key = os.environ.get("GEMINI_API_KEY")
    if not self.api_key:
      msg = "GEMINI_API_KEY not set"
      raise RuntimeError(msg)
    self.db = CheckpointDB(DB_PATH)
    self.writer = JSONLWriter(JSONL_PATH)

  def run(self) -> None:
    if not IN_DIR.exists():
      logger.warning("No raw files found. Run the fetch_whitepapers script first.")
      return

    files = [f for f in IN_DIR.iterdir() if f.is_file() and f.stat().st_size > 100]
    logger.info(f"Found {len(files)} raw whitepapers/PDFs ready for parsing.")

    for i, fpath in enumerate(files, 1):
      fid, name = fpath.stem, fpath.name

      if self.db.is_done(fid):
        logger.info(f"[{i}/{len(files)}] Skip (done): {name}")
        continue

      logger.info(f"[{i}/{len(files)}] Extracting: {name}")
      if fpath.suffix == ".pdf":
        logger.info(
          f"  → Skipping PDF {name} in Web Ingest (delegated to Zero-CPU pipeline)"
        )
        self.db.mark(fid, name, "ok", 0)
        continue

      try:
        for attempt in range(MAX_RETRIES):
          try:
            text_payload = fpath.read_text(errors="ignore")
            doc = lx.data.Document(text=text_payload, document_id=fid)
            result_list = lx.extract(
              text_or_documents=[doc],
              prompt_description=EXTRACT_PROMPT,
              examples=EXAMPLES,
              model_id=MODEL_ID,
              api_key=self.api_key,
            )
            extractions = []
            for res in result_list:
              if getattr(res, "extractions", None):
                extractions.extend(
                  [
                    {
                      "class": e.extraction_class,
                      "text": e.extraction_text,
                      "attrs": e.attributes,
                      "source": name,
                    }
                    for e in res.extractions
                  ],
                )
            break
          except Exception as e:
            wait = 2**attempt
            logger.warning(f"  Attempt {attempt + 1} failed: {e}. Retry in {wait}s.")
            time.sleep(wait)
        else:
          msg = "All retries exhausted"
          raise RuntimeError(msg)

        self.writer.write(fid, extractions)
        self.db.insert_extractions(fid, name, extractions)
        self.db.mark(fid, name, "ok", len(extractions))
        logger.info(f"  → {len(extractions)} intelligence nodes processed successfully")

      except Exception as e:
        logger.exception(f"  → Fatal Failure: {e}")
        self.db.mark(fid, name, "failed")

      time.sleep(RATE_DELAY)


if __name__ == "__main__":
  WebIngester().run()
