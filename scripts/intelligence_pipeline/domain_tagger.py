"""Step 1 — Domain Tagger.

Classifies each of 2,856 LanceDB documents into:
  tech | biz | memory | arch | research | skills

Pass 1 (free):  heuristic filename regex — covers ~50% instantly
Pass 2 (LLM):   Gemini Flash batches of 20 for the remainder

Output: data/intelligence_pipeline/crossref.db → table doc_domains
"""

import json
import logging
import os
import re
import sqlite3
import time
from datetime import datetime
from pathlib import Path

import google.auth
import google.auth.transport.requests

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent.parent
DB_PATH = REPO_ROOT / "data" / "intelligence_pipeline" / "crossref.db"
LANCEDB_PATH = REPO_ROOT / "data" / "lancedb" / "workspace_knowledge"

GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "shadowtag-omega-v4")
REGION = "us-central1"
MODEL = "gemini-3.1-flash-lite-preview"
ENDPOINT = (
    f"https://{REGION}-aiplatform.googleapis.com/v1/projects/{GCP_PROJECT_ID}/locations/{REGION}/publishers/google/models/{MODEL}:generateContent"
)
TEMPERATURE = 0.3
MAX_TOKENS = 800

# Heuristic regex patterns for Pass 1
DOMAIN_PATTERNS = {
    "biz": re.compile(
        r"(BIZ_PLAN|revenue|MONETARY|pricing|market|pitch|investor|budget|"
        r"forecast|roadmap|strategy|GTM|go.to.market|ARR|MRR|churn|CAC|LTV)",
        re.IGNORECASE,
    ),
    "arch": re.compile(
        r"(ARCHITECTURE|ADR|CONTROL_PLANE|design_doc|system_design|infra|"
        r"deployment|k8s|kubernetes|terraform|docker|GKE|GCP|cloud_run|pubsub)",
        re.IGNORECASE,
    ),
    "skills": re.compile(
        r"(skill|COPILOT|PROMPT_ADAPTATION|prompt_engineering|few.shot|"
        r"chain.of.thought|agent_behavior|playbook|runbook|SOP)",
        re.IGNORECASE,
    ),
    "tech": re.compile(
        r"(requirements\.txt|CMakeLists|package\.json|pyproject|setup\.py|"
        r"Makefile|\.bazelrc|\.go|\.ts|\.py|API_spec|openapi|swagger|"
        r"migration|schema|database|dockerfile)",
        re.IGNORECASE,
    ),
    "memory": re.compile(
        r"(THREAD_TRANSFER|handoff|memory_lock|memory_state|MEMORY|"
        r"session_snapshot|context_dump|agent_memory|working_memory)",
        re.IGNORECASE,
    ),
    "research": re.compile(
        r"(arxiv|_paper_|_datasheet_|whitepaper|literature_review|benchmark|"
        r"eval_report|ablation|experiment_log|hypothesis)",
        re.IGNORECASE,
    ),
}


def get_access_token() -> str:
    """Get GCP access token via ADC."""
    creds, _ = google.auth.default()
    creds.refresh(google.auth.transport.requests.Request())
    return creds.token


def classify_by_filename(filename: str) -> str | None:
    """Pass 1: heuristic classification by filename patterns."""
    for domain, pattern in DOMAIN_PATTERNS.items():
        if pattern.search(filename):
            return domain
    return None


def classify_batch_llm(docs: list[dict], token: str) -> list[dict]:
    """Pass 2: classify a batch of documents using Gemini Flash."""
    import requests

    prompt = (
        "Classify each document into exactly ONE domain: "
        "tech, biz, memory, arch, research, skills.\n\n"
        'Return JSON array: [{"id": ..., "domain": ...}]\n\n'
    )
    for doc in docs:
        prompt += f"- id={doc['id']}, title={doc.get('title', 'unknown')}\n"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": TEMPERATURE, "maxOutputTokens": MAX_TOKENS},
    }
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.post(ENDPOINT, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()

    text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    # Extract JSON from response
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        return json.loads(match.group())
    return []


def _fallback_classify(title: str) -> str:
    """Fallback classification when LLM fails."""
    return "tech"


def init_db() -> sqlite3.Connection:
    """Initialize crossref.db with doc_domains table."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        """CREATE TABLE IF NOT EXISTS doc_domains (
            doc_id TEXT PRIMARY KEY,
            title TEXT,
            domain TEXT NOT NULL,
            method TEXT NOT NULL,
            tagged_at TEXT NOT NULL
        )""",
    )
    conn.commit()
    return conn


def already_tagged(conn: sqlite3.Connection) -> set:
    """Return set of doc IDs already tagged."""
    rows = conn.execute("SELECT doc_id FROM doc_domains").fetchall()
    return {r[0] for r in rows}


def insert_domain(conn: sqlite3.Connection, doc_id: str, title: str, domain: str, method: str) -> None:
    """Insert a domain classification."""
    conn.execute(
        "INSERT OR REPLACE INTO doc_domains (doc_id, title, domain, method, tagged_at) VALUES (?, ?, ?, ?, ?)",
        (doc_id, title, domain, method, datetime.utcnow().isoformat()),
    )


def run_domain_tagger(cfg=None) -> dict:
    """Execute Step 1: Domain Tagger."""
    import lancedb

    logger.info("Domain Tagger — Step 1")

    db = lancedb.connect(str(REPO_ROOT / "data" / "lancedb"))
    tbl = db.open_table("workspace_knowledge")
    docs = tbl.to_pandas()
    logger.info(f"Loaded {len(docs)} documents from LanceDB")

    conn = init_db()
    tagged = already_tagged(conn)
    logger.info(f"Already tagged: {len(tagged)}")

    # Pass 1: heuristic
    heuristic_count = 0
    llm_queue = []
    for _, row in docs.iterrows():
        doc_id = str(row.get("id", row.name))
        if doc_id in tagged:
            continue
        title = str(row.get("title", row.get("source", "")))
        domain = classify_by_filename(title)
        if domain:
            insert_domain(conn, doc_id, title, domain, "heuristic")
            heuristic_count += 1
        else:
            llm_queue.append({"id": doc_id, "title": title})

    conn.commit()
    logger.info(f"Pass 1 (heuristic): {heuristic_count} classified, {len(llm_queue)} remaining")

    # Pass 2: LLM batches
    if llm_queue and not (cfg and cfg.dry_run):
        token = get_access_token()
        batch_size = 20
        for i in range(0, len(llm_queue), batch_size):
            batch = llm_queue[i : i + batch_size]
            try:
                results = classify_batch_llm(batch, token)
                for r in results:
                    insert_domain(conn, r["id"], "", r["domain"], "llm")
            except Exception as e:
                logger.warning(f"LLM batch {i} failed: {e}, using fallback")
                for doc in batch:
                    insert_domain(conn, doc["id"], doc["title"], _fallback_classify(doc["title"]), "fallback")
            conn.commit()
            time.sleep(1)  # Rate limit

    conn.close()
    stats = {"heuristic": heuristic_count, "llm_queued": len(llm_queue)}
    logger.info(f"Domain Tagger complete: {stats}")
    return stats


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Domain Tagger — Step 1")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    from dataclasses import dataclass

    @dataclass
    class Cfg:
        dry_run: bool = False

    run_domain_tagger(Cfg(dry_run=args.dry_run))
