"""Atomic Thread Orchestrator with Multi-Model Consensus (Ultrathink Merged)
Combines AoT decomposition with circular peer review + Ultrathink model allocation

Architecture:
0. Grok intake layer - pre-processes and structures query (Ultrathink)
1. Claude decomposes query into atomic threads (Purpose/Reasons/Brakes)
2. Each thread broadcast with model allocation: Gemini 40%, Claude 35%, GPT-5 15%, Perplexity 5%, Grok 5%
3. Circular peer review (2 rounds)
4. Claude stitches results into execution-ready output
"""

import asyncio
import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import aiohttp

# Import archive and cost tracking
try:
    from transcript_archive import TranscriptArchive

    ARCHIVE_AVAILABLE = True
except ImportError:
    ARCHIVE_AVAILABLE = False

try:
    from cost_tracker import CostTracker

    COST_TRACKING_AVAILABLE = True
except ImportError:
    COST_TRACKING_AVAILABLE = False


# ATP 5-19 Risk Classification
class RiskLevel(Enum):
    RA_1 = "routine"  # Normal operations
    RA_2 = "low"  # Minor impact if fails
    RA_3 = "moderate"  # Significant but containable
    RA_4 = "high"  # Mission-critical failure


@dataclass
class AtomicThread:
    """Single atomic reasoning unit with isolated context.
    Failure in one thread does not cascade to others.
    """

    thread_id: str
    purpose: str  # ShadowTag-v2JR: What is this thread solving?
    reasons: list[str]  # ShadowTag-v2JR: Why is this approach valid?
    brakes: list[str]  # ShadowTag-v2JR: What constraints must be enforced?
    risk_level: RiskLevel
    prompt: str
    dependencies: list[str] = field(default_factory=list)

    # Multi-model consensus results
    model_responses: list[dict[str, Any]] = field(default_factory=list)
    peer_reviews: list[dict[str, Any]] = field(default_factory=list)
    consensus_result: str | None = None

    error: Exception | None = None
    execution_time: float = 0.0

    def get_audit_trail(self) -> dict[str, Any]:
        """Generate audit trail for ShadowTag-v2JR compliance."""
        return {
            "thread_id": self.thread_id,
            "purpose": self.purpose,
            "reasons": self.reasons,
            "brakes": self.brakes,
            "risk_level": self.risk_level.value,
            "execution_time": self.execution_time,
            "models_consulted": len(self.model_responses),
            "peer_reviews_conducted": len(self.peer_reviews),
            "success": self.error is None,
            "error": str(self.error) if self.error else None,
            "timestamp": datetime.utcnow().isoformat(),
        }


