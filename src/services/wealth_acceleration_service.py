# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Wealth Acceleration Service - FastAPI Integration

This service provides FastAPI endpoints for the wealth acceleration strategist agent,
enabling RESTful API access to monetization analysis and strategic recommendations.

Version: 1.0.0
Last Updated: 2025-11-08
"""

from typing import List, Optional
from collections.abc import AsyncIterator
from pydantic import BaseModel, Field
from enum import Enum
from claude_agent_sdk import query, ClaudeAgentOptions


class EngagementLevel(str, Enum):
    """Audience engagement level"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class MarketPosition(str, Enum):
    """Market positioning strategy"""

    BUDGET = "budget"
    MID_MARKET = "mid-market"
    PREMIUM = "premium"
    LUXURY = "luxury"


class BusinessContext(BaseModel):
    """Business context for analysis"""

    niche: str | None = Field(None, description="Primary niche or industry")
    current_monthly_revenue: float | None = Field(None, description="Current monthly revenue in dollars")
    audience_size: int | None = Field(None, description="Total audience size across all platforms")
    engagement_level: EngagementLevel | None = Field(None, description="Audience engagement level")
    revenue_streams: list[str] | None = Field(None, description="Existing revenue streams")
    platforms: list[str] | None = Field(None, description="Content platforms being used")
    additional_context: str | None = Field(None, description="Any additional relevant context")


class OfferInfo(BaseModel):
    """Information about a specific offer"""

    name: str = Field(..., description="Name of the offer")
    price: float = Field(..., description="Price of the offer")
    monthly_sales: int | None = Field(None, description="Average monthly sales")


class FunnelStage(BaseModel):
    """Funnel stage data"""

    name: str = Field(..., description="Stage name")
    visitors: int = Field(..., description="Number of visitors")
    conversions: int | None = Field(None, description="Number of conversions to next stage")
    revenue: float | None = Field(None, description="Revenue generated at this stage")


class AnalysisRequest(BaseModel):
    """Base request for analysis"""

    business_context: BusinessContext | None = Field(None, description="Business context for the analysis")
    prompt: str = Field(..., description="Specific query or request")


class MonetizationStrategyRequest(BaseModel):
    """Request for complete monetization strategy analysis"""

    business_context: BusinessContext
    focus_areas: list[str] | None = Field(
        None,
        description="Specific focus areas (e.g., 'pricing', 'conversion', 'LTV')",
    )


class FunnelAnalysisRequest(BaseModel):
    """Request for funnel analysis"""

    business_context: BusinessContext | None = None
    funnel_stages: list[FunnelStage] = Field(..., description="List of funnel stages with metrics")


class PricingEvaluationRequest(BaseModel):
    """Request for pricing strategy evaluation"""

    business_context: BusinessContext | None = None
    product_type: str = Field(..., description="Type of product or service")
    current_price: float = Field(..., description="Current price")
    cost_to_deliver: float = Field(..., description="Cost to deliver")
    monthly_customers: int = Field(..., description="Monthly customer volume")
    market_position: MarketPosition = Field(..., description="Target market positioning")


class RevenueProjectionRequest(BaseModel):
    """Request for revenue projections"""

    business_context: BusinessContext | None = None
    current_monthly_revenue: float
    current_audience_size: int
    monthly_audience_growth: float = Field(..., description="Monthly audience growth rate as percentage")
    current_conversion_rate: float = Field(..., description="Current conversion rate as percentage")
    projection_months: int = Field(12, description="Number of months to project")


class LTVCalculationRequest(BaseModel):
    """Request for LTV calculation"""

    business_context: BusinessContext | None = None
    average_order_value: float
    purchase_frequency: float = Field(..., description="Average purchases per year")
    customer_lifespan: float = Field(..., description="Average customer lifespan in years")
    gross_margin: float = Field(..., description="Gross margin percentage (0-100)")


class OpportunityAssessmentRequest(BaseModel):
    """Request for market opportunity assessment"""

    niche: str
    audience_size: int
    engagement: EngagementLevel
    current_revenue: float
    potential_revenue_streams: list[str] = Field(
        ...,
        description="List of potential revenue streams to evaluate",
    )


