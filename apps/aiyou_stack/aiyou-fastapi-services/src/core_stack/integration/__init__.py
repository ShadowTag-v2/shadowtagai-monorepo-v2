# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""PNKLN Core Stack™ — Integration Layer
Gemini Ingestion → Judge 6 → Services

This module handles the data flow between:
1. Gemini Ingestion Layer (nightly batch intelligence collection)
2. Judge 6 (real-time governance enforcement)
3. Services (inference, training, gateway systems)

Key Components:
- ingestion_models: Data contracts (IngestionBriefing, IngestedItem, JudgeDecision)
- pipeline_orchestrator: Integration orchestration (Publisher, Updater, Client)
"""

from .ingestion_models import (
    ContentType,
    CostSummary,
    IngestedItem,
    IngestionBriefing,
    JudgeDecision,
    QualityMetrics,
    SourceTier,
)
from .pipeline_orchestrator import IngestionPublisher, Claude_Code_6Client, Claude_Code_6Updater, PipelineConfig

__all__ = [
    # Models
    "SourceTier",
    "ContentType",
    "QualityMetrics",
    "CostSummary",
    "IngestedItem",
    "IngestionBriefing",
    "JudgeDecision",
    # Orchestration
    "PipelineConfig",
    "IngestionPublisher",
    "Claude_Code_6Updater",
    "Claude_Code_6Client",
]

__version__ = "1.0.0"
