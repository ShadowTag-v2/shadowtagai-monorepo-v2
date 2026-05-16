#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
core/rag_evolve.py — Antigravity Corpus Intelligence Engine
------------------------------------------------------------
Runs business plans and tech stack docs against the 70K-extraction
ingested corpus to surface improvements, validate architecture, and
gate commits via Judge 6.

Modes
-----
  --gatekeeper    Judge 6 hook: checks staged diff against corpus, PASS/FAIL
  --evolve FILE   Evolve a single document (existing behaviour)
  --analyze       Bulk: all biz plans × full corpus → improvement report
  --loop          Daily delta: analyze, diff against last run, write delta

Copyright Protection
--------------------
Extractions from Anna's Archive (commercial books) → Gemini must
synthesize/paraphrase only. No verbatim quotation permitted.
Government/NIST/military/ISO sources → safe to cite directly.
The prompt enforces this contractually; output is also n-gram checked.

Usage
-----
  # One-time full analysis
  python3 core/rag_evolve.py --analyze

  # Daily loop (add to cron or launchd)
  python3 core/rag_evolve.py --loop

  # Judge 6 gate (called by scripts/judge6.sh automatically)
  python3 core/rag_evolve.py --gatekeeper
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from google import genai

# ── Configuration ────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).parent.parent

# All corpus databases — add new ingest DBs here as they come online
CORPUS_DBS: list[Path] = [
  REPO_ROOT / "data/drive_ingest/ingest.db",  # 74K — Google Drive docs/books
  REPO_ROOT / "data/web_ingest/ingest.db",  # 11K — web/PDF scrapes (82 whitepapers)
  REPO_ROOT
  / "data/alphaxiv/ingest.db",  # live — arXiv research via alphaXiv MCP (mcp SDK)
]

# Legacy single-DB alias kept for backward compat
DB_PATH = CORPUS_DBS[0]

INTEL_DIR = REPO_ROOT / "artifacts/corpus-intel"
DELTA_STATE = INTEL_DIR / ".last_run_hash.json"
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

# Biz plan / tech stack doc globs to include in --analyze / --loop
BIZPLAN_GLOBS = [
  "artifacts/workspace_archive/icloud_notes/*BUSINESS PLAN*/*.txt",
  "artifacts/workspace_archive/icloud_notes/*PNKLN*/*.txt",
  "artifacts/workspace_archive/icloud_notes/Wealth Planning/*.txt",
  "artifacts/workspace_archive/icloud_notes/*valuation*/*.txt",
  "artifacts/workspace_archive/icloud_notes/*Partnership*/*.txt",
  "docs/**/*.md",
  "AGENTS.md",
  "REVIEW.md",
]

# FTS5 query limit per thematic vector
FTS_TOP_K = int(os.environ.get("RAG_FTS_TOP_K", "8"))

# n-gram length for copyright verbatim check
NGRAM_LEN = 8
NGRAM_THRESHOLD = 0.15  # >15% matching n-grams triggers copyright warning

# ── Copyright Classification ─────────────────────────────────────────────────

# Sources safe to quote directly (public domain / government works)
_PUBLIC_DOMAIN_PATTERNS = re.compile(
  r"NIST|ATP_|ARN\d|HIPAA|PCI.DSS|IRS.Pub|IRC.\d|ISO_IEC|SSUG|"
  r"Open.Source.Initiative|auditing_standards|army\.mil",
  re.IGNORECASE,
)

# Sources requiring synthesis only (commercial books from Anna's Archive)
_COPYRIGHTED_PATTERN = re.compile(r"Annas.Archive", re.IGNORECASE)


def is_copyrighted(source_name: str) -> bool:
  """True if source requires synthesis-only (no verbatim quotation)."""
  if _COPYRIGHTED_PATTERN.search(source_name):
    return True
  if _PUBLIC_DOMAIN_PATTERNS.search(source_name):
    return False
  return True  # default-safe: assume copyrighted if unknown


def label_extraction(row: sqlite3.Row) -> dict[str, Any]:
  """Attach copyright label to a corpus row."""
  name = row["name"] or ""
  return {
    "class": row["class"],
    "name": name,
    "text": row["text"] or "",
    "copyrighted": is_copyrighted(name),
  }


# ── Corpus Search (FTS5) ──────────────────────────────────────────────────────


