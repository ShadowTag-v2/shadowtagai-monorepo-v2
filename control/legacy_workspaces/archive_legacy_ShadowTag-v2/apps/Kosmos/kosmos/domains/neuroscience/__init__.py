# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Neuroscience domain module - connectomics, neurodegeneration, and brain network analysis"""

from kosmos.domains.neuroscience.apis import (
    AllenBrainClient,
    AMPADClient,
    ConnectomeDataset,
    FlyWireClient,
    GeneExpressionData,
    GEOClient,
    MICrONSClient,
    NeuronData,
    OpenConnectomeClient,
    WormBaseClient,
)
from kosmos.domains.neuroscience.apis import (
    DifferentialExpressionResult as APIDifferentialExpressionResult,
)
from kosmos.domains.neuroscience.connectomics import (
    ConnectomicsAnalyzer,
    ConnectomicsResult,
    CrossSpeciesComparison,
    PowerLawFit,
    ScalingRelationship,
)
from kosmos.domains.neuroscience.neurodegeneration import (
    CrossSpeciesValidation,
    DifferentialExpressionResult,
    NeurodegenerationAnalyzer,
    NeurodegenerationResult,
    PathwayEnrichmentResult,
    TemporalStage,
)
from kosmos.domains.neuroscience.ontology import (
    NeuroscienceOntology,
)

__all__ = [
    # API Clients
    "FlyWireClient",
    "AllenBrainClient",
    "MICrONSClient",
    "GEOClient",
    "AMPADClient",
    "OpenConnectomeClient",
    "WormBaseClient",
    # API Data Models
    "NeuronData",
    "GeneExpressionData",
    "ConnectomeDataset",
    "APIDifferentialExpressionResult",
    # Connectomics
    "ConnectomicsAnalyzer",
    "ConnectomicsResult",
    "ScalingRelationship",
    "PowerLawFit",
    "CrossSpeciesComparison",
    # Neurodegeneration
    "NeurodegenerationAnalyzer",
    "NeurodegenerationResult",
    "DifferentialExpressionResult",
    "PathwayEnrichmentResult",
    "CrossSpeciesValidation",
    "TemporalStage",
    # Ontology
    "NeuroscienceOntology",
]
