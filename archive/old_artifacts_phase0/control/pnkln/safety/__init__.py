"""
PNKLN Safety Module

Training data safety indexing and content classification based on:
- Apertus LLM Training Data Indexing Research (arxiv:2510.09471v1)
- Judge 6 governance integration
- ShadowTag provenance verification

Components:
- TrainingDataIndexer: Full-text search over training data
- SafetyLexicon: Multilingual harmful content lexicons
- SafetyGate: Pre-governance content filtering
"""

from .training_data_indexer import (
    SafetyCategory,
    SafetyGate,
    SafetyHit,
    SafetyLexicon,
    SafetyScanResult,
    TrainingDataIndexer,
)

__all__ = [
    "TrainingDataIndexer",
    "SafetyCategory",
    "SafetyHit",
    "SafetyScanResult",
    "SafetyLexicon",
    "SafetyGate",
]
