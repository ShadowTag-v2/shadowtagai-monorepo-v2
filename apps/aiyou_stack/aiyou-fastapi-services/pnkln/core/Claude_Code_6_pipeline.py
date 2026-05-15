# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Claude Code 6 pipeline — alias for Judge 6 validation pipeline.

Re-exports from judge_six_pipeline for backwards compatibility.
"""

from pnkln.core.judge_six_pipeline import JudgeSixPipeline, ValidationResult

__all__ = ["JudgeSixPipeline", "ValidationResult"]