class AtomicConsensusOrchestrator:
    """Unified orchestrator: Atomic threading + Multi-model consensus

    Flow:
    1. Claude decomposes into threads (JR)
    2. Each thread → Gemini, Perplexity, SuperGrok
    3. Circular peer review (2 rounds)
    4. Claude stitches (Cor)
    """

    def __init__(self):
        # API keys from environment
        self.anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        self.google_key = os.environ.get("GOOGLE_API_KEY")
        self.perplexity_key = os.environ.get("PERPLEXITY_API_KEY")
        self.xai_key = os.environ.get("XAI_API_KEY")
        self.openai_key = os.environ.get("OPENAI_API_KEY")

        # API endpoints
        self.anthropic_endpoint = "https://api.anthropic.com/v1/messages"
        self.perplexity_endpoint = "https://api.perplexity.ai/chat/completions"
        self.xai_endpoint = "https://api.x.ai/v1/chat/completions"
        self.openai_endpoint = "https://api.openai.com/v1/chat/completions"

        # Ultrathink model allocation percentages
        self.model_allocation = {
            "gemini": 0.40,  # 40%
            "claude": 0.35,  # 35%
            "gpt": 0.15,  # 15%
            "perplexity": 0.05,  # 5%
            "grok": 0.05,  # 5%
        }

        # Initialize Gemini
        try:
            import google.generativeai as genai

            if self.google_key:
                genai.configure(api_key=self.google_key)
                self.gemini_model = genai.GenerativeModel("gemini-3.1-flash-lite-preview")
            else:
                self.gemini_model = None
        except ImportError:
            print("[WARNING] google-generativeai not installed")
            self.gemini_model = None

        # Model order for circular review (Ultrathink: all 5 models)
        self.models = ["Gemini", "Claude", "GPT", "Perplexity", "Grok"]

    async def process_message(
        self,
        user_message: str,
        max_threads: int = 6,
        auto_archive: bool = True,
        tags: list[str] = None,
    ) -> dict[str, Any]:
        """Full pipeline: Decompose → Consensus → Stitch"""
        print(f"\n{'=' * 80}")
        print("ATOMIC CONSENSUS ORCHESTRATOR (ULTRATHINK)")
        print(f"{'=' * 80}\n")

        # Step 0: Grok intake layer (Ultrathink pre-processing)
        print("[Grok Intake] Pre-processing and structuring query...")
        structured_message = await self._grok_intake(user_message)
        print("[Grok Intake] Query structured ✓\n")

        # Step 1: Claude decomposes into atomic threads
        print("[JR] Decomposing message into atomic threads...")
        threads = await self._decompose_into_threads(structured_message, max_threads)
        print(f"[JR] Created {len(threads)} atomic threads\n")

        if not threads:
            return {
                "final_output": "Could not decompose query into threads.",
                "threads": [],
                "execution_summary": {},
            }

        # Step 2: Execute each thread with multi-model consensus
        print("[NS] Executing threads with multi-model consensus...")
        executed_threads = await self._execute_threads_with_consensus(threads)
        print(f"[NS] Completed {len(executed_threads)} threads\n")

        # Step 3: Claude stitches everything together
        print("[Cor] Stitching results into unified output...")
        final_result = await self._stitch_results(user_message, executed_threads)
        print("[✓] Complete - ready for execution\n")

        # Step 4: Auto-archive if enabled
        transcript_id = None
        if auto_archive and ARCHIVE_AVAILABLE:
            try:
                archive = TranscriptArchive()
                transcript_id = archive.archive(
                    user_query=user_message,
                    result=final_result,
                    system_type="atomic",
                    tags=tags or [],
                )
                archive.close()
                print(f"[Archive] Saved as transcript #{transcript_id}\n")
            except Exception as e:
                print(f"[WARNING] Failed to archive: {e}\n")

        # Step 5: Track costs if enabled
        if COST_TRACKING_AVAILABLE and transcript_id:
            try:
                cost_tracker = CostTracker()

                # Calculate model usage from final_result
                model_usage = self._extract_token_usage(final_result, executed_threads)

                # Track cost
                # Ultrathink: Grok intake (1) + decompose (1) + threads * 11 + stitch (1)
                total_api_calls = 1 + 1 + (len(executed_threads) * 11) + 1
                query_cost = cost_tracker.track_query_cost(
                    transcript_id=transcript_id,
                    system_type="atomic",
                    model_usage=model_usage,
                    api_calls=total_api_calls,
                    peer_reviews=sum(len(t.peer_reviews) for t in executed_threads),
                    threads=len(executed_threads),
                )

                cost_tracker.close()
                print(
                    f"[Cost] ${query_cost.total_cost:.4f} ({query_cost.api_calls_made} API calls)\n",
                )

                # Add cost to result
                final_result["cost_breakdown"] = query_cost.to_dict()

            except Exception as e:
                print(f"[WARNING] Failed to track cost: {e}\n")

        return final_result

    async def _grok_intake(self, user_message: str) -> str:
        """Ultrathink Layer 0: Grok pre-processes and structures the query
        before Claude decomposition.

        Adds context, identifies ambiguities, suggests decomposition hints.
        """
        intake_prompt = f"""You are the Grok intake processor in an Ultrathink multi-AI system.

USER QUERY:
{user_message}

Your role: Analyze and structure this query to maximize the effectiveness of downstream AI processing.

Provide:
1. **Query Intent**: What is the user actually trying to accomplish?
2. **Key Dimensions**: What aspects/dimensions should be analyzed?
3. **Ambiguities**: What needs clarification or assumptions?
4. **Decomposition Hints**: How should this be broken down into sub-problems?
5. **Structured Query**: Enhanced version of the query with added context

Return as JSON:
{{
    "intent": "...",
    "dimensions": ["dimension1", "dimension2"],
    "ambiguities": ["ambiguity1"],
    "decomposition_hints": ["hint1", "hint2"],
    "structured_query": "Enhanced query with context..."
}}"""

        if not self.xai_key:
            # Fallback: return original message if no Grok access
            return user_message

        try:
            async with (
                aiohttp.ClientSession() as session,
                session.post(
                    self.xai_endpoint,
                    headers={
                        "Authorization": f"Bearer {self.xai_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "grok-2-latest",
                        "messages": [{"role": "user", "content": intake_prompt}],
                        "temperature": 0.5,
                    },
                ) as response,
            ):
                data = await response.json()
                grok_output = data["choices"][0]["message"]["content"]

                # Parse JSON
                if "```json" in grok_output:
                    grok_output = grok_output.split("```json")[1].split("```")[0]

                try:
                    intake_data = json.loads(grok_output.strip())
                    # Return the structured query with metadata
                    structured = f"""[GROK INTAKE ANALYSIS]
Intent: {intake_data.get("intent", "N/A")}
Dimensions: {", ".join(intake_data.get("dimensions", []))}
Decomposition Hints: {", ".join(intake_data.get("decomposition_hints", []))}

[STRUCTURED QUERY]
{intake_data.get("structured_query", user_message)}"""
                    return structured
                except json.JSONDecodeError:
                    # Fallback: use Grok's text output
                    return f"[GROK INTAKE]\n{grok_output}\n\n[ORIGINAL QUERY]\n{user_message}"

        except Exception as e:
            print(f"[WARNING] Grok intake failed: {e}, using original query")
            return user_message

    def _extract_token_usage(
        self,
        final_result: dict[str, Any],
        threads: list[AtomicThread],
    ) -> dict[str, dict[str, int]]:
        """Extract token usage from result and threads for cost tracking (Ultrathink).
        Returns: {model_name: {input: X, output: Y}}
        """
        model_usage = {}

        # 1. Grok intake cost (new in Ultrathink)
        grok_intake_tokens = {"input": 800, "output": 600}
        model_usage["grok-2-latest"] = {
            "input": grok_intake_tokens["input"],
            "output": grok_intake_tokens["output"],
        }

        # 2. Claude calls (decomposition + stitching)
        claude_model = "claude-sonnet-4-20250514"
        decompose_tokens = {"input": 1500, "output": 700}  # Increased due to Grok intake context
        stitch_tokens = {"input": 5000, "output": 2000}

        if claude_model not in model_usage:
            model_usage[claude_model] = {"input": 0, "output": 0}

        model_usage[claude_model]["input"] += decompose_tokens["input"] + stitch_tokens["input"]
        model_usage[claude_model]["output"] += decompose_tokens["output"] + stitch_tokens["output"]

        # 3. Count model usage from threads based on allocation
        # With Ultrathink: Gemini 40%, Claude 35%, GPT 15%, Perplexity 5%, Grok 5%
        model_pricing_map = {
            "Gemini": "gemini-3.1-flash-lite-preview",
            "Claude": "claude-sonnet-4-20250514",
            "GPT": "gpt-4-turbo-preview",
            "Perplexity": "llama-3.1-sonar-large-128k-online",
            "Grok": "grok-2-latest",
        }

        for thread in threads:
            # Count models actually used in this thread
            models_in_thread = set()
            for response in thread.model_responses:
                model_name = response.get("model", "Unknown")
                models_in_thread.add(model_name)

            # Each model in thread: main response + 2 peer reviews
            for model_name in models_in_thread:
                pricing_key = model_pricing_map.get(model_name, "grok-2-latest")

                if pricing_key not in model_usage:
                    model_usage[pricing_key] = {"input": 0, "output": 0}

                # Main response + 2 peer reviews
                model_usage[pricing_key]["input"] += 3 * 1500
                model_usage[pricing_key]["output"] += 3 * 800

            # Claude synthesis per thread (if not already primary)
            if "Claude" not in models_in_thread:
                model_usage[claude_model]["input"] += 2000
                model_usage[claude_model]["output"] += 1000

        return model_usage

    async def _decompose_into_threads(
        self,
        user_message: str,
        max_threads: int,
    ) -> list[AtomicThread]:
        """JR Layer: Claude decomposes message into atomic threads
        with Purpose/Reasons/Brakes
        """
        decomposition_prompt = f"""You are ShadowTag-v2JR Judge 6, a military-grade reasoning system.

USER MESSAGE:
{user_message}

Decompose this into atomic, parallelizable reasoning threads.

For each thread:
1. PURPOSE: What specific sub-problem does this solve?
2. REASONS: Why is this decomposition valid? What assumptions hold?
3. BRAKES: What constraints/limits must be respected?
4. RISK_LEVEL: RA-1 (routine), RA-2 (low), RA-3 (moderate), RA-4 (high)
5. DEPENDENCIES: Which threads must complete first? (use thread_ids)

Return JSON array (max {max_threads} threads):
[
  {{
    "thread_id": "T001_analysis",
    "purpose": "Specific sub-problem to solve",
    "reasons": ["Reason 1", "Reason 2"],
    "brakes": ["Constraint 1", "Constraint 2"],
    "risk_level": "RA-2",
    "dependencies": [],
    "prompt": "Detailed prompt for this thread..."
  }}
]

CRITICAL: Threads must be independent (minimal dependencies) for parallel execution.
Each prompt should be self-contained."""

        async with (
            aiohttp.ClientSession() as session,
            session.post(
                self.anthropic_endpoint,
                headers={
                    "x-api-key": self.anthropic_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 4000,
                    "messages": [{"role": "user", "content": decomposition_prompt}],
                },
            ) as response,
        ):
            data = await response.json()
            text = data["content"][0]["text"].strip()

            # Parse JSON
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            try:
                threads_data = json.loads(text.strip())
            except json.JSONDecodeError:
                print("[WARNING] Could not parse thread decomposition")
                return []

            # Convert to AtomicThread objects
            threads = []
            for td in threads_data:
                thread = AtomicThread(
                    thread_id=td["thread_id"],
                    purpose=td["purpose"],
                    reasons=td["reasons"],
                    brakes=td["brakes"],
                    risk_level=RiskLevel[td["risk_level"].replace("-", "_")],
                    prompt=td["prompt"],
                    dependencies=td.get("dependencies", []),
                )
                threads.append(thread)

            return threads

    async def _execute_threads_with_consensus(
        self,
        threads: list[AtomicThread],
    ) -> list[AtomicThread]:
        """Execute threads concurrently, each with full consensus pipeline"""
        # Build execution order (topological sort)
        executed = set()
        results = []
        total_threads = len(threads)

        while len(executed) < len(threads):
            # Find threads ready to execute
            ready = [
                t
                for t in threads
                if t.thread_id not in executed and all(dep in executed for dep in t.dependencies)
            ]

            if not ready:
                break  # Circular dependency or done

            # Execute ready threads concurrently (pass indices for model allocation)
            thread_indices = [threads.index(t) for t in ready]
            batch_results = await asyncio.gather(
                *[
                    self._execute_single_thread(ready[i], thread_indices[i], total_threads)
                    for i in range(len(ready))
                ],
                return_exceptions=True,
            )

            for thread_result in batch_results:
                if isinstance(thread_result, Exception):
                    print(f"[WARNING] Thread execution failed: {thread_result}")
                else:
                    results.append(thread_result)
                    executed.add(thread_result.thread_id)

        return results

    async def _execute_single_thread(
        self,
        thread: AtomicThread,
        thread_index: int = 0,
        total_threads: int = 1,
    ) -> AtomicThread:
        """Execute single thread with multi-model consensus + peer review"""
        start_time = time.time()

        try:
            # Enforce brakes
            enforced_prompt = f"""[ShadowTag-v2JR CONSTRAINTS]
PURPOSE: {thread.purpose}
BRAKES: {", ".join(thread.brakes)}

[TASK]
{thread.prompt}

[ENFORCEMENT]
You MUST respect the brakes above. Provide structured response with clear reasoning."""

            # Broadcast to models (with Ultrathink allocation)
            model_responses = await self._broadcast_to_models(
                enforced_prompt,
                thread_index,
                total_threads,
            )
            thread.model_responses = model_responses

            if not model_responses:
                thread.error = Exception("No model responses received")
                return thread

            # Circular peer review (2 rounds)
            peer_reviews = await self._circular_peer_review(model_responses)
            thread.peer_reviews = peer_reviews

            # Synthesize consensus for this thread
            thread.consensus_result = await self._synthesize_thread_consensus(
                thread,
                model_responses,
                peer_reviews,
            )

        except Exception as e:
            thread.error = e
        finally:
            thread.execution_time = time.time() - start_time

        return thread

    async def _broadcast_to_models(
        self,
        prompt: str,
        thread_index: int = 0,
        total_threads: int = 1,
    ) -> list[dict[str, Any]]:
        """Broadcast prompt to models based on Ultrathink allocation.

        Model allocation (weighted selection):
        - Gemini: 40%
        - Claude: 35%
        - GPT: 15%
        - Perplexity: 5%
        - Grok: 5%

        Each thread gets 3 models: 1 primary (based on allocation) + 2 for peer review
        """
        import random

        # Determine primary model for this thread based on allocation
        rand_val = (thread_index / max(total_threads, 1)) + random.random() * 0.1
        if rand_val < 0.40:
            primary = "gemini"
        elif rand_val < 0.75:  # 0.40 + 0.35
            primary = "claude"
        elif rand_val < 0.90:  # 0.75 + 0.15
            primary = "gpt"
        elif rand_val < 0.95:  # 0.90 + 0.05
            primary = "perplexity"
        else:
            primary = "grok"

        # Always include primary + select 2 others for peer review
        tasks = []
        models_used = set()

        # Add primary model
        if primary == "gemini" and self.gemini_model:
            tasks.append(self._query_gemini(prompt))
            models_used.add("gemini")
        elif primary == "claude" and self.anthropic_key:
            tasks.append(self._query_claude(prompt))
            models_used.add("claude")
        elif primary == "gpt" and self.openai_key:
            tasks.append(self._query_gpt(prompt))
            models_used.add("gpt")
        elif primary == "perplexity" and self.perplexity_key:
            tasks.append(self._query_perplexity(prompt))
            models_used.add("perplexity")
        elif primary == "grok" and self.xai_key:
            tasks.append(self._query_grok(prompt))
            models_used.add("grok")

        # Add 2 peer review models (different from primary)
        available_models = [
            ("gemini", self.gemini_model, self._query_gemini),
            ("claude", self.anthropic_key, self._query_claude),
            ("gpt", self.openai_key, self._query_gpt),
            ("perplexity", self.perplexity_key, self._query_perplexity),
            ("grok", self.xai_key, self._query_grok),
        ]

        peer_reviewers = [
            (name, query_func)
            for name, key, query_func in available_models
            if name not in models_used and key
        ]

        # Select up to 2 peer reviewers
        for name, query_func in peer_reviewers[:2]:
            tasks.append(query_func(prompt))
            models_used.add(name)

        if not tasks:
            return []

        responses = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in responses if isinstance(r, dict)]

    async def _circular_peer_review(self, responses: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """2 rounds of circular peer review:
        Round 1: Each reviews right neighbor
        Round 2: Each reviews second neighbor
        """
        all_reviews = []
        n = len(responses)

        # Round 1: shift right once
        for i, reviewer_resp in enumerate(responses):
            reviewed_idx = (i + 1) % n
            reviewed_resp = responses[reviewed_idx]

            if reviewer_resp["model"] != reviewed_resp["model"]:
                review = await self._get_peer_review(reviewer_resp, reviewed_resp)
                all_reviews.append(review)

        # Round 2: shift right twice
        for i, reviewer_resp in enumerate(responses):
            reviewed_idx = (i + 2) % n
            reviewed_resp = responses[reviewed_idx]

            if reviewer_resp["model"] != reviewed_resp["model"]:
                review = await self._get_peer_review(reviewer_resp, reviewed_resp)
                all_reviews.append(review)

        return all_reviews

    async def _get_peer_review(
        self,
        reviewer_resp: dict[str, Any],
        reviewed_resp: dict[str, Any],
    ) -> dict[str, Any]:
        """Get one model to review another's response"""
        review_prompt = f"""Peer-review another AI model's response.

MODEL BEING REVIEWED: {reviewed_resp["model"]}
THEIR RESPONSE:
{reviewed_resp["content"]}

Provide critical review in JSON:
{{
    "agreement_score": 0.85,
    "strengths": ["point 1"],
    "concerns": ["issue 1"],
    "suggestions": ["suggestion 1"],
    "critique": "Detailed critique..."
}}"""

        model_name = reviewer_resp["model"].lower()

        if "gemini" in model_name:
            review_text = await self._query_gemini_text(review_prompt)
        elif "claude" in model_name:
            review_text = await self._query_claude_text(review_prompt)
        elif "gpt" in model_name:
            review_text = await self._query_gpt_text(review_prompt)
        elif "perplexity" in model_name:
            review_text = await self._query_perplexity_text(review_prompt)
        elif "grok" in model_name or "supergrok" in model_name:
            review_text = await self._query_grok_text(review_prompt)
        else:
            return {
                "reviewer": reviewer_resp["model"],
                "reviewed": reviewed_resp["model"],
                "critique": "Could not route review",
                "agreement_score": 0.5,
            }

        # Parse JSON
        try:
            if "```json" in review_text:
                review_text = review_text.split("```json")[1].split("```")[0]
            review_data = json.loads(review_text.strip())
        except:
            review_data = {"agreement_score": 0.5, "critique": review_text}

        return {
            "reviewer": reviewer_resp["model"],
            "reviewed": reviewed_resp["model"],
            "agreement_score": review_data.get("agreement_score", 0.5),
            "critique": review_data.get("critique", review_text),
            "concerns": review_data.get("concerns", []),
            "suggestions": review_data.get("suggestions", []),
        }

    async def _synthesize_thread_consensus(
        self,
        thread: AtomicThread,
        responses: list[dict[str, Any]],
        reviews: list[dict[str, Any]],
    ) -> str:
        """Synthesize consensus for single thread"""
        context = f"""THREAD: {thread.thread_id}
PURPOSE: {thread.purpose}

MODEL RESPONSES:
"""
        for resp in responses:
            context += f"\n{resp['model']}:\n{resp['content']}\n"

        if reviews:
            context += "\nPEER REVIEWS:\n"
            for review in reviews:
                context += f"{review['reviewer']} → {review['reviewed']} (agreement: {review['agreement_score']}):\n{review['critique']}\n\n"

        synthesis_prompt = f"""{context}

Synthesize the above into a single consensus answer for this thread.
Focus on points of agreement, resolve contradictions, integrate peer feedback.
Keep it concise and execution-ready."""

        async with (
            aiohttp.ClientSession() as session,
            session.post(
                self.anthropic_endpoint,
                headers={
                    "x-api-key": self.anthropic_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 2000,
                    "messages": [{"role": "user", "content": synthesis_prompt}],
                },
            ) as response,
        ):
            data = await response.json()
            return data["content"][0]["text"]

    async def _stitch_results(
        self,
        original_message: str,
        threads: list[AtomicThread],
    ) -> dict[str, Any]:
        """Cor Layer: Claude stitches all thread results into final output"""
        successful = [t for t in threads if t.error is None and t.consensus_result]
        failed = [t for t in threads if t.error is not None or not t.consensus_result]

        # Build stitching context
        thread_results = "\n\n".join(
            [
                f"## Thread: {t.thread_id}\n**Purpose:** {t.purpose}\n**Consensus Result:**\n{t.consensus_result}"
                for t in successful
            ],
        )

        stitching_prompt = f"""You are Cor, the unified execution brain.

ORIGINAL USER MESSAGE:
{original_message}

ATOMIC THREAD RESULTS (each validated by multi-model consensus):
{thread_results}

{"FAILED THREADS:" if failed else ""}
{chr(10).join([f"- {t.thread_id}: {t.error}" for t in failed]) if failed else ""}

TASK:
Synthesize these thread results into a coherent, execution-ready response.
- Maintain logical flow
- Resolve contradictions
- Add executive summary
- Make it actionable

Generate final output now."""

        async with (
            aiohttp.ClientSession() as session,
            session.post(
                self.anthropic_endpoint,
                headers={
                    "x-api-key": self.anthropic_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 8000,
                    "messages": [{"role": "user", "content": stitching_prompt}],
                },
            ) as response,
        ):
            data = await response.json()
            final_output = data["content"][0]["text"]

        return {
            "final_output": final_output,
            "threads": [t.get_audit_trail() for t in threads],
            "execution_summary": {
                "total_threads": len(threads),
                "successful_threads": len(successful),
                "failed_threads": len(failed),
                "total_models_consulted": sum(len(t.model_responses) for t in threads),
                "total_peer_reviews": sum(len(t.peer_reviews) for t in threads),
                "avg_execution_time": sum(t.execution_time for t in threads) / len(threads)
                if threads
                else 0,
                "success_rate": len(successful) / len(threads) if threads else 0,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    # === Model query methods ===

    async def _query_gemini(self, prompt: str) -> dict[str, Any]:
        """Query Gemini"""
        response = await asyncio.to_thread(self.gemini_model.generate_content, prompt)
        return {"model": "Gemini", "content": response.text}

    async def _query_gemini_text(self, prompt: str) -> str:
        """Query Gemini, return text only"""
        response = await self._query_gemini(prompt)
        return response["content"]

    async def _query_perplexity(self, prompt: str) -> dict[str, Any]:
        """Query Perplexity"""
        async with (
            aiohttp.ClientSession() as session,
            session.post(
                self.perplexity_endpoint,
                headers={
                    "Authorization": f"Bearer {self.perplexity_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.1-sonar-large-128k-online",
                    "messages": [{"role": "user", "content": prompt}],
                },
            ) as response,
        ):
            data = await response.json()
            return {"model": "Perplexity", "content": data["choices"][0]["message"]["content"]}

    async def _query_perplexity_text(self, prompt: str) -> str:
        """Query Perplexity, return text only"""
        response = await self._query_perplexity(prompt)
        return response["content"]

    async def _query_grok(self, prompt: str) -> dict[str, Any]:
        """Query Grok (xAI)"""
        async with (
            aiohttp.ClientSession() as session,
            session.post(
                self.xai_endpoint,
                headers={
                    "Authorization": f"Bearer {self.xai_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "grok-2-latest",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                },
            ) as response,
        ):
            data = await response.json()
            return {"model": "Grok", "content": data["choices"][0]["message"]["content"]}

    async def _query_grok_text(self, prompt: str) -> str:
        """Query Grok, return text only"""
        response = await self._query_grok(prompt)
        return response["content"]

    # Alias for backward compatibility
    async def _query_supergrok(self, prompt: str) -> dict[str, Any]:
        """Query SuperGrok (alias for Grok)"""
        return await self._query_grok(prompt)

    async def _query_supergrok_text(self, prompt: str) -> str:
        """Query SuperGrok, return text only (alias)"""
        return await self._query_grok_text(prompt)

    async def _query_claude(self, prompt: str) -> dict[str, Any]:
        """Query Claude Sonnet"""
        async with (
            aiohttp.ClientSession() as session,
            session.post(
                self.anthropic_endpoint,
                headers={
                    "x-api-key": self.anthropic_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 2000,
                    "messages": [{"role": "user", "content": prompt}],
                },
            ) as response,
        ):
            data = await response.json()
            return {"model": "Claude", "content": data["content"][0]["text"]}

    async def _query_claude_text(self, prompt: str) -> str:
        """Query Claude, return text only"""
        response = await self._query_claude(prompt)
        return response["content"]

    async def _query_gpt(self, prompt: str) -> dict[str, Any]:
        """Query GPT-4/GPT-5"""
        async with (
            aiohttp.ClientSession() as session,
            session.post(
                self.openai_endpoint,
                headers={
                    "Authorization": f"Bearer {self.openai_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4-turbo-preview",  # Will use GPT-5 when available
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                },
            ) as response,
        ):
            data = await response.json()
            return {"model": "GPT", "content": data["choices"][0]["message"]["content"]}

    async def _query_gpt_text(self, prompt: str) -> str:
        """Query GPT, return text only"""
        response = await self._query_gpt(prompt)
        return response["content"]


# === CLI ===


async def main():
    """CLI interface"""
    import sys

    orchestrator = AtomicConsensusOrchestrator()

    if len(sys.argv) > 1:
        user_message = " ".join(sys.argv[1:])
    else:
        print("Atomic Consensus Orchestrator")
        print("Enter your message:\n")
        user_message = input("> ").strip()

    if not user_message:
        print("No message provided.")
        return

    # Process
    result = await orchestrator.process_message(user_message)

    # Display
    print(f"{'=' * 80}")
    print("FINAL OUTPUT (Execution-Ready)")
    print(f"{'=' * 80}\n")
    print(result["final_output"])
    print(f"\n{'=' * 80}")
    print("EXECUTION SUMMARY")
    print(f"{'=' * 80}")
    summary = result["execution_summary"]
    print(f"Threads: {summary['total_threads']}")
    print(f"Success Rate: {summary['success_rate'] * 100:.0f}%")
    print(f"Models Consulted: {summary['total_models_consulted']}")
    print(f"Peer Reviews: {summary['total_peer_reviews']}")
    print(f"Avg Thread Time: {summary['avg_execution_time']:.2f}s")
    print(f"{'=' * 80}\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure API keys are set:")
        print("  export ANTHROPIC_API_KEY='...'")
        print("  export GOOGLE_API_KEY='...'")
        print("  export PERPLEXITY_API_KEY='...'")
        print("  export XAI_API_KEY='...'")
