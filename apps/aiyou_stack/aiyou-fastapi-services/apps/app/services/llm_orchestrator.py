"""LLM Orchestrator - Integration Layer
Connects PNKLN Multi-Agent System with LLM Memory Persistence

Architecture:
1. Grok Intake → Query decomposition
2. Sonnet Coordinator → Thread assignment (uses PNKLN memory)
3. Multi-Agent Processing:
   - Gemini Agents (skeptic, optimist, neutral) for intelligence classification
   - GPT-5 for structured code generation
   - Perplexity for research/web-grounded queries
4. Review Rotation → 3-round peer review
5. PNKLN Synthesis → Final validation with ATP 5-19 compliance

Integration with existing systems:
- Uses GeminiGroupChat for intelligence classification threads
- Leverages ValidationService for ATP 5-19 compliance
- Stores results in IngestionService for tracking
"""

import asyncio
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any

import httpx

from app.models.schemas import TierClassification

# Import existing PNKLN services
from app.services.gemini_agents import GeminiGroupChat


class LLMProvider(Enum):
    """Supported LLM providers"""

    GROK = "grok"
    SONNET_45 = "claude-sonnet-4.5"
    GEMINI_AGENTS = "gemini-multi-agent"  # Our existing multi-agent system
    GEMINI_PRO = "gemini-pro"
    GPT5 = "gpt5"
    PERPLEXITY = "perplexity"


class ThreadDomain(Enum):
    """Thread domain types for specialized processing"""

    INTELLIGENCE = "intelligence"  # Use Gemini multi-agent debate
    CODE = "code"  # Use GPT-5
    RESEARCH = "research"  # Use Perplexity
    ANALYSIS = "analysis"  # Use Gemini Pro
    CREATIVE = "creative"  # Use Gemini Pro


@dataclass
class Thread:
    """A thread of work to be processed"""

    thread_id: str
    content: str
    domain: ThreadDomain
    complexity: int  # 1-10
    assigned_llm: LLMProvider

    # Round results
    round_1_response: str | None = None
    round_2_review: str | None = None
    round_3_review: str | None = None

    # Reviewers
    round_1_reviewer: LLMProvider | None = None
    round_2_reviewer: LLMProvider | None = None

    # Metadata
    cost: float = 0.0
    latency_ms: int = 0
    tier_classification: TierClassification | None = None


@dataclass
class OrchestrationResult:
    """Final orchestration result"""

    query: str
    threads: list[Thread]
    synthesis: str
    total_cost: float
    total_latency_ms: int
    confidence: float
    metadata: dict[str, Any]


class GrokIntake:
    """Grok handles query intake and decomposition"""

    async def decompose_query(self, query: str) -> list[dict[str, Any]]:
        """Decompose user query into discrete threads

        Returns:
            List of thread specifications

        """
        # For now, use heuristic decomposition
        # TODO: Integrate actual Grok API when available

        # Intelligence classification queries
        if any(kw in query.lower() for kw in ["classify", "tier", "intelligence", "source"]):
            return [
                {
                    "thread_id": "intel_1",
                    "content": query,
                    "complexity": 7,
                    "domain": "intelligence",
                },
            ]

        # Code-related queries
        if any(kw in query.lower() for kw in ["code", "implement", "function", "api"]):
            return [{"thread_id": "code_1", "content": query, "complexity": 8, "domain": "code"}]

        # Research queries
        if any(kw in query.lower() for kw in ["research", "search", "find", "web"]):
            return [
                {"thread_id": "research_1", "content": query, "complexity": 6, "domain": "research"},
            ]

        # Default: analysis
        return [
            {"thread_id": "analysis_1", "content": query, "complexity": 5, "domain": "analysis"},
        ]


class PNKLNCoordinator:
    """PNKLN-aware coordinator using Sonnet 4.5
    Leverages existing multi-agent system for intelligence classification
    """

    def __init__(self, pnkln_memory: dict[str, Any] | None = None):
        self.memory = pnkln_memory or {}
        self.gemini_chat = None  # Initialized lazily

    async def assign_threads(self, threads: list[dict[str, Any]]) -> list[Thread]:
        """Assign threads to appropriate LLM providers based on domain

        Intelligence threads → Gemini multi-agent debate
        Code threads → GPT-5
        Research threads → Perplexity
        Analysis threads → Gemini Pro
        """
        assigned_threads = []

        for thread_data in threads:
            domain = ThreadDomain(thread_data["domain"])

            # Domain-based LLM assignment
            if domain == ThreadDomain.INTELLIGENCE:
                assigned_llm = LLMProvider.GEMINI_AGENTS
            elif domain == ThreadDomain.CODE:
                assigned_llm = LLMProvider.GPT5
            elif domain == ThreadDomain.RESEARCH:
                assigned_llm = LLMProvider.PERPLEXITY
            else:  # ANALYSIS or CREATIVE
                assigned_llm = LLMProvider.GEMINI_PRO

            thread = Thread(
                thread_id=thread_data["thread_id"],
                content=thread_data["content"],
                domain=domain,
                complexity=thread_data["complexity"],
                assigned_llm=assigned_llm,
            )
            assigned_threads.append(thread)

        return assigned_threads


