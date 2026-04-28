# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""SHADOWTAGAI Core Stack - Gemini Ingestion Layer

An intelligence collection pipeline designed for nightly batch processing
on GKE CronJob infrastructure. This layer is called by services across 4
namespaces and provides ethical web crawling with tier classification.

Architecture: GKE CronJob Multi-Container
Target Runtime: ~45 minutes/night
Cost Model: ~$77/month operational
Confidence Threshold: ≥60% (pre-production, specs-only)

Key Components:
- Multi-source ingestion (YouTube, Twitter, News, etc.)
- Ethical crawling with robots.txt compliance and rate limiting
- 3-tier classification system
- Quality gates for Items, Sources, Costs, Scores
- AM briefing delivery
"""

__version__ = "0.1.0"
__author__ = "SHADOWTAGAI Core Stack Team"
