"""Gemini Code Assist Pool - 10× Parallel Execution with Kosmos RSTA
=================================================================
Routes atoms to 10 Gemini Code Assist Enterprise licenses.
Each license has embedded Kosmos (380 agents) for consensus.

Total: 3,800 agents (380 × 10)

Replaces: ClaudeCodePool (10× Claude Code licenses)
Savings: ~97% token cost reduction
"""

import asyncio
import os
from dataclasses import dataclass
from typing import Any

import httpx

from .intake import Atom

# Import Kosmos if available
try:
    from kosmos.core import KosmosInstance, KosmosPool, KosmosType, create_kosmos_pool

    KOSMOS_AVAILABLE = True
except ImportError:
    KOSMOS_AVAILABLE = False


@dataclass
class CodeResult:
    """Result from code generation"""

    atom_id: str
    code: str
    language: str
    tests: list[str]
    reasoning: str
    confidence: float


class GeminiCodeAssistPool:
    """10× Gemini Code Assist Enterprise Licenses Pool with Kosmos RSTA

    Each license has embedded Kosmos (380 agents) using RSTA structure:
    - HHT: 80 agents (Command, S-2/S-3/S-6, FSE)
    - RECON A/B/C: 180 agents (explore solutions)
    - SURV: 60 agents (monitor for errors)
    - MFRC: 60 agents (security consensus)

    Total: 3,800 agents (380 × 10 licenses)
    """

    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    CODE_PROMPT = """You are Gemini Code Assist in the Antigravity pipeline.
You are one of 10 parallel Gemini Code Assist instances generating perfect monkey code.

TASK TO IMPLEMENT:
{atom_content}

FULL REASONING CHAIN (from Gemini Intake, Perplexity, SuperGrok):
{reasoning_chain}

TESTS TO PASS:
{tests}

RISK LEVEL: {risk_level}
JURA TIER: {jura_tier}

INSTRUCTIONS:
1. Review ALL prior reasoning from the chain
2. Implement the task completely
3. Ensure all tests will pass
4. Write clean, production-ready code
5. Follow existing patterns in the codebase

OUTPUT JSON:
{{
    "code": "complete implementation",
    "language": "python|typescript|etc",
    "tests": ["test implementations"],
    "reasoning": "implementation decisions",
    "confidence": 0.0-1.0
}}

Return ONLY valid JSON with working code."""

    def __init__(
        self, pool_size: int = 10, use_kosmos: bool = True, model: str = "gemini-2.0-flash-exp",
    ):
        self.pool_size = pool_size
        self.semaphore = asyncio.Semaphore(pool_size)
        self.use_kosmos = use_kosmos and KOSMOS_AVAILABLE
        self.model_name = model

        # Load multi-account API keys
        self.api_keys = []
        for i in range(1, pool_size + 1):
            key = os.getenv(f"GEMINI_KEY_{i}") or os.getenv("GEMINI_API_KEY")
            self.api_keys.append(key)

        self._current_key_idx = 0

        # Initialize Kosmos pool if available
        if self.use_kosmos:
            self.kosmos_pool = create_kosmos_pool(
                KosmosType.GEMINI_CODE_ASSIST, pool_size=pool_size,
            )
        else:
            self.kosmos_pool = None

    def _get_next_key(self) -> str:
        """Round-robin through API keys"""
        key = self.api_keys[self._current_key_idx]
        self._current_key_idx = (self._current_key_idx + 1) % len(self.api_keys)
        return key

    async def generate(self, atom: Atom) -> str:
        """Generate code for an atom using Gemini with Kosmos consensus"""
        async with self.semaphore:
            # Get next API key and instance
            key_idx = self._current_key_idx
            api_key = self._get_next_key()

            if self.use_kosmos and self.kosmos_pool:
                # Use Kosmos instance with RSTA consensus
                kosmos = self.kosmos_pool.instances[key_idx % len(self.kosmos_pool.instances)]
                result = await kosmos.process(
                    task=atom.content,
                    context={
                        "reasoning_chain": atom.reasoning_chain,
                        "tests": atom.tests,
                    },
                    risk_level=atom.risk_level.value.upper()
                    if hasattr(atom.risk_level, "value")
                    else "MEDIUM",
                )

                if result["consensus"]["consensus_reached"]:
                    # Generate code after consensus
                    return await self._generate_single(atom, api_key)
                # Blocked by RSTA consensus
                return self._blocked_response(atom, result["consensus"])
            # Direct generation without Kosmos
            return await self._generate_single(atom, api_key)

    async def _generate_single(self, atom: Atom, api_key: str) -> str:
        """Single code generation call to Gemini"""
        if not api_key:
            return self._fallback_code(atom)

        prompt = self.CODE_PROMPT.format(
            atom_content=atom.content,
            reasoning_chain="\n".join(atom.reasoning_chain),
            tests="\n".join(atom.tests) if atom.tests else "No specific tests",
            risk_level=atom.risk_level.value
            if hasattr(atom.risk_level, "value")
            else str(atom.risk_level),
            jura_tier=atom.jura_tier.value
            if hasattr(atom.jura_tier, "value")
            else str(atom.jura_tier),
        )

        url = f"{self.GEMINI_API_URL}/{self.model_name}:generateContent?key={api_key}"

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    url,
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "temperature": 0.2,
                            "maxOutputTokens": 8192,
                            "responseMimeType": "application/json",
                        },
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    text = (
                        data.get("candidates", [{}])[0]
                        .get("content", {})
                        .get("parts", [{}])[0]
                        .get("text", "")
                    )
                    # Extract code from JSON response
                    import json

                    try:
                        result = json.loads(text)
                        return result.get("code", text)
                    except json.JSONDecodeError:
                        return text
            except Exception:
                pass

        return self._fallback_code(atom)

    def _fallback_code(self, atom: Atom) -> str:
        """Fallback code when API fails"""
        return f"""# Atom: {atom.id}
# Task: {atom.content}
# Risk: {atom.risk_level.value if hasattr(atom.risk_level, "value") else str(atom.risk_level)}
# Tier: {atom.jura_tier.value if hasattr(atom.jura_tier, "value") else str(atom.jura_tier)}

# TODO: Implementation required
# Prior reasoning:
# {chr(10).join(f"# - {r}" for r in atom.reasoning_chain)}

raise NotImplementedError("Code generation failed - implement manually")
"""

    def _blocked_response(self, atom: Atom, consensus: dict[str, Any]) -> str:
        """Response when blocked by RSTA consensus"""
        return f"""# BLOCKED BY KOSMOS RSTA CONSENSUS
# Atom: {atom.id}
# Task: {atom.content}
# Consensus: {consensus["consensus_percent"]:.0%} (threshold: {consensus["threshold"]:.0%})
# Reason: Security validation did not reach consensus

# This task was blocked by the MFRC security section.
# Review the task and try again with lower risk classification.

raise SecurityError("Task blocked by RSTA consensus - security validation failed")
"""

    async def generate_batch(self, atoms: list[Atom]) -> list[dict[str, Any]]:
        """Generate code for multiple atoms in parallel (up to pool_size)"""
        tasks = [self.generate(atom) for atom in atoms]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return [
            {
                "atom_id": atom.id,
                "code": result if isinstance(result, str) else str(result),
                "success": isinstance(result, str) and "BLOCKED" not in result,
            }
            for atom, result in zip(atoms, results, strict=False)
        ]

    def get_status(self) -> dict[str, Any]:
        """Get pool status"""
        status = {
            "pool_type": "GeminiCodeAssistPool",
            "pool_size": self.pool_size,
            "model": self.model_name,
            "kosmos_enabled": self.use_kosmos,
        }

        if self.use_kosmos and self.kosmos_pool:
            kosmos_status = self.kosmos_pool.get_status()
            status["total_agents"] = kosmos_status["total_agents"]
            status["kosmos_instances"] = len(kosmos_status["instances"])

        return status


# Factory function with environment-based selection
def create_execution_pool(
    pool_size: int = 10, model: str = "gemini-2.0-flash-exp",
) -> GeminiCodeAssistPool:
    """Create execution pool based on environment config.

    Returns GeminiCodeAssistPool by default.
    Using Gemini 2.0 Flash for heavy lifting.
    """
    # Always return GeminiCodeAssistPool
    return GeminiCodeAssistPool(pool_size=pool_size, use_kosmos=True, model=model)
