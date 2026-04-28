# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""ShadowTagAi Pipelines

Specialized execution pipelines built on COR Orchestrator patterns.
"""

from shadowtagai.pipelines.research_pipeline import (
    MultiSourceResearchPipeline,
    ResearchResult,
    execute_research,
)

__all__ = ["MultiSourceResearchPipeline", "ResearchResult", "execute_research"]
