# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Policy enforcement agent using Google ADK and Gemini.

Implements real governance decisions with RAG-based policy retrieval,
structured output, and comprehensive reasoning traces.
"""

import json
import uuid
from typing import Any

import vertexai
from vertexai.generative_models import (
    Content,
    GenerationConfig,
    GenerativeModel,
    Part,
)

from src.agents.base import (
    BaseGovernanceAgent,
    DecisionStatus,
    GovernanceDecision,
    PolicyReference,
    RiskLevel,
)
from src.gov_config import settings


class PolicyEnforcementAgent(BaseGovernanceAgent):
    """Primary governance agent for policy enforcement.

    Uses Gemini 2.0 with function calling for structured decisions,
    RAG for policy retrieval, and comprehensive audit trails.
    """

    def __init__(
        self,
        agent_id: str = "policy-enforcer-01",
        name: str = "Primary Policy Enforcement Agent",
        model: str = None,
        policy_retriever: Any = None,
    ):
        model = model or settings.default_model.value
        super().__init__(
            agent_id=agent_id,
            name=name,
            model=model,
            temperature=settings.temperature,
            max_input_tokens=settings.max_input_tokens,
            max_output_tokens=settings.max_output_tokens,
        )

        # Initialize Vertex AI
        vertexai.init(
            project=settings.gcp_project_id,
            location=settings.gcp_location,
        )

        # Initialize model
        self.gemini = GenerativeModel(
            model_name=self.model,
            generation_config=GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_output_tokens,
                response_mime_type="application/json",
            ),
        )

        # Policy retriever (injected dependency)
        self.policy_retriever = policy_retriever

        # System instruction
        self.system_instruction = """You are a governance enforcement agent responsible for making policy-based decisions.

Your role:
1. Analyze the request against organizational policies
2. Provide structured decisions with clear reasoning
3. Cite specific policy sections that support your decision
4. Assess risk levels using ATP 5-19 framework
5. Escalate when confidence is low or risk is high

Output Format (JSON):
{
  "decision": "APPROVED" | "DENIED" | "ESCALATED",
  "confidence_score": 0.0-1.0,
  "risk_level": "EH" | "H" | "M" | "L",
  "reasoning_steps": ["step 1", "step 2", ...],
  "policy_references": [
    {
      "policy_id": "POL-001",
      "section": "2.3",
      "clause": "Access Control",
      "confidence": 0.95
    }
  ],
  "evidence": ["quote from policy", ...],
  "escalation_needed": true/false,
  "escalation_reason": "explanation if needed"
}

Risk Assessment (ATP 5-19):
- Probability: A (freq), B (likely), C (may), D (seldom), E (unlikely)
- Severity: I (catastrophic), II (critical), III (moderate), IV (negligible)
- Matrix lookup for risk level (EH/H/M/L)

