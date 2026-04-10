"""
Multi-LLM Consensus Orchestrator with Cross-Validation
=======================================================
Architecture: Claude → [Grok, Gemini, GPT-4] → Peer Review → Claude Synthesis

Army Doctrine Integration (v3.0.0):
- ATP 5-19: Risk-based consensus thresholds
- Dynamic agreement requirements based on residual risk level
- LOW=50%, MEDIUM=60%, HIGH=75%, EXTREMELY_HIGH=90%
"""

import asyncio
import json
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import aiohttp

# Army Doctrine Integration
try:
    from src.kosmos.doctrine import (
        RiskLevel as DoctrineRiskLevel,
    )
    from src.kosmos.doctrine import (
        RiskManager as DoctrineRiskManager,
    )
    from src.kosmos.doctrine.atp_5_19 import APPROVAL_AUTHORITY, CONSENSUS_THRESHOLDS

    DOCTRINE_AVAILABLE = True
except ImportError:
    DOCTRINE_AVAILABLE = False
    # Fallback consensus thresholds based on ATP 5-19
    CONSENSUS_THRESHOLDS = {"LOW": 0.50, "MEDIUM": 0.60, "HIGH": 0.75, "EXTREMELY_HIGH": 0.90}
    APPROVAL_AUTHORITY = {
        "LOW": "Team Lead",
        "MEDIUM": "Commander",
        "HIGH": "Executive",
        "EXTREMELY_HIGH": "Founder",
    }


class ModelType(Enum):
    """Supported LLM models"""

    CLAUDE = "claude-sonnet-4-20250514"
    GROK = "grok-2-latest"
    GEMINI = "gemini-2.0-flash-exp"
    GPT4 = "gpt-4-turbo-preview"


@dataclass
class ModelResponse:
    """Single model's response with metadata"""

    model: ModelType
    content: str
    reasoning: str
    confidence: float
    token_usage: dict[str, int]
    latency: float
    timestamp: str


@dataclass
class PeerReview:
    """Cross-validation review from one model about another's response"""

    reviewer_model: ModelType
    reviewed_model: ModelType
    critique: str
    agreement_score: float
    identified_issues: list[str]
    suggestions: list[str]


class ConsensusOrchestrator:
    """
    Multi-LLM consensus system with cross-validation and Army Doctrine Integration.

    Layer 1: Claude initial reasoning
    Layer 2: Parallel analysis (Grok, Gemini, GPT-4)
    Layer 2.5: Peer review cross-validation
    Layer 3: Claude final synthesis

    Army Doctrine Integration:
    - ATP 5-19: Dynamic consensus thresholds based on risk level
    - Agreement requirements: LOW=50%, MEDIUM=60%, HIGH=75%, EXTREMELY_HIGH=90%
    """

    def __init__(
        self,
        anthropic_api_key: str = None,
        google_api_key: str = None,
        openai_api_key: str = None,
        xai_api_key: str = None,
        session_id: str = None,
    ):
        # Session tracking
        self.session_id = session_id or datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        # Load from environment if not provided
        self.anthropic_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.google_key = google_api_key or os.environ.get("GOOGLE_API_KEY")
        self.openai_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        self.xai_key = xai_api_key or os.environ.get("XAI_API_KEY")

        # API endpoints
        self.anthropic_endpoint = "https://api.anthropic.com/v1/messages"
        self.xai_endpoint = "https://api.x.ai/v1/chat/completions"
        self.openai_endpoint = "https://api.openai.com/v1/chat/completions"

        # === Army Doctrine Integration (ATP 5-19) ===
        if DOCTRINE_AVAILABLE:
            self.risk_manager = DoctrineRiskManager(session_id=self.session_id)
            print(f"[DOCTRINE] ATP 5-19 consensus thresholds ENABLED (session: {self.session_id})")
        else:
            self.risk_manager = None
            print("[DOCTRINE] ATP 5-19 integration NOT AVAILABLE - using fallback thresholds")

        # Current risk state
        self.current_risk_level: str = "MEDIUM"
        self.consensus_threshold: float = CONSENSUS_THRESHOLDS.get("MEDIUM", 0.60)

        # Initialize Gemini
        try:
            import google.generativeai as genai

            if self.google_key:
                genai.configure(api_key=self.google_key)
                self.gemini_model = genai.GenerativeModel("gemini-2.0-flash-exp")
            else:
                self.gemini_model = None
        except ImportError:
            print("[WARNING] google-generativeai not installed. Gemini disabled.")
            self.gemini_model = None

    async def layer1_initial_reasoning(self, query: str) -> ModelResponse:
        """Layer 1: Claude Sonnet 4.5 initial reasoning pass"""
        prompt = f"""You are the initial reasoning layer in a multi-model consensus system.

QUERY: {query}

Your task is to:
1. Analyze the query thoroughly
2. Identify key sub-questions that need answering
3. Outline your initial reasoning approach
4. Provide a preliminary response with clear reasoning chains

Your response will be sent verbatim to 3 other advanced models (Grok, Gemini Pro, GPT-4) for independent analysis.

Be thorough but concise. Show your reasoning clearly."""

        start_time = asyncio.get_event_loop().time()

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
            latency = asyncio.get_event_loop().time() - start_time

            return ModelResponse(
                model=ModelType.CLAUDE,
                content=data["content"][0]["text"],
                reasoning="Initial framework reasoning",
                confidence=0.85,
                token_usage={
                    "input": data["usage"]["input_tokens"],
                    "output": data["usage"]["output_tokens"],
                },
                latency=latency,
                timestamp=datetime.utcnow().isoformat(),
            )

    async def layer2_parallel_analysis(
        self, claude_response: str, original_query: str
    ) -> list[ModelResponse]:
        """Layer 2: Broadcast Claude's response to 3 models for parallel analysis"""
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