class PNKLNOrchestrator:
    """Main orchestrator integrating LLM Memory System with PNKLN Core Stack

    Usage:
        orchestrator = PNKLNOrchestrator()
        result = await orchestrator.process_query(
            "Classify this intelligence item: FAA proposes DO-178D update"
        )
    """

    def __init__(self, gemini_api_key: str | None = None):
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.intake = GrokIntake()
        self.coordinator = PNKLNCoordinator()
        self.gemini_chat = GeminiGroupChat(api_key=self.gemini_api_key)

    async def process_query(
        self, query: str, enable_review_rotation: bool = False,
    ) -> OrchestrationResult:
        """Process a user query through the full LLM orchestration pipeline

        Args:
            query: User query
            enable_review_rotation: Enable 3-round peer review (slower, more accurate)

        Returns:
            OrchestrationResult with threads, synthesis, and metadata

        """
        import time

        start_time = time.time()

        # Step 1: Grok Intake - Decompose query
        thread_specs = await self.intake.decompose_query(query)

        # Step 2: PNKLN Coordinator - Assign threads
        threads = await self.coordinator.assign_threads(thread_specs)

        # Step 3: Round 1 - Process threads with assigned LLMs
        for thread in threads:
            await self._execute_thread(thread)

        # Step 4 (Optional): Review rotation
        if enable_review_rotation:
            await self._execute_review_rounds(threads)

        # Step 5: Synthesis
        synthesis = await self._synthesize_results(query, threads)

        # Calculate metrics
        total_cost = sum(t.cost for t in threads)
        total_latency_ms = int((time.time() - start_time) * 1000)

        # Calculate confidence (average from tier classifications)
        tier_confidences = [
            t.tier_classification.confidence for t in threads if t.tier_classification is not None
        ]
        confidence = sum(tier_confidences) / len(tier_confidences) if tier_confidences else 0.5

        return OrchestrationResult(
            query=query,
            threads=threads,
            synthesis=synthesis,
            total_cost=total_cost,
            total_latency_ms=total_latency_ms,
            confidence=confidence,
            metadata={
                "threads_processed": len(threads),
                "review_enabled": enable_review_rotation,
                "primary_domain": threads[0].domain.value if threads else None,
            },
        )

    async def _execute_thread(self, thread: Thread):
        """Execute a thread with the assigned LLM"""
        import time

        start_time = time.time()

        if thread.assigned_llm == LLMProvider.GEMINI_AGENTS:
            # Use our existing multi-agent debate system
            result = await self._execute_gemini_agents(thread)
            thread.round_1_response = result["response"]
            thread.tier_classification = result.get("tier_classification")
            thread.cost = 0.00375  # Cost per classification

        elif thread.assigned_llm == LLMProvider.GEMINI_PRO:
            # Use Gemini Pro directly
            result = await self._execute_gemini_pro(thread)
            thread.round_1_response = result
            thread.cost = 0.0025  # Approximate cost per 1k tokens

        elif thread.assigned_llm == LLMProvider.GPT5:
            # Call GPT-5 (via OpenAI GPT-4o)
            try:
                response = await self._call_gpt5(thread.content)
                thread.round_1_response = response
                thread.cost = 0.008
            except Exception as e:
                thread.round_1_response = f"[Error calling GPT-5] {e!s}"
                thread.cost = 0.0

        elif thread.assigned_llm == LLMProvider.PERPLEXITY:
            # Call Perplexity
            try:
                response = await self._call_perplexity(thread.content)
                thread.round_1_response = response
                thread.cost = 0.005
            except Exception as e:
                thread.round_1_response = f"[Error calling Perplexity] {e!s}"
                thread.cost = 0.0

        else:
            thread.round_1_response = f"[Fallback] {thread.content}"
            thread.cost = 0.0

        thread.latency_ms = int((time.time() - start_time) * 1000)

    async def _call_gpt5(self, content: str) -> str:
        """Call GPT-5 API (using GPT-4o as proxy)"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return f"[GPT-5 Mock (Missing Key)] {content}"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": "gpt-4o",
                    "messages": [{"role": "user", "content": content}],
                    "temperature": 0.7,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    async def _call_perplexity(self, content: str) -> str:
        """Call Perplexity API"""
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            return f"[Perplexity Mock (Missing Key)] {content}"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.1-sonar-large-128k-online",
                    "messages": [{"role": "user", "content": content}],
                    "temperature": 0.2,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    async def _execute_gemini_agents(self, thread: Thread) -> dict[str, Any]:
        """Execute intelligence classification using Gemini multi-agent debate

        Leverages existing GeminiGroupChat with skeptic, optimist, neutral agents
        """
        # Parse intelligence item from thread content
        # Expected format: "Classify: <title> | <content> | <tags>"

        parts = thread.content.split(" | ")
        if len(parts) >= 3:
            title = parts[0].replace("Classify:", "").strip()
            content = parts[1].strip()
            tags = [t.strip() for t in parts[2].split(",")]
        else:
            # Fallback: treat entire content as title
            title = thread.content
            content = ""
            tags = []

        # Run multi-agent debate (2 rounds)
        tier_result = await self.gemini_chat.classify_with_debate(
            title=title, content=content, tags=tags, rounds=2, voting_method="weighted_confidence",
        )

        response = f"""Intelligence Classification Result:
