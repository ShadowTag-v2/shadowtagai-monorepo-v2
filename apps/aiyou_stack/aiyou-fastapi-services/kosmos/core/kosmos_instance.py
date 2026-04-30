"""Kosmos Instance - Autonomous AI Scientist per LLM
=================================================
Wraps an LLM + RSTA Squadron (380 agents) into a single Kosmos instance.
Each Kosmos operates autonomously with its own agents using ONLY its own LLM.

Based on: https://arxiv.org/pdf/2511.02824 (Kosmos AI Scientist)
Combined with: FM 3-21.31 RSTA Squadron doctrine

Key Features:
- Autonomous hypothesis generation
- Self-verification via RSTA consensus
- No logic bleed between LLM stages
- Dynamic security (replaces static allow/deny lists)
"""

import asyncio
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

import httpx

from agents.rsta_squadron import Agent, create_rsta_squadron

logger = logging.getLogger(__name__)


class KosmosType(StrEnum):
    """Types of Kosmos instances in the pipeline"""

    GEMINI_INTAKE = "gemini_intake"  # Stage 1: Gemini 2M context
    PERPLEXITY = "perplexity"  # Stage 2: Research
    SUPERGROK = "supergrok"  # Stage 3: X/Grokipedia research
    GEMINI_CODE_ASSIST = "gemini_code"  # Stage 4: 10× Code execution


@dataclass
class KosmosConfig:
    """Configuration for a Kosmos instance"""

    kosmos_type: KosmosType
    model_name: str
    api_url: str
    api_key_env: str  # Environment variable name for API key
    agents_per_instance: int = 380
    consensus_threshold: float = 0.75


# Default configurations for each Kosmos type
KOSMOS_CONFIGS = {
    KosmosType.GEMINI_INTAKE: KosmosConfig(
        kosmos_type=KosmosType.GEMINI_INTAKE,
        model_name="gemini-3.1-flash-lite-preview",
        api_url="https://generativelanguage.googleapis.com/v1beta/models",
        api_key_env="GEMINI_API_KEY",
    ),
    KosmosType.PERPLEXITY: KosmosConfig(
        kosmos_type=KosmosType.PERPLEXITY,
        model_name="llama-3.1-sonar-large-128k-online",
        api_url="https://api.perplexity.ai/chat/completions",
        api_key_env="PERPLEXITY_API_KEY",
    ),
    KosmosType.SUPERGROK: KosmosConfig(
        kosmos_type=KosmosType.SUPERGROK,
        model_name="grok-2-latest",
        api_url="https://api.x.ai/v1/chat/completions",
        api_key_env="GROK_API_KEY",
    ),
    KosmosType.GEMINI_CODE_ASSIST: KosmosConfig(
        kosmos_type=KosmosType.GEMINI_CODE_ASSIST,
        model_name="gemini-3.1-flash-lite-preview",
        api_url="https://generativelanguage.googleapis.com/v1beta/models",
        api_key_env="GEMINI_API_KEY",
    ),
}


