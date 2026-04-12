"""
Message-Level Consensus Orchestrator for Claude Code
Processes user messages through 3 LLMs with circular peer review

Flow:
1. User message → Claude (Layer 1)
2. Claude broadcasts to: Gemini, Perplexity, SuperGrok
3. Circular review round 1: Each reviews right neighbor
4. Circular review round 2: Each reviews second neighbor
5. Claude synthesizes and executes
"""

import asyncio
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
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


@dataclass
class ModelResponse:
    """Single model's response"""

    model_name: str
    content: str
    timestamp: str
    token_usage: dict[str, int] = None


@dataclass
class PeerReview:
    """Peer review from one model about another"""

    reviewer: str
    reviewed: str
    critique: str
    agreement_score: float
    suggestions: list[str]


class MessageConsensusOrchestrator:
    """
    Lightweight consensus system for Claude Code messages.
    Fixed models: Gemini, Perplexity, SuperGrok
    """

    def __init__(self):
        # API keys from environment
        self.anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        self.google_key = os.environ.get("GOOGLE_API_KEY")
        self.perplexity_key = os.environ.get("PERPLEXITY_API_KEY")
        self.xai_key = os.environ.get("XAI_API_KEY")

        # API endpoints
        self.anthropic_endpoint = "https://api.anthropic.com/v1/messages"
        self.perplexity_endpoint = "https://api.perplexity.ai/chat/completions"
        self.xai_endpoint = "https://api.x.ai/v1/chat/completions"

        # Initialize Gemini
        try:
            import google.generativeai as genai

            if self.google_key:
                genai.configure(api_key=self.google_key)
                self.gemini_model = genai.GenerativeModel("gemini-2.0-flash-exp")
            else:
                self.gemini_model = None
        except ImportError:
            print("[WARNING] google-generativeai not installed")
            self.gemini_model = None

        # Model order for circular review (fixed)
        self.models = ["Gemini", "Perplexity", "SuperGrok"]

    async def process_message(
        self, user_message: str, auto_archive: bool = True, tags: list[str] = None
    ) -> dict[str, Any]:
        """
        Process user message through full consensus pipeline.

        Returns:
            Dict with final_answer, explanations, and metadata
        """
        print(f"\n{'=' * 80}")
        print("MESSAGE CONSENSUS ORCHESTRATOR")
        print(f"{'=' * 80}\n")

        # Layer 1: Claude initial analysis
        print("[Layer 1] Claude analyzing your message...")
        claude_initial = await self._query_claude(user_message, is_initial=True)

        # Layer 2: Broadcast to the 3 models
        print("\n[Layer 2] Broadcasting to Gemini, Perplexity, SuperGrok...")
        layer2_responses = await self._broadcast_to_models(user_message, claude_initial.content)

        if not layer2_responses:
            print("[WARNING] No Layer 2 responses. Using Claude only.")
            result = {
                "final_output": claude_initial.content,
                "explanations": [],
                "peer_reviews": [],
                "execution_ready": True,
            }
        else:
            print(f"[Layer 2] Received {len(layer2_responses)} responses\n")

            # Layer 2.5: Circular peer review (2 rounds)
            print("[Layer 2.5] Round 1: Each model reviews right neighbor...")
            round1_reviews = await self._circular_review_round(layer2_responses, shift=1)

            print("[Layer 2.5] Round 2: Each model reviews second neighbor...")
            round2_reviews = await self._circular_review_round(layer2_responses, shift=2)

            all_reviews = round1_reviews + round2_reviews
            print(f"[Layer 2.5] Completed {len(all_reviews)} peer reviews\n")

            # Layer 3: Claude synthesizes and prepares execution
            print("[Layer 3] Claude synthesizing final answer for execution...")
            result = await self._claude_synthesis(
                user_message, claude_initial, layer2_responses, all_reviews
            )

        print("[✓] Consensus complete - ready for execution\n")

        # Auto-archive if enabled
        transcript_id = None
        if auto_archive and ARCHIVE_AVAILABLE:
            try:
                archive = TranscriptArchive()
                transcript_id = archive.archive(
                    user_query=user_message, result=result, system_type="simple", tags=tags or []
                )
                archive.close()
                print(f"[Archive] Saved as transcript #{transcript_id}\n")
            except Exception as e:
                print(f"[WARNING] Failed to archive: {e}\n")

        # Track costs if enabled
        if COST_TRACKING_AVAILABLE and transcript_id:
            try:
                cost_tracker = CostTracker()

                # Calculate model usage
                model_usage = {
                    "claude-sonnet-4-20250514": {
                        "input": 3000,  # Layer 1 + Layer 3
                        "output": 2000,
                    }
                }

                # Add Layer 2 models if used
                if layer2_responses:
                    for resp in layer2_responses:
                        model_name = self._map_model_name(resp.model_name)
                        if model_name not in model_usage:
                            model_usage[model_name] = {"input": 0, "output": 0}
                        # 1 response + 2 peer reviews
                        model_usage[model_name]["input"] += 3 * 1500
                        model_usage[model_name]["output"] += 3 * 800

                # Track cost
                api_calls = 2 + (
                    len(layer2_responses) * 3 if layer2_responses else 0
                )  # Claude L1/L3 + models * 3
                peer_reviews = len(all_reviews) if layer2_responses else 0

                query_cost = cost_tracker.track_query_cost(
                    transcript_id=transcript_id,
                    system_type="simple",
                    model_usage=model_usage,
                    api_calls=api_calls,
                    peer_reviews=peer_reviews,
                    threads=0,
                )

                cost_tracker.close()
                print(
                    f"[Cost] ${query_cost.total_cost:.4f} ({query_cost.api_calls_made} API calls)\n"
                )

                # Add cost to result
                result["cost_breakdown"] = query_cost.to_dict()

            except Exception as e:
                print(f"[WARNING] Failed to track cost: {e}\n")

        return result

    def _map_model_name(self, model_name: str) -> str:
        """Map friendly model names to pricing keys"""
        mapping = {
            "Gemini": "gemini-2.0-flash-exp",
            "Perplexity": "llama-3.1-sonar-large-128k-online",
            "SuperGrok": "grok-2-latest",
            "GPT4": "gpt-4-turbo-preview",
        }
        return mapping.get(model_name, model_name)

    async def _query_claude(self, message: str, is_initial: bool = False) -> ModelResponse:
        """Query Claude (Layer 1 or Layer 3)"""
        if is_initial:
            prompt = f"""You are the initial reasoning layer in a consensus system.

USER MESSAGE:
{message}

Analyze this message:
1. What is the user asking for?
2. What are the key requirements?
3. What approach would you take?
4. What potential issues should we watch for?

Your analysis will be sent to Gemini, Perplexity, and SuperGrok for their input.
Be thorough but concise."""
        else:
            # This will be used for synthesis
            prompt = message

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
                    "messages": [{"role": "user", "content": prompt}],
                },
            ) as response,
        ):
            data = await response.json()
            return ModelResponse(
                model_name="Claude",
                content=data["content"][0]["text"],
                timestamp=datetime.utcnow().isoformat(),
                token_usage={
                    "input": data["usage"]["input_tokens"],
                    "output": data["usage"]["output_tokens"],
                },
            )

    async def _broadcast_to_models(
        self, user_message: str, claude_analysis: str
    ) -> list[ModelResponse]:
        """Broadcast to Gemini, Perplexity, SuperGrok in parallel"""

        base_prompt = f"""You are part of a multi-model consensus system.

USER'S ORIGINAL MESSAGE:
{user_message}

CLAUDE'S INITIAL ANALYSIS:
{claude_analysis}

Your task:
1. Analyze the user's message independently
2. Consider Claude's analysis
3. Provide your complete response
4. Explain your reasoning

Your response will be peer-reviewed by other models."""

        tasks = []

        if self.gemini_model:
            tasks.append(self._query_gemini(base_prompt))
        if self.perplexity_key:
            tasks.append(self._query_perplexity(base_prompt))
        if self.xai_key:
            tasks.append(self._query_supergrok(base_prompt))

        if not tasks:
            return []

        responses = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in responses if isinstance(r, ModelResponse)]

    async def _circular_review_round(
        self, responses: list[ModelResponse], shift: int
    ) -> list[PeerReview]:
        """
        Perform one round of circular peer review.
        shift=1: Each reviews right neighbor
        shift=2: Each reviews second neighbor
        """
        reviews = []
        n = len(responses)

        for i, reviewer_response in enumerate(responses):
            # Calculate which response to review (circular)
            reviewed_idx = (i + shift) % n
            reviewed_response = responses[reviewed_idx]

            # Skip self-review
            if reviewer_response.model_name == reviewed_response.model_name:
                continue

            review = await self._get_peer_review(reviewer_response, reviewed_response)
            reviews.append(review)

        return reviews

    async def _get_peer_review(
        self, reviewer_response: ModelResponse, reviewed_response: ModelResponse
    ) -> PeerReview:
        """Get peer review from reviewer about reviewed"""

        review_prompt = f"""Peer review another AI model's response.

MODEL BEING REVIEWED: {reviewed_response.model_name}
THEIR RESPONSE:
{reviewed_response.content}

Provide critical peer review in JSON:
{{
    "agreement_score": 0.85,
    "strengths": ["point 1", "point 2"],
    "concerns": ["issue 1", "issue 2"],
    "suggestions": ["suggestion 1"],
    "critique": "Your detailed critique..."
}}"""

        # Route to appropriate model
        model_name = reviewer_response.model_name.lower()

        if "gemini" in model_name:
            review_text = await self._query_gemini_text(review_prompt)
        elif "perplexity" in model_name:
            review_text = await self._query_perplexity_text(review_prompt)
        elif "grok" in model_name or "supergrok" in model_name:
            review_text = await self._query_supergrok_text(review_prompt)
        else:
            return None

        # Parse JSON
        try:
            if "```json" in review_text:
                review_text = review_text.split("```json")[1].split("```")[0]
            review_data = json.loads(review_text.strip())
        except:
            review_data = {"agreement_score": 0.5, "critique": review_text, "suggestions": []}

        return PeerReview(
            reviewer=reviewer_response.model_name,
            reviewed=reviewed_response.model_name,
            critique=review_data.get("critique", review_text),
            agreement_score=review_data.get("agreement_score", 0.5),
            suggestions=review_data.get("suggestions", []),
        )

    async def _claude_synthesis(
        self,
        user_message: str,
        claude_initial: ModelResponse,
        layer2_responses: list[ModelResponse],
        peer_reviews: list[PeerReview],
    ) -> dict[str, Any]:
        """Claude synthesizes everything into execution-ready answer"""

        # Build synthesis context
        context = []
        context.append(f"USER'S ORIGINAL MESSAGE:\n{user_message}\n")
        context.append(f"YOUR INITIAL ANALYSIS:\n{claude_initial.content}\n")
        context.append("\nOTHER MODELS' RESPONSES:")

        for resp in layer2_responses:
            context.append(f"\n{resp.model_name}:\n{resp.content}\n")

        if peer_reviews:
            context.append("\nPEER REVIEW FEEDBACK:")
            for review in peer_reviews:
                context.append(
                    f"\n{review.reviewer} reviewed {review.reviewed} "
                    f"(agreement: {review.agreement_score:.2f}):\n{review.critique}\n"
                )

        full_context = "\n".join(context)

        synthesis_prompt = f"""{full_context}

You are Claude Code. Your task is to synthesize all the above into a final, execution-ready response.

Instructions:
1. Identify consensus points across all models
2. Evaluate disagreements and choose the strongest position
3. Integrate peer review feedback
4. Provide a clear, actionable answer
5. If this involves code, provide ready-to-execute code
6. Flag any remaining uncertainties

Provide:
- FINAL ANSWER (comprehensive and execution-ready)
- KEY INSIGHTS (what the consensus revealed)
- CONFIDENCE LEVEL (high/medium/low with reasoning)
- RECOMMENDED NEXT STEPS (if applicable)

This is your final output - make it ready for immediate execution."""

        final_response = await self._query_claude(synthesis_prompt, is_initial=False)

        return {
            "final_answer": final_response.content,
            "explanations": [
                {"model": r.model_name, "content": r.content} for r in layer2_responses
            ],
            "peer_reviews": [
                {
                    "reviewer": r.reviewer,
                    "reviewed": r.reviewed,
                    "agreement": r.agreement_score,
                    "critique": r.critique,
                }
                for r in peer_reviews
            ],
            "execution_ready": True,
            "timestamp": datetime.utcnow().isoformat(),
        }

    # === Model-specific query methods ===

    async def _query_gemini(self, prompt: str) -> ModelResponse:
        """Query Gemini"""
        response = await asyncio.to_thread(self.gemini_model.generate_content, prompt)
        return ModelResponse(
            model_name="Gemini",
            content=response.text,
            timestamp=datetime.utcnow().isoformat(),
            token_usage={
                "input": getattr(response, "prompt_token_count", 0),
                "output": getattr(response, "candidates_token_count", 0),
            },
        )

    async def _query_gemini_text(self, prompt: str) -> str:
        """Query Gemini and return text only"""
        response = await self._query_gemini(prompt)
        return response.content

    async def _query_perplexity(self, prompt: str) -> ModelResponse:
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
            return ModelResponse(
                model_name="Perplexity",
                content=data["choices"][0]["message"]["content"],
                timestamp=datetime.utcnow().isoformat(),
                token_usage={
                    "input": data["usage"]["prompt_tokens"],
                    "output": data["usage"]["completion_tokens"],
                },
            )

    async def _query_perplexity_text(self, prompt: str) -> str:
        """Query Perplexity and return text only"""
        response = await self._query_perplexity(prompt)
        return response.content

    async def _query_supergrok(self, prompt: str) -> ModelResponse:
        """Query SuperGrok (xAI Grok 2)"""
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
            return ModelResponse(
                model_name="SuperGrok",
                content=data["choices"][0]["message"]["content"],
                timestamp=datetime.utcnow().isoformat(),
                token_usage={
                    "input": data["usage"]["prompt_tokens"],
                    "output": data["usage"]["completion_tokens"],
                },
            )

    async def _query_supergrok_text(self, prompt: str) -> str:
        """Query SuperGrok and return text only"""
        response = await self._query_supergrok(prompt)
        return response.content


# === CLI Interface ===


async def main():
    """Simple CLI for testing"""

    orchestrator = MessageConsensusOrchestrator()

    if len(sys.argv) > 1:
        # Message passed as argument
        user_message = " ".join(sys.argv[1:])
    else:
        # Interactive mode
        print("Message Consensus Orchestrator")
        print("Enter your message (or press Ctrl+C to exit):\n")
        user_message = input("> ").strip()

    if not user_message:
        print("No message provided.")
        return

    # Process through consensus
    result = await orchestrator.process_message(user_message)

    # Display result
    print(f"{'=' * 80}")
    print("FINAL ANSWER (Ready for Execution)")
    print(f"{'=' * 80}\n")
    print(result["final_answer"])
    print(f"\n{'=' * 80}")
    print(f"Models consulted: {len(result['explanations']) + 2}")  # +2 for Claude Layer 1 & 3
    print(f"Peer reviews: {len(result['peer_reviews'])}")
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
