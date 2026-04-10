"""
UnGPT - Atomic Thread Orchestrator
Implements Atom of Thoughts (AoT) with multi-LLM consensus
"""

from .consensus import ConsensusOrchestrator, ModelResponse, ModelType, PeerReview
from .orchestrator import AtomicThread, DecompositionResult, PNKLNAtomicOrchestrator

__version__ = "0.1.0"

__all__ = [
    "AtomicThread",
    "DecompositionResult",
    "PNKLNAtomicOrchestrator",
    "ModelType",
    "ModelResponse",
    "PeerReview",
    "ConsensusOrchestrator",
]
