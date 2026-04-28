# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Contractual Services Package

This package contains core business logic for the Contractual platform:
- conflict_detection.py: AI-powered conflict detection engine
- negotiation_engine.py: Negotiation workflow management (future)
- document_generation.py: Contract document generation (future)

Author: PNKLN Core Stack / ShadowTag-v4 FastAPI Services
Version: 1.0.0
Status: Strategic Planning Phase
"""

from .conflict_detection import ConflictDetector, DetectedConflict, Term

__all__ = ["ConflictDetector", "DetectedConflict", "Term"]
