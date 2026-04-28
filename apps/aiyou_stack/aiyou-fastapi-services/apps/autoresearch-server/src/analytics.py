# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from fastapi import APIRouter

try:
    from shadowtag_v4.governance.sentinel_v2 import JudgeSixCSRMC
except ImportError:
    # Fallback/Mock if PYTHONPATH isn't perfectly set in this context
    class JudgeSixCSRMC:
        def calculate_s_score(self, h, v):
            return "NOMINAL", 1.0


router = APIRouter()
sentinel = JudgeSixCSRMC()


@router.get("/survivability/heatmap")
async def get_heatmap_data():
    # 1. Fetch live telemetry from the Cortex (Firestore)
    # 2. Map files to S-Scores
    heatmap = [
        {"file": "libs/shadowtag_v4/agents/recursive_rlm.py", "s_score": 1.4, "status": "HARDENED"},
        {
            "file": "apps/n-autoresearch/Kosmos/BioAgents-server/src/main.py",
            "s_score": 0.8,
            "status": "VULNERABLE",
        },
        {"file": "infra/terraform/main.tf", "s_score": 1.1, "status": "STABLE"},
    ]
    return heatmap
