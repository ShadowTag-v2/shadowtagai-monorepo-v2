# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Kosmos specialized agents for multi-agent workflows."""

from kosmos.agents.base import BaseAgent
from kosmos.agents.data_analysis import DataAnalysisAgent
from kosmos.agents.hypothesis import HypothesisAgent
from kosmos.agents.literature import LiteratureAgent
from kosmos.agents.synthesis import SynthesisAgent

__all__ = [
    "BaseAgent",
    "DataAnalysisAgent",
    "HypothesisAgent",
    "LiteratureAgent",
    "SynthesisAgent",
]
