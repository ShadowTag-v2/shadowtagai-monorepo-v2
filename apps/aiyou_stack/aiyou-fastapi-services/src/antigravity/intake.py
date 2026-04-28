# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Gemini 3 Pro Intake - 2M Context Window

Atomizes input into discrete tasks with:
- Tests for each atom
- Risk level classification
- JURA tier assignment
- Pipeline/Drive/Memory/Web search BEFORE atomizing
"""

import json
import os
from dataclasses import dataclass, field

# Import from pipeline to avoid circular
from enum import Enum
from typing import Any

import google.generativeai as genai


class RiskLevel(Enum):
    LOW = "LOW"
    MED = "MED"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


class JuraTier(Enum):
    FREE = "FREE"
    FLASH = "FLASH"
    PRO = "PRO"


@dataclass
class Atom:
    """Atomic unit of work"""

    id: str
    content: str
    risk_level: RiskLevel
    jura_tier: JuraTier
    tests: list[str] = field(default_factory=list)
    reasoning_chain: list[str] = field(default_factory=list)


class GeminiIntake:
    """Gemini 3 Pro Intake Layer

    2M token context window for massive input processing.
    Atomizes complex tasks into discrete, testable units.
    """

    MODEL_NAME = "gemini-3-pro-preview"

    ATOMIZE_PROMPT = """You are Antigravity's intake processor. Your job is to:

1. SEARCH CONTEXT FIRST: Before atomizing, mentally search:
   - Pipeline: existing code patterns
   - Drive: related documents
   - Memory: previous chat context
   - Web: current best practices

2. ATOMIZE: Break this input into atomic, independent tasks.
   Each atom should be:
   - Self-contained
   - Testable
   - Risk-classified

3. WRITE TESTS: For each atom, write the test cases BEFORE the implementation.

4. CLASSIFY RISK:
   - LOW: Simple queries, documentation, minor changes
   - MED: Standard code, internal tools, non-prod
   - HIGH: Auth, payments, PII, security
   - EXTREME: Production infra, compliance, legal

5. ASSIGN JURA TIER:
   - FREE (30%): Simple, low risk, ~$0.001/req
   - FLASH (60%): Standard, medium risk, ~$0.01/req
   - PRO (10%): Complex, high risk, ~$0.10-1.00/req

INPUT:
{input}

OUTPUT JSON ARRAY:
[
  {
    "id": "atom_001",
    "content": "specific task description",
    "risk_level": "LOW|MED|HIGH|EXTREME",
    "jura_tier": "FREE|FLASH|PRO",
    "tests": ["test case 1", "test case 2"],
    "reasoning": "why this classification"
  }
]

Return ONLY valid JSON array, no markdown."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY required")
        genai.configure(api_key=self.api_key)

    async def decompose(self, input_text: str) -> list[Atom]:
        """Atomize input into discrete tasks using Gemini 3 Pro's 2M context."""
        # Alias for pipeline compatibility
        return await self._atomize_impl(input_text)

    async def atomize(self, input_text: str) -> list[Atom]:
        """Legacy alias for decompose."""
        return await self._atomize_impl(input_text)

    async def _atomize_impl(self, input_text: str) -> list[Atom]:
        """Core atomization logic."""
        prompt = self.ATOMIZE_PROMPT.format(input=input_text)

        try:
            model = genai.GenerativeModel(self.MODEL_NAME)
            response = await model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 8192,
                    "response_mime_type": "application/json",
                },
            )

            atoms_data = json.loads(response.text)

            return [
                Atom(
                    id=a.get("id", f"atom_{i:03d}"),
                    content=a["content"],
                    risk_level=RiskLevel[a.get("risk_level", "MED")],
                    jura_tier=JuraTier[a.get("jura_tier", "FLASH")],
                    tests=a.get("tests", []),
                    reasoning_chain=[a.get("reasoning", "")],
                )
                for i, a in enumerate(atoms_data)
            ]
        except (KeyError, json.JSONDecodeError, Exception):
            return [self._fallback_atom(input_text)]

    def _fallback_atom(self, input_text: str) -> Atom:
        """Create a single atom when parsing fails"""
        return Atom(
            id="atom_001",
            content=input_text,
            risk_level=RiskLevel.MED,
            jura_tier=JuraTier.FLASH,
            tests=[],
            reasoning_chain=["Fallback: single atom created"],
        )

    async def search_context(self, query: str) -> dict[str, Any]:
        """Search pipeline/drive/memory/web for context before atomizing.
        This runs BEFORE atomization to inform the breakdown.
        """
        # TODO: Implement full context search
        # For now, return empty context
        return {"pipeline": [], "drive": [], "memory": [], "web": []}