Be thorough. Your response will be peer-reviewed by other advanced models."""

        # Execute all 3 models concurrently
        tasks = []

        if self.xai_key:
            tasks.append(self._query_grok(base_prompt))
        if self.gemini_model:
            tasks.append(self._query_gemini(base_prompt))
        if self.openai_key:
            tasks.append(self._query_gpt4(base_prompt))

        if not tasks:
            print("[WARNING] No Layer 2 models configured. Using only Claude.")
            return []

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        valid_responses = [r for r in responses if isinstance(r, ModelResponse)]
        return valid_responses

    async def layer2_5_cross_validation(
        self, responses: list[ModelResponse]
    ) -> dict[ModelType, list[PeerReview]]:
        """Layer 2.5: Cross-validation - each model reviews the other two"""
        reviews = {}

        for target_response in responses:
            peer_reviews = []
            for reviewer_response in responses:
                if reviewer_response.model == target_response.model:
                    continue  # Don't review yourself

                review = await self._get_peer_review(
                    reviewer=reviewer_response.model, target_response=target_response
                )
                peer_reviews.append(review)

            reviews[target_response.model] = peer_reviews

        return reviews

    async def _get_peer_review(
        self, reviewer: ModelType, target_response: ModelResponse
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
}}"""

        # Route to appropriate model
        if reviewer == ModelType.GROK:
            response_text = await self._query_grok_text(review_prompt)
        elif reviewer == ModelType.GEMINI:
            response_text = await self._query_gemini_text(review_prompt)
        elif reviewer == ModelType.GPT4:
            response_text = await self._query_gpt4_text(review_prompt)
        else:
            raise ValueError(f"Unknown reviewer: {reviewer}")

        # Parse JSON response
        try:
            # Clean up markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            review_data = json.loads(response_text.strip())
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
            critique=review_data.get("critique", response_text),
            agreement_score=review_data.get("agreement_score", 0.5),
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
        """Layer 3: Claude Sonnet 4.5 synthesizes all responses and peer reviews"""
        # Build synthesis prompt
        synthesis_sections = []
        synthesis_sections.append(f"ORIGINAL QUERY:\n{original_query}\n")
        synthesis_sections.append(f"YOUR INITIAL REASONING (Layer 1):\n{layer1_response.content}\n")

        if layer2_responses:
            synthesis_sections.append("INDEPENDENT ANALYSES (Layer 2):")
            for resp in layer2_responses:
                synthesis_sections.append(f"\n{resp.model.value}:\n{resp.content}\n")

        if peer_reviews:
            synthesis_sections.append("PEER REVIEW CROSS-VALIDATION (Layer 2.5):")
            for model, reviews in peer_reviews.items():
                synthesis_sections.append(f"\n{model.value} received reviews:")
                for review in reviews:
                    synthesis_sections.append(
                        f"  From {review.reviewer_model.value} "
                        f"(agreement: {review.agreement_score:.2f}):\n"
                        f"  {review.critique}\n"
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

This is your final output - make it authoritative and actionable."""

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
                    "messages": [{"role": "user", "content": synthesis_prompt}],
                },
            ) as response,
        ):
            data = await response.json()

            return {
                "final_synthesis": data["content"][0]["text"],
                "layer1_response": layer1_response,
                "layer2_responses": layer2_responses,
                "peer_reviews": peer_reviews,
                "token_usage": {
                    "layer1": layer1_response.token_usage,
                    "layer2": [r.token_usage for r in layer2_responses],
                    "layer3": {
                        "input": data["usage"]["input_tokens"],
                        "output": data["usage"]["output_tokens"],
                    },
                },
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def execute_full_consensus(self, query: str) -> dict[str, Any]:
        """Execute full 3-layer consensus pipeline with cross-validation"""
        print("[Layer 1] Claude initial reasoning...")
        layer1 = await self.layer1_initial_reasoning(query)

        print("[Layer 2] Broadcasting to available models...")
        layer2 = await self.layer2_parallel_analysis(layer1.content, query)
        print(f"[Layer 2] Received {len(layer2)} responses")

        if layer2:
            print("[Layer 2.5] Cross-validation peer reviews...")
            peer_reviews = await self.layer2_5_cross_validation(layer2)
            print(
                f"[Layer 2.5] Completed {sum(len(v) for v in peer_reviews.values())} peer reviews"
            )
        else:
            peer_reviews = {}
            print("[Layer 2.5] Skipped (no Layer 2 responses)")

        print("[Layer 3] Final synthesis by Claude...")
        result = await self.layer3_final_synthesis(query, layer1, layer2, peer_reviews)
        print("[✓] Consensus complete")

        return result

    # === Model-specific query methods ===

    async def _query_grok(self, prompt: str) -> ModelResponse:
        """Query Grok via xAI API"""
        start_time = asyncio.get_event_loop().time()

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

        response = await asyncio.to_thread(self.gemini_model.generate_content, prompt)

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

    async def _query_gpt4(self, prompt: str) -> ModelResponse:
        """Query GPT-4 Turbo via OpenAI API"""
        start_time = asyncio.get_event_loop().time()

        async with (
            aiohttp.ClientSession() as session,
            session.post(
                self.openai_endpoint,
                headers={
                    "Authorization": f"Bearer {self.openai_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4-turbo-preview",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                },
            ) as response,
        ):
            data = await response.json()
            latency = asyncio.get_event_loop().time() - start_time

            return ModelResponse(
                model=ModelType.GPT4,
                content=data["choices"][0]["message"]["content"],
                reasoning="GPT-4 analysis",
                confidence=0.83,
                token_usage={
                    "input": data["usage"]["prompt_tokens"],
                    "output": data["usage"]["completion_tokens"],
                },
                latency=latency,
                timestamp=datetime.utcnow().isoformat(),
            )

    async def _query_gpt4_text(self, prompt: str) -> str:
        """Query GPT-4 and return just text"""
        response = await self._query_gpt4(prompt)
        return response.content

    # =========================================================================
    # Army Doctrine Integration Methods (ATP 5-19)
    # =========================================================================

    async def assess_risk_and_set_threshold(self, query: str) -> dict[str, Any]:
        """
        Assess query risk using ATP 5-19 and set consensus threshold.

        Risk levels and thresholds:
        - LOW: 50% consensus required
        - MEDIUM: 60% consensus required
        - HIGH: 75% consensus required
        - EXTREMELY_HIGH: 90% consensus required

        Returns:
            Dict with risk_level, consensus_threshold, and approval_authority
        """
        if DOCTRINE_AVAILABLE and self.risk_manager:
            try:
                risk_result = await self.risk_manager.full_assessment(query)
                residual_risk = risk_result.get("residual_risk", "MEDIUM")
                self.current_risk_level = residual_risk
                self.consensus_threshold = CONSENSUS_THRESHOLDS.get(residual_risk, 0.60)

                return {
                    "risk_level": residual_risk,
                    "consensus_threshold": self.consensus_threshold,
                    "approval_authority": APPROVAL_AUTHORITY.get(residual_risk, "Commander"),
                    "crm_assessment": risk_result,
                    "session_id": self.session_id,
                }
            except Exception as e:
                print(f"[WARNING] Doctrine risk assessment failed: {e}")

        # Fallback to default
        self.current_risk_level = "MEDIUM"
        self.consensus_threshold = CONSENSUS_THRESHOLDS.get("MEDIUM", 0.60)

        return {
            "risk_level": "MEDIUM",
            "consensus_threshold": self.consensus_threshold,
            "approval_authority": APPROVAL_AUTHORITY.get("MEDIUM", "Commander"),
            "session_id": self.session_id,
        }

    def check_consensus_reached(
        self, peer_reviews: dict[ModelType, list[PeerReview]]
    ) -> dict[str, Any]:
        """
        Check if consensus threshold is met based on ATP 5-19 risk level.

        Args:
            peer_reviews: Dictionary of peer reviews from Layer 2.5

        Returns:
            Dict with consensus_reached, average_agreement, and threshold_used
        """
        if not peer_reviews:
            return {
                "consensus_reached": False,
                "average_agreement": 0.0,
                "threshold_used": self.consensus_threshold,
                "reason": "No peer reviews available",
            }

        # Calculate average agreement score
        all_scores = []
        for model_reviews in peer_reviews.values():
            for review in model_reviews:
                all_scores.append(review.agreement_score)

        if not all_scores:
            return {
                "consensus_reached": False,
                "average_agreement": 0.0,
                "threshold_used": self.consensus_threshold,
                "reason": "No agreement scores found",
            }

        average_agreement = sum(all_scores) / len(all_scores)
        consensus_reached = average_agreement >= self.consensus_threshold

        return {
            "consensus_reached": consensus_reached,
            "average_agreement": average_agreement,
            "threshold_used": self.consensus_threshold,
            "risk_level": self.current_risk_level,
            "approval_authority": APPROVAL_AUTHORITY.get(self.current_risk_level, "Commander"),
            "total_reviews": len(all_scores),
            "reason": "Threshold met"
            if consensus_reached
            else f"Agreement {average_agreement:.0%} below {self.consensus_threshold:.0%} threshold",
        }

    async def execute_full_consensus_with_doctrine(self, query: str) -> dict[str, Any]:
        """
        Execute full consensus pipeline with ATP 5-19 risk-based thresholds.

        Enhanced version that includes:
        1. Pre-assessment risk evaluation
        2. Dynamic consensus threshold
        3. Consensus validation check
        """
        print("[DOCTRINE] Assessing query risk using ATP 5-19...")
        risk_assessment = await self.assess_risk_and_set_threshold(query)
        print(
            f"[DOCTRINE] Risk: {risk_assessment['risk_level']} → Consensus threshold: {self.consensus_threshold:.0%}"
        )

        # Execute standard consensus pipeline
        result = await self.execute_full_consensus(query)

        # Check if consensus was reached
        consensus_check = self.check_consensus_reached(result.get("peer_reviews", {}))
        result["doctrine"] = {
            "risk_assessment": risk_assessment,
            "consensus_check": consensus_check,
            "session_id": self.session_id,
        }

        if not consensus_check["consensus_reached"]:
            print(f"[DOCTRINE WARNING] Consensus NOT reached: {consensus_check['reason']}")
            print(f"[DOCTRINE WARNING] Requires {consensus_check['approval_authority']} approval")

        return result

    def get_doctrine_status(self) -> dict[str, Any]:
        """Get Army Doctrine integration status."""
        return {
            "available": DOCTRINE_AVAILABLE,
            "session_id": self.session_id,
            "current_risk_level": self.current_risk_level,
            "current_consensus_threshold": self.consensus_threshold,
            "thresholds_reference": CONSENSUS_THRESHOLDS,
            "approval_authorities": APPROVAL_AUTHORITY,
            "risk_manager_active": self.risk_manager is not None,
        }


# === CLI for testing ===


async def main():
    """Example usage"""
    orchestrator = ConsensusOrchestrator()

    query = """
    Analyze the business viability of deploying ground-mounted GPU compute
    infrastructure at cell tower sites for edge AI workloads. Consider:
    1) Technical feasibility and power requirements
    2) Partnership models with telecom carriers
    3) Competitive positioning vs cloud hyperscalers
    4) Revenue projections for 5-year horizon
    """

    result = await orchestrator.execute_full_consensus(query)

    print("\n" + "=" * 80)
    print("FINAL SYNTHESIS:")
    print("=" * 80)
    print(result["final_synthesis"])

    print("\n" + "=" * 80)
    print("META-ANALYSIS:")
    print("=" * 80)
    print(f"Total Tokens Used: {json.dumps(result['token_usage'], indent=2)}")
    print(
        f"Models Consulted: {len(result['layer2_responses']) + 2}"
    )  # +2 for Layer 1 and Layer 3 Claude
    if result["peer_reviews"]:
        print(f"Peer Reviews Conducted: {sum(len(v) for v in result['peer_reviews'].values())}")


if __name__ == "__main__":
    asyncio.run(main())
