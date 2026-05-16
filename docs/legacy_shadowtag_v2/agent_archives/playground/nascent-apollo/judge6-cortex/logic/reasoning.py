# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from governance.judge_llm_v7 import vet_sovereign_action


def evaluate_verdict(input_context: str) -> dict:
    """
    The Core Logic Block.
    Fused with Judge LLM V7 for Sovereign reasoning.
    """
    result = vet_sovereign_action(input_context)

    print(f"> ORCHESTRATOR: ANALYZING {len(input_context)} BYTES...")

    return {
        "verdict": "AUTHORIZED" if result["authorized"] else "DENIED",
        "confidence": result["confidence"],
        "reasoning": result["reasoning"],
    }