def _ensure_fts5(conn: sqlite3.Connection) -> bool:
  """Build FTS5 virtual table if the DB lacks one. Returns True if usable."""
  c = conn.cursor()
  c.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='extractions_fts'"
  )
  if c.fetchone():
    return True
  try:
    c.execute(
      "CREATE VIRTUAL TABLE extractions_fts USING fts5(text, name, class, content='extractions', content_rowid='id')"
    )
    c.execute("INSERT INTO extractions_fts(extractions_fts) VALUES('rebuild')")
    conn.commit()
    return True
  except sqlite3.Error as exc:
    print(f"[corpus] FTS5 build failed: {exc}", file=sys.stderr)
    return False


def _sanitize_fts5(query: str) -> str:
  """Strip FTS5 special syntax to prevent column-not-found errors on natural language queries."""
  import re

  # Remove colons (FTS5 uses col:term syntax), quotes, and boolean operators
  q = re.sub(r"[:\"\(\)\*\^]", " ", query)
  # Collapse runs of whitespace and strip
  return " ".join(q.split())


def _query_one_db(db_path: Path, query: str, top_k: int) -> list[dict[str, Any]]:
  """Query a single corpus DB via FTS5."""
  if not db_path.exists():
    return []
  try:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    if not _ensure_fts5(conn):
      conn.close()
      return []
    c = conn.cursor()
    fts_query = _sanitize_fts5(query)
    c.execute(
      "SELECT e.id, e.name, e.class, e.text "
      "FROM extractions_fts f "
      "JOIN extractions e ON f.rowid = e.id "
      "WHERE extractions_fts MATCH ? "
      "ORDER BY rank LIMIT ?",
      (fts_query, top_k),
    )
    rows = [label_extraction(r) for r in c.fetchall()]
    conn.close()
    return rows
  except sqlite3.Error as exc:
    print(f"[corpus] {db_path.name}: {exc}", file=sys.stderr)
    return []


def search_corpus(query: str, top_k: int = FTS_TOP_K) -> list[dict[str, Any]]:
  """Query all CORPUS_DBS via FTS5, merge results, deduplicate by text hash."""
  seen: set[str] = set()
  results: list[dict[str, Any]] = []
  per_db = max(top_k, top_k // len(CORPUS_DBS) + 1)
  for db_path in CORPUS_DBS:
    for row in _query_one_db(db_path, query, per_db):
      key = (row["name"], row["text"][:80])
      if key not in seen:
        seen.add(key)
        results.append(row)
  return results[: top_k * 2]  # return more hits for better synthesis


def format_context(extractions: list[dict]) -> str:
  """Render extractions into prompt context with copyright labels."""
  if not extractions:
    return "(no corpus hits)"
  lines = []
  for e in extractions:
    tag = (
      "[SYNTH-ONLY — do not quote]" if e["copyrighted"] else "[PUBLIC DOMAIN — citable]"
    )
    lines.append(f"• [{e['class']}] {e['name']} {tag}\n  {e['text'][:300]}")
  return "\n".join(lines)


# ── Gemini Client ─────────────────────────────────────────────────────────────


def get_client() -> genai.Client:
  api_key = os.environ.get("GEMINI_API_KEY")
  if not api_key:
    print("Error: GEMINI_API_KEY not set.", file=sys.stderr)
    sys.exit(1)
  return genai.Client(api_key=api_key)


def call_gemini(client: genai.Client, prompt: str) -> str:
  resp = client.models.generate_content(model=MODEL, contents=prompt)
  return resp.text or ""


# ── Copyright N-gram Check ───────────────────────────────────────────────────


def make_ngrams(text: str, n: int = NGRAM_LEN) -> set[str]:
  words = re.findall(r"\w+", text.lower())
  return {" ".join(words[i : i + n]) for i in range(len(words) - n + 1)}


def check_copyright_verbatim(output: str, extractions: list[dict]) -> list[str]:
  """Return list of copyright warnings for verbatim n-gram matches."""
  out_ngrams = make_ngrams(output)
  warnings = []
  for e in extractions:
    if not e["copyrighted"]:
      continue
    src_ngrams = make_ngrams(e["text"])
    overlap = out_ngrams & src_ngrams
    if src_ngrams and len(overlap) / len(src_ngrams) > NGRAM_THRESHOLD:
      warnings.append(
        f"Verbatim overlap with copyrighted source: {e['name']} ({len(overlap)} n-gram matches)"
      )
  return warnings


# ── Document Discovery ────────────────────────────────────────────────────────


def find_bizplan_docs() -> list[Path]:
  """Discover all biz plan and tech stack docs matching BIZPLAN_GLOBS."""
  found: list[Path] = []
  for pattern in BIZPLAN_GLOBS:
    found.extend(REPO_ROOT.glob(pattern))
  # Deduplicate, exclude binary/image files
  seen: set[Path] = set()
  out: list[Path] = []
  for p in found:
    if p in seen or not p.is_file():
      continue
    if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".avif", ".webp", ".ico"}:
      continue
    seen.add(p)
    out.append(p)
  return sorted(out)


