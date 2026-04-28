# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Configuration for Market Analyst Product Strategy Agent"""

MARKET_ANALYST_CONFIG = {
    "name": "Market Analyst - Product Strategy",
    "version": "1.0.0",
    "description": "Competitive analysis expert for product positioning",
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 8096,
    "temperature": 0.7,
    "features": [
        "competitive_analysis",
        "feature_comparison",
        "market_positioning",
        "differentiation",
        "feature_gaps",
        "winning_features",
    ],
    "use_cases": [
        "Feature comparison",
        "Competitive advantage",
        "Market positioning",
        "Feature planning",
        "Differentiation strategy",
        "Gap analysis",
    ],
}

ANALYSIS_FRAMEWORKS = {
    "competitive_analysis": {
        "description": "Comprehensive competitor feature and positioning analysis",
        "output_format": "structured_report",
    },
    "feature_comparison": {
        "description": "Side-by-side feature matrix comparison",
        "output_format": "comparison_matrix",
    },
    "swot_analysis": {
        "description": "Strengths, Weaknesses, Opportunities, Threats analysis",
        "output_format": "swot_matrix",
    },
    "gap_analysis": {
        "description": "Identify feature gaps and opportunities",
        "output_format": "gap_report",
    },
    "differentiation": {
        "description": "Find unique value propositions and unfair advantages",
        "output_format": "differentiation_report",
    },
}
