"""Growth Engineer Agent

A specialized agent that implements viral mechanics and finds where users get hooked
in your app to build viral loops that actually work.

Key Features:
- Viral mechanics implementation
- User hook identification
- Growth loop design
- A/B testing framework
- Analytics tracking
- Engagement feature optimization
"""

from datetime import datetime
from typing import Any

from claude_agent_sdk import ClaudeAgentOptions, query


class GrowthEngineerAgent:
    """Growth engineering specialist who implements viral mechanics.
    Finds where users get hooked in your app and builds viral loops that actually work.
    """

    def __init__(self):
        self.agent_metadata = {
            "name": "Growth Engineer",
            "category": "Product Strategy",
            "description": "Finds where users get hooked in your app and builds viral loops that actually work",
            "version": "1.0.0",
            "capabilities": [
                "viral_mechanics",
                "user_hooks",
                "growth_loops",
                "ab_testing",
                "analytics_tracking",
                "engagement_features",
            ],
        }

        self.system_prompt = """You are a Growth Engineering specialist who implements viral mechanics and product strategy.

Your expertise includes:

1. VIRAL MECHANICS
   - Design referral programs that users actually want to share
   - Implement social sharing features with optimal placement
   - Create network effects and viral coefficients > 1
   - Build invite systems with tracking and attribution
   - Design shareable moments and content

2. USER HOOKS
   - Identify activation moments and "aha" experiences
   - Find friction points in user journeys
   - Analyze user behavior patterns for hook opportunities
   - Design habit-forming features using Hooked model
   - Optimize onboarding for faster time-to-value

3. GROWTH LOOPS
   - Build self-reinforcing growth loops
   - Design user-generated content loops
   - Create paid acquisition loops with positive ROI
   - Implement viral loops with measurable k-factor
   - Build network effects and platform dynamics

4. A/B TESTING
   - Design statistically valid experiments
   - Calculate sample sizes and test duration
   - Implement feature flags and gradual rollouts
   - Analyze test results and statistical significance
   - Run multivariate and sequential testing

5. ANALYTICS TRACKING
   - Implement event tracking for key metrics
   - Design funnel analytics and conversion tracking
   - Track cohort retention and engagement
   - Build dashboards for growth metrics
   - Implement attribution and source tracking

6. ENGAGEMENT FEATURES
   - Design gamification and reward systems
   - Build notification systems that don't annoy
   - Create personalization and recommendation engines
   - Implement social proof and FOMO mechanics
   - Design re-engagement and win-back campaigns

Your approach:
- Data-driven: Everything is measured and tested
- User-centric: Growth tactics enhance user experience
- Systematic: Build repeatable growth systems, not hacks
- Ethical: No dark patterns or manipulative tactics
- Scalable: Solutions that work at increasing user volumes

Always provide:
- Clear metrics and success criteria
- Implementation code with best practices
- Testing strategies and success indicators
- Potential risks and mitigation strategies
- Timeline and resource estimates
"""

    async def analyze_user_hooks(self, app_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze application to find where users get hooked and engaged.

        Args:
            app_data: Application data including user flows, features, and metrics

        Returns:
            Analysis of user hooks with recommendations

        """
        prompt = f"""Analyze this application data to identify user hooks and engagement opportunities:

Application Data:
{app_data}

Please provide:
1. Current activation points and "aha moments"
2. Friction points that prevent engagement
3. Opportunities for new hooks and engagement features
4. Recommended hook implementation strategy
5. Success metrics to track

Focus on finding genuine value moments, not manipulative tactics."""

        results = []
        async for message in query(
            prompt=prompt, options=ClaudeAgentOptions(system_prompt=self.system_prompt),
        ):
            results.append(message)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "analysis_type": "user_hooks",
            "results": results,
        }

    async def design_viral_loop(self, product_info: dict[str, Any]) -> dict[str, Any]:
        """Design a viral loop mechanism for the product.

        Args:
            product_info: Information about the product, users, and value proposition

        Returns:
            Viral loop design with implementation plan

        """
        prompt = f"""Design a viral loop for this product:

Product Information:
{product_info}

Please provide:
1. Viral loop mechanism design
2. Expected viral coefficient (k-factor) calculation
3. Implementation steps and technical requirements
4. Key metrics to track (invites sent, conversion rate, cycle time)
5. A/B testing strategy for optimization
6. Potential challenges and solutions

Design for sustainable, user-value-aligned growth."""

        results = []
        async for message in query(
            prompt=prompt, options=ClaudeAgentOptions(system_prompt=self.system_prompt),
        ):
            results.append(message)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "analysis_type": "viral_loop_design",
            "results": results,
        }

    async def create_ab_test(self, experiment_config: dict[str, Any]) -> dict[str, Any]:
        """Create and configure an A/B test experiment.

        Args:
            experiment_config: Test configuration including hypothesis, variants, and metrics

        Returns:
            A/B test setup with statistical parameters

        """
        prompt = f"""Design an A/B test for this experiment:

Experiment Configuration:
{experiment_config}

Please provide:
1. Null and alternative hypotheses
2. Sample size calculation
3. Test duration estimate
4. Statistical significance threshold
5. Implementation code/pseudocode
6. Analysis plan and decision criteria
7. Potential confounding factors

Ensure statistical rigor and practical feasibility."""

        results = []
        async for message in query(
            prompt=prompt, options=ClaudeAgentOptions(system_prompt=self.system_prompt),
        ):
            results.append(message)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "analysis_type": "ab_test_design",
            "results": results,
        }

    async def analyze_growth_metrics(self, metrics_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze growth metrics and provide optimization recommendations.

        Args:
            metrics_data: Current growth metrics and analytics data

        Returns:
            Analysis with actionable recommendations

        """
        prompt = f"""Analyze these growth metrics and provide optimization recommendations:

Metrics Data:
{metrics_data}

Please provide:
1. Key insights from the data
2. Growth bottlenecks and opportunities
3. Metric health assessment (good/concerning/critical)
4. Prioritized recommendations for improvement
5. Expected impact of each recommendation
6. Implementation complexity and timeline

Focus on highest-leverage opportunities first."""

        results = []
        async for message in query(
            prompt=prompt, options=ClaudeAgentOptions(system_prompt=self.system_prompt),
        ):
            results.append(message)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "analysis_type": "growth_metrics_analysis",
            "results": results,
        }

    async def design_engagement_feature(self, feature_request: dict[str, Any]) -> dict[str, Any]:
        """Design an engagement feature with viral potential.

        Args:
            feature_request: Feature requirements and context

        Returns:
            Feature design with implementation plan

        """
        prompt = f"""Design an engagement feature for this request:

Feature Request:
{feature_request}

Please provide:
1. Feature design and user experience flow
2. Engagement mechanics and psychology principles used
3. Viral potential and sharing opportunities
4. Implementation technical requirements
5. Success metrics and KPIs
6. Potential risks and ethical considerations
7. Rollout and testing strategy

Balance engagement with user value and ethical design."""

        results = []
        async for message in query(
            prompt=prompt, options=ClaudeAgentOptions(system_prompt=self.system_prompt),
        ):
            results.append(message)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "analysis_type": "engagement_feature_design",
            "results": results,
        }

    async def implement_analytics_tracking(
        self, tracking_requirements: dict[str, Any],
    ) -> dict[str, Any]:
        """Implement analytics tracking for growth metrics.

        Args:
            tracking_requirements: Requirements for tracking events and metrics

        Returns:
            Analytics implementation plan and code

        """
        prompt = f"""Implement analytics tracking for these requirements:

Tracking Requirements:
{tracking_requirements}

Please provide:
1. Event taxonomy and naming conventions
2. Implementation code for tracking
3. Data schema and storage recommendations
4. Dashboard and reporting structure
5. Privacy and compliance considerations
6. Testing and validation approach

Use industry best practices and ensure GDPR/privacy compliance."""

        results = []
        async for message in query(
            prompt=prompt, options=ClaudeAgentOptions(system_prompt=self.system_prompt),
        ):
            results.append(message)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "analysis_type": "analytics_implementation",
            "results": results,
        }

    async def optimize_referral_system(self, referral_data: dict[str, Any]) -> dict[str, Any]:
        """Optimize an existing referral system for better performance.

        Args:
            referral_data: Current referral system data and performance

        Returns:
            Optimization recommendations and implementation plan

        """
        prompt = f"""Optimize this referral system:

Referral System Data:
{referral_data}

Please provide:
1. Current performance analysis
2. Bottlenecks in the referral flow
3. Optimization opportunities (incentives, UX, messaging)
4. A/B test ideas for improvement
5. Expected impact on referral metrics
6. Implementation plan and code changes

Focus on improving conversion at each step of the referral funnel."""

        results = []
        async for message in query(
            prompt=prompt, options=ClaudeAgentOptions(system_prompt=self.system_prompt),
        ):
            results.append(message)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "analysis_type": "referral_optimization",
            "results": results,
        }

    async def general_growth_query(
        self, user_query: str, context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Handle general growth engineering queries with optional context.

        Args:
            user_query: The growth engineering question or request
            context: Optional additional context

        Returns:
            Agent response with recommendations

        """
        context_str = f"\n\nContext:\n{context}" if context else ""

        prompt = f"""{user_query}{context_str}"""

        results = []
        async for message in query(
            prompt=prompt, options=ClaudeAgentOptions(system_prompt=self.system_prompt),
        ):
            results.append(message)

        return {"timestamp": datetime.utcnow().isoformat(), "query": user_query, "results": results}

    def get_capabilities(self) -> list[str]:
        """Return list of agent capabilities"""
        return self.agent_metadata["capabilities"]

    def get_metadata(self) -> dict[str, Any]:
        """Return agent metadata"""
        return self.agent_metadata
