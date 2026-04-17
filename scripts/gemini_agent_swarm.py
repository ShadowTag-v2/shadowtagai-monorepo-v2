#!/usr/bin/env python3
"""
scripts/gemini_agent_swarm.py
Gemini Agent Swarm — replaces n-autoresearch/Kosmos/BioAgents with a Gemini-native multi-agent loop.

Architectural lineage:
  karpathy/autoresearch   →  agentic research loop: query → synthesize → re-query
  jimmc414/Kosmos         →  multimodal context assembly (text + code + docs)
  bio-xyz/BioAgents       →  specialised agent roles with explicit handoff protocol

All agents share a single Gemini Context Cache slab (Aegaeon Protocol).
Roles:
  research   — queries corpus (rag_evolve FTS5) + alphaXiv for supporting evidence
  synthesize — assembles multi-source findings into a grounded recommendation
  critique   — red-teams the recommendation for IDOR / logic flaws / copyright risk
  architect  — produces final structured improvement directive for Judge 6

Run:
  GEMINI_API_KEY=... python3 scripts/gemini_agent_swarm.py --query "..."
  GEMINI_API_KEY=... python3 scripts/gemini_agent_swarm.py --loop   # continuous
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core.aegaeon import SwarmRouter, SwarmTask, SwarmTier
from core.rag_evolve import search_corpus  # type: ignore[import]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("gemini_agent_swarm")

# ── Agent role prompts ──────────────────────────────────────────────────────

_RESEARCH_TMPL = """\
ROLE: Research Agent (autoresearch pattern)
TASK: Gather supporting evidence for the following query from the Antigravity corpus.

CORPUS HITS (LOCAL LANCEDB/FTS5):
{corpus_hits}

GITNEXUS AST MONOREPO GRAPH:
{ast_context}

QUERY: {query}

Output a JSON object with keys:
  "evidence": [list of 3-5 relevant findings with source names]
  "gaps": [list of knowledge gaps needing alphaXiv lookup]
"""

_SYNTHESIZE_TMPL = """\
ROLE: Synthesis Agent (Kosmos multimodal pattern)
TASK: Assemble the research evidence into a structured improvement directive.

QUERY: {query}
EVIDENCE: {evidence}

Output a JSON object with keys:
  "recommendation": "one-paragraph actionable improvement"
  "tech_stack_impact": ["list of affected components"]
  "financial_impact": "brief revenue / cost impact estimate"
  "risk": "low | medium | high"
"""

_CRITIQUE_TMPL = """\
ROLE: Critique Agent (red-team, BioAgents adversarial pattern)
TASK: Find flaws in this recommendation before it reaches production.
Check for: IDOR, logic flaws, copyright risk, security regressions, overclaims.

RECOMMENDATION: {recommendation}

Output a JSON object with keys:
  "verdict": "approve | revise | reject"
  "issues": [list of specific flaws found, empty if none]
  "copyright_risk": "clean | review_required | blocked"
"""

_ARCHITECT_TMPL = """\
ROLE: Cor — Principal AI Coding Architect (final directive)
TASK: Convert the approved recommendation into a structured Judge 6 directive.

RECOMMENDATION: {recommendation}
CRITIQUE VERDICT: {verdict}

Output a JSON object with keys:
  "directive": "final one-paragraph implementation instruction for Cor"
  "files_to_change": ["list of files"]
  "judge6_gate": "pass | warn | block"
  "summary": "≤ 140-char tweet-length summary"
