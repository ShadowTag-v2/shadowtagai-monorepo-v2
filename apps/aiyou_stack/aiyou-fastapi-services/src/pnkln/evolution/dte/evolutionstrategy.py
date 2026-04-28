# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from enum import StrEnum


class EvolutionStrategy(StrEnum):
    """Evolution strategies for prompt/agent improvement"""

    RCR_MAD = "rcr_mad"
    GRPO = "grpo"
    BENCHMARK = "benchmark"
    HYBRID = "hybrid"
