"""
Step 5 — Synthesis Report

Feeds top-100 gaps to Gemini 2.0 Flash → ranked action queue JSON + Markdown report.

Output:
  data/intelligence_pipeline/reports/synthesis_YYYYMMDD.json
  data/intelligence_pipeline/reports/synthesis_YYYYMMDD.md
"""

import json
import logging
import os
import re
import sqlite3
from datetime import date
from pathlib import Path

import google.auth
import google.auth.transport.requests
import requests

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent.parent
DB_PATH = REPO_ROOT / "data" / "intelligence_pipeline" / "crossref.db"
REPORT_DIR = REPO_ROOT / "data" / "intelligence_pipeline" / "reports"

GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "shadowtag-omega-v4")
REGION = "us-central1"
MODEL = "gemini-3.1-flash-lite-preview"
ENDPOINT = (
    f"https://{REGION}-aiplatform.googleapis.com/v1/projects/{GCP_PROJECT_ID}/locations/{REGION}/publishers/google/models/{MODEL}:generateContent"
)


def get_access_token() -> str:
    """Get GCP access token via ADC."""
    creds, _ = google.auth.default()
    creds.refresh(google.auth.transport.requests.Request())
    return creds.token


def load_top_gaps(conn: sqlite3.Connection, top_n: int = 100) -> list[dict]:
    """Load top N gaps ordered by priority."""
    priority_order = {"high": 1, "medium": 2, "low": 3}
    rows = conn.execute(
        """SELECT gap_type, source_id, source_title, best_match_id,
                  best_similarity, domain, priority
           FROM gap_matrix
           WHERE status = 'open'
           ORDER BY CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END
           LIMIT ?""",
        (top_n,),
    ).fetchall()
    return [
        {
            "type": r[0],
            "source_id": r[1],
            "title": r[2],
            "match": r[3],
            "similarity": r[4],
            "domain": r[5],
            "priority": r[6],
        }
        for r in rows
    ]


def load_domain_distribution(conn: sqlite3.Connection) -> dict:
    """Load domain distribution stats."""
    rows = conn.execute("SELECT domain, COUNT(*) FROM doc_domains GROUP BY domain").fetchall()
    return {r[0]: r[1] for r in rows}


def load_high_confidence_examples(conn: sqlite3.Connection, limit: int = 10) -> list[dict]:
    """Load high-confidence match examples for context."""
    rows = conn.execute(
        """SELECT doc_id, code_path, similarity
           FROM doc_code_matches
           WHERE rank = 1 AND similarity > 0.8
           ORDER BY similarity DESC
           LIMIT ?""",
        (limit,),
    ).fetchall()
    return [{"doc": r[0], "code": r[1], "sim": r[2]} for r in rows]


def call_gemini(prompt: str, token: str) -> str:
    """Call Gemini Flash for synthesis."""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 4096},
    }
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.post(ENDPOINT, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    return resp.json()["candidates"][0]["content"]["parts"][0]["text"]


def _fallback_report(gaps: list[dict]) -> dict:
    """Generate a basic report without LLM when API fails."""
    actions = []
    for i, g in enumerate(gaps[:20]):
        actions.append(
            {
                "rank": i + 1,
                "action": f"Address {g['type']} gap: {g['title']}",
                "type": g["type"],
                "priority": g["priority"],
                "domain": g["domain"],
            }
        )
    return {"actions": actions, "summary": f"Fallback report: {len(gaps)} gaps found"}


def render_markdown(report: dict, domain_dist: dict) -> str:
    """Render report dict as markdown."""
    lines = ["# Intelligence Pipeline — Synthesis Report", ""]
    lines.append(f"**Generated:** {date.today().isoformat()}")
    lines.append("")

    # Domain distribution
    lines.append("## Domain Distribution")
    lines.append("")
    for domain, count in sorted(domain_dist.items(), key=lambda x: -x[1]):
        lines.append(f"- **{domain}**: {count}")
    lines.append("")

    # Action queue
    lines.append("## Action Queue")
    lines.append("")
    lines.append("| Rank | Action | Type | Priority | Domain |")
    lines.append("|------|--------|------|----------|--------|")
    for a in report.get("actions", []):
        lines.append(f"| {a['rank']} | {a['action']} | {a['type']} | {a['priority']} | {a['domain']} |")
    lines.append("")

    if "summary" in report:
        lines.append("## Summary")
        lines.append("")
        lines.append(report["summary"])

    return "\n".join(lines)


def run_synthesis_report(cfg=None) -> dict:
    """Execute Step 5: Synthesis Report."""
    logger.info("Synthesis Report — Step 5")

    conn = sqlite3.connect(str(DB_PATH))
    top_n = cfg.top_n if cfg else 50
    gaps = load_top_gaps(conn, top_n)
    domain_dist = load_domain_distribution(conn)
    examples = load_high_confidence_examples(conn)
    conn.close()

    logger.info(f"Loaded {len(gaps)} gaps, {len(examples)} high-confidence examples")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().strftime("%Y%m%d")

    try:
        token = get_access_token()
        prompt = (
            "You are a senior engineering lead reviewing a gap analysis.\n\n"
            f"Domain distribution: {json.dumps(domain_dist)}\n\n"
            f"Top gaps ({len(gaps)}):\n" + json.dumps(gaps[:30], indent=2) + "\n\nGenerate a ranked action queue as JSON: "
            '{"actions": [{"rank": N, "action": "...", "type": "A/B/C", '
            '"priority": "high/medium/low", "domain": "..."}], "summary": "..."}'
        )
        response = call_gemini(prompt, token)

        # Parse JSON from response
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            report = json.loads(match.group())
        else:
            report = _fallback_report(gaps)

    except Exception as e:
        logger.warning(f"Gemini synthesis failed: {e}, using fallback")
        report = _fallback_report(gaps)

    # Write JSON
    json_path = REPORT_DIR / f"synthesis_{today}.json"
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2)

    # Write Markdown
    md_path = REPORT_DIR / f"synthesis_{today}.md"
    md_content = render_markdown(report, domain_dist)
    with open(md_path, "w") as f:
        f.write(md_content)

    stats = {"gaps_analyzed": len(gaps), "actions": len(report.get("actions", []))}
    logger.info(f"Synthesis Report complete: {stats}")
    return stats


if __name__ == "__main__":
    run_synthesis_report()
