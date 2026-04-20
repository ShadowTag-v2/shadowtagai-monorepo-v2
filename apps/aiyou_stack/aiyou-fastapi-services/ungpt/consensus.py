"""Multi-LLM Consensus System with Cross-Validation
Layer 1: Claude initial reasoning
Layer 2: Parallel analysis (Grok, Gemini, GPT-5)
Layer 2.5: Peer review cross-validation
Layer 3: Claude final synthesis
"""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import aiohttp


class ModelType(Enum):
    """Supported LLM models for consensus"""

    CLAUDE = "claude-sonnet-4-20250514"
    GROK = "grok-2-latest"
    GEMINI = "gemini-3.1-flash-lite-preview"
    GPT5 = "gpt-4-turbo-preview"  # Update when GPT-5 available


@dataclass
class ModelResponse:
    """Single model's response with metadata"""

    model: ModelType
    content: str
    reasoning: str
    confidence: float  # 0.0 - 1.0
    token_usage: dict[str, int]
    latency: float
    timestamp: str


@dataclass
class PeerReview:
    """Cross-validation review from one model about another's response"""

    reviewer_model: ModelType
    reviewed_model: ModelType
    critique: str
    agreement_score: float  # 0.0 - 1.0
    identified_issues: list[str]
    suggestions: list[str]