class KosmosInstance:
    """Autonomous AI Scientist instance with embedded RSTA Squadron.

    Each Kosmos:
    - Has 380 agents (RSTA structure)
    - Uses ONLY its own LLM model (no cross-contamination)
    - Reaches consensus BEFORE passing to next stage
    - Replaces static allow/deny lists with dynamic security voting
    """

    def __init__(
        self,
        kosmos_type: KosmosType,
        config: KosmosConfig | None = None,
        instance_id: int = 1,
    ):
        """Initialize Kosmos instance.

        Args:
            kosmos_type: Type of Kosmos (GEMINI_INTAKE, PERPLEXITY, etc.)
            config: Optional custom config, defaults to KOSMOS_CONFIGS
            instance_id: Instance ID (1-10 for parallel Code Assist)

        """
        self.kosmos_type = kosmos_type
        self.config = config or KOSMOS_CONFIGS[kosmos_type]
        self.instance_id = instance_id
        self.created_at = datetime.utcnow()

        # Initialize RSTA Squadron with this LLM's model
        self.squadron = create_rsta_squadron(model=self.config.model_name)

        # Get API key (support multi-account for Code Assist)
        if kosmos_type == KosmosType.GEMINI_CODE_ASSIST:
            # Try GEMINI_KEY_1, GEMINI_KEY_2, etc. for multi-account
            self.api_key = os.getenv(f"GEMINI_KEY_{instance_id}") or os.getenv(
                self.config.api_key_env,
            )
        else:
            self.api_key = os.getenv(self.config.api_key_env)

        logger.info(
            f"Initialized Kosmos-{kosmos_type.value}#{instance_id} "
            f"with {self.squadron.get_status()['total_agents']} agents",
        )

    async def process(
        self,
        task: str,
        context: dict[str, Any] | None = None,
        risk_level: str = "MEDIUM",
    ) -> dict[str, Any]:
        """Process task through this Kosmos instance.

        Workflow:
        1. RECON: Explore solution options (180 agents)
        2. SURV: Monitor for errors (60 agents)
        3. S-2 INTEL: Gather intelligence (20 agents)
        4. MFRC: Security validation via consensus (60 agents)
        5. COMMAND: Final decision (10 agents)

        Args:
            task: Task to process
            context: Optional context from prior stages
            risk_level: LOW/MEDIUM/HIGH/EXTREME

        Returns:
            Result with consensus outcome and generated content

        """
        start_time = datetime.utcnow()

        # Execute with RSTA consensus
        consensus_result = await self.squadron.execute_with_consensus(
            task=task,
            execute_fn=self._execute_single_agent,
            threshold=self.config.consensus_threshold,
            risk_level=risk_level,
        )

        # If consensus reached, generate final output
        if consensus_result["consensus_reached"]:
            output = await self._generate_output(task, context)
        else:
            output = {
                "blocked": True,
                "reason": f"Consensus not reached ({consensus_result['consensus_percent']:.0%} < {consensus_result['threshold']:.0%})",
            }

        return {
            "kosmos_type": self.kosmos_type.value,
            "instance_id": self.instance_id,
            "task": task,
            "consensus": consensus_result,
            "output": output,
            "model": self.config.model_name,
            "agents_used": consensus_result["recon_count"]
            + consensus_result["surv_count"]
            + consensus_result["intel_count"],
            "duration_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
        }

    async def _execute_single_agent(self, agent: Agent, task: str) -> dict[str, Any]:
        """Execute task with a single agent (LLM call)"""
        # In production, this makes the actual LLM API call
        # For now, return simulated result
        return {
            "agent_id": agent.agent_id,
            "role": agent.role,
            "status": "complete",
            "result": f"Agent {agent.agent_id} processed task",
        }

    async def _generate_output(
        self,
        task: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate final output after consensus reached"""
        if not self.api_key:
            return {"error": f"No API key for {self.config.api_key_env}", "fallback": True}

        prompt = self._build_prompt(task, context)

        try:
            if self.kosmos_type in [KosmosType.GEMINI_INTAKE, KosmosType.GEMINI_CODE_ASSIST]:
                return await self._call_gemini(prompt)
            if self.kosmos_type == KosmosType.PERPLEXITY:
                return await self._call_perplexity(prompt)
            if self.kosmos_type == KosmosType.SUPERGROK:
                return await self._call_grok(prompt)
        except Exception as e:
            logger.error(f"Kosmos {self.kosmos_type.value} generation failed: {e}")
            return {"error": str(e), "fallback": True}

    def _build_prompt(self, task: str, context: dict[str, Any] | None = None) -> str:
        """Build prompt with context from prior stages"""
        prompt_parts = [f"Task: {task}"]

        if context:
            if "reasoning_chain" in context:
                prompt_parts.append("\n## Prior Reasoning Chain:")
                for reasoning in context["reasoning_chain"]:
                    prompt_parts.append(f"- {reasoning}")

            if "evidence" in context:
                prompt_parts.append("\n## Evidence Found:")
                for evidence in context["evidence"]:
                    prompt_parts.append(f"- {evidence}")

        return "\n".join(prompt_parts)

    async def _call_gemini(self, prompt: str) -> dict[str, Any]:
        """Call Gemini API"""
        url = f"{self.config.api_url}/{self.config.model_name}:generateContent?key={self.api_key}"

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                url,
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.2,
                        "maxOutputTokens": 8192,
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
                return {"text": text, "model": self.config.model_name}

            return {"error": f"API error: {response.status_code}", "body": response.text}

    async def _call_perplexity(self, prompt: str) -> dict[str, Any]:
        """Call Perplexity API"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                self.config.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.config.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )

            if response.status_code == 200:
                data = response.json()
                text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                return {"text": text, "model": self.config.model_name}

            return {"error": f"API error: {response.status_code}"}

    async def _call_grok(self, prompt: str) -> dict[str, Any]:
        """Call Grok/X.AI API"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                self.config.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.config.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )

            if response.status_code == 200:
                data = response.json()
                text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                return {"text": text, "model": self.config.model_name}

            return {"error": f"API error: {response.status_code}"}

    def get_status(self) -> dict[str, Any]:
        """Get Kosmos instance status"""
        squadron_status = self.squadron.get_status()

        return {
            "kosmos_type": self.kosmos_type.value,
            "instance_id": self.instance_id,
            "model": self.config.model_name,
            "agents": squadron_status["total_agents"],
            "ready_agents": squadron_status["ready_agents"],
            "readiness_percent": squadron_status["readiness_percent"],
            "uptime_seconds": (datetime.utcnow() - self.created_at).total_seconds(),
            "has_api_key": bool(self.api_key),
        }


class KosmosPool:
    """Pool of Kosmos instances for parallel execution.
    Used for 10× Gemini Code Assist stage.
    """

    def __init__(self, kosmos_type: KosmosType, pool_size: int = 10):
        self.kosmos_type = kosmos_type
        self.pool_size = pool_size
        self.instances: list[KosmosInstance] = []
        self.semaphore = asyncio.Semaphore(pool_size)

        # Create pool of instances
        for i in range(1, pool_size + 1):
            instance = KosmosInstance(kosmos_type, instance_id=i)
            self.instances.append(instance)

        logger.info(f"Created KosmosPool with {pool_size} instances ({kosmos_type.value})")

    async def process_batch(
        self,
        tasks: list[str],
        context: dict[str, Any] | None = None,
        risk_level: str = "MEDIUM",
    ) -> list[dict[str, Any]]:
        """Process multiple tasks in parallel across pool"""

        async def process_with_instance(task: str, instance: KosmosInstance):
            async with self.semaphore:
                return await instance.process(task, context, risk_level)

        # Distribute tasks across instances
        coroutines = []
        for i, task in enumerate(tasks):
            instance = self.instances[i % len(self.instances)]
            coroutines.append(process_with_instance(task, instance))

        return await asyncio.gather(*coroutines, return_exceptions=True)

    def get_status(self) -> dict[str, Any]:
        """Get pool status"""
        total_agents = sum(inst.squadron.get_status()["total_agents"] for inst in self.instances)

        return {
            "kosmos_type": self.kosmos_type.value,
            "pool_size": self.pool_size,
            "total_agents": total_agents,
            "instances": [inst.get_status() for inst in self.instances],
        }


# Factory functions
def create_kosmos(kosmos_type: KosmosType, instance_id: int = 1) -> KosmosInstance:
    """Create a single Kosmos instance"""
    return KosmosInstance(kosmos_type, instance_id=instance_id)


def create_kosmos_pool(kosmos_type: KosmosType, pool_size: int = 10) -> KosmosPool:
    """Create a pool of Kosmos instances"""
    return KosmosPool(kosmos_type, pool_size)