Guidelines:
- Be conservative: when in doubt, escalate
- Always cite specific policy sections
- Provide clear reasoning for auditors
- Consider precedents and context
- Never hallucinate policies - only use provided context"""

    async def get_policy_context(self, request: dict[str, Any]) -> list[str]:
        """Retrieve relevant policy context using RAG.

        Args:
            request: Governance request

        Returns:
            List of policy document snippets

        """
        if not self.policy_retriever:
            return ["No policy retriever configured - using default policies"]

        # Build query from request
        query = self._build_policy_query(request)

        # Retrieve relevant policies
        policy_chunks = await self.policy_retriever.retrieve(
            query=query,
            top_k=settings.retrieval_top_k,
        )

        return policy_chunks

    def _build_policy_query(self, request: dict[str, Any]) -> str:
        """Build semantic query for policy retrieval."""
        action = request.get("action", "")
        resource = request.get("resource", "")
        user_context = request.get("user_context", {})

        query_parts = [
            f"Action: {action}",
            f"Resource: {resource}",
        ]

        if user_context:
            role = user_context.get("role", "")
            department = user_context.get("department", "")
            if role:
                query_parts.append(f"User role: {role}")
            if department:
                query_parts.append(f"Department: {department}")

        return " | ".join(query_parts)

    async def evaluate(
        self,
        request: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> GovernanceDecision:
        """Evaluate governance request using Gemini with RAG policy context.

        Args:
            request: Governance request {action, resource, user_context}
            context: Additional context (trust_score, historical_violations, etc.)

        Returns:
            Structured governance decision

        """
        # Validate request
        self.validate_request(request)

        # Generate decision ID
        decision_id = f"dec_{uuid.uuid4().hex[:12]}"

        try:
            # Retrieve policy context
            policy_context = await self.get_policy_context(request)

            # Build prompt
            prompt = self._build_prompt(request, policy_context, context)

            # Call Gemini
            response = await self._call_gemini(prompt)

            # Parse structured response
            decision_data = self._parse_response(response)

            # Build decision object
            decision = GovernanceDecision(
                decision_id=decision_id,
                status=DecisionStatus(decision_data.get("decision", "ESCALATED")),
                confidence_score=decision_data.get("confidence_score", 0.0),
                risk_level=RiskLevel(decision_data.get("risk_level", "H")),
                reasoning_trace=decision_data.get("reasoning_steps", []),
                policy_references=self._parse_policy_refs(
                    decision_data.get("policy_references", []),
                ),
                evidence_snippets=decision_data.get("evidence", []),
                user_id=request.get("user_context", {}).get("user_id"),
                resource_id=request.get("resource", {}).get("id"),
                action_type=request.get("action", ""),
                requires_escalation=decision_data.get("escalation_needed", False),
                escalation_reason=decision_data.get("escalation_reason"),
                trust_score=context.get("trust_score") if context else None,
                metrics=self.get_metrics(),
            )

            # Apply guardrails
            decision = await self._apply_guardrails(decision)

            return decision

        except Exception as e:
            # Error handling with fallback decision
            return GovernanceDecision(
                decision_id=decision_id,
                status=DecisionStatus.ERROR,
                confidence_score=0.0,
                reasoning_trace=[f"Error during evaluation: {e!s}"],
                requires_escalation=True,
                escalation_reason=f"System error: {e!s}",
                action_type=request.get("action", ""),
                metrics=self.get_metrics(),
            )

    def _build_prompt(
        self,
        request: dict[str, Any],
        policy_context: list[str],
        context: dict[str, Any] | None,
    ) -> str:
        """Build comprehensive prompt for Gemini."""
        prompt_parts = [
            "# GOVERNANCE REQUEST EVALUATION\n",
            "## Request Details",
            f"Action: {request.get('action', 'N/A')}",
            f"Resource: {json.dumps(request.get('resource', {}), indent=2)}",
            f"User Context: {json.dumps(request.get('user_context', {}), indent=2)}",
            "\n## Relevant Policies",
        ]

        # Add policy context
        for i, policy in enumerate(policy_context, 1):
            prompt_parts.append(f"\n### Policy Snippet {i}")
            prompt_parts.append(policy)

        # Add additional context if provided
        if context:
            prompt_parts.append("\n## Additional Context")
            if "trust_score" in context:
                prompt_parts.append(f"Trust Score: {context['trust_score']:.2f}")
            if "historical_violations" in context:
                prompt_parts.append(f"Historical Violations: {context['historical_violations']}")
            if "precedents" in context:
                prompt_parts.append(f"Precedents: {json.dumps(context['precedents'])}")

        prompt_parts.append(
            "\n## Task\nEvaluate this request against the policies and provide a structured JSON decision.",
        )

        return "\n".join(prompt_parts)

    async def _call_gemini(self, prompt: str) -> str:
        """Call Gemini model and track metrics."""
        import time

        start = time.time()

        # Build content
        contents = [
            Content(
                role="user",
                parts=[Part.from_text(self.system_instruction + "\n\n" + prompt)],
            ),
        ]

        # Generate
        response = self.gemini.generate_content(
            contents,
            stream=False,
        )

        # Track TTFT if streaming (not implemented in this version)
        self.metrics.ttft_ms = int((time.time() - start) * 1000)

        # Extract metrics from response
        if hasattr(response, "usage_metadata"):
            metadata = response.usage_metadata
            self.metrics.input_tokens = getattr(metadata, "prompt_token_count", 0)
            self.metrics.output_tokens = getattr(metadata, "candidates_token_count", 0)
            self.metrics.cached_tokens = getattr(metadata, "cached_content_token_count", 0)
            self.metrics.cache_hit = self.metrics.cached_tokens > 0

        # Calculate cost
        cost, savings = await self._calculate_cost(
            self.metrics.input_tokens,
            self.metrics.output_tokens,
            self.metrics.cached_tokens,
        )
        self.metrics.cost_usd = cost
        self.metrics.cached_savings_usd = savings

        return response.text

    def _parse_response(self, response_text: str) -> dict[str, Any]:
        """Parse JSON response from Gemini."""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback parsing
            return {
                "decision": "ESCALATED",
                "confidence_score": 0.0,
                "risk_level": "H",
                "reasoning_steps": ["Failed to parse model response"],
                "escalation_needed": True,
                "escalation_reason": "Invalid response format",
            }

    def _parse_policy_refs(self, refs_data: list[dict]) -> list[PolicyReference]:
        """Parse policy references from response."""
        refs = []
        for ref in refs_data:
            try:
                refs.append(PolicyReference(**ref))
            except Exception:
                continue
        return refs
