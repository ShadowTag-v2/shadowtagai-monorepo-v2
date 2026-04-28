# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Transformer Circuits: Tracing Attention Computation Through Feature Interactions

This package implements the methods described in "Tracing Attention Computation Through Feature Interactions"
by Kamath, Ameisen, et al. (2025) from Anthropic's Transformer Circuits Thread.

Main components:
- QK Attributions: Explain attention patterns through feature interactions
- Head Loadings: Compute attention head contributions to attribution graph edges
- Attribution Graphs: Represent transformer forward pass as interpretable causal graphs
- Feature Interventions: Steering and validation experiments
"""

from transformer_circuits.attribution_graph import (
    AttributionEdge,
    AttributionGraph,
    AttributionNode,
)
from transformer_circuits.feature_interventions import (
    FeatureIntervenor,
    steer_features,
    validate_circuit,
)
from transformer_circuits.head_loadings import (
    HeadLoadingComputer,
    compute_head_loadings,
)
from transformer_circuits.qk_attribution import (
    QKAttributor,
    compute_attention_scores,
    compute_qk_attributions,
)

__version__ = "0.1.0"
__all__ = [
    "AttributionEdge",
    "AttributionGraph",
    "AttributionNode",
    "FeatureIntervenor",
    "HeadLoadingComputer",
    "QKAttributor",
    "compute_attention_scores",
    "compute_head_loadings",
    "compute_qk_attributions",
    "steer_features",
    "validate_circuit",
]
