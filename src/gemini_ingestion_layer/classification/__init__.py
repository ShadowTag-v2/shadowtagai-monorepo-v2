# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Tier Classification Module

Implements 3-tier data classification system:
- Tier 1: High-value, verified sources (30% target)
- Tier 2: Medium-value, credible sources (50% target)
- Tier 3: Low-value, unverified sources (20% max)

Uses Gemini 2.5 Flash-Lite for cost-effective classification.
"""

from .tier_classifier import TierClassifier, ClassificationResult

__all__ = ["TierClassifier", "ClassificationResult"]
