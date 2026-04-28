# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Landing Page Optimizer service implementation using Claude Agent SDK"""

import json
import re
from datetime import datetime
from typing import Any

from app.core.exceptions import AgentException
from app.core.settings import settings
from app.services.landing_page_optimizer.schemas import (
    CTAVariation,
    FocusArea,
    GenerateCTARequest,
    GenerateHeadlinesRequest,
    GenerateSocialProofRequest,
    HeadlineVariation,
    OptimizationAnalysis,
    OptimizePageRequest,
    Priority,
    Recommendation,
    SocialProofSuggestion,
)
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class LandingPageOptimizerService:
    """Service for optimizing landing pages using Claude Agent SDK

    This service acts as a conversion copywriting expert that:
    - Analyzes landing page content for conversion opportunities
    - Generates compelling headlines and CTAs
    - Provides social proof suggestions
    - Offers actionable optimization recommendations
    """

    SYSTEM_PROMPT = """You are a world-class conversion copywriting expert and landing page optimization specialist with deep expertise in:

- Conversion Rate Optimization (CRO) best practices
- Consumer psychology and persuasion principles
- A/B testing and data-driven optimization
- User experience (UX) and interface design
- Copywriting techniques that drive action
- Social proof and trust-building strategies
- Value proposition development
- Call-to-action optimization

Your role is to analyze landing pages and provide specific, actionable recommendations that will measurably improve conversion rates. Focus on:

1. Clear, compelling value propositions
2. Persuasive headlines that grab attention
3. Strong, action-oriented CTAs
4. Strategic use of social proof and trust signals
5. Reducing friction in the conversion funnel
6. Creating urgency without being pushy
7. Clarity and simplicity in messaging

Provide concrete examples and prioritize recommendations by expected impact on conversions."""

    def __init__(self, api_key: str | None = None):
        """Initialize the Landing Page Optimizer service

        Args:
            api_key: Anthropic API key (uses settings.ANTHROPIC_API_KEY if not provided)

        """
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not set - service will not function properly")

    async def optimize_page(self, request: OptimizePageRequest) -> OptimizationAnalysis:
        """Analyze and optimize a landing page

        Args:
            request: Optimization request with page content and parameters

        Returns:
            OptimizationAnalysis with detailed recommendations

        Raises:
            AgentException: If Claude Agent SDK encounters an error
            ValidationException: If request validation fails

        """
        try:
            start_time = datetime.now()
            logger.info(f"Starting landing page optimization - Focus: {request.focus_areas}")

            # Build the analysis prompt
            prompt = self._build_optimization_prompt(request)

            # Query Claude Agent SDK
            analysis_text = await self._query_claude(prompt)

            # Parse the response into structured format
            analysis = self._parse_optimization_response(analysis_text, request)

            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.info(f"Optimization completed in {processing_time:.2f}ms")

            return analysis

        except Exception as e:
            logger.exception(f"Error during landing page optimization: {e!s}")
            raise AgentException(
                message=f"Failed to optimize landing page: {e!s}",
                details={"request": request.model_dump()},
            ) from e

    async def generate_headlines(
        self,
        request: GenerateHeadlinesRequest,
    ) -> list[HeadlineVariation]:
        """Generate headline variations

        Args:
            request: Headline generation request

        Returns:
            List of headline variations

        """
        prompt = f"""Generate {request.count} compelling headline variations for a landing page.

Product/Service: {request.product_service}
Target Audience: {request.target_audience}
Key Benefit: {request.key_benefit}
Tone: {request.tone}

For each headline, provide:
1. The headline text
2. Reasoning for why it works
3. The target emotion it appeals to

Format your response as a JSON array of objects with fields: text, reasoning, target_emotion"""

        try:
            response_text = await self._query_claude(prompt)
            headlines = self._parse_json_response(response_text, list)

            return [
                HeadlineVariation(
                    text=h.get("text", ""),
                    reasoning=h.get("reasoning", ""),
                    target_emotion=h.get("target_emotion", ""),
                )
                for h in headlines[: request.count]
            ]
        except Exception as e:
            logger.exception(f"Error generating headlines: {e!s}")
            raise AgentException(f"Failed to generate headlines: {e!s}") from e

    async def generate_ctas(self, request: GenerateCTARequest) -> list[CTAVariation]:
        """Generate CTA variations

        Args:
            request: CTA generation request

        Returns:
            List of CTA variations

        """
        prompt = f"""Generate {request.count} compelling call-to-action (CTA) variations for a landing page.

Action Type: {request.action_type}
Product/Service: {request.product_service}
Urgency Level: {request.urgency_level}

For each CTA, provide:
1. The CTA button text
2. Suggested color (e.g., "primary-blue", "success-green", "urgent-red")
3. Suggested placement on page
4. Reasoning for why it works

Format your response as a JSON array of objects with fields: text, color_suggestion, placement, reasoning"""

        try:
            response_text = await self._query_claude(prompt)
            ctas = self._parse_json_response(response_text, list)

            return [
                CTAVariation(
                    text=c.get("text", ""),
                    color_suggestion=c.get("color_suggestion"),
                    placement=c.get("placement", ""),
                    reasoning=c.get("reasoning", ""),
                )
                for c in ctas[: request.count]
            ]
        except Exception as e:
            logger.exception(f"Error generating CTAs: {e!s}")
            raise AgentException(f"Failed to generate CTAs: {e!s}") from e

    async def generate_social_proof(
        self,
        request: GenerateSocialProofRequest,
    ) -> list[SocialProofSuggestion]:
        """Generate social proof suggestions

        Args:
            request: Social proof generation request

        Returns:
            List of social proof suggestions

        """
        prompt = f"""Generate social proof element suggestions for a landing page.

Product/Service: {request.product_service}
Existing Data: {json.dumps(request.existing_data) if request.existing_data else "None provided"}
Proof Types Requested: {", ".join(request.proof_types)}

For each suggestion, provide:
1. Type of social proof (testimonial, statistic, logo, trust_badge, etc.)
2. Suggested content
3. Where to place this element on the page

Format your response as a JSON array of objects with fields: type, content, placement"""

        try:
            response_text = await self._query_claude(prompt)
            suggestions = self._parse_json_response(response_text, list)

            return [
                SocialProofSuggestion(
                    type=s.get("type", ""),
                    content=s.get("content", ""),
                    placement=s.get("placement", ""),
                )
                for s in suggestions
            ]
        except Exception as e:
            logger.exception(f"Error generating social proof: {e!s}")
            raise AgentException(f"Failed to generate social proof: {e!s}") from e

    def _build_optimization_prompt(self, request: OptimizePageRequest) -> str:
        """Build the optimization prompt from request parameters"""
        focus_areas_str = ", ".join([area.value for area in request.focus_areas])

        prompt = f"""Analyze this landing page and provide a comprehensive optimization report.

LANDING PAGE CONTENT:
{request.page_content}

CONTEXT:
- Focus Areas: {focus_areas_str}
"""

        if request.current_conversion_rate is not None:
            prompt += f"- Current Conversion Rate: {request.current_conversion_rate}%\n"

        if request.target_conversion_rate is not None:
            prompt += f"- Target Conversion Rate: {request.target_conversion_rate}%\n"

        if request.target_audience:
            prompt += f"- Target Audience: {request.target_audience}\n"

        if request.product_service:
            prompt += f"- Product/Service: {request.product_service}\n"

        if request.page_url:
            prompt += f"- Page URL: {request.page_url}\n"

        prompt += """
Provide your analysis in the following JSON format:
{
    "overall_score": <number 0-100>,
    "key_strengths": [<list of strings>],
    "key_weaknesses": [<list of strings>],
    "recommendations": [
        {
            "title": "<string>",
            "description": "<string>",
            "category": "<headlines|cta|social_proof|copy|forms|layout|value_proposition|trust_signals|all>",
            "priority": "<high|medium|low>",
            "expected_impact": "<string>",
            "implementation_steps": [<list of strings>],
            "before_example": "<string or null>",
            "after_example": "<string or null>"
        }
    ],
    "headline_variations": [
        {
            "text": "<string>",
            "reasoning": "<string>",
            "target_emotion": "<string>"
        }
    ],
    "cta_variations": [
        {
            "text": "<string>",
            "color_suggestion": "<string or null>",
            "placement": "<string>",
            "reasoning": "<string>"
        }
    ],
    "social_proof_suggestions": [
        {
            "type": "<string>",
            "content": "<string>",
            "placement": "<string>"
        }
    ],
    "estimated_conversion_lift": "<string>"
}

Focus on providing specific, actionable recommendations that can be implemented immediately."""

        return prompt

    async def _query_claude(self, prompt: str) -> str:
        """Query Claude Agent SDK

        Args:
            prompt: User prompt

        Returns:
            Response text from Claude

        """
        try:
            # Import here to avoid circular dependencies and allow for lazy loading
            from anthropic import Anthropic

            client = Anthropic(api_key=self.api_key)

            message = client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE,
                system=self.SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract text from response
            response_text = ""
            for block in message.content:
                if hasattr(block, "text"):
                    response_text += block.text

            return response_text.strip()

        except Exception as e:
            logger.exception(f"Error querying Claude: {e!s}")
            raise AgentException(f"Failed to query Claude Agent: {e!s}") from e

    def _parse_optimization_response(
        self,
        response_text: str,
        request: OptimizePageRequest,
    ) -> OptimizationAnalysis:
        """Parse Claude's response into structured OptimizationAnalysis

        Args:
            response_text: Raw response from Claude
            request: Original request for context

        Returns:
            Structured OptimizationAnalysis

        """
        try:
            # Try to extract JSON from the response
            data = self._parse_json_response(response_text, dict)

            # Parse recommendations
            recommendations = [
                Recommendation(
                    title=rec.get("title", ""),
                    description=rec.get("description", ""),
                    category=FocusArea(rec.get("category", "all")),
                    priority=Priority(rec.get("priority", "medium")),
                    expected_impact=rec.get("expected_impact", ""),
                    implementation_steps=rec.get("implementation_steps", []),
                    before_example=rec.get("before_example"),
                    after_example=rec.get("after_example"),
                )
                for rec in data.get("recommendations", [])
            ]

            # Parse headline variations if present
            headline_variations = None
            if data.get("headline_variations"):
                headline_variations = [HeadlineVariation(**h) for h in data["headline_variations"]]

            # Parse CTA variations if present
            cta_variations = None
            if data.get("cta_variations"):
                cta_variations = [CTAVariation(**c) for c in data["cta_variations"]]

            # Parse social proof suggestions if present
            social_proof_suggestions = None
            if data.get("social_proof_suggestions"):
                social_proof_suggestions = [
                    SocialProofSuggestion(**s) for s in data["social_proof_suggestions"]
                ]

            return OptimizationAnalysis(
                overall_score=data.get("overall_score", 50.0),
                key_strengths=data.get("key_strengths", []),
                key_weaknesses=data.get("key_weaknesses", []),
                recommendations=recommendations,
                headline_variations=headline_variations,
                cta_variations=cta_variations,
                social_proof_suggestions=social_proof_suggestions,
                estimated_conversion_lift=data.get("estimated_conversion_lift"),
            )

        except Exception as e:
            logger.exception(f"Error parsing optimization response: {e!s}")
            # Return a basic analysis if parsing fails
            return OptimizationAnalysis(
                overall_score=50.0,
                key_strengths=["Unable to parse detailed analysis"],
                key_weaknesses=["Parsing error occurred"],
                recommendations=[
                    Recommendation(
                        title="Analysis Error",
                        description=f"Failed to parse analysis: {e!s}. Raw response available in logs.",
                        category=FocusArea.ALL,
                        priority=Priority.HIGH,
                        expected_impact="N/A",
                        implementation_steps=["Contact support with error details"],
                    ),
                ],
            )

    def _parse_json_response(self, response_text: str, expected_type: type) -> Any:
        """Extract and parse JSON from Claude's response

        Args:
            response_text: Raw response text that may contain JSON
            expected_type: Expected type (dict or list)

        Returns:
            Parsed JSON object

        """
        # Try to find JSON in markdown code blocks first
        json_match = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find raw JSON
            json_match = re.search(r"(\{.*\}|\[.*\])", response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                raise ValueError("No JSON found in response")

        try:
            data = json.loads(json_str)
            if not isinstance(data, expected_type):
                raise ValueError(f"Expected {expected_type.__name__}, got {type(data).__name__}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e!s}\nContent: {json_str[:500]}")
            raise ValueError(f"Invalid JSON in response: {e!s}") from e