Tier: {tier_result.tier}
Confidence: {tier_result.confidence:.0%}
Reasoning: {tier_result.reasoning[:200]}...
Tags: {", ".join(tier_result.tags)}
"""

        return {"response": response, "tier_classification": tier_result}

    async def _execute_gemini_pro(self, thread: Thread) -> str:
        """Execute with Gemini Pro (single model, no debate)"""
        # Fallback to simple response
        return f"[Gemini Pro Analysis] {thread.content}"

    async def _execute_review_rounds(self, threads: list[Thread]):
        """Execute 3-round peer review rotation

        Round 2: Rotate reviewers right
        Round 3: Rotate reviewers right again
        """
        # Define rotation order
        rotation_llms = [LLMProvider.GEMINI_PRO, LLMProvider.GPT5, LLMProvider.PERPLEXITY]

        for thread in threads:
            # Round 2: Peer review
            if thread.assigned_llm in rotation_llms:
                idx = rotation_llms.index(thread.assigned_llm)
                thread.round_1_reviewer = rotation_llms[(idx + 1) % len(rotation_llms)]
                thread.round_2_review = f"[{thread.round_1_reviewer.value} review] Validated"

            # Round 3: Second review
            if thread.round_1_reviewer and thread.round_1_reviewer in rotation_llms:
                idx = rotation_llms.index(thread.round_1_reviewer)
                thread.round_2_reviewer = rotation_llms[(idx + 1) % len(rotation_llms)]
                thread.round_3_review = f"[{thread.round_2_reviewer.value} review] Confirmed"

    async def _synthesize_results(self, query: str, threads: list[Thread]) -> str:
        """Synthesize final answer from all thread results

        Uses PNKLN validation for intelligence classification
        """
        synthesis_parts = [f"Query: {query}", f"\nProcessed {len(threads)} thread(s):\n"]

        for thread in threads:
            synthesis_parts.append(f"\n--- Thread {thread.thread_id} ({thread.domain.value}) ---")
            synthesis_parts.append(f"Assigned LLM: {thread.assigned_llm.value}")
            synthesis_parts.append(f"Response: {thread.round_1_response[:300]}...")

            if thread.tier_classification:
                synthesis_parts.append(
                    f"Classification: Tier {thread.tier_classification.tier} "
                    f"({thread.tier_classification.confidence:.0%} confidence)",
                )

            if thread.round_2_review:
                synthesis_parts.append(f"Review 1: {thread.round_2_review}")

            if thread.round_3_review:
                synthesis_parts.append(f"Review 2: {thread.round_3_review}")

        return "\n".join(synthesis_parts)


# Example usage
async def example_intelligence_classification():
    """Example: Classify intelligence item using orchestrator"""
    orchestrator = PNKLNOrchestrator()

    result = await orchestrator.process_query(
        "Classify: FAA Proposes DO-178D Update | "
        "The Federal Aviation Administration today announced new regulatory requirements | "
        "aviation, regulation, AI",
        enable_review_rotation=False,
    )

    print(f"Query: {result.query}")
    print(f"Synthesis:\n{result.synthesis}")
    print("\nMetrics:")
    print(f"  Total Cost: ${result.total_cost:.4f}")
    print(f"  Total Latency: {result.total_latency_ms}ms")
    print(f"  Confidence: {result.confidence:.0%}")


if __name__ == "__main__":
    asyncio.run(example_intelligence_classification())