# Wealth Acceleration Agent Prompt
WEALTH_ACCELERATION_PROMPT = """
<agent_configuration>
  <metadata>
    <agent_name>Wealth Acceleration Strategist</agent_name>
    <version>1.0.0</version>
    <claude_model>claude-sonnet-4.5-20250514</claude_model>
    <last_updated>2025-11-08</last_updated>
  </metadata>

  <role>
You are my personal wealth acceleration strategist, obsessed with turning attention into income at scale.

Here's who you are:

- You operate with razor-sharp market intelligence and spot money-making opportunities others miss entirely
- You've generated millions in revenue across digital products, content monetization, and automated income systems
- You understand the attention economy, viral mechanics, and conversion psychology at a master level
- You don't waste time on theory—you deliver brutal honesty and actionable paths to profit
- You think in leverage and scalability—if it doesn't multiply income without multiplying effort, you reject it
- You see cash flow opportunities in every audience, platform, and piece of content
- You approach every problem with McKinsey-level strategic rigor and Sequoia-style boardroom precision
  </role>

  <execution_philosophy>
Your responsibilities in every response:

1. THE HARD TRUTH: What's costing money right now (brutal, specific)
2. EXECUTIVE SUMMARY: What needs to happen and why (McKinsey/Sequoia style)
3. DETAILED STRATEGY: Complete monetization architecture with implementation steps
4. IMMEDIATE CHALLENGE: Specific action to take today that generates income

Communication Style:
- Zero fluff, maximum signal-to-noise ratio
- Quantified wherever possible (specific dollar amounts, percentages, timelines)
- Structured for scannability and immediate action
- Brutal honesty about what's working and what's not
  </execution_philosophy>

  <quality_standards>
Every output must be:
- ACTIONABLE: Specific, implementable steps (not vague advice)
- QUANTIFIED: Numbers, metrics, projections (not hand-waving)
- STRATEGIC: Tied to broader monetization architecture (not random tactics)
- SCALABLE: Multiplies income without multiplying effort proportionally
- VALIDATED: Based on proven frameworks and market evidence
  </quality_standards>
</agent_configuration>

<mission>
Your mission is to engineer the user's current operation into a high-converting wealth generation machine—taking their content, audience, and offers and turning them into predictable, scalable revenue streams.

The goal: turn attention into a self-scaling income engine where revenue grows faster than audience does.
</mission>
"""


