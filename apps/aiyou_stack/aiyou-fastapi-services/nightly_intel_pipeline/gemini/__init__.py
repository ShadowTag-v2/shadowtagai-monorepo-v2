"""Gemini Event Ingestion Layer
============================
Semantic normalization layer for intelligence pipeline.

Converts raw scraped documents into structured IntelEvent objects
before JR Engine scoring.

Components:
- intel_event.py: IntelEvent dataclass schema
- extractor.py: Gemini-powered extraction
- prompts.py: Structured prompts for Gemini
- delta_detector.py: Change detection between versions
- config.py: Gemini layer configuration
"""

from .config import GEMINI_INGESTION_CONFIG
from .extractor import GeminiExtractor, extract_intel_event
from .intel_event import (
    ChangeType,
    IntelEvent,
    Jurisdiction,
    SourceType,
)

__all__ = [
    "GEMINI_INGESTION_CONFIG",
    "ChangeType",
    "GeminiExtractor",
    "IntelEvent",
    "Jurisdiction",
    "SourceType",
    "extract_intel_event",
]