"""


# ── Swarm pipeline ──────────────────────────────────────────────────────────


async def run_swarm(query: str) -> dict:
    router = SwarmRouter()

    # Phase 1 — Research (Fast Path): pull corpus hits
    hits = search_corpus(query, top_k=8)
    corpus_text = "\n".join(f"[{h.get('class', '?')}] {h.get('name', '?')}: {h.get('text', '')[:300]}" for h in hits)

    # Extract actual GitNexus localized structural intelligence
    import subprocess

    try:
        ast_result = subprocess.check_output(
            ["npx", "gitnexus", "query", query],
            cwd="apps/gitnexus",
            stderr=subprocess.DEVNULL,
            timeout=10,
        ).decode()
    except Exception:
        ast_result = "[AST Nexus: Local graph compilation unavailable or timed out.]"

    research_task = SwarmTask(
        "research",
        _RESEARCH_TMPL.format(query=query, corpus_hits=corpus_text or "(no hits)", ast_context=ast_result),
        tier=SwarmTier.FAST,
    )
    [research_result] = await router.dispatch([research_task])
    research_data = _safe_json(research_result.text)
    evidence_str = json.dumps(research_data.get("evidence", []), indent=2)

    # Phase 2 — Synthesize (Fast Path) + Critique (Heavy Lift): parallel
    synth_task = SwarmTask(
        "synthesize",
        _SYNTHESIZE_TMPL.format(query=query, evidence=evidence_str),
        tier=SwarmTier.FAST,
    )
    crit_task = SwarmTask(
        "critique_preliminary",
        _CRITIQUE_TMPL.format(recommendation=evidence_str),
        tier=SwarmTier.HEAVY,
    )
    synth_result, _ = await router.dispatch([synth_task, crit_task])
    synth_data = _safe_json(synth_result.text)
    recommendation = synth_data.get("recommendation", synth_result.text[:500])

    # Phase 3 — Final critique + architect directive: parallel
    final_crit_task = SwarmTask(
        "critique_final",
        _CRITIQUE_TMPL.format(recommendation=recommendation),
        tier=SwarmTier.HEAVY,
    )
    [crit_result] = await router.dispatch([final_crit_task])
    crit_data = _safe_json(crit_result.text)

    arch_task = SwarmTask(
        "architect",
        _ARCHITECT_TMPL.format(
            recommendation=recommendation,
            verdict=crit_data.get("verdict", "unknown"),
        ),
        tier=SwarmTier.HEAVY,
    )
    [arch_result] = await router.dispatch([arch_task])
    arch_data = _safe_json(arch_result.text)

    output = {
        "query": query,
        "research": research_data,
        "synthesis": synth_data,
        "critique": crit_data,
        "architect_directive": arch_data,
    }
    logger.info("Swarm complete. Judge6 gate: %s", arch_data.get("judge6_gate", "?"))
    return output


def _safe_json(text: str) -> dict:
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
    except json.JSONDecodeError:
        pass
    return {"raw": text}


async def _loop(query: str, interval: int) -> None:
    logger.info("Starting continuous swarm loop (interval=%ds)", interval)

    import subprocess
    import sys

    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    try:
        from omega_auto_dispatcher import dispatch_payload_by_id
    except ImportError:

        def dispatch_payload_by_id(pid: int) -> None:
            logger.debug("omega_auto_dispatcher unavailable; skipping payload %s", pid)

    while True:
        try:
            git_status = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=False,
            )
            if git_status.stdout.strip():
                logger.info("YOLO MODE: Swarm detected architectural drift. Firing Payload 4 (Boy Scout Sweep).")
                dispatch_payload_by_id(4)

            result = await run_swarm(query)
            directive = result.get("architect_directive", {}).get("summary", "")
            logger.info("Loop result: %s", directive)

            if directive and ("vector" in directive.lower() or "ingest" in directive.lower()):
                logger.info("YOLO MODE: Architecture blueprint requested ingest. Firing Payload 2 (Vector Sync).")
                dispatch_payload_by_id(2)

        except Exception as exc:
            logger.error("Swarm iteration failed: %s", exc)
        await asyncio.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gemini Agent Swarm")
    parser.add_argument("--query", default="improve Antigravity tech stack and biz plan alignment")
    parser.add_argument("--loop", action="store_true", help="Run continuously")
    parser.add_argument("--interval", type=int, default=3600, help="Loop interval in seconds")
    parser.add_argument("--out", help="Write JSON result to file")
    args = parser.parse_args()

    if args.loop:
        asyncio.run(_loop(args.query, args.interval))
    else:
        result = asyncio.run(run_swarm(args.query))
        output = json.dumps(result, indent=2)
        if args.out:
            Path(args.out).write_text(output)
            logger.info("Result written to %s", args.out)
        else:
            print(output)
