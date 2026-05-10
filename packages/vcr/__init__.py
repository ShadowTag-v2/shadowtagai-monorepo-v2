# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""VCR interceptor package — deterministic API record/replay/diff.

Public API:
  - VCRRecorder: Main recorder (record/replay/diff modes)
  - VCRMode: Enum of operational modes
  - Cassette: JSONL-backed interaction storage
  - CassetteEntry: Single recorded API interaction
  - compute_request_hash: Deterministic request fingerprinting
  - ReplayMiss: Exception for replay cache misses
  - DiffMismatch: Result of a diff comparison
  - VCRInterceptor: Legacy interceptor (deprecated, use VCRRecorder)
"""

from vcr.cassette import Cassette, CassetteEntry, compute_request_hash
from vcr.recorder import DiffMismatch, ReplayMiss, VCRMode, VCRRecorder

__all__ = [
  "Cassette",
  "CassetteEntry",
  "DiffMismatch",
  "ReplayMiss",
  "VCRMode",
  "VCRRecorder",
  "compute_request_hash",
]
