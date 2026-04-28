# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import random
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class TaskRequest(BaseModel):
    task: str
    content: str | None = None
    cost_tier: str = "flash"
    metadata: dict[str, Any] = {}


@router.post("/task")
async def swarm_task(request: TaskRequest):
    """Simulates the minion 650-Agent Swarm processing a task.
    This enables the 'vote' logic to return a valid consensus.
    """
    print(f"🐒 [minion Service] Received Task: {request.task}")

    # Mock Voting Logic (Simulating 650 Agents)
    # In a real heavy lift, we'd delegate to celery/redis/pubsub.

    is_code_review = request.metadata.get("vote_type") == "code_review"
    confidence = 0.88 if is_code_review else 0.75

    # Random variance for realism (but bias towards approval as per 'Accept All' directive)
    if random.random() > 0.95:
        result_text = "REJECT: Validation failed on minor syntax."
        confidence = 0.40
    else:
        result_text = "APPROVED: 620/650 Agents concur. Code is solid."

    return {
        "status": "completed",
        "result": result_text,
        "confidence": confidence,
        "metadata": request.metadata,
    }