# ── Document Evolve (single file) ────────────────────────────────────────────

_CLEAN_ROOM_DIRECTIVE = """
CLEAN ROOM COPYRIGHT DIRECTIVE (non-negotiable):
- For any extraction marked [SYNTH-ONLY — do not quote]: you MUST
  synthesize the concept into your own words. NEVER reproduce more
  than 6 consecutive words from those sources.
- For extractions marked [PUBLIC DOMAIN — citable]: you may quote
  briefly with attribution (Author/Title).
- Violation = commit blocked by Judge-6 n-gram parity check.
"""


def _extract_queries(client: genai.Client, content: str) -> list[str]:
  prompt = (
    "Extract exactly 3 thematic FTS5 search queries (5–7 words each) "
    "that would retrieve the most relevant strategic, financial, or "
    "technical data for improving this document.\n"
    "Output ONLY the 3 queries, one per line, no bullets.\n\n"
    f"{content[:4000]}"
  )
  raw = call_gemini(client, prompt)
  return [q.strip(" -*0123456789.") for q in raw.splitlines() if q.strip()][:3]


def _synthesize_improvements(
  client: genai.Client,
  content: str,
  context: str,
  doc_label: str,
) -> str:
  prompt = f"""
You are the Antigravity Corpus Intelligence Engine.

{_CLEAN_ROOM_DIRECTIVE}

TASK: Identify 5–8 specific, actionable improvements to the document
below. For each improvement:
1. State the gap or opportunity (1 sentence)
2. Cite the supporting corpus evidence (source name + concept)
3. Give a concrete action step

CORPUS CONTEXT:
{context}

DOCUMENT ({doc_label}):
{content[:6000]}

Output as Markdown with ## headers per improvement. Be specific.
Improvements must be grounded in the corpus, not generic advice.
"""
  return call_gemini(client, prompt)


def evolve_document(filepath: str, overwrite: bool = False) -> None:
  """Evolve a single document using corpus context."""
  path = Path(filepath)
  if not path.exists():
    print(f"File not found: {filepath}")
    return

  content = path.read_text(encoding="utf-8", errors="replace")
  client = get_client()

  print(f"[{path.name}] Pass 1: extracting thematic queries...")
  queries = _extract_queries(client, content)

  print(f"[{path.name}] Pass 2: FTS5 corpus retrieval ({queries})...")
  extractions: list[dict] = []
  for q in queries:
    extractions.extend(search_corpus(q))

  context = format_context(extractions)

  print(f"[{path.name}] Pass 3: synthesizing improvements...")
  result = _synthesize_improvements(client, content, context, path.name)

  warnings = check_copyright_verbatim(result, extractions)
  if warnings:
    print("[copyright] WARNINGS:", file=sys.stderr)
    for w in warnings:
      print(f"  ⚠ {w}", file=sys.stderr)
    print("[copyright] Blocking output — rerun with stricter model.", file=sys.stderr)
    sys.exit(1)

  out_path = path if overwrite else path.with_stem(path.stem + "_evolved")
  out_path.write_text(result, encoding="utf-8")
  print(f"[{path.name}] Done → {out_path}")


# ── Analyze Mode (bulk all plans) ────────────────────────────────────────────


