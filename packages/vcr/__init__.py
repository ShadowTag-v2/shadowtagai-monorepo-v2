# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""VCR Record/Replay Subsystem for Deterministic API Testing.

Ported from: services/vcr.ts (ant-only, FORCE_VCR=1)
Reference: AGNT STATE B Spec P3.1

Three modes:
  - RECORD: Capture all Gemini API req/res to cassette files
  - REPLAY: Return recorded responses instead of live API calls
  - DIFF: Compare live vs recorded for regression detection
"""

from vcr.cassette import Cassette, CassetteEntry
from vcr.recorder import VCRRecorder, VCRMode

__all__ = [
    "Cassette",
    "CassetteEntry",
    "VCRRecorder",
    "VCRMode",
]
