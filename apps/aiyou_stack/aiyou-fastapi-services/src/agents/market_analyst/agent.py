"""Market Analyst Product Strategy Agent Implementation"""

import os
from typing import Any

import anthropic

from ..base_agent import BaseAgent
from .config import ANALYSIS_FRAMEWORKS, MARKET_ANALYST_CONFIG
from .prompts import (
    COMPETITIVE_ANALYSIS_TEMPLATE,
    DIFFERENTIATION_TEMPLATE,
    FEATURE_GAP_TEMPLATE,
    MARKET_ANALYST_SYSTEM_PROMPT,
)
from .tools import CompetitiveAnalysisTools, MarketPositioningTools


class MarketAnalystAgent(BaseAgent):
    """Market Analyst agent for competitive product strategy and positioning.

    Capabilities:
    - Competitive analysis
    - Feature comparison
    - Market positioning
    - Differentiation strategy
    - Feature gap analysis
    - Identifying winning features
    """

    def __init__(self):
        """Initialize Market Analyst agent"""
        super().__init__(
            name=MARKET_ANALYST_CONFIG["name"],
            system_prompt=MARKET_ANALYST_SYSTEM_PROMPT,
            config=MARKET_ANALYST_CONFIG,
        )

        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")

        self.client = anthropic.Anthropic(api_key=api_key)
        self.tools = CompetitiveAnalysisTools()
        self.positioning_tools = MarketPositioningTools()

    async def process(
        self, prompt: str, context: dict[str, Any] | None = None, stream: bool = False,
    ) -> dict[str, Any]:
        """Process competitive analysis request

        Args:
            prompt: User's analysis request
            context: Additional context (competitors, features, etc.)
            stream: Whether to stream response (not implemented yet)

        Returns:
            Analysis results

        """
        if not self.validate_input(prompt, context):
            return {"error": "Invalid input", "message": "Prompt cannot be empty"}

        # Enhance prompt with context
        enhanced_prompt = self._enhance_prompt(prompt, context)

        # Call Claude API
        try:
            response = self.client.messages.create(
                model=self.config["model"],
                max_tokens=self.config["max_tokens"],
                temperature=self.config.get("temperature", 0.7),
                system=self.system_prompt,
                messages=[{"role": "user", "content": enhanced_prompt}],
            )

            analysis_result = {
                "agent": self.name,
                "analysis": response.content[0].text,
                "model": self.config["model"],
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "status": "success",
            }

            # Add structured analysis if context provides data
            if context:
                analysis_result["structured_insights"] = self._extract_structured_insights(context)

            return analysis_result

        except Exception as e:
            return {"error": str(e), "status": "failed"}

    def _enhance_prompt(self, prompt: str, context: dict[str, Any] | None = None) -> str:
        """Enhance user prompt with additional context and structure

        Args:
            prompt: Original user prompt
            context: Additional context

        Returns:
            Enhanced prompt

        """
        enhanced = prompt

        if context:
            # Add product information
            if "product" in context:
                enhanced += f"\n\n## Product Information\n{context['product']}"

            # Add competitor information
            if "competitors" in context:
                enhanced += "\n\n## Competitors\n"
                for comp in context["competitors"]:
                    enhanced += f"- {comp}\n"

            # Add feature list
            if "features" in context:
                enhanced += "\n\n## Features to Analyze\n"
                for feature in context["features"]:
                    enhanced += f"- {feature}\n"

            # Add analysis type
            if "analysis_type" in context:
                analysis_type = context["analysis_type"]
                if analysis_type in ANALYSIS_FRAMEWORKS:
                    framework = ANALYSIS_FRAMEWORKS[analysis_type]
                    enhanced += f"\n\n## Analysis Framework\n{framework['description']}\n"
                    enhanced += f"Output Format: {framework['output_format']}\n"

        return enhanced

    def _extract_structured_insights(self, context: dict[str, Any]) -> dict[str, Any]:
        """Extract structured insights using analysis tools

        Args:
            context: Analysis context with data

        Returns:
            Structured insights

        """
        insights = {}

        # Create feature matrix if data available
        if all(k in context for k in ["product", "competitors", "features"]):
            feature_matrix = self.tools.create_feature_matrix(
                product=context["product"],
                competitors=context["competitors"],
                features=context["features"],
            )
            insights["feature_matrix"] = feature_matrix

            # Calculate coverage
            coverage = self.tools.calculate_feature_coverage(feature_matrix)
            insights["coverage_stats"] = coverage

            # Identify gaps
            gaps = self.tools.identify_gaps(feature_matrix, context["product"])
            insights["gap_analysis"] = gaps

        # Prioritize features if available
        if "features_to_prioritize" in context:
            prioritized = self.tools.prioritize_features(context["features_to_prioritize"])
            insights["prioritized_features"] = prioritized

        return insights

    def get_capabilities(self) -> list[str]:
        """Get list of agent capabilities"""
        return self.config.get("features", [])

    def analyze_competitors(
        self, product: str, competitors: list[str], features: list[str],
    ) -> dict[str, Any]:
        """Perform structured competitive analysis

        Args:
            product: Your product name
            competitors: List of competitors
            features: Features to compare

        Returns:
            Competitive analysis results

        """
        # Create feature matrix
        matrix = self.tools.create_feature_matrix(product, competitors, features)

        # Calculate coverage
        coverage = self.tools.calculate_feature_coverage(matrix)

        # Identify gaps
        gaps = self.tools.identify_gaps(matrix, product)

        return {
            "feature_matrix": matrix,
            "coverage_statistics": coverage,
            "gap_analysis": gaps,
            "recommendations": self._generate_recommendations(gaps),
        }

    def _generate_recommendations(self, gaps: dict[str, Any]) -> list[str]:
        """Generate recommendations based on gap analysis

        Args:
            gaps: Gap analysis results

        Returns:
            List of recommendations

        """
        recommendations = []

        # Critical gaps
        if gaps.get("critical_gaps"):
            recommendations.append(
                f"Address {len(gaps['critical_gaps'])} critical feature gaps "
                "to achieve competitive parity",
            )

        # Unique features
        if gaps.get("unique_features"):
            recommendations.append(
                f"Leverage {len(gaps['unique_features'])} unique features for differentiation",
            )

        # Parity gaps
        if gaps.get("parity_gaps"):
            recommendations.append(
                f"Consider {len(gaps['parity_gaps'])} additional features for competitive advantage",
            )

        return recommendations

    def get_templates(self) -> dict[str, str]:
        """Get available analysis templates"""
        return {
            "competitive_analysis": COMPETITIVE_ANALYSIS_TEMPLATE,
            "feature_gap": FEATURE_GAP_TEMPLATE,
            "differentiation": DIFFERENTIATION_TEMPLATE,
        }