def run_analyze() -> str:
  """Bulk: all biz plan docs × corpus → single improvement report."""
  docs = find_bizplan_docs()
  if not docs:
    return "No biz plan documents found matching configured globs."

  client = get_client()
  INTEL_DIR.mkdir(parents=True, exist_ok=True)

  sections: list[str] = []
  ts = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
  sections.append(f"# Corpus Intelligence Report\n_Generated: {ts}_\n")
  sections.append(f"**Documents analyzed:** {len(docs)}  \n**Corpus:** {DB_PATH}\n")

  for doc in docs:
    rel = doc.relative_to(REPO_ROOT)
    print(f"  → {rel}")
    content = doc.read_text(encoding="utf-8", errors="replace")
    if len(content.strip()) < 100:
      continue

    queries = _extract_queries(client, content)
    extractions: list[dict] = []
    for q in queries:
      extractions.extend(search_corpus(q))

    context = format_context(extractions)
    improvements = _synthesize_improvements(client, content, context, str(rel))

    warnings = check_copyright_verbatim(improvements, extractions)
    if warnings:
      improvements += "\n\n> ⚠ **Copyright warnings** (auto-flagged):\n"
      improvements += "\n".join(f"> - {w}" for w in warnings)

    sections.append(f"\n---\n## {rel}\n\n{improvements}")

  report = "\n".join(sections)

  ts_file = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
  report_path = INTEL_DIR / f"corpus-intel-{ts_file}.md"
  report_path.write_text(report, encoding="utf-8")
  print(f"\n[analyze] Report written → {report_path}")
  return report


# ── Delta State (loop) ────────────────────────────────────────────────────────


def _hash_report(text: str) -> str:
  import hashlib

  return hashlib.sha256(text.encode()).hexdigest()[:16]


def _load_delta_state() -> dict:
  if DELTA_STATE.exists():
    return json.loads(DELTA_STATE.read_text())
  return {}


def _save_delta_state(data: dict) -> None:
  INTEL_DIR.mkdir(parents=True, exist_ok=True)
  DELTA_STATE.write_text(json.dumps(data, indent=2))


def _compute_delta(client: genai.Client, prev: str, curr: str) -> str:
  if not prev:
    return "_First run — no delta available._"
  prompt = f"""
Compare these two Corpus Intelligence Reports and summarize NEW
improvements or changed recommendations only. Ignore anything
identical between them. Output as a concise bullet list.

PREVIOUS REPORT (truncated):
{prev[:3000]}

CURRENT REPORT (truncated):
{curr[:3000]}
"""
  return call_gemini(client, prompt)


# ── Loop Mode ─────────────────────────────────────────────────────────────────


def run_loop() -> None:
  """Daily delta: run full analyze, diff against last run, commit delta."""
  state = _load_delta_state()
  prev_text = state.get("last_report_text", "")

  print("[loop] Running full corpus analysis...")
  curr_report = run_analyze()

  curr_hash = _hash_report(curr_report)
  prev_hash = state.get("last_hash", "")

  if curr_hash == prev_hash:
    print("[loop] No changes detected since last run. Exiting.")
    return

  client = get_client()
  print("[loop] Computing delta against previous run...")
  delta = _compute_delta(client, prev_text, curr_report)

  ts = datetime.now(UTC).strftime("%Y-%m-%d")
  delta_path = INTEL_DIR / f"delta-{ts}.md"
  delta_path.write_text(
    f"# Corpus Intelligence Delta — {ts}\n\n{delta}\n",
    encoding="utf-8",
  )
  print(f"[loop] Delta written → {delta_path}")

  _save_delta_state({"last_hash": curr_hash, "last_report_text": curr_report[:8000]})


# ── Gatekeeper Mode (Judge 6) ─────────────────────────────────────────────────


def _classify_changed_docs(diff: str) -> list[str]:
  """Extract file paths touched in diff that match biz/tech doc patterns."""
  paths = re.findall(r"^(?:\+\+\+|---) [ab]/(.+)$", diff, re.MULTILINE)
  patterns = re.compile(
    r"(\.md$|bizplan|PNKLN|AGENTS|REVIEW|icloud_notes|docs/|"
    r"legaltrack|cosmic-crab|uphillsnowball)",
    re.IGNORECASE,
  )
  return list({p for p in paths if patterns.search(p)})


