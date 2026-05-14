# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Knowledge Search Tool — GEAP Part 2.

Provides semantic search over the company knowledge base using LanceDB.
Falls back to keyword matching when LanceDB is unavailable.

Reference: GEAP Tutorial Series Part 2
Project: shadowtag-omega-v4
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

log = logging.getLogger(__name__)

# --- LanceDB Configuration ---

LANCE_DB_PATH = os.getenv(
    "LANCE_DB_PATH",
    str(Path(__file__).resolve().parents[4] / "data" / "lancedb"),
)
LANCE_TABLE_NAME = os.getenv("LANCE_TABLE_NAME", "knowledge_docs")


def _get_lance_table():
    """Attempt to connect to LanceDB and return the knowledge table."""
    try:
        import lancedb

        db = lancedb.connect(LANCE_DB_PATH)
        if LANCE_TABLE_NAME in db.list_tables():
            return db.open_table(LANCE_TABLE_NAME)
        log.warning(
            "LanceDB table '%s' not found at %s", LANCE_TABLE_NAME, LANCE_DB_PATH
        )
    except ImportError:
        log.debug("lancedb not installed, using keyword fallback")
    except Exception as e:
        log.debug("LanceDB unavailable: %s", e)
    return None


# --- Fallback Knowledge Base ---

_KNOWLEDGE_BASE = [
    {
        "title": "VPN Troubleshooting Guide",
        "content": (
            "If VPN connection drops frequently: "
            "1) Check your internet connection stability. "
            "2) Update the VPN client to the latest version. "
            "3) Try switching between TCP and UDP protocols. "
            "4) Verify your firewall isn't blocking VPN ports (443, 1194). "
            "5) Contact IT if issues persist after these steps."
        ),
        "category": "network",
        "tags": ["vpn", "network", "connectivity", "troubleshooting"],
    },
    {
        "title": "New Employee IT Onboarding Checklist",
        "content": (
            "Day 1 IT Setup: "
            "1) Collect laptop and peripherals from IT (Desk Setup Kit). "
            "2) Activate Okta SSO account using the welcome email. "
            "3) Install required software: Slack, Chrome, VS Code, 1Password. "
            "4) Connect to corporate WiFi 'ShadowTag-Secure'. "
            "5) Set up VPN for remote access. "
            "6) Complete security awareness training module. "
            "7) Join #it-support Slack channel for help."
        ),
        "category": "onboarding",
        "tags": ["onboarding", "new hire", "setup", "checklist"],
    },
    {
        "title": "Software Installation Policy",
        "content": (
            "All software must be approved before installation. "
            "Approved software can be self-installed from the Company App Store. "
            "Unapproved software requires a ticket with justification. "
            "Admin rights are NOT provided by default — request via IT ticket. "
            "Open-source software must be vetted by the Security team."
        ),
        "category": "policy",
        "tags": ["software", "installation", "policy", "security"],
    },
    {
        "title": "Printer Setup and Troubleshooting",
        "content": (
            "To add a network printer: "
            "1) Open System Preferences > Printers & Scanners. "
            "2) Click '+' and search for the printer by name. "
            "3) Floor printers: F1-PRINTER, F2-PRINTER, F3-PRINTER. "
            "Common issues: Clear paper jams, check toner levels, "
            "restart print spooler service if jobs are stuck."
        ),
        "category": "hardware",
        "tags": ["printer", "hardware", "setup", "troubleshooting"],
    },
    {
        "title": "Data Security and Classification Policy",
        "content": (
            "Data classification levels: "
            "PUBLIC — No restrictions. "
            "INTERNAL — Share within company only. "
            "CONFIDENTIAL — Need-to-know basis, encrypt at rest. "
            "PRIVILEGED — Legal privilege protected under Heppner standard. "
            "Never share CONFIDENTIAL or PRIVILEGED data via email without encryption. "
            "Use approved file sharing (Google Drive with restricted access)."
        ),
        "category": "security",
        "tags": ["security", "data", "classification", "policy", "privilege"],
    },
    {
        "title": "Password Policy",
        "content": (
            "Password requirements: "
            "Minimum 14 characters, mixed case, numbers, and symbols. "
            "Change every 90 days. No reuse of last 12 passwords. "
            "MFA required on all accounts (Okta Verify or hardware key). "
            "Never share passwords. Use 1Password for credential management. "
            "Report any suspected compromise immediately to security@shadowtag.ai."
        ),
        "category": "security",
        "tags": ["password", "security", "mfa", "policy"],
    },
    {
        "title": "Remote Work IT Guidelines",
        "content": (
            "Remote work requirements: "
            "1) Use company VPN for all work activities. "
            "2) Lock screen when stepping away (Ctrl+L or Cmd+Ctrl+Q). "
            "3) Use encrypted WiFi only — no public/open networks. "
            "4) Keep OS and software updated. "
            "5) Report lost/stolen devices to IT within 1 hour. "
            "6) Use headphones in public spaces for calls."
        ),
        "category": "policy",
        "tags": ["remote", "work from home", "security", "vpn"],
    },
]


def knowledge_search(query: str, max_results: int = 3) -> str:
    """Search the company IT knowledge base for relevant articles and guides.

    Args:
        query: Natural language search query (e.g., 'how to set up VPN').
        max_results: Maximum number of results to return (default 3).

    Returns:
        Relevant knowledge base articles matching the query.
    """
    query_lower = query.lower().strip()

    if not query_lower:
        return "Please provide a search query."

    # Try LanceDB semantic search first
    lance_table = _get_lance_table()
    if lance_table is not None:
        try:
            results = lance_table.search(query_lower).limit(max_results).to_list()
            if results:
                lines = [f"📚 Knowledge Base — {len(results)} result(s) for '{query}':"]
                for i, r in enumerate(results, 1):
                    title = r.get("title", r.get("source", "Untitled"))
                    content = r.get("content", r.get("text", ""))[:300]
                    score = r.get("_distance", "N/A")
                    lines.append(f"\n{i}. **{title}** (relevance: {score})")
                    lines.append(f"   {content}...")
                return "\n".join(lines)
        except Exception as e:
            log.debug("LanceDB search failed, falling back to keyword: %s", e)

    # Keyword fallback
    scored: list[tuple[float, dict]] = []
    query_terms = set(query_lower.split())

    for article in _KNOWLEDGE_BASE:
        score = 0.0
        title_lower = article["title"].lower()
        content_lower = article["content"].lower()
        tags = {t.lower() for t in article.get("tags", [])}

        for term in query_terms:
            if term in title_lower:
                score += 3.0
            if term in tags:
                score += 2.0
            if term in content_lower:
                score += 1.0

        if score > 0:
            scored.append((score, article))

    scored.sort(key=lambda x: -x[0])
    top = scored[:max_results]

    if not top:
        return (
            f"📚 No knowledge base articles found for '{query}'.\n"
            "Try different keywords or create a ticket for personalized help."
        )

    lines = [f"📚 Knowledge Base — {len(top)} result(s) for '{query}':"]
    for i, (score, article) in enumerate(top, 1):
        lines.append(f"\n{i}. **{article['title']}** [{article['category']}]")
        lines.append(f"   {article['content'][:200]}...")

    return "\n".join(lines)