class WealthAccelerationService:
    """
    Service class for wealth acceleration analysis using Claude Agent SDK
    """

    def __init__(self, api_key: str | None = None):
        """
        Initialize the wealth acceleration service

        Args:
            api_key: Optional Anthropic API key (can also use environment variable)
        """
        self.api_key = api_key
        self.model = "claude-sonnet-4.5-20250514"

    def _format_business_context(self, context: BusinessContext | None) -> str:
        """Format business context as a prompt addition"""
        if not context:
            return ""

        parts = ["<business_context>"]

        if context.niche:
            parts.append(f"Niche: {context.niche}")

        if context.current_monthly_revenue is not None:
            parts.append(f"Current Monthly Revenue: ${context.current_monthly_revenue:,.2f}")

        if context.audience_size:
            parts.append(f"Total Audience Size: {context.audience_size:,}")

        if context.engagement_level:
            parts.append(f"Engagement Level: {context.engagement_level}")

        if context.revenue_streams:
            parts.append(f"Current Revenue Streams: {', '.join(context.revenue_streams)}")

        if context.platforms:
            parts.append(f"Platforms: {', '.join(context.platforms)}")

        if context.additional_context:
            parts.append(f"\nAdditional Context:\n{context.additional_context}")

        parts.append("</business_context>")

        return "\n".join(parts)

    async def analyze(
        self,
        user_prompt: str,
        business_context: BusinessContext | None = None,
        stream: bool = True,
    ) -> AsyncIterator[str]:
        """
        Run analysis with the wealth acceleration agent

        Args:
            user_prompt: The user's query or request
            business_context: Optional business context
            stream: Whether to stream the response

        Yields:
            Response chunks from the agent
        """
        contextual_prompt = user_prompt
        if business_context:
            context_str = self._format_business_context(business_context)
            contextual_prompt = f"{context_str}\n\n{user_prompt}"

        options = ClaudeAgentOptions(
            system_prompt=WEALTH_ACCELERATION_PROMPT,
            model=self.model,
            max_tokens=8000,
            temperature=1.0,
        )

        if self.api_key:
            options.api_key = self.api_key

        async for message in query(prompt=contextual_prompt, options=options):
            # Handle different message types
            if isinstance(message, str):
                yield message
            elif hasattr(message, "text"):
                yield message.text
            elif hasattr(message, "content"):
                yield str(message.content)

    async def analyze_monetization_strategy(self, request: MonetizationStrategyRequest) -> AsyncIterator[str]:
        """
        Analyze complete monetization strategy

        Args:
            request: Monetization strategy analysis request

        Yields:
            Analysis results
        """
        focus = ""
        if request.focus_areas:
            focus = f"\nFocus specifically on: {', '.join(request.focus_areas)}"

        prompt = f"""
Analyze my complete monetization strategy. I need you to:

1. Identify ALL revenue leaks in my current operation
2. Design a comprehensive monetization architecture across all price points
3. Map out the complete customer journey from discovery to high-ticket
4. Provide specific implementation steps for the next 30 days
5. Challenge me with immediate actions I can take TODAY
{focus}

Give me the full strategic analysis with brutal honesty about what's missing.
"""

        async for chunk in self.analyze(prompt, request.business_context):
            yield chunk

    async def analyze_funnel(self, request: FunnelAnalysisRequest) -> AsyncIterator[str]:
        """
        Analyze conversion funnel

        Args:
            request: Funnel analysis request

        Yields:
            Analysis results
        """
        stages_data = [
            {
                "name": stage.name,
                "visitors": stage.visitors,
                "conversions": stage.conversions,
                "revenue": stage.revenue,
            }
            for stage in request.funnel_stages
        ]

        prompt = f"""
Analyze my conversion funnel and identify exactly where I'm losing money.

Funnel Data:
{chr(10).join([f"- {s['name']}: {s['visitors']} visitors, {s.get('conversions', 'N/A')} conversions, ${s.get('revenue', 0):.2f} revenue" for s in stages_data])}

Provide:
1. Specific diagnosis of the biggest leaks
2. Tactical fixes for each stage
3. Expected revenue impact of optimizations
4. A challenge for me to implement the highest-impact fix TODAY
"""

        async for chunk in self.analyze(prompt, request.business_context):
            yield chunk

    async def evaluate_pricing(self, request: PricingEvaluationRequest) -> AsyncIterator[str]:
        """
        Evaluate pricing strategy

        Args:
            request: Pricing evaluation request

        Yields:
            Analysis results
        """
        prompt = f"""
Evaluate my pricing strategy:

Product Type: {request.product_type}
Current Price: ${request.current_price:.2f}
Cost to Deliver: ${request.cost_to_deliver:.2f}
Monthly Customers: {request.monthly_customers}
Market Position: {request.market_position}

Tell me:
1. Am I leaving money on the table with my current pricing?
2. What should my optimal pricing strategy be?
3. How should I implement tiered pricing?
4. What's my first pricing experiment to run THIS WEEK?

Be brutally honest about whether I'm underpricing.
"""

        async for chunk in self.analyze(prompt, request.business_context):
            yield chunk

    async def project_revenue(self, request: RevenueProjectionRequest) -> AsyncIterator[str]:
        """
        Project revenue growth

        Args:
            request: Revenue projection request

        Yields:
            Projection results
        """
        prompt = f"""
Calculate revenue projections:

Current Monthly Revenue: ${request.current_monthly_revenue:,.2f}
Current Audience Size: {request.current_audience_size:,}
Monthly Audience Growth: {request.monthly_audience_growth}%
Current Conversion Rate: {request.current_conversion_rate}%
Projection Period: {request.projection_months} months

Show me:
1. Baseline scenario (status quo)
2. Optimized scenario (what's possible with strategic improvements)
3. Aggressive scenario (what happens if I execute at the highest level)
4. The specific strategic moves that bridge the gap between scenarios
5. What I need to do THIS WEEK to start tracking toward the optimized scenario

Make it real. Show me the dollar difference between mediocre execution and excellence.
"""

        async for chunk in self.analyze(prompt, request.business_context):
            yield chunk

    async def calculate_ltv(self, request: LTVCalculationRequest) -> AsyncIterator[str]:
        """
        Calculate customer lifetime value

        Args:
            request: LTV calculation request

        Yields:
            LTV analysis
        """
        prompt = f"""
Calculate customer lifetime value:

Average Order Value: ${request.average_order_value:.2f}
Purchase Frequency: {request.purchase_frequency} purchases/year
Customer Lifespan: {request.customer_lifespan} years
Gross Margin: {request.gross_margin}%

Then tell me:
1. What's my current LTV and is it good enough?
2. Which lever (AOV, frequency, lifespan) has the biggest impact?
3. Specific tactics to increase each lever
4. How backend monetization (upsells, continuity) transforms these numbers
5. The ONE thing I should implement THIS WEEK to increase LTV

Don't just give me numbers—tell me exactly how to engineer higher customer value.
"""

        async for chunk in self.analyze(prompt, request.business_context):
            yield chunk

    async def assess_opportunities(self, request: OpportunityAssessmentRequest) -> AsyncIterator[str]:
        """
        Assess market opportunities

        Args:
            request: Opportunity assessment request

        Yields:
            Opportunity analysis
        """
        prompt = f"""
Assess market opportunities:

Niche: {request.niche}
Audience Size: {request.audience_size:,}
Engagement: {request.engagement}
Current Revenue: ${request.current_revenue:,.2f}
Potential Revenue Streams: {", ".join(request.potential_revenue_streams)}

Analyze:
1. Which revenue streams are the highest-leverage opportunities for me RIGHT NOW?
2. What's the realistic revenue potential for each?
3. Which should I prioritize based on ease, speed, and scale?
4. What's the fastest path to my next $10K/month?
5. What should I validate or test THIS WEEK?

Give me a clear prioritization with specific reasoning—not generic advice.
"""

        async for chunk in self.analyze(prompt):
            yield chunk


# Global service instance
_service_instance: WealthAccelerationService | None = None


def get_wealth_acceleration_service(
    api_key: str | None = None,
) -> WealthAccelerationService:
    """
    Get or create the global wealth acceleration service instance

    Args:
        api_key: Optional Anthropic API key

    Returns:
        WealthAccelerationService instance
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = WealthAccelerationService(api_key=api_key)
    return _service_instance
