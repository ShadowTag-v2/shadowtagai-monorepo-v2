"""Research Chain: Perplexity → SuperGrok

Each LLM explains reasoning to the next (REASONING HANDOFF pattern).
Research sources: all sources + X + Grokipedia.
Apply business acumen to each atom.
"""

import json
import os
from dataclasses import dataclass, field
from typing import Any

import httpx

from .intake import Atom


@dataclass
class ReasoningHandoff:
    """Handoff data between LLMs"""

    explain_reasoning: bool = True
    include_prior_chain: bool = True
    apply_biz_acumen: bool = True
    prior_reasoning: list[str] = field(default_factory=list)
    evidence_found: list[str] = field(default_factory=list)
    biz_insights: str = ""


class PerplexityClient:
    """Perplexity API client for research"""

    API_URL = "https://api.perplexity.ai/chat/completions"

    RESEARCH_PROMPT = """You are a research agent in the Antigravity pipeline.

TASK: Research all sources for context, upgrades, and best practices.

ATOM TO RESEARCH:
{atom_content}

PRIOR REASONING CHAIN:
{prior_reasoning}

INSTRUCTIONS:
1. Search all available sources for relevant information
2. Find any useful context or upgrade potential
3. Apply business acumen to evaluate practical value
4. Explain your reasoning clearly for the next agent

OUTPUT JSON:
{
    "findings": ["finding 1", "finding 2"],
    "evidence": ["source 1", "source 2"],
    "biz_acumen": "business insight",
    "reasoning": "explanation for next agent",
    "confidence": 0.0-1.0
}

Return ONLY valid JSON."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")

    async def research(self, atom: Atom, handoff: ReasoningHandoff) -> dict[str, Any]:
        """Research an atom using Perplexity"""
        if not self.api_key:
            return self._fallback_research(atom)

        prompt = self.RESEARCH_PROMPT.format(
            atom_content=atom.content,
            prior_reasoning="\n".join(handoff.prior_reasoning)
            if handoff.prior_reasoning
            else "None",
        )

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    self.API_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "llama-3.1-sonar-large-128k-online",
                        "messages": [{"role": "user", "content": prompt}],
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    text = data["choices"][0]["message"]["content"]
                    return json.loads(text)
            except Exception:
                pass

        return self._fallback_research(atom)

    def _fallback_research(self, atom: Atom) -> dict[str, Any]:
        return {
            "findings": [],
            "evidence": [],
            "biz_acumen": "No research available",
            "reasoning": f"Fallback for atom: {atom.id}",
            "confidence": 0.5,
        }


class SuperGrokClient:
    """SuperGrok/X API client for X and Grokipedia research"""

    # Note: Using X API endpoint - adjust as needed
    API_URL = "https://api.x.ai/v1/chat/completions"

    RESEARCH_PROMPT = """You are SuperGrok in the Antigravity pipeline.

TASK: Research X (Twitter) and Grokipedia for:
- Real-time tech updates
- Community best practices
- Emerging patterns
- Business insights

ATOM TO RESEARCH:
{atom_content}

ALL PRIOR REASONING (from Gemini and Perplexity):
{prior_reasoning}

PERPLEXITY FINDINGS:
{perplexity_findings}

INSTRUCTIONS:
1. Search X for real-time discussions and trends
2. Search Grokipedia for accumulated knowledge
3. Apply business acumen
4. Explain ALL prior reasoning plus your additions for Claude Code

OUTPUT JSON:
{
    "x_findings": ["from X"],
    "grokipedia_findings": ["from Grokipedia"],
    "biz_acumen": "business insight",
    "full_reasoning_chain": ["all reasoning from all agents"],
    "confidence": 0.0-1.0
}

Return ONLY valid JSON."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("GROK_API_KEY")

    async def research(
        self, atom: Atom, handoff: ReasoningHandoff, perplexity_findings: dict[str, Any],
    ) -> dict[str, Any]:
        """Research using SuperGrok (X + Grokipedia)"""
        if not self.api_key:
            return self._fallback_research(atom, handoff, perplexity_findings)

        prompt = self.RESEARCH_PROMPT.format(
            atom_content=atom.content,
            prior_reasoning="\n".join(handoff.prior_reasoning),
            perplexity_findings=json.dumps(perplexity_findings, indent=2),
        )

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    self.API_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "grok-2-latest",
                        "messages": [{"role": "user", "content": prompt}],
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    text = data["choices"][0]["message"]["content"]
                    return json.loads(text)
            except Exception:
                pass

        return self._fallback_research(atom, handoff, perplexity_findings)

    def _fallback_research(
        self, atom: Atom, handoff: ReasoningHandoff, perplexity_findings: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "x_findings": [],
            "grokipedia_findings": [],
            "biz_acumen": perplexity_findings.get("biz_acumen", ""),
            "full_reasoning_chain": handoff.prior_reasoning
            + [perplexity_findings.get("reasoning", "")],
            "confidence": 0.5,
        }


class ResearchChain:
    """Research Chain: Perplexity → SuperGrok

    Each LLM explains reasoning to the next.
    Full reasoning chain passed to Claude Code.
    """

    def __init__(self, perplexity_api_key: str | None = None, grok_api_key: str | None = None):
        self.perplexity = PerplexityClient(perplexity_api_key)
        self.grok = SuperGrokClient(grok_api_key)

    async def enrich(self, atoms: list[Atom]) -> list[Atom]:
        """Enrich atoms with research from Perplexity → SuperGrok.
        Returns atoms with updated reasoning chains.
        """
        enriched = []

        for atom in atoms:
            # Build handoff from atom's existing reasoning
            handoff = ReasoningHandoff(prior_reasoning=atom.reasoning_chain.copy())

            # Step 1: Perplexity research
            perplexity_result = await self.perplexity.research(atom, handoff)

            # Update handoff with Perplexity reasoning
            handoff.prior_reasoning.append(f"Perplexity: {perplexity_result.get('reasoning', '')}")
            handoff.evidence_found.extend(perplexity_result.get("evidence", []))

            # Step 2: SuperGrok research
            grok_result = await self.grok.research(atom, handoff, perplexity_result)

            # Build full reasoning chain
            full_chain = grok_result.get("full_reasoning_chain", [])
            if not full_chain:
                full_chain = handoff.prior_reasoning + [
                    f"SuperGrok X: {grok_result.get('x_findings', [])}",
                    f"SuperGrok Grokipedia: {grok_result.get('grokipedia_findings', [])}",
                    f"Biz Acumen: {grok_result.get('biz_acumen', '')}",
                ]

            # Create enriched atom
            enriched_atom = Atom(
                id=atom.id,
                content=atom.content,
                risk_level=atom.risk_level,
                jura_tier=atom.jura_tier,
                tests=atom.tests,
                reasoning_chain=full_chain,
            )
            enriched.append(enriched_atom)

        return enriched