def run_gatekeeper() -> bool:
  """Judge 6 integration: gate the commit, return True=PASS."""
  diff_proc = subprocess.run(["git", "diff", "HEAD"], capture_output=True, text=True)
  diff = diff_proc.stdout

  if not diff.strip():
    print("[gatekeeper] No staged diff. PASS.")
    return True

  changed_docs = _classify_changed_docs(diff)
  client = get_client()

  # Pass 1: extract tech changes
  tech_prompt = (
    "Extract the top 3 specific technologies or architectural decisions "
    "changed in this git diff. Output ONLY the tech names, one per line.\n\n"
    f"{diff[:3000]}"
  )
  techs_raw = call_gemini(client, tech_prompt)
  techs = [t.strip("- *0123456789.") for t in techs_raw.splitlines() if t.strip()][:3]

  # Pass 2: FTS5 corpus for each tech
  context_parts: list[str] = []
  all_extractions: list[dict] = []
  for tech in techs:
    hits = search_corpus(f"{tech} vulnerabilities security anti-patterns", top_k=4)
    all_extractions.extend(hits)
    context_parts.append(f"=== {tech} ===\n{format_context(hits)}")
  context = "\n".join(context_parts) or "(no corpus hits)"

  # Pass 3: copyright check on the diff itself
  copyright_warnings = check_copyright_verbatim(diff, all_extractions)

  # Pass 4: security + architecture verdict
  verdict_prompt = f"""
You are JUDGE-6, Antigravity's infallible security and architecture gatekeeper.

{_CLEAN_ROOM_DIRECTIVE}

PROPOSED DIFF (excerpt):
{diff[:2000]}

CHANGED DOC PATHS: {changed_docs}

CORPUS CONTEXT (NIST/DoD/NVIDIA knowledge):
{context}

TASK: If the diff introduces a fundamentally insecure vector, an
explicitly documented anti-pattern, or verbatim copyrighted text, output
'BLOCKED: <1-sentence reason>'. Otherwise output 'APPROVED'.
"""
  verdict_raw = call_gemini(client, verdict_prompt)
  print(f"[gatekeeper] Judge-6 RAG verdict:\n{verdict_raw}")

  if copyright_warnings:
    print("[gatekeeper] COPYRIGHT VIOLATIONS DETECTED:", file=sys.stderr)
    for w in copyright_warnings:
      print(f"  ✗ {w}", file=sys.stderr)
    return False

  return "APPROVED" in verdict_raw.upper()


# ── Post-Ingest Trigger ───────────────────────────────────────────────────────


def run_post_ingest(source_label: str) -> None:
  """
  Called by any ingest daemon after writing new rows to a corpus DB.
  Fires --loop if new content was added since last delta state.

  Usage in daemon scripts:
      import subprocess, sys
      subprocess.run(
          [sys.executable, "core/rag_evolve.py", "--post-ingest", "drive"],
          cwd=REPO_ROOT
      )
  """
  state = _load_delta_state()
  last_counts = state.get("corpus_counts", {})

  current_counts: dict[str, int] = {}
  for db_path in CORPUS_DBS:
    if not db_path.exists():
      continue
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM extractions")
    current_counts[str(db_path)] = c.fetchone()[0]
    conn.close()

  new_rows = sum(
    current_counts.get(k, 0) - last_counts.get(k, 0) for k in current_counts
  )

  print(f"[post-ingest:{source_label}] {new_rows} new extractions since last loop.")
  if new_rows <= 0:
    print("[post-ingest] No new rows. Skipping loop.")
    return

  # Persist updated counts before running loop
  state["corpus_counts"] = current_counts
  _save_delta_state(state)
  print(f"[post-ingest] Triggering --loop ({new_rows} new rows)...")
  run_loop()


# ── Entrypoint ────────────────────────────────────────────────────────────────


def main() -> None:
  parser = argparse.ArgumentParser(
    description="Antigravity Corpus Intelligence Engine",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=__doc__,
  )
  parser.add_argument(
    "--gatekeeper", action="store_true", help="Judge 6 gate on git diff"
  )
  parser.add_argument(
    "--analyze", action="store_true", help="Bulk biz plan x corpus analysis"
  )
  parser.add_argument("--loop", action="store_true", help="Daily delta loop mode")
  parser.add_argument(
    "--post-ingest", metavar="SOURCE", help="Post-ingest trigger (drive|web|downloads)"
  )
  parser.add_argument(
    "--evolve", type=str, metavar="FILE", help="Evolve a single document"
  )
  parser.add_argument(
    "--overwrite", action="store_true", help="Overwrite instead of _evolved suffix"
  )
  args = parser.parse_args()

  if args.gatekeeper:
    sys.exit(0 if run_gatekeeper() else 1)
  elif args.analyze:
    run_analyze()
  elif args.loop:
    run_loop()
  elif args.post_ingest:
    run_post_ingest(args.post_ingest)
  elif args.evolve:
    evolve_document(args.evolve, args.overwrite)
  else:
    parser.print_help()


if __name__ == "__main__":
  main()