class ConsensusOrchestrator:
    """Multi-LLM consensus system with cross-validation

    Architecture:
    Query → Layer 1 (Claude) → Layer 2 (Broadcast to Grok/Gemini/GPT) →
    Layer 2.5 (Cross-validation) → Layer 3 (Claude synthesis)
    """

    def __init__(
        self,
        anthropic_client: Any,
        google_client: Any,
        openai_client: Any,
        xai_api_key: str,
        xai_endpoint: str = "https://api.x.ai/v1/chat/completions",
    ):
        self.anthropic_client = anthropic_client
        self.google_client = google_client
        self.openai_client = openai_client
        self.xai_api_key = xai_api_key
        self.xai_endpoint = xai_endpoint

    async def layer1_initial_reasoning(self, query: str) -> ModelResponse:
        """Layer 1: Claude Sonnet 4.5 initial reasoning pass
        This sets the framework that other models will analyze
        """
        prompt = f"""You are the initial reasoning layer in a multi-model consensus system.

QUERY: {query}

Your task is to:
1. Analyze the query thoroughly
2. Identify key sub-questions that need answering
3. Outline your initial reasoning approach
4. Provide a preliminary response with clear reasoning chains

Your response will be sent verbatim to 3 other advanced models (Grok, Gemini Pro, GPT-5) for independent analysis.

Be thorough but concise. Show your reasoning clearly.
"""

        start_time = asyncio.get_event_loop().time()

        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )

        latency = asyncio.get_event_loop().time() - start_time

        return ModelResponse(
            model=ModelType.CLAUDE,
            content=response.content[0].text,
            reasoning="Initial framework reasoning",
            confidence=0.85,
            token_usage={
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens,
            },
            latency=latency,
            timestamp=datetime.utcnow().isoformat(),
        )

    async def layer2_parallel_analysis(
        self,
        claude_response: str,
        original_query: str,
    ) -> list[ModelResponse]:
        """Layer 2: Broadcast Claude's response to 3 models for parallel analysis
        Each model analyzes independently without seeing others' work
        """
        base_prompt = f"""You are participating in a multi-model consensus system.

ORIGINAL QUERY:
{original_query}

CLAUDE SONNET 4.5's INITIAL ANALYSIS:
{claude_response}

Your task:
1. Independently analyze the original query
2. Evaluate Claude's reasoning (agree/disagree/extend)
3. Provide your own complete response
4. Rate your confidence (0.0-1.0)

Be thorough. Your response will be peer-reviewed by other advanced models.
"""

        # Execute all 3 models concurrently
        tasks = [
            self._query_grok(base_prompt),
            self._query_gemini(base_prompt),
            self._query_gpt5(base_prompt),
        ]

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out any exceptions
        valid_responses = [r for r in responses if isinstance(r, ModelResponse)]
        return valid_responses

    async def layer2_5_cross_validation(
        self,
        responses: list[ModelResponse],
    ) -> dict[ModelType, list[PeerReview]]:
        """Layer 2.5: Cross-validation - each model reviews the other two

        Returns:
            Dict mapping each model to reviews it received from peers

        """
        reviews = {}

        # For each model, get reviews from the other two
        for target_response in responses:
            peer_reviews = []

            for reviewer_response in responses:
                if reviewer_response.model == target_response.model:
                    continue  # Don't review yourself

                review = await self._get_peer_review(
                    reviewer=reviewer_response.model,
                    target_response=target_response,
                )
                peer_reviews.append(review)

            reviews[target_response.model] = peer_reviews

        return reviews

    async def _get_peer_review(
        self,
        reviewer: ModelType,
        target_response: ModelResponse,
    ) -> PeerReview:
        """Get one model to review another model's response"""
        review_prompt = f"""You are peer-reviewing another advanced AI model's response.

MODEL BEING REVIEWED: {target_response.model.value}

THEIR RESPONSE:
{target_response.content}

Provide a critical peer review:
1. What did they get right?
2. What concerns or errors do you identify?
3. What would you suggest they improve or reconsider?
4. Overall agreement score (0.0 = completely disagree, 1.0 = full agreement)

Return JSON:
{{
  "agreement_score": 0.85,
  "strengths": ["point 1", "point 2"],
  "concerns": ["issue 1", "issue 2"],
  "suggestions": ["suggestion 1", "suggestion 2"],
  "critique": "Your detailed critique here..."
}}
"""

        # Route to appropriate model
        if reviewer == ModelType.GROK:
            response_text = await self._query_grok_text(review_prompt)
        elif reviewer == ModelType.GEMINI:
            response_text = await self._query_gemini_text(review_prompt)
        elif reviewer == ModelType.GPT5:
            response_text = await self._query_gpt5_text(review_prompt)
        else:
            raise ValueError(f"Unknown reviewer: {reviewer}")

        # Parse JSON response
        try:
            # Extract JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                response_text = response_text[json_start:json_end]
            review_data = json.loads(response_text)
        except:
            # Fallback if JSON parsing fails
            review_data = {
                "agreement_score": 0.5,
                "strengths": [],
                "concerns": ["Failed to parse review"],
                "suggestions": [],
                "critique": response_text,
            }

        return PeerReview(
            reviewer_model=reviewer,
            reviewed_model=target_response.model,
            critique=review_data["critique"],
            agreement_score=review_data["agreement_score"],
            identified_issues=review_data.get("concerns", []),
            suggestions=review_data.get("suggestions", []),
        )

    async def layer3_final_synthesis(
        self,
        original_query: str,
        layer1_response: ModelResponse,
        layer2_responses: list[ModelResponse],
        peer_reviews: dict[ModelType, list[PeerReview]],
    ) -> dict[str, Any]:
        """Layer 3: Claude Sonnet 4.5 synthesizes all responses and peer reviews
        into final execution-ready output
        """
        # Build synthesis prompt
        synthesis_sections = []

        synthesis_sections.append(f"ORIGINAL QUERY:\n{original_query}\n")

        synthesis_sections.append(f"YOUR INITIAL REASONING (Layer 1):\n{layer1_response.content}\n")

        synthesis_sections.append("INDEPENDENT ANALYSES (Layer 2):")
        for resp in layer2_responses:
            synthesis_sections.append(f"\n{resp.model.value}:\n{resp.content}\n")

        synthesis_sections.append("PEER REVIEW CROSS-VALIDATION (Layer 2.5):")
        for model, reviews in peer_reviews.items():
            synthesis_sections.append(f"\n{model.value} received reviews:")
            for review in reviews:
                synthesis_sections.append(
                    f"  From {review.reviewer_model.value} "
                    f"(agreement: {review.agreement_score:.2f}):\n"
                    f"  {review.critique}\n",
                )

        full_context = "\n".join(synthesis_sections)

        synthesis_prompt = f"""You are the final synthesis layer in a multi-model consensus system.

{full_context}

Your task (Layer 3 - Final Synthesis):
1. Identify consensus points across all models
2. Identify disagreements and evaluate which position is strongest
3. Integrate peer review feedback to catch errors or blind spots
4. Synthesize into a single, high-confidence, execution-ready response
5. Flag any remaining uncertainties

Provide:
- EXECUTIVE SUMMARY (2-3 sentences)
- FINAL ANSWER (comprehensive, incorporating best elements from all models)
- CONFIDENCE ASSESSMENT (with reasoning)
- DISSENTING VIEWS (if any significant disagreements remain)
- RECOMMENDED ACTIONS (if applicable)

This is your final output - make it authoritative and actionable.
"""

        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            messages=[{"role": "user", "content": synthesis_prompt}],
        )

        return {
            "final_synthesis": response.content[0].text,
            "layer1_response": layer1_response,
            "layer2_responses": layer2_responses,
            "peer_reviews": peer_reviews,
            "token_usage": {
                "layer1": layer1_response.token_usage,
                "layer2": [r.token_usage for r in layer2_responses],
                "layer3": {
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens,
                },
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def execute_full_consensus(self, query: str) -> dict[str, Any]:
        """Execute full 3-layer consensus pipeline with cross-validation"""
        print("[Layer 1] Claude initial reasoning...")
        layer1 = await self.layer1_initial_reasoning(query)

        print("[Layer 2] Broadcasting to Grok, Gemini, GPT-5...")
        layer2 = await self.layer2_parallel_analysis(layer1.content, query)
        print(f"[Layer 2] Received {len(layer2)} responses")

        print("[Layer 2.5] Cross-validation peer reviews...")
        peer_reviews = await self.layer2_5_cross_validation(layer2)
        print(f"[Layer 2.5] Completed {sum(len(v) for v in peer_reviews.values())} peer reviews")

        print("[Layer 3] Final synthesis by Claude...")
        result = await self.layer3_final_synthesis(query, layer1, layer2, peer_reviews)

        print("[✓] Consensus complete")
        return result

    # Model-specific query methods

    async def _query_grok(self, prompt: str) -> ModelResponse:
        """Query Grok via xAI API"""
        start_time = asyncio.get_event_loop().time()

        async with (
            aiohttp.ClientSession() as session,
            session.post(
                self.xai_endpoint,
                headers={
                    "Authorization": f"Bearer {self.xai_api_key}",
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

            latency = asyncio.get_event_loop().time() - start_time

            return ModelResponse(
                model=ModelType.GROK,
                content=data["choices"][0]["message"]["content"],
                reasoning="Grok analysis",
                confidence=0.80,
                token_usage={
                    "input": data["usage"]["prompt_tokens"],
                    "output": data["usage"]["completion_tokens"],
                },
                latency=latency,
                timestamp=datetime.utcnow().isoformat(),
            )

    async def _query_grok_text(self, prompt: str) -> str:
        """Query Grok and return just text"""
        response = await self._query_grok(prompt)
        return response.content

    async def _query_gemini(self, prompt: str) -> ModelResponse:
        """Query Gemini 2.0"""
        start_time = asyncio.get_event_loop().time()

        response = await asyncio.to_thread(self.google_client.generate_content, prompt)

        latency = asyncio.get_event_loop().time() - start_time

        return ModelResponse(
            model=ModelType.GEMINI,
            content=response.text,
            reasoning="Gemini analysis",
            confidence=0.82,
            token_usage={
                "input": getattr(response, "prompt_token_count", 0),
                "output": getattr(response, "candidates_token_count", 0),
            },
            latency=latency,
            timestamp=datetime.utcnow().isoformat(),
        )

    async def _query_gemini_text(self, prompt: str) -> str:
        """Query Gemini and return just text"""
        response = await self._query_gemini(prompt)
        return response.content

    async def _query_gpt5(self, prompt: str) -> ModelResponse:
        """Query GPT-5 (or GPT-4 Turbo until GPT-5 available)"""
        start_time = asyncio.get_event_loop().time()

        response = await asyncio.to_thread(
            self.openai_client.chat.completions.create,
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        latency = asyncio.get_event_loop().time() - start_time

        return ModelResponse(
            model=ModelType.GPT5,
            content=response.choices[0].message.content,
            reasoning="GPT-5 analysis",
            confidence=0.83,
            token_usage={
                "input": response.usage.prompt_tokens,
                "output": response.usage.completion_tokens,
            },
            latency=latency,
            timestamp=datetime.utcnow().isoformat(),
        )

    async def _query_gpt5_text(self, prompt: str) -> str:
        """Query GPT-5 and return just text"""
        response = await self._query_gpt5(prompt)
        return response.content
